# PDD, Validation, Monitoring, And Verification Artifact Split Workplan

## Purpose

Split the current combined workflow surfaces into four accountable artifact
families:

1. Project Design Document (PDD), authored by the project developer.
2. Validation Report, authored by a validator against a specific PDD version.
3. Monitoring Report, authored by the project or monitoring party for a specific
   monitoring period.
4. Verification Report, authored by a verifier against a specific Monitoring
   Report, with traceability to the validated PDD.

The target architecture must support different people, different execution
times, different platforms, and one-to-many review relationships. A PDD can have
more than one validation report over time. A Monitoring Report can have more
than one verification report. Certificate issuance gates should query linked
artifacts; they should not require review artifacts to be embedded in the PDD or
Monitoring Report publication.

## Code Review Findings

### High: PDD rendering currently embeds downstream governance artifacts

`dataRequirements/document-rendering/pdd-rendering-profile.md` renders
Validation Review Summary and PDD-CIR content inside the PDD appendices
(`Appendix A.1` and `Appendix A.2`). The workflow rendering map also maps PDD
validation reviews and PDD-CIR into the PDD publication.

Why this matters: the rendered PDD becomes a container for independent validator
and certificate-request artifacts. That conflicts with the target model where a
PDD is a developer-authored design artifact and validation reports are separate
review publications.

Relevant locations:

- `dataRequirements/document-rendering/pdd-rendering-profile.md:122`
- `dataRequirements/document-rendering/pdd-rendering-profile.md:126`
- `dataRequirements/document-rendering/pdd-rendering-profile.md:134`
- `dataRequirements/document-rendering/pdd-rendering-profile.md:150`

### High: the PDD workflow shell stores design, validation, and PDD-CIR in one state machine

`PddWorkflowStep` includes `pddA`, `pddB`, `pddC`, all three validation review
steps, and `pddCir`. `PddWorkflowState` then gates review opening and PDD-CIR
opening from one in-memory `_submitted` map.

Why this matters: this assumes validation happens in the same UI/session as PDD
creation. It also models one review artifact per PDD section, not multiple
validators or independently submitted review packages.

Relevant locations:

- `dataRequirements/shape2flutter/pdd_workflow_shell/lib/src/workflow_contract.dart:7`
- `dataRequirements/shape2flutter/pdd_workflow_shell/lib/src/workflow_contract.dart:287`
- `dataRequirements/shape2flutter/pdd_workflow_shell/lib/src/workflow_contract.dart:336`
- `dataRequirements/shape2flutter/pdd_workflow_shell/lib/src/pdd_workflow_shell_app.dart:126`

### High: final PDD export is blocked by validation payloads instead of publishing the PDD artifact independently

The PDD exporter accepts review JSON files and uses `pdd-export.yaml` final gate
requirements before rendering final PDD output. Those requirements point to
fixed `pdd-alpha` document IDs.

Why this matters: final PDD publication should validate the PDD document itself.
Validation approval should be a separate linked artifact and an issuance-gate
input, not a prerequisite for rendering the PDD as a final design artifact.

Relevant locations:

- `dataRequirements/shape2flutter/pdd_workflow_shell/tool/export_pdd_workflow_markdown.py:428`
- `dataRequirements/shape2flutter/pdd_workflow_shell/tool/export_pdd_workflow_markdown.py:452`
- `dataRequirements/document-rendering/config/pdd-export.yaml:5`
- `dataRequirements/document-rendering/tool/export_workflow_report.py:26`

### Medium: validation and verification are combined in one UI and rendering lane

`validation-verification-ui-shapes.ttl`, `workflows/validation-verification.yaml`,
the shared export script, and the shared rendering profile all treat validation
and verification as variants of one review workflow.

Why this matters: sharing helper code is fine, but the user-facing activities are
different in subject, timing, actor, evidence, and reviewed artifact. The startup
commands and output directories should let a validator run validation separately
from a verifier running verification.

Relevant locations:

- `dataRequirements/shape2flutter/workflows/validation-verification.yaml:1`
- `dataRequirements/shape2flutter/validation_verification_report/tool/export_validation_verification_report_markdown.py:304`
- `dataRequirements/document-rendering/validation-verification-report-rendering-profile.md:1`

### Medium: Monitoring Report has canonical SHACL shapes but no first-class UI or renderer flow

`MonitoringReportShape` exists, but the current shape2flutter UI bundle covers
review, Data Lineage Report, VIC-IR, VIC, and impact summary screens. There is
not yet a dedicated Monitoring Report UI bundle, workflow YAML, handoff adapter,
or Markdown rendering profile.

