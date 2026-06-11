# Validation–Verification UI And Document Split Specification

## 1. Purpose

This document specifies the work required to completely separate the
validation workflow and rendering surfaces from the verification workflow
and rendering surfaces in the NIAS toolchain.

Validation and verification are fundamentally different activities:

- **Validation** is an ex-ante formal compliance review. The object of
  validation is the Project Design Document (PDD). A validator works
  section-by-section and paragraph-by-paragraph against the PDD and its
  supporting evidence, assessing clarity, level of evidence, and completeness
  (the accounting principles). The governing questions are in
  `glossary/GuidingReviewQuestions.ttl` and the requirements in
  `glossary/ValidationVerificationStandard.ttl` with
  `nias-o:reviewMandate nias-cs:validation`.
- **Verification** is an ex-post process in which actual project
  implementation is monitored against the validated monitoring plan set out
  in PDD Section B. The verifier inspects the data lineage and calculations
  recorded in the Data Lineage Report and Monitoring Report. The governing
  questions are the verification-mandate questions in
  `glossary/GuidingReviewQuestions.ttl` and the requirements with
  `nias-o:reviewMandate nias-cs:verification`.

These are carried out at different times, by differently licensed actors
(`nias-cs:pdd-validator` vs. `nias-cs:mr-verifier`), against different
primary artifacts (PDD vs. Monitoring Report + DLR), and must therefore
have separate UIs and separate document rendering profiles.

## 2. Glossary Inventory

### 2.1 Ontology Classes (glossary/NovaImpactAccountingStandardOntology.ttl)

| Class | Mandate | Role |
| --- | --- | --- |
| `nias-o:ReviewMandate` | — | Abstract class for `nias-cs:validation` and `nias-cs:verification` instances |
| `nias-o:ValidationVerificationRequirement` | both | Abstract parent for all VVS requirements |
| `nias-o:ValidationRequirement` | validation | Governs ex-ante review of PDD and related artifacts |
| `nias-o:VerificationRequirement` | verification | Governs ex-post review of DLR, MR, and related artifacts |
| `nias-o:EvidenceRequirement` | both | Specifies evidence type and quality required |
| `nias-o:RequirementMapping` | both | Links a requirement to artifact anchors |
| `nias-o:DocumentFieldReview` | both | Paragraph-level finding for a specific anchor |
| `nias-o:ReviewTarget` | both | Pairs a reviewed artifact with a reviewed anchor |
| `nias-o:GlobalQualitativeDocumentReview` | validation | Document-level qualitative evaluation (used for validation UI) |
| `nias-o:VerifiedImpactCertificateIssuanceRequestReview` | verification | VIC issuance review (used for verification UI) |
| `nias-o:GenericDocumentReview` | both (legacy) | Generic review; retained for backward compatibility |

### 2.2 Ontology Properties

| Property | Direction | Mandate | Meaning |
| --- | --- | --- | --- |
| `nias-o:reviewMandate` | Requirement → ReviewMandate | — | Tags a requirement as validation-only, verification-only, or both |
| `nias-o:validatedAt` | Requirement → PDD anchor class | validation | Ex-ante anchor at which the requirement is assessed |
| `nias-o:verifiedBy` | Requirement → DLR/MR anchor class | verification | Ex-post anchor at which the requirement is assessed |
| `nias-o:pddSectionAValidationReview` | PDD → review | validation | Approved validation review for PDD Section A |
| `nias-o:pddSectionBValidationReview` | PDD → review | validation | Approved validation review for PDD Section B |
| `nias-o:pddSectionCValidationReview` | PDD → review | validation | Approved validation review for PDD Section C |
| `nias-o:monitoringReportReview` | MR → review | verification | Approved verification review for a Monitoring Report |

### 2.3 Review Mandate Concepts (glossary/NovaImpactAccountingStandardOntology.ttl)

`nias-cs:validation` and `nias-cs:verification` are used as `nias-o:ReviewMandate`
instances throughout the VVS and guiding questions but are not yet declared
as SKOS Concepts with labels and definitions in any TTL file. See Phase 6.

