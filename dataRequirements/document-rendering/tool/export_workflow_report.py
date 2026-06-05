#!/usr/bin/env python3
from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

import yaml

NIAS = "https://nova.org.za/novaimpactaccountingstandard/"

ARTIFACT_IDENTITY_FIELDS = (
    "artifactContentCid",
    "artifactSchemaCid",
    "artifactSchemaVersionLabel",
    "artifactAuthor",
    "workflowSubject",
    "submissionTopicId",
    "submissionConsensusTimestamp",
)
REVIEWED_ARTIFACT_IDENTITY_FIELDS = (
    "reviewedArtifactType",
    "reviewedArtifactContentCid",
    "reviewedArtifactSchemaCid",
    "reviewedArtifactSchemaVersionLabel",
    "reviewedSubmissionTopicId",
    "reviewedSubmissionConsensusTimestamp",
)
UPSTREAM_ALIGNMENT_FIELDS = (
    "alignedPddContentCid",
    "alignedPddSubmissionTopicId",
    "alignedPddSubmissionConsensusTimestamp",
)
DLR_LINKAGE_FIELDS = (
    "linkedDlrContentCid",
    "reviewedDlrContentCid",
)
DERIVED_SUBMISSION_FIELDS = (
    "submissionEventKey",
    "submissionMessageUrl",
)

IDENTITY_FIELD_ALIASES = {
    "artifactSchemaVersionLabel": ("artifactSchemaLabel", "schemaVersionLabel"),
    "submissionTopicId": ("topicId", "submissionTopic"),
    "submissionConsensusTimestamp": ("consensusTimestamp", "submissionTimestamp"),
    "reviewedSubmissionTopicId": ("reviewedTopicId", "reviewedSubmissionTopic"),
    "reviewedSubmissionConsensusTimestamp": (
        "reviewedConsensusTimestamp",
        "reviewedSubmissionTimestamp",
    ),
}


def _nias_field(name: str) -> str:
    return f"{NIAS}{name}"


def normalize_identity_field_names(payload: dict) -> dict:
    if not isinstance(payload, dict):
        return payload
    normalized = dict(payload)
    for canonical, aliases in IDENTITY_FIELD_ALIASES.items():
        canonical_key = _nias_field(canonical)
        if canonical_key in normalized:
            continue
        for alias in aliases:
            alias_key = _nias_field(alias)
            if alias_key in normalized:
                normalized[canonical_key] = normalized[alias_key]
                break
    return normalized


def _short_cid(value: str | None, length: int = 8) -> str:
    if not value:
        return "unknown"
    cid = value.strip().removeprefix("ipfs://")
    return cid[:length] if cid else "unknown"


def schema_version_label(*, schema_family: str, track: str, generated_at: str, schema_cid: str) -> str:
    date_text = (generated_at or "").strip()[:10] or "unknown-date"
    track_text = (track or "").strip() or "default"
    return f"nias:{schema_family}:{track_text}:{date_text}:{_short_cid(schema_cid)}"


def submission_event_key(topic_id: str, consensus_timestamp: str) -> str:
    return f"{topic_id}@{consensus_timestamp}"


def submission_message_url(topic_id: str, consensus_timestamp: str) -> str:
    return f"/api/v1/topics/{topic_id}/messages/{consensus_timestamp}"


def load_export_config(path: Path) -> dict:
    try:
        config = yaml.safe_load(path.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as exc:
        raise ValueError(f"Invalid YAML export config in {path}: {exc}") from exc
    if not isinstance(config, dict):
        raise ValueError(f"Invalid export config in {path}: expected a YAML mapping.")
    return config


def evaluate_final_gate_failures(config: dict, review_payloads: dict) -> list[str]:
    failures = []
    for section, gate in (config.get("final_gate_requirements") or {}).items():
        label = gate.get("label") or section.upper()
        review = review_payloads.get(section)
        if review is None:
            failures.append(f"{label} validation review has not been submitted.")
            continue
        if review.get(f"{NIAS}finalReviewDecision") != gate.get("required_decision"):
            failures.append(f"{label} validation review is not approved.")
        if review.get(f"{NIAS}isReviewOf") != gate.get("required_review_of"):
            failures.append(f"{label} review does not point to the submitted document.")
    return failures


def _resolve_renderer_script(repo_root: Path, config: dict) -> Path:
    renderer_relative = config.get("renderer_script")
    if not renderer_relative:
        raise ValueError("Export config must define renderer_script.")
    return repo_root / renderer_relative


def run_renderer_with_payload(
    *,
    repo_root: Path,
    config: dict,
    renderer_payload: dict | list,
    render_mode: str,
    source_artifact_id: str,
    parser,
    output: Path | None = None,
    output_dir: Path | None = None,
    output_targets: list[str] | None = None,
    extra_renderer_args: list[str] | None = None,
) -> None:
    render_script = _resolve_renderer_script(repo_root, config)
    payload_name = config.get("payload_filename")
    if not payload_name:
        raise ValueError("Export config must define payload_filename.")
    with tempfile.TemporaryDirectory(prefix="nias-workflow-export-") as tmpdir:
        payload_path = Path(tmpdir) / payload_name
        payload_path.write_text(
            json.dumps(renderer_payload, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        command = [
            os.environ.get("PYTHON3_BIN") or sys.executable,
            str(render_script),
            "--input-jsonld",
            str(payload_path),
            "--render-mode",
            render_mode,
            "--source-artifact-id",
            source_artifact_id,
        ]
        command.extend(extra_renderer_args or [])

        if output:
            command.extend(["--output", str(output)])
        if output_dir:
            command.extend(["--output-dir", str(output_dir)])
            for target in output_targets or config.get("default_output_targets", ["markdown"]):
                command.extend(["--output-target", target])

        completed = subprocess.run(
            command,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )

        if completed.returncode != 0:
            parser.exit(completed.returncode, completed.stderr or completed.stdout)

        if not output and not output_dir:
            print(completed.stdout, end="")
