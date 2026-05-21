# shape2flutter Integration

This directory contains UI-facing SHACL views for generating Flutter forms from
NIAS workflow screen shapes.

The canonical SHACL constraints remain in `dataRequirements/*.ttl`. The
`validation-verification-ui-shapes.ttl` file flattens inherited/composed shapes
and adds `ui:` hints so `shape2flutter` can generate usable first-pass forms.
The `pdd-workflow-ui-shapes.ttl` file does the same for PDD creation,
validation, and certificate issuance request forms.

For the planned PDD creation and validation workflow, see
[`pdd-workflow-roadmap.md`](pdd-workflow-roadmap.md).

## Validation And Verification Build

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

## Validation And Verification Preview

After running the build script, launch the Flutter web preview from the
generated schema and Dart files:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-verification/schema \
  --build-dir /tmp/nias-shape2flutter/validation-verification/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-verification/preview \
  --port 8080
```

The preview command builds the preview app, starts a local HTTP server, and
opens the browser. If the browser does not open automatically, use:

```text
http://localhost:8080
```

To keep the server in the terminal but avoid opening a browser automatically:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-verification/schema \
  --build-dir /tmp/nias-shape2flutter/validation-verification/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-verification/preview \
  --port 8080 \
  --no-browser
```

To only generate the preview app and web build without starting the HTTP
server:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-verification/schema \
  --build-dir /tmp/nias-shape2flutter/validation-verification/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-verification/preview \
  --serve=false \
  --no-browser
```

Use a different port if `8080` is already occupied:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-verification/schema \
  --build-dir /tmp/nias-shape2flutter/validation-verification/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-verification/preview \
  --port 3000 \
  --no-browser
```

While the server is running, these debug endpoints are useful:

- `http://localhost:8080/health`
- `http://localhost:8080/debug`
- `http://localhost:8080/files`

Stop the preview server with `Ctrl+C`.

## PDD Workflow Build

```bash
dataRequirements/shape2flutter/build-pdd-workflow.sh
```

By default this writes generated artifacts outside the repository:

- `/tmp/nias-shape2flutter/pdd-workflow/schema/forms.jsonld`
- `/tmp/nias-shape2flutter/pdd-workflow/flutter/*.dart`

Override paths when needed:

```bash
SHAPE2FLUTTER_BIN=/Users/christiaanpauw/shape2flutter/shape2flutter \
OUT_ROOT=/tmp/nias-shape2flutter/pdd-workflow \
dataRequirements/shape2flutter/build-pdd-workflow.sh
```

## PDD Workflow Preview

After running the PDD workflow build script, launch the Flutter web preview from
the generated schema and Dart files:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/pdd-workflow/schema \
  --build-dir /tmp/nias-shape2flutter/pdd-workflow/flutter \
  --preview-dir /tmp/nias-shape2flutter/pdd-workflow/preview \
  --port 8080
```

To keep the server in the terminal but avoid opening a browser automatically:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/pdd-workflow/schema \
  --build-dir /tmp/nias-shape2flutter/pdd-workflow/flutter \
  --preview-dir /tmp/nias-shape2flutter/pdd-workflow/preview \
  --port 8080 \
  --no-browser
```

To only generate the preview app and web build without starting the HTTP
server:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/pdd-workflow/schema \
  --build-dir /tmp/nias-shape2flutter/pdd-workflow/flutter \
  --preview-dir /tmp/nias-shape2flutter/pdd-workflow/preview \
  --serve=false \
  --no-browser
```

Use a different port if `8080` is already occupied:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/pdd-workflow/schema \
  --build-dir /tmp/nias-shape2flutter/pdd-workflow/flutter \
  --preview-dir /tmp/nias-shape2flutter/pdd-workflow/preview \
  --port 3000 \
  --no-browser
```

## Covered Screens

Validation and verification:

- Generic document review
- Document field review
- Verified impact certificate issuance request review
- Verified impact certificate issuance request
- Verified impact certificate
- Impact summary
- Data lineage report

PDD workflow:

- PDD Section A
- PDD Section B
- PDD Section C
- PDD certificate issuance request
- PDD Section A validation review
- PDD Section B validation review
- PDD Section C validation review

## Notes

- The UI shapes intentionally avoid changing the canonical SHACL model.
- The PDD-CIR approval gate is documented in
  [`pdd-workflow-gate.md`](pdd-workflow-gate.md); it is enforced by the workflow
  shell or Fluree-backed service, not by the generated form alone.
- Repeated review fields use a bounded UI maximum so `shape2flutter` renders
  them as repeatable subforms.
- Helper subforms for workflow submissions, document references, resource
  artifacts, and time intervals are included so generated widgets are not plain
  text placeholders.
- Current lint warnings for review decision fields are expected: those controls
  use `sh:in` over SKOS concept IRIs rather than literal datatypes.
- Current PDD workflow lint warnings for controlled vocabulary fields are
  expected for the same reason: those controls use `sh:in` over concept IRIs or
  literal branch values.
- Hedera account format validation remains in the canonical SHACL shapes. It is
  not repeated in this preview shape because the current Dart generator needs to
  escape regex end anchors before those patterns can compile in generated code.
