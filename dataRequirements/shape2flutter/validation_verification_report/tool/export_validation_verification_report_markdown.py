#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[4]
sys.path.insert(0, str(REPO_ROOT / "dataRequirements/document-rendering/tool"))
from export_workflow_report import (
    load_export_config,
    run_renderer_with_payload,
)
from nias_local_env import load_repo_env

load_repo_env(REPO_ROOT)
EXPORT_CONFIGS = {
    "validation": REPO_ROOT / "dataRequirements/document-rendering/config/validation-report-export.yaml",
    "verification": REPO_ROOT / "dataRequirements/document-rendering/config/verification-report-export.yaml",
}

DATA = "https://jellyfiiish.xyz/ns/"
HEDERA = "https://hashgraphontology.xyz/core/"
INFOCOMM = "http://w3id.org/infocomm#"
NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
XSD = "http://www.w3.org/2001/XMLSchema#"

REVIEW_CLASSES = {
    "validation": f"{NIAS}GenericDocumentReview",
    "verification": f"{NIAS}VerifiedImpactCertificateIssuanceRequestReview",
}
REVIEW_SCHEMAS = {
    "validation": f"{NIAS}document-schema/GenericDocumentReview-5.0.0",
    "verification": f"{NIAS}document-schema/DRVICIR-1.0.0",
}


def _load_json(path: Path):
    return json.loads(path.read_text(encoding="utf-8"))


def _as_list(value):
    if isinstance(value, list):
        return [item for item in value if item is not None]
    if value is None:
        return []
    return [value]


def _first_map(value):
    if isinstance(value, dict):
        return value
    for item in _as_list(value):
        if isinstance(item, dict):
            return item
    return {}


def _value(value):
    if isinstance(value, dict):
        if "@id" in value:
            return value["@id"]
        if "@value" in value:
            return value["@value"]
    return value


def _string(value, default=None):
    value = _value(value)
    if value is None:
        return default
    if isinstance(value, str):
        stripped = value.strip()
        return stripped if stripped else default
    return str(value)


def _iri(value, fallback):
    return _string(value, fallback)


def _iri_value(value):
    return [{"@id": value}]


def _literal_value(value, datatype=None):
    item = {"@value": value}
    if datatype:
        item["@type"] = datatype
    return [item]


def _optional_literal(node, predicate, value, datatype=None):
    value = _value(value)
    if value is not None:
        node[predicate] = _literal_value(value, datatype=datatype)


def _optional_iri(node, predicate, value):
    value = _string(value)
    if value:
        node[predicate] = _iri_value(value)


def _node_id(suffix):
    return f"{NIAS}{suffix}"


def _local_label(iri):
    return str(iri).rstrip("/").split("/")[-1].split("#")[-1]


def _topic_id_from_value(value, default):
    text = _string(value)
    if text and re.fullmatch(r"\d+\.\d+\.\d+", text):
        return text
    return default


def _topic_iri_from_value(value, topic_id):
    text = _string(value)
    if text and text.startswith(("http://", "https://")):
        return text
    return _node_id(f"topics/{topic_id}")


def _bool_arg(value):
    return str(value).strip().lower() in {"true", "1", "yes"}


def _review_id(args, payload, index):
    if index - 1 < len(args.review_id):
        return args.review_id[index - 1]
    submission = _first_map(payload.get(f"{NIAS}hasWorkflowSubmission"))
    submitted_document = _string(submission.get(f"{NIAS}submittedDocument"))
    if submitted_document:
        return submitted_document
    return _node_id(f"review-packages/{args.report_type}-review-{index}")


def _build_field_review_nodes(payload, review_id):
    nodes = []
    references = []
    for index, raw_field in enumerate(_as_list(payload.get(f"{NIAS}fieldReview")), start=1):
        if not isinstance(raw_field, dict):
            continue
        field_id = _iri(
            raw_field.get("@id"),
            f"{review_id}/field-review-{index}",
        )
        references.append({"@id": field_id})
        node = {
            "@id": field_id,
            "@type": [f"{NIAS}DocumentFieldReview"],
        }
        _optional_literal(node, f"{NIAS}fieldKey", raw_field.get(f"{NIAS}fieldKey"))
        _optional_literal(node, f"{NIAS}fieldTitle", raw_field.get(f"{NIAS}fieldTitle"))
        _optional_literal(node, f"{NIAS}fieldPrompt", raw_field.get(f"{NIAS}fieldPrompt"))
        _optional_literal(node, f"{NIAS}originalResponse", raw_field.get(f"{NIAS}originalResponse"))
        _optional_iri(node, f"{NIAS}reviewerDecision", raw_field.get(f"{NIAS}reviewerDecision"))
        _optional_literal(
            node,
            f"{NIAS}reviewerFeedback",
            raw_field.get(f"{NIAS}reviewerFeedback"),
        )
        nodes.append(node)
    return references, nodes


