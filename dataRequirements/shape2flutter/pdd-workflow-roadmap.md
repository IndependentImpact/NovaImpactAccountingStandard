# PDD shape2flutter Workflow Roadmap

This document defines the implementation path for recreating the PDD creation
and validation workflow with `shape2flutter`.

The goal is to generate usable Flutter form components from SHACL while keeping
the canonical NIAS data model authoritative. `shape2flutter` should receive
UI-facing adapter shapes, not replace the canonical SHACL constraints.

## Scope

In scope:

- PDD Section A creation.
- PDD Section B creation.
- PDD Section C creation.
- PDD certificate issuance request creation.
- PDD Section A, B, and C validation review screens.
- Field-level review using `GenericDocumentReview` and `DocumentFieldReview`.
- Workflow handoff from submitted PDD sections to validation reviews and then
  to PDD-CIR.

Out of scope for this roadmap:

- PLA creation.
- Monitoring Report creation.
- MR verification.
- Verified Impact Certificate issuance beyond references already needed by
  the PDD workflow.
- Exact visual parity with the historical R UI unless the original R screen
  layout and wording are explicitly harvested as a separate task.

## Current Assets

Canonical SHACL assets already available:

- `dataRequirements/project-design-shapes.ttl`
  - PDD-A project design.
  - Project parties.
  - Legal matters.
  - Public funding status and source rules.
  - Debundling and eligibility fields.
- `dataRequirements/impact-declaration-shapes.ttl`
  - PDD-B impact declaration.
  - Declared impacts.
  - Monitored and unmonitored impact branches.
- `dataRequirements/stakeholder-engagement-shapes.ttl`
  - PDD-C stakeholder engagement.
- `dataRequirements/pdd-certificate-shapes.ttl`
  - PDD-CIR.
  - References to approved PDD-A, PDD-B, and PDD-C validation reviews.
- `dataRequirements/review-shapes.ttl`
  - Generic document review.
  - Field-level document review.
- `dataRequirements/shape2flutter/validation-verification-ui-shapes.ttl`
  - Existing example of UI-facing flattened shapes for `shape2flutter`.

Known metadata clean-up:

- `dataRequirements/legacy-field-map.csv` has been reconciled for the PDD
  workflow rows needed before shape2flutter work starts.
- PDD-A, PDD-B, PDD-C, PDD-CIR, `ProjectParty`, `Impact`,
  `TableRow-DataParameterMonitoring`, `GenericDocumentReview`, and
  `DocumentFieldReview` now have canonical RDF mappings recorded.
- Remaining `UNMAPPED` rows outside that set belong to other workflows and
  should not block the PDD workflow SHACL readiness step.

## SHACL Readiness Baseline

As of 2026-05-20, the PDD workflow has canonical SHACL coverage for:

- PDD Section A report content using `nias-o:PddSectionAReportShape`.
- PDD Section A project design details using `nias-o:ProjectDesignShape`.
- PDD Section B report content using `nias-o:PddSectionBReportShape`.
- PDD Section B declared impacts using `nias-o:ImpactRequirementShape`.
- PDD Section B impact claims using `nias-o:ImpactClaimShape`.
- PDD Section C stakeholder engagement using `nias-o:PddSectionCShape`.
- PDD-CIR using `nias-o:PddCertificateIssuanceRequestShape`.
- PDD validation reviews using `nias-o:GenericDocumentReviewShape` and
  `nias-o:DocumentFieldReviewShape`.
- Document metadata, workflow submissions, document references, Hedera topic
  messages, resource artifacts, dates, project parties, technologies, and data
  parameter requirements through shared helper shapes.

The readiness fixtures and tests are:

- `dataRequirements/fixtures/pdd-workflow/`
- `dataRequirements/tests/test_pdd_workflow_shapes.py`

Do not begin PDD `shape2flutter` UI adapter work unless these tests pass.

## Architecture

Use three layers.

