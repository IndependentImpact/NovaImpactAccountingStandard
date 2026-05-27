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

### _[Project title to be populated]_


| Field | Value |
| --- | --- |
| Project ID | _[optional: project display ID or project IRI]_ |
| PDD/schema version | _[optional: document version or schema IRI]_ |
| Completion/publication date | _[optional: completion or publication date]_ |
| Project developer | _[required: project developer or responsible party]_ |
| Project representative | _[optional: representative]_ |
| Host party or country | _[required where applicable]_ |
| Project participants and communities | _[required: project parties]_ |
| Methodology and version | _[required: methodology reference(s)]_ |
| Product or impact type | _[optional: product requirement or impact type]_ |
| Project cycle | _[optional: regular, retroactive, or other cycle]_ |


\newpage

## Table Of Contents

- [Section A. Description Of Project](#section-a-description-of-project)
  - [A.1 Purpose And General Description](#a1-purpose-and-general-description)
  - [A.2 Location Of Project](#a2-location-of-project)
  - [A.3 Technologies And Measures](#a3-technologies-and-measures)
  - [A.4 Project Parties](#a4-project-parties)
  - [A.5 Legal Matters, Funding, History, And Eligibility](#a5-legal-matters-funding-history-and-eligibility)
- [Section B. Impact Claims And Monitoring](#section-b-impact-claims-and-monitoring)
  - [B.1 Methodology References](#b1-methodology-references)
  - [B.2 Declared Impacts](#b2-declared-impacts)
  - [B.3 Impact Claims](#b3-impact-claims)
  - [B.4 Crediting And Monitoring Periods](#b4-crediting-and-monitoring-periods)
  - [B.5 Data And Parameter Requirements](#b5-data-and-parameter-requirements)
  - [B.6 Ex Ante Estimates](#b6-ex-ante-estimates)
- [Section C. Stakeholder Engagement](#section-c-stakeholder-engagement)
  - [C.1 Stakeholder Engagement Modalities](#c1-stakeholder-engagement-modalities)
  - [C.2 Stakeholder Comment Summary](#c2-stakeholder-comment-summary)
  - [C.3 Stakeholder Comment Consideration](#c3-stakeholder-comment-consideration)
- [Appendix A. Document And Process Metadata](#appendix-a-document-and-process-metadata)
  - [A.1 Validation Review Summary](#a1-validation-review-summary)
  - [A.2 PDD Certificate Issuance Request](#a2-pdd-certificate-issuance-request)
- [Appendix B. Field-To-Predicate Map](#appendix-b-field-to-predicate-map)
- [Appendix C. Source Graph And Hash Evidence](#appendix-c-source-graph-and-hash-evidence)


\newpage

## Section A. Description Of Project



### A.1 Purpose And General Description

- **[required]** Project title: _[to be populated]_
- **[required]** Objective: _[to be populated]_


### A.2 Location Of Project

- **[required]** Project locations: _[location, boundary, map, or resource reference]_


### A.3 Technologies And Measures

- **[required]** Type: _[facility, system, equipment, or other]_
- **[required]** Description: _[to be populated]_
- **[required]** Current age in years: _[to be populated]_
- **[required]** Estimated lifespan in years: _[to be populated]_
- **[optional]** Additional information: _[to be populated]_


### A.4 Project Parties

- **[required]** Party name: _[to be populated]_
- **[required]** Host party: _[yes/no]_
- **[required]** Participant party: _[yes/no]_
- **[required]** Public or private: _[to be populated]_
- **[optional]** Additional information: _[to be populated]_


### A.5 Legal Matters, Funding, History, And Eligibility

- **[required]** Legal matters: _[to be populated]_
- **[required]** Public funding: _[yes/no]_
- **[optional]** Public funding sources: _[to be populated]_
- **[required]** Project history: _[to be populated]_
- **[required]** Debundling assessment: _[to be populated]_
- **[optional]** Eligibility description: _[to be populated]_


## Section B. Impact Claims And Monitoring



### B.1 Methodology References

- **[required]** Methodology reference and version: _[to be populated]_


### B.2 Declared Impacts

- **[required]** Intentionality: _[intentional or unintentional]_
- **[required]** Beneficial or adverse: _[beneficial or adverse]_
- **[required]** Impact description: _[to be populated]_
- **[required]** Monitored: _[yes/no]_
- **[optional]** Not monitored justification: _[to be populated]_
- **[optional]** Additionality justification: _[to be populated]_
- **[optional]** Baseline or counterfactual state: _[indicator, value, unit, date/time]_
- **[optional]** Project or real state: _[indicator, value, unit, date/time]_
- **[optional]** Provenance resources: _[to be populated]_


### B.3 Impact Claims

- **[required]** Impact claim subject: _[project or activity]_
- **[required]** Methodology references: _[to be populated]_


### B.4 Crediting And Monitoring Periods

- **[optional]** Crediting period start: _[to be populated]_
- **[optional]** Crediting period end: _[to be populated]_
- **[optional]** Renewable crediting period: _[yes/no]_
- **[optional]** Monitoring periods: _[start and end date/time]_


### B.5 Data And Parameter Requirements

#### Parameter: _[parameter label]_

| Field | Value |
| --- | --- |
| Description | _[required]_ |
| Purpose | _[required]_ |
| Unit | _[required unit IRI or label]_ |
| Monitoring status | _[required: monitored or fixed ex ante]_ |
| Measurement methods and procedures | _[optional]_ |
| QA/QC procedures | _[optional]_ |
| Monitoring frequency | _[optional]_ |
| Sampling plan | _[optional]_ |
| Applied value | _[optional]_ |
| Data source | _[optional]_ |


Each data or monitoring parameter renders as one table under this subsection.

### B.6 Ex Ante Estimates

- **[optional]** Ex-ante impact estimate: _[to be populated]_


## Section C. Stakeholder Engagement



### C.1 Stakeholder Engagement Modalities

- **[required]** Stakeholder engagement modalities: _[to be populated]_


### C.2 Stakeholder Comment Summary

- **[optional]** Stakeholder comment summary: _[to be populated]_


### C.3 Stakeholder Comment Consideration

- **[optional]** Stakeholder comment consideration: _[to be populated]_


## Appendix A. Document And Process Metadata

| Field | Value |
| --- | --- |
| Document IPFS URI | _[required: source document artifact URI]_ |
| Document schema IRI | _[required: source document schema IRI]_ |
| Encrypted | _[required: yes/no]_ |
| Document author | _[required: author or reporting agent IRI]_ |
| Authenticity proof | _[required: none, signature, or verifiable credential]_ |
| Workflow submission | _[required: workflow submission evidence]_ |
| Source artifact | _[rendering source artifact identifier]_ |
| Rendering profile | nias-pdd-rendering-profile |
| Rendering mode | _[draft or final]_ |
| Source graph/hash evidence | _[see Appendix C]_ |


### A.1 Validation Review Summary

- **[required]** PDD-A review workflow submission: _[to be populated]_
  - **[required]** Submitted document: _[to be populated]_
  - **[required]** Workflow: _[to be populated]_
  - **[required]** Workflow step: _[to be populated]_
  - **[required]** Workflow subject: _[to be populated]_
  - **[required]** Submitted by: _[to be populated]_
  - **[required]** Recipient: _[to be populated]_
  - **[required]** Consensus message: _[to be populated]_
    - **[required]** Consensus topic: _[to be populated]_
    - **[optional]** Sequence number: _[to be populated]_
    - **[required]** Consensus timestamp: _[to be populated]_
    - **[optional]** Message content: _[to be populated]_
- **[required]** Reviewed PDD-A document: _[to be populated]_
- **[required]** PDD-A field reviews: _[to be populated]_
  - **[required]** Field key: _[to be populated]_
  - **[required]** Field title: _[to be populated]_
  - **[required]** Field prompt: _[to be populated]_
  - **[required]** Original response: _[to be populated]_
  - **[required]** Reviewer decision: _[to be populated]_
  - **[required]** Reviewer feedback: _[to be populated]_
- **[required]** Final PDD-A review decision: _[to be populated]_


- **[required]** PDD-B review workflow submission: _[to be populated]_
  - **[required]** Submitted document: _[to be populated]_
  - **[required]** Workflow: _[to be populated]_
  - **[required]** Workflow step: _[to be populated]_
  - **[required]** Workflow subject: _[to be populated]_
  - **[required]** Submitted by: _[to be populated]_
  - **[required]** Recipient: _[to be populated]_
  - **[required]** Consensus message: _[to be populated]_
    - **[required]** Consensus topic: _[to be populated]_
    - **[optional]** Sequence number: _[to be populated]_
    - **[required]** Consensus timestamp: _[to be populated]_
    - **[optional]** Message content: _[to be populated]_
- **[required]** Reviewed PDD-B document: _[to be populated]_
- **[required]** PDD-B field reviews: _[to be populated]_
  - **[required]** Field key: _[to be populated]_
  - **[required]** Field title: _[to be populated]_
  - **[required]** Field prompt: _[to be populated]_
  - **[required]** Original response: _[to be populated]_
  - **[required]** Reviewer decision: _[to be populated]_
  - **[required]** Reviewer feedback: _[to be populated]_
- **[required]** Final PDD-B review decision: _[to be populated]_


- **[required]** PDD-C review workflow submission: _[to be populated]_
  - **[required]** Submitted document: _[to be populated]_
  - **[required]** Workflow: _[to be populated]_
  - **[required]** Workflow step: _[to be populated]_
  - **[required]** Workflow subject: _[to be populated]_
  - **[required]** Submitted by: _[to be populated]_
  - **[required]** Recipient: _[to be populated]_
  - **[required]** Consensus message: _[to be populated]_
    - **[required]** Consensus topic: _[to be populated]_
    - **[optional]** Sequence number: _[to be populated]_
    - **[required]** Consensus timestamp: _[to be populated]_
    - **[optional]** Message content: _[to be populated]_
- **[required]** Reviewed PDD-C document: _[to be populated]_
- **[required]** PDD-C field reviews: _[to be populated]_
  - **[required]** Field key: _[to be populated]_
  - **[required]** Field title: _[to be populated]_
  - **[required]** Field prompt: _[to be populated]_
  - **[required]** Original response: _[to be populated]_
  - **[required]** Reviewer decision: _[to be populated]_
  - **[required]** Reviewer feedback: _[to be populated]_
- **[required]** Final PDD-C review decision: _[to be populated]_


### A.2 PDD Certificate Issuance Request

- **[required]** Document IPFS URI: _[to be populated]_
- **[required]** Document schema IRI: _[to be populated]_
- **[required]** Encrypted: _[to be populated]_
- **[required]** Document author: _[to be populated]_
- **[required]** Authenticity proof: _[to be populated]_
- **[required]** Workflow submission: _[to be populated]_
  - **[required]** Submitted document: _[to be populated]_
  - **[required]** Workflow: _[to be populated]_
  - **[required]** Workflow step: _[to be populated]_
  - **[required]** Workflow subject: _[to be populated]_
  - **[required]** Submitted by: _[to be populated]_
  - **[required]** Recipient: _[to be populated]_
  - **[required]** Consensus message: _[to be populated]_
    - **[required]** Consensus topic: _[to be populated]_
    - **[optional]** Sequence number: _[to be populated]_
    - **[required]** Consensus timestamp: _[to be populated]_
    - **[optional]** Message content: _[to be populated]_
- **[required]** Approved PDD-A validation review: _[to be populated]_
  - **[required]** Message ID: _[to be populated]_
  - **[required]** IPFS URI: _[to be populated]_
- **[required]** Approved PDD-B validation review: _[to be populated]_
  - **[required]** Message ID: _[to be populated]_
  - **[required]** IPFS URI: _[to be populated]_
- **[required]** Approved PDD-C validation review: _[to be populated]_
  - **[required]** Message ID: _[to be populated]_
  - **[required]** IPFS URI: _[to be populated]_
- **[required]** Issuance account ID: _[to be populated]_


## Appendix B. Field-To-Predicate Map

- **[optional]** predicateMapAppendix: _[to be populated]_


## Appendix C. Source Graph And Hash Evidence

- **[optional]** sourceEvidenceAppendix: _[to be populated]_
