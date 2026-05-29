#!/usr/bin/env bash
set -euo pipefail

SHELL_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
ROOT_DIR="$(cd "$SHELL_DIR/../../../.." && pwd)"
. "$ROOT_DIR/dataRequirements/shape2flutter/load-env.sh"
load_nias_env "$ROOT_DIR"

"$SHELL_DIR/tool/prepare_pdd_workflow_shell.sh"

cd "$SHELL_DIR"
flutter test
flutter analyze
flutter build web