Why this matters: Verification should review a submitted Monitoring Report. The
monitoring activity needs its own creation and publication path before
verification can be cleanly separated.

Relevant locations:

- `dataRequirements/monitoring-report-shapes.ttl:42`
- `dataRequirements/shape2flutter/validation-verification-ui-shapes.ttl:246`
- `dataRequirements/shape2flutter/validation-verification-ui-shapes.ttl:354`
- `dataRequirements/shape2flutter/validation-verification-ui-shapes.ttl:430`

### Low: shared helper UI shapes are duplicated across UI shape bundles

`TimeInstantUiShape`, `DateTimeIntervalUiShape`, `HederaTopicMessageUiShape`,
`WorkflowDocumentSubmissionUiShape`, `DocumentReferenceUiShape`, and
`DocumentFieldReviewUiShape` are declared in both PDD and
validation/verification UI shape bundles.

Why this matters: the split will add more UI bundles. Without a shared helper
shape module, drift in common workflow, document reference, and review fields is
likely.

Relevant locations:

- `dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl:24`
- `dataRequirements/shape2flutter/validation-verification-ui-shapes.ttl:17`

## Target Artifact Boundaries

### PDD / Design

Owner: project developer.

Purpose: describe the proposed project, methodology, ex-ante impact claims,
monitoring design, project parties, legal/funding/history information, and
stakeholder engagement.

Inputs:

- PDD-A, PDD-B, and PDD-C form payloads.
- Developer identity and document envelope metadata.

Outputs:

- PDD JSON-LD package.
- `pdd.md`, `pdd.pdf`, `pdd.html`.
- PDD metadata and validation sidecars.

Does not output:

- Validation Report body.
- Validation Review Summary appendix.
- PDD-CIR body.

### Validation Report

Owner: validator.

Purpose: record an independent review of a specific PDD version.

Inputs:

- PDD artifact reference and optional PDD evidence graph.
- Validator field reviews.
- Final validation decision.

Outputs:

- Validation review package JSON-LD.
- `validation-report.md`, `validation-report.pdf`, `validation-report.html`.
- Validation report metadata and validation sidecars.

Relationship:

- `ValidationReport isReviewOf PDDVersion`.
- More than one validation report may reference the same PDD version.
- A later PDD version requires a new validation decision or an explicit rule
  stating that an existing validation still applies.

### Monitoring Report

Owner: project operator, monitoring party, or delegated reporting party.

Purpose: report measured impacts and supporting calculation/evidence for a
specific monitoring period against a validated PDD.

Inputs:

- Validated PDD reference.
- Monitoring period.
- Measured impact observations.
- Dataset references and data lineage review references.
- Calculation code/report/result references.
- Requested issuance account.

Outputs:

- Monitoring Report JSON-LD package.
- `monitoring-report.md`, `monitoring-report.pdf`,
  `monitoring-report.html`.
- Monitoring report metadata and validation sidecars.

Relationship:

- `MonitoringReport alignedWithPDD PDDVersion`.
- `MonitoringReport usesDataset Dataset`.
- `MonitoringReport reportedObservation IndicatorObservation`.

### Verification Report

Owner: verifier.

Purpose: record an independent review of a specific Monitoring Report and its
evidence, with traceability back to the validated PDD.

Inputs:

- Monitoring Report reference and evidence graph.
- Optional PDD and validation report evidence graphs.
- Verifier field reviews.
- Final verification decision.

Outputs:

- Verification review package JSON-LD.
- `verification-report.md`, `verification-report.pdf`,
  `verification-report.html`.
- Verification report metadata and validation sidecars.

Relationship:

- `VerificationReport isReviewOf MonitoringReport`.
- More than one verification report may reference the same Monitoring Report.
- VIC-IR gates query approved verification reports and linked monitoring
  reports, not embedded verifier content.

## Target UI Model

### Individual Activity UIs

Create or keep separate launch paths for:

- PDD Design UI: developer-only PDD-A/B/C capture and PDD publication.
- Validation UI: validator review of an externally supplied PDD artifact.
- Monitoring Report UI: monitoring party capture and monitoring publication.
- Verification UI: verifier review of an externally supplied Monitoring Report.

Each UI should accept artifact references as inputs and produce its own artifact
package as output. None of these UIs should require the previous actor to be in
the same local session.

### Combined Workbench

Keep a combined workbench as an optional local developer/demo shell. It should
compose separate artifact packages rather than own their state directly.

The combined workbench can show:

- Project artifact timeline.
- PDD versions and validation reports.
- Monitoring periods and Monitoring Reports.
- Verification reports.
- Issuance gate status.

