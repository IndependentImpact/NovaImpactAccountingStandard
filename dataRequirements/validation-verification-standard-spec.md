# Validation & Verification Standard (VVS) Ontology and SHACL Specification

## 1. Purpose

This specification defines how to evolve the current NIAS Turtle assets from section-specific validation logic toward a requirement-centric Validation & Verification Standard (VVS), while preserving existing SHACL validation behavior.

The target state is:

1. scoring vocabularies remain controlled concepts;
2. requirements become named resources with stable IDs;
3. each requirement is implemented by one or more SHACL shapes;
4. requirements are mapped to:
   - PDD anchors for validation (ex ante),
   - Data lineage and monitoring anchors for verification (ex post).

## 2. Scope and Non-Goals

In scope:

1. ontology extensions in `glossary/NovaImpactAccountingStandardOntology.ttl`;
2. new requirement graph(s) and mapping graph(s);
3. new SHACL shapes implementing requirement checks;
4. phase-gated tests and fixtures.

Out of scope for this migration:

1. replacing existing PDD, DLR, MR structural shapes;
2. changing ledger/deployment model;
3. rewriting historical fixtures unless required by new tests.

## 3. Namespace and Artifact Strategy

Use additive namespaces in the same base IRI pattern unless a future release requires separation:

1. `nias-o:` core ontology classes and properties (extended);
2. `nias-cs:` concept schemes (existing);
3. `nias-vvs:` requirement instances and VVS metadata (new graph file);
4. `nias-map:` explicit mapping resources if mapping objects are required (optional, phase 3+).

Recommended new files:

1. `glossary/ValidationVerificationStandard.ttl`
2. `dataRequirements/vvs-requirement-shapes.ttl`
3. `dataRequirements/mappings/pdd-requirement-map.ttl`
4. `dataRequirements/mappings/dlr-requirement-map.ttl`
5. `dataRequirements/mappings/mr-requirement-map.ttl`
6. `dataRequirements/fixtures/vvs/*.ttl`
7. `dataRequirements/tests/test_vvs_requirements.py`

## 4. Core Modeling Pattern

Each requirement is both:

1. a governed requirement resource (ID, text, status, mandate, provenance);
2. an executable SHACL constraint via linked shape(s).

Pattern:

```ttl
nias-vvs:REQ-PDD-001 a nias-o:ValidationRequirement ;
    nias-o:reviewMandate nias-cs:validation ;
    nias-o:implementedByShape nias-o:ReqPdd001Shape ;
    nias-o:validatedAt nias-o:PddSectionAReport .

nias-o:ReqPdd001Shape a sh:NodeShape ;
    sh:targetClass nias-o:PddSectionAReport ;
    ...
```

## 5. Ontology Additions (Minimum)

Add classes:

1. `nias-o:ValidationVerificationRequirement`
2. `nias-o:ValidationRequirement`
3. `nias-o:VerificationRequirement`
4. `nias-o:EvidenceRequirement`
5. `nias-o:RequirementMapping` (optional but recommended)

Add properties:

1. `nias-o:implementedByShape` (Requirement -> sh:Shape)
2. `nias-o:derivedFromRule` (Requirement -> nias-o:ScoringRule or scoring term)
3. `nias-o:validatedAt` (Requirement -> PDD anchor class/resource)
4. `nias-o:verifiedBy` (Requirement -> DLR/MR anchor class/resource)
5. `nias-o:hasEvidenceRequirement` (Requirement -> EvidenceRequirement)
6. `nias-o:requirementId` (literal identifier, optional if URI is canonical)
7. `nias-o:requirementStatus` (draft/active/deprecated concept)

## 6. Constraint Architecture

Keep existing files as structural/base constraints:

1. `project-design-shapes.ttl`
2. `report-shapes.ttl`
3. `data-lineage-shapes.ttl`
4. `monitoring-report-shapes.ttl`

Add requirement shapes in `vvs-requirement-shapes.ttl`:

1. one shape per requirement where practical (`ReqPdd001Shape`);
2. grouped shapes only when multiple requirements share a common cardinality check;
3. each shape carries a stable `sh:name`/`sh:message` with requirement ID.

Rules:

1. no business-critical requirement exists without at least one linked shape;
2. no shape in `vvs-requirement-shapes.ttl` exists without a linked requirement resource;
3. validation and verification requirements may link to separate shapes for different artifact types.

## 7. Phased Delivery Plan

### Phase 1 - Ontology Foundation

Deliverables:

