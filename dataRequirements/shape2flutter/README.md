# shape2flutter Integration

This directory contains UI-facing SHACL views for generating Flutter forms from
the NIAS validation and verification screen shapes.

The canonical SHACL constraints remain in `dataRequirements/*.ttl`. The
`validation-verification-ui-shapes.ttl` file flattens inherited/composed shapes
and adds `ui:` hints so `shape2flutter` can generate usable first-pass forms.

## Build

```bash
dataRequirements/shape2flutter/build-validation-verification.sh
```

By default this writes generated artifacts outside the repository:

- `/tmp/nias-shape2flutter/validation-verification/schema/forms.jsonld`
- `/tmp/nias-shape2flutter/validation-verification/flutter/*.dart`

Override paths when needed:

```bash
SHAPE2FLUTTER_BIN=/Users/christiaanpauw/shape2flutter/shape2flutter \
OUT_ROOT=/tmp/nias-shape2flutter/validation-verification \
dataRequirements/shape2flutter/build-validation-verification.sh
```

## Covered Screens

- Generic document review
- Document field review
- Verified impact certificate issuance request review
- Verified impact certificate issuance request
- Verified impact certificate
- Impact summary
- Data lineage report

## Notes

- The UI shapes intentionally avoid changing the canonical SHACL model.
- Repeated review fields use a bounded UI maximum so `shape2flutter` renders
  them as repeatable subforms.
- Helper subforms for workflow submissions, document references, resource
  artifacts, and time intervals are included so generated widgets are not plain
  text placeholders.
- Current lint warnings for review decision fields are expected: those controls
  use `sh:in` over SKOS concept IRIs rather than literal datatypes.