It should call the same import/export APIs used by the individual UIs.

## Data And Linking Model

Use explicit artifact references everywhere:

```text
PDD v1
  <- isReviewOf
Validation Report A
Validation Report B

PDD v1
  <- alignedWithPDD
Monitoring Report 2026-Q1
  <- isReviewOf
Verification Report A
Verification Report B
```

Minimum reference fields:

- Referenced artifact IRI.
- Document schema IRI.
- Document message ID.
- Resource IPFS URI.
- Source graph hash or equivalent digest when available.
- Version or revision marker.
- Author/submitter identity.
- Timestamp or workflow consensus evidence.

Gate checks should be query-shaped:

- PDD certificate gate: find at least one approved Validation Report for the
  target PDD version.
- VIC issuance gate: find at least one approved Verification Report for the
  target Monitoring Report, and verify the Monitoring Report aligns with a
  validated PDD version.

## Implementation Plan

### Phase 0: Confirm vocabulary and ownership boundaries

Deliverables:

- Agree whether Section A/B/C remain separate submitted artifacts or are bundled
  into one PDD version package at publication time.
- Decide whether `GenericDocumentReview` is enough for PDD validation or whether
  a named `PddValidationReport` class is useful as a publication projection.
- Decide whether Verification Report reviews `MonitoringReport`,
  `VerifiedImpactCertificateIssuanceRequest`, or both.
- Define version-specific artifact reference shape used across all four lanes.

Acceptance criteria:

- A one-page artifact relationship diagram exists.
- The team can answer "who authored this artifact?" and "what exact artifact was
  reviewed?" for every output.

### Phase 1: Create shared UI helper shapes

Deliverables:

- Move duplicated helper UI shapes into a shared shape2flutter helper bundle.
- Update PDD and validation/verification shape bundles to import or compose
  shared helper shapes.
- Keep generated Dart names stable where possible.

Candidate shared shapes:

- Time instant.
- Date/time interval.
- Hedera topic message.
- Workflow document submission.
- Document reference.
- Resource artifact.
- Document field review.

Acceptance criteria:

- PDD and validation/verification builds still generate.
- Shared helper field order and labels are defined in one place.

### Phase 2: Split PDD Design from PDD validation and PDD-CIR

Status note 2026-06-05: the PDD Design UI bundle split is in place through
`pdd-design-ui-shapes.ttl` and `build-pdd-design.sh`. The combined
`pdd-workflow-ui-shapes.ttl` bundle remains available for the local demo shell.
Renderer/export boundary cleanup remains tracked below.

Deliverables:

- Create a PDD Design workflow YAML with only PDD-A, PDD-B, and PDD-C.
- Create a PDD Design shell or mode that only loads PDD forms.
- Update the PDD renderer profile so PDD publication contains design content and
  PDD metadata only.
- Move validation summary and PDD-CIR rendering out of the PDD profile.
- Update PDD export final mode so it validates PDD SHACL conformance only.

Acceptance criteria:

- A PDD can be rendered final without validator review JSON.
- PDD output does not include Validation Review Summary or PDD-CIR sections.
- Existing PDD tests are updated to assert the new boundary.

### Phase 3: Make Validation Report a separate workflow and renderer output

Deliverables:

- Create validation-specific workflow YAML and startup commands.
- Create validation-specific output path defaults.
- Ensure validation UI accepts PDD artifact references/evidence instead of
  depending on in-memory PDD shell state.
- Ensure the Validation Report renderer displays the reviewed PDD reference
  prominently.
- Support multiple validation report packages per PDD version.

Acceptance criteria:

- A validator can render a Validation Report from review JSON plus PDD evidence.
- The same PDD version can be referenced by more than one validation report.
- Validation Report output never mutates or embeds itself into the PDD output.

### Phase 4: Add Monitoring Report UI and renderer flow

Deliverables:

- Add `monitoring-report-ui-shapes.ttl` for `MonitoringReportShape` and nested
  dataset/observation/resource artifact fields.
- Add `workflows/monitoring-report.yaml`.
- Add build and preview script for Monitoring Report forms.
- Add Monitoring Report handoff adapter from UI payload to canonical JSON-LD.
- Add `monitoring-report-rendering-profile.md`.
- Add Monitoring Report renderer and tests.

Acceptance criteria:

- Monitoring Report can be authored independently after PDD validation.
- Monitoring Report references a validated PDD version.
- Monitoring Report output has its own deterministic filenames and sidecars.

### Phase 5: Split Verification Report from validation and align it to Monitoring Report

Deliverables:

