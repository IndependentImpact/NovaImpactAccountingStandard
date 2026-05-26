# PDD Document Rendering

This directory contains the NIAS Project Design Document (PDD) rendering
profile, renderer, fixtures, and roadmap for Markdown-first PDD publication.

The rendering boundary has three layers:

1. canonical SHACL shapes in `dataRequirements/`;
2. the presentation-only rendering profile in `pdd-rendering-profile.md`;
3. filled JSON-LD payloads from the PDD workflow shell or other local exports.

The renderer stays independent of Fluree, IPFS, and Hedera deployment concerns.
It consumes canonical data and produces deterministic document artifacts.

## Prerequisites

- `python3`
- Python packages:
  - `rdflib`
  - `pyshacl` for `--render-mode final`
- `pandoc` for PDF and HTML compilation targets

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

For final export, include approved validation review payloads and request any
desired deterministic targets:

```bash
python3 dataRequirements/shape2flutter/pdd_workflow_shell/tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --review-a-json /tmp/review-a.json \
  --review-b-json /tmp/review-b.json \
  --review-c-json /tmp/review-c.json \
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
when Pandoc is available. The automated Python suite still covers the PDF/HTML
code paths deterministically by using a fake Pandoc binary in
`test_pdd_output_compilation.py`.
