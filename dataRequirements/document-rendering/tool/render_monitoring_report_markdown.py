#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
from datetime import datetime, timezone
from pathlib import Path

from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, Namespace

import render_pdd_markdown as pdd_renderer


REPO_ROOT = Path(__file__).resolve().parents[3]
DEFAULT_PROFILE = (
    REPO_ROOT / "dataRequirements/document-rendering/monitoring-report-rendering-profile.md"
)
DEFAULT_MONITORING_ANCHOR_DEFINITIONS = (
    REPO_ROOT / "dataRequirements/mappings/monitoring-anchor-definitions.ttl"
)
DEFAULT_STRUCTURAL_SHAPES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-reference-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-shapes.ttl",
    REPO_ROOT / "dataRequirements/monitoring-report-shapes.ttl",
]
DEFAULT_ONTOLOGIES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

DIRECTIVE_PATTERN = re.compile(r"^\{\{ render: ([a-zA-Z0-9_.-]+) \}\}$")

DATA = Namespace("https://jellyfiiish.xyz/ns/")
DCTERMS = Namespace("http://purl.org/dc/terms/")
HEDERA = Namespace("https://hashgraphontology.xyz/core/")
IND = Namespace("http://independentimpact.org/indicator-owl/")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
RDFS = Namespace("http://www.w3.org/2000/01/rdf-schema#")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
TIME = Namespace("http://www.w3.org/2006/time#")


def _load_graph(paths, *, fmt=None):
    graph = Graph()
    for path in paths:
        graph.parse(str(path), format=fmt)
    return graph


def _load_jsonld_graph(path: Path):
    graph = Graph()
    graph.parse(str(path), format="json-ld")
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


def _heading_value_blocks(rows, heading_level: int = 4):
    marker = "#" * heading_level
    lines: list[str] = []
    row_items = list(rows)
    for index, (heading, value) in enumerate(row_items):
        lines.append(f"{marker} {heading}")
        text = "" if value is None else str(value).strip()
        lines.append(text if text else "_Not provided._")
        if index < len(row_items) - 1:
            lines.append("")
    return lines


def _monitoring_reports(graph: Graph):
    return sorted(graph.subjects(RDF.type, NIAS.MonitoringReport), key=lambda item: _display_value(graph, item))


def _node_text(node) -> str | None:
    if node is None:
        return None
    if isinstance(node, Literal):
        return str(node.toPython())
    return str(node)


def _first_node_text(graph: Graph, subject, predicate) -> str | None:
    return _node_text(_first_value(graph, subject, predicate))


def _monitoring_identity_metadata(graph: Graph) -> dict:
    reports = _monitoring_reports(graph)
    if not reports:
        return {}
    report = reports[0]
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
        "alignedPddContentCid",
        "alignedPddSubmissionTopicId",
        "alignedPddSubmissionConsensusTimestamp",
        "linkedDlrContentCid",
    ):
        value = _first_node_text(graph, report, URIRef(f"{NIAS}{field}"))
        if value:
            metadata[f"nias:{field}"] = value
    return metadata


def _ensure_final_identity_fields(graph: Graph):
    reports = _monitoring_reports(graph)
    if not reports:
        return
    report = reports[0]
    required_fields = (
        "alignedPddContentCid",
        "alignedPddSubmissionTopicId",
        "alignedPddSubmissionConsensusTimestamp",
        "linkedDlrContentCid",
    )
    for field in required_fields:
        if not _first_node_text(graph, report, URIRef(f"{NIAS}{field}")):
            raise ValueError(f"{field} is required in final render mode.")


def _load_display_graph(data_graph: Graph):
    display_graph = Graph()
    for triple in data_graph:
        display_graph.add(triple)
    for ontology_path in DEFAULT_ONTOLOGIES:
        display_graph.parse(str(ontology_path), format="turtle")
    return display_graph