### 2.4 License Scope Concepts (glossary/NovaImpactAccountingStandardGlossary.ttl)

| Concept | Label | Definition |
| --- | --- | --- |
| `nias-cs:pdd-validator` | PDD validator | License scope permitting validation of project design documents |
| `nias-cs:mr-verifier` | MR verifier | License scope permitting verification of monitoring reports |
| `nias-cs:verified` | Verified | Report content has been independently verified and attested |

### 2.5 Guiding Review Questions (glossary/GuidingReviewQuestions.ttl)

| Question | Mandate | Scope | Linked principle |
| --- | --- | --- | --- |
| GQ-001 | `nias-cs:validation` | paragraph | accounting-relevance |
| GQ-002 | `nias-cs:validation` | paragraph | accounting-completeness |
| GQ-003 | `nias-cs:verification` | paragraph | accounting-consistency |
| GQ-004 | `nias-cs:verification` | paragraph | accounting-accountability |
| GQ-005 | `nias-cs:validation` | section | accounting-completeness |
| GQ-006 | `nias-cs:verification` | section | accounting-accuracy |
| GQ-007 | `nias-cs:validation` | document | accounting-accountability |
| GQ-008 | `nias-cs:verification` | document | accounting-verifiability |

Validation guiding questions: GQ-001, GQ-002, GQ-005, GQ-007.
Verification guiding questions: GQ-003, GQ-004, GQ-006, GQ-008.

### 2.6 VVS Requirements (glossary/ValidationVerificationStandard.ttl)

| Requirement | Type | Mandate | Assessed at |
| --- | --- | --- | --- |
| REQ-PDD-001 | ValidationRequirement | validation | `PddSectionAReport` |
| REQ-PDD-002 | ValidationRequirement | validation | `PddSectionBReport` |
| REQ-PDD-003 | ValidationRequirement | validation + verification | `PddSectionCReport` / `MonitoringReport` |
| REQ-PDD-004 | ValidationRequirement + VerificationRequirement | both | `PddSectionCReport` / `MonitoringReport` |
| REQ-PDD-005 | ValidationRequirement + VerificationRequirement | both | `PddSectionCReport` / `MonitoringReport` |
| REQ-DLR-001 | VerificationRequirement | verification | `DataLineageReport` |
| REQ-DLR-002 | VerificationRequirement | verification | `DataLineageReport` |
| REQ-MR-001 | VerificationRequirement | verification | `MonitoringReport` |
| REQ-MR-002 | VerificationRequirement | verification | `MonitoringReport` |
| REQ-CROSS-001 | VerificationRequirement | verification | `MonitoringReport` |
| TERM-PDD-METADATA-001 | ValidationRequirement | validation | deprecated; replaced by REQ-PDD-001 |
| TERM-PDD-METADATA-002 | ValidationRequirement | validation | deprecated; replaced by REQ-PDD-002 |
| TERM-PDD-METADATA-003 | ValidationRequirement | validation | deprecated; replaced by REQ-PDD-003 |

Validation-only requirements: REQ-PDD-001, REQ-PDD-002.
Verification-only requirements: REQ-DLR-001, REQ-DLR-002, REQ-MR-001, REQ-MR-002, REQ-CROSS-001.
Both: REQ-PDD-003, REQ-PDD-004, REQ-PDD-005 (dual-mandate requirements
assessed at PDD Section C for validation and at the MonitoringReport for
verification; they appear in both UI/renderer surfaces, but in each surface
they render only the properties relevant to that mandate).

## 3. Current State Analysis

### 3.1 Already Split

The following surfaces were split as part of the earlier
`pdd-validation-monitoring-verification-split-workplan` (now completed):

