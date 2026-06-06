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
reportType: verification
---

# Nova Impact Accounting Standard

## Verification Report

### _[Verification Report package title]_


#### Report type
Verification Report

#### Review documents
**[required]** _[to be populated]_

#### Anchor reviews
**[required]** _[to be populated]_

#### Final decisions
**[required]** _[to be populated]_

#### VVS evidence targets
**[required for final]** _[to be populated]_

#### Generated at
**[optional]** _[to be populated]_

#### Rendering mode
**[optional]** _[draft or final]_

#### Source artifact
**[optional]** _[to be populated]_


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

| Review document | Review type | Final decision | Anchor reviews |
| --- | --- | --- | ---: |
| **[required]** _[review document]_ | _[validation or verification]_ | _[approve or reject]_ | _[anchor review count]_ |


## Anchor Review Findings

| Review document | Reviewed artifact | Reviewed anchor | Decision | Feedback | Reviewed content |
| --- | --- | --- | --- | --- | --- |
| **[required]** _[review document]_ | _[artifact IRI]_ | _[anchor IRI]_ | _[review decision]_ | _[reviewer feedback]_ | _[anchored content]_ |


## VVS Requirement Coverage Summary

| Requirement | Mandate | Anchor | Shape | Evidence status |
| --- | --- | --- | --- | --- |
| **[required]** _[REQ-*]_ | _[validation or verification]_ | _[exact anchor key and title]_ | _[SHACL shape]_ | _[not assessed]_ |


\newpage

## Appendix A. Review Document And Workflow Evidence

| Review document | Schema | Author | IPFS URI | Encrypted | Auth proof |
| --- | --- | --- | --- | --- | --- |
| **[required]** _[review document]_ | _[schema IRI]_ | _[author]_ | _[IPFS URI]_ | _[yes/no]_ | _[proof type]_ |


| Review document | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| **[required]** _[review document]_ | _[submitted document]_ | _[workflow step]_ | _[subject]_ | _[submitter]_ | _[recipient]_ | _[topic]_ | _[sequence]_ | _[timestamp]_ |


\newpage

## Appendix B. Source Graph And Hash Evidence

### Input JSON-LD
**[required]** _[to be populated]_

### Evidence JSON-LD
**[optional]** _[to be populated]_

### Source graph hash evidence
**[optional]** _[to be populated]_


\newpage

## Appendix C. Field-To-Predicate Map

### Review document type
rdf:type

### Document schema
nias-o:documentSchema

### Document author
nias-o:documentAuthor

### Document IPFS URI
nias-o:resourceIpfsUri

### Authenticity proof
nias-o:authProof

### Final review decision
nias-o:finalReviewDecision

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

### Workflow submission evidence
nias-o:hasWorkflowSubmission

### Consensus message
nias-o:workflowSubmissionConsensusMessage

### VVS requirement implementation
nias-o:implementedByShape
