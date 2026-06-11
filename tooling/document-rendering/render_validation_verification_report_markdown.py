from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, Namespace

import render_pdd_markdown as pdd_renderer


REPO_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_PROFILES = {
    "validation": REPO_ROOT
    / "dataRequirements/document-rendering/validation-report-rendering-profile.md",
    "verification": REPO_ROOT
    / "dataRequirements/document-rendering/verification-report-rendering-profile.md",
}
DEFAULT_VVS_REQUIREMENTS = REPO_ROOT / "glossary/ValidationVerificationStandard.ttl"
DEFAULT_VVS_SHAPES = REPO_ROOT / "dataRequirements/vvs-requirement-shapes.ttl"
DEFAULT_VVS_REQUIREMENT_ANCHOR_MAP = (
    REPO_ROOT / "dataRequirements/mappings/vvs-requirement-anchor-map.ttl"
)
DEFAULT_REQUIREMENT_COVERAGE_PROOF_SHAPES = (
    REPO_ROOT / "dataRequirements/requirement-coverage-proof-shapes.ttl"
)
DEFAULT_ANCHOR_DEFINITIONS = [
    REPO_ROOT / "dataRequirements/mappings/pdd-anchor-definitions.ttl",
    REPO_ROOT / "dataRequirements/mappings/monitoring-anchor-definitions.ttl",
    REPO_ROOT / "dataRequirements/mappings/dlr-anchor-definitions.ttl",
]
DEFAULT_ARTIFACT_ANCHOR_SHAPES = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"
DEFAULT_STRUCTURAL_SHAPES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
    DEFAULT_ARTIFACT_ANCHOR_SHAPES,
    REPO_ROOT / "dataRequirements/document-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-reference-shapes.ttl",
    REPO_ROOT / "dataRequirements/review-shapes.ttl",
    REPO_ROOT / "dataRequirements/certificate-shapes.ttl",
]
DEFAULT_ONTOLOGIES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]
REPORT_TYPES = ("validation", "verification")

DIRECTIVE_PATTERN = re.compile(r"^\{\{ render: ([a-zA-Z0-9_.-]+) \}\}$")
TOC_PLACEHOLDER = "<!-- NIAS_VV_REPORT_TABLE_OF_CONTENTS -->"