| Surface | Validation path | Verification path |
| --- | --- | --- |
| Workflow YAML | `shape2flutter/workflows/validation-report.yaml` | `shape2flutter/workflows/verification-report.yaml` |
| UI shape bundle | `shape2flutter/validation-report-ui-shapes.ttl` | `shape2flutter/verification-report-ui-shapes.ttl` |
| Build script | `shape2flutter/build-validation-report.sh` | `shape2flutter/build-verification-report.sh` |
| shape2flutter export | `shape2flutter/validation_report/tool/export_validation_report_markdown.py` | `shape2flutter/verification_report/tool/export_verification_report_markdown.py` |
| Export config | `document-rendering/config/validation-report-export.yaml` | `document-rendering/config/verification-report-export.yaml` |

Legacy combined paths are retained in archive folders:

- `shape2flutter/workflows/archive/validation-verification.yaml`
- `shape2flutter/archive/validation-verification-ui-shapes.ttl`
- `shape2flutter/archive/build-validation-verification.sh`
- `document-rendering/config/validation-verification-export.yaml` (legacy demo)

### 3.2 Still Combined (Remaining Work)

#### 3.2.1 Shared Rendering Profile

**Location**: `dataRequirements/document-rendering/validation-verification-report-rendering-profile.md`

This is a single combined rendering profile referenced by both the validation
and verification renderers. Its YAML front matter declares both validation and
verification sidecar outputs. Its section headings (Sections 1–4) use
ambiguous language ("Paragraph-Level Validation Findings" for both types). The
rendering map lists both `GlobalQualitativeDocumentReviewUiShape` and
`VerifiedImpactCertificateIssuanceRequestReviewUiShape`.

**Effect**: A validator opening the profile sees verification-related headings.
A verifier sees validation-specific headings. The front-matter profile ID
`nias-validation-verification-report-rendering-profile` appears in all fixture
outputs and is referenced directly by rendered fixture files.

**Required**: Two separate profiles (see Phase 1).

#### 3.2.2 Single Renderer Script with a Dispatch Flag

**Location**: `tooling/document-rendering/render_validation_verification_report_markdown.py`

The renderer resolves its `DEFAULT_PROFILE` to the combined rendering profile.
When `--report-type validation` or `--report-type verification` is passed, it
dispatches rendering differently, but both code paths load the same profile.

The blank-template and rendered-report fixtures also reference the combined
profile ID in their front matter.

**Required**: After the profile is split (Phase 1), update `DEFAULT_PROFILE`
to dispatch per `--report-type` to the appropriate split profile (see Phase 2).

#### 3.2.3 Combined Fixture Files

**Location**: `dataRequirements/document-rendering/fixtures/`

The following fixtures cover both validation and verification in a single file:

- `validation-verification-report-evidence.jsonld`
- `validation-verification-report-input.jsonld`
- `validation-verification-report-invalid-structural.jsonld`
- `validation-verification-report-invalid-vvs-evidence.jsonld`

Tests in `test_validation_verification_report_rendering.py` and
`test_linked_artifact_identity.py` load these combined fixtures.
The rendered fixtures `validation-report-rendered.md` and
`verification-report-rendered.md` reference the combined input fixture name
and the combined profile ID.

**Required**: Split the shared fixtures into type-specific files; update tests
accordingly (see Phase 3).

#### 3.2.4 Combined Legacy Tool Directory

**Location**: `dataRequirements/shape2flutter/validation_verification_report/tool/export_validation_verification_report_markdown.py`

This is the original combined export script. It is still referenced by
`shape2flutter/validation_report/tool/export_validation_report_markdown.py`
as a parent-import path. The combined script contains a `--workflow` argument
that defaults to `nias:workflows/validation-verification` (an archived
workflow ID).

**Required**: Remove the parent-import coupling between the active split export
scripts and the combined legacy script. Each split script should be
self-contained or import only from the shared `tooling/` layer (see Phase 4).

#### 3.2.5 Content Alignment of UI Shapes

**Validation UI (`validation-report-ui-shapes.ttl`)**

- The `GlobalQualitativeDocumentReviewUiShape` is currently generic.
- The section labels reference "guiding questions" without filtering to
  validation-mandate questions only (GQ-001, GQ-002, GQ-005, GQ-007).
- The help text for section 2.0 does not direct the validator to the
  validation-specific rendering profile.