def _render_blank_directive(directive: str):
    if directive == "titlePage.reportTitle":
        return ["### _[Monitoring Report package title]_"]
    if directive == "titlePage.packageSummary":
        return _heading_value_blocks(
            [
                ("Report documents", "**[required]** _[to be populated]_"),
                ("Aligned PDD version", "**[required]** _[to be populated]_"),
                ("Monitoring period", "**[required]** _[to be populated]_"),
                ("Measured observations", "**[required]** _[to be populated]_"),
                ("Datasets", "**[required]** _[to be populated]_"),
                ("Issuance account", "**[required]** _[to be populated]_"),
                ("Generated at", "**[optional]** _[to be populated]_"),
                ("Rendering mode", "**[optional]** _[draft or final]_"),
                ("Source artifact", "**[optional]** _[to be populated]_"),
            ],
            heading_level=4,
        )
    if directive == "monitoring.documentEnvelope":
        return [
            "| Monitoring report | Schema | Author | Aligned PDD | IPFS URI | Encrypted | Auth proof |",
            "| --- | --- | --- | --- | --- | --- | --- |",
            "| **[required]** _[report document]_ | _[schema IRI]_ | _[author]_ | _[PDD version]_ | _[IPFS URI]_ | _[yes/no]_ | _[proof type]_ |",
        ]
    if directive == "monitoring.period":
        return [
            "| Monitoring report | Indicator label | Start | End |",
            "| --- | --- | --- | --- |",
            "| **[required]** _[report document]_ | _[indicator]_ | _[start]_ | _[end]_ |",
        ]
    if directive == "monitoring.observation":
        return [
            "| Monitoring report | Observation | Indicator | Value | Unit | Observation period |",
            "| --- | --- | --- | ---: | --- | --- |",
            "| **[required]** _[report document]_ | _[observation]_ | _[indicator]_ | _[value]_ | _[unit]_ | _[period]_ |",
        ]
    if directive == "monitoring.datasets":
        return [
            "| Monitoring report | Dataset | Dataset name | Data lineage message | Data lineage IPFS | Final dataset IPFS |",
            "| --- | --- | --- | --- | --- | --- |",
            "| **[required]** _[report document]_ | _[dataset]_ | _[name]_ | _[message ID]_ | _[IPFS URI]_ | _[IPFS URI]_ |",
        ]
    if directive == "monitoring.resources":
        return [
            "| Monitoring report | Calculation code | Impact result | Calculation report | Issuance account |",
            "| --- | --- | --- | --- | --- |",
            "| **[required]** _[report document]_ | _[IPFS URI]_ | _[IPFS URI]_ | _[IPFS URI]_ | _[account]_ |",
        ]
    if directive == "workflow.consensusEvidence":
        return [
            "| Monitoring report | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |",
            "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
            "| **[required]** _[report document]_ | _[submitted document]_ | _[workflow step]_ | _[subject]_ | _[submitter]_ | _[recipient]_ | _[topic]_ | _[sequence]_ | _[timestamp]_ |",
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
                ("Monitoring report type", "rdf:type"),
                ("Document schema", "nias-o:documentSchema"),
                ("Aligned PDD version", "nias-o:alignedWithPDD"),
                ("Monitoring period", "nias-o:forPeriod"),
                ("Reported observation", "nias-o:reportedObservation"),
                ("Dataset evidence", "nias-o:usesDataset"),
                ("Calculation code", "nias-o:calculationCode"),
                ("Impact result", "nias-o:impactResultResource"),
                ("Calculation report", "nias-o:calculationReport"),
                ("Requested issuance account", "nias-o:requestedIssuanceAccountId"),
            ],
            heading_level=3,
        )
    return [f"- **[optional]** {directive}: _[to be populated]_"]


def render_blank_template(profile_path: Path):
    front_matter, body = pdd_renderer._read_front_matter_and_body(profile_path)
    front_matter = pdd_renderer._insert_front_matter_metadata(
        front_matter,
        {"renderedDocumentType": "Monitoring Report"},
    )
    lines = []
    for raw_line in body.splitlines():
        stripped = raw_line.strip()
        if stripped == "## Rendering Map":
            break
        directive_match = DIRECTIVE_PATTERN.match(stripped)
        if not directive_match:
            lines.append(raw_line)
            continue
        lines.extend(_render_blank_directive(directive_match.group(1)))
        lines.append("")
    rendered_body = "\n".join(lines).rstrip() + "\n"
    return f"{front_matter}{rendered_body}"


