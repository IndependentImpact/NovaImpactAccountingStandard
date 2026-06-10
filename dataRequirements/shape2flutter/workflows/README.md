# shape2flutter Workflow Definitions

This directory contains YAML files that define the activity workflows supported
by the NIAS shape2flutter integration. Each file describes one workflow: which
role captures data, which SHACL shapes back the UI forms, how the resulting
artifact is identified, and — for review activities — which upstream artifact is
being reviewed.

## Files in This Directory

| File | Status | Purpose |
|---|---|---|
| `pdd-design.yaml` | Primary | PDD Section A / B / C capture by a project developer |
| `validation-report.yaml` | Primary | Validation review of a completed PDD by a validator |
| `monitoring-report.yaml` | Primary | Monitoring report capture by a monitoring party |
| `verification-report.yaml` | Primary | Verification review of a monitoring report by a verifier |

The four **primary** workflow files are the authoritative definitions used by
the build and test infrastructure.

## Archive

Legacy and demo workflow definitions have been moved to the
[`archive/`](archive/) subdirectory:

| File | Purpose |
|---|---|
| `archive/pdd.yaml` | Combined PDD creation + review screens (pre-split shell) |
| `archive/validation-verification.yaml` | Combined validation and verification screens (pre-split shell) |

These files are retained for backward compatibility with older local scripts and
the combined PDD workflow shell demo but are not the primary startup path.

## Role in the Broader Process

The workflow YAML files sit at the center of a four-stage pipeline:

```
Canonical SHACL / TTL shapes
        │
        │  canonical_bundle declares which shapes
        │  are projected into the UI adapter bundle
        ▼
*-ui-shapes.ttl  (activity-specific adapter bundle)
        │
        │  shape2flutter build script reads the bundle
        │  and generates Flutter form code
        ▼
Generated Flutter widgets  (written to /tmp/..., not committed)
        │
        │  Workflow shell captures user input and
        │  produces captured JSON payloads
        ▼
Export tool  →  JSON-LD package  →  Document renderer  →  Markdown / PDF / HTML
```

Concretely:

1. **Canonical shapes** (`dataRequirements/*.ttl`, `glossary/*.ttl`) define
   the authoritative data model and SHACL constraints.
2. **This directory's YAML files** declare which canonical shapes are projected
   by each activity's UI adapter bundle, and which form `sh:NodeShape`s are
   exposed as workflow steps.
3. **UI adapter bundles** (e.g. `pdd-design-ui-shapes.ttl`) flatten inherited
   shapes and add `ui:` hints so `shape2flutter` can produce usable Flutter
   forms.
4. **Build scripts** (e.g. `build-pdd-design.sh`) call `shape2flutter build`
   with the adapter bundle and write generated Dart/schema artifacts to
   `/tmp/nias-shape2flutter/…` outside the repository.
5. **Export tools** (e.g.
   `shape2flutter/validation_report/tool/export_validation_report_markdown.py`)
   map captured JSON payloads to renderer-ingestible JSON-LD packages.
6. **Document renderers** consume those packages and produce the final
   Markdown, PDF, and HTML artifacts.

The workflow YAMLs are therefore the local contract between the semantic
standard and the shape2flutter toolchain. They are read by the automated tests
in `dataRequirements/tests/test_artifact_split_workflows.py`, which verify that
every declared form is backed by a real `sh:NodeShape` in the listed canonical
sources.

## YAML Field Reference

### Top-Level Fields

