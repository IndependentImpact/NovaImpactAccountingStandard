# Semantic Standard Operating Model Finish Plan

Temporary branch planning note for
`codex/finish-semantic-standard-operating-model`.

This file is local planning material and is not intended to be included in the
final pull request.

## Objective

Finish the local semantic operating model for the Nova Impact Accounting
Standard.

The goal is not to implement Hedera, IPFS, or Fluree integration in this branch.
The goal is to express and operate the standard in terms of semantic artifacts:
ontology, concept schemes, SHACL shapes, anchor definitions, requirement-anchor
mappings, generated UI bundles, rendering profiles, report outputs, and
SHACL-valid proof artifacts.

## Completion Checklist

### 1. Repository Housekeeping

- [x] Merge requirement-to-anchor coverage work into `main`.
- [x] Pull latest `origin/main` locally.
- [x] Create branch `codex/finish-semantic-standard-operating-model`.
- [x] Create this branch-local, gitignored plan.

### 2. Define The Release Package

- [x] Define what files constitute a versioned NIAS semantic standard release.
- [x] Document the dependency order between ontology, concept schemes, SHACL
  shapes, anchor definitions, mappings, workflow YAMLs, rendering profiles, and
  generated artifacts.
- [x] Identify which files are canonical source artifacts and which files are
  generated or derived artifacts.
- [x] Define the expected release manifest fields, including version label,
  schema CID placeholders, content hash placeholders, and artifact roles.
- [x] Add tests or checks proving all listed release package files exist and
  parse.

Implemented:

- Added `dataRequirements/releases/1.0.0/semantic-standard-release-package.md`.
- Added `dataRequirements/releases/1.0.0/semantic-standard-release-manifest.jsonld`.
- Added `dataRequirements/tests/test_semantic_standard_release_package.py`.
- Current verification:
  - `/usr/local/bin/python3 -m unittest dataRequirements.tests.test_semantic_standard_release_package -q`

### 3. Canonical Bundle Generation

- [x] Confirm the canonical SHACL source bundle for the PDD UI.
- [x] Confirm the canonical SHACL source bundle for the PDD validation UI.
- [x] Confirm the canonical SHACL source bundle for the Monitoring Report UI.
- [x] Confirm the canonical SHACL source bundle for the MR verification UI.
- [x] Ensure shape2flutter workflows identify the same canonical shape files
  used by validation and rendering.
- [x] Mark generated Flutter/UI files as downstream outputs, not normative
  source files.

Implemented:

- Added `canonical_bundle` blocks to:
  - `dataRequirements/shape2flutter/workflows/pdd-design.yaml`;
  - `dataRequirements/shape2flutter/workflows/validation-report.yaml`;
  - `dataRequirements/shape2flutter/workflows/monitoring-report.yaml`;
  - `dataRequirements/shape2flutter/workflows/verification-report.yaml`.
- Each primary workflow now declares:
  - its `ui_shape_bundle`;
  - its `canonical_shape_sources`;
  - `generated_output_status: downstream-generated`.
- Aligned the PDD Section C workflow form to canonical `PddSectionCShape`.
- Extended `dataRequirements/tests/test_artifact_split_workflows.py` to verify
  bundle declarations, source existence/parsing, and canonical node-shape
  backing for each workflow form.
- Updated shape2flutter and release package documentation.
- Current verification:
  - `/usr/local/bin/python3 -m unittest dataRequirements.tests.test_artifact_split_workflows -q`

### 4. Artifact Identity Contract

- [x] Finalize the identity fields for schema versions, submitted content,
  submission events, reviewed artifacts, review reports, and proof sidecars.
- [x] Align PDD, MR, DLR, validation report, and verification report fixtures to
  the same identity vocabulary.
- [x] Confirm simulated CIDs and Hedera message IDs are represented consistently
  enough for later integration.
- [x] Add semantic checks that reject mismatched schema/content/version identity
  fields where those fields are already modeled.

Implemented:

- Added `dataRequirements/artifact-identity-contract-shapes.ttl`.
- The contract defines role-specific SHACL shapes for:
  - submitted artifact identity;
  - reviewed artifact identity;
  - monitoring report alignment to a submitted PDD;
  - verification report linkage to a reviewed DLR.
- Added SPARQL constraints that reject:
  - incorrect derived `submissionEventKey`;
  - incorrect derived `submissionMessageUrl`;
  - reviewed-artifact identity that does not match the reviewed artifact node;
  - monitoring alignment identity that does not match the referenced PDD node.
- Aligned the VVS traceability fixture, validation/verification rendering
  fixture, and monitoring rendering fixture with full simulated identity fields.
- Added a full simulated PDD submission node to the monitoring rendering fixture
  so the aligned PDD is also a complete `data:Document` under the existing
  `DocumentShape`.
- Added `dataRequirements/tests/test_artifact_identity_contract.py`.
- Included the identity contract in the release manifest and in the canonical
  bundles declared by all four primary shape2flutter workflows.
- Updated rendered golden fixtures where deterministic input hashes changed.
- Current verification:
  - `/usr/local/bin/python3 -m unittest dataRequirements.tests.test_artifact_identity_contract -q`
  - `/usr/local/bin/python3 -m unittest dataRequirements.tests.test_semantic_standard_release_package dataRequirements.tests.test_artifact_split_workflows -q`
  - `/usr/local/bin/python3 -m unittest discover -s dataRequirements/tests -q`
  - `riot --validate dataRequirements/artifact-identity-contract-shapes.ttl dataRequirements/fixtures/vvs/requirement-anchor-traceability.ttl`