def _validate_structural_monitoring_graph(report_graph: Graph):
    from pyshacl import validate

    shapes_graph = _load_graph(DEFAULT_STRUCTURAL_SHAPES, fmt="turtle")
    ontology_graph = _load_graph(DEFAULT_ONTOLOGIES, fmt="turtle")
    conforms, _, validation_text = validate(
        data_graph=report_graph,
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
            "Final render mode requires structurally conformant Monitoring Report input.\n"
            f"{validation_text}"
        )
    return validation_text


def _render_package_summary(
    graph: Graph,
    source_artifact: str,
    generated_at: str,
    render_mode: str,
):
    reports = _monitoring_reports(graph)
    datasets = sum(len(_sorted_values(graph, report, NIAS.usesDataset)) for report in reports)
    observations = sum(1 for report in reports if _first_value(graph, report, NIAS.reportedObservation) is not None)
    aligned = ", ".join(
        _display_value(graph, _first_value(graph, report, NIAS.alignedWithPDD))
        for report in reports
    ) or "Unavailable"
    accounts = ", ".join(
        _display_value(graph, _first_value(graph, report, NIAS.requestedIssuanceAccountId))
        for report in reports
    ) or "Unavailable"
    return _heading_value_blocks(
        [
            ("Report documents", len(reports)),
            ("Aligned PDD version", aligned),
            ("Measured observations", observations),
            ("Datasets", datasets),
            ("Issuance account", accounts),
            ("Generated at", generated_at),
            ("Rendering mode", render_mode),
            ("Source artifact", source_artifact),
        ],
        heading_level=4,
    )


def _resource_location(graph: Graph, resource):
    ipfs = _first_value(graph, resource, NIAS.resourceIpfsUri)
    if ipfs is not None:
        return _display_value(graph, ipfs)
    location = _first_value(graph, resource, NIAS.resourceContentLocation)
    return _display_value(graph, location)


def _period_text(graph: Graph, period):
    start = _first_value(graph, _first_value(graph, period, TIME.hasBeginning), TIME.inXSDDateTimeStamp)
    end = _first_value(graph, _first_value(graph, period, TIME.hasEnd), TIME.inXSDDateTimeStamp)
    return _display_value(graph, start), _display_value(graph, end)


def _render_document_envelope(graph: Graph):
    lines = [
        "| Monitoring report | Schema | Author | Aligned PDD | IPFS URI | Encrypted | Auth proof |",
        "| --- | --- | --- | --- | --- | --- | --- |",
    ]
    for report in _monitoring_reports(graph):
        lines.append(
            "| {report} | {schema} | {author} | {pdd} | {ipfs} | {encrypted} | {auth_proof} |".format(
                report=_escape(_display_value(graph, report)),
                schema=_escape(_display_value(graph, _first_value(graph, report, NIAS.documentSchema))),
                author=_escape(_display_value(graph, _first_value(graph, report, NIAS.documentAuthor))),
                pdd=_escape(_display_value(graph, _first_value(graph, report, NIAS.alignedWithPDD))),
                ipfs=_escape(_display_value(graph, _first_value(graph, report, NIAS.resourceIpfsUri))),
                encrypted=_escape(_display_value(graph, _first_value(graph, report, NIAS.isEncrypted))),
                auth_proof=_escape(_display_value(graph, _first_value(graph, report, NIAS.authProof))),
            )
        )
    if len(lines) == 2:
        lines.append("| No Monitoring Report document supplied. |  |  |  |  |  |  |")
    return lines


def _render_period(graph: Graph):
    lines = [
        "| Monitoring report | Indicator label | Start | End |",
        "| --- | --- | --- | --- |",
    ]
    for report in _monitoring_reports(graph):
        start, end = _period_text(graph, _first_value(graph, report, NIAS.forPeriod))
        lines.append(
            "| {report} | {label} | {start} | {end} |".format(
                report=_escape(_display_value(graph, report)),
                label=_escape(_display_value(graph, _first_value(graph, report, NIAS.reportedIndicatorLabel))),
                start=_escape(start),
                end=_escape(end),
            )
        )
    if len(lines) == 2:
        lines.append("| No monitoring period supplied. |  |  |  |")
    return lines


