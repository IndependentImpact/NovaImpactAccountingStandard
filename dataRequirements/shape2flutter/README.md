# shape2flutter Integration

This directory contains UI-facing SHACL views for generating Flutter forms from
NIAS workflow screen shapes.

The canonical SHACL constraints remain in `dataRequirements/*.ttl`. The
`validation-verification-ui-shapes.ttl` file flattens inherited/composed shapes
and adds `ui:` hints so `shape2flutter` can generate usable first-pass forms.
The `pdd-workflow-ui-shapes.ttl` file currently does the same for the combined
local PDD workflow preview: PDD creation, validation review, and PDD certificate
issuance request forms.

For the planned PDD creation and validation workflow, see
[`pdd-workflow-roadmap.md`](pdd-workflow-roadmap.md).

For the planned split between PDD Design, Validation Report, Monitoring Report,
and Verification Report activities, see
[`pdd-validation-monitoring-verification-split-workplan.md`](pdd-validation-monitoring-verification-split-workplan.md).

## Activity Startup Guide

The repository currently supports a combined PDD workflow shell plus separate
launch/export paths for PDD Design, Validation, Monitoring Report, and
Verification activities that exchange linked artifacts. Validation and
Verification still share one generated UI shape bundle internally.

### Run The Current Combined PDD Demo

Use this when you want to exercise the current local PDD workflow shell with
PDD-A/B/C, validation review screens, role gates, and the PDD-CIR gate together.

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/prepare_pdd_workflow_shell.sh
flutter run -d chrome
```

Run the combined local regression check from the repository root:

```bash
dataRequirements/shape2flutter/check-pdd-workflow.sh
```

### Run PDD Design Forms Only

Use this when you only need developer-side PDD capture. Today these forms are
generated from the combined PDD workflow shape bundle; use the PDD Section A,
PDD Section B, and PDD Section C screens and ignore the validation/PDD-CIR
screens.

```bash
dataRequirements/shape2flutter/build-pdd-workflow.sh
```

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/pdd-workflow/schema \
  --build-dir /tmp/nias-shape2flutter/pdd-workflow/flutter \
  --preview-dir /tmp/nias-shape2flutter/pdd-workflow/preview \
  --port 8080 \
  --no-browser
```

Draft PDD Markdown export from captured PDD-A/B/C JSON payloads:

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --render-mode draft \
  --output /tmp/pdd.md
```

### Run Validation Only

Use this when a validator is reviewing a specific PDD artifact. The current
generated preview still uses the shared validation/verification UI shape bundle,
but it writes to a validation-specific output root and exports through a
validation-specific command.

```bash
dataRequirements/shape2flutter/build-validation-report.sh
```

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-report/schema \
  --build-dir /tmp/nias-shape2flutter/validation-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-report/preview \
  --port 8081 \
  --no-browser
```

```bash
python3 dataRequirements/shape2flutter/validation_report/tool/export_validation_report_markdown.py \
  --review-json /tmp/validation-review-form.json \
  --evidence-jsonld /tmp/reviewed-pdd.jsonld \
  --document-author https://nova.org.za/novaimpactaccountingstandard/users/validator-1 \
  --resource-ipfs-uri ipfs://bafy-validation-review \
  --workflow-step-label "Validate PDD" \
  --render-mode draft \
  --output /tmp/validation-report.md
```

### Run Monitoring Report Only

Use this when a monitoring party is publishing measured impact for a specific
monitoring period against a validated PDD version.

```bash
dataRequirements/shape2flutter/build-monitoring-report.sh
```

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/monitoring-report/schema \
  --build-dir /tmp/nias-shape2flutter/monitoring-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/monitoring-report/preview \
  --port 8083 \
  --no-browser
```

```bash
python3 dataRequirements/shape2flutter/monitoring_report/tool/export_monitoring_report_markdown.py \
  --monitoring-json /tmp/monitoring-report-form.json \
  --aligned-pdd https://nova.org.za/novaimpactaccountingstandard/pdd-versions/pdd-v1 \
  --document-author https://nova.org.za/novaimpactaccountingstandard/users/monitoring-party-1 \
  --resource-ipfs-uri ipfs://bafy-monitoring-report \
  --workflow-step-label "Submit Monitoring Report" \
  --render-mode draft \
  --output /tmp/monitoring-report.md