- Paragraph-level findings (section 3.0) use the generic label
  "Paragraph-level validation findings" which is appropriate but the help
  text does not reference PDD anchor definitions.

**Verification UI (`verification-report-ui-shapes.ttl`)**

- `VerifiedImpactCertificateIssuanceRequestReviewUiShape` does not explicitly
  distinguish section-level and paragraph-level review from monitoring plan
  perspective.
- The shape does not prompt the verifier to cross-reference the Monitoring
  Report and DLR anchor definitions when recording findings.
- There is no explicit prompt to record which Monitoring Report version was
  inspected at the paragraph level.

**Required**: Add targeted help text and update section labels in both UI
shapes to align language to PDD (validation) and Monitoring Report/DLR
(verification) respectively (see Phase 5).

#### 3.2.6 Undefined Review Mandate Concepts

`nias-cs:validation` and `nias-cs:verification` appear throughout the VVS,
guiding questions, and requirement maps as `nias-o:ReviewMandate` instances
but are not declared as SKOS Concepts with `skos:prefLabel` and
`skos:definition`. This means they have no machine-readable human labels and
no formal glossary entries.

**Required**: Declare `nias-cs:validation` and `nias-cs:verification` as
SKOS Concepts with definitions aligned to the canonical distinctions above
(see Phase 6).

## 4. Implementation Plan

### Phase 1: Split the Rendering Profile

**Rationale**: The rendering profile is the primary document surface that
determines how a rendered report is structured. Combining validation and
verification in one profile contradicts the principle that they are separate
activities.

**Deliverables**:

1. Create `dataRequirements/document-rendering/validation-report-rendering-profile.md`
   with profile ID `nias-validation-report-rendering-profile`.
   - Front matter: `documentType: Validation Report`; remove all
     verification-specific sidecar references.
   - Headings explicitly named for PDD assessment:
     - `## Section 1. Global PDD Evaluation`
     - `### 1.1 Document-Level PDD Qualitative Evaluation`
     - `## Section 2. PDD Section-Level Evaluation (Guiding Questions)`
     - `## Section 3. PDD Paragraph-Level Validation Findings`
     - `## Section 4. Validation VVS Requirement Coverage`
   - Rendering map references only `GlobalQualitativeDocumentReviewUiShape`
     and validation-mandate VVS requirements.
   - Sidecar outputs: `validation-report.metadata.jsonld` and
     `validation-report.validation.json` only.
   - Note in the profile header that guiding questions GQ-001, GQ-002,
     GQ-005, GQ-007 apply and that VVS requirements in scope are REQ-PDD-001,
     REQ-PDD-002, REQ-PDD-003 (validation facet), REQ-PDD-004 (validation
     facet), and REQ-PDD-005 (validation facet).

2. Create `dataRequirements/document-rendering/verification-report-rendering-profile.md`
   with profile ID `nias-verification-report-rendering-profile`.
   - Front matter: `documentType: Verification Report`; remove all
     validation-specific sidecar references.
   - Headings explicitly named for Monitoring Report/DLR assessment:
     - `## Section 1. Global Monitoring Report Evaluation`
     - `### 1.1 Document-Level Monitoring Report Qualitative Evaluation`
     - `## Section 2. Monitoring Report Section-Level Evaluation (Guiding Questions)`
     - `## Section 3. Monitoring Report Paragraph-Level Verification Findings`
     - `## Section 4. Verification VVS Requirement Coverage`
   - Rendering map references only
     `VerifiedImpactCertificateIssuanceRequestReviewUiShape` and
     verification-mandate VVS requirements.
   - Sidecar outputs: `verification-report.metadata.jsonld` and
     `verification-report.validation.json` only.
   - Note in the profile header that guiding questions GQ-003, GQ-004,
     GQ-006, GQ-008 apply and that VVS requirements in scope are REQ-DLR-001,
     REQ-DLR-002, REQ-MR-001, REQ-MR-002, REQ-CROSS-001, REQ-PDD-003
     (verification facet), REQ-PDD-004 (verification facet), and REQ-PDD-005
     (verification facet).

