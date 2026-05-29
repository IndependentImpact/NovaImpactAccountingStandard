#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
. "$ROOT_DIR/dataRequirements/shape2flutter/load-env.sh"
load_nias_env "$ROOT_DIR"
SHAPE2FLUTTER_BIN="${SHAPE2FLUTTER_BIN:-/Users/christiaanpauw/shape2flutter/shape2flutter}"
OUT_BASE="${NIAS_TMP_DIR:-/tmp}"
OUT_BASE="${OUT_BASE%/}"
OUT_ROOT="${OUT_ROOT:-$OUT_BASE/nias-shape2flutter/pdd-workflow}"
PYTHON_BIN="${PYTHON3_BIN:-python3}"
RUN_WORKFLOW_SHELL_CHECK="${RUN_WORKFLOW_SHELL_CHECK:-true}"

log_step() {
  printf '\n==> %s\n' "$1"
}

log_step "Validate Turtle artifacts"
riot --validate \
  "$ROOT_DIR"/glossary/*.ttl \
  "$ROOT_DIR"/indicators/*.ttl \
  "$ROOT_DIR"/knowledgeDomains/*.ttl \
  "$ROOT_DIR"/methodologies/*.ttl \
  "$ROOT_DIR"/dataRequirements/*.ttl \
  "$ROOT_DIR"/dataRequirements/releases/1.0.0/*.ttl \
  "$ROOT_DIR"/dataRequirements/shape2flutter/*.ttl \
  "$ROOT_DIR"/dataRequirements/fixtures/pdd-workflow/*.ttl

log_step "Run SHACL and workflow gate tests"
"$PYTHON_BIN" -m unittest discover -s "$ROOT_DIR/dataRequirements/tests" -q

log_step "Run PDD Markdown rendering regression tests"
"$PYTHON_BIN" -m unittest discover \
  -s "$ROOT_DIR/dataRequirements/tests" \
  -p "test_pdd_*.py" \
  -q

log_step "Build PDD shape2flutter artifacts"
SHAPE2FLUTTER_BIN="$SHAPE2FLUTTER_BIN" \
OUT_ROOT="$OUT_ROOT" \
  "$ROOT_DIR/dataRequirements/shape2flutter/build-pdd-workflow.sh"

log_step "Compile PDD shape2flutter preview without serving"
"$SHAPE2FLUTTER_BIN" preview \
  --schema-dir "$OUT_ROOT/schema" \
  --build-dir "$OUT_ROOT/flutter" \
  --preview-dir "$OUT_ROOT/preview" \
  --serve=false \
  --no-browser

if [ "$RUN_WORKFLOW_SHELL_CHECK" != "false" ]; then
  log_step "Run PDD workflow shell checks"
  SHAPE2FLUTTER_BIN="$SHAPE2FLUTTER_BIN" \
  OUT_ROOT="$OUT_ROOT" \
    "$ROOT_DIR/dataRequirements/shape2flutter/pdd_workflow_shell/tool/check_pdd_workflow_shell.sh"
else
  log_step "Skip PDD workflow shell checks"
fi

log_step "PDD local workflow regression complete"
