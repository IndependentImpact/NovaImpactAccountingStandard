# Fluree Ledger Deployment Package

Status: Phase 6 package created on 2026-05-21.

The implementation files live in `dataRequirements/fluree/`. This document
remains the higher-level specification and extraction path for a future
`web32fluree` tool.

This document specifies the future Fluree deployment layer for the Nova Impact
Accounting Standard. It should be implemented only after the ontology, concept
schemes, document schema resources, and SHACL data requirements have stabilized.

## Purpose

Independent Impact uses Fluree as its graph database. The standard itself is
defined as semantic web artifacts:

- ontology terms;
- SKOS concept schemes;
- indicator, knowledge-domain, and methodology vocabularies;
- document schema resources;
- SHACL shapes for data requirements;
- workflow and document reference requirements.

The Fluree layer should package those artifacts into a reproducible ledger
bootstrap. It must not create a second data model. It is a deployment and
operational projection of the semantic standard into Fluree.

## Non-Goals

- Do not replace the ontology with Fluree-specific classes or predicates.
- Do not duplicate SHACL constraints in a separate schema language.
- Do not invent new Fluree terms unless the canonical ontology is first updated.
- Do not embed environment-specific secrets, credentials, or private endpoints
  in repository artifacts.
- Do not start this work before the SHACLs needed for the current workflow are
  complete and tested.

## Relationship To SHACL Work

The implementation order is:

1. Finish canonical SHACL coverage.
2. Add representative valid and invalid fixtures.
3. Confirm local validation with `riot`, pySHACL, and existing test tooling.
4. Generate UI-facing shapes where needed for `shape2flutter`.
5. Define the Fluree ledger deployment package.
6. Implement the workflow shell against the Fluree transaction templates.

The Fluree package depends on the canonical SHACLs because Fluree should load
and enforce those shapes at transaction time where supported.

## Package Responsibilities

The deployment package should provide:

- a Fluree-ready JSON-LD context;
- deterministic bootstrap ordering;
- Fluree transaction payloads for ontology terms;
- Fluree transaction payloads for concept schemes;
- Fluree transaction payloads for document schema resources;
- Fluree transaction payloads for SHACL shapes;
- a compatibility matrix for SHACL constraints in Fluree;
- seed queries for artifact lookup;
- transaction templates for workflow submissions;
- access-policy requirements;
- deployment notes for hosted ledgers such as `data.flur.ee`.

## Proposed Repository Structure

When implementation starts, create:

```text
dataRequirements/fluree/
  README.md
  context.jsonld
  bootstrap-order.md
  bootstrap-ledger.jsonld
  shacl-compatibility-matrix.md
  policy-requirements.md
  artifact-lookup-queries.md
  pdd-workflow-transactions.md
```

The first implementation can be hand-authored or lightly scripted. Extract a
separate reusable tool only after the NIAS package proves the shape of the
problem.

## Inputs

Initial inputs for the NIAS deployment package:

- `glossary/NovaImpactAccountingStandardOntology.ttl`
- NIAS SKOS concept schemes in the glossary and data requirements release files.
- indicator concept schemes.
- knowledge-domain concept schemes.
- methodology concept schemes.
- `dataRequirements/document-shapes.ttl`
- `dataRequirements/document-reference-shapes.ttl`
- `dataRequirements/report-shapes.ttl`
- `dataRequirements/common-shapes.ttl`
- all workflow-specific SHACL files in `dataRequirements/*.ttl`
- release metadata in `dataRequirements/releases/`

The exact file list should be recorded in `bootstrap-order.md` once the SHACL
set is stable.

## Bootstrap Order

The ledger bootstrap should be deterministic. The expected order is:

1. JSON-LD context and namespace aliases.
2. External vocabulary references that are materialized locally, if any.
3. NIAS ontology classes and properties.
4. NIAS concept schemes and concepts.
5. Indicator, knowledge-domain, and methodology schemes.
6. Document schema resources.
7. Common helper shapes.
8. Document, report, and workflow shapes.
9. Workflow-specific shapes.
10. Optional access policies.
11. Optional seed data for development ledgers.

This ordering should avoid loading shape references before the referenced terms
and concept IRIs are known to the ledger.

## JSON-LD Context

`context.jsonld` should make transactions readable while preserving canonical
IRIs. It should include only stable prefixes used by the standard.

Expected prefixes include:

- `nias`
- `nias-o`
- `nias-cs`
- `sh`
- `rdf`
- `rdfs`
- `owl`
- `skos`
- `xsd`
- `dcterms`
- `schema`
- `time`
- `aiao`
- `claimont`
- `impactont`
- `ind`
- `meth`
- `qudt`
- `unit`
- `f` for Fluree policy vocabulary

The context should not change the meaning of canonical IRIs. It is only a
transaction convenience.

## Transaction Package

`bootstrap-ledger.jsonld` should be a Fluree transaction package or a sequence of
transaction payloads. The package should preserve source IRIs and named
resources.

The implementation may need to split transactions by artifact type or by file if
the combined payload becomes too large for a single hosted-ledger transaction.
If splitting is required, the split order belongs in `bootstrap-order.md`.

Each generated or hand-authored transaction should be traceable back to its
source file.

## SHACL Compatibility Matrix

