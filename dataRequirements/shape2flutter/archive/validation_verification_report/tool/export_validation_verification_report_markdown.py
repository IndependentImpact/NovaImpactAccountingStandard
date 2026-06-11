#!/usr/bin/env python3
from __future__ import annotations

import os
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[5]
ACTIVE_EXPORTER = (
    REPO_ROOT
    / "tooling/document-rendering/export_validation_verification_report_markdown.py"
)


def main():
    command = [sys.executable, str(ACTIVE_EXPORTER), *sys.argv[1:]]
    os.execv(sys.executable, command)


if __name__ == "__main__":
    raise SystemExit(main())