1. Canonical SHACL

   These are the authoritative validation shapes in `dataRequirements/*.ttl`.
   They express the RDF model, cardinality, datatypes, class constraints, and
   cross-field validation rules.

2. shape2flutter UI adapter shapes

   These are UI-facing shapes in `dataRequirements/shape2flutter/`. They may
   flatten composed SHACL, add `ui:` annotations, bound repeatable fields for UI
   rendering, and use user-facing labels. They must preserve canonical paths and
   classes.

3. Flutter workflow shell

   The generated forms do not by themselves implement workflow state. A thin
   Flutter shell must route users through the PDD steps, carry references between
   submissions, enforce role and approval gates, and assemble the data needed by
   later forms.

## Proposed Files

Add these files during implementation:

- `dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl`
- `dataRequirements/shape2flutter/build-pdd-workflow.sh`
- `dataRequirements/shape2flutter/pdd-workflow-gate.md`
- `dataRequirements/fixtures/shape2flutter/pdd-section-a-valid.ttl`
- `dataRequirements/fixtures/shape2flutter/pdd-section-b-valid.ttl`
- `dataRequirements/fixtures/shape2flutter/pdd-section-c-valid.ttl`
- `dataRequirements/fixtures/shape2flutter/pdd-section-a-review-valid.ttl`
- `dataRequirements/fixtures/shape2flutter/pdd-section-b-review-valid.ttl`
- `dataRequirements/fixtures/shape2flutter/pdd-section-c-review-valid.ttl`
- `dataRequirements/fixtures/shape2flutter/pdd-cir-valid.ttl`

Generated artifacts should remain outside the repository by default, following
the existing `/tmp/nias-shape2flutter/...` pattern.

After the SHACL work is complete, add a Fluree deployment projection:

- `dataRequirements/fluree/README.md`
- `dataRequirements/fluree/context.jsonld`
- `dataRequirements/fluree/bootstrap-ledger.jsonld`
- `dataRequirements/fluree/shacl-compatibility-matrix.md`
- `dataRequirements/fluree/policy-requirements.md`
- `dataRequirements/fluree/pdd-workflow-transactions.md`

The Fluree projection must not become a second source of truth. It should load
and operationalize the ontology, concept schemes, document schema resources, and
SHACL shapes using the same canonical IRIs.

The detailed post-SHACL specification is
[`../fluree-ledger-deployment-package.md`](../fluree-ledger-deployment-package.md).

## UI Adapter Shape Set

The first PDD bundle should generate these forms:

- `PddSectionAUiShape`
  - workflow submission metadata where applicable.
  - project title.
  - project purpose/objective.
  - project location resources.
  - technologies and measures.
  - project parties.
  - legal matters.
  - public funding status.
  - public funding sources.
  - project history.
  - debundling assessment.
  - eligibility description.
- `ProjectPartyUiShape`
  - name.
  - host party flag.
  - participant party flag.
  - public/private classification.
  - additional information.
- `PddSectionBUiShape`
  - workflow submission metadata.
  - project subject reference.
  - repeatable impact declarations or declared impacts.
  - methodology references.
- `ImpactDeclarationUiShape`
  - declared impact.
  - impact claim.
  - methodology use.
- `ImpactRequirementUiShape`
  - description.
  - intentionality.
  - beneficial/adverse classification.
  - monitoring status.
  - monitored impact branch fields.
  - unmonitored impact branch fields.
- `PddSectionCUiShape`
  - workflow submission metadata.
  - stakeholder engagement modalities.
  - stakeholder comment summary.
  - stakeholder comment consideration.
- `PddCertificateIssuanceRequestUiShape`
  - workflow submission metadata.
  - approved PDD-A validation review reference.
  - approved PDD-B validation review reference.
  - approved PDD-C validation review reference.
  - requested issuance account ID.
- `PddSectionAValidationReviewUiShape`
- `PddSectionBValidationReviewUiShape`
- `PddSectionCValidationReviewUiShape`
  - each should reuse the generic document review model but expose
    PDD-specific labels and field review grouping.

