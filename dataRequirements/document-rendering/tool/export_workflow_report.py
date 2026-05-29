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