`shacl-compatibility-matrix.md` should classify every canonical shape and any
important property constraint.

Use these categories:

- `fluree-enforced`: expected to work directly in Fluree SHACL validation.
- `fluree-rewrite`: semantically valid SHACL, but needs a Fluree-compatible
  rewrite or simplification.
- `service-enforced`: must be enforced by application or service logic.
- `advisory`: retained for documentation, UI generation, or external validation.

The matrix should call out at least:

- `sh:targetClass`
- `sh:path`
- `sh:minCount`
- `sh:maxCount`
- `sh:datatype`
- `sh:class`
- `sh:node`
- `sh:in`
- `sh:pattern`
- `sh:or`
- property paths
- SPARQL-based constraints

Fluree limitations should be documented against the concrete shapes affected,
not as abstract warnings.

## Artifact Lookup Queries

The package should define reusable lookup queries for UI controls and workflow
gates.

Examples:

- list active document schema resources;
- list approved PDD-A validation reviews for a project;
- list approved PDD-B validation reviews for a project;
- list approved PDD-C validation reviews for a project;
- list indicators by concept scheme;
- list methodologies by knowledge domain or applicable indicator;
- list submitted workflow documents for a project;
- list eligible PDD-CIR artifacts.

These queries should return stable option records:

```json
{
  "id": "canonical artifact IRI",
  "label": "human-readable label",
  "type": "artifact class IRI",
  "source": "ledger name or query identifier"
}
```

The query records can later drive dynamic dropdowns in Flutter or
`shape2flutter` if dynamic option sources are supported.

## Workflow Transaction Templates

`pdd-workflow-transactions.md` should document the transaction shape for each
PDD step:

- PDD Section A submission;
- PDD Section B submission;
- PDD Section C submission;
- PDD Section A validation review;
- PDD Section B validation review;
- PDD Section C validation review;
- PDD certificate issuance request.

For each transaction template, document:

- required input fields;
- generated or supplied `@id` strategy;
- required `@type` values;
- document schema IRI;
- workflow subject IRI;
- author or reviewer identity;
- Hedera message or document reference fields;
- IPFS or resource URI fields;
- expected SHACL target shape;
- prerequisite artifact references.

The templates should use the same canonical predicates as the SHACL shapes and
fixtures.

## Policy Requirements

`policy-requirements.md` should describe access-control requirements before any
Fluree policy is implemented.

At minimum, cover:

- project developer can create and update their own draft PDD submissions;
- project developer can submit PDD sections;
- PDD validator can create validation reviews;
- PDD validator cannot review documents where they have a conflict of interest,
  if that rule is part of the standard or platform policy;
- project developer can create PDD-CIR only from approved PDD-A, PDD-B, and
  PDD-C validation review references;
- read permissions for public, private, encrypted, and VC-backed documents;
- administrative ability to load standard artifacts into a ledger.

Policy implementation details belong after the requirements are stable.

## Environment Configuration

The repository should not store secrets. Deployment should use runtime
configuration for:

- Fluree endpoint;
- ledger name;
- identity or DID;
- signing key or token;
- policy headers;
- environment name;
- dry-run mode;
- transaction batch size.

Example environment variables may include:

```text
FLUREE_ENDPOINT=https://data.flur.ee
FLUREE_LEDGER=independent-impact/nias
FLUREE_IDENTITY=did:key:...
FLUREE_DRY_RUN=true
```

The final variable names should be chosen during implementation.

## Future web32fluree Project

If the NIAS package becomes reusable, extract the generic compiler/deployer into
a separate project named `web32fluree`.

The future tool should accept semantic web artifacts and emit Fluree deployment
packages:

```text
OWL / RDFS / SKOS / SHACL / TTL / JSON-LD
        ->
web32fluree
        ->
Fluree ledger deployment package
```

Likely commands:

```bash
web32fluree compile \
  --ontology glossary/NovaImpactAccountingStandardOntology.ttl \
  --concept-schemes glossary/*.ttl \
  --shapes dataRequirements/*.ttl \
  --out build/fluree
```

```bash
web32fluree deploy \
  --endpoint "$FLUREE_ENDPOINT" \
  --ledger "$FLUREE_LEDGER" \
  --package build/fluree
```

Extraction criteria:

- the NIAS deployment package is working locally;
- bootstrap ordering is deterministic;
- SHACL compatibility classification is repeatable;
- transaction splitting rules are known;
- at least one workflow has end-to-end Fluree transaction templates;
- the reusable parts are clearly separated from NIAS-specific policies.

## Acceptance Criteria

The Fluree ledger deployment package is ready to implement when:

- canonical SHACL coverage for the target workflow is complete;
- fixtures validate locally;
- UI-facing shapes generate and compile where needed;
- the source artifact list is stable;
- this document has been reconciled with current Fluree behavior;
- any hosted-ledger constraints for `data.flur.ee` are known.

The package is complete when:

- it can bootstrap a clean Fluree ledger from repository artifacts;
- it preserves canonical IRIs;
- it loads ontology, concept schemes, document schema resources, and SHACL
  shapes in deterministic order;
- it documents which SHACL constraints Fluree enforces;
- it provides workflow transaction templates;
- it provides artifact lookup queries for UI dropdowns and workflow gates;
- it avoids becoming a second source of truth.