DATA = Namespace("https://jellyfiiish.xyz/ns/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
HEDERA = Namespace("https://hashgraphontology.xyz/core/")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
NIAS_VVS = Namespace("https://nova.org.za/novaimpactaccountingstandard/vvs/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SH = Namespace("http://www.w3.org/ns/shacl#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")


def _load_graph(paths, *, fmt=None):
    graph = Graph()
    for path in paths:
        graph.parse(str(path), format=fmt)
    return graph


def _first_value(graph: Graph, subject, predicate):
    if subject is None:
        return None
    return next(iter(graph.objects(subject, predicate)), None)


def _sorted_values(graph: Graph, subject, predicate):
    if subject is None:
        return []
    return sorted(graph.objects(subject, predicate), key=lambda item: _display_value(graph, item))


def _local_name(node):
    return pdd_renderer._local_name(node)


def _display_value(graph: Graph, node):
    if node is None:
        return "Unavailable"
    if isinstance(node, Literal):
        value = node.toPython()
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value)
    if isinstance(node, URIRef):
        for predicate in (
            RDFS.label,
            SKOS.prefLabel,
            DCTERMS.title,
            NIAS.renderHeading,
            NIAS.anchorKey,
        ):
            label = graph.value(node, predicate)
            if label is not None:
                return str(label)
    return _local_name(node)


def _escape(value):
    return pdd_renderer._escape_table_cell(value)


def _two_column_table(rows):
    return pdd_renderer._two_column_table(rows)


def _heading_value_blocks(rows, heading_level: int = 4):
    def _scalar_text(value):
        if value is None:
            return ""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        return str(value).strip()

    marker = "#" * heading_level
    row_items = list(rows)
    lines: list[str] = []
    for index, (heading, value) in enumerate(row_items):
        lines.append(f"{marker} {_scalar_text(heading)}")
        content = _scalar_text(value)
        lines.append(content if content else "_Not provided._")
        if index < len(row_items) - 1:
            lines.append("")
    return lines


def _report_label(report_type: str):
    return "Validation Report" if report_type == "validation" else "Verification Report"


def _report_package_title(report_type: str):
    return (
        "Validation Review Package"
        if report_type == "validation"
        else "Verification Review Package"
    )


def _report_basename(report_type: str):
    return f"{report_type}-report"


def _report_mandate(report_type: str):
    return NIAS.validation if report_type == "validation" else NIAS.verification


def _review_nodes(graph: Graph, report_type: str | None = None):
    nodes = set(graph.subjects(RDF.type, NIAS.GenericDocumentReview))
    nodes.update(graph.subjects(RDF.type, NIAS.GlobalQualitativeDocumentReview))
    nodes.update(graph.subjects(RDF.type, NIAS.VerifiedImpactCertificateIssuanceRequestReview))
    if report_type == "validation":
        nodes = {
            node
            for node in nodes
            if (node, RDF.type, NIAS.VerifiedImpactCertificateIssuanceRequestReview)
            not in graph
        }
    elif report_type == "verification":
        nodes = {
            node
            for node in nodes
            if (node, RDF.type, NIAS.VerifiedImpactCertificateIssuanceRequestReview)
            in graph
        }
    return sorted(nodes, key=lambda item: _display_value(graph, item))


def _node_text(node) -> str | None:
    if node is None:
        return None
    if isinstance(node, Literal):
        return str(node.toPython())
    return str(node)


def _first_node_text(graph: Graph, subject, predicate) -> str | None:
    return _node_text(_first_value(graph, subject, predicate))


def _reviewed_dlr_content_cid(graph: Graph, review) -> str | None:
    return _first_node_text(
        graph, review, URIRef(f"{NIAS}reviewedDlrContentCid")
    ) or _first_node_text(graph, review, URIRef(f"{NIAS}linkedDlrContentCid"))


def _review_identity_metadata(graph: Graph, report_type: str) -> dict:
    reviews = _review_nodes(graph, report_type)
    if not reviews:
        return {}
    review = reviews[0]
    metadata = {}
    for field in (
        "artifactContentCid",
        "artifactSchemaCid",
        "artifactSchemaVersionLabel",
        "artifactAuthor",
        "workflowSubject",
        "submissionTopicId",
        "submissionConsensusTimestamp",
        "submissionEventKey",
        "submissionMessageUrl",
        "reviewedArtifactType",
        "reviewedArtifactContentCid",
        "reviewedArtifactSchemaCid",
        "reviewedArtifactSchemaVersionLabel",
        "reviewedSubmissionTopicId",
        "reviewedSubmissionConsensusTimestamp",
    ):
        value = _first_node_text(graph, review, URIRef(f"{NIAS}{field}"))
        if value:
            metadata[f"nias:{field}"] = value
    reviewed_dlr_cid = _reviewed_dlr_content_cid(graph, review)
    if reviewed_dlr_cid:
        metadata["nias:reviewedDlrContentCid"] = reviewed_dlr_cid
    return metadata


def _ensure_final_review_identity_fields(graph: Graph, report_type: str):
    required = [
        "reviewedArtifactType",
        "reviewedArtifactContentCid",
        "reviewedSubmissionTopicId",
        "reviewedSubmissionConsensusTimestamp",
    ]
    if report_type == "verification":
        required.append("reviewedDlrContentCid")
    for review in _review_nodes(graph, report_type):
        for field in required:
            if field == "reviewedDlrContentCid":
                if not _reviewed_dlr_content_cid(graph, review):
                    raise ValueError(
                        "reviewedDlrContentCid is required in final render mode."
                    )
                continue
            if not _first_node_text(graph, review, URIRef(f"{NIAS}{field}")):
                raise ValueError(f"{field} is required in final render mode.")


def _review_kind(graph: Graph, review):
    if (review, RDF.type, NIAS.VerifiedImpactCertificateIssuanceRequestReview) in graph:
        return "Verification review"
    return "Validation review"


def _field_review_nodes(graph: Graph, review):
    return _sorted_values(graph, review, NIAS.fieldReview)


def _all_field_review_nodes(graph: Graph, report_type: str | None = None):
    fields = []
    for review in _review_nodes(graph, report_type):
        for field_review in _field_review_nodes(graph, review):
            fields.append((review, field_review))
    return fields


def _load_display_graph(data_graph: Graph):
    display_graph = Graph()
    for triple in data_graph:
        display_graph.add(triple)
    for ontology_path in DEFAULT_ONTOLOGIES:
        display_graph.parse(str(ontology_path), format="turtle")
    return display_graph


def _document_headings_for_toc(body: str):
    headings = []
    collecting = False
    for raw_line in body.splitlines():
        line = raw_line.strip()
        if line == "## Rendering Map":
            break
        match = re.match(r"^(#{2,4})\s+(.+)$", line)
        if not match:
            continue
        title = match.group(2).strip()
        if title == "Review Decision Register":
            collecting = True
        if not collecting or title == "Table Of Contents":
            continue
        headings.append((len(match.group(1)), title))
    return headings


def _heading_anchor(title):
    slug = title.lower().replace("&", "and")
    slug = re.sub(r"`([^`]+)`", r"\1", slug)
    slug = re.sub(r"[^a-z0-9\s.-]", "", slug)
    slug = re.sub(r"\s+", "-", slug.strip())
    slug = re.sub(r"-+", "-", slug)
    return slug


def _render_table_of_contents(body: str):
    headings = _document_headings_for_toc(body)
    if not headings:
        return [
            "| Section | Page |",
            "| --- | ---: |",
            "| _[table of contents to be generated]_ |  |",
        ]
    return [
        "| Section | Page |",
        "| --- | ---: |",
        *[
            f"| {title} | \\pageref{{{_heading_anchor(title)}}} |"
            for _, title in headings
        ],
    ]


def _replace_table_of_contents(rendered_body: str):
    return rendered_body.replace(
        TOC_PLACEHOLDER,
        "\n".join(_render_table_of_contents(rendered_body)),
    )


def _render_blank_directive(directive: str, report_type: str):
    if directive == "titlePage.reportTitle":
        return [f"### _[{_report_label(report_type)} package title]_"]
    if directive == "titlePage.packageSummary":
        return _heading_value_blocks(
            [
                ("Report type", _report_label(report_type)),
                ("Review documents", "**[required]** _[to be populated]_"),
                ("Anchor reviews", "**[required]** _[to be populated]_"),
                ("Final decisions", "**[required]** _[to be populated]_"),
                ("VVS evidence targets", "**[required for final]** _[to be populated]_"),
                ("Generated at", "**[optional]** _[to be populated]_"),
                ("Rendering mode", "**[optional]** _[draft or final]_"),
                ("Source artifact", "**[optional]** _[to be populated]_"),
            ],
            heading_level=4,
        )
    if directive == "tableOfContents":
        return [r"\tableofcontents"]
    if directive == "review.decisionRegister":
        return [
            "| Review document | Review type | Final decision | Anchor reviews |",
            "| --- | --- | --- | ---: |",
            "| **[required]** _[review document]_ | _[validation or verification]_ | _[approve or reject]_ | _[anchor review count]_ |",
        ]
    if directive == "review.documentQualitativeEvaluation":
        return [
            "| Review document | Review type | Document-level qualitative judgement |",
            "| --- | --- | --- |",
            "| **[required for validation]** _[review document]_ | _[validation or verification]_ | _[global qualitative judgement against guiding questions]_ |",
        ]
    if directive == "review.sectionQualitativeEvaluation":
        return [
            "| Review document | Review type | Section-level qualitative judgement |",
            "| --- | --- | --- |",
            "| **[required for validation]** _[review document]_ | _[validation or verification]_ | _[section-level qualitative judgement against guiding questions]_ |",
        ]
    if directive == "review.documentEnvelope":
        return [
            "| Review document | Schema | Author | IPFS URI | Encrypted | Auth proof |",
            "| --- | --- | --- | --- | --- | --- |",
            "| **[required]** _[review document]_ | _[schema IRI]_ | _[author]_ | _[IPFS URI]_ | _[yes/no]_ | _[proof type]_ |",
        ]
    if directive == "review.fieldFindings":
        return [
            "| Review document | Reviewed artifact | Reviewed anchor | Decision | Feedback | Reviewed content |",
            "| --- | --- | --- | --- | --- | --- |",
            "| **[required]** _[review document]_ | _[artifact IRI]_ | _[anchor IRI]_ | _[review decision]_ | _[reviewer feedback]_ | _[anchored content]_ |",
        ]
    if directive == "vvs.requirementCoverage":
        return [
            "| Requirement | Mandate | Anchor | Shape | Evidence status |",
            "| --- | --- | --- | --- | --- |",
            "| **[required]** _[REQ-*]_ | _[validation or verification]_ | _[exact anchor key and title]_ | _[SHACL shape]_ | _[not assessed]_ |",
        ]
    if directive == "workflow.consensusEvidence":
        return [
            "| Review document | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
            "| **[required]** _[review document]_ | _[submitted document]_ | _[workflow step]_ | _[subject]_ | _[submitter]_ | _[recipient]_ | _[topic]_ | _[sequence]_ | _[timestamp]_ |",
        ]
    if directive == "sourceEvidenceAppendix":
        return _heading_value_blocks(
            [
                ("Input JSON-LD", "**[required]** _[to be populated]_"),
                ("Evidence JSON-LD", "**[optional]** _[to be populated]_"),
                ("Source graph hash evidence", "**[optional]** _[to be populated]_"),
            ],
            heading_level=3,
        )
    if directive == "predicateMapAppendix":
        return _heading_value_blocks(
            [
                ("Review document type", "rdf:type"),
                ("Document schema", "nias-o:documentSchema"),
                ("Document author", "nias-o:documentAuthor"),
                ("Document IPFS URI", "nias-o:resourceIpfsUri"),
                ("Authenticity proof", "nias-o:authProof"),
                ("Final review decision", "nias-o:finalReviewDecision"),
                ("Document-level qualitative judgement", "nias-o:documentLevelQualitativeJudgement"),
                ("Section-level qualitative judgement", "nias-o:sectionQualitativeJudgement"),
                ("Anchor review", "nias-o:fieldReview"),
                ("Review target", "nias-o:reviewTarget"),
                ("Reviewed artifact", "nias-o:reviewedArtifact"),
                ("Reviewed anchor", "nias-o:reviewedAnchor"),
                ("Reviewer decision", "nias-o:reviewerDecision"),
                ("Reviewer feedback", "nias-o:reviewerFeedback"),
                ("Workflow submission evidence", "nias-o:hasWorkflowSubmission"),
                ("Consensus message", "nias-o:workflowSubmissionConsensusMessage"),
                ("VVS requirement implementation", "nias-o:implementedByShape"),
            ],
            heading_level=3,
        )
    return [f"- **[optional]** {directive}: _[to be populated]_"]


def render_blank_template(profile_path: Path, report_type: str):
    front_matter, body = pdd_renderer._read_front_matter_and_body(profile_path)
    front_matter = pdd_renderer._insert_front_matter_metadata(
        front_matter,
        {
            "renderedDocumentType": _report_label(report_type),
            "reportType": report_type,
        },
    )
    lines = []
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if stripped == "## Rendering Map":
            break
        if stripped == "## Validation Report Or Verification Report":
            lines.append(f"## {_report_label(report_type)}")
            continue
        directive_match = DIRECTIVE_PATTERN.match(stripped)
        if not directive_match:
            lines.append(raw_line)
            continue
        lines.extend(_render_blank_directive(directive_match.group(1), report_type))
        lines.append("")
    rendered_body = "\n".join(lines).rstrip() + "\n"
    return f"{front_matter}{rendered_body}"


def _vvs_target_classes(shape_graph: Graph):
    return sorted(
        {
            target_class
            for _, _, target_class in shape_graph.triples((None, SH.targetClass, None))
        },
        key=_local_name,
    )


def _vvs_target_subjects(data_graph: Graph, shape_graph: Graph):
    target_classes = _vvs_target_classes(shape_graph)
    subjects = []
    for target_class in target_classes:
        for subject in data_graph.subjects(RDF.type, target_class):
            subjects.append((subject, target_class))
    return sorted(subjects, key=lambda item: (_local_name(item[1]), _local_name(item[0])))


def _validate_structural_review_graph(review_graph: Graph):
    from pyshacl import validate

    shapes_graph = _load_graph(DEFAULT_STRUCTURAL_SHAPES, fmt="turtle")
    ontology_graph = _load_graph(DEFAULT_ONTOLOGIES, fmt="turtle")
    conforms, _, validation_text = validate(
        data_graph=review_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        advanced=True,
    )
    if not conforms:
        raise ValueError(
            "Final render mode requires structurally conformant review input.\n"
            f"{validation_text}"
        )
    return validation_text


def _selected_requirement_shapes(report_type: str):
    requirement_graph = Graph()
    requirement_graph.parse(str(DEFAULT_VVS_REQUIREMENTS), format="turtle")
    shape_graph = Graph()
    shape_graph.parse(str(DEFAULT_VVS_SHAPES), format="turtle")
    selected_shapes = set()
    selected_mandate = NIAS.validation if report_type == "validation" else NIAS.verification
    for requirement in requirement_graph.subjects(NIAS.reviewMandate, selected_mandate):
        shape = _first_value(requirement_graph, requirement, NIAS.implementedByShape)
        if shape is not None:
            selected_shapes.add(shape)
    return requirement_graph, shape_graph, selected_shapes


def _selected_target_subjects(data_graph: Graph, report_type: str):
    _, shape_graph, selected_shapes = _selected_requirement_shapes(report_type)
    subjects = []
    for shape in selected_shapes:
        for target_class in shape_graph.objects(shape, SH.targetClass):
            for subject in data_graph.subjects(RDF.type, target_class):
                subjects.append((subject, target_class))
    return sorted(subjects, key=lambda item: (_local_name(item[1]), _local_name(item[0])))


def _copy_shape_node(source_graph: Graph, target_graph: Graph, node, seen):
    if node in seen:
        return
    seen.add(node)

    for subject, predicate, object_node in source_graph.triples((node, None, None)):
        target_graph.add((subject, predicate, object_node))
        if isinstance(object_node, BNode):
            _copy_shape_node(source_graph, target_graph, object_node, seen)
        elif predicate in {SH.node, SH.property} and isinstance(object_node, URIRef):
            _copy_shape_node(source_graph, target_graph, object_node, seen)


def _filtered_vvs_shapes_graph(report_type: str):
    source_graph = Graph()
    source_graph.parse(str(DEFAULT_VVS_SHAPES), format="turtle")
    _, _, selected_shapes = _selected_requirement_shapes(report_type)
    filtered_graph = Graph()
    seen = set()
    for shape in selected_shapes:
        _copy_shape_node(source_graph, filtered_graph, shape, seen)
    return filtered_graph


def _validate_vvs_graph(combined_graph: Graph, report_type: str):
    from pyshacl import validate

    shapes_graph = _filtered_vvs_shapes_graph(report_type)
    target_subjects = _selected_target_subjects(combined_graph, report_type)
    if not target_subjects:
        raise ValueError(
            f"Final {report_type} render mode requires at least one {report_type} "
            "VVS-targeted evidence artifact "
            "in --input-jsonld or --evidence-jsonld."
        )

    ontology_graph = _load_graph(DEFAULT_ONTOLOGIES, fmt="turtle")
    conforms, _, validation_text = validate(
        data_graph=combined_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        advanced=True,
    )
    if not conforms:
        raise ValueError(
            "Final render mode requires VVS requirement-conformant evidence.\n"
            f"{validation_text}"
        )
    return validation_text, target_subjects


def _load_jsonld_graph(path: Path):
    graph = Graph()
    graph.parse(str(path), format="json-ld")
    return graph


def _merge_graphs(graphs):
    merged = Graph()
    for graph in graphs:
        for triple in graph:
            merged.add(triple)
    return merged


def _parse_inputs(input_path: Path, evidence_paths: list[Path]):
    review_graph = _load_jsonld_graph(input_path)
    evidence_graphs = [_load_jsonld_graph(path) for path in evidence_paths]
    combined_graph = _merge_graphs([review_graph, *evidence_graphs])
    return review_graph, combined_graph


def _review_decision_counts(graph: Graph, report_type: str):
    counts = {}
    for review in _review_nodes(graph, report_type):
        decision = _first_value(graph, review, NIAS.finalReviewDecision)
        label = _display_value(graph, decision)
        counts[label] = counts.get(label, 0) + 1
    return ", ".join(f"{label}: {count}" for label, count in sorted(counts.items())) or "Unavailable"


def _render_package_summary(
    display_graph: Graph,
    combined_graph: Graph,
    source_artifact: str,
    generated_at: str,
    render_mode: str,
    report_type: str,
):
    target_subjects = _selected_target_subjects(combined_graph, report_type)
    return _heading_value_blocks(
        [
            ("Report type", _report_label(report_type)),
            ("Review documents", len(_review_nodes(display_graph, report_type))),
            ("Anchor reviews", len(_all_field_review_nodes(display_graph, report_type))),
            ("Final decisions", _review_decision_counts(display_graph, report_type)),
            ("VVS evidence targets", len(target_subjects)),
            ("Generated at", generated_at),
            ("Rendering mode", render_mode),
            ("Source artifact", source_artifact),
        ],
        heading_level=4,
    )


def _render_decision_register(graph: Graph, report_type: str):
    lines = [
        "| Review document | Review type | Final decision | Anchor reviews |",
        "| --- | --- | --- | ---: |",
    ]
    for review in _review_nodes(graph, report_type):
        lines.append(
            "| {review} | {kind} | {decision} | {field_count} |".format(
                review=_escape(_display_value(graph, review)),
                kind=_escape(_review_kind(graph, review)),
                decision=_escape(_display_value(graph, _first_value(graph, review, NIAS.finalReviewDecision))),
                field_count=len(_field_review_nodes(graph, review)),
            )
        )
    if len(lines) == 2:
        lines.append("| No review documents supplied. |  |  |  |")
    return lines


def _render_document_qualitative_evaluations(graph: Graph, report_type: str):
    lines = [
        "| Review document | Review type | Document-level qualitative judgement |",
        "| --- | --- | --- |",
    ]
    for review in _review_nodes(graph, report_type):
        lines.append(
            "| {review} | {kind} | {judgement} |".format(
                review=_escape(_display_value(graph, review)),
                kind=_escape(_review_kind(graph, review)),
                judgement=_escape(
                    _display_value(
                        graph,
                        _first_value(graph, review, NIAS.documentLevelQualitativeJudgement),
                    )
                ),
            )
        )
    if len(lines) == 2:
        lines.append("| No global qualitative evaluations supplied. |  |  |")
    return lines


def _render_section_qualitative_evaluations(graph: Graph, report_type: str):
    lines = [
        "| Review document | Review type | Section-level qualitative judgement |",
        "| --- | --- | --- |",
    ]
    for review in _review_nodes(graph, report_type):
        lines.append(
            "| {review} | {kind} | {judgement} |".format(
                review=_escape(_display_value(graph, review)),
                kind=_escape(_review_kind(graph, review)),
                judgement=_escape(
                    _display_value(
                        graph,
                        _first_value(graph, review, NIAS.sectionQualitativeJudgement),
                    )
                ),
            )
        )
    if len(lines) == 2:
        lines.append("| No section-level qualitative evaluations supplied. |  |  |")
    return lines


def _render_review_document_envelope(graph: Graph, report_type: str):
    lines = [
        "| Review document | Schema | Author | IPFS URI | Encrypted | Auth proof |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for review in _review_nodes(graph, report_type):
        lines.append(
            "| {review} | {schema} | {author} | {ipfs} | {encrypted} | {auth_proof} |".format(
                review=_escape(_display_value(graph, review)),
                schema=_escape(_display_value(graph, _first_value(graph, review, NIAS.documentSchema))),
                author=_escape(_display_value(graph, _first_value(graph, review, NIAS.documentAuthor))),
                ipfs=_escape(_display_value(graph, _first_value(graph, review, NIAS.resourceIpfsUri))),
                encrypted=_escape(_display_value(graph, _first_value(graph, review, NIAS.isEncrypted))),
                auth_proof=_escape(_display_value(graph, _first_value(graph, review, NIAS.authProof))),
            )
        )
    if len(lines) == 2:
        lines.append("| No review document envelope supplied. |  |  |  |  |  |")
    return lines


def _render_field_findings(graph: Graph, report_type: str):
    lines = [
        "| Review document | Reviewed artifact | Reviewed anchor | Decision | Feedback | Reviewed content |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for review, field_review in _all_field_review_nodes(graph, report_type):
        review_target = _first_value(graph, field_review, NIAS.reviewTarget)
        reviewed_artifact = _first_value(graph, review_target, NIAS.reviewedArtifact)
        reviewed_anchor = _first_value(graph, review_target, NIAS.reviewedAnchor)
        lines.append(
            "| {review} | {artifact} | {anchor} | {decision} | {feedback} | {response} |".format(
                review=_escape(_display_value(graph, review)),
                artifact=_escape(_display_value(graph, reviewed_artifact)),
                anchor=_escape(_display_value(graph, reviewed_anchor)),
                decision=_escape(_display_value(graph, _first_value(graph, field_review, NIAS.reviewerDecision))),
                feedback=_escape(_display_value(graph, _first_value(graph, field_review, NIAS.reviewerFeedback))),
                response=_escape(_display_value(graph, _first_value(graph, field_review, NIAS.originalResponse))),
            )
        )
    if len(lines) == 2:
        lines.append("| No anchor reviews supplied. |  |  |  |  |  |")
    return lines


def _active_requirements(requirement_graph: Graph, report_type: str):
    active = []
    selected_mandate = NIAS.validation if report_type == "validation" else NIAS.verification
    for requirement in requirement_graph.subjects(NIAS.requirementStatus, NIAS_VVS.active):
        if (requirement, NIAS.reviewMandate, selected_mandate) not in requirement_graph:
            continue
        requirement_id = _first_value(requirement_graph, requirement, NIAS.requirementId)
        active.append((_display_value(requirement_graph, requirement_id), requirement))
    return [item[1] for item in sorted(active)]


def _anchor_sort_key(mapping_graph: Graph, anchor_graph: Graph, mapping):
    anchor = _first_value(mapping_graph, mapping, NIAS.mappedAnchor)
    artifact_type = _display_value(mapping_graph, _first_value(mapping_graph, mapping, NIAS.targetArtifactType))
    artifact_order = {
        "pdd": 0,
        "data-lineage-report": 1,
        "monitoring-report": 2,
    }.get(artifact_type, 99)
    render_order = _first_value(anchor_graph, anchor, NIAS.renderOrder)
    try:
        order = int(render_order.toPython()) if render_order is not None else 999999
    except (TypeError, ValueError):
        order = 999999
    anchor_key = _display_value(anchor_graph, _first_value(anchor_graph, anchor, NIAS.anchorKey))
    return (artifact_order, artifact_type, order, anchor_key)


def _display_exact_anchor(anchor_graph: Graph, anchor):
    if anchor is None:
        return "Unavailable"
    anchor_key = _first_value(anchor_graph, anchor, NIAS.anchorKey)
    title = _first_value(anchor_graph, anchor, DCTERMS.title)
    if anchor_key is not None and title is not None:
        return f"{_display_value(anchor_graph, anchor_key)} - {_display_value(anchor_graph, title)}"
    if anchor_key is not None:
        return _display_value(anchor_graph, anchor_key)
    if title is not None:
        return _display_value(anchor_graph, title)
    return _display_value(anchor_graph, anchor)


def _requirement_exact_anchors(mapping_graph: Graph, anchor_graph: Graph, requirement, report_type: str):
    selected_mandate = NIAS.validation if report_type == "validation" else NIAS.verification
    mappings = [
        mapping
        for mapping in mapping_graph.subjects(NIAS.mappedRequirement, requirement)
        if (mapping, NIAS.reviewMandate, selected_mandate) in mapping_graph
    ]
    anchors = []
    seen = set()
    for mapping in sorted(
        mappings,
        key=lambda item: _anchor_sort_key(mapping_graph, anchor_graph, item),
    ):
        anchor = _first_value(mapping_graph, mapping, NIAS.mappedAnchor)
        if anchor is None or anchor in seen:
            continue
        anchors.append(_display_exact_anchor(anchor_graph, anchor))
        seen.add(anchor)
    return "; ".join(anchors) if anchors else "Unavailable"


def _requirement_target_classes(shape_graph: Graph, shape):
    return list(shape_graph.objects(shape, SH.targetClass))


def _render_vvs_requirement_coverage(combined_graph: Graph, render_mode: str, report_type: str):
    requirement_graph = Graph()
    requirement_graph.parse(str(DEFAULT_VVS_REQUIREMENTS), format="turtle")
    shape_graph = Graph()
    shape_graph.parse(str(DEFAULT_VVS_SHAPES), format="turtle")
    mapping_graph = Graph()
    mapping_graph.parse(str(DEFAULT_VVS_REQUIREMENT_ANCHOR_MAP), format="turtle")
    anchor_graph = _load_graph(DEFAULT_ANCHOR_DEFINITIONS, fmt="turtle")
    requirement_graph += shape_graph

    lines = [
        "| Requirement | Mandate | Anchor | Shape | Evidence status |",
        "| --- | --- | --- | --- | --- |",
    ]
    for requirement in _active_requirements(requirement_graph, report_type):
        requirement_id = _display_value(
            requirement_graph, _first_value(requirement_graph, requirement, NIAS.requirementId)
        )
        mandate = _display_value(
            requirement_graph, _first_value(requirement_graph, requirement, NIAS.reviewMandate)
        )
        shape = _first_value(requirement_graph, requirement, NIAS.implementedByShape)
        target_classes = _requirement_target_classes(shape_graph, shape)
        target_count = sum(
            1
            for target_class in target_classes
            for _ in combined_graph.subjects(RDF.type, target_class)
        )
        if render_mode == "final":
            evidence_status = "passed" if target_count else "not targeted by supplied evidence"
        else:
            evidence_status = (
                f"draft evidence present ({target_count})"
                if target_count
                else "not assessed in draft mode"
            )
        lines.append(
            "| {requirement_id} | {mandate} | {anchor} | {shape} | {status} |".format(
                requirement_id=_escape(requirement_id),
                mandate=_escape(mandate),
                anchor=_escape(
                    _requirement_exact_anchors(
                        mapping_graph,
                        anchor_graph,
                        requirement,
                        report_type,
                    )
                ),
                shape=_escape(_display_value(requirement_graph, shape)),
                status=_escape(evidence_status),
            )
        )
    return lines


def _mappings_by_anchor_key(mapping_graph: Graph, anchor_graph: Graph, report_type: str):
    selected_mandate = _report_mandate(report_type)
    mappings = {}
    for mapping in mapping_graph.subjects(RDF.type, NIAS.RequirementMapping):
        if (mapping, NIAS.reviewMandate, selected_mandate) not in mapping_graph:
            continue
        anchor = _first_value(mapping_graph, mapping, NIAS.mappedAnchor)
        anchor_key = _first_value(anchor_graph, anchor, NIAS.anchorKey)
        if anchor_key is None:
            continue
        mappings.setdefault(str(anchor_key), []).append(mapping)
    for anchor_key in mappings:
        mappings[anchor_key].sort(key=str)
    return mappings


def _artifact_anchor_key(graph: Graph, artifact_anchor):
    anchor_key = _first_value(graph, artifact_anchor, NIAS.anchorKey)
    if anchor_key is not None:
        return str(anchor_key)
    anchor_definition = _first_value(graph, artifact_anchor, NIAS.anchorDefinition)
    anchor_key = _first_value(graph, anchor_definition, NIAS.anchorKey)
    return str(anchor_key) if anchor_key is not None else None


def _required_coverage_value(value, message: str):
    if value is None or (isinstance(value, Literal) and str(value).strip() == ""):
        raise ValueError(message)
    return value


def _reviewed_artifact_identity_value(
    graph: Graph,
    review,
    reviewed_artifact,
    artifact_field: str,
    reviewed_artifact_field: str,
):
    artifact_value = _first_value(graph, reviewed_artifact, URIRef(f"{NIAS}{artifact_field}"))
    if artifact_value is not None:
        return artifact_value
    return _first_value(graph, review, URIRef(f"{NIAS}{reviewed_artifact_field}"))


def _reviewed_content_hash(graph: Graph, artifact_anchor, reviewed_content):
    existing_hash = _first_value(graph, artifact_anchor, NIAS.contentHash)
    if existing_hash is not None:
        return existing_hash
    return Literal(f"sha256:{pdd_renderer._sha256_text(_node_text(reviewed_content) or '')}")


def _copy_subject_triples(
    source_graph: Graph,
    target_graph: Graph,
    subject,
    *,
    excluded_predicates=None,
):
    excluded = set(excluded_predicates or [])
    for _, predicate, object_node in source_graph.triples((subject, None, None)):
        if predicate in excluded:
            continue
        target_graph.add((subject, predicate, object_node))


def _safe_proof_suffix(mapping, field_review):
    raw = f"{_local_name(mapping)}-{_local_name(field_review)}"
    normalized = re.sub(r"[^A-Za-z0-9_.-]+", "-", raw).strip("-")
    digest = pdd_renderer._sha256_text(f"{mapping}|{field_review}")[:12]
    return f"{normalized}-{digest}"


def _add_requirement_coverage_proof(
    coverage_graph: Graph,
    proof_set,
    document_id: str,
    source_graph: Graph,
    requirement_graph: Graph,
    mapping_graph: Graph,
    anchor_graph: Graph,
    report_type: str,
    review,
    field_review,
    review_target,
    artifact_anchor,
    reviewed_artifact,
    mapping,
):
    mandate = _report_mandate(report_type)
    requirement = _required_coverage_value(
        _first_value(mapping_graph, mapping, NIAS.mappedRequirement),
        f"{mapping} has no mapped requirement.",
    )
    schema_anchor = _required_coverage_value(
        _first_value(mapping_graph, mapping, NIAS.mappedAnchor),
        f"{mapping} has no mapped anchor.",
    )
    shape = _required_coverage_value(
        _first_value(mapping_graph, mapping, NIAS.mappedShape),
        f"{mapping} has no mapped SHACL shape.",
    )
    requirement_id = _required_coverage_value(
        _first_value(requirement_graph, requirement, NIAS.requirementId),
        f"{requirement} has no requirement ID.",
    )
    anchor_key = _required_coverage_value(
        _first_value(anchor_graph, schema_anchor, NIAS.anchorKey),
        f"{schema_anchor} has no anchor key.",
    )
    anchor_title = _required_coverage_value(
        _first_value(anchor_graph, schema_anchor, DCTERMS.title),
        f"{schema_anchor} has no anchor title.",
    )
    reviewed_artifact_type = _required_coverage_value(
        _first_value(mapping_graph, mapping, NIAS.targetArtifactType),
        f"{mapping} has no target artifact type.",
    )
    reviewed_content = _required_coverage_value(
        _first_value(source_graph, field_review, NIAS.originalResponse),
        f"{field_review} has no reviewed content.",
    )
    review_decision = _required_coverage_value(
        _first_value(source_graph, field_review, NIAS.reviewerDecision),
        f"{field_review} has no reviewer decision.",
    )
    reviewer_feedback = _required_coverage_value(
        _first_value(source_graph, field_review, NIAS.reviewerFeedback),
        f"{field_review} has no reviewer feedback.",
    )
    content_cid = _required_coverage_value(
        _reviewed_artifact_identity_value(
            source_graph,
            review,
            reviewed_artifact,
            "artifactContentCid",
            "reviewedArtifactContentCid",
        ),
        f"{reviewed_artifact} has no reviewed artifact content CID.",
    )
    schema_cid = _required_coverage_value(
        _reviewed_artifact_identity_value(
            source_graph,
            review,
            reviewed_artifact,
            "artifactSchemaCid",
            "reviewedArtifactSchemaCid",
        ),
        f"{reviewed_artifact} has no reviewed artifact schema CID.",
    )
    schema_version_label = _required_coverage_value(
        _reviewed_artifact_identity_value(
            source_graph,
            review,
            reviewed_artifact,
            "artifactSchemaVersionLabel",
            "reviewedArtifactSchemaVersionLabel",
        ),
        f"{reviewed_artifact} has no reviewed artifact schema version label.",
    )
    content_hash = _reviewed_content_hash(source_graph, artifact_anchor, reviewed_content)

    proof = URIRef(
        f"urn:nias:{document_id}:requirement-coverage:"
        f"{_safe_proof_suffix(mapping, field_review)}"
    )

    for subject_graph, subject in [
        (mapping_graph, mapping),
        (requirement_graph, requirement),
        (anchor_graph, schema_anchor),
    ]:
        _copy_subject_triples(subject_graph, coverage_graph, subject)

    _copy_subject_triples(
        source_graph,
        coverage_graph,
        artifact_anchor,
        excluded_predicates={NIAS.anchorDefinition, NIAS.contentHash},
    )
    _copy_subject_triples(source_graph, coverage_graph, reviewed_artifact)
    _copy_subject_triples(source_graph, coverage_graph, review_target)
    _copy_subject_triples(source_graph, coverage_graph, field_review)
    _copy_subject_triples(source_graph, coverage_graph, review)

    coverage_graph.add((mapping, RDF.type, NIAS.RequirementMapping))
    coverage_graph.add((requirement, RDF.type, NIAS.ValidationVerificationRequirement))
    coverage_graph.add((schema_anchor, RDF.type, NIAS.AnchorDefinition))
    coverage_graph.add((artifact_anchor, RDF.type, NIAS.ArtifactAnchor))
    coverage_graph.add((artifact_anchor, NIAS.anchorDefinition, schema_anchor))
    coverage_graph.add((artifact_anchor, NIAS.anchorKey, Literal(str(anchor_key))))
    coverage_graph.add((artifact_anchor, NIAS.contentHash, content_hash))
    coverage_graph.add((artifact_anchor, DCTERMS.isPartOf, reviewed_artifact))
    coverage_graph.add((reviewed_artifact, RDF.type, DATA.Document))
    coverage_graph.add((reviewed_artifact, NIAS.artifactContentCid, content_cid))
    coverage_graph.add((reviewed_artifact, NIAS.artifactSchemaCid, schema_cid))
    coverage_graph.add(
        (reviewed_artifact, NIAS.artifactSchemaVersionLabel, schema_version_label)
    )
    coverage_graph.add((review_target, RDF.type, NIAS.ReviewTarget))
    coverage_graph.add((review_target, NIAS.reviewedArtifact, reviewed_artifact))
    coverage_graph.add((review_target, NIAS.reviewedAnchor, artifact_anchor))
    coverage_graph.add((field_review, RDF.type, NIAS.DocumentFieldReview))
    coverage_graph.add((field_review, NIAS.reviewTarget, review_target))
    coverage_graph.add((review, NIAS.fieldReview, field_review))
    coverage_graph.add((review, NIAS.reviewMandate, mandate))

    coverage_graph.add((proof_set, DCTERMS.hasPart, proof))
    coverage_graph.add((proof, DCTERMS.isPartOf, proof_set))
    coverage_graph.add((proof, RDF.type, NIAS.RequirementCoverageProof))
    coverage_graph.add((proof, NIAS.coverageRequirementMapping, mapping))
    coverage_graph.add((proof, NIAS.coverageRequirement, requirement))
    coverage_graph.add((proof, NIAS.coverageRequirementId, Literal(str(requirement_id))))
    coverage_graph.add((proof, NIAS.reviewMandate, mandate))
    coverage_graph.add((proof, NIAS.coverageShape, shape))
    coverage_graph.add((proof, NIAS.coverageAnchorDefinition, schema_anchor))
    coverage_graph.add((proof, NIAS.coverageAnchorKey, Literal(str(anchor_key))))
    coverage_graph.add((proof, NIAS.coverageAnchorTitle, Literal(str(anchor_title))))
    coverage_graph.add((proof, NIAS.coverageArtifactAnchor, artifact_anchor))
    coverage_graph.add((proof, NIAS.coverageReviewedArtifact, reviewed_artifact))
    coverage_graph.add(
        (proof, NIAS.coverageReviewedArtifactType, Literal(str(reviewed_artifact_type)))
    )
    coverage_graph.add((proof, NIAS.coverageReviewedArtifactContentCid, content_cid))
    coverage_graph.add((proof, NIAS.coverageReviewedArtifactSchemaCid, schema_cid))
    coverage_graph.add(
        (
            proof,
            NIAS.coverageReviewedArtifactSchemaVersionLabel,
            schema_version_label,
        )
    )
    coverage_graph.add((proof, NIAS.coverageReviewField, field_review))
    coverage_graph.add((proof, NIAS.coverageReviewedContent, reviewed_content))
    coverage_graph.add((proof, NIAS.coverageReviewedContentHash, content_hash))
    coverage_graph.add((proof, NIAS.coverageReviewDecision, review_decision))
    coverage_graph.add((proof, NIAS.coverageReviewerFeedback, reviewer_feedback))
    return proof


def build_requirement_coverage_proof_graph(
    combined_graph: Graph,
    document_id: str,
    source_artifact: str,
    generated_at: str,
    render_mode: str,
    report_type: str,
):
    requirement_graph = Graph()
    requirement_graph.parse(str(DEFAULT_VVS_REQUIREMENTS), format="turtle")
    mapping_graph = Graph()
    mapping_graph.parse(str(DEFAULT_VVS_REQUIREMENT_ANCHOR_MAP), format="turtle")
    anchor_graph = _load_graph(DEFAULT_ANCHOR_DEFINITIONS, fmt="turtle")
    mappings_by_key = _mappings_by_anchor_key(mapping_graph, anchor_graph, report_type)

    coverage_graph = Graph()
    coverage_graph.bind("data", DATA)
    coverage_graph.bind("dcterms", DCTERMS)
    coverage_graph.bind("nias", NIAS)
    coverage_graph.bind("rdf", RDF)
    proof_set = URIRef(f"urn:nias:{document_id}:requirement-coverage")
    coverage_graph.add((proof_set, RDF.type, NIAS.RequirementCoverageProofSet))
    coverage_graph.add((proof_set, DCTERMS.identifier, Literal(document_id)))
    coverage_graph.add((proof_set, DCTERMS.source, Literal(source_artifact)))
    coverage_graph.add((proof_set, DCTERMS.created, Literal(generated_at)))
    coverage_graph.add((proof_set, URIRef(f"{NIAS}renderMode"), Literal(render_mode)))
    coverage_graph.add((proof_set, URIRef(f"{NIAS}reportType"), Literal(report_type)))

    proof_nodes = []
    for review, field_review in _all_field_review_nodes(combined_graph, report_type):
        review_target = _first_value(combined_graph, field_review, NIAS.reviewTarget)
        artifact_anchor = _first_value(combined_graph, review_target, NIAS.reviewedAnchor)
        reviewed_artifact = _first_value(
            combined_graph,
            review_target,
            NIAS.reviewedArtifact,
        )
        anchor_key = _artifact_anchor_key(combined_graph, artifact_anchor)
        if not anchor_key:
            continue
        for mapping in mappings_by_key.get(anchor_key, []):
            proof_nodes.append(
                _add_requirement_coverage_proof(
                    coverage_graph,
                    proof_set,
                    document_id,
                    combined_graph,
                    requirement_graph,
                    mapping_graph,
                    anchor_graph,
                    report_type,
                    review,
                    field_review,
                    review_target,
                    artifact_anchor,
                    reviewed_artifact,
                    mapping,
                )
            )
    return coverage_graph, proof_nodes


def _validate_requirement_coverage_graph(coverage_graph: Graph):
    from pyshacl import validate

    shapes_graph = _load_graph(
        [
            DEFAULT_ARTIFACT_ANCHOR_SHAPES,
            DEFAULT_REQUIREMENT_COVERAGE_PROOF_SHAPES,
        ],
        fmt="turtle",
    )
    ontology_graph = _load_graph(DEFAULT_ONTOLOGIES, fmt="turtle")
    conforms, _, validation_text = validate(
        data_graph=coverage_graph,
        shacl_graph=shapes_graph,
        ont_graph=ontology_graph,
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        advanced=True,
    )
    if not conforms:
        raise ValueError(
            "Final render mode produced invalid requirement coverage proof sidecar.\n"
            f"{validation_text}"
        )
    return validation_text


def _coverage_jsonld_context():
    return {
        "data": str(DATA),
        "dcterms": str(DCTERMS),
        "nias": str(NIAS),
        "rdf": "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
    }


def _serialize_coverage_jsonld(coverage_graph: Graph):
    serialized = coverage_graph.serialize(
        format="json-ld",
        context=_coverage_jsonld_context(),
        auto_compact=True,
        indent=2,
    )
    return json.dumps(json.loads(serialized), indent=2, sort_keys=True) + "\n"


def _render_workflow_evidence(graph: Graph, report_type: str):
    lines = [
        "| Review document | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for review in _review_nodes(graph, report_type):
        submission = _first_value(graph, review, NIAS.hasWorkflowSubmission)
        message = _first_value(graph, submission, NIAS.workflowSubmissionConsensusMessage)
        lines.append(
            "| {review} | {submitted} | {step} | {subject} | {submitted_by} | {recipient} | {topic} | {sequence} | {timestamp} |".format(
                review=_escape(_display_value(graph, review)),
                submitted=_escape(_display_value(graph, _first_value(graph, submission, NIAS.submittedDocument))),
                step=_escape(_display_value(graph, _first_value(graph, submission, NIAS.workflowStep))),
                subject=_escape(_display_value(graph, _first_value(graph, submission, NIAS.workflowSubject))),
                submitted_by=_escape(_display_value(graph, _first_value(graph, submission, NIAS.workflowDocumentSubmittedBy))),
                recipient=_escape(_display_value(graph, _first_value(graph, submission, NIAS.workflowDocumentRecipient))),
                topic=_escape(_display_value(graph, _first_value(graph, message, HEDERA.inTopic))),
                sequence=_escape(_display_value(graph, _first_value(graph, message, HEDERA.hasSequenceNumber))),
                timestamp=_escape(_display_value(graph, _first_value(graph, message, HEDERA.hasConsensusTimestamp))),
            )
        )
    if len(lines) == 2:
        lines.append("| No workflow evidence supplied. |  |  |  |  |  |  |  |  |")
    return lines


def _render_source_evidence(input_path: Path, evidence_paths: list[Path], source_artifact: str):
    rows = [
        ("Source artifact", source_artifact),
        ("Input JSON-LD", input_path.name),
        ("Input SHA-256", pdd_renderer._sha256_file(input_path)),
    ]
    if evidence_paths:
        for index, path in enumerate(evidence_paths, start=1):
            rows.append((f"Evidence JSON-LD {index}", path.name))
            rows.append((f"Evidence SHA-256 {index}", pdd_renderer._sha256_file(path)))
    else:
        rows.append(("Evidence JSON-LD", "Not supplied"))
    return _heading_value_blocks(rows, heading_level=3)


def _render_predicate_map():
    return _heading_value_blocks(
        [
            ("Review document type", "rdf:type"),
            ("Document schema", "nias-o:documentSchema"),
            ("Final review decision", "nias-o:finalReviewDecision"),
            ("Document-level qualitative judgement", "nias-o:documentLevelQualitativeJudgement"),
            ("Section-level qualitative judgement", "nias-o:sectionQualitativeJudgement"),
            ("Anchor review", "nias-o:fieldReview"),
            ("Review target", "nias-o:reviewTarget"),
            ("Reviewed artifact", "nias-o:reviewedArtifact"),
            ("Reviewed anchor", "nias-o:reviewedAnchor"),
            ("Reviewer decision", "nias-o:reviewerDecision"),
            ("Reviewer feedback", "nias-o:reviewerFeedback"),
            ("Document author", "nias-o:documentAuthor"),
            ("Document IPFS URI", "nias-o:resourceIpfsUri"),
            ("Authenticity proof", "nias-o:authProof"),
            ("Workflow submission evidence", "nias-o:hasWorkflowSubmission"),
            ("Consensus message", "nias-o:workflowSubmissionConsensusMessage"),
            ("VVS requirement ID", "nias-o:requirementId"),
            ("VVS implementing shape", "nias-o:implementedByShape"),
        ],
        heading_level=3,
    )


def _render_filled_directive(
    directive: str,
    display_graph: Graph,
    combined_graph: Graph,
    input_path: Path,
    evidence_paths: list[Path],
    source_artifact: str,
    generated_at: str,
    render_mode: str,
    report_type: str,
):
    if directive == "titlePage.reportTitle":
        return [f"### {_report_package_title(report_type)}"]
    if directive == "titlePage.packageSummary":
        return _render_package_summary(
            display_graph,
            combined_graph,
            source_artifact,
            generated_at,
            render_mode,
            report_type,
        )
    if directive == "tableOfContents":
        return [r"\tableofcontents"]
    if directive == "review.decisionRegister":
        return _render_decision_register(display_graph, report_type)
    if directive == "review.documentQualitativeEvaluation":
        return _render_document_qualitative_evaluations(display_graph, report_type)
    if directive == "review.sectionQualitativeEvaluation":
        return _render_section_qualitative_evaluations(display_graph, report_type)
    if directive == "review.documentEnvelope":
        return _render_review_document_envelope(display_graph, report_type)
    if directive == "review.fieldFindings":
        return _render_field_findings(display_graph, report_type)
    if directive == "vvs.requirementCoverage":
        return _render_vvs_requirement_coverage(combined_graph, render_mode, report_type)
    if directive == "workflow.consensusEvidence":
        return _render_workflow_evidence(display_graph, report_type)
    if directive == "sourceEvidenceAppendix":
        return _render_source_evidence(input_path, evidence_paths, source_artifact)
    if directive == "predicateMapAppendix":
        return _render_predicate_map()
    return [f"No data provided for `{directive}`."]


def render_filled_markdown(
    profile_path: Path,
    input_path: Path,
    evidence_paths: list[Path],
    source_artifact: str,
    generated_at: str,
    render_mode: str = "draft",
    report_type: str = "validation",
):
    front_matter, body = pdd_renderer._read_front_matter_and_body(profile_path)
    review_graph, combined_graph = _parse_inputs(input_path, evidence_paths)
    display_graph = _load_display_graph(combined_graph)

    if render_mode == "final":
        try:
            _validate_structural_review_graph(review_graph)
            _validate_vvs_graph(combined_graph, report_type)
            _ensure_final_review_identity_fields(review_graph, report_type)
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Final render mode requires pySHACL. Install dependency `pyshacl`."
            ) from exc

    front_matter = pdd_renderer._insert_front_matter_metadata(
        front_matter,
        {
            "renderedDocumentType": _report_label(report_type),
            "renderMode": render_mode,
            "reportType": report_type,
            "rendererVersion": "0.1.0",
            "sourceArtifact": source_artifact,
            "generatedAt": generated_at,
        },
    )

    lines = []
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if stripped == "## Rendering Map":
            break
        if stripped == "## Validation Report Or Verification Report":
            lines.append(f"## {_report_label(report_type)}")
            continue
        directive_match = DIRECTIVE_PATTERN.match(stripped)
        if not directive_match:
            lines.append(raw_line)
            continue
        lines.extend(
            _render_filled_directive(
                directive_match.group(1),
                display_graph,
                combined_graph,
                input_path,
                evidence_paths,
                source_artifact,
                generated_at,
                render_mode,
                report_type,
            )
        )
        lines.append("")
    rendered_body = "\n".join(lines).rstrip() + "\n"
    return f"{front_matter}{rendered_body}"


def export_rendered_outputs(
    rendered_markdown: str,
    output_dir: Path,
    output_targets: list[str],
    source_artifact: str,
    generated_at: str,
    render_mode: str,
    report_type: str,
    combined_graph: Graph | None = None,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    document_hash = pdd_renderer._sha256_text(rendered_markdown)
    basename = _report_basename(report_type)
    document_id = f"{basename}-{document_hash[:12]}"

    markdown_path = output_dir / f"{basename}.md"
    markdown_path.write_text(rendered_markdown, encoding="utf-8")
    artifacts = [
        {
            "artifact": "markdown",
            "path": markdown_path.name,
            "sha256": pdd_renderer._sha256_file(markdown_path),
        }
    ]

    if "html" in output_targets:
        html_path = output_dir / f"{basename}.html"
        pdd_renderer._compile_pandoc_output(
            markdown_path,
            html_path,
            output_format="html",
            document_reference=document_id,
        )
        artifacts.append(
            {
                "artifact": "website",
                "path": html_path.name,
                "sha256": pdd_renderer._sha256_file(html_path),
            }
        )

    if "pdf" in output_targets:
        pdf_path = output_dir / f"{basename}.pdf"
        pdd_renderer._compile_pdf_output(
            markdown_path,
            pdf_path,
            document_reference=document_id,
        )
        artifacts.append(
            {
                "artifact": "pdf",
                "path": pdf_path.name,
                "sha256": pdd_renderer._sha256_file(pdf_path),
            }
        )

    if render_mode == "final":
        coverage_sidecar = None
        if combined_graph is not None:
            try:
                coverage_graph, proof_nodes = build_requirement_coverage_proof_graph(
                    combined_graph=combined_graph,
                    document_id=document_id,
                    source_artifact=source_artifact,
                    generated_at=generated_at,
                    render_mode=render_mode,
                    report_type=report_type,
                )
                _validate_requirement_coverage_graph(coverage_graph)
            except ModuleNotFoundError as exc:
                raise RuntimeError(
                    "Final render mode requires pySHACL. Install dependency `pyshacl`."
                ) from exc

            coverage_path = output_dir / f"{basename}.requirement-coverage.jsonld"
            coverage_path.write_text(
                _serialize_coverage_jsonld(coverage_graph),
                encoding="utf-8",
            )
            coverage_sidecar = {
                "artifact": "requirement-coverage-proof",
                "path": coverage_path.name,
                "proofCount": len(proof_nodes),
                "sha256": pdd_renderer._sha256_file(coverage_path),
            }

        metadata_path = output_dir / f"{basename}.metadata.jsonld"
        metadata_payload = {
            "@context": {
                "dcterms": "http://purl.org/dc/terms/",
                "nias": "https://nova.org.za/novaimpactaccountingstandard/",
            },
            "@id": f"urn:nias:{document_id}",
            "@type": "dcterms:BibliographicResource",
            "dcterms:identifier": document_id,
            "dcterms:source": source_artifact,
            "dcterms:created": generated_at,
            "nias:renderMode": render_mode,
            "nias:reportType": report_type,
            "nias:artifacts": artifacts,
        }
        if combined_graph is not None:
            metadata_payload.update(_review_identity_metadata(combined_graph, report_type))
        if coverage_sidecar is not None:
            metadata_payload["nias:requirementCoverageProofSidecar"] = coverage_sidecar
        metadata_path.write_text(
            json.dumps(metadata_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        validation_path = output_dir / f"{basename}.validation.json"
        validation_payload = {
            "documentId": document_id,
            "renderMode": render_mode,
            "reportType": report_type,
            "status": "passed",
            "sourceArtifact": source_artifact,
            "generatedAt": generated_at,
            "artifacts": artifacts,
        }
        if coverage_sidecar is not None:
            validation_payload["requirementCoverageProofSidecar"] = coverage_sidecar
        validation_path.write_text(
            json.dumps(validation_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def main():
    parser = argparse.ArgumentParser(
        description="Render NIAS Validation or Verification Report Markdown from review JSON-LD."
    )
    parser.add_argument("--profile", type=Path)
    parser.add_argument(
        "--report-type",
        choices=REPORT_TYPES,
        default="validation",
        help="Render a validation report or verification report. Defaults to validation.",
    )
    parser.add_argument("--input-jsonld", type=Path)
    parser.add_argument(
        "--evidence-jsonld",
        action="append",
        type=Path,
        default=[],
        help="Additional reviewed artifact JSON-LD graph used for final VVS validation. Repeatable.",
    )
    parser.add_argument("--source-artifact-id")
    parser.add_argument("--generated-at")
    parser.add_argument(
        "--render-mode",
        choices=["draft", "final"],
        default="draft",
        help="Draft allows placeholders; final enforces review structural and VVS SHACL validation.",
    )
    parser.add_argument(
        "--output-target",
        action="append",
        choices=["markdown", "pdf", "html"],
        help="Add compiled output target(s) for --output-dir. Repeat to include multiple targets.",
    )
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    profile_path = args.profile or DEFAULT_PROFILES[args.report_type]

    source_artifact = "blank-template"
    generated_at = datetime.now(timezone.utc).isoformat()
    if args.input_jsonld:
        source_artifact = args.source_artifact_id or args.input_jsonld.name
        generated_at = args.generated_at or generated_at
        try:
            rendered = render_filled_markdown(
                profile_path,
                args.input_jsonld,
                args.evidence_jsonld,
                source_artifact=source_artifact,
                generated_at=generated_at,
                render_mode=args.render_mode,
                report_type=args.report_type,
            )
        except (RuntimeError, ValueError) as exc:
            parser.exit(1, f"{exc}\n")
    else:
        rendered = render_blank_template(profile_path, args.report_type)

    if args.output_dir:
        output_targets = args.output_target or ["markdown"]
        combined_graph = None
        if args.input_jsonld:
            _, combined_graph = _parse_inputs(args.input_jsonld, args.evidence_jsonld)
        try:
            export_rendered_outputs(
                rendered_markdown=rendered,
                output_dir=args.output_dir,
                output_targets=output_targets,
                source_artifact=source_artifact,
                generated_at=generated_at,
                render_mode=args.render_mode,
                report_type=args.report_type,
                combined_graph=combined_graph,
            )
        except (RuntimeError, ValueError) as exc:
            parser.exit(1, f"{exc}\n")

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    elif not args.output_dir:
        print(rendered, end="")


if __name__ == "__main__":
    main()
