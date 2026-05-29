from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from rdflib import BNode, Graph, Literal, URIRef
from rdflib.namespace import RDF, Namespace

import render_pdd_markdown as pdd_renderer


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROFILE = (
    REPO_ROOT
    / "dataRequirements/document-rendering/validation-verification-report-rendering-profile.md"
)
DEFAULT_VVS_REQUIREMENTS = REPO_ROOT / "glossary/ValidationVerificationStandard.ttl"
DEFAULT_VVS_SHAPES = REPO_ROOT / "dataRequirements/vvs-requirement-shapes.ttl"
DEFAULT_STRUCTURAL_SHAPES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
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
        for predicate in (RDFS.label, SKOS.prefLabel, DCTERMS.title):
            label = graph.value(node, predicate)
            if label is not None:
                return str(label)
    return _local_name(node)


def _escape(value):
    return pdd_renderer._escape_table_cell(value)


def _two_column_table(rows):
    return pdd_renderer._two_column_table(rows)


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


def _review_nodes(graph: Graph, report_type: str | None = None):
    nodes = set(graph.subjects(RDF.type, NIAS.GenericDocumentReview))
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
        return _two_column_table(
            [
                ("Report type", _report_label(report_type)),
                ("Review documents", "**[required]** _[to be populated]_"),
                ("Field reviews", "**[required]** _[to be populated]_"),
                ("Final decisions", "**[required]** _[to be populated]_"),
                ("VVS evidence targets", "**[required for final]** _[to be populated]_"),
                ("Generated at", "**[optional]** _[to be populated]_"),
                ("Rendering mode", "**[optional]** _[draft or final]_"),
                ("Source artifact", "**[optional]** _[to be populated]_"),
            ]
        )
    if directive == "tableOfContents":
        return [TOC_PLACEHOLDER]
    if directive == "review.decisionRegister":
        return [
            "| Review document | Review type | Final decision | Field reviews |",
            "| --- | --- | --- | ---: |",
            "| **[required]** _[review document]_ | _[validation or verification]_ | _[approve or reject]_ | _[field review count]_ |",
        ]
    if directive == "review.documentEnvelope":
        return [
            "| Review document | Schema | Author | IPFS URI | Encrypted | Auth proof |",
            "| --- | --- | --- | --- | --- | --- |",
            "| **[required]** _[review document]_ | _[schema IRI]_ | _[author]_ | _[IPFS URI]_ | _[yes/no]_ | _[proof type]_ |",
        ]
    if directive == "review.fieldFindings":
        return [
            "| Review document | Field | Decision | Feedback | Original response |",
            "| --- | --- | --- | --- | --- |",
            "| **[required]** _[review document]_ | _[field title]_ | _[field decision]_ | _[reviewer feedback]_ | _[submitted response]_ |",
        ]
    if directive == "vvs.requirementCoverage":
        return [
            "| Requirement | Mandate | Anchor | Shape | Evidence status |",
            "| --- | --- | --- | --- | --- |",
            "| **[required]** _[REQ-*]_ | _[validation or verification]_ | _[PDD/DLR/MR anchor]_ | _[SHACL shape]_ | _[not assessed]_ |",
        ]
    if directive == "workflow.consensusEvidence":
        return [
            "| Review document | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
            "| **[required]** _[review document]_ | _[submitted document]_ | _[workflow step]_ | _[subject]_ | _[submitter]_ | _[recipient]_ | _[topic]_ | _[sequence]_ | _[timestamp]_ |",
        ]
    if directive == "sourceEvidenceAppendix":
        return _two_column_table(
            [
                ("Input JSON-LD", "**[required]** _[to be populated]_"),
                ("Evidence JSON-LD", "**[optional]** _[to be populated]_"),
                ("Source graph hash evidence", "**[optional]** _[to be populated]_"),
            ]
        )
    if directive == "predicateMapAppendix":
        return _two_column_table(
            [
                ("Review document type", "rdf:type"),
                ("Document schema", "nias-o:documentSchema"),
                ("Document author", "nias-o:documentAuthor"),
                ("Document IPFS URI", "nias-o:resourceIpfsUri"),
                ("Authenticity proof", "nias-o:authProof"),
                ("Final review decision", "nias-o:finalReviewDecision"),
                ("Field review", "nias-o:fieldReview"),
                ("Reviewer decision", "nias-o:reviewerDecision"),
                ("Reviewer feedback", "nias-o:reviewerFeedback"),
                ("Workflow submission evidence", "nias-o:hasWorkflowSubmission"),
                ("Consensus message", "nias-o:workflowSubmissionConsensusMessage"),
                ("VVS requirement implementation", "nias-o:implementedByShape"),
            ]
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
    rendered_body = _replace_table_of_contents("\n".join(lines).rstrip()) + "\n"
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
    return _two_column_table(
        [
            ("Report type", _report_label(report_type)),
            ("Review documents", len(_review_nodes(display_graph, report_type))),
            ("Field reviews", len(_all_field_review_nodes(display_graph, report_type))),
            ("Final decisions", _review_decision_counts(display_graph, report_type)),
            ("VVS evidence targets", len(target_subjects)),
            ("Generated at", generated_at),
            ("Rendering mode", render_mode),
            ("Source artifact", source_artifact),
        ]
    )


def _render_decision_register(graph: Graph, report_type: str):
    lines = [
        "| Review document | Review type | Final decision | Field reviews |",
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
        "| Review document | Field | Decision | Feedback | Original response |",
        "| --- | --- | --- | --- | --- |",
    ]
    for review, field_review in _all_field_review_nodes(graph, report_type):
        field_title = _first_value(graph, field_review, NIAS.fieldTitle)
        field_key = _first_value(graph, field_review, NIAS.fieldKey)
        field_label = _display_value(graph, field_title) if field_title is not None else _display_value(graph, field_key)
        lines.append(
            "| {review} | {field} | {decision} | {feedback} | {response} |".format(
                review=_escape(_display_value(graph, review)),
                field=_escape(field_label),
                decision=_escape(_display_value(graph, _first_value(graph, field_review, NIAS.reviewerDecision))),
                feedback=_escape(_display_value(graph, _first_value(graph, field_review, NIAS.reviewerFeedback))),
                response=_escape(_display_value(graph, _first_value(graph, field_review, NIAS.originalResponse))),
            )
        )
    if len(lines) == 2:
        lines.append("| No field reviews supplied. |  |  |  |  |")
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


def _requirement_anchor(requirement_graph: Graph, requirement, report_type: str):
    anchors = []
    predicate = NIAS.validatedAt if report_type == "validation" else NIAS.verifiedBy
    for anchor in requirement_graph.objects(requirement, predicate):
        anchors.append(_display_value(requirement_graph, anchor))
    return ", ".join(anchors) if anchors else "Unavailable"


def _requirement_target_classes(shape_graph: Graph, shape):
    return list(shape_graph.objects(shape, SH.targetClass))


def _render_vvs_requirement_coverage(combined_graph: Graph, render_mode: str, report_type: str):
    requirement_graph = Graph()
    requirement_graph.parse(str(DEFAULT_VVS_REQUIREMENTS), format="turtle")
    shape_graph = Graph()
    shape_graph.parse(str(DEFAULT_VVS_SHAPES), format="turtle")
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
                anchor=_escape(_requirement_anchor(requirement_graph, requirement, report_type)),
                shape=_escape(_display_value(requirement_graph, shape)),
                status=_escape(evidence_status),
            )
        )
    return lines


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
    return _two_column_table(rows)


