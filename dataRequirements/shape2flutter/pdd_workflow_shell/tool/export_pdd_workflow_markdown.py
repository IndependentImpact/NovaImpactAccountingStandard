#!/usr/bin/env python3
import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[4]
RENDER_SCRIPT = (
    REPO_ROOT / "dataRequirements/document-rendering/tool/render_pdd_markdown.py"
)

NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
CLAIM = "http://w3id.org/claimont#"
AIAO = "http://w3id.org/aiao#"
IMPACTONT = "http://w3id.org/impactont#"
DCTERMS = "http://purl.org/dc/terms/"
SCHEMA = "https://schema.org/"

SECTION_STEPS = {
    "a": {
        "step_name": "pddA",
        "review_of": f"{NIAS}documents/pdd-alpha/pddA",
        "review_decision": f"{NIAS}review-approve",
    },
    "b": {
        "step_name": "pddB",
        "review_of": f"{NIAS}documents/pdd-alpha/pddB",
        "review_decision": f"{NIAS}review-approve",
    },
    "c": {
        "step_name": "pddC",
        "review_of": f"{NIAS}documents/pdd-alpha/pddC",
        "review_decision": f"{NIAS}review-approve",
    },
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _first(values):
    if isinstance(values, list) and values:
        return values[0]
    if isinstance(values, dict):
        return values
    return {}


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


def _gate_failures(review_payloads):
    failures = []
    for section, expected in SECTION_STEPS.items():
        review = review_payloads.get(section)
        if review is None:
            failures.append(f"PDD-{section.upper()} validation review has not been submitted.")
            continue
        if review.get(f"{NIAS}finalReviewDecision") != expected["review_decision"]:
            failures.append(f"PDD-{section.upper()} validation review is not approved.")
        if review.get(f"{NIAS}isReviewOf") != expected["review_of"]:
            failures.append(
                f"PDD-{section.upper()} review does not point to the submitted document."
            )
    return failures


def build_renderer_payload(pdd_a, pdd_b, pdd_c):
    pdd_a_content = _first(pdd_a.get(f"{NIAS}reportContent"))
    project = _first(pdd_a_content.get(f"{CLAIM}hasSubject"))

    objective = _first(project.get(f"{AIAO}hasObjective"))
    location = _first(project.get(f"{IMPACTONT}hasSpatialLocation"))
    technology = _first(project.get(f"{NIAS}technologyOrMeasure"))
    party = _first(project.get(f"{NIAS}projectParty"))

    pdd_b_content = _first(pdd_b.get(f"{NIAS}reportContent"))
    declared_impact = _first(pdd_b_content.get(f"{NIAS}hasDeclaredImpact"))
    impact_claim = _first(pdd_b_content.get(f"{NIAS}impactClaim"))
    methodologies = pdd_b_content.get(f"{NIAS}usesMethodology") or []

    graph = [
        {
            "@id": _node_id("projects/pdd-alpha"),
            "@type": "aiao:Project",
            f"{NIAS}title": project.get(f"{NIAS}title", ""),
            f"{AIAO}hasObjective": _as_node_reference(
                objective.get("@id"), "objectives/pdd-alpha-objective"
            ),
            f"{IMPACTONT}hasSpatialLocation": _as_node_reference(
                location.get("@id"), "locations/pdd-alpha-location"
            ),
            f"{NIAS}technologyOrMeasure": _as_node_reference(
                technology.get("@id"), "technologies/pdd-alpha-technology"
            ),
            f"{NIAS}projectParty": _as_node_reference(
                party.get("@id"), "parties/pdd-alpha-party"
            ),
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
        {
            "@id": _node_id("locations/pdd-alpha-location"),
            f"{NIAS}resourceIpfsUri": location.get(
                f"{NIAS}resourceIpfsUri", "ipfs://draft-pdd-location"
            ),
        },
        {
            "@id": _node_id("technologies/pdd-alpha-technology"),
            f"{NIAS}techMeasType": _as_node_reference(
                technology.get(f"{NIAS}techMeasType"), "concepts/facility"
            ),
            f"{SCHEMA}description": technology.get(f"{SCHEMA}description", ""),
        },
        {
            "@id": _node_id("parties/pdd-alpha-party"),
            f"{NIAS}partyName": party.get(f"{NIAS}partyName", ""),
            f"{NIAS}isHostParty": bool(party.get(f"{NIAS}isHostParty", False)),
            f"{NIAS}isParticipantParty": bool(
                party.get(f"{NIAS}isParticipantParty", False)
            ),
        },
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
        {
            "@id": _node_id("impact/impact-1"),
            "@type": "impactont:Impact",
            f"{SCHEMA}description": declared_impact.get(f"{SCHEMA}description", ""),
            f"{NIAS}impactIntentionality": _as_node_reference(
                declared_impact.get(f"{NIAS}impactIntentionality"),
                "concepts/intentional",
            ),
            f"{NIAS}beneficialOrAdverse": _as_node_reference(
                declared_impact.get(f"{NIAS}beneficialOrAdverse"),
                "concepts/beneficial",
            ),
            f"{NIAS}monitored": _as_bool(
                declared_impact.get(f"{NIAS}monitored"), True
            ),
        },
        {
            "@id": _node_id("claims/impact-claim-1"),
            "@type": "aiao:ImpactClaim",
            f"{CLAIM}hasSubject": _as_node_reference(
                impact_claim.get(f"{CLAIM}hasSubject"), "projects/pdd-alpha"
            ),
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
            "@id": _node_id("reports/pdd-section-b"),
            "@type": "nias:PddSectionBReport",
            f"{CLAIM}isMadeBy": _as_node_reference(
                pdd_b_content.get(f"{CLAIM}isMadeBy"), "users/project-developer-1"
            ),
            f"{NIAS}hasDeclaredImpact": {"@id": _node_id("impact/impact-1")},
            f"{NIAS}impactClaim": {"@id": _node_id("claims/impact-claim-1")},
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
            "nias": NIAS,
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
    parser.add_argument("--review-a-json", type=Path)
    parser.add_argument("--review-b-json", type=Path)
    parser.add_argument("--review-c-json", type=Path)
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

    if args.render_mode == "final":
        review_payloads = {
            "a": _load_json(args.review_a_json) if args.review_a_json else None,
            "b": _load_json(args.review_b_json) if args.review_b_json else None,
            "c": _load_json(args.review_c_json) if args.review_c_json else None,
        }
        failures = _gate_failures(review_payloads)
        if failures:
            parser.exit(1, "Workflow gate failed for final export:\n- " + "\n- ".join(failures) + "\n")

    renderer_payload = build_renderer_payload(pdd_a, pdd_b, pdd_c)

    with tempfile.TemporaryDirectory(prefix="nias-workflow-export-") as tmpdir:
        payload_path = Path(tmpdir) / "workflow-shell-render-input.jsonld"
        payload_path.write_text(
            json.dumps(renderer_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        command = [
            sys.executable,
            str(RENDER_SCRIPT),
            "--input-jsonld",
            str(payload_path),
            "--render-mode",
            args.render_mode,
            "--source-artifact-id",
            args.source_artifact_id,
        ]

        if args.output:
            command.extend(["--output", str(args.output)])
        if args.output_dir:
            command.extend(["--output-dir", str(args.output_dir)])
            for target in args.output_target or ["markdown"]:
                command.extend(["--output-target", target])

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if completed.returncode != 0:
            parser.exit(completed.returncode, completed.stderr or completed.stdout)

        if not args.output and not args.output_dir:
            print(completed.stdout, end="")


if __name__ == "__main__":
    main()
