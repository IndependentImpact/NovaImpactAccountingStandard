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
from export_workflow_report import load_export_config, run_renderer_with_payload
from export_workflow_report import (
    normalize_identity_field_names,
    schema_version_label,
    submission_event_key,
    submission_message_url,
)
from nias_local_env import load_repo_env

load_repo_env(REPO_ROOT)
EXPORT_CONFIG = (
    REPO_ROOT / "dataRequirements/document-rendering/config/monitoring-report-export.yaml"
)

DATA = "https://jellyfiiish.xyz/ns/"
DCTERMS = "http://purl.org/dc/terms/"
HEDERA = "https://hashgraphontology.xyz/core/"
IND = "http://independentimpact.org/indicator-owl/"
INFOCOMM = "http://w3id.org/infocomm#"
NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
RDFS = "http://www.w3.org/2000/01/rdf-schema#"
TIME = "http://www.w3.org/2006/time#"
XSD = "http://www.w3.org/2001/XMLSchema#"


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


def _monitoring_report_id(args, payload):
    if args.monitoring_report_id:
        return args.monitoring_report_id
    submission = _first_map(payload.get(f"{NIAS}hasWorkflowSubmission"))
    submitted_document = _string(submission.get(f"{NIAS}submittedDocument"))
    if submitted_document:
        return submitted_document
    return _node_id("monitoring-reports/monitoring-report-1")


def _build_instant_node(raw, instant_id):
    node = {"@id": instant_id, "@type": [f"{TIME}Instant"]}
    _optional_literal(
        node,
        f"{TIME}inXSDDateTimeStamp",
        raw.get(f"{TIME}inXSDDateTimeStamp"),
        datatype=f"{XSD}dateTimeStamp",
    )
    return node


def _build_interval_nodes(raw, interval_id):
    beginning_raw = _first_map(raw.get(f"{TIME}hasBeginning"))
    end_raw = _first_map(raw.get(f"{TIME}hasEnd"))
    beginning_id = _iri(beginning_raw.get("@id"), f"{interval_id}/start")
    end_id = _iri(end_raw.get("@id"), f"{interval_id}/end")
    interval_node = {
        "@id": interval_id,
        "@type": [f"{TIME}Interval"],
        f"{TIME}hasBeginning": _iri_value(beginning_id),
        f"{TIME}hasEnd": _iri_value(end_id),
    }
    return interval_id, [
        interval_node,
        _build_instant_node(beginning_raw, beginning_id),
        _build_instant_node(end_raw, end_id),
    ]


def _build_resource_node(raw, fallback_id):
    resource_id = _iri(raw.get("@id"), fallback_id)
    node = {
        "@id": resource_id,
        "@type": [f"{NIAS}ResourceArtifact"],
    }
    _optional_literal(
        node,
        f"{NIAS}resourceIpfsUri",
        raw.get(f"{NIAS}resourceIpfsUri"),
        datatype=f"{XSD}anyURI",
    )
    _optional_literal(
        node,
        f"{NIAS}resourceContentLocation",
        raw.get(f"{NIAS}resourceContentLocation"),
        datatype=f"{XSD}anyURI",
    )
    return resource_id, node


def _build_document_reference_node(raw, fallback_id):
    reference_id = _iri(raw.get("@id"), fallback_id)
    node = {
        "@id": reference_id,
        "@type": [f"{NIAS}DocumentReference"],
    }
    _optional_literal(node, f"{NIAS}documentMessageId", raw.get(f"{NIAS}documentMessageId"))
    _optional_literal(
        node,
        f"{NIAS}resourceIpfsUri",
        raw.get(f"{NIAS}resourceIpfsUri"),
        datatype=f"{XSD}anyURI",
    )
    return reference_id, node


