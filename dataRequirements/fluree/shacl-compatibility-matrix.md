# SHACL Compatibility Matrix

This matrix classifies how the canonical NIAS SHACL constraints should be
enforced in a Fluree deployment.

Categories:

- `fluree-enforced` - expected to work directly in Fluree SHACL validation.
- `fluree-rewrite` - semantically valid SHACL, but should be simplified or
  rewritten before relying on Fluree transaction-time enforcement.
- `service-enforced` - must be enforced by the application or service layer.
- `advisory` - retained for documentation, UI generation, or external
  validation.

This assessment is based on current Fluree documentation checked on
2026-05-21. It must be verified against the target hosted ledger before policy
or production deployment.

## Constraint Feature Assessment

| SHACL feature | Status | NIAS usage | Deployment note |
| --- | --- | --- | --- |
| `sh:targetClass` | `fluree-enforced` | All canonical node shapes. | Load shapes before workflow transactions. |
| `sh:property` and direct `sh:path` | `fluree-enforced` | All canonical property constraints. | Direct predicate paths should load as-is. |
| `sh:minCount`, `sh:maxCount` | `fluree-enforced` | Required workflow headers, document references, review decisions, PDD fields. | Core transaction-time validation. |
| `sh:datatype` | `fluree-enforced` | Strings, booleans, integers, decimals, `xsd:anyURI`, `xsd:dateTimeStamp`. | Keep typed JSON-LD literals where ambiguity exists. |
| `sh:class` | `fluree-enforced` | Document references, workflow submissions, platform users, communication parties, documents. | Ensure referenced nodes include matching `@type`. |
| `sh:nodeKind` | `fluree-enforced` | Document schema IRIs, workflow subjects, controlled IRI fields. | Use `@id` objects in JSON-LD transactions. |
| `sh:pattern` | `fluree-enforced` | IPFS/IPNS URI patterns, Hedera account patterns, document schema namespace patterns. | Escape regex strings once when generating JSON-LD. |
| `sh:in` | `fluree-enforced` | Review decisions and controlled vocabularies such as yes/no, monitoring status, party type. | Use canonical concept IRIs, not display labels. |
| `sh:or` | `fluree-enforced` | `DocumentShape` author IRI/string, quantity literal variants, resource content alternatives. | Verify with a minimal deployment test. |
| `sh:hasValue` | `fluree-rewrite` | PDD document schema checks and branch-specific helper shapes. | Rewrite as singleton `sh:in` or service assertion if target ledger does not enforce `sh:hasValue`. |
| `sh:node` | `fluree-rewrite` | Nested helper shapes throughout document, workflow, PDD, MR, and certificate shapes. | Prefer direct verification; if unsupported, flatten critical nested constraints into deployment shapes. |
| `sh:qualifiedMinCount`, `sh:qualifiedValueShape` | `fluree-rewrite` | Monitoring claim evidence and attestation requirements in `report-shapes.ttl`. | Rewrite to explicit properties or enforce in service layer. |
| `sh:sparql` | `service-enforced` | Monitored impact branch rule in `impact-declaration-shapes.ttl`. | Keep pySHACL for canonical validation and mirror rule in the workflow service. |
| Cross-document ledger lookup | `service-enforced` | PDD-CIR approval gate and future certificate issuance gates. | Use query or policy logic, not ordinary document-local SHACL. |
| `ui:` annotations | `advisory` | shape2flutter adapter shapes only. | Do not load as canonical ledger schema unless UI metadata becomes a ledger artifact. |

## PDD Workflow Shape Assessment

| Shape file | Main shapes | Status | Notes |
| --- | --- | --- | --- |
| `common-shapes.ttl` | Time, quantity, state, indicator value, impact helpers. | Mixed: `fluree-enforced` plus `fluree-rewrite`. | Direct datatype/cardinality constraints should enforce; nested `sh:node` and `sh:hasValue` need ledger tests. |
| `document-reference-shapes.ttl` | `DocumentReferenceShape`, `ResourceArtifactShape`. | `fluree-enforced` with `sh:node` verification. | Critical for PDD-CIR references and workflow gates. |
| `document-shapes.ttl` | `DocumentShape`, `WorkflowDocumentSubmissionShape`, Hedera message shapes, document schema resources. | Mixed: mostly `fluree-enforced`. | `sh:or` and nested `sh:node` should be confirmed in a minimal ledger before relying on them. |
| `report-shapes.ttl` | PDD-A/B/C report wrappers and monitoring report wrappers. | Mixed. | PDD wrappers are straightforward except `sh:hasValue`; monitoring wrappers include qualified value constraints. |
| `project-design-shapes.ttl` | PDD-A project design and parties. | Mixed. | Public funding branch uses `sh:hasValue` and `sh:or`; test or rewrite. |
| `impact-declaration-shapes.ttl` | PDD-B impacts, claims, monitored/unmonitored branches. | Mixed. | SPARQL branch rule is service-enforced. |
| `stakeholder-engagement-shapes.ttl` | PDD-C stakeholder engagement. | `fluree-enforced` with `sh:node` verification. | Mostly direct cardinality/datatype constraints. |
| `review-shapes.ttl` | `GenericDocumentReviewShape`, `DocumentFieldReviewShape`. | `fluree-enforced` with `sh:node` verification. | Review decisions use canonical SKOS concept IRIs. |
| `pdd-certificate-shapes.ttl` | `PddCertificateIssuanceRequestShape`. | Mixed. | Local reference fields are SHACL-enforced; approved-review semantics are service-enforced by the gate. |

## Runtime Gate Rules

The PDD-CIR approval gate from
`dataRequirements/shape2flutter/pdd-workflow-gate.md` is classified as
`service-enforced`.

The reason is structural: `nias-o:DocumentReference` values carry a message ID
and resource URI, while approval status lives on the resolved review document.
That requires ledger lookup across artifacts and cannot be validated by
document-local SHACL alone.

The Fluree implementation can still enforce the gate with transaction policy or
service preflight logic. The query templates in `artifact-lookup-queries.md`
define the required lookup shape.