```

### Run Verification Only

Use this when a verifier is reviewing a Monitoring Report or VIC issuance
request package. The current generated preview still uses the shared
validation/verification UI shape bundle, but it writes to a
verification-specific output root and exports through a verification-specific
command.

```bash
dataRequirements/shape2flutter/build-verification-report.sh
```

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/verification-report/schema \
  --build-dir /tmp/nias-shape2flutter/verification-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/verification-report/preview \
  --port 8082 \
  --no-browser
```

```bash
python3 dataRequirements/shape2flutter/verification_report/tool/export_verification_report_markdown.py \
  --review-json /tmp/verification-review-form.json \
  --evidence-jsonld /tmp/reviewed-monitoring-report.jsonld \
  --document-author https://nova.org.za/novaimpactaccountingstandard/users/verifier-1 \
  --resource-ipfs-uri ipfs://bafy-verification-review \
  --workflow-step-label "Verify Monitoring Report" \
  --render-mode draft \
  --output /tmp/verification-report.md
```

## Input/Output Handoff Architecture

The generated UI/forms remain input-side only. Export/rendering remains
output-side only. They are connected by a stable handoff contract:

1. Canonical SHACL/TTL shapes define authoritative paths and validation.
2. `shape2flutter/*-ui-shapes.ttl` files project those paths into form capture.
3. Workflow shell exporters map captured payloads into renderer-ingestible
   JSON-LD.
4. The shared export engine in
   `dataRequirements/document-rendering/tool/export_workflow_report.py` invokes
   profile-driven renderers.

Workflow step definitions are tracked in:

- `dataRequirements/shape2flutter/workflows/pdd-design.yaml`
- `dataRequirements/shape2flutter/workflows/validation-report.yaml`
- `dataRequirements/shape2flutter/workflows/monitoring-report.yaml`
- `dataRequirements/shape2flutter/workflows/verification-report.yaml`

The existing combined preview definitions remain available while the generated
UIs are being split:

- `dataRequirements/shape2flutter/workflows/pdd.yaml`
- `dataRequirements/shape2flutter/workflows/validation-verification.yaml`

Per-report export mapping config now lives in:

- `dataRequirements/document-rendering/config/pdd-export.yaml`
- `dataRequirements/document-rendering/config/monitoring-report-export.yaml`
- `dataRequirements/document-rendering/config/validation-report-export.yaml`
- `dataRequirements/document-rendering/config/verification-report-export.yaml`

The legacy combined validation/verification export config remains available for
older local scripts:

- `dataRequirements/document-rendering/config/validation-verification-export.yaml`

## Monitoring Report Build

```bash
OUT_ROOT=/tmp/nias-shape2flutter/monitoring-report \
dataRequirements/shape2flutter/build-monitoring-report.sh
```

This generates a separate Monitoring Report Flutter form bundle:

- `/tmp/nias-shape2flutter/monitoring-report/schema/forms.jsonld`
- `/tmp/nias-shape2flutter/monitoring-report/flutter/*.dart`

Preview it with:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/monitoring-report/schema \
  --build-dir /tmp/nias-shape2flutter/monitoring-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/monitoring-report/preview \
  --port 8083 \
  --no-browser
