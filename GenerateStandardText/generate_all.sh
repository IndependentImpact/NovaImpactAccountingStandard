#!/usr/bin/env bash
# Generate all standard-text markdown files from SKOS Turtle sources.
# Run from the repository root:
#   bash GenerateStandardText/generate_all.sh
# Pass --check to exit non-zero if any generated file differs from the
# committed copy:
#   bash GenerateStandardText/generate_all.sh --check

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
TOOL="$REPO_ROOT/GenerateStandardText/tool/generate_skos_markdown.py"
OUT="$REPO_ROOT/GenerateStandardText"
GLOSSARY_DIR="$REPO_ROOT/glossary"

run_generator() {
  python "$TOOL" \
    --ttl "$1" \
    --output "$2" \
    --section-heading "$3" \
    ${CHECK_FLAG:+"--check"}
}

CHECK_FLAG=""
if [[ "${1:-}" == "--check" ]]; then
  CHECK_FLAG="--check"
fi

run_generator \
  "$GLOSSARY_DIR/NovaImpactAccountingStandardGlossary.ttl" \
  "$OUT/02-a-Glossary.md" \
  "## Glossary"

run_generator \
  "$GLOSSARY_DIR/Principle.ttl" \
  "$OUT/03-a-Principles.md" \
  "## Principles"

run_generator \
  "$GLOSSARY_DIR/GuidingReviewQuestions.ttl" \
  "$OUT/03-b-GuidingAndReviewQuestions.md" \
  "## Guiding And Review Questions"

run_generator \
  "$GLOSSARY_DIR/ReputationRules.ttl" \
  "$OUT/04-a-KnowledgeAndSkillsReputationRules.md" \
  "## Reputation Lifecycle Terms"

run_generator \
  "$GLOSSARY_DIR/ScoringRules.ttl" \
  "$OUT/05-a-ScoringRules.md" \
  "## Scoring Rules"

run_generator \
  "$GLOSSARY_DIR/ValidationVerificationStandard.ttl" \
  "$OUT/VVS-RequirementStatus.md" \
  "## Requirement Status"