## Implementation Phases

### Phase 1: Reconcile Field Inventory

Tasks:

- Compare `legacy-field-map.csv` with `legacy-to-canonical-map.csv`.
- Update stale PDD-A, PDD-B, PDD-C, PDD-CIR, `ProjectParty`,
  `GenericDocumentReview`, and `DocumentFieldReview` rows.
- Leave a field marked unmapped only when it is intentionally out of scope or
  truly has no canonical predicate.
- Record any remaining intentional gaps in the relevant Markdown migration
  document.

Exit criteria:

- PDD workflow rows in the field map match current canonical SHACL coverage.
- Remaining gaps are named and justified.

### Phase 2: Confirm Canonical SHACL Readiness

Tasks:

- Validate canonical PDD-A, PDD-B, PDD-C, PDD-CIR, and review shapes with
  `riot`.
- Validate representative valid and invalid fixtures with the repository's
  SHACL test tooling.
- Confirm PDD-B has a document/workflow wrapper strategy, not only individual
  impact rows.

Exit criteria:

- Canonical shapes validate.
- Fixtures cover all PDD sections and review outputs.
- PDD-B wrapper/header handling is explicitly modeled or deliberately handled
  by the workflow shell.

### Phase 3: Build PDD UI Adapter Shapes

Status: completed on 2026-05-20.

Tasks:

- Created `pdd-workflow-ui-shapes.ttl`.
- Flattened nested and composed structures enough for `shape2flutter`.
- Added `ui:` labels, ordering, widgets, and helper subforms.
- Reused helper patterns from `validation-verification-ui-shapes.ttl`.
- Kept canonical predicates and classes intact.

Exit criteria:

- `shape2flutter lint` succeeds, with only understood warnings.
- `shape2flutter emit-jsonld` succeeds.
- `shape2flutter build` generates 26 Dart forms for the PDD workflow bundle.
- A no-server `shape2flutter preview` compile succeeds from the generated
  schema and Dart output.

### Phase 4: Add PDD Build And Preview Script

Status: completed on 2026-05-20.

Tasks:

- Added `build-pdd-workflow.sh`.
- Used `SHAPE2FLUTTER_BIN` and `OUT_ROOT` environment overrides.
- Wrote generated output to `/tmp/nias-shape2flutter/pdd-workflow` by default.
- Documented preview commands in `README.md`.

Exit criteria:

- The full PDD UI adapter build can be run with one command.
- The generated Flutter preview compiles.
- The generated forms are inspectable in the browser.

### Phase 5: Add PDD Validation Review Forms

Status: completed on 2026-05-20.

Tasks:

- Created PDD-specific UI aliases around `GenericDocumentReview`.
- Added `nias-o:isReviewOf` to the PDD-specific review adapter shapes so each
  review payload identifies the submitted PDD document it reviewed.
- Used repeatable `DocumentFieldReview` subforms.
- Added labels that identify the reviewed section.
- Ensured final review decisions are compatible with the canonical SKOS concept
  values.
- Documented the cross-document approval gate in
  `pdd-workflow-gate.md`.
- Added a gate fixture and unit tests proving that rejected, unresolved, or
  wrong-section reviews cannot unlock PDD-CIR.

Exit criteria:

- Review forms can represent PDD-A, PDD-B, and PDD-C validation.
- PDD-CIR can reference the approved review artifacts.
- Rejected or incomplete reviews cannot satisfy the PDD-CIR workflow gate in
  the workflow shell.

### Phase 6: Define The Fluree Deployment Projection

Status: completed on 2026-05-21.

Do this only after the canonical and UI-facing SHACL work is complete enough to
generate and validate the PDD forms.

Tasks:

- Created `dataRequirements/fluree/README.md` and defined the Fluree layer as a
  deployment and operational projection of the semantic standard.
