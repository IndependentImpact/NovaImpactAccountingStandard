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

#### Field reviews
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

## Review Decision Register

| Review document | Review type | Final decision | Field reviews |
| --- | --- | --- | ---: |
| vv-verification-review-1 | Verification review | Approve | 1 |


## Field Review Findings

| Review document | Field | Decision | Feedback | Original response |
| --- | --- | --- | --- | --- |
| vv-verification-review-1 | Monitoring report impact summary | Approve | The verified impact summary is consistent with the monitoring report review. | 87.5 tCO2e avoided during the monitoring period. |


## VVS Requirement Coverage Summary

| Requirement | Mandate | Anchor | Shape | Evidence status |
| --- | --- | --- | --- | --- |
| REQ-CROSS-001 | verification | MonitoringReport | ReqCross001Shape | draft evidence present (1) |
| REQ-DLR-001 | verification | DataLineageReport | ReqDlr001Shape | draft evidence present (1) |
| REQ-DLR-002 | verification | DataLineageReport | ReqDlr002Shape | draft evidence present (1) |
| REQ-MR-001 | verification | MonitoringReport | ReqMr001Shape | draft evidence present (1) |
| REQ-MR-002 | verification | MonitoringReport | ReqMr002Shape | draft evidence present (1) |


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
8af13c57b79c6863cb421ac7a76b65fb49b8238d84619e67136d8e85bb1d3dfd

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

### Field review
nias-o:fieldReview

### Field key
nias-o:fieldKey

### Field title
nias-o:fieldTitle

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
