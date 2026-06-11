# Legacy Reference Freeze

Freeze date: 2026-05-14

Phase 0 treats the current `reference/` R adapters and JSON schemas as frozen
legacy inputs. They are retained as evidence of previous platform behavior and
should not be changed to match the new SHACL model.

If legacy behavior needs to be preserved, add compatibility logic outside
`reference/` and keep this directory as the audit baseline. If a legacy artifact
must be corrected, update `dataRequirements/legacy-reference-manifest.sha256`
in the same change and document why the freeze was intentionally moved.

The frozen artifact inventory is recorded in:

- `dataRequirements/legacy-reference-manifest.sha256`

The migration field inventory is recorded in:

- `dataRequirements/legacy-field-map.csv`