- Created a NIAS JSON-LD context for Fluree transactions.
- Defined a bootstrap manifest and deterministic order that loads:
  - the NIAS ontology.
  - NIAS concept schemes.
  - indicator concept schemes.
  - knowledge-domain and methodology concept schemes.
  - document schema resources.
  - canonical SHACL shapes.
- Created a SHACL compatibility matrix that classifies canonical constraints as:
  - directly enforceable in Fluree.
  - enforceable after minor rewrite.
  - enforced by the application or service layer.
  - advisory or documentation only.
- Defined PDD workflow transaction templates for PDD-A, PDD-B, PDD-C,
  validation reviews, and PDD-CIR.
- Defined access-policy requirements for project developers, PDD validators,
  document authorship, review submission, and downstream workflow gates.
- Translated the `pdd-workflow-gate.md` approval contract into Fluree artifact
  lookup queries or transaction policy requirements.

Exit criteria:

- The Fluree layer uses canonical NIAS IRIs and introduces no parallel data
  model terms unless the ontology is first updated.
- The ledger bootstrap contents are listed in a reproducible order.
- The team knows which SHACL constraints Fluree can enforce at transaction time
  and which constraints must stay in application/service validation.
- The Flutter workflow shell has a target transaction shape for each PDD step.

### Phase 7: Implement The Workflow Shell

Tasks:

- Route users through PDD-A, PDD-B, PDD-C, validation reviews, and PDD-CIR.
- Persist generated RDF or JSON-LD payloads between steps.
- Capture document message IDs and resource/IPFS URIs after submission.
- Carry approved validation review references into PDD-CIR.
- Implement the PDD-CIR approval gate from `pdd-workflow-gate.md`.
- Separate project developer and PDD validator roles.
- Block downstream steps until prerequisites are complete.

Exit criteria:

- A developer can complete PDD-A, PDD-B, and PDD-C submissions.
- A validator can review each submitted section.
- A developer can create PDD-CIR only from approved review references.

### Phase 8: Add Regression Checks

Tasks:

- Add repeatable commands for:
  - Turtle syntax validation.
  - SHACL fixture validation.
  - `shape2flutter lint`.
  - `shape2flutter emit-jsonld`.
  - `shape2flutter build`.
  - `shape2flutter preview --serve=false --no-browser`.
- Consider adding these checks to CI once the local workflow is stable.

Exit criteria:

- A single local command or short documented sequence proves the generated PDD
  workflow artifacts still compile.
- Invalid fixtures continue to fail for the intended reasons.

## Suggested Work Order

1. Reconcile `legacy-field-map.csv` with current canonical PDD mappings.
2. Add or adjust PDD fixtures so every section has at least one valid example.
3. Confirm whether PDD-B needs a canonical workflow wrapper shape.
4. Create `pdd-workflow-ui-shapes.ttl` for PDD-A first.
5. Add PDD-B, PDD-C, and PDD-CIR UI shapes.
6. Add PDD-A, PDD-B, and PDD-C validation review UI aliases.
7. Add `build-pdd-workflow.sh`.
8. Run the build and no-server preview compile.
9. Inspect generated forms and refine UI annotations.
10. Define the Fluree deployment projection once the SHACL work is stable.
11. Implement the Flutter workflow shell around the generated forms and Fluree
    transaction templates.

## Acceptance Criteria

The PDD workflow is ready for application integration when:

- All intended PDD creation and validation forms are generated.
- Generated Dart compiles in the preview app.
- PDD-A, PDD-B, PDD-C, review, and PDD-CIR fixtures validate against canonical
  SHACL.
- Repeatable sections render as repeatable subforms, not plain text fields.
- PDD-CIR can only be assembled from approved PDD-A, PDD-B, and PDD-C validation
  review references.
- The Fluree deployment projection documents the ledger bootstrap, JSON-LD
  context, SHACL compatibility, policy requirements, and transaction templates
  without becoming a second data model.
- The implementation path is reproducible from repository scripts and docs.
