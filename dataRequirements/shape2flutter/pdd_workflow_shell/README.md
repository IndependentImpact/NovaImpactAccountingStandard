# PDD Workflow Shell

This Flutter package hosts the generated PDD shape2flutter forms in a workflow
shell.

The shell is intentionally thin:

- it routes between PDD-A, PDD-B, PDD-C, PDD-A/B/C validation reviews, and
  PDD-CIR;
- it keeps generated JSON-LD-like payload maps between steps;
- it captures local document message IDs and IPFS URI references;
- it separates project developer and PDD validator roles;
- it blocks PDD-CIR until the approval gate from
  `../pdd-workflow-gate.md` passes.

The generated form Dart files are not committed. They are copied into
`lib/generated/` by the preparation script.

## Prepare

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/prepare_pdd_workflow_shell.sh
```

This runs `../build-pdd-workflow.sh` and copies the generated Dart widgets from
`/tmp/nias-shape2flutter/pdd-workflow/flutter`.

## Run

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
flutter run -d chrome
```

## Check

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/check_pdd_workflow_shell.sh
```

The check script prepares generated forms, runs Flutter tests, runs the analyzer,
and builds the web app.

## Export Markdown

Use the shell export bridge to hand off submitted PDD-A/B/C payload JSON to the
document renderer:

```bash
cd dataRequirements/shape2flutter/pdd_workflow_shell
tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --render-mode draft \
  --output /tmp/pdd.md
```

For final export, include approved review payload JSON files so the workflow
gate can be checked before SHACL final rendering:

```bash
tool/export_pdd_workflow_markdown.py \
  --pdd-a-json /tmp/pdd-a.json \
  --pdd-b-json /tmp/pdd-b.json \
  --pdd-c-json /tmp/pdd-c.json \
  --review-a-json /tmp/review-a.json \
  --review-b-json /tmp/review-b.json \
  --review-c-json /tmp/review-c.json \
  --render-mode final \
  --output-dir /tmp/pdd-export \
  --output-target markdown --output-target pdf --output-target html
```

## Integration Boundary

This package currently uses in-memory workflow state. The Fluree-backed
implementation should replace the in-memory submission calls with transaction
calls shaped by:

- `../../fluree/pdd-workflow-transactions.md`
- `../../fluree/artifact-lookup-queries.md`
- `../../fluree/policy-requirements.md`

The generated forms remain UI projections. Canonical validation still belongs
to the SHACL assets and the Fluree/service enforcement layer.
