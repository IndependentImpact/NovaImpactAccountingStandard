# NIAS Fluree Deployment Projection

This directory defines a Fluree ledger deployment package for the Nova Impact
Accounting Standard.

The package is an operational projection of the semantic standard. It must load
and use the canonical NIAS ontology, SKOS concept schemes, document schema
resources, and SHACL shapes. It must not create a second data model.

## Current Status

Status: Phase 6 specification package.

This package is ready for implementation work after the PDD SHACL and
shape2flutter workflow checks have passed. It is not yet a deployer script. The
first deployer should consume the files documented here and emit Fluree
transactions without changing canonical IRIs.

## Files

- `context.jsonld` - stable JSON-LD prefixes for transactions, queries, and
  policy examples.
- `bootstrap-order.md` - deterministic source artifact load order.
- `bootstrap-ledger.jsonld` - machine-readable bootstrap manifest.
- `shacl-compatibility-matrix.md` - current assessment of SHACL constraints and
  where they should be enforced.
- `artifact-lookup-queries.md` - Fluree query templates for dropdowns and
  workflow gates.
- `pdd-workflow-transactions.md` - transaction templates for PDD-A, PDD-B,
  PDD-C, validation reviews, and PDD-CIR.
- `policy-requirements.md` - access-control and workflow-gate requirements.

## Deployment Model

The target deployment flow is:

1. Validate source Turtle files locally.
2. Create or select a Fluree ledger.
3. Load ontology and concept scheme artifacts.
4. Load document schema resources and canonical SHACL shapes.
5. Load policy transactions when the policy design is finalized.
6. Use the PDD workflow transaction templates from the Flutter workflow shell.
7. Use lookup queries to populate dropdowns and enforce workflow gates.

Fluree supports JSON-LD transactions and can also accept Turtle request bodies
for transaction endpoints. The first implementation can therefore load the
canonical Turtle artifacts directly, then introduce JSON-LD conversion only if
batching, hosted-ledger limits, or audit traceability require it.

## Environment

Do not commit ledger credentials or identity keys. Use runtime configuration:

```text
FLUREE_ENDPOINT=https://data.flur.ee
FLUREE_LEDGER=independent-impact/nias
FLUREE_IDENTITY=did:key:...
FLUREE_DRY_RUN=true
FLUREE_BATCH_SIZE=1
```

The final deployer should accept equivalent command-line flags so local and
hosted deployments are reproducible.

## Source Of Truth

Canonical source artifacts:

- `glossary/NovaImpactAccountingStandardOntology.ttl`
- `glossary/NovaImpactAccountingStandardGlossary.ttl`
- `indicators/GHGIndicators.ttl`
- `knowledgeDomains/GHGKnowledgeDomains.ttl`
- `methodologies/GHGMethodologies.ttl`
- `dataRequirements/*.ttl`
- `dataRequirements/releases/`

Generated Flutter forms and shape2flutter UI adapter shapes are not ledger
schema. They are UI projections of the canonical SHACL.

## Implementation Checks

Before deploying:

```bash
riot --validate \
  glossary/NovaImpactAccountingStandardOntology.ttl \
  glossary/NovaImpactAccountingStandardGlossary.ttl \
  indicators/GHGIndicators.ttl \
  knowledgeDomains/GHGKnowledgeDomains.ttl \
  methodologies/GHGMethodologies.ttl \
  dataRequirements/*.ttl
```

```bash
python3 -m unittest discover -s dataRequirements/tests -q
```

After deployment, run a small transaction test for each PDD workflow step and
confirm that invalid PDD-CIR references are rejected by the workflow gate.

## Fluree References

Checked on 2026-05-21:

- JSON-LD foundation: https://developers.flur.ee/docs/learn/foundations/json-ld/
- HTTP transaction endpoints: https://next.developers.flur.ee/docs/reference/http-api/transactions/
- SHACL validation: https://next.developers.flur.ee/docs/reference/shacl-validation/
- Policy syntax: https://developers.flur.ee/docs/reference/policy-syntax/
