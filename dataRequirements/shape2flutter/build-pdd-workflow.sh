#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
SHAPE2FLUTTER_BIN="${SHAPE2FLUTTER_BIN:-/Users/christiaanpauw/shape2flutter/shape2flutter}"
OUT_ROOT="${OUT_ROOT:-/tmp/nias-shape2flutter/pdd-workflow}"
SHAPES_FILE="$ROOT_DIR/dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl"
SCHEMA_DIR="$OUT_ROOT/schema"
FLUTTER_DIR="$OUT_ROOT/flutter"

ALLOWED_PREFIXES="https://nova.org.za/novaimpactaccountingstandard/,https://nova.org.za/novaimpactaccountingstandard/shape2flutter/,http://w3id.org/aiao#,http://w3id.org/claimont#,http://w3id.org/impactont#,http://independentimpact.org/indicator-owl/,http://purl.org/dc/terms/,https://schema.org/,http://www.w3.org/1999/02/22-rdf-syntax-ns#,http://www.w3.org/2000/01/rdf-schema#,http://www.w3.org/2006/time#,https://hashgraphontology.xyz/core/"

mkdir -p "$SCHEMA_DIR" "$FLUTTER_DIR"

"$SHAPE2FLUTTER_BIN" lint \
  -allow-path-prefixes "$ALLOWED_PREFIXES" \
  "$SHAPES_FILE"

"$SHAPE2FLUTTER_BIN" emit-jsonld \
  -format jsonld \
  -o "$SCHEMA_DIR/forms.jsonld" \
  "$SHAPES_FILE"

"$SHAPE2FLUTTER_BIN" build \
  -outdir "$FLUTTER_DIR" \
  "$SHAPES_FILE"

printf 'shape2flutter PDD workflow output:\n'
printf '  schema: %s\n' "$SCHEMA_DIR/forms.jsonld"
printf '  dart:   %s\n' "$FLUTTER_DIR"
