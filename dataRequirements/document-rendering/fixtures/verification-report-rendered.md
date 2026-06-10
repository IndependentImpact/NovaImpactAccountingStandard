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
renderedDocumentType: Verification Report
renderMode: draft
reportType: verification
rendererVersion: 0.1.0
sourceArtifact: validation-verification-report-input.jsonld
generatedAt: 2026-05-28T00:00:00Z
---

# Nova Impact Accounting Standard

## Verification Report

### Verification Review Package


#### Report type
Verification Report

#### Review documents
1

#### Anchor reviews
1

#### Final decisions
Approve: 1

#### VVS evidence targets
5

#### Generated at
2026-05-28T00:00:00Z

#### Rendering mode
draft

#### Source artifact
validation-verification-report-input.jsonld


\thispagestyle{pddtitle}

\newpage

\pagenumbering{roman}
\setcounter{page}{1}

## Table Of Contents

\tableofcontents

\newpage

\pagenumbering{arabic}
\setcounter{page}{1}

## Section 1. Global Evaluation

| Review document | Review type | Final decision | Anchor reviews |
| --- | --- | --- | ---: |
| vv-verification-review-1 | Verification review | Approve | 1 |


### 1.1 Document-Level Qualitative Evaluation

| Review document | Review type | Document-level qualitative judgement |
| --- | --- | --- |
| vv-verification-review-1 | Verification review | Unavailable |


## Section 2. Section-Level Evaluation (Guiding Questions)

| Review document | Review type | Section-level qualitative judgement |
| --- | --- | --- |
| vv-verification-review-1 | Verification review | Unavailable |


## Section 3. Paragraph-Level Validation Findings

| Review document | Reviewed artifact | Reviewed anchor | Decision | Feedback | Reviewed content |
| --- | --- | --- | --- | --- | --- |
| vv-verification-review-1 | monitoring-report | monitoring.observation | Approve | The verified impact summary is consistent with the monitoring report review. | 87.5 tCO2e avoided during the monitoring period. |


## Section 4. VVS Requirement Coverage Summary

| Requirement | Mandate | Anchor | Shape | Evidence status |
| --- | --- | --- | --- | --- |
| REQ-CROSS-001 | verification | pdd.sectionB.declaredImpacts - B.2 Declared Impacts; monitoring.packageSummary - Monitoring Report; monitoring.observation - Measured Impact Observation | ReqCross001Shape | draft evidence present (1) |
| REQ-DLR-001 | verification | pdd.sectionB.dataParameterTables - B.5 Data And Parameter Requirements; dlr.rawDataset - Raw Dataset Artifact; dlr.dataTransferCode - Data Transfer Code Artifact | ReqDlr001Shape | draft evidence present (1) |
| REQ-DLR-002 | verification | pdd.sectionB.dataParameterTables - B.5 Data And Parameter Requirements; dlr.finalDataset - Final Dataset Artifact | ReqDlr002Shape | draft evidence present (1) |
| REQ-MR-001 | verification | pdd.sectionB.declaredImpacts - B.2 Declared Impacts; monitoring.observation - Measured Impact Observation | ReqMr001Shape | draft evidence present (1) |
| REQ-MR-002 | verification | monitoring.resources - Calculation Resources | ReqMr002Shape | draft evidence present (1) |
| REQ-PDD-004 | validation | monitoring.sectionReviewEvidence - Monitoring Report | ReqPdd004Shape | not assessed in draft mode |
| REQ-PDD-005 | validation | monitoring.documentLevelReviewEvidence - Calculation Resources | ReqPdd005Shape | not assessed in draft mode |


\newpage

## Appendix A. Review Document And Workflow Evidence

| Review document | Schema | Author | IPFS URI | Encrypted | Auth proof |
| --- | --- | --- | --- | --- | --- |
| vv-verification-review-1 | DRVICIR-1.0.0 | verifier-1 | ipfs://bafyvvverificationreview | No | None |


| Review document | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| vv-verification-review-1 | vv-verification-review-1 | Verify monitoring report and VIC issuance request | project-1 | verifier-1 | registry-1 | topic-1 | 22 | 2026-05-27T11:00:00Z |


\newpage

## Appendix B. Source Graph And Hash Evidence

### Source artifact
validation-verification-report-input.jsonld

### Input JSON-LD
validation-verification-report-input.jsonld

### Input SHA-256
fbba3078461bbb06351c98d5768c5dfa6628f9645ef138facb71ce6e33bed4ab

### Evidence JSON-LD 1
validation-verification-report-evidence.jsonld

### Evidence SHA-256 1
880acc33f8caa29240d2d34c4bce0891480bcdbe852f14818ce6d7ed8c74d659


\newpage

## Appendix C. Field-To-Predicate Map

### Review document type
rdf:type

### Document schema
nias-o:documentSchema

### Final review decision
nias-o:finalReviewDecision

### Document-level qualitative judgement
nias-o:documentLevelQualitativeJudgement

### Section-level qualitative judgement
nias-o:sectionQualitativeJudgement

### Anchor review
nias-o:fieldReview

### Review target
nias-o:reviewTarget

### Reviewed artifact
nias-o:reviewedArtifact

### Reviewed anchor
nias-o:reviewedAnchor

### Reviewer decision
nias-o:reviewerDecision

### Reviewer feedback
nias-o:reviewerFeedback

### Document author
nias-o:documentAuthor

### Document IPFS URI
nias-o:resourceIpfsUri

### Authenticity proof
nias-o:authProof

### Workflow submission evidence
nias-o:hasWorkflowSubmission

### Consensus message
nias-o:workflowSubmissionConsensusMessage

### VVS requirement ID
nias-o:requirementId

### VVS implementing shape
nias-o:implementedByShape