def _build_dataset_nodes(payload, report_id):
    references = []
    nodes = []
    for index, raw_dataset in enumerate(_as_list(payload.get(f"{NIAS}usesDataset")), start=1):
        if not isinstance(raw_dataset, dict):
            continue
        dataset_id = _iri(raw_dataset.get("@id"), f"{report_id}/dataset-{index}")
        references.append({"@id": dataset_id})

        lineage_id, lineage_node = _build_document_reference_node(
            _first_map(raw_dataset.get(f"{NIAS}dataLineageReview")),
            f"{dataset_id}/data-lineage-review",
        )
        artifact_id, artifact_node = _build_resource_node(
            _first_map(raw_dataset.get(f"{NIAS}finalDatasetArtifact")),
            f"{dataset_id}/final-dataset-artifact",
        )
        dataset_node = {
            "@id": dataset_id,
            "@type": [f"{NIAS}Dataset"],
            f"{NIAS}dataLineageReview": _iri_value(lineage_id),
            f"{NIAS}finalDatasetArtifact": _iri_value(artifact_id),
        }
        _optional_literal(dataset_node, f"{DCTERMS}title", raw_dataset.get(f"{DCTERMS}title"))
        nodes.extend([dataset_node, lineage_node, artifact_node])
    return references, nodes


def _build_observation_nodes(payload, report_id, default_period_id):
    raw_observation = _first_map(payload.get(f"{NIAS}reportedObservation"))
    observation_id = _iri(raw_observation.get("@id"), f"{report_id}/reported-observation")
    period_raw = _first_map(raw_observation.get(f"{IND}timePeriod"))
    if period_raw:
        period_id, period_nodes = _build_interval_nodes(
            period_raw,
            _iri(period_raw.get("@id"), f"{observation_id}/period"),
        )
    else:
        period_id, period_nodes = default_period_id, []

    node = {
        "@id": observation_id,
        "@type": [f"{IND}IndicatorObservation"],
        f"{IND}timePeriod": _iri_value(period_id),
    }
    _optional_iri(node, f"{IND}observesIndicator", raw_observation.get(f"{IND}observesIndicator"))
    _optional_literal(node, f"{IND}obsValue", raw_observation.get(f"{IND}obsValue"))
    _optional_iri(node, f"{IND}hasUnit", raw_observation.get(f"{IND}hasUnit"))
    return observation_id, [node, *period_nodes]