| Field | Required | Description |
|---|---|---|
| `workflow_id` | Yes | Globally unique IRI identifying this workflow. Must be unique across all files in this directory. |
| `title` | Yes | Human-readable workflow name. |
| `artifact_type` | Yes (primary) | The type of artifact produced (e.g. `pdd`, `validation-report`, `monitoring-report`, `verification-report`). |
| `owner_role` | Yes (primary) | The role responsible for capture (e.g. `project-developer`, `validator`, `monitoring-party`, `verifier`). |
| `reviewed_artifact` | No | The artifact type that this workflow reviews. Present only on review-based workflows (`validation-report`, `verification-report`). |
| `steps` | Yes | Ordered list of form steps (see below). |
| `outputs` | Yes (primary) | List of artifact types produced by this workflow. |
| `canonical_bundle` | Yes (primary) | Contract block linking this workflow to its UI adapter bundle and canonical shape sources (see below). |
| `artifact_identity_fields` | Yes (primary) | Ordered list of identity field names that must be present in exported payloads for this artifact. |
| `reviewed_artifact_identity_fields` | No | Identity fields that must be carried forward from the reviewed artifact. Present on review workflows. |
| `shape_enforced_reviewed_identity_fields` | No | Subset of `reviewed_artifact_identity_fields` that are additionally enforced by SHACL shapes. |
| `upstream_alignment_fields` | No | Fields linking this artifact to an upstream reference (e.g. the aligned PDD for a monitoring report). |
| `dlr_linkage_fields` | No | Fields linking this artifact to a Data Lineage Record (DLR). |
| `shape_enforced_dlr_field` | No | Single DLR linkage field additionally enforced by a SHACL shape. |

### `steps` List

Each entry in `steps` declares one form screen in the workflow.

| Sub-field | Required | Description |
|---|---|---|
| `id` | Yes | Short identifier for this step (used internally by the workflow shell). |
| `label` | Yes | Human-readable label shown in the UI. |
| `form` | Yes | Name of the `sh:NodeShape` that backs this form. Must exist as a `sh:NodeShape` in the canonical sources listed under `canonical_bundle`. |

### `canonical_bundle` Block

| Sub-field | Required | Description |
|---|---|---|
| `ui_shape_bundle` | Yes | Repository-relative path to the `*-ui-shapes.ttl` adapter bundle used for Flutter form generation. |
| `generated_output_status` | Yes | Always `downstream-generated`. Marks that Flutter code and form schemas are operational outputs, not normative standard artifacts. |
| `canonical_shape_sources` | Yes | Ordered list of repository-relative paths to the canonical Turtle files (ontology, SHACL shapes, mapping anchors) that this workflow draws from. |

### Common Artifact Identity Fields

All primary workflow files must declare at minimum the following fields under
`artifact_identity_fields` (enforced by
`test_artifact_split_workflows.py`):

```
artifactContentCid
artifactSchemaCid
artifactSchemaVersionLabel
artifactAuthor
workflowSubject
submissionTopicId
submissionConsensusTimestamp
submissionEventKey        # optional derived field
submissionMessageUrl      # optional derived field
```

## Creating a New Workflow File

### When Is a New File Useful?

Add a new workflow YAML when:

- **A new artifact type is introduced** into the standard and requires a
  dedicated data-capture activity (e.g. a new report or certificate type).
- **A new review activity is introduced** that examines an existing artifact
  type under a distinct role or with distinct SHACL constraints.
- **A new role-based capture path is needed** that projects a different subset
  of the canonical shapes from an existing artifact type.

Do **not** add a new file simply to give an existing workflow a different UI
layout — that is an adapter-bundle concern (the `*-ui-shapes.ttl` file), not a
workflow-definition concern.

### Step-by-Step Guide

**1. Create the YAML file**

Name the file after the artifact type or activity, using kebab-case:

```
dataRequirements/shape2flutter/workflows/<activity-name>.yaml
```

**2. Choose a unique `workflow_id`**

Follow the existing pattern:

```
https://nova.org.za/novaimpactaccountingstandard/workflows/<activity-name>
```

The automated tests enforce uniqueness across all files in this directory.

**3. Declare the `canonical_bundle`**

List every Turtle file whose shapes the workflow depends on. Start with the
common preamble (ontology + glossary + common shapes + identity contract), then
add the activity-specific shape files and any relevant mapping anchors.