def _build_workflow_nodes(args, payload, review_id, index, generated_at):
    submission = _first_map(payload.get(f"{NIAS}hasWorkflowSubmission"))
    message = _first_map(submission.get(f"{NIAS}workflowSubmissionConsensusMessage"))

    submission_id = _iri(
        submission.get("@id"),
        f"{review_id}/workflow-submission",
    )
    workflow_id = _iri(
        submission.get(f"{NIAS}workflow") or args.workflow,
        _node_id("workflows/validation-verification"),
    )
    step_id = _iri(
        submission.get(f"{NIAS}workflowStep") or args.workflow_step,
        _node_id(f"workflow-steps/{args.report_type}-review"),
    )
    subject_id = _iri(
        submission.get(f"{NIAS}workflowSubject") or args.workflow_subject,
        _node_id("projects/project-1"),
    )
    submitted_by = _iri(
        submission.get(f"{NIAS}workflowDocumentSubmittedBy") or args.submitted_by,
        args.document_author,
    )
    recipient = _iri(
        submission.get(f"{NIAS}workflowDocumentRecipient") or args.recipient,
        _node_id("registry/nova-registry"),
    )

    topic_value = message.get(f"{HEDERA}inTopic")
    topic_id = _topic_id_from_value(topic_value, args.topic_id)
    topic_iri = _topic_iri_from_value(topic_value, topic_id)
    message_id = _iri(
        message.get("@id"),
        f"{submission_id}/consensus-message",
    )
    timestamp = _string(message.get(f"{HEDERA}hasConsensusTimestamp"), generated_at)

    submission_node = {
        "@id": submission_id,
        "@type": [f"{NIAS}WorkflowDocumentSubmission"],
        f"{NIAS}submittedDocument": _iri_value(review_id),
        f"{NIAS}workflow": _iri_value(workflow_id),
        f"{NIAS}workflowStep": _iri_value(step_id),
        f"{NIAS}workflowSubject": _iri_value(subject_id),
        f"{NIAS}workflowDocumentSubmittedBy": _iri_value(submitted_by),
        f"{NIAS}workflowDocumentRecipient": _iri_value(recipient),
        f"{NIAS}workflowSubmissionConsensusMessage": _iri_value(message_id),
    }
    message_node = {
        "@id": message_id,
        "@type": [f"{HEDERA}TopicMessage"],
        f"{HEDERA}inTopic": _iri_value(topic_iri),
        f"{HEDERA}hasConsensusTimestamp": _literal_value(
            timestamp, datatype=f"{XSD}dateTimeStamp"
        ),
    }
    sequence = _value(message.get(f"{HEDERA}hasSequenceNumber"))
    if sequence is not None:
        message_node[f"{HEDERA}hasSequenceNumber"] = _literal_value(
            int(sequence), datatype=f"{XSD}integer"
        )
    _optional_literal(message_node, f"{HEDERA}hasMessageContent", message.get(f"{HEDERA}hasMessageContent"))

    return submission_id, [
        submission_node,
        {"@id": workflow_id, "@type": [f"{NIAS}Workflow"]},
        {
            "@id": step_id,
            "@type": [f"{NIAS}WorkflowStep"],
            f"{RDFS}label": _literal_value(args.workflow_step_label or _local_label(step_id)),
        },
        {"@id": submitted_by, "@type": [f"{NIAS}PlatformUser"]},
        {"@id": recipient, "@type": [f"{INFOCOMM}CommunicationParty"]},
        {
            "@id": topic_iri,
            "@type": [f"{HEDERA}ConsensusTopic"],
            f"{HEDERA}hasTopicId": _literal_value(topic_id),
        },
        message_node,
    ]


