# PDD Document Rendering

This directory contains the NIAS Project Design Document (PDD) rendering
profile, renderer, fixtures, and roadmap for Markdown-first PDD publication.

The rendering boundary has three layers:

1. canonical SHACL shapes in `dataRequirements/`;
2. the presentation-only rendering profile in `pdd-rendering-profile.md`;
3. filled JSON-LD payloads from the PDD workflow shell or other local exports.

The renderer stays independent of Fluree, IPFS, and Hedera deployment concerns.
It consumes canonical data and produces deterministic document artifacts.

## Shared Workflow Export Engine

Workflow-shell handoff exporters now share a config-backed export engine:

- engine: `dataRequirements/document-rendering/tool/export_workflow_report.py`
- PDD mapping config: `dataRequirements/document-rendering/config/pdd-export.yaml`
- Validation mapping config:
  `dataRequirements/document-rendering/config/validation-report-export.yaml`
- Monitoring mapping config:
  `dataRequirements/document-rendering/config/monitoring-report-export.yaml`
- Verification mapping config:
  `dataRequirements/document-rendering/config/verification-report-export.yaml`

The input/UI side still emits structured workflow payloads, and the output side
ingests them through deterministic handoff adapters. Final-mode PDD rendering
validates the PDD artifact itself; validation, monitoring, and verification
reports are separate linked outputs.

## Prerequisites

- `python3`
- Python packages:
  - `rdflib`
  - `pyshacl` for `--render-mode final`
- `pandoc` for preferred PDF and HTML compilation targets
  - set `PANDOC_BIN=/usr/local/bin/pandoc` if Pandoc is installed outside PATH
  - PDF compilation defaults to `xelatex`; set `PANDOC_PDF_ENGINE=lualatex`
    or another Pandoc-supported engine only when a local or release workflow
    deliberately needs it
  - PDF output has a built-in fallback renderer when Pandoc is unavailable or
    cannot compile the Markdown
  - generated PDF files are checked for a valid PDF header and EOF marker; if
    `qpdf` is available they are also checked with `qpdf --check`

## Generate A Blank Markdown PDD

Render the blank template projected from SHACL plus the rendering profile:

```bash
python3 dataRequirements/document-rendering/tool/render_pdd_markdown.py
```

Write the template to a file:

```bash
python3 dataRequirements/document-rendering/tool/render_pdd_markdown.py \
  --output /tmp/pdd-blank.md
```

## Render Draft Markdown From Filled JSON-LD

Use the fixture payload or a workflow-shell JSON-LD export:

```bash
python3 dataRequirements/document-rendering/tool/render_pdd_markdown.py \
  --input-jsonld dataRequirements/document-rendering/fixtures/pdd-alpha-input.jsonld \
  --source-artifact-id pdd-alpha-input.jsonld \
  --generated-at 2026-05-25T00:00:00Z \
  --render-mode draft \
  --output /tmp/pdd-draft.md
```

Draft mode keeps placeholders visible and does not require SHACL conformance.

## Render Final Markdown With Validation

Final mode requires a SHACL-conformant JSON-LD payload and `pyshacl`:

```bash
python3 dataRequirements/document-rendering/tool/render_pdd_markdown.py \
  --input-jsonld /tmp/pdd-final.jsonld \
  --source-artifact-id pdd-final.jsonld \
  --generated-at 2026-05-26T00:00:00Z \
  --render-mode final \
  --output /tmp/pdd-final.md
```

If validation fails, the command exits non-zero and prints the SHACL report.

## Compile Markdown, PDF, And Website Output

Use `--output-dir` together with one or more repeatable `--output-target`
arguments:

```bash
python3 dataRequirements/document-rendering/tool/render_pdd_markdown.py \
  --input-jsonld /tmp/pdd-final.jsonld \
  --source-artifact-id pdd-final.jsonld \
  --generated-at 2026-05-26T00:00:00Z \
  --render-mode final \
  --output-dir /tmp/pdd-export \
  --output-target markdown \
  --output-target pdf \
  --output-target html
```

