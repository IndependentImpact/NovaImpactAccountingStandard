# PDD Markdown Export Phase 1 Assessment

Status: completed on 2026-05-25.

## Scope Decision

The PDD Markdown export is a document-rendering projection of the NIAS semantic
standard.

It is not:

- a SHACL extension;
- a second PDD data model;
- a Flutter-only feature;
- a Fluree/IPFS/Hedera deployment feature.

It consumes:

- canonical SHACL shapes;
- a Markdown rendering profile with YAML front matter;
- filled-in JSON-LD payloads from the PDD workflow shell.

It produces:

- a blank Markdown PDD template from SHACL plus the rendering profile;
- a filled Markdown PDD from SHACL, the rendering profile, and validated data;
- later PDF, HTML, website, and sidecar metadata outputs.

The correct home for this work is `dataRequirements/document-rendering/`.

## Canonical Source Shape Inventory

The source shapes for PDD rendering are split across the existing SHACL files.
There is no standalone `dataRequirements/pdd-shapes.ttl` file.

| PDD concern | Canonical source | Primary shapes |
| --- | --- | --- |
| Document schemas and schema IRIs | `dataRequirements/document-shapes.ttl` | `document-schema/PDDxA-1.0.0`, `document-schema/PDDxB-9.0.0`, `document-schema/PDDxC-4.0.0`, `document-schema/PDDCIR-3.0.0`, `document-schema/GenericDocumentReview-5.0.0` |
| Document artifact and workflow submission metadata | `dataRequirements/document-shapes.ttl` | `DocumentShape`, `WorkflowDocumentSubmissionShape`, Hedera consensus-message constraints |
| Document-to-report content link | `dataRequirements/report-shapes.ttl` | `DocumentReportLinkShape`, `ProjectDesignDocumentShape` |
| PDD-A project design content | `dataRequirements/report-shapes.ttl`, `dataRequirements/project-design-shapes.ttl`, `dataRequirements/common-shapes.ttl` | `PddSectionAReportShape`, `ProjectDesignShape`, `ObjectiveShape`, `ProjectPartyShape`, `SpatialLocationResourceShape`, `TechnologyOrMeasureShape` |
| PDD-B impact declaration and monitoring content | `dataRequirements/report-shapes.ttl`, `dataRequirements/impact-declaration-shapes.ttl`, `dataRequirements/common-shapes.ttl` | `PddSectionBReportShape`, `ImpactRequirementShape`, `ImpactClaimShape`, `StateWithIndicatorValueShape`, `DataParameterRequirementShape`, `CreditingPeriodShape`, `DateTimeIntervalShape` |
| PDD-C stakeholder engagement content | `dataRequirements/stakeholder-engagement-shapes.ttl`, `dataRequirements/report-shapes.ttl` | `PddSectionCShape`, `PddSectionCReportShape` |
| PDD section validation reviews | `dataRequirements/review-shapes.ttl`, `dataRequirements/document-shapes.ttl` | `GenericDocumentReviewShape`, `DocumentFieldReviewShape`, `DocumentReviewShape`, `document-schema/GenericDocumentReview-5.0.0` |
| PDD-CIR references to approved reviews | `dataRequirements/pdd-certificate-shapes.ttl`, `dataRequirements/document-reference-shapes.ttl` | `PddCertificateIssuanceRequestShape`, `DocumentReferenceShape` |
| PDD workflow gate evidence | `dataRequirements/tests/test_pdd_workflow_gate.py`, `dataRequirements/fixtures/pdd-workflow/*.ttl` | approved PDD-A/B/C review references, reviewed-document schema checks, workflow subject checks |
| UI labels, order, and first-pass subform projection | `dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl` | `PddSectionAUiShape`, `PddSectionBUiShape`, `PddSectionCUiShape`, review UI shapes, `PddCertificateIssuanceRequestUiShape` |

The UI adapter shapes are rendering inputs, not canonical validation authority.
They are useful because they already encode labels, order, and simplified
subform structures for `shape2flutter`.

## Reference PDD Documents

Tracked reference templates in `reference/` provide conventional PDD structure
and publication expectations:

- `reference/T-PreReview_V1.5-Project-Design-Document.docx`
- `reference/T-PAA_PreReview_V2.0_Project-Design-Document.docx`
- `reference/TGuide-PAA_PreReview_V2.0_Project-Design-Document.docx`
- `reference/A6.4-FORM-AC-020.docx`

These reference documents are not canonical NIAS data requirements. They inform
the rendering profile, especially title-page layout, section ordering, repeated
parameter tables, appendices, and human-readable body text.

## Rendering Boundary

The renderer may:

- choose heading text and heading levels;
- group canonical fields into conventional PDD sections;
- add standard boilerplate and format/version text;
- render repeated parameter structures as one table per parameter;
- include title-page and key-project-information tables;
- add a metadata appendix;
- add a footer with an ID, version, or hash;
- emit machine-readable sidecar files.