def build_review_package(args, generated_at):
    graph = []
    for index, review_path in enumerate(args.review_json, start=1):
        payload = _load_json(review_path)
        review_id = _review_id(args, payload, index)
        field_refs, field_nodes = _build_field_review_nodes(payload, review_id)
        submission_id, workflow_nodes = _build_workflow_nodes(
            args, payload, review_id, index, generated_at
        )

        schema = args.document_schema or REVIEW_SCHEMAS[args.report_type]
        review_node = {
            "@id": review_id,
            "@type": [f"{DATA}Document", REVIEW_CLASSES[args.report_type]],
            f"{NIAS}documentSchema": _iri_value(schema),
            f"{NIAS}isEncrypted": _literal_value(_bool_arg(args.is_encrypted)),
            f"{NIAS}documentAuthor": _iri_value(args.document_author),
            f"{NIAS}authProof": _iri_value(args.auth_proof),
            f"{NIAS}resourceIpfsUri": _literal_value(
                args.resource_ipfs_uri or f"ipfs://draft-{args.report_type}-review-{index}",
                datatype=f"{XSD}anyURI",
            ),
            f"{NIAS}hasWorkflowSubmission": _iri_value(submission_id),
        }
        if field_refs:
            review_node[f"{NIAS}fieldReview"] = field_refs
        _optional_iri(review_node, f"{NIAS}finalReviewDecision", payload.get(f"{NIAS}finalReviewDecision"))
        if args.report_type == "verification":
            _optional_literal(
                review_node,
                f"{NIAS}requestedIssuanceAccountId",
                payload.get(f"{NIAS}requestedIssuanceAccountId"),
            )

        graph.extend([review_node, *field_nodes, *workflow_nodes])
    return graph


def write_review_package(path: Path, graph):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Wrap generated validation/verification review form JSON and render a NIAS report."
    )
    parser.add_argument("--report-type", choices=("validation", "verification"), default="validation")
    parser.add_argument("--review-json", action="append", type=Path, required=True)
    parser.add_argument("--review-id", action="append", default=[])
    parser.add_argument("--evidence-jsonld", action="append", type=Path, default=[])
    parser.add_argument("--review-package-output", type=Path)
    parser.add_argument("--document-schema")
    parser.add_argument("--document-author", default=f"{NIAS}users/reviewer-1")
    parser.add_argument("--resource-ipfs-uri")
    parser.add_argument("--auth-proof", default=f"{NIAS}none")
    parser.add_argument("--is-encrypted", default="false")
    parser.add_argument("--workflow", default=f"{NIAS}workflows/validation-verification")
    parser.add_argument("--workflow-step")
    parser.add_argument("--workflow-step-label")
    parser.add_argument("--workflow-subject", default=f"{NIAS}projects/project-1")
    parser.add_argument("--submitted-by")
    parser.add_argument("--recipient", default=f"{NIAS}registry/nova-registry")
    parser.add_argument("--topic-id", default="0.0.1001")
    parser.add_argument("--source-artifact-id", default="validation-verification-workflow-shell")
    parser.add_argument("--generated-at")
    parser.add_argument("--render-mode", choices=("draft", "final"), default="draft")
    parser.add_argument("--output", type=Path)
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument(
        "--output-target",
        action="append",
        choices=("markdown", "pdf", "html"),
        help="Repeat to request multiple deterministic artifact targets.",
    )
    args = parser.parse_args()

    generated_at = args.generated_at or datetime.now(timezone.utc).isoformat()
    graph = build_review_package(args, generated_at)
    export_config = load_export_config(EXPORT_CONFIGS[args.report_type])

    if args.review_package_output:
        write_review_package(args.review_package_output, graph)

    extra_renderer_args = [
        "--report-type",
        args.report_type,
        "--generated-at",
        generated_at,
    ]
    for evidence_path in args.evidence_jsonld:
        extra_renderer_args.extend(["--evidence-jsonld", str(evidence_path)])
    run_renderer_with_payload(
        repo_root=REPO_ROOT,
        config=export_config,
        renderer_payload=graph,
        render_mode=args.render_mode,
        source_artifact_id=args.source_artifact_id,
        parser=parser,
        output=args.output,
        output_dir=args.output_dir,
        output_targets=args.output_target,
        extra_renderer_args=extra_renderer_args,
    )


if __name__ == "__main__":
    main()
