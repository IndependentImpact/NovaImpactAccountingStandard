#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)"
. "$ROOT_DIR/dataRequirements/shape2flutter/load-env.sh"
load_nias_env "$ROOT_DIR"
SHELL_DIR="$ROOT_DIR/dataRequirements/shape2flutter/pdd_workflow_shell"
OUT_BASE="${NIAS_TMP_DIR:-/tmp}"
OUT_BASE="${OUT_BASE%/}"
OUT_ROOT="${OUT_ROOT:-$OUT_BASE/nias-shape2flutter/pdd-workflow}"

"$ROOT_DIR/dataRequirements/shape2flutter/build-pdd-workflow.sh"

rm -f "$SHELL_DIR/lib/generated"/*.dart
cp "$OUT_ROOT/flutter"/*.dart "$SHELL_DIR/lib/generated/"

if command -v flutter >/dev/null 2>&1; then
  (cd "$SHELL_DIR" && flutter pub get >/dev/null)
fi

if command -v dart >/dev/null 2>&1; then
  dart format "$SHELL_DIR/lib" "$SHELL_DIR/test" >/dev/null
fi

printf 'PDD workflow shell generated forms copied to %s\n' "$SHELL_DIR/lib/generated"