def _render_predicate_map():
    return _two_column_table(
        [
            ("Review document type", "rdf:type"),
            ("Document schema", "nias-o:documentSchema"),
            ("Final review decision", "nias-o:finalReviewDecision"),
            ("Field review", "nias-o:fieldReview"),
            ("Field key", "nias-o:fieldKey"),
            ("Field title", "nias-o:fieldTitle"),
            ("Reviewer decision", "nias-o:reviewerDecision"),
            ("Reviewer feedback", "nias-o:reviewerFeedback"),
            ("Document author", "nias-o:documentAuthor"),
            ("Document IPFS URI", "nias-o:resourceIpfsUri"),
            ("Authenticity proof", "nias-o:authProof"),
            ("Workflow submission evidence", "nias-o:hasWorkflowSubmission"),
            ("Consensus message", "nias-o:workflowSubmissionConsensusMessage"),
            ("VVS requirement ID", "nias-o:requirementId"),
            ("VVS implementing shape", "nias-o:implementedByShape"),
        ]
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
        return [TOC_PLACEHOLDER]
    if directive == "review.decisionRegister":
        return _render_decision_register(display_graph, report_type)
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
    display_graph = _load_display_graph(review_graph)

    if render_mode == "final":
        try:
            _validate_structural_review_graph(review_graph)
            _validate_vvs_graph(combined_graph, report_type)
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
    rendered_body = _replace_table_of_contents("\n".join(lines).rstrip()) + "\n"
    return f"{front_matter}{rendered_body}"


def export_rendered_outputs(
    rendered_markdown: str,
    output_dir: Path,
    output_targets: list[str],
    source_artifact: str,
    generated_at: str,
    render_mode: str,
    report_type: str,
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
        validation_path.write_text(
            json.dumps(validation_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )


def main():
    parser = argparse.ArgumentParser(
        description="Render NIAS Validation or Verification Report Markdown from review JSON-LD."
    )
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
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

    source_artifact = "blank-template"
    generated_at = datetime.now(timezone.utc).isoformat()
    if args.input_jsonld:
        source_artifact = args.source_artifact_id or args.input_jsonld.name
        generated_at = args.generated_at or generated_at
        try:
            rendered = render_filled_markdown(
                args.profile,
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
        rendered = render_blank_template(args.profile, args.report_type)

    if args.output_dir:
        output_targets = args.output_target or ["markdown"]
        try:
            export_rendered_outputs(
                rendered_markdown=rendered,
                output_dir=args.output_dir,
                output_targets=output_targets,
                source_artifact=source_artifact,
                generated_at=generated_at,
                render_mode=args.render_mode,
                report_type=args.report_type,
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