3. Move `dataRequirements/document-rendering/validation-verification-report-rendering-profile.md`
   to the `archive/` folder with a note pointing to the two split profiles.

4. Update tests in `test_validation_verification_rendering_profile.py` to
   test each split profile separately (one test class per profile).

**Completion criteria**:
- `validation-report-rendering-profile.md` and
  `verification-report-rendering-profile.md` exist, have separate profile IDs,
  and contain no cross-references to the other mandate's sections.
- All section headings in the validation profile reference PDD; all headings
  in the verification profile reference Monitoring Report or DLR.
- Tests pass confirming the section structure of each profile.
- The combined profile is moved to archive.

### Phase 2: Update the Renderer to Dispatch Per Profile

**Rationale**: The renderer currently uses a single `DEFAULT_PROFILE`. After
Phase 1, two profiles exist and the renderer must load the appropriate one.

**Deliverables**:

1. In `tooling/document-rendering/render_validation_verification_report_markdown.py`,
   replace `DEFAULT_PROFILE` with a dict:
   ```python
   DEFAULT_PROFILES = {
       "validation": REPO_ROOT / "dataRequirements/document-rendering/validation-report-rendering-profile.md",
       "verification": REPO_ROOT / "dataRequirements/document-rendering/verification-report-rendering-profile.md",
   }
   ```
   When `--profile` is not explicitly provided, resolve the default profile
   from `DEFAULT_PROFILES[args.report_type]`.

2. Verify that `render_blank_markdown` and `render_filled_markdown` both
   accept the resolved profile path and do not fall back to the combined
   profile.

3. Update the export configs to no longer reference the combined profile
   (the renderer now handles this automatically via `--report-type`).

4. Update rendered fixture files:
   - `validation-report-blank-template.md`: change `profile` front-matter field
     to `nias-validation-report-rendering-profile`.
   - `verification-report-blank-template.md`: change `profile` front-matter
     field to `nias-verification-report-rendering-profile`.

5. Regenerate `validation-report-rendered.md` and `verification-report-rendered.md`
   using the split profiles.

**Completion criteria**:
- Running `render_validation_verification_report_markdown.py --report-type validation`
  without `--profile` uses the validation profile exclusively.
- Running with `--report-type verification` uses the verification profile
  exclusively.
- Blank template fixtures carry the correct profile ID in their front matter.
- All existing renderer tests pass.

### Phase 3: Split Combined Fixture Files

**Rationale**: Combined fixture names imply a shared artifact. Separate
fixtures reinforce that validation and verification take different inputs.

**Deliverables**:

1. Create `dataRequirements/document-rendering/fixtures/validation-report-input.jsonld`
   from the validation-relevant portion of `validation-verification-report-input.jsonld`.
   The content should represent a `GenericDocumentReview` or
   `GlobalQualitativeDocumentReview` over a PDD artifact.

2. Create `dataRequirements/document-rendering/fixtures/verification-report-input.jsonld`
   from the verification-relevant portion. The content should represent a
   `VerifiedImpactCertificateIssuanceRequestReview` over a Monitoring Report
   artifact.

3. Create `dataRequirements/document-rendering/fixtures/validation-report-evidence.jsonld`
   carrying PDD-specific evidence (VVS proof shapes for REQ-PDD-*).

4. Create `dataRequirements/document-rendering/fixtures/verification-report-evidence.jsonld`
   carrying DLR/MR-specific evidence (VVS proof shapes for REQ-DLR-*, REQ-MR-*,
   REQ-CROSS-001).

5. Create `dataRequirements/document-rendering/fixtures/validation-report-invalid-structural.jsonld`
   and `verification-report-invalid-structural.jsonld` for negative-path test
   coverage.

6. Update all tests in `test_validation_verification_report_rendering.py`,
   `test_linked_artifact_identity.py`, and any other tests that reference the
   combined fixture files to reference the split fixtures instead.

7. Move the four combined fixture files to an `archive/` or `legacy/` subfolder
   (do not delete; they may be needed for backward compatibility checks).

**Completion criteria**:
- No active test references `validation-verification-report-*.jsonld` fixture
  files.