Deterministic filenames:

- `pdd.md`
- `pdd.pdf`
- `pdd.html`

Final exports also emit:

- `pdd.metadata.jsonld`
- `pdd.validation.json`

`pdd.metadata.jsonld` includes concrete `nias:artifactAnchor` entries for the
rendered PDD body sections. Validation review packages should reference these
artifact anchor IRIs through `nias:reviewTarget` rather than using legacy field
keys.

Blank-template and filled-data PDF outputs are still actual PDF files. The
renderer prefers Pandoc, but falls back to a minimal valid PDF renderer if
Pandoc cannot produce a PDF.

Pandoc PDF compilation uses `xelatex` by default because NIAS PDD content may
include Unicode labels, names, units, and concept-scheme terms. Override it only
for explicit local or release checks:

```bash
PANDOC_PDF_ENGINE=lualatex \
python3 dataRequirements/document-rendering/tool/render_pdd_markdown.py \
  --input-jsonld /tmp/pdd-final.jsonld \
  --source-artifact-id pdd-final.jsonld \
  --generated-at 2026-05-26T00:00:00Z \
  --render-mode final \
  --output-dir /tmp/pdd-export \
  --output-target pdf
```

## Export From The PDD Workflow Shell

The workflow-shell bridge converts submitted PDD-A, PDD-B, and PDD-C payloads to
the renderer input model:

```bash
python3 dataRequirements/shape2flutter/pdd_workflow_shell/tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --render-mode draft \
  --output /tmp/pdd-workflow.md
```

For final export, request any desired deterministic targets:

```bash
python3 dataRequirements/shape2flutter/pdd_workflow_shell/tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --render-mode final \
  --output-dir /tmp/pdd-export \
  --output-target markdown \
  --output-target pdf \
  --output-target html
```

## Regression Checks

Run the focused PDD rendering test suite from the repository root:

```bash
python3 -m unittest discover -s dataRequirements/tests -p 'test_pdd_*.py' -q
```

Run the focused Validation/Verification Report rendering suite:

```bash
python3 -m unittest dataRequirements.tests.test_validation_verification_report_rendering -q
```

Run the focused Monitoring Report rendering suite:

```bash
python3 -m unittest dataRequirements.tests.test_monitoring_report_rendering -q
```

## Render A Validation Report Or Verification Report

Render a blank Validation Report template:

```bash
python3 dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py \
  --report-type validation
```

Render a blank Verification Report template:

```bash
python3 dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py \
  --report-type verification
```

Render a draft Validation Report from review JSON-LD and optional
reviewed-artifact evidence:

```bash
python3 dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py \
  --report-type validation \
  --input-jsonld dataRequirements/document-rendering/fixtures/validation-verification-report-input.jsonld \
  --evidence-jsonld dataRequirements/document-rendering/fixtures/validation-verification-report-evidence.jsonld \
  --source-artifact-id validation-verification-report-input.jsonld \
  --generated-at 2026-05-28T00:00:00Z \
  --render-mode draft
```

Use `--report-type verification` for the corresponding Verification Report.

When starting from generated validation or verification review forms, use the
shape2flutter handoff adapter first. It wraps the generated form payloads into
canonical review-package JSON-LD, writes the optional package handoff file, and
then invokes this renderer:

```bash
python3 dataRequirements/shape2flutter/validation_report/tool/export_validation_report_markdown.py \
  --review-json /tmp/validation-review-form.json \
  --evidence-jsonld /tmp/reviewed-artifacts.jsonld \
  --document-author https://nova.org.za/novaimpactaccountingstandard/users/validator-1 \
  --resource-ipfs-uri ipfs://bafy-validation-review \
  --render-mode final \
  --review-package-output /tmp/validation-review-package.jsonld \
  --output-dir /tmp/validation-report \
  --output-target markdown
```

Use `dataRequirements/shape2flutter/verification_report/tool/export_verification_report_markdown.py`
for the corresponding Verification Report.

