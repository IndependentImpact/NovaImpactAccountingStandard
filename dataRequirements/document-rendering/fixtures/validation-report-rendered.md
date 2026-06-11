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
renderedDocumentType: Validation Report
renderMode: draft
reportType: validation
rendererVersion: 0.1.0
sourceArtifact: validation-report-input.jsonld
generatedAt: 2026-05-28T00:00:00Z
---

# Nova Impact Accounting Standard

## Validation Report

Validation scope note: guiding questions in scope are GQ-001, GQ-002, GQ-005,
and GQ-007. VVS requirements in scope are REQ-PDD-001, REQ-PDD-002,
REQ-PDD-003 (validation facet), REQ-PDD-004 (validation facet), and
REQ-PDD-005 (validation facet).

### Validation Review Package


#### Report type
Validation Report

#### Review documents
1

#### Anchor reviews
1

#### Final decisions
Approve: 1

#### VVS evidence targets
3

#### Generated at
2026-05-28T00:00:00Z

#### Rendering mode
draft

#### Source artifact
validation-report-input.jsonld


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

| Review document | Review type | Final decision | Anchor reviews |
| --- | --- | --- | ---: |
| vv-validation-review-1 | Validation review | Approve | 1 |


### 1.1 Document-Level PDD Qualitative Evaluation

| Review document | Review type | Document-level qualitative judgement |
| --- | --- | --- |
| vv-validation-review-1 | Validation review | Unavailable |


## Section 2. PDD Section-Level Evaluation (Guiding Questions)

| Review document | Review type | Section-level qualitative judgement |
| --- | --- | --- |
| vv-validation-review-1 | Validation review | Unavailable |


## Section 3. PDD Paragraph-Level Validation Findings

| Review document | Reviewed artifact | Reviewed anchor | Decision | Feedback | Reviewed content |
| --- | --- | --- | --- | --- | --- |
| vv-validation-review-1 | pdd-b-report | pdd.sectionB.declaredImpacts | Approve | The impact declaration is complete for validation. | One beneficial GHG impact is declared with a quantification methodology. |


## Section 4. Validation VVS Requirement Coverage

| Requirement | Mandate | Anchor | Shape | Evidence status |
| --- | --- | --- | --- | --- |
| REQ-PDD-001 | validation | pdd.sectionA - Section A. Description Of Project; pdd.sectionA.technologiesAndMeasures - A.3 Technologies And Measures | ReqPdd001Shape | draft evidence present (1) |
| REQ-PDD-002 | validation | pdd.sectionB.methodologyReferences - B.1 Methodology References; pdd.sectionB.declaredImpacts - B.2 Declared Impacts | ReqPdd002Shape | draft evidence present (1) |
| REQ-PDD-003 | validation | pdd.sectionC - Section C. Stakeholder Engagement | ReqPdd003Shape | draft evidence present (1) |
| REQ-PDD-004 | validation | pdd.sectionReview.qualitativeCompletion - Section C. Stakeholder Engagement | ReqPdd004Shape | not assessed in draft mode |
| REQ-PDD-005 | validation | pdd.documentLevel.qualitativeCompletion - Section B. Impact Claims And Monitoring | ReqPdd005Shape | not assessed in draft mode |


\newpage

## Appendix A. Review Document And Workflow Evidence

| Review document | Schema | Author | IPFS URI | Encrypted | Auth proof |
| --- | --- | --- | --- | --- | --- |
| vv-validation-review-1 | GenericDocumentReview-5.0.0 | validator-1 | ipfs://bafyvvvalidationreview | No | None |


| Review document | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| vv-validation-review-1 | vv-validation-review-1 | Validate PDD impact declaration | project-1 | validator-1 | registry-1 | topic-1 | 21 | 2026-05-27T10:00:00Z |


\newpage

## Appendix B. Source Graph And Hash Evidence

### Source artifact
validation-report-input.jsonld

### Input JSON-LD
validation-report-input.jsonld

### Input SHA-256
f64c3d766c74455566910b12e1da2cada48e799650dc1a618a85483c6b48e7bc

### Evidence JSON-LD 1
validation-report-evidence.jsonld

### Evidence SHA-256 1
6dd85600f61fa7333121798dbd7225f25faf92940fdacc74bdfd0c0bdeecd8bf


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
