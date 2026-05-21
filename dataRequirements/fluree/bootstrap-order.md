# Fluree Bootstrap Order

This is the deterministic load order for a NIAS Fluree ledger deployment. The
source artifacts remain authoritative; this file only defines how they should be
projected into a ledger.

Fluree currently accepts JSON-LD or Turtle request bodies for transaction
endpoints, so the first implementation can load Turtle files directly and keep
JSON-LD conversion as an optimization step.

## Ordered Inputs

| Order | Source | Purpose | Load format |
| --- | --- | --- | --- |
| 1 | `dataRequirements/fluree/context.jsonld` | Shared JSON-LD aliases for transactions and queries. | JSON-LD context |
| 2 | `glossary/NovaImpactAccountingStandardOntology.ttl` | NIAS classes, properties, and ontology definitions. | Turtle |
| 3 | `glossary/NovaImpactAccountingStandardGlossary.ttl` | NIAS glossary concepts and controlled vocabularies. | Turtle |
| 4 | `glossary/NovaImpactAccountingStandardShapes.ttl` | Legacy glossary-level helper shapes retained as reference material. | Turtle |
| 5 | `indicators/GHGIndicators.ttl` | Indicator concept scheme artifacts. | Turtle |
| 6 | `knowledgeDomains/GHGKnowledgeDomains.ttl` | Knowledge-domain concept scheme artifacts. | Turtle |
| 7 | `methodologies/GHGMethodologies.ttl` | Methodology concept scheme artifacts. | Turtle |
| 8 | `dataRequirements/releases/1.0.0/nias-shapes-1.0.0.ttl` | Release-level document schema references. | Turtle |
| 9 | `dataRequirements/common-shapes.ttl` | Shared helper shapes for resources, time, quantities, states, and impacts. | Turtle |
| 10 | `dataRequirements/document-reference-shapes.ttl` | Compact document reference and resource artifact shapes. | Turtle |
| 11 | `dataRequirements/document-shapes.ttl` | Document metadata, workflow submission, Hedera message, and document schema resources. | Turtle |
| 12 | `dataRequirements/report-shapes.ttl` | PDD and monitoring report wrapper shapes. | Turtle |
| 13 | `dataRequirements/project-design-shapes.ttl` | PDD-A project design shapes. | Turtle |
| 14 | `dataRequirements/impact-declaration-shapes.ttl` | PDD-B impact declaration and impact requirement shapes. | Turtle |
| 15 | `dataRequirements/stakeholder-engagement-shapes.ttl` | PDD-C stakeholder engagement shapes. | Turtle |
| 16 | `dataRequirements/review-shapes.ttl` | Generic and specialized document review shapes. | Turtle |
| 17 | `dataRequirements/pdd-certificate-shapes.ttl` | PDD certificate issuance request shapes. | Turtle |
| 18 | `dataRequirements/project-listing-shapes.ttl` | Project listing application shapes. | Turtle |
| 19 | `dataRequirements/license-shapes.ttl` | License application and license review shapes. | Turtle |
| 20 | `dataRequirements/monitoring-report-shapes.ttl` | Monitoring report shapes. | Turtle |
| 21 | `dataRequirements/certificate-shapes.ttl` | Verified impact certificate and issuance request shapes. | Turtle |
| 22 | `dataRequirements/data-lineage-shapes.ttl` | Data lineage report shapes. | Turtle |
| 23 | `dataRequirements/fluree/policy-requirements.md` | Policy requirements for later policy transactions. | Documentation |
| 24 | `dataRequirements/fluree/pdd-workflow-transactions.md` | PDD workflow transaction templates for the application shell. | Documentation |
| 25 | `dataRequirements/fluree/artifact-lookup-queries.md` | Lookup query templates for dropdowns and workflow gates. | Documentation |

## Load Rules

- Validate every Turtle source with `riot --validate` before deployment.
- Load ontology and concept schemes before shapes that reference them.
- Load `common-shapes.ttl`, document references, and document shapes before
  workflow-specific shapes.
- Keep transaction batches traceable to the source file and position above.
- Do not load generated shape2flutter artifacts into the ledger as standard
  artifacts unless a later deployment task explicitly adds UI metadata.
- Do not store credentials, hosted ledger names, or private endpoints here.
