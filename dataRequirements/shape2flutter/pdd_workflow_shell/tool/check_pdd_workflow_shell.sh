#!/usr/bin/env bash
set -euo pipefail

SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"

"$SHELL_DIR/tool/prepare_pdd_workflow_shell.sh"

cd "$SHELL_DIR"
flutter test
flutter analyze
flutter build web
