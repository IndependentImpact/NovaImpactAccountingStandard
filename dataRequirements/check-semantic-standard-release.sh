#!/usr/bin/env bash
set -euo pipefail

PYTHON_BIN="${PYTHON3_BIN:-python3}"

VERIFICATION_MODULES=(
  dataRequirements.tests.test_semantic_standard_release_package
  dataRequirements.tests.test_concept_schemes
  dataRequirements.tests.test_phase7_validation
  dataRequirements.tests.test_vvs_requirements
  dataRequirements.tests.test_requirement_anchor_traceability
  dataRequirements.tests.test_pdd_output_compilation
  dataRequirements.tests.test_monitoring_report_rendering
  dataRequirements.tests.test_validation_verification_report_rendering
)

if [ "${1:-}" = "--list-modules" ]; then
  printf '%s\n' "${VERIFICATION_MODULES[@]}"
  exit 0
fi

if [ "$#" -ne 0 ]; then
  printf 'Usage: %s [--list-modules]\n' "$0" >&2
  exit 1
fi

printf '\n==> Running semantic standard release verification suite\n'
"$PYTHON_BIN" -m unittest "${VERIFICATION_MODULES[@]}" -q
printf '\n==> Semantic standard release verification suite complete\n'