def _render_observation(graph: Graph):
    lines = [
        "| Monitoring report | Observation | Indicator | Value | Unit | Observation period |",
        "| --- | --- | --- | ---: | --- | --- |",
    ]
    for report in _monitoring_reports(graph):
        observation = _first_value(graph, report, NIAS.reportedObservation)
        period = _first_value(graph, observation, IND.timePeriod)
        start, end = _period_text(graph, period)
        lines.append(
            "| {report} | {observation} | {indicator} | {value} | {unit} | {period} |".format(
                report=_escape(_display_value(graph, report)),
                observation=_escape(_display_value(graph, observation)),
                indicator=_escape(_display_value(graph, _first_value(graph, observation, IND.observesIndicator))),
                value=_escape(_display_value(graph, _first_value(graph, observation, IND.obsValue))),
                unit=_escape(_display_value(graph, _first_value(graph, observation, IND.hasUnit))),
                period=_escape(f"{start} to {end}"),
            )
        )
    if len(lines) == 2:
        lines.append("| No measured impact observation supplied. |  |  |  |  |  |")
    return lines


def _render_datasets(graph: Graph):
    lines = [
        "| Monitoring report | Dataset | Dataset name | Data lineage message | Data lineage IPFS | Final dataset IPFS |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for report in _monitoring_reports(graph):
        for dataset in _sorted_values(graph, report, NIAS.usesDataset):
            lineage = _first_value(graph, dataset, NIAS.dataLineageReview)
            final_dataset = _first_value(graph, dataset, NIAS.finalDatasetArtifact)
            lines.append(
                "| {report} | {dataset} | {title} | {message} | {lineage_ipfs} | {final_ipfs} |".format(
                    report=_escape(_display_value(graph, report)),
                    dataset=_escape(_display_value(graph, dataset)),
                    title=_escape(_display_value(graph, _first_value(graph, dataset, DCTERMS.title))),
                    message=_escape(_display_value(graph, _first_value(graph, lineage, NIAS.documentMessageId))),
                    lineage_ipfs=_escape(_display_value(graph, _first_value(graph, lineage, NIAS.resourceIpfsUri))),
                    final_ipfs=_escape(_resource_location(graph, final_dataset)),
                )
            )
    if len(lines) == 2:
        lines.append("| No dataset evidence supplied. |  |  |  |  |  |")
    return lines


def _render_resources(graph: Graph):
    lines = [
        "| Monitoring report | Calculation code | Impact result | Calculation report | Issuance account |",
        "| --- | --- | --- | --- | --- |",
    ]
    for report in _monitoring_reports(graph):
        lines.append(
            "| {report} | {code} | {result} | {calculation_report} | {account} |".format(
                report=_escape(_display_value(graph, report)),
                code=_escape(_resource_location(graph, _first_value(graph, report, NIAS.calculationCode))),
                result=_escape(_resource_location(graph, _first_value(graph, report, NIAS.impactResultResource))),
                calculation_report=_escape(_resource_location(graph, _first_value(graph, report, NIAS.calculationReport))),
                account=_escape(_display_value(graph, _first_value(graph, report, NIAS.requestedIssuanceAccountId))),
            )
        )
    if len(lines) == 2:
        lines.append("| No calculation resources supplied. |  |  |  |  |")
    return lines


def _render_workflow_evidence(graph: Graph):
    lines = [
        "| Monitoring report | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |",
        "| --- | --- | --- | --- | --- | --- | --- | ---: | --- |",
    ]
    for report in _monitoring_reports(graph):
        submission = _first_value(graph, report, NIAS.hasWorkflowSubmission)
        message = _first_value(graph, submission, NIAS.workflowSubmissionConsensusMessage)
        lines.append(
            "| {report} | {submitted} | {step} | {subject} | {submitted_by} | {recipient} | {topic} | {sequence} | {timestamp} |".format(
                report=_escape(_display_value(graph, report)),
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
    return _render_blank_directive("predicateMapAppendix")


def _render_filled_directive(
    directive: str,
    display_graph: Graph,
    input_path: Path,
    evidence_paths: list[Path],
    source_artifact: str,
    generated_at: str,
    render_mode: str,
):
    if directive == "titlePage.reportTitle":
        return ["### Monitoring Report Package"]
    if directive == "titlePage.packageSummary":
        return _render_package_summary(display_graph, source_artifact, generated_at, render_mode)
    if directive == "monitoring.documentEnvelope":
        return _render_document_envelope(display_graph)
    if directive == "monitoring.period":
        return _render_period(display_graph)
    if directive == "monitoring.observation":
        return _render_observation(display_graph)
    if directive == "monitoring.datasets":
        return _render_datasets(display_graph)
    if directive == "monitoring.resources":
        return _render_resources(display_graph)
    if directive == "workflow.consensusEvidence":
        return _render_workflow_evidence(display_graph)
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
):
    front_matter, body = pdd_renderer._read_front_matter_and_body(profile_path)
    report_graph = _load_jsonld_graph(input_path)
    display_graph = _load_display_graph(report_graph)

    if render_mode == "final":
        try:
            _validate_structural_monitoring_graph(report_graph)
            _ensure_final_identity_fields(report_graph)
        except ModuleNotFoundError as exc:
            raise RuntimeError(
                "Final render mode requires pySHACL. Install dependency `pyshacl`."
            ) from exc

    front_matter = pdd_renderer._insert_front_matter_metadata(
        front_matter,
        {
            "renderedDocumentType": "Monitoring Report",
            "renderMode": render_mode,
            "reportType": "monitoring",
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
        directive_match = DIRECTIVE_PATTERN.match(stripped)
        if not directive_match:
            lines.append(raw_line)
            continue
        lines.extend(
            _render_filled_directive(
                directive_match.group(1),
                display_graph,
                input_path,
                evidence_paths,
                source_artifact,
                generated_at,
                render_mode,
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
    report_graph: Graph | None = None,
):
    output_dir.mkdir(parents=True, exist_ok=True)
    document_hash = pdd_renderer._sha256_text(rendered_markdown)
    basename = "monitoring-report"
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
        artifact_anchors = pdd_renderer._artifact_anchors(
            rendered_markdown,
            document_id,
            DEFAULT_MONITORING_ANCHOR_DEFINITIONS,
        )
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
            "nias:reportType": "monitoring",
            "nias:artifacts": artifacts,
            "nias:artifactAnchor": artifact_anchors,
        }
        if report_graph is not None:
            metadata_payload.update(_monitoring_identity_metadata(report_graph))
        metadata_path.write_text(
            json.dumps(metadata_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        validation_path = output_dir / f"{basename}.validation.json"
        validation_payload = {
            "documentId": document_id,
            "renderMode": render_mode,
            "reportType": "monitoring",
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
        description="Render NIAS Monitoring Report Markdown from Monitoring Report JSON-LD."
    )
    parser.add_argument("--profile", type=Path, default=DEFAULT_PROFILE)
    parser.add_argument("--input-jsonld", type=Path)
    parser.add_argument(
        "--evidence-jsonld",
        action="append",
        type=Path,
        default=[],
        help="Additional linked artifact JSON-LD graph recorded in source evidence. Repeatable.",
    )
    parser.add_argument("--source-artifact-id")
    parser.add_argument("--generated-at")
    parser.add_argument(
        "--render-mode",
        choices=["draft", "final"],
        default="draft",
        help="Draft allows placeholders; final enforces Monitoring Report SHACL validation.",
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
            )
        except (RuntimeError, ValueError) as exc:
            parser.exit(1, f"{exc}\n")
    else:
        rendered = render_blank_template(args.profile)

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
                report_graph=_load_jsonld_graph(args.input_jsonld) if args.input_jsonld else None,
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