Create a new `*-ui-shapes.ttl` adapter bundle in
`dataRequirements/shape2flutter/` that flattens and annotates the shapes for
`shape2flutter`. Point `ui_shape_bundle` at that file.

**4. Define the `steps`**

For each form screen, declare an `id`, a `label`, and the `form` NodeShape
name. The NodeShape must already exist in one of the files listed under
`canonical_shape_sources`. The automated tests in
`test_artifact_split_workflows.py` will fail if a declared form is not found in
the canonical sources.

**5. Declare `artifact_identity_fields`**

Include at minimum the nine common fields listed above. Add any
activity-specific identity or linkage fields that the export tool needs to
populate.

**6. Add a build script**

Follow the pattern of `build-pdd-design.sh`, `build-validation-report.sh`,
etc. The script should:

- load `load-env.sh` to resolve environment variables,
- call `shape2flutter build` with the new `*-ui-shapes.ttl` bundle,
- write output to a dedicated path under `/tmp/nias-shape2flutter/<activity>/`.

**7. Register the workflow in the tests**

Add the new filename and its `ui_shape_bundle` path to the
`PRIMARY_WORKFLOW_BUNDLES` dict in
`dataRequirements/tests/test_artifact_split_workflows.py` so that the suite
validates the new workflow's canonical sources and form shapes automatically.

**8. Document the new activity**

Add a section to `dataRequirements/shape2flutter/README.md` describing the new
build command, preview command, and any export steps, following the pattern of
the existing activity sections.

### Minimal Example

```yaml
workflow_id: https://nova.org.za/novaimpactaccountingstandard/workflows/my-new-report
title: My New Report Workflow
artifact_type: my-new-report
owner_role: my-new-role
canonical_bundle:
  ui_shape_bundle: dataRequirements/shape2flutter/my-new-report-ui-shapes.ttl
  generated_output_status: downstream-generated
  canonical_shape_sources:
    - glossary/NovaImpactAccountingStandardOntology.ttl
    - glossary/NovaImpactAccountingStandardGlossary.ttl
    - dataRequirements/common-shapes.ttl
    - dataRequirements/document-shapes.ttl
    - dataRequirements/artifact-anchor-shapes.ttl
    - dataRequirements/artifact-identity-contract-shapes.ttl
    # Add activity-specific shape files here
steps:
  - id: my-step
    label: Submit My Report
    form: MyNewReportShape          # must be a sh:NodeShape in the sources above
outputs:
  - my-new-report
artifact_identity_fields:
  - artifactContentCid
  - artifactSchemaCid
  - artifactSchemaVersionLabel
  - artifactAuthor
  - workflowSubject
  - submissionTopicId
  - submissionConsensusTimestamp
  - submissionEventKey
  - submissionMessageUrl
```

For a review-based workflow that examines an existing artifact, also add:

```yaml
reviewed_artifact: <artifact-type-being-reviewed>
reviewed_artifact_identity_fields:
  - reviewedArtifactType
  - reviewedArtifactContentCid
  - reviewedArtifactSchemaCid
  - reviewedArtifactSchemaVersionLabel
  - reviewedSubmissionTopicId
  - reviewedSubmissionConsensusTimestamp
shape_enforced_reviewed_identity_fields:
  - reviewedArtifactType
  - reviewedArtifactContentCid
```

## Related Files

- `dataRequirements/shape2flutter/README.md` — overall shape2flutter integration guide
- `dataRequirements/shape2flutter/*-ui-shapes.ttl` — activity-specific adapter bundles
- `dataRequirements/shape2flutter/build-*.sh` — build scripts that call `shape2flutter`
- `dataRequirements/tests/test_artifact_split_workflows.py` — automated tests for these workflow files
- `dataRequirements/linked-artifact-boundary-decisions.md` — normative linked-artifact identity decisions
- `dataRequirements/artifact-identity-contract-shapes.ttl` — SHACL identity contract