def _build_workflow_nodes(args, payload, report_id, generated_at):
    submission = _first_map(payload.get(f"{NIAS}hasWorkflowSubmission"))
    message = _first_map(submission.get(f"{NIAS}workflowSubmissionConsensusMessage"))

    submission_id = _iri(submission.get("@id"), f"{report_id}/workflow-submission")
    workflow_id = _iri(
        submission.get(f"{NIAS}workflow") or args.workflow,
        _node_id("workflows/monitoring-report"),
    )
    step_id = _iri(
        submission.get(f"{NIAS}workflowStep") or args.workflow_step,
        _node_id("workflow-steps/monitoring-report"),
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
    message_id = _iri(message.get("@id"), f"{submission_id}/consensus-message")
    timestamp = _string(message.get(f"{HEDERA}hasConsensusTimestamp"), generated_at)

    submission_node = {
        "@id": submission_id,
        "@type": [f"{NIAS}WorkflowDocumentSubmission"],
        f"{NIAS}submittedDocument": _iri_value(report_id),
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


def build_monitoring_package(args, generated_at):
    payload = normalize_identity_field_names(_load_json(args.monitoring_json))
    report_id = _monitoring_report_id(args, payload)
    submission_id, submission_topic_id, submission_consensus_timestamp, workflow_nodes = _build_workflow_nodes(
        args, payload, report_id, generated_at
    )
    period_id, period_nodes = _build_interval_nodes(
        _first_map(payload.get(f"{NIAS}forPeriod")),
        f"{report_id}/monitoring-period",
    )
    observation_id, observation_nodes = _build_observation_nodes(
        payload, report_id, period_id
    )
    dataset_refs, dataset_nodes = _build_dataset_nodes(payload, report_id)
    calculation_code_id, calculation_code_node = _build_resource_node(
        _first_map(payload.get(f"{NIAS}calculationCode")),
        f"{report_id}/calculation-code",
    )
    impact_result_id, impact_result_node = _build_resource_node(
        _first_map(payload.get(f"{NIAS}impactResultResource")),
        f"{report_id}/impact-result",
    )
    calculation_report_id, calculation_report_node = _build_resource_node(
        _first_map(payload.get(f"{NIAS}calculationReport")),
        f"{report_id}/calculation-report",
    )
    artifact_content_cid = _string(payload.get(f"{NIAS}artifactContentCid"), args.artifact_content_cid)
    artifact_schema_cid = _string(payload.get(f"{NIAS}artifactSchemaCid"), args.artifact_schema_cid)
    artifact_schema_version_label = _string(
        payload.get(f"{NIAS}artifactSchemaVersionLabel"),
        args.artifact_schema_version_label
        or schema_version_label(
            schema_family="mr-schema",
            track=args.schema_track,
            generated_at=submission_consensus_timestamp,
            schema_cid=artifact_schema_cid,
        ),
    )
    aligned_pdd_content_cid = _string(
        payload.get(f"{NIAS}alignedPddContentCid"), args.aligned_pdd_content_cid
    )
    aligned_pdd_submission_topic_id = _string(
        payload.get(f"{NIAS}alignedPddSubmissionTopicId"), args.aligned_pdd_submission_topic_id
    )
    aligned_pdd_submission_consensus_timestamp = _string(
        payload.get(f"{NIAS}alignedPddSubmissionConsensusTimestamp"),
        args.aligned_pdd_submission_consensus_timestamp,
    )
    linked_dlr_content_cid = _string(
        payload.get(f"{NIAS}linkedDlrContentCid"), args.linked_dlr_content_cid
    )

    if args.render_mode == "final":
        artifact_content_cid = _required_string(
            artifact_content_cid, "artifactContentCid"
        )
        artifact_schema_cid = _required_string(artifact_schema_cid, "artifactSchemaCid")
        artifact_schema_version_label = _required_string(
            artifact_schema_version_label, "artifactSchemaVersionLabel"
        )
        aligned_pdd_content_cid = _required_string(
            aligned_pdd_content_cid, "alignedPddContentCid"
        )
        aligned_pdd_submission_topic_id = _required_string(
            aligned_pdd_submission_topic_id, "alignedPddSubmissionTopicId"
        )
        aligned_pdd_submission_consensus_timestamp = _required_string(
            aligned_pdd_submission_consensus_timestamp,
            "alignedPddSubmissionConsensusTimestamp",
        )
        linked_dlr_content_cid = _required_string(
            linked_dlr_content_cid, "linkedDlrContentCid"
        )

    report_node = {
        "@id": report_id,
        "@type": [f"{DATA}Document", f"{NIAS}MonitoringReport"],
        f"{NIAS}documentSchema": _iri_value(args.document_schema),
        f"{NIAS}isEncrypted": _literal_value(_bool_arg(args.is_encrypted)),
        f"{NIAS}documentAuthor": _iri_value(args.document_author),
        f"{NIAS}authProof": _iri_value(args.auth_proof),
        f"{NIAS}resourceIpfsUri": _literal_value(
            args.resource_ipfs_uri or "ipfs://draft-monitoring-report",
            datatype=f"{XSD}anyURI",
        ),
        f"{NIAS}hasWorkflowSubmission": _iri_value(submission_id),
        f"{NIAS}forPeriod": _iri_value(period_id),
        f"{NIAS}reportedObservation": _iri_value(observation_id),
        f"{NIAS}calculationCode": _iri_value(calculation_code_id),
        f"{NIAS}impactResultResource": _iri_value(impact_result_id),
        f"{NIAS}calculationReport": _iri_value(calculation_report_id),
        f"{NIAS}artifactContentCid": _literal_value(artifact_content_cid),
        f"{NIAS}artifactSchemaCid": _literal_value(artifact_schema_cid),
        f"{NIAS}artifactSchemaVersionLabel": _literal_value(artifact_schema_version_label),
        f"{NIAS}artifactAuthor": _iri_value(args.document_author),
        f"{NIAS}workflowSubject": _iri_value(args.workflow_subject),
        f"{NIAS}submissionTopicId": _literal_value(submission_topic_id),
        f"{NIAS}submissionConsensusTimestamp": _literal_value(
            submission_consensus_timestamp
        ),
        f"{NIAS}submissionEventKey": _literal_value(
            submission_event_key(submission_topic_id, submission_consensus_timestamp)
        ),
        f"{NIAS}submissionMessageUrl": _literal_value(
            submission_message_url(submission_topic_id, submission_consensus_timestamp)
        ),
    }
    _optional_literal(report_node, f"{NIAS}alignedPddContentCid", aligned_pdd_content_cid)
    _optional_literal(
        report_node,
        f"{NIAS}alignedPddSubmissionTopicId",
        aligned_pdd_submission_topic_id,
    )
    _optional_literal(
        report_node,
        f"{NIAS}alignedPddSubmissionConsensusTimestamp",
        aligned_pdd_submission_consensus_timestamp,
    )
    _optional_literal(report_node, f"{NIAS}linkedDlrContentCid", linked_dlr_content_cid)
    _optional_iri(
        report_node,
        f"{NIAS}alignedWithPDD",
        payload.get(f"{NIAS}alignedWithPDD") or args.aligned_pdd,
    )
    _optional_literal(
        report_node,
        f"{NIAS}reportedIndicatorLabel",
        payload.get(f"{NIAS}reportedIndicatorLabel"),
    )
    _optional_literal(
        report_node,
        f"{NIAS}requestedIssuanceAccountId",
        payload.get(f"{NIAS}requestedIssuanceAccountId"),
    )
    if dataset_refs:
        report_node[f"{NIAS}usesDataset"] = dataset_refs

    return [
        report_node,
        *period_nodes,
        *observation_nodes,
        *dataset_nodes,
        calculation_code_node,
        impact_result_node,
        calculation_report_node,
        *workflow_nodes,
    ]


def write_monitoring_package(path: Path, graph):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(graph, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(
        description="Wrap generated Monitoring Report form JSON and render a NIAS Monitoring Report."
    )
    parser.add_argument("--monitoring-json", type=Path, required=True)
    parser.add_argument("--monitoring-report-id")
    parser.add_argument("--monitoring-package-output", type=Path)
    parser.add_argument(
        "--document-schema",
        default=f"{NIAS}document-schema/MonitoringReport-6.0.0",
    )
    parser.add_argument("--document-author", default=f"{NIAS}users/monitoring-party-1")
    parser.add_argument("--resource-ipfs-uri")
    parser.add_argument("--aligned-pdd")
    parser.add_argument("--artifact-content-cid", default="bafymonitoringartifactcid")
    parser.add_argument("--artifact-schema-cid", default="bafymonitoringschemacid")
    parser.add_argument("--artifact-schema-version-label")
    parser.add_argument("--schema-track", default="main")
    parser.add_argument("--submission-consensus-timestamp")
    parser.add_argument("--aligned-pdd-content-cid")
    parser.add_argument("--aligned-pdd-submission-topic-id")
    parser.add_argument("--aligned-pdd-submission-consensus-timestamp")
    parser.add_argument("--linked-dlr-content-cid")
    parser.add_argument("--auth-proof", default=f"{NIAS}none")
    parser.add_argument("--is-encrypted", default="false")
    parser.add_argument("--workflow", default=f"{NIAS}workflows/monitoring-report")
    parser.add_argument("--workflow-step")
    parser.add_argument("--workflow-step-label")
    parser.add_argument("--workflow-subject", default=f"{NIAS}projects/project-1")
    parser.add_argument("--submitted-by")
    parser.add_argument("--recipient", default=f"{NIAS}registry/nova-registry")
    parser.add_argument("--topic-id", default="0.0.1001")
    parser.add_argument("--source-artifact-id", default="monitoring-report-workflow-shell")
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
    graph = build_monitoring_package(args, generated_at)
    export_config = load_export_config(EXPORT_CONFIG)

    if args.monitoring_package_output:
        write_monitoring_package(args.monitoring_package_output, graph)

    extra_renderer_args = ["--generated-at", generated_at]
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