- Separate validation and verification fixtures exist and are loaded by the
  correct test classes.
- All tests pass.

### Phase 4: Decouple the Legacy Combined Export Script

**Rationale**: The active validation export script
`shape2flutter/validation_report/tool/export_validation_report_markdown.py`
currently imports from the combined legacy script via a relative path, coupling
the active split path to the archived combined path.

**Deliverables**:

1. Identify all imports from
   `shape2flutter/validation_verification_report/tool/export_validation_verification_report_markdown.py`
   in the active split scripts.

2. Move any shared helper logic into a common module under
   `tooling/document-rendering/` so both the validation and verification
   export scripts can import from a shared location without depending on
   the archived combined script.

3. Confirm that `shape2flutter/validation_report/tool/export_validation_report_markdown.py`
   and `shape2flutter/verification_report/tool/export_verification_report_markdown.py`
   import only from `tooling/document-rendering/` or from the Python standard
   library.

4. Move `shape2flutter/validation_verification_report/` to
   `shape2flutter/archive/validation_verification_report/` to signal that it
   is no longer an active path.

**Completion criteria**:
- Neither active split export script has a direct import path that traverses
  into `validation_verification_report/`.
- The `validation_verification_report/` directory is archived.
- All existing export engine tests pass.

### Phase 5: Align UI Shape Language to Artifact Type

**Rationale**: UI labels and help text are the primary guide for practitioners
using the form. Validation forms must use PDD-oriented language; verification
forms must use Monitoring Report/DLR-oriented language.

**Deliverables** (in `dataRequirements/shape2flutter/`):

**For `validation-report-ui-shapes.ttl`** (operates on `GlobalQualitativeDocumentReviewUiShape`):

1. Update `ui:label` for the document-level qualitative judgement property to:
   `"1.1 Global PDD qualitative evaluation (validation guiding questions GQ-001, GQ-002, GQ-005, GQ-007)"`.

2. Update `ui:help` for that property to explicitly state:
   `"Respond to the validation guiding questions: GQ-001 (relevance of stated purpose), GQ-002 (completeness of justification), GQ-005 (section-level narrative coherence), GQ-007 (full-document coherence). These questions are defined in GuidingReviewQuestions.ttl."`.

3. Update `ui:label` for the section-level qualitative judgement property to:
   `"2.0 PDD section-level qualitative evaluation (validation guiding question GQ-005)"`.

4. Update `ui:label` for paragraph-level findings to:
   `"3.0 PDD paragraph-level validation findings (per PDD anchor definitions)"`.

5. Update `ui:help` for the `reviewTarget.reviewedArtifact` field to:
   `"IRI of the PDD version being validated."`.

6. Update `ui:help` for the `reviewTarget.reviewedAnchor` field to:
   `"IRI of the specific PDD anchor (section or paragraph) being validated. Refer to pdd-anchor-definitions.ttl."`.

7. Update the `finalReviewDecision` label to:
   `"4.0 Final validation decision (approve or reject the PDD)"`.

**For `verification-report-ui-shapes.ttl`** (operates on `VerifiedImpactCertificateIssuanceRequestReviewUiShape`):

1. Update `ui:label` for `hasWorkflowSubmission` to:
   `"1.0 Verification workflow submission context"`.

2. Add a document-level qualitative judgement property (if not already present)
   with `ui:label`:
   `"1.1 Monitoring Report global qualitative evaluation (verification guiding questions GQ-003, GQ-004, GQ-006, GQ-008)"`
   and `ui:help`:
   `"Respond to the verification guiding questions: GQ-003 (consistency of implemented activity with purpose), GQ-004 (material changes disclosure), GQ-006 (section-level evidence alignment), GQ-008 (cross-section and linked-artifact coherence). These questions are defined in GuidingReviewQuestions.ttl."`.

3. Update `ui:label` for paragraph-level anchor findings to:
   `"2.0 Monitoring Report paragraph-level verification findings (per MR/DLR anchor definitions)"`.

