#!/usr/bin/env python3
import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "dataRequirements/document-rendering/tool"))
from export_workflow_report import (
    load_export_config,
    run_renderer_with_payload,
)
from nias_local_env import load_repo_env

load_repo_env(REPO_ROOT)
EXPORT_CONFIG = (
    REPO_ROOT / "dataRequirements/document-rendering/config/pdd-export.yaml"
)

NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
CLAIM = "http://w3id.org/claimont#"
AIAO = "http://w3id.org/aiao#"
IMPACTONT = "http://w3id.org/impactont#"
DCTERMS = "http://purl.org/dc/terms/"
IND = "http://independentimpact.org/indicator-owl/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
SCHEMA = "https://schema.org/"

IRI_VALUE_FIELDS = {
    f"{NIAS}publicPrivateClassification",
    f"{NIAS}techMeasType",
    f"{IND}hasUnit",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _first(values):
    if isinstance(values, list) and values:
        return values[0]
    if isinstance(values, dict):
        return values
    return {}


def _as_list(values):
    if isinstance(values, list):
        return [value for value in values if value is not None]
    if values is None:
        return []
    return [values]


def _node_id(suffix: str):
    return f"{NIAS}{suffix}"


def _as_node_reference(value, fallback_suffix: str):
    if isinstance(value, dict):
        identifier = value.get("@id")
        if isinstance(identifier, str) and identifier.strip():
            return {"@id": identifier.strip()}
    if isinstance(value, str) and value.strip():
        return {"@id": value.strip()}
    return {"@id": _node_id(fallback_suffix)}


def _generated_node_id(value, fallback_suffix: str):
    return _as_node_reference(value, fallback_suffix)["@id"]


def _optional_node_reference(value):
    if isinstance(value, dict):
        identifier = value.get("@id")
        if isinstance(identifier, str) and identifier.strip():
            return {"@id": identifier.strip()}
    if isinstance(value, str) and value.strip():
        return {"@id": value.strip()}
    return None


def _as_bool(value, default: bool):
    if isinstance(value, bool):
        return value
    if isinstance(value, dict):
        literal_value = value.get("@value")
        if isinstance(literal_value, bool):
            return literal_value
        value = value.get("@id", literal_value)
    if isinstance(value, str):
        normalized = value.strip().lower()
        if normalized in {"true", "1", "yes"} or normalized.endswith("/yes"):
            return True
        if normalized in {"false", "0", "no"} or normalized.endswith("/no"):
            return False
    return default


def _copy_form_value(value, target_key):
    if target_key in IRI_VALUE_FIELDS:
        return _optional_node_reference(value)
    return value


def _copy_optional(source, target, keys):
    for key in keys:
        if key in source:
            copied = _copy_form_value(source[key], key)
            if copied is not None:
                target[key] = copied


def _resource_nodes(values, prefix, extra_fields):
    nodes = []
    references = []
    for index, value in enumerate(_as_list(values), start=1):
        item = value if isinstance(value, dict) else {}
        node_id = _generated_node_id(item, f"{prefix}-{index}")
        references.append({"@id": node_id})
        node = {"@id": node_id}
        for source_key, target_key, default in extra_fields:
            if source_key in item:
                copied = _copy_form_value(item[source_key], target_key)
                if copied is not None:
                    node[target_key] = copied
            elif default is not None:
                node[target_key] = default
        nodes.append(node)
    return references, nodes


def build_renderer_payload(pdd_a, pdd_b, pdd_c):
    pdd_a_content = _first(pdd_a.get(f"{NIAS}reportContent"))
    project = _first(pdd_a_content.get(f"{CLAIM}hasSubject"))

    objective = _first(project.get(f"{AIAO}hasObjective"))
    location_refs, location_nodes = _resource_nodes(
        project.get(f"{IMPACTONT}hasSpatialLocation"),
        "locations/pdd-alpha-location",
        [(f"{NIAS}resourceIpfsUri", f"{NIAS}resourceIpfsUri", "ipfs://draft-pdd-location")],
    )
    technology_refs, technology_nodes = _resource_nodes(
        project.get(f"{NIAS}technologyOrMeasure"),
        "technologies/pdd-alpha-technology",
        [
            (f"{NIAS}techMeasType", f"{NIAS}techMeasType", _as_node_reference(None, "concepts/facility")),
            (f"{SCHEMA}description", f"{SCHEMA}description", ""),
            (f"{NIAS}currentAgeInYears", f"{NIAS}currentAgeInYears", None),
            (f"{NIAS}estimatedLifespanInYears", f"{NIAS}estimatedLifespanInYears", None),
            (f"{NIAS}additionalInfo", f"{NIAS}additionalInfo", None),
        ],
    )
    party_refs, party_nodes = _resource_nodes(
        project.get(f"{NIAS}projectParty"),
        "parties/pdd-alpha-party",
        [
            (f"{NIAS}partyName", f"{NIAS}partyName", ""),
            (f"{NIAS}isHostParty", f"{NIAS}isHostParty", False),
            (f"{NIAS}isParticipantParty", f"{NIAS}isParticipantParty", False),
            (f"{NIAS}publicPrivateClassification", f"{NIAS}publicPrivateClassification", None),
            (f"{NIAS}additionalInfo", f"{NIAS}additionalInfo", None),
        ],
    )

    pdd_b_content = _first(pdd_b.get(f"{NIAS}reportContent"))
    methodologies = pdd_b_content.get(f"{NIAS}usesMethodology") or []
    impact_nodes = []
    impact_refs = []
    parameter_nodes = []
    for impact_index, impact_value in enumerate(
        _as_list(pdd_b_content.get(f"{NIAS}hasDeclaredImpact")), start=1
    ):
        impact = impact_value if isinstance(impact_value, dict) else {}
        impact_id = _generated_node_id(impact, f"impact/impact-{impact_index}")
        impact_refs.append({"@id": impact_id})
        parameter_refs = []
        for parameter_index, parameter_value in enumerate(
            _as_list(impact.get(f"{NIAS}dataParameterRequirement")), start=1
        ):
            parameter = parameter_value if isinstance(parameter_value, dict) else {}
            parameter_id = _generated_node_id(
                parameter, f"parameters/impact-{impact_index}-parameter-{parameter_index}"
            )
            parameter_refs.append({"@id": parameter_id})
            parameter_node = {"@id": parameter_id, "@type": "nias:DataParameterRequirement"}
            _copy_optional(
                parameter,
                parameter_node,
                [
                    f"{SCHEMA}description",
                    f"{NIAS}dataParameterPurpose",
                    f"{NIAS}monitoredOrFixed",
                    f"{NIAS}measurementMethodsAndProcedures",
                    f"{NIAS}qaQcProcedures",
                    f"{NIAS}monitoringFrequency",
                    f"{NIAS}samplingPlan",
                    f"{NIAS}parameterAppliedValue",
                    f"{NIAS}dataSource",
                    f"{IND}hasUnit",
                    f"{RDFS}label",
                ],
            )
            parameter_nodes.append(parameter_node)

        impact_node = {
            "@id": impact_id,
            "@type": "impactont:Impact",
            f"{SCHEMA}description": impact.get(f"{SCHEMA}description", ""),
            f"{NIAS}impactIntentionality": _as_node_reference(
                impact.get(f"{NIAS}impactIntentionality"),
                "concepts/intentional",
            ),
            f"{NIAS}beneficialOrAdverse": _as_node_reference(
                impact.get(f"{NIAS}beneficialOrAdverse"),
                "concepts/beneficial",
            ),
            f"{NIAS}monitored": _as_bool(impact.get(f"{NIAS}monitored"), True),
        }
        _copy_optional(
            impact,
            impact_node,
            [
                f"{NIAS}notMonitoredJustification",
                f"{NIAS}additionalityJustification",
                f"{NIAS}exAnteImpactEstimate",
            ],
        )
        if parameter_refs:
            impact_node[f"{NIAS}dataParameterRequirement"] = parameter_refs
        impact_nodes.append(impact_node)

    claim_nodes = []
    claim_refs = []
    for claim_index, claim_value in enumerate(
        _as_list(pdd_b_content.get(f"{NIAS}impactClaim")), start=1
    ):
        claim = claim_value if isinstance(claim_value, dict) else {}
        claim_id = _generated_node_id(claim, f"claims/impact-claim-{claim_index}")
        claim_refs.append({"@id": claim_id})
        claim_methodologies = claim.get(f"{NIAS}usesMethodology") or methodologies
        claim_nodes.append(
            {
                "@id": claim_id,
                "@type": "aiao:ImpactClaim",
                f"{CLAIM}hasSubject": _as_node_reference(
                    claim.get(f"{CLAIM}hasSubject"), "projects/pdd-alpha"
                ),
                f"{NIAS}usesMethodology": [
                    _as_node_reference(method, "methodologies/default-pdd-methodology")
                    for method in claim_methodologies
                ]
                or [{"@id": _node_id("methodologies/default-pdd-methodology")}],
            }
        )

    graph = [
        {
            "@id": _node_id("projects/pdd-alpha"),
            "@type": "aiao:Project",
            f"{NIAS}title": project.get(f"{NIAS}title", ""),
            f"{AIAO}hasObjective": _as_node_reference(
                objective.get("@id"), "objectives/pdd-alpha-objective"
            ),
            f"{IMPACTONT}hasSpatialLocation": location_refs
            or [_as_node_reference(None, "locations/pdd-alpha-location-1")],
            f"{NIAS}technologyOrMeasure": technology_refs
            or [_as_node_reference(None, "technologies/pdd-alpha-technology-1")],
            f"{NIAS}projectParty": party_refs
            or [_as_node_reference(None, "parties/pdd-alpha-party-1")],
            f"{NIAS}legalMatters": project.get(f"{NIAS}legalMatters", ""),
            f"{NIAS}publicFundingStatus": _as_bool(
                project.get(f"{NIAS}publicFundingStatus"), False
            ),
            f"{NIAS}projectHistory": project.get(f"{NIAS}projectHistory", ""),
            f"{NIAS}debundlingAssessment": project.get(
                f"{NIAS}debundlingAssessment", ""
            ),
        },
        {
            "@id": _node_id("objectives/pdd-alpha-objective"),
            f"{SCHEMA}description": objective.get(f"{SCHEMA}description", ""),
        },
        *(
            location_nodes
            or [
                {
                    "@id": _node_id("locations/pdd-alpha-location-1"),
                    f"{NIAS}resourceIpfsUri": "ipfs://draft-pdd-location",
                }
            ]
        ),
        *(
            technology_nodes
            or [
                {
                    "@id": _node_id("technologies/pdd-alpha-technology-1"),
                    f"{NIAS}techMeasType": _as_node_reference(None, "concepts/facility"),
                    f"{SCHEMA}description": "",
                }
            ]
        ),
        *(
            party_nodes
            or [
                {
                    "@id": _node_id("parties/pdd-alpha-party-1"),
                    f"{NIAS}partyName": "",
                    f"{NIAS}isHostParty": False,
                    f"{NIAS}isParticipantParty": False,
                }
            ]
        ),
        {
            "@id": _node_id("reports/pdd-section-a"),
            "@type": "nias:PddSectionAReport",
            f"{CLAIM}hasSubject": {"@id": _node_id("projects/pdd-alpha")},
            f"{CLAIM}isMadeBy": _as_node_reference(
                pdd_a_content.get(f"{CLAIM}isMadeBy"), "users/project-developer-1"
            ),
            f"{DCTERMS}conformsTo": _as_node_reference(
                pdd_a_content.get(f"{DCTERMS}conformsTo"), "document-schema/PDDxA-1.0.0"
            ),
        },
        *(
            impact_nodes
            or [
                {
                    "@id": _node_id("impact/impact-1"),
                    "@type": "impactont:Impact",
                    f"{SCHEMA}description": "",
                    f"{NIAS}impactIntentionality": _as_node_reference(
                        None, "concepts/intentional"
                    ),
                    f"{NIAS}beneficialOrAdverse": _as_node_reference(
                        None, "concepts/beneficial"
                    ),
                    f"{NIAS}monitored": True,
                }
            ]
        ),
        *parameter_nodes,
        *(
            claim_nodes
            or [
                {
                    "@id": _node_id("claims/impact-claim-1"),
                    "@type": "aiao:ImpactClaim",
                    f"{CLAIM}hasSubject": _as_node_reference(
                        None, "projects/pdd-alpha"
                    ),
                    f"{NIAS}usesMethodology": [
                        _as_node_reference(
                            method, "methodologies/default-pdd-methodology"
                        )
                        for method in methodologies
                    ]
                    or [
                        {
                            "@id": _node_id("methodologies/default-pdd-methodology"),
                        }
                    ],
                }
            ]
        ),
        {
            "@id": _node_id("reports/pdd-section-b"),
            "@type": "nias:PddSectionBReport",
            f"{CLAIM}isMadeBy": _as_node_reference(
                pdd_b_content.get(f"{CLAIM}isMadeBy"), "users/project-developer-1"
            ),
            f"{CLAIM}hasSubject": _as_node_reference(
                pdd_b_content.get(f"{CLAIM}hasSubject"), "projects/pdd-alpha"
            ),
            f"{NIAS}hasDeclaredImpact": impact_refs
            or [{"@id": _node_id("impact/impact-1")}],
            f"{NIAS}impactClaim": claim_refs
            or [{"@id": _node_id("claims/impact-claim-1")}],
            f"{NIAS}usesMethodology": [
                _as_node_reference(method, "methodologies/default-pdd-methodology")
                for method in methodologies
            ]
            or [
                {
                    "@id": _node_id("methodologies/default-pdd-methodology"),
                }
            ],
        },
        {
            "@id": _node_id("reports/pdd-section-c"),
            "@type": "nias:PddSectionCStakeholderEngagement",
            f"{NIAS}stakeholderEngagementModalities": pdd_c.get(
                f"{NIAS}stakeholderEngagementModalities", ""
            ),
            f"{NIAS}stakeholderCommentSummary": pdd_c.get(
                f"{NIAS}stakeholderCommentSummary", ""
            ),
            f"{NIAS}stakeholderCommentConsideration": pdd_c.get(
                f"{NIAS}stakeholderCommentConsideration", ""
            ),
        },
    ]

    return {
        "@context": {
            "aiao": AIAO,
            "claim": CLAIM,
            "dcterms": DCTERMS,
            "impactont": IMPACTONT,
            "ind": "http://independentimpact.org/indicator-owl/",
            "nias": NIAS,
            "rdfs": "http://www.w3.org/2000/01/rdf-schema#",
            "schema": SCHEMA,
        },
        "@graph": graph,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Export workflow shell section payloads to PDD Markdown artifacts."
    )
    parser.add_argument("--pdd-a-json", type=Path, required=True)
    parser.add_argument("--pdd-b-json", type=Path, required=True)
    parser.add_argument("--pdd-c-json", type=Path, required=True)
    parser.add_argument(
        "--review-a-json",
        type=Path,
        help="Deprecated. Validation reports are exported separately from PDD.",
    )
    parser.add_argument(
        "--review-b-json",
        type=Path,
        help="Deprecated. Validation reports are exported separately from PDD.",
    )
    parser.add_argument(
        "--review-c-json",
        type=Path,
        help="Deprecated. Validation reports are exported separately from PDD.",
    )
    parser.add_argument("--render-mode", choices=["draft", "final"], default="draft")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--output-target",
        action="append",
        choices=["markdown", "pdf", "html"],
        help="Repeat to request multiple deterministic artifact targets.",
    )
    parser.add_argument(
        "--source-artifact-id",
        default="workflow-shell",
        help="Source artifact identifier passed through to renderer metadata.",
    )
    args = parser.parse_args()

    pdd_a = _load_json(args.pdd_a_json)
    pdd_b = _load_json(args.pdd_b_json)
    pdd_c = _load_json(args.pdd_c_json)
    export_config = load_export_config(EXPORT_CONFIG)

    renderer_payload = build_renderer_payload(pdd_a, pdd_b, pdd_c)
    run_renderer_with_payload(
        repo_root=REPO_ROOT,
        config=export_config,
        renderer_payload=renderer_payload,
        render_mode=args.render_mode,
        source_artifact_id=args.source_artifact_id,
        parser=parser,
        output=args.output,
        output_dir=args.output_dir,
        output_targets=args.output_target,
    )


if __name__ == "__main__":
    main()