Validation and Verification Report bodies render review decisions, anchor review
findings, and VVS requirement coverage only. Each finding must identify a
`nias:reviewTarget` with `nias:reviewedArtifact` and `nias:reviewedAnchor`;
the renderer displays these as anchor review findings. Review document-envelope metadata,
workflow submission evidence, source graph hashes, and predicate mappings are
kept in appendices and final-mode sidecars so the report body does not treat
legacy `headers` input as substantive content.

Final mode validates the review package structurally and validates only the VVS
requirement shapes for the selected `--report-type` over the review package plus
repeatable `--evidence-jsonld` graphs:

```bash
python3 dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py \
  --report-type validation \
  --input-jsonld /tmp/vv-review-package.jsonld \
  --evidence-jsonld /tmp/vv-evidence.jsonld \
  --source-artifact-id vv-review-package.jsonld \
  --generated-at 2026-05-28T00:00:00Z \
  --render-mode final \
  --output-dir /tmp/vv-report \
  --output-target markdown \
  --output-target pdf \
  --output-target html
```

Deterministic validation outputs:

- `validation-report.md`
- `validation-report.pdf`
- `validation-report.html`
- `validation-report.metadata.jsonld`
- `validation-report.validation.json`

Deterministic verification outputs:

- `verification-report.md`
- `verification-report.pdf`
- `verification-report.html`
- `verification-report.metadata.jsonld`
- `verification-report.validation.json`

## Render A Monitoring Report

Render a blank Monitoring Report template:

```bash
python3 dataRequirements/document-rendering/tool/render_monitoring_report_markdown.py
```

Render a draft Monitoring Report from JSON-LD:

```bash
python3 dataRequirements/document-rendering/tool/render_monitoring_report_markdown.py \
  --input-jsonld dataRequirements/document-rendering/fixtures/monitoring-report-input.jsonld \
  --source-artifact-id monitoring-report-input.jsonld \
  --generated-at 2026-05-28T00:00:00Z \
  --render-mode draft
```

When starting from generated Monitoring Report forms, use the shape2flutter
handoff adapter:

```bash
python3 dataRequirements/shape2flutter/monitoring_report/tool/export_monitoring_report_markdown.py \
  --monitoring-json /tmp/monitoring-report-form.json \
  --aligned-pdd https://nova.org.za/novaimpactaccountingstandard/pdd-versions/pdd-v1 \
  --document-author https://nova.org.za/novaimpactaccountingstandard/users/monitoring-party-1 \
  --resource-ipfs-uri ipfs://bafy-monitoring-report \
  --render-mode final \
  --monitoring-package-output /tmp/monitoring-report-package.jsonld \
  --output-dir /tmp/monitoring-report \
  --output-target markdown
```

Final mode validates the Monitoring Report document envelope, workflow
submission, PDD reference, monitoring period, measured observation, dataset
evidence, calculation resources, and requested issuance account.

Deterministic monitoring outputs:

- `monitoring-report.md`
- `monitoring-report.pdf`
- `monitoring-report.html`
- `monitoring-report.metadata.jsonld`
- `monitoring-report.validation.json`

Run the full local workflow regression command:

```bash
dataRequirements/shape2flutter/check-pdd-workflow.sh
```

That command validates Turtle syntax, runs the repository Python tests, reruns
the explicit PDD rendering regression suite, rebuilds the generated workflow
artifacts, compiles the preview, and optionally checks the Flutter workflow
shell.

## CI And Release Check Decision

Repository automation should treat the Python rendering regression suite as the
required default check. That keeps CI Markdown-first and avoids making system
Pandoc installation a hard requirement.

PDF and HTML compilation should remain part of local and release verification
when Pandoc is available. Release PDF checks should use the default `xelatex`
engine unless a documented release profile overrides `PANDOC_PDF_ENGINE`. The
automated Python suite still covers the PDF/HTML code paths deterministically by
using a fake Pandoc binary in `test_pdd_output_compilation.py`.
