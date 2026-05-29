---
profile: nias-validation-verification-report-rendering-profile
profileVersion: 0.1.0
standard: Nova Impact Accounting Standard
documentType: Validation or Verification Report
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
defaultOutputTargets:
  - markdown
  - pdf
  - html
sidecarOutputs:
  - validation-report.metadata.jsonld
  - validation-report.validation.json
  - verification-report.metadata.jsonld
  - verification-report.validation.json
---

# Nova Impact Accounting Standard

## Validation Report Or Verification Report

{{ render: titlePage.reportTitle }}

{{ render: titlePage.packageSummary }}

\thispagestyle{pddtitle}

\newpage

\pagenumbering{roman}
\setcounter{page}{1}

## Table Of Contents

\tableofcontents

\newpage

\pagenumbering{arabic}
\setcounter{page}{1}

## Review Decision Register

{{ render: review.decisionRegister }}

## Field Review Findings

{{ render: review.fieldFindings }}

## VVS Requirement Coverage Summary

{{ render: vvs.requirementCoverage }}

\newpage

## Appendix A. Review Document And Workflow Evidence

{{ render: review.documentEnvelope }}

{{ render: workflow.consensusEvidence }}

\newpage

## Appendix B. Source Graph And Hash Evidence

{{ render: sourceEvidenceAppendix }}

\newpage

## Appendix C. Field-To-Predicate Map

{{ render: predicateMapAppendix }}

## Rendering Map

| Report section | Source shape | Publication location | Render directive |
| --- | --- | --- | --- |
| Review package summary | `GenericDocumentReviewShape` / `VerifiedImpactCertificateIssuanceRequestReviewShape` | Title page | `{{ render: titlePage.packageSummary }}` |
| Review decisions | `GenericDocumentReviewShape` / `VerifiedImpactCertificateIssuanceRequestReviewShape` | Review Decision Register | `{{ render: review.decisionRegister }}` |
| Field findings | `DocumentFieldReviewShape` | Field Review Findings | `{{ render: review.fieldFindings }}` |
| VVS requirements | `vvs-requirement-shapes.ttl` / `ValidationVerificationStandard.ttl` | VVS Requirement Coverage Summary | `{{ render: vvs.requirementCoverage }}` |
| Review document envelope | `DocumentShape` | Appendix A. Review Document And Workflow Evidence | `{{ render: review.documentEnvelope }}` |
| Workflow evidence | `WorkflowDocumentSubmissionShape` / `HederaTopicMessageShape` | Appendix A. Review Document And Workflow Evidence | `{{ render: workflow.consensusEvidence }}` |

## Rendering Boundary

The Validation Report and Verification Report are separate publication
projections over existing review documents and requirement metadata. They do not
introduce a new canonical report class. Reviewed PDD, Data Lineage Report,
Monitoring Report, VIC-IR, or VIC artifacts may be supplied as evidence graphs
for final SHACL validation, but their substantive source content is not rendered
in the main report body. Document-envelope and workflow-submission metadata
render in appendices or sidecars, not as report content.

## Default Field Rendering Rules

| Value kind | Rendering behavior |
| --- | --- |
| Review document | One row in the decision register |
| Review document envelope | Appendix-only provenance row with schema, author, IPFS URI, encryption, and proof metadata |
| Field review | One row in the findings register |
| Review decision concept | Human label when available, otherwise compact IRI |
| Workflow submission | Appendix-only workflow evidence row with subject, parties, and consensus message |
| VVS requirement | One row per active requirement with shape, anchor, and evidence status |
| Missing optional value in draft mode | Empty placeholder |
| Missing required value in draft mode | Visible placeholder |
| Missing required value in final mode | Export failure before rendering |

## Sidecar Output Rules

Final validation exports should produce:

- `validation-report.md`
- `validation-report.pdf`
- `validation-report.html`
- `validation-report.metadata.jsonld`
- `validation-report.validation.json`

Final verification exports should produce:

- `verification-report.md`
- `verification-report.pdf`
- `verification-report.html`
- `verification-report.metadata.jsonld`
- `verification-report.validation.json`

The Markdown/PDF/HTML outputs are human-readable projections. The sidecar files
carry machine-readable provenance, validation, source graph, hash, and artifact
metadata.