The renderer may not:

- add new validation constraints;
- require fields that are not required by SHACL in final validation mode;
- hide missing required values in draft mode;
- change canonical predicate paths;
- introduce project-specific values.

Where human document presentation needs values that are not canonical data
requirements, the rendering profile must either:

- derive them from existing canonical data;
- put them in rendering metadata/front matter;
- mark them optional for the first profile;
- or record a future SHACL gap for later standards work.

## Human PDD Fields Already Covered

The current SHACL set already covers many fields needed for a conventional PDD:

- project title: `nias-o:title`;
- project purpose/objective: `aiao:hasObjective / schema:description`;
- project locations: `impactont:hasSpatialLocation`;
- technologies and measures: `nias-o:technologyOrMeasure`;
- project parties: `nias-o:projectParty`;
- legal matters: `nias-o:legalMatters`;
- public funding status and source: `nias-o:publicFundingStatus`,
  `nias-o:publicFundingSource`;
- project history: `nias-o:projectHistory`;
- debundling assessment: `nias-o:debundlingAssessment`;
- project eligibility text: `nias-o:eligibilityDescription`;
- methodology references: `nias-o:usesMethodology`;
- declared impacts: `nias-o:hasDeclaredImpact`;
- impact claims: `nias-o:impactClaim`;
- monitoring periods and crediting period: `nias-o:monitoringPeriod`,
  `nias-o:creditingPeriod`;
- data and parameter requirements: `nias-o:dataParameterRequirement`;
- stakeholder engagement modalities and comments:
  `nias-o:stakeholderEngagementModalities`,
  `nias-o:stakeholderCommentSummary`,
  `nias-o:stakeholderCommentConsideration`;
- document schema/version IRIs: `nias-o:documentSchema`,
  `dcterms:conformsTo`;
- workflow submission and Hedera message evidence:
  `nias-o:hasWorkflowSubmission`,
  `nias-o:workflowSubmissionConsensusMessage`;
- document artifact references: `nias-o:resourceIpfsUri`;
- validation review decisions and field-level reviewer notes:
  `nias-o:finalReviewDecision`, `nias-o:fieldReview`.

## Human PDD Fields Not Yet Explicit As Canonical Data

The reference PDD templates include several title-page or key-project-information
items that are not yet first-class canonical PDD fields, or are only indirectly
available.

These should not be added in Phase 1. They should be handled in the Phase 2
rendering profile as optional title-page fields, derived fields, or future
standards gaps.

| Human document item | Current status | Phase 1 decision |
| --- | --- | --- |
| Display project ID | Project IRI exists, but no separate human display identifier is required. | Derive from project IRI in first profile; consider future display ID field if needed. |
| PDD document version number | Document schema version exists, but project-specific PDD version is not explicit. | Use rendering/front-matter metadata initially; consider future canonical version field. |
| Completion or publication date | Workflow consensus timestamp exists, but title-page completion date is not explicit. | Derive from workflow submission timestamp or rendering metadata. |
| Project representative | Document author/reporting agent exists, but representative role is not explicit. | Treat as optional front-matter/title-page metadata initially. |
| Host country or countries | Spatial location resource exists, but host-country text is not explicit. | Derive only if available from location metadata; otherwise optional title-page metadata. |
| Activity requirements applied | Not explicit in current PDD-A/B/C shapes. | Optional rendering-profile field for now; future standards gap if required. |
| Product requirements or impact product type | Impact and methodology references exist, but product-requirement labels are not explicit. | Resolve from method/impact metadata where possible; otherwise optional. |
| Project cycle or status | Workflow step/status exists, but conventional PDD cycle label is not explicit. | Use workflow state or front-matter metadata. |
| Project scale | Not explicit in current PDD-A/B/C shapes. | Optional title-page metadata; future standards gap if required. |
| Contact details for project parties | Project parties exist, but contact fields are not required. | Keep out of first profile unless already present in source data. |
| Safeguarding and gender assessment sections | Present in some conventional templates, not part of current NIAS PDD-A/B/C source shapes. | Out of scope for first NIAS PDD profile unless SHACL coverage is added later. |

## Phase 1 Conclusion

Phase 1 confirms that NIAS has enough canonical SHACL structure to start a
Markdown rendering profile for the local PDD-A/B/C workflow, provided the first
profile is scoped to the PDD content currently modeled by NIAS.

The next phase should not add new canonical fields. It should define
`pdd-rendering-profile.md` as a Markdown-with-YAML rendering profile that:

- maps the existing source shapes into a conventional PDD outline;
- treats title-page gaps as optional rendering metadata or derived values;
- keeps platform references and hashes in the footer, metadata appendix, and
  sidecar files;
- preserves SHACL as the validation authority.