- Create verification-specific workflow YAML and startup commands.
- Ensure verification UI accepts Monitoring Report reference/evidence and, when
  needed, PDD and validation evidence.
- Keep multiple verification reports per Monitoring Report.
- Decide whether VIC-IR remains in the verification bundle or becomes a separate
  issuance request workflow.

Acceptance criteria:

- A verifier can render a Verification Report without using the validation UI.
- Verification final mode validates against Monitoring Report/VVS evidence.
- Verification Report output references the exact Monitoring Report reviewed.

### Phase 6: Rebuild issuance gates as linked-artifact queries

Deliverables:

- Replace in-memory PDD-CIR gate logic with query-shaped gate contracts.
- Keep local demo gate implementations for tests and previews.
- Document Fluree/service requirements for production gates.

Candidate gates:

- PDD-CIR requires approved validation for the referenced PDD version.
- VIC-IR requires approved verification for the referenced Monitoring Report.
- Monitoring Report must align with a validated PDD version.

Acceptance criteria:

- Gates can be evaluated from externally supplied artifact references.
- Gate logic no longer assumes one validation review per PDD section.
- Gate failures identify missing or stale linked artifacts.

### Phase 7: Update docs, tests, and generated fixtures

Deliverables:

- Update `dataRequirements/shape2flutter/README.md`.
- Update `dataRequirements/document-rendering/README.md`.
- Add per-activity quick starts.
- Add together-mode/demo quick start.
- Update fixtures and regression tests for the split outputs.
- Mark old combined PDD workflow commands as legacy/demo if retained.

Acceptance criteria:

- A developer can start each activity individually from README commands.
- A developer can start the combined local demo from README commands.
- Tests cover PDD-only rendering, validation-only rendering, monitoring report
  rendering, verification-only rendering, and linked-artifact gates.

## Proposed File Layout

```text
dataRequirements/shape2flutter/
  shared-ui-shapes.ttl
  pdd-design-ui-shapes.ttl
  validation-report-ui-shapes.ttl
  monitoring-report-ui-shapes.ttl
  verification-report-ui-shapes.ttl
  workflows/
    pdd-design.yaml
    validation-report.yaml
    monitoring-report.yaml
    verification-report.yaml

dataRequirements/document-rendering/
  pdd-rendering-profile.md
  validation-report-rendering-profile.md
  monitoring-report-rendering-profile.md
  verification-report-rendering-profile.md
  config/
    pdd-export.yaml
    validation-report-export.yaml
    monitoring-report-export.yaml
    verification-report-export.yaml
```

The exact filenames can be adjusted, but each accountable artifact should have
an obvious shape bundle, workflow definition, export config, renderer profile,
and startup command.

## Test Plan

Unit tests:

- PDD final export succeeds without validation review payloads.
- PDD final export fails only on PDD SHACL validation issues.
- Validation Report final export requires a valid review package and PDD
  evidence.
- Monitoring Report final export requires measured observation, period, dataset,
  and issuance account fields.
- Verification Report final export requires Monitoring Report evidence.
- Gate functions accept multiple validation and verification reports and choose
  approved reports by artifact reference and version.

Regression tests:

- Blank templates for all four artifact families.
- Filled draft renders for all four artifact families.
- Final-mode validation output sidecars for all four artifact families.
- Combined demo shell smoke test, if retained.

Manual checks:

- Start each individual preview.
- Start the combined demo shell.
- Export each artifact to Markdown.
- Confirm report body boundaries by visual inspection.

## Documentation Updates Required

Update the shape2flutter README with:

- "Run everything together" commands for local demo workflows.
- "Run PDD Design only" commands.
- "Run Validation only" commands.
- "Run Monitoring Report only" commands.
- "Run Verification only" commands.
- A note that generated previews are input-side only and rendered reports are
  generated by the handoff/export scripts.

Update the document-rendering README with:

- Separate render/export commands for PDD, Validation Report, Monitoring Report,
  and Verification Report.
- Explanation of linked-artifact evidence graphs.
- Explanation that final issuance gates query linked artifacts.

## Open Questions

1. Should PDD-A/B/C remain three workflow submissions, or should publication
   mint a single PDD version artifact that contains all three sections?
2. Should validators review PDD-A/B/C separately, one full PDD package, or both?
3. How should multiple validators be represented in report output: separate
   reports only, or an optional aggregated validation summary?
4. Should verification review a Monitoring Report directly, a VIC-IR directly,
   or a package containing both?
5. What stable version identifier should link PDD, Validation Report,
   Monitoring Report, and Verification Report across platforms?
6. Which artifact store is the source of truth for local development before
   Fluree/IPFS/Hedera integration is available?
