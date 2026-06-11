---
profile: nias-validation-report-rendering-profile
profileVersion: 0.1.0
standard: Nova Impact Accounting Standard
documentType: Validation Report
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
---

# Nova Impact Accounting Standard

## Validation Report

Validation scope note: guiding questions in scope are GQ-001, GQ-002, GQ-005,
and GQ-007. VVS requirements in scope are REQ-PDD-001, REQ-PDD-002,
REQ-PDD-003 (validation facet), REQ-PDD-004 (validation facet), and
REQ-PDD-005 (validation facet).

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

## Section 1. Global PDD Evaluation

{{ render: review.decisionRegister }}

### 1.1 Document-Level PDD Qualitative Evaluation

{{ render: review.documentQualitativeEvaluation }}

## Section 2. PDD Section-Level Evaluation (Guiding Questions)

{{ render: review.sectionQualitativeEvaluation }}

## Section 3. PDD Paragraph-Level Validation Findings

{{ render: review.fieldFindings }}

## Section 4. Validation VVS Requirement Coverage

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
| Review package summary | `GlobalQualitativeDocumentReviewUiShape` | Title page | `{{ render: titlePage.packageSummary }}` |
| Global decision register | `GlobalQualitativeDocumentReviewUiShape` | Section 1. Global PDD Evaluation | `{{ render: review.decisionRegister }}` |
| Document-level qualitative evaluation | `GlobalQualitativeDocumentReviewUiShape` | Section 1.1 Document-Level PDD Qualitative Evaluation | `{{ render: review.documentQualitativeEvaluation }}` |
| Section-level qualitative evaluation | `GlobalQualitativeDocumentReviewUiShape` | Section 2. PDD Section-Level Evaluation (Guiding Questions) | `{{ render: review.sectionQualitativeEvaluation }}` |
| Paragraph-level findings | `DocumentFieldReviewUiShape` | Section 3. PDD Paragraph-Level Validation Findings | `{{ render: review.fieldFindings }}` |
| Validation VVS requirements | `ValidationVerificationStandard.ttl` (`nias-o:reviewMandate nias-cs:validation`) | Section 4. Validation VVS Requirement Coverage | `{{ render: vvs.requirementCoverage }}` |
| Review document envelope | `DocumentShape` | Appendix A. Review Document And Workflow Evidence | `{{ render: review.documentEnvelope }}` |
| Workflow evidence | `WorkflowDocumentSubmissionShape` / `HederaTopicMessageShape` | Appendix A. Review Document And Workflow Evidence | `{{ render: workflow.consensusEvidence }}` |
