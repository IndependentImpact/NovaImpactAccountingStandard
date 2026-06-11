---
profile: nias-verification-report-rendering-profile
profileVersion: 0.1.0
standard: Nova Impact Accounting Standard
documentType: Verification Report
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
  - verification-report.metadata.jsonld
  - verification-report.validation.json
---

# Nova Impact Accounting Standard

## Verification Report

Verification scope note: guiding questions in scope are GQ-003, GQ-004,
GQ-006, and GQ-008. VVS requirements in scope are REQ-DLR-001,
REQ-DLR-002, REQ-MR-001, REQ-MR-002, REQ-CROSS-001, REQ-PDD-003
(verification facet), REQ-PDD-004 (verification facet), and REQ-PDD-005
(verification facet).

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

## Section 1. Global Monitoring Report Evaluation

{{ render: review.decisionRegister }}

### 1.1 Document-Level Monitoring Report Qualitative Evaluation

{{ render: review.documentQualitativeEvaluation }}

## Section 2. Monitoring Report Section-Level Evaluation (Guiding Questions)

{{ render: review.sectionQualitativeEvaluation }}

## Section 3. Monitoring Report Paragraph-Level Verification Findings

{{ render: review.fieldFindings }}

## Section 4. Verification VVS Requirement Coverage

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
| Review package summary | `VerifiedImpactCertificateIssuanceRequestReviewUiShape` | Title page | `{{ render: titlePage.packageSummary }}` |
| Global decision register | `VerifiedImpactCertificateIssuanceRequestReviewUiShape` | Section 1. Global Monitoring Report Evaluation | `{{ render: review.decisionRegister }}` |
| Document-level qualitative evaluation | `VerifiedImpactCertificateIssuanceRequestReviewUiShape` | Section 1.1 Document-Level Monitoring Report Qualitative Evaluation | `{{ render: review.documentQualitativeEvaluation }}` |
| Section-level qualitative evaluation | `VerifiedImpactCertificateIssuanceRequestReviewUiShape` | Section 2. Monitoring Report Section-Level Evaluation (Guiding Questions) | `{{ render: review.sectionQualitativeEvaluation }}` |
| Paragraph-level findings | `ReviewTargetUiShape` | Section 3. Monitoring Report Paragraph-Level Verification Findings | `{{ render: review.fieldFindings }}` |
| Verification VVS requirements | `ValidationVerificationStandard.ttl` (`nias-o:reviewMandate nias-cs:verification`) | Section 4. Verification VVS Requirement Coverage | `{{ render: vvs.requirementCoverage }}` |
| Review document envelope | `DocumentShape` | Appendix A. Review Document And Workflow Evidence | `{{ render: review.documentEnvelope }}` |
| Workflow evidence | `WorkflowDocumentSubmissionShape` / `HederaTopicMessageShape` | Appendix A. Review Document And Workflow Evidence | `{{ render: workflow.consensusEvidence }}` |