4. Update `ui:help` for the `reviewTarget.reviewedArtifact` field to:
   `"IRI of the Monitoring Report version being verified."`.

5. Update `ui:help` for the `reviewTarget.reviewedAnchor` field to:
   `"IRI of the specific Monitoring Report or Data Lineage Report anchor being verified. Refer to monitoring-anchor-definitions.ttl and dlr-anchor-definitions.ttl."`.

6. Update `ui:label` for the `finalReviewDecision` property to:
   `"3.0 Final verification decision (approve or reject the Monitoring Report)"`.

**Completion criteria**:
- No `ui:label` or `ui:help` text in `validation-report-ui-shapes.ttl`
  references monitoring reports, DLR, or verification-specific concepts.
- No `ui:label` or `ui:help` text in `verification-report-ui-shapes.ttl`
  references PDD sections or validation-specific concepts.
- The guiding question IDs referenced in help text match the mandate-filtered
  sets from Section 2.5 above.
- shape2flutter lint passes on both updated files.

### Phase 6: Declare Review Mandate Concepts Formally

**Rationale**: `nias-cs:validation` and `nias-cs:verification` are used as
`nias-o:ReviewMandate` instances but lack SKOS declarations.

**Deliverables** (in `glossary/NovaImpactAccountingStandardOntology.ttl` or a
dedicated `glossary/ReviewMandateConcepts.ttl`):

1. Declare `nias-cs:validation` as:
   ```ttl
   nias-cs:validation a nias-o:ReviewMandate, skos:Concept ;
       skos:prefLabel "Validation"@en ;
       skos:definition "Ex-ante formal compliance review of a Project Design Document by a licensed validator. Validation assesses the PDD section-by-section and paragraph-by-paragraph for clarity, completeness, and level of evidence against the Validation & Verification Standard and the accounting principles."@en ;
       skos:inScheme nias-cs:ReviewMandateScheme .
   ```

2. Declare `nias-cs:verification` as:
   ```ttl
   nias-cs:verification a nias-o:ReviewMandate, skos:Concept ;
       skos:prefLabel "Verification"@en ;
       skos:definition "Ex-post process in which actual project implementation is monitored in accordance with the validated monitoring plan set out in PDD Section B. Verification inspects the Data Lineage Report and Monitoring Report for data lineage and calculation correctness."@en ;
       skos:inScheme nias-cs:ReviewMandateScheme .
   ```

3. Declare `nias-cs:ReviewMandateScheme` as a `skos:ConceptScheme` with both
   concepts as top concepts.

4. Add a test to `test_concept_schemes.py` that verifies both concepts are
   declared with labels and definitions and belong to the scheme.

**Completion criteria**:
- `nias-cs:validation` and `nias-cs:verification` have `skos:prefLabel` and
  `skos:definition` triples loadable from the glossary.
- A SKOS scheme groups them.
- SHACL validation (pyshacl) against `PrincipleShapes.ttl` passes for the
  new declarations.
- Concept scheme test passes.

## 5. Out of Scope

The following items are explicitly out of scope for this workplan:

1. Changing the ontology class hierarchy or VVS requirement text.
2. Splitting the underlying Python renderer into two entirely separate files
   (the dispatch-flag approach in Phase 2 is sufficient; full duplication
   of the renderer would increase maintenance burden without adding clarity).
3. Changing the PDD rendering pipeline or PDD workflow shell.
4. Changing the Monitoring Report rendering pipeline.
5. Altering ledger deployment or Hedera topic configuration.

## 6. Sequencing and Dependencies

```
Phase 6 (declare concepts)     — no dependencies
Phase 1 (split rendering profile) — no dependencies
Phase 5 (align UI shape language) — no dependencies
Phase 2 (update renderer dispatch) — depends on Phase 1
Phase 3 (split fixtures) — depends on Phase 1 and Phase 2
Phase 4 (decouple legacy export) — depends on Phase 3
```

Phases 1, 5, and 6 can be started in parallel. Phase 2 requires Phase 1 to
be complete. Phase 3 requires Phases 1 and 2 to be complete. Phase 4 requires
Phase 3 to be complete.
