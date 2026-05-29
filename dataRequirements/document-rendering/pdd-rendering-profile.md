---
profile: nias-pdd-rendering-profile
profileVersion: 0.1.0
standard: Nova Impact Accounting Standard
documentType: Project Design Document
formatVersion: 0.1.0
canonicalDataAuthority: SHACL
primaryInput: JSON-LD
internalModel: expanded-jsonld-or-rdf
pdfCompiler: pandoc
toc: true
toc-depth: 3
toc-title: "Table of Contents"
draftModeAllowsPlaceholders: true
finalModeRequiresValidation: true
repeatedParameterMode: table-per-parameter
defaultOutputTargets:
  - markdown
  - pdf
  - html
sidecarOutputs:
  - pdd.metadata.jsonld
  - pdd.validation.json
---

# Nova Impact Accounting Standard

## Project Design Document

{{ render: titlePage.projectTitle }}

{{ render: titlePage.keyProjectInformation }}

\thispagestyle{pddtitle}

\newpage

\pagenumbering{roman}
\setcounter{page}{1}

## Table Of Contents

\tableofcontents

\newpage

\pagenumbering{arabic}
\setcounter{page}{1}

## Section A. Description Of Project

{{ render: pdd.sectionA }}

### A.1 Purpose And General Description

{{ render: pdd.sectionA.projectPurpose }}

### A.2 Location Of Project

{{ render: pdd.sectionA.locations }}

### A.3 Technologies And Measures

{{ render: pdd.sectionA.technologiesAndMeasures }}

### A.4 Project Parties

{{ render: pdd.sectionA.projectParties }}

### A.5 Legal Matters, Funding, History, And Eligibility

{{ render: pdd.sectionA.legalFundingHistoryEligibility }}

## Section B. Impact Claims And Monitoring

{{ render: pdd.sectionB }}

### B.1 Methodology References

{{ render: pdd.sectionB.methodologyReferences }}

### B.2 Declared Impacts

{{ render: pdd.sectionB.declaredImpacts }}

### B.3 Impact Claims

{{ render: pdd.sectionB.impactClaims }}

### B.4 Crediting And Monitoring Periods

{{ render: pdd.sectionB.creditingAndMonitoringPeriods }}

### B.5 Data And Parameter Requirements

{{ render: pdd.sectionB.dataParameterTables }}

Each data or monitoring parameter renders as one table under this subsection.

### B.6 Ex Ante Estimates

{{ render: pdd.sectionB.exAnteEstimates }}

## Section C. Stakeholder Engagement

{{ render: pdd.sectionC }}

### C.1 Stakeholder Engagement Modalities

{{ render: pdd.sectionC.stakeholderEngagementModalities }}

### C.2 Stakeholder Comment Summary

{{ render: pdd.sectionC.stakeholderCommentSummary }}

### C.3 Stakeholder Comment Consideration

{{ render: pdd.sectionC.stakeholderCommentConsideration }}

\newpage

## Appendix A. Document And Process Metadata

{{ render: metadataAppendix }}

### A.1 Validation Review Summary

{{ render: pdd.validation.sectionA }}

{{ render: pdd.validation.sectionB }}

{{ render: pdd.validation.sectionC }}

### A.2 PDD Certificate Issuance Request

{{ render: pdd.certificateIssuanceRequest }}

\newpage

## Appendix B. Field-To-Predicate Map

{{ render: predicateMapAppendix }}

\newpage

## Appendix C. Source Graph And Hash Evidence

{{ render: sourceEvidenceAppendix }}

## Workflow Section Rendering Map

| Workflow section | Source shape | Publication location | Render directive |
| --- | --- | --- | --- |
| PDD Section A | `PddSectionAUiShape` / `PddSectionAReportShape` | Section A. Description Of Project | `{{ render: pdd.sectionA }}` |
| PDD Section B | `PddSectionBUiShape` / `PddSectionBReportShape` | Section B. Impact Claims And Monitoring | `{{ render: pdd.sectionB }}` |
| PDD Section C | `PddSectionCUiShape` / `PddSectionCShape` | Section C. Stakeholder Engagement | `{{ render: pdd.sectionC }}` |
| PDD Section A validation review | `PddSectionAValidationReviewUiShape` / `GenericDocumentReviewShape` | Appendix A.1 Validation Review Summary | `{{ render: pdd.validation.sectionA }}` |
| PDD Section B validation review | `PddSectionBValidationReviewUiShape` / `GenericDocumentReviewShape` | Appendix A.1 Validation Review Summary | `{{ render: pdd.validation.sectionB }}` |
| PDD Section C validation review | `PddSectionCValidationReviewUiShape` / `GenericDocumentReviewShape` | Appendix A.1 Validation Review Summary | `{{ render: pdd.validation.sectionC }}` |
| PDD-CIR | `PddCertificateIssuanceRequestUiShape` / `PddCertificateIssuanceRequestShape` | Appendix A.2 PDD Certificate Issuance Request | `{{ render: pdd.certificateIssuanceRequest }}` |

