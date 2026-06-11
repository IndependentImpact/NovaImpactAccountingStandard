#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
TOOLING_DIR = Path(__file__).resolve().parent
if str(TOOLING_DIR) not in sys.path:
    sys.path.insert(0, str(TOOLING_DIR))
from export_workflow_report import (
    load_export_config,
    normalize_identity_field_names,
    run_renderer_with_payload,
    schema_version_label,
    submission_event_key,
    submission_message_url,
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
REVIEW_DECISIONS = {
    f"{NIAS}review-approve",
    f"{NIAS}review-forward-action-request",
    f"{NIAS}review-corrective-action-request",
    f"{NIAS}review-reject",
}
FINAL_REVIEW_DECISIONS = {
    f"{NIAS}review-approve",
    f"{NIAS}review-reject",
}
HEDERA_ACCOUNT_ID_PATTERN = re.compile(r"^\d+\.\d+\.\d+$")


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


def _required_string(value, field_name):
    text = _string(value)
    if text:
        return text
    raise ValueError(f"{field_name} is required.")


def _required_iri(node, predicate, value, field_name):
    node[predicate] = _iri_value(_required_string(value, field_name))


def _required_literal(node, predicate, value, field_name, datatype=None):
    node[predicate] = _literal_value(
        _required_string(value, field_name),
        datatype=datatype,
    )


def _required_review_decision(node, predicate, value, field_name, allowed_values):
    decision = _required_string(value, field_name)
    if decision not in allowed_values:
        raise ValueError(
            f"{field_name} must be one of: {', '.join(sorted(allowed_values))}."
        )
    node[predicate] = _iri_value(decision)


def _required_hedera_account_id(node, predicate, value, field_name):
    account_id = _required_string(value, field_name)
    if not HEDERA_ACCOUNT_ID_PATTERN.fullmatch(account_id):
        raise ValueError(f"{field_name} must match shard.realm.num.")
    node[predicate] = _literal_value(account_id)


def _first_review_target(payload):
    fields = _as_list(payload.get(f"{NIAS}fieldReview"))
    if not fields:
        return {}
    first_field = _first_map(fields[0])
    return _first_map(first_field.get(f"{NIAS}reviewTarget"))


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


def _anchor_key_from_iri(anchor_iri):
    if not anchor_iri:
        return None
    text = str(anchor_iri)
    if "/anchors/" in text:
        return text.split("/anchors/", 1)[1]
    return _local_label(text)


def _build_review_target_support_nodes(
    args,
    review_id,
    field_id,
    index,
    reviewed_artifact,
    reviewed_anchor,
    field_title,
    generated_at,
):
    if not reviewed_artifact and not reviewed_anchor:
        return []

    support_id = f"{field_id}/support"
    artifact_submission_id = f"{support_id}/reviewed-artifact-submission"
    artifact_step_id = f"{support_id}/reviewed-artifact-step"
    artifact_message_id = f"{artifact_submission_id}/consensus-message"
    topic_id = args.topic_id
    topic_iri = _node_id(f"topics/{topic_id}")
    workflow_id = _node_id("workflows/review-target-support")
    submitted_by = _iri(args.submitted_by, args.document_author)
    recipient = _iri(args.recipient, _node_id("registry/nova-registry"))

    nodes = [
        {"@id": workflow_id, "@type": [f"{NIAS}Workflow"]},
        {
            "@id": artifact_step_id,
            "@type": [f"{NIAS}WorkflowStep"],
            f"{RDFS}label": _literal_value("Capture reviewed artifact support"),
        },
        {"@id": submitted_by, "@type": [f"{NIAS}PlatformUser"]},
        {"@id": recipient, "@type": [f"{INFOCOMM}CommunicationParty"]},
        {
            "@id": topic_iri,
            "@type": [f"{HEDERA}ConsensusTopic"],
            f"{HEDERA}hasTopicId": _literal_value(topic_id),
        },
        {
            "@id": artifact_message_id,
            "@type": [f"{HEDERA}TopicMessage"],
            f"{HEDERA}inTopic": _iri_value(topic_iri),
            f"{HEDERA}hasConsensusTimestamp": _literal_value(
                generated_at, datatype=f"{XSD}dateTimeStamp"
            ),
            f"{HEDERA}hasSequenceNumber": _literal_value(
                index, datatype=f"{XSD}integer"
            ),
        },
    ]

    if reviewed_artifact:
        nodes.extend(
            [
                {
                    "@id": reviewed_artifact,
                    "@type": [f"{DATA}Document"],
                    f"{NIAS}documentSchema": _iri_value(
                        f"{NIAS}document-schema/ReviewedArtifact-1.0.0"
                    ),
                    f"{NIAS}isEncrypted": _literal_value(False),
                    f"{NIAS}documentAuthor": _iri_value(args.document_author),
                    f"{NIAS}authProof": _iri_value(args.auth_proof),
                    f"{NIAS}resourceIpfsUri": _literal_value(
                        f"ipfs://review-target-support-{index}",
                        datatype=f"{XSD}anyURI",
                    ),
                    f"{NIAS}hasWorkflowSubmission": _iri_value(artifact_submission_id),
                },
                {
                    "@id": artifact_submission_id,
                    "@type": [f"{NIAS}WorkflowDocumentSubmission"],
                    f"{NIAS}submittedDocument": _iri_value(reviewed_artifact),
                    f"{NIAS}workflow": _iri_value(workflow_id),
                    f"{NIAS}workflowStep": _iri_value(artifact_step_id),
                    f"{NIAS}workflowSubject": _iri_value(args.workflow_subject),
                    f"{NIAS}workflowDocumentSubmittedBy": _iri_value(submitted_by),
                    f"{NIAS}workflowDocumentRecipient": _iri_value(recipient),
                    f"{NIAS}workflowSubmissionConsensusMessage": _iri_value(
                        artifact_message_id
                    ),
                },
            ]
        )

    if reviewed_anchor:
        anchor_key = _anchor_key_from_iri(reviewed_anchor)
        anchor_definition_id = f"{support_id}/anchor-definition"
        anchor_definition = {
            "@id": anchor_definition_id,
            "@type": [f"{NIAS}AnchorDefinition"],
            f"{NIAS}anchorKey": _literal_value(anchor_key),
            "http://purl.org/dc/terms/title": _literal_value(
                field_title or _local_label(anchor_key)
            ),
            f"{NIAS}sourceShape": _iri_value(f"{NIAS}ReviewTargetShape"),
            f"{NIAS}renderOrder": _literal_value(index, datatype=f"{XSD}integer"),
        }
        anchor_node = {
            "@id": reviewed_anchor,
            "@type": [f"{NIAS}ArtifactAnchor"],
            f"{NIAS}anchorDefinition": _iri_value(anchor_definition_id),
            f"{NIAS}anchorKey": _literal_value(anchor_key),
            f"{NIAS}sourceNode": _iri_value(reviewed_artifact or review_id),
        }
        if reviewed_artifact:
            anchor_node["http://purl.org/dc/terms/isPartOf"] = _iri_value(
                reviewed_artifact
            )
        nodes.extend([anchor_definition, anchor_node])

    return nodes


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


def _build_field_review_nodes(args, payload, review_id, generated_at):
    nodes = []
    references = []
    support_nodes = []
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

        raw_target = _first_map(raw_field.get(f"{NIAS}reviewTarget"))
        target_id = _iri(
            raw_target.get("@id"),
            f"{field_id}/review-target",
        )
        target_node = {
            "@id": target_id,
            "@type": [f"{NIAS}ReviewTarget"],
        }
        reviewed_artifact = _string(
            raw_target.get(f"{NIAS}reviewedArtifact")
            or raw_field.get(f"{NIAS}reviewedArtifact")
        )
        reviewed_anchor = _string(
            raw_target.get(f"{NIAS}reviewedAnchor")
            or raw_field.get(f"{NIAS}reviewedAnchor")
        )
        _required_iri(
            target_node,
            f"{NIAS}reviewedArtifact",
            reviewed_artifact,
            f"Field review {index} reviewedArtifact",
        )
        _required_iri(
            target_node,
            f"{NIAS}reviewedAnchor",
            reviewed_anchor,
            f"Field review {index} reviewedAnchor",
        )
        node[f"{NIAS}reviewTarget"] = _iri_value(target_id)
        _required_literal(
            node,
            f"{NIAS}fieldTitle",
            raw_field.get(f"{NIAS}fieldTitle"),
            f"Field review {index} fieldTitle",
        )
        _required_literal(
            node,
            f"{NIAS}fieldPrompt",
            raw_field.get(f"{NIAS}fieldPrompt"),
            f"Field review {index} fieldPrompt",
        )
        _required_literal(
            node,
            f"{NIAS}originalResponse",
            raw_field.get(f"{NIAS}originalResponse"),
            f"Field review {index} originalResponse",
        )
        _required_review_decision(
            node,
            f"{NIAS}reviewerDecision",
            raw_field.get(f"{NIAS}reviewerDecision"),
            f"Field review {index} reviewerDecision",
            REVIEW_DECISIONS,
        )
        _required_literal(
            node,
            f"{NIAS}reviewerFeedback",
            raw_field.get(f"{NIAS}reviewerFeedback"),
            f"Field review {index} reviewerFeedback",
        )
        nodes.extend([node, target_node])
        support_nodes.extend(
            _build_review_target_support_nodes(
                args,
                review_id,
                field_id,
                index,
                reviewed_artifact,
                reviewed_anchor,
                _string(raw_field.get(f"{NIAS}fieldTitle")),
                generated_at,
            )
        )
    return references, nodes, support_nodes


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

    return submission_id, topic_id, timestamp, [
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
    seen = set()

    def add_nodes(*nodes):
        for node in nodes:
            node_id = node.get("@id")
            if node_id is None:
                raise ValueError("Generated review-package nodes must include @id.")
            if node_id in seen:
                continue
            seen.add(node_id)
            graph.append(node)

    for index, review_path in enumerate(args.review_json, start=1):
        payload = normalize_identity_field_names(_load_json(review_path))
        review_id = _review_id(args, payload, index)
        field_refs, field_nodes, support_nodes = _build_field_review_nodes(
            args, payload, review_id, generated_at
        )
        submission_id, submission_topic_id, submission_consensus_timestamp, workflow_nodes = _build_workflow_nodes(
            args, payload, review_id, index, generated_at
        )
        review_target = normalize_identity_field_names(_first_review_target(payload))
        reviewed_artifact_content_cid = _string(
            payload.get(f"{NIAS}reviewedArtifactContentCid")
        )
        if not reviewed_artifact_content_cid:
            reviewed_artifact_content_cid = _string(
                review_target.get(f"{NIAS}reviewedArtifactContentCid")
            )
        reviewed_artifact_schema_cid = _string(
            payload.get(f"{NIAS}reviewedArtifactSchemaCid")
        ) or _string(review_target.get(f"{NIAS}reviewedArtifactSchemaCid"))
        reviewed_artifact_schema_version_label = _string(
            payload.get(f"{NIAS}reviewedArtifactSchemaVersionLabel")
        ) or _string(review_target.get(f"{NIAS}reviewedArtifactSchemaVersionLabel"))
        reviewed_submission_topic_id = _string(
            payload.get(f"{NIAS}reviewedSubmissionTopicId")
        ) or _string(review_target.get(f"{NIAS}reviewedSubmissionTopicId"))
        reviewed_submission_consensus_timestamp = _string(
            payload.get(f"{NIAS}reviewedSubmissionConsensusTimestamp")
        ) or _string(review_target.get(f"{NIAS}reviewedSubmissionConsensusTimestamp"))
        reviewed_dlr_content_cid = _string(
            payload.get(f"{NIAS}reviewedDlrContentCid")
        ) or _string(review_target.get(f"{NIAS}reviewedDlrContentCid"))
        artifact_content_cid = _string(payload.get(f"{NIAS}artifactContentCid"), f"bafy{args.report_type}artifactcid{index}")
        artifact_schema_cid = _string(payload.get(f"{NIAS}artifactSchemaCid"), f"bafy{args.report_type}schemacid")
        artifact_schema_version_label = _string(
            payload.get(f"{NIAS}artifactSchemaVersionLabel"),
            schema_version_label(
                schema_family=f"{args.report_type}-schema",
                track="main",
                generated_at=submission_consensus_timestamp,
                schema_cid=artifact_schema_cid,
            ),
        )
        artifact_author = _string(payload.get(f"{NIAS}artifactAuthor"), args.document_author)
        workflow_subject = _string(payload.get(f"{NIAS}workflowSubject"), args.workflow_subject)

        if args.render_mode == "final":
            _required_string(reviewed_artifact_content_cid, "reviewedArtifactContentCid")
            _required_string(reviewed_submission_topic_id, "reviewedSubmissionTopicId")
            _required_string(
                reviewed_submission_consensus_timestamp,
                "reviewedSubmissionConsensusTimestamp",
            )
            if args.report_type == "verification":
                _required_string(reviewed_dlr_content_cid, "reviewedDlrContentCid")

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
            f"{NIAS}artifactContentCid": _literal_value(artifact_content_cid),
            f"{NIAS}artifactSchemaCid": _literal_value(artifact_schema_cid),
            f"{NIAS}artifactSchemaVersionLabel": _literal_value(artifact_schema_version_label),
            f"{NIAS}artifactAuthor": _iri_value(artifact_author),
            f"{NIAS}workflowSubject": _iri_value(workflow_subject),
            f"{NIAS}submissionTopicId": _literal_value(submission_topic_id),
            f"{NIAS}submissionConsensusTimestamp": _literal_value(submission_consensus_timestamp),
            f"{NIAS}submissionEventKey": _literal_value(
                submission_event_key(submission_topic_id, submission_consensus_timestamp)
            ),
            f"{NIAS}submissionMessageUrl": _literal_value(
                submission_message_url(submission_topic_id, submission_consensus_timestamp)
            ),
            f"{NIAS}reviewedArtifactType": _literal_value(
                "pdd" if args.report_type == "validation" else "monitoring-report"
            ),
        }
        if reviewed_artifact_content_cid:
            review_node[f"{NIAS}reviewedArtifactContentCid"] = _literal_value(
                reviewed_artifact_content_cid
            )
        if reviewed_artifact_schema_cid:
            review_node[f"{NIAS}reviewedArtifactSchemaCid"] = _literal_value(
                reviewed_artifact_schema_cid
            )
        if reviewed_artifact_schema_version_label:
            review_node[f"{NIAS}reviewedArtifactSchemaVersionLabel"] = _literal_value(
                reviewed_artifact_schema_version_label
            )
        if reviewed_submission_topic_id:
            review_node[f"{NIAS}reviewedSubmissionTopicId"] = _literal_value(
                reviewed_submission_topic_id
            )
        if reviewed_submission_consensus_timestamp:
            review_node[f"{NIAS}reviewedSubmissionConsensusTimestamp"] = _literal_value(
                reviewed_submission_consensus_timestamp
            )
        if reviewed_dlr_content_cid:
            review_node[f"{NIAS}reviewedDlrContentCid"] = _literal_value(
                reviewed_dlr_content_cid
            )
        if field_refs:
            review_node[f"{NIAS}fieldReview"] = field_refs
        _required_review_decision(
            review_node,
            f"{NIAS}finalReviewDecision",
            payload.get(f"{NIAS}finalReviewDecision"),
            "finalReviewDecision",
            FINAL_REVIEW_DECISIONS,
        )
        if args.report_type == "verification":
            _required_hedera_account_id(
                review_node,
                f"{NIAS}requestedIssuanceAccountId",
                payload.get(f"{NIAS}requestedIssuanceAccountId"),
                "requestedIssuanceAccountId",
            )

        add_nodes(review_node, *field_nodes, *support_nodes, *workflow_nodes)
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
