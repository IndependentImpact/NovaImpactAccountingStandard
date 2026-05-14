# Remaining SHACL Migration Actions (Execution Order)

This checklist is derived from `dataRequirements/shacl-migration-path.md`,
excluding actions already marked as completed there. Items completed after this
checklist was created are retained with artifact pointers.

1. **Phase 0: Freeze and inventory legacy inputs**
   - No remaining actions (completed 2026-05-14).
   - Freeze recorded in `dataRequirements/legacy-reference-freeze.md` and
     `dataRequirements/legacy-reference-manifest.sha256`.
   - Field inventory recorded in `dataRequirements/legacy-field-map.csv`.
   - Minimal legacy RDF fixtures recorded in `dataRequirements/fixtures/legacy/`.

2. **Phase 1: Normalize namespaces and value semantics**
   - No remaining actions (completed 2026-05-14).
   - Canonical namespace, MethOnt, InfoComm, and Hashgraph choices are recorded
     in `glossary/NovaImpactAccountingStandardOntology.ttl`.
   - Methodology use is claim-centered via `nias-o:usesMethodology` on
     `claimont:Claim`.
   - Document-schema validation dispatch is recorded with
     `nias-o:validatingShape`.
   - Hedera consensus evidence is represented with Hashgraph Ontology
     `hedera:TopicMessage` resources.

3. **Phase 2: Build concept schemes**
   - No remaining actions (completed).

4. **Phase 3: Author core SHACL shapes**
   - No remaining actions (completed 2026-05-14).
   - Common node shapes are recorded in `dataRequirements/common-shapes.ttl`.
   - PDD-A project design shapes are recorded in
     `dataRequirements/project-design-shapes.ttl`.
   - PDD-B impact declaration shapes are recorded in
     `dataRequirements/impact-declaration-shapes.ttl`.
   - Document metadata and workflow submission shapes are recorded in
     `dataRequirements/document-shapes.ttl`.
   - Shapes remain open by default; no Phase 3 shape uses `sh:closed true`.

5. **Phase 4: Convert R functions into compatibility adapters**
   - No remaining actions (completed 2026-05-14).
   - Compatibility adapters are recorded in
     `dataRequirements/adapters/phase4_compatibility_toFluree.R`.
   - Legacy-to-canonical mappings are recorded in
     `dataRequirements/legacy-to-canonical-map.csv`.
   - The frozen `reference/` audit baseline remains unchanged.

6. **Phase 5: Add claim and report wrappers**
   - No remaining actions (completed 2026-05-14).
   - `nias-o:ProjectDesignDocument` added as a `claimont:Report` subclass in
     `glossary/NovaImpactAccountingStandardOntology.ttl`.
   - `nias-o:MonitoringImpactReport` added as a `claimont:Report` subclass for
     monitoring period report content.
   - Optional PDD section subclasses added: `nias-o:PddSectionAReport`,
     `nias-o:PddSectionBReport`, `nias-o:PddSectionCReport`.
   - `nias-o:reportContent` added to link `data:Document` to `claimont:Report`.
   - `nias-o:stateClaim` and `nias-o:stateProvenanceClaim` added to link reports
     to `aiao:StateClaim` and `aiao:StateProvenanceClaim`.
   - `nias-o:implementationPlan` and `nias-o:monitoringPlan` added to link
     reports and projects to `prov:Plan` nodes (used only for explicit future
     planning resources; the PDD itself is not typed as `prov:Plan`).
   - `nias-o:usesMethodology` domain widened to include `claimont:Report`.
   - `nias-o:impactClaim` domain widened to include `claimont:Report`.
   - Report wrapper SHACL shapes recorded in `dataRequirements/report-shapes.ttl`.
   - Example fixtures recorded in:
     - `dataRequirements/fixtures/report-wrapper-pdd-valid.ttl` (valid PDD wrapper)
     - `dataRequirements/fixtures/report-wrapper-pdd-invalid.ttl` (invalid cases)

7. **Phase 6: Design monitoring report shapes**
   - Use `impactont:Impact` for measured impact.
   - Use claim/report context to distinguish ex-ante vs ex-post.
   - Add a local status concept scheme if needed (`projected`, `measured`, `verified`, `revised`).
   - Require measured states and indicator values in monitoring report shapes.
   - Link measured impacts to project, monitoring period, methodology, supporting documents, and verification attestation.

8. **Phase 7: Validation and cutover**
   - Validate fixtures with pySHACL (or equivalent).
   - Validate with ontology and concept scheme graphs loaded.
   - Add regression tests for controlled vocabularies, monitored/unmonitored branches, invalid periods, invalid IPFS URI, invalid namespace IRI, and missing workflow submission fields.
   - Publish versioned SHACL files and document schema resources.
   - Deprecate old R schema names after canonical shapes/adapters pass validation.
