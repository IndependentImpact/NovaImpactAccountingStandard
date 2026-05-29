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
reportType: validation
---

# Nova Impact Accounting Standard

## Validation Report

### _[Validation Report package title]_


| Field | Value |
| --- | --- |
| Report type | Validation Report |
| Review documents | **[required]** _[to be populated]_ |
| Field reviews | **[required]** _[to be populated]_ |
| Final decisions | **[required]** _[to be populated]_ |
| VVS evidence targets | **[required for final]** _[to be populated]_ |
| Generated at | **[optional]** _[to be populated]_ |
| Rendering mode | **[optional]** _[draft or final]_ |
| Source artifact | **[optional]** _[to be populated]_ |


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
| Workflow And Consensus Evidence | \pageref{workflow-and-consensus-evidence} |
| Appendix A. Source Graph And Hash Evidence | \pageref{appendix-a.-source-graph-and-hash-evidence} |
| Appendix B. Field-To-Predicate Map | \pageref{appendix-b.-field-to-predicate-map} |


\newpage

\pagenumbering{arabic}
\setcounter{page}{1}

## Review Decision Register

| Review document | Review type | Final decision | Schema | Reviewer | IPFS URI |
| --- | --- | --- | --- | --- | --- |
| **[required]** _[review document]_ | _[validation or verification]_ | _[approve or reject]_ | _[schema IRI]_ | _[reviewer]_ | _[IPFS URI]_ |


## Field Review Findings

| Review document | Field | Decision | Feedback | Original response |
| --- | --- | --- | --- | --- |
| **[required]** _[review document]_ | _[field title]_ | _[field decision]_ | _[reviewer feedback]_ | _[submitted response]_ |


## VVS Requirement Coverage Summary

| Requirement | Mandate | Anchor | Shape | Evidence status |
| --- | --- | --- | --- | --- |
| **[required]** _[REQ-*]_ | _[validation or verification]_ | _[PDD/DLR/MR anchor]_ | _[SHACL shape]_ | _[not assessed]_ |


## Workflow And Consensus Evidence

| Review document | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| **[required]** _[review document]_ | _[submitted document]_ | _[workflow step]_ | _[subject]_ | _[submitter]_ | _[recipient]_ | _[topic]_ | _[sequence]_ | _[timestamp]_ |


\newpage

## Appendix A. Source Graph And Hash Evidence

| Field | Value |
| --- | --- |
| Input JSON-LD | **[required]** _[to be populated]_ |
| Evidence JSON-LD | **[optional]** _[to be populated]_ |
| Source graph hash evidence | **[optional]** _[to be populated]_ |


\newpage

## Appendix B. Field-To-Predicate Map

| Field | Value |
| --- | --- |
| Final review decision | nias-o:finalReviewDecision |
| Field review | nias-o:fieldReview |
| Reviewer decision | nias-o:reviewerDecision |
| Reviewer feedback | nias-o:reviewerFeedback |
| Workflow submission | nias-o:hasWorkflowSubmission |
| VVS requirement implementation | nias-o:implementedByShape |
