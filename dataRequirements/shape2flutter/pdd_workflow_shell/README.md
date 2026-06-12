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

## Prerequisites

| Tool | Requirement | Notes |
|------|-------------|-------|
| Flutter SDK | ≥ 3.0.0 | `flutter --version` to check |
| Dart SDK | included with Flutter | |
| `shape2flutter` binary | any recent build | set `SHAPE2FLUTTER_BIN` in `.env` |
| Python 3 | for export bridge | set `PYTHON3_BIN` in `.env` if not on `PATH` |

### Environment variables

Copy the repository-root `.env.example` to `.env` and adjust for your machine:

```bash
cp ../../../../.env.example ../../../../.env
# then edit ../../../../.env
```

Relevant variables for this package:

| Variable | Default | Purpose |
|----------|---------|---------|
| `SHAPE2FLUTTER_BIN` | *(must be set)* | Absolute path to the `shape2flutter` binary |
| `NIAS_TMP_DIR` | `/tmp` | Directory for intermediate build output |

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

## Modifying and Extending the Shell

For detailed guidance on how the shell is structured and how to build equivalent
shells for other workflows (e.g. a monitoring-report shell), see
**[ARCHITECTURE.md](ARCHITECTURE.md)**.

Key sections:

| Section | Topic |
|---------|-------|
| §2 Code Layout | Directory structure and file responsibilities |
| §3 Build Pipeline | From SHACL shapes → Dart widgets → shell |
| §4 Generated Widget Import Contract | How generated widgets are imported and aliased |
| §5–8 Routing, State, Seed Data, Roles | Core shell patterns |
| §14 Reusable Patterns | Checklist for building a new workflow shell |
| §16 Monitoring-Report Shell | Step-by-step walkthrough for adding a monitoring shell |
