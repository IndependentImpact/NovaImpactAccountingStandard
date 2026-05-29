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
renderedDocumentType: Validation Report
renderMode: draft
reportType: validation
rendererVersion: 0.1.0
sourceArtifact: validation-verification-report-input.jsonld
generatedAt: 2026-05-28T00:00:00Z
---

# Nova Impact Accounting Standard

## Validation Report

### Validation Review Package


| Field | Value |
| --- | --- |
| Report type | Validation Report |
| Review documents | 1 |
| Field reviews | 1 |
| Final decisions | Approve: 1 |
| VVS evidence targets | 3 |
| Generated at | 2026-05-28T00:00:00Z |
| Rendering mode | draft |
| Source artifact | validation-verification-report-input.jsonld |


\thispagestyle{pddtitle}

\newpage

\pagenumbering{roman}
\setcounter{page}{1}

## Table Of Contents

| Section | Page |
| --- | ---: |
| Review Decision Register | \pageref{review-decision-register} |
| Field Review Findings | \pageref{field-review-findings} |
| VVS Requirement Coverage Summary | \pageref{vvs-requirement-coverage-summary} |
| Appendix A. Review Document And Workflow Evidence | \pageref{appendix-a.-review-document-and-workflow-evidence} |
| Appendix B. Source Graph And Hash Evidence | \pageref{appendix-b.-source-graph-and-hash-evidence} |
| Appendix C. Field-To-Predicate Map | \pageref{appendix-c.-field-to-predicate-map} |


\newpage

\pagenumbering{arabic}
\setcounter{page}{1}

## Review Decision Register

| Review document | Review type | Final decision | Field reviews |
| --- | --- | --- | ---: |
| vv-validation-review-1 | Validation review | Approve | 1 |


## Field Review Findings

| Review document | Field | Decision | Feedback | Original response |
| --- | --- | --- | --- | --- |
| vv-validation-review-1 | PDD Section B declared impacts | Approve | The impact declaration is complete for validation. | One beneficial GHG impact is declared with a quantification methodology. |


## VVS Requirement Coverage Summary

| Requirement | Mandate | Anchor | Shape | Evidence status |
| --- | --- | --- | --- | --- |
| REQ-PDD-001 | validation | PddSectionAReport | ReqPdd001Shape | draft evidence present (1) |
| REQ-PDD-002 | validation | PddSectionBReport | ReqPdd002Shape | draft evidence present (1) |
| REQ-PDD-003 | validation | PddSectionCReport | ReqPdd003Shape | draft evidence present (1) |


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

| Field | Value |
| --- | --- |
| Source artifact | validation-verification-report-input.jsonld |
| Input JSON-LD | validation-verification-report-input.jsonld |
| Input SHA-256 | 8af13c57b79c6863cb421ac7a76b65fb49b8238d84619e67136d8e85bb1d3dfd |
| Evidence JSON-LD 1 | validation-verification-report-evidence.jsonld |
| Evidence SHA-256 1 | 880acc33f8caa29240d2d34c4bce0891480bcdbe852f14818ce6d7ed8c74d659 |


\newpage

## Appendix C. Field-To-Predicate Map

| Field | Value |
| --- | --- |
| Review document type | rdf:type |
| Document schema | nias-o:documentSchema |
| Final review decision | nias-o:finalReviewDecision |
| Field review | nias-o:fieldReview |
| Field key | nias-o:fieldKey |
| Field title | nias-o:fieldTitle |
| Reviewer decision | nias-o:reviewerDecision |
| Reviewer feedback | nias-o:reviewerFeedback |
| Document author | nias-o:documentAuthor |
| Document IPFS URI | nias-o:resourceIpfsUri |
| Authenticity proof | nias-o:authProof |
| Workflow submission evidence | nias-o:hasWorkflowSubmission |
| Consensus message | nias-o:workflowSubmissionConsensusMessage |
| VVS requirement ID | nias-o:requirementId |
| VVS implementing shape | nias-o:implementedByShape |