## Top-Level Content Shape Heading Map

| Content shape | Canonical source | Publication heading |
| --- | --- | --- |
| `PddSectionAReportContentUiShape` | `PddSectionAReportShape` | Section A. Description Of Project |
| `ProjectDesignUiShape` | `ProjectDesignShape` | Section A.1 through Section A.5 |
| `ObjectiveUiShape` | `ObjectiveShape` | Section A.1 Purpose And General Description |
| `SpatialLocationUiShape` | `SpatialLocationResourceShape` | Section A.2 Location Of Project |
| `TechnologyOrMeasureUiShape` | `TechnologyOrMeasureShape` | Section A.3 Technologies And Measures |
| `ProjectPartyUiShape` | `ProjectPartyShape` | Section A.4 Project Parties |
| `PddSectionBReportContentUiShape` | `PddSectionBReportShape` | Section B. Impact Claims And Monitoring |
| `ImpactRequirementUiShape` | `ImpactRequirementShape` | Section B.2 Declared Impacts |
| `ImpactClaimUiShape` | `ImpactClaimShape` | Section B.3 Impact Claims |
| `CreditingPeriodUiShape` | `CreditingPeriodShape` | Section B.4 Crediting And Monitoring Periods |
| `DateTimeIntervalUiShape` | `DateTimeIntervalShape` | Section B.4 Crediting And Monitoring Periods |
| `DataParameterRequirementUiShape` | `DataParameterRequirementShape` | Section B.5 Data And Parameter Requirements |
| `PddSectionCUiShape` | `PddSectionCShape` | Section C. Stakeholder Engagement |
| `DocumentFieldReviewUiShape` | `DocumentFieldReviewShape` | Appendix A.1 Validation Review Summary |
| `DocumentReferenceUiShape` | `DocumentReferenceShape` | Appendix A.2 PDD Certificate Issuance Request and Appendix A |

## Main Body And Metadata Boundary

The main PDD body, from Section A through Section C, renders substantive project
design content only. Document wrapper and workflow/process metadata such as
document IPFS URI, document schema IRI, encryption status, document author,
authenticity proof, workflow submission evidence, validation review evidence,
and PDD certificate issuance request evidence render in Appendix A or sidecar
metadata files, not inside the PDD content sections. The PDF footer should carry
only a short document ID, hash, or version reference.

## Default Field Rendering Rules

| Value kind | Rendering behavior |
| --- | --- |
| Scalar text | Paragraph or table cell under the mapped heading |
| Long text | Paragraph block preserving line breaks |
| IRI with known label | Human label with IRI retained in metadata appendix |
| IRI without known label | Compact IRI or full IRI, depending on available prefix mapping |
| Boolean | Yes/No text |
| Controlled vocabulary value | Preferred label from concept scheme |
| Date or timestamp | ISO date/time unless a display format is configured later |
| Document reference | Message ID plus IPFS URI where available |
| Single nested object | Subsection or table according to heading map |
| Repeated nested object | Repeated subsection unless a table-specific rule exists |
| Data or monitoring parameter | One table per parameter under Section B.5 |
| Missing optional value in draft mode | Empty placeholder |
| Missing required value in draft mode | Visible placeholder and warning marker |
| Missing required value in final mode | Export failure before rendering |

## Footer Rule

PDF output should include a short footer value composed from available document
metadata:

```text
NIAS PDD | {{ project.displayId }} | {{ document.version }} | {{ source.hash }}
```

If a value is unavailable in draft mode, the footer must use a visible draft
placeholder.

## Sidecar Output Rules

Final exports should produce:

- `pdd.md`
- `pdd.pdf`
- `pdd.html`
- `pdd.metadata.jsonld`
- `pdd.validation.json`

The Markdown/PDF/HTML outputs are human-readable projections. The sidecar files
carry machine-readable provenance, validation, source graph, hash, and
field-to-predicate metadata.