1. Add new requirement classes/properties to ontology.
2. Create `ValidationVerificationStandard.ttl` with at least 5 pilot requirements.
3. No breaking changes to existing shapes.

End-of-phase criteria:

1. all TTL syntax validates;
2. ontology imports and existing tests still pass;
3. requirement resources resolve and use stable IDs.

Tests:

1. `riot --validate glossary/NovaImpactAccountingStandardOntology.ttl`
2. `riot --validate glossary/ValidationVerificationStandard.ttl`
3. `python -m unittest dataRequirements.tests.test_phase7_validation`
4. `python -m unittest dataRequirements.tests.test_validation_verification_shapes`

### Phase 2 - SHACL Requirement Pilot

Deliverables:

1. Add `vvs-requirement-shapes.ttl`.
2. Implement SHACL for the same pilot requirements (PDD-focused first).
3. Link each pilot requirement via `nias-o:implementedByShape`.

End-of-phase criteria:

1. positive fixtures conform;
2. negative fixtures fail with requirement-specific messages;
3. zero regressions in existing PDD workflow tests.

Tests:

1. `riot --validate dataRequirements/vvs-requirement-shapes.ttl`
2. new `python -m unittest dataRequirements.tests.test_vvs_requirements`
3. `python -m unittest dataRequirements.tests.test_pdd_workflow_shapes`
4. `python -m unittest dataRequirements.tests.test_pdd_workflow_gate`

### Phase 3 - Mapping Layer (PDD/DLR/MR)

Deliverables:

1. Add `mappings/pdd-requirement-map.ttl`.
2. Add `mappings/dlr-requirement-map.ttl`.
3. Add `mappings/mr-requirement-map.ttl`.
4. Ensure each pilot requirement has:
   - at least one PDD validation anchor,
   - at least one DLR or MR verification anchor.

End-of-phase criteria:

1. every active requirement has at least one mapping triple for validation or verification;
2. no orphan mappings to missing requirement IDs;
3. mappings are queryable with deterministic SPARQL patterns.

Tests:

1. syntax validation for all mapping TTLs (`riot --validate ...`)
2. new graph integrity tests in `test_vvs_requirements.py`:
   - missing requirement link -> fail
   - missing shape link -> fail
   - mapping to unknown anchor -> fail

### Phase 4 - Coverage Expansion

Deliverables:

1. migrate remaining scoring-derived requirements into `ValidationVerificationStandard.ttl`;
2. implement corresponding SHACL constraints;
3. add fixtures for each requirement family (PDD, DLR, MR).

End-of-phase criteria:

1. 100% of in-scope active requirements mapped to shape(s);
2. 100% of mapped requirements covered by at least one positive and one negative fixture;
3. legacy structural validations remain green.

Tests:

1. `python -m unittest discover -s dataRequirements/tests`
2. optional CI summary report listing:
   - total active requirements,
   - requirements with shapes,
   - requirements with validation mappings,
   - requirements with verification mappings.

### Phase 5 - Governance and Deprecation

Deliverables:

1. mark superseded PDD-metadata-based validation terms as deprecated;
2. document migration map old-term -> requirement ID;
3. publish release notes for integrators.

End-of-phase criteria:

1. no active requirement depends only on deprecated modeling path;
2. deprecation annotations exist and are machine-readable;
3. release artifact includes ontology + shapes + mapping + fixtures.

Tests:

1. regression suite remains green;
2. deprecation integrity test:
   - deprecated term referenced as active control -> fail.

## 8. Test Discipline Requirements

For every new requirement `REQ-*`:

1. add requirement instance triple set;
2. add at least one linked shape;
3. add at least one valid fixture;
4. add at least one invalid fixture;
5. add mapping triple(s) to validation and/or verification anchors;
6. add/extend unit test assertions.

No phase closes unless these are true for all requirements introduced in that phase.

## 9. Change Control

1. Requirement IDs are immutable.
2. Requirement text can be revised, with version/date metadata.
3. Shape IRIs should remain stable; if replaced, keep `dcterms:isReplacedBy`.
4. Breaking semantic changes require minor/major schema version bump aligned with document schema governance.

## 10. Immediate Next Implementation Slice

Start with 3 to 5 pilot requirements:

1. one PDD-A structural/content requirement;
2. one PDD-B impact declaration requirement;
3. one DLR evidence lineage requirement;
4. one MR measured observation requirement;
5. one cross-artifact traceability requirement.

Implement those end-to-end through Phase 3 before scaling to full catalog.