### 5. End-To-End Semantic Fixtures

- [x] Build one complete simulated project package:
  submitted PDD, validation report, Monitoring Report, DLR, verification report,
  and coverage proof sidecars.
- [x] Ensure the fixture traces project -> submitted PDD -> validation report ->
  Monitoring Report + DLR -> verification report.
- [x] Ensure every review field points to a concrete submitted
  `nias-o:ArtifactAnchor`.
- [x] Ensure every emitted `RequirementCoverageProof` validates against SHACL.

Implemented:

- Extended `dataRequirements/fixtures/vvs/requirement-anchor-traceability.ttl`
  with:
  - an explicit simulated project package;
  - submitted PDD, validation report, Monitoring Report, DLR, and verification
    report document metadata;
  - workflow submission, Hedera topic/message, and package membership nodes;
  - monitoring-to-PDD/DLR identity links;
  - validation and verification `RequirementCoverageProofSet` sidecars.
- Extended `dataRequirements/tests/test_requirement_anchor_traceability.py` to
  verify:
  - project package completeness;
  - end-to-end project -> PDD -> validation -> Monitoring Report + DLR ->
    verification traceability;
  - package document SHACL conformance on focused subgraphs;
  - validation/monitoring identity-contract conformance in the traceability
    fixture;
  - validation and verification sidecars partition all emitted
    `RequirementCoverageProof` rows.
- Current verification:
  - `/usr/local/bin/python3 -m unittest dataRequirements.tests.test_requirement_anchor_traceability -q`
  - `/usr/local/bin/python3 -m unittest dataRequirements.tests.test_requirement_anchor_traceability dataRequirements.tests.test_artifact_identity_contract -q`
  - `/usr/local/bin/python3 -m unittest discover -s dataRequirements/tests -p 'test_*.py' -q`

### 6. Rendering Contract

- [x] Verify PDD rendering consumes canonical anchors and identity metadata.
- [x] Verify validation report rendering consumes canonical anchors and emits
  proof sidecars.
- [x] Verify Monitoring Report rendering consumes canonical anchors and identity
  metadata.
- [x] Verify verification report rendering consumes canonical anchors and emits
  proof sidecars.
- [x] Confirm filled forms can render to markdown and PDF without hidden manual
  mappings.

Implemented:

- Extended `dataRequirements/tests/test_pdd_output_compilation.py` to verify
  final PDD metadata anchor keys are emitted in canonical
  `pdd-anchor-definitions.ttl` render order.
- Extended `dataRequirements/tests/test_monitoring_report_rendering.py` to
  verify final Monitoring Report metadata anchor keys are emitted from canonical
  `monitoring-anchor-definitions.ttl` and to verify filled final exports produce
  both markdown and PDF outputs.
- Extended
  `dataRequirements/tests/test_validation_verification_report_rendering.py` to
  verify validation/verification proof sidecar anchor keys resolve through the
  canonical `vvs-requirement-anchor-map.ttl` + anchor definition bundles, and to
  verify filled verification exports produce both markdown and PDF outputs.
- Existing identity metadata coverage for PDD/monitoring/validation/verification
  remains verified in
  `dataRequirements/tests/test_linked_artifact_identity.py`.
- Current verification:
  - `python -m unittest dataRequirements.tests.test_pdd_output_compilation -q`
  - `python -m unittest dataRequirements.tests.test_monitoring_report_rendering -q`
  - `python -m unittest dataRequirements.tests.test_validation_verification_report_rendering -q`
  - `python -m unittest dataRequirements.tests.test_linked_artifact_identity -q`
  - `python -m unittest discover -s dataRequirements/tests -p 'test_*.py' -q`

### 7. Release Verification

- [x] Add one command, script, or unittest target that verifies the full semantic
  standard package locally.
- [x] The verification target should parse ontology and concept schemes.
- [x] The verification target should validate canonical SHACL shapes.
- [x] The verification target should resolve requirement-anchor mappings.
- [x] The verification target should validate end-to-end fixtures.
- [x] The verification target should render reports and validate JSON-LD proof
  sidecars.

Implemented:

- Added `dataRequirements/check-semantic-standard-release.sh` as a single local
  release verification entry point.
- The script composes existing semantic-package suites for:
  - ontology + concept scheme parsing/conformance;
  - canonical SHACL validation;
  - requirement-anchor mapping integrity + traceability;
  - end-to-end fixture validation;
  - report rendering and proof-sidecar validation.
- Added
  `dataRequirements/tests/test_semantic_standard_release_verification_command.py`
  to verify the command entry point is executable, declares the expected suite,
  and is documented in the release package document.
- Updated
  `dataRequirements/releases/1.0.0/semantic-standard-release-package.md` with
  the verification entry point and exact composed unittest command.
- Current verification:
  - `python -m unittest dataRequirements.tests.test_semantic_standard_release_verification_command -q`
  - `dataRequirements/check-semantic-standard-release.sh`
  - `python -m unittest discover -s dataRequirements/tests -p 'test_*.py' -q`

## Working Notes

- Keep Hedera, IPFS, and Fluree out of scope except as simulated identifiers.
- Treat semantic correctness as the acceptance criterion.
- Prefer canonical RDF/SHACL files as source of truth.
- Treat UI bundles, markdown, PDF, website output, metadata sidecars, and proof
  sidecars as generated or operational artifacts.
- Keep this plan updated as work progresses.
