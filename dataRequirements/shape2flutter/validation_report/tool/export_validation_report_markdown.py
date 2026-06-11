#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
REPO_ROOT = Path(__file__).resolve().parents[4]
SHARED_EXPORTER = (
    REPO_ROOT
    / "tooling/document-rendering/export_validation_verification_report_markdown.py"
)


def main():
    if "--report-type" in sys.argv[1:]:
        print(
            "export_validation_report_markdown.py always renders --report-type validation.",
            file=sys.stderr,
        )
        return 2
    command = [
        sys.executable,
        str(SHARED_EXPORTER),
        "--report-type",
        "validation",
        "--workflow",
        f"{NIAS}workflows/validation-report",
        "--source-artifact-id",
        "validation-report-workflow",
        *sys.argv[1:],
    ]
    os.execv(sys.executable, command)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
