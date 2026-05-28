# VVS Phase 5 governance and deprecation notes (release 1.0.0)

This release completes Phase 5 governance and deprecation requirements for the Validation & Verification Standard (VVS).

## Deprecated PDD metadata validation terms and replacements

- `TERM-PDD-METADATA-001` → `REQ-PDD-001`
- `TERM-PDD-METADATA-002` → `REQ-PDD-002`
- `TERM-PDD-METADATA-003` → `REQ-PDD-003`

Machine-readable deprecation annotations are published in:

- `glossary/ValidationVerificationStandard.ttl`
- `dataRequirements/mappings/vvs-deprecation-map.ttl`

## Phase 5 release artifact scope for integrators

- ontology: `glossary/NovaImpactAccountingStandardOntology.ttl`, `glossary/ValidationVerificationStandard.ttl`
- requirement shapes: `dataRequirements/vvs-requirement-shapes.ttl`
- requirement mappings: `dataRequirements/mappings/{pdd-requirement-map.ttl,dlr-requirement-map.ttl,mr-requirement-map.ttl,vvs-deprecation-map.ttl}`
- fixtures: `dataRequirements/fixtures/vvs/*.ttl`