```

## Validation And Verification Build

```bash
dataRequirements/shape2flutter/build-validation-report.sh
dataRequirements/shape2flutter/build-verification-report.sh
```

Both scripts still use the shared `validation-verification-ui-shapes.ttl`
bundle, but they write generated artifacts to activity-specific output roots:

- `/tmp/nias-shape2flutter/validation-report/schema/forms.jsonld`
- `/tmp/nias-shape2flutter/validation-report/flutter/*.dart`
- `/tmp/nias-shape2flutter/verification-report/schema/forms.jsonld`
- `/tmp/nias-shape2flutter/verification-report/flutter/*.dart`

Override paths when needed:

```bash
SHAPE2FLUTTER_BIN=/Users/christiaanpauw/shape2flutter/shape2flutter \
OUT_ROOT=/tmp/nias-shape2flutter/validation-report \
dataRequirements/shape2flutter/build-validation-report.sh
```

## Validation And Verification Preview

After running the relevant build script, launch the Flutter web preview from the
generated schema and Dart files. Validation defaults to port `8081`:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-report/schema \
  --build-dir /tmp/nias-shape2flutter/validation-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-report/preview \
  --port 8081
```

Verification defaults to port `8082`:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/verification-report/schema \
  --build-dir /tmp/nias-shape2flutter/verification-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/verification-report/preview \
  --port 8082
```

The preview command builds the preview app, starts a local HTTP server, and
opens the browser. If the browser does not open automatically, use:

```text
http://localhost:8081
```

To keep the server in the terminal but avoid opening a browser automatically:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-report/schema \
  --build-dir /tmp/nias-shape2flutter/validation-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-report/preview \
  --port 8081 \
  --no-browser
```

To only generate the preview app and web build without starting the HTTP
server:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-report/schema \
  --build-dir /tmp/nias-shape2flutter/validation-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-report/preview \
  --serve=false \
  --no-browser
```

Use a different port if `8080` is already occupied:

```bash
/Users/christiaanpauw/shape2flutter/shape2flutter preview \
  --schema-dir /tmp/nias-shape2flutter/validation-report/schema \
  --build-dir /tmp/nias-shape2flutter/validation-report/flutter \
  --preview-dir /tmp/nias-shape2flutter/validation-report/preview \
  --port 3000 \
  --no-browser
```

While the server is running, these debug endpoints are useful:

- `http://localhost:8081/health`
- `http://localhost:8081/debug`
- `http://localhost:8081/files`

Stop the preview server with `Ctrl+C`.

## Validation And Verification Report Handoff

Generated validation and verification review forms are UI payloads. Before final
report rendering, wrap them into a canonical review package with
`data:Document`, the appropriate review class, document-envelope metadata,
workflow submission evidence, and optional reviewed-artifact evidence graphs:

```bash
python3 dataRequirements/shape2flutter/validation_report/tool/export_validation_report_markdown.py \
  --review-json /tmp/validation-review-form.json \
  --review-id https://nova.org.za/novaimpactaccountingstandard/reviews/validation-review-1 \
  --evidence-jsonld /tmp/reviewed-artifacts.jsonld \
  --document-author https://nova.org.za/novaimpactaccountingstandard/users/validator-1 \
  --resource-ipfs-uri ipfs://bafy-validation-review \
  --workflow-step-label "Validate PDD" \
  --source-artifact-id validation-review-form.json \
  --generated-at 2026-05-28T00:00:00Z \
  --render-mode final \
  --review-package-output /tmp/validation-review-package.jsonld \
  --output-dir /tmp/validation-report \
  --output-target markdown \
  --output-target pdf \
  --output-target html
```

Use `dataRequirements/shape2flutter/verification_report/tool/export_verification_report_markdown.py`
for the corresponding Verification Report.
The handoff script passes repeatable `--evidence-jsonld` graphs through to the
report renderer; final mode requires VVS-targeted evidence in the review package
or evidence graphs.

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

## PDD Workflow Shell

The Phase 7 workflow shell lives in `pdd_workflow_shell/`. It hosts the
generated forms behind workflow routing, role gates, in-memory state, and the
PDD-CIR approval gate.

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/prepare_pdd_workflow_shell.sh
flutter run -d chrome
```

Run the shell checks with:

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/check_pdd_workflow_shell.sh
```

To export submitted shell payloads to PDD Markdown artifacts:

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --render-mode draft \
  --output /tmp/pdd.md
```

## PDD Workflow Regression

Run the complete local PDD workflow regression suite from the repository root:

```bash
dataRequirements/shape2flutter/check-pdd-workflow.sh
```

This validates Turtle artifacts, runs the SHACL and workflow gate tests, builds
the PDD shape2flutter forms, compiles the no-server preview, and checks the
workflow shell. To skip the Flutter workflow shell check when Flutter is not
available:

```bash
RUN_WORKFLOW_SHELL_CHECK=false \
dataRequirements/shape2flutter/check-pdd-workflow.sh
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
