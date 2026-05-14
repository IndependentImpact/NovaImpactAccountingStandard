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
   - Create common node shapes (IPFS resources, OWL-Time, crediting period, SKOS value constraints, technology/measure, state/indicator value, indicator definition, indicator observation).
   - Create project design shapes from PDD-A.
   - Create impact declaration shapes from PDD-B.
   - Create document metadata and workflow submission shapes.
   - Keep shapes open by default during migration, using `sh:closed true` only where needed.

5. **Phase 4: Convert R functions into compatibility adapters**
   - Replace hard-coded string outputs for controlled values with SKOS IRIs.
   - Emit canonical namespace IRIs.
   - Emit `impactont:hasIndicatorValue` instead of `impactont:hasValue`.
   - Replace `nias-o:unitOfMeasure` literals with `ind:hasUnit` links to QUDT unit IRIs.
   - Replace embedded ad hoc methodologies and indicators with links to stable local concept resources where possible.
   - Keep a legacy-to-canonical mapping table.
   - Run SHACL validation after adapter output generation.

6. **Phase 5: Add claim and report wrappers**
   - Model PDD and monitoring report content as `claimont:Report` instances.
   - Use `claimont:isMadeBy` for reporting agent identity.
   - Use `claimont:hasSubject` for project/impact/state/document subject linkage.
   - Use `aiao:ImpactClaim`, `aiao:StateClaim`, and `aiao:StateProvenanceClaim` where needed.
   - Link document metadata to report content via a clear property.

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
