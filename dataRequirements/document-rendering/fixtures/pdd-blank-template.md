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


# {{ project.title }}

- **[optional]** titlePage.keyProjectInformation: _[to be populated]_


## Document Control

- **[optional]** documentControl.versionSummary: _[to be populated]_


- **[optional]** documentControl.validationStatus: _[to be populated]_


This Project Design Document is generated from NIAS semantic workflow data. The
canonical data requirements are defined by the NIAS SHACL shapes. This rendering
profile controls document presentation only.

## Section A. Description Of Project

- **[required]** Document IPFS URI: _[to be populated]_
- **[required]** Document schema IRI: _[to be populated]_
- **[required]** Encrypted: _[to be populated]_
- **[required]** Document author: _[to be populated]_
- **[required]** Authenticity proof: _[to be populated]_
- **[required]** PDD Section A content: _[to be populated]_
  - **[required]** Reporting agent IRI: _[to be populated]_
  - **[required]** Project design: _[to be populated]_
    - **[required]** Project title: _[to be populated]_
    - **[required]** Project purpose: _[to be populated]_
      - **[required]** Objective: _[to be populated]_
    - **[required]** Project locations: _[to be populated]_
      - **[required]** Location IPFS URI: _[to be populated]_
    - **[required]** Technologies and measures: _[to be populated]_
      - **[required]** Type: _[to be populated]_
      - **[required]** Description: _[to be populated]_
      - **[required]** Current age in years: _[to be populated]_
      - **[required]** Estimated lifespan in years: _[to be populated]_
      - **[optional]** Additional information: _[to be populated]_
    - **[required]** Project parties: _[to be populated]_
      - **[required]** Party name: _[to be populated]_
      - **[required]** Host party: _[to be populated]_
      - **[required]** Participant party: _[to be populated]_
      - **[required]** Public or private: _[to be populated]_
      - **[optional]** Additional information: _[to be populated]_
    - **[required]** Legal matters: _[to be populated]_
    - **[required]** Public funding: _[to be populated]_
    - **[optional]** Public funding sources: _[to be populated]_
    - **[required]** Project history: _[to be populated]_
    - **[required]** Debundling assessment: _[to be populated]_
    - **[optional]** Eligibility description: _[to be populated]_
  - **[required]** Document schema IRI: _[to be populated]_
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


### A.1 Purpose And General Description

- **[optional]** pdd.sectionA.projectPurpose: _[to be populated]_


### A.2 Location Of Project

- **[optional]** pdd.sectionA.locations: _[to be populated]_


### A.3 Technologies And Measures

- **[optional]** pdd.sectionA.technologiesAndMeasures: _[to be populated]_


### A.4 Project Parties

- **[optional]** pdd.sectionA.projectParties: _[to be populated]_


### A.5 Legal Matters, Funding, History, And Eligibility

- **[optional]** pdd.sectionA.legalFundingHistoryEligibility: _[to be populated]_


## Section B. Impact Claims And Monitoring

- **[required]** Document IPFS URI: _[to be populated]_
- **[required]** Document schema IRI: _[to be populated]_
- **[required]** Encrypted: _[to be populated]_
- **[required]** Document author: _[to be populated]_
- **[required]** Authenticity proof: _[to be populated]_
- **[required]** PDD Section B content: _[to be populated]_
  - **[required]** Reporting agent IRI: _[to be populated]_
  - **[required]** Project subject IRI: _[to be populated]_
  - **[required]** Declared impacts: _[to be populated]_
    - **[required]** Intentionality: _[to be populated]_
    - **[required]** Beneficial or adverse: _[to be populated]_
    - **[required]** Impact description: _[to be populated]_
    - **[required]** Monitored: _[to be populated]_
    - **[optional]** Not monitored justification: _[to be populated]_
    - **[optional]** Additionality justification: _[to be populated]_
    - **[optional]** Baseline or counterfactual state: _[to be populated]_
      - **[required]** Temporal location: _[to be populated]_
        - **[required]** Date and time: _[to be populated]_
      - **[required]** State modality: _[to be populated]_
      - **[required]** Indicator definition IRI: _[to be populated]_
      - **[required]** Indicator value: _[to be populated]_
        - **[required]** Indicator value: _[to be populated]_
        - **[optional]** Unit IRI: _[to be populated]_
    - **[optional]** Project or real state: _[to be populated]_
      - **[required]** Temporal location: _[to be populated]_
        - **[required]** Date and time: _[to be populated]_
      - **[required]** State modality: _[to be populated]_
      - **[required]** Indicator definition IRI: _[to be populated]_
      - **[required]** Indicator value: _[to be populated]_
        - **[required]** Indicator value: _[to be populated]_
        - **[optional]** Unit IRI: _[to be populated]_
    - **[optional]** Provenance resources: _[to be populated]_
    - **[optional]** Crediting period: _[to be populated]_
      - **[required]** Crediting period start: _[to be populated]_
        - **[required]** Date and time: _[to be populated]_
      - **[required]** Crediting period end: _[to be populated]_
        - **[required]** Date and time: _[to be populated]_
      - **[required]** Renewable crediting period: _[to be populated]_
    - **[optional]** Monitoring periods: _[to be populated]_
      - **[required]** Start: _[to be populated]_
        - **[required]** Date and time: _[to be populated]_
      - **[required]** End: _[to be populated]_
        - **[required]** Date and time: _[to be populated]_
    - **[optional]** Data and parameter requirements: _[to be populated]_
      - **[required]** Parameter label: _[to be populated]_
      - **[required]** Description: _[to be populated]_
      - **[required]** Purpose: _[to be populated]_
      - **[required]** Unit IRI: _[to be populated]_
      - **[required]** Monitoring status: _[to be populated]_
      - **[optional]** Measurement methods and procedures: _[to be populated]_
      - **[optional]** QA/QC procedures: _[to be populated]_
      - **[optional]** Monitoring frequency: _[to be populated]_
      - **[optional]** Sampling plan: _[to be populated]_
      - **[optional]** Applied value: _[to be populated]_
      - **[optional]** Data source: _[to be populated]_
    - **[optional]** Ex-ante impact estimate: _[to be populated]_
  - **[required]** Impact claims: _[to be populated]_
    - **[required]** Project subject IRI: _[to be populated]_
    - **[required]** Methodology IRIs: _[to be populated]_
  - **[optional]** Report methodology IRIs: _[to be populated]_
  - **[required]** Document schema IRI: _[to be populated]_
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


### B.1 Methodology References

- **[optional]** pdd.sectionB.methodologyReferences: _[to be populated]_


### B.2 Declared Impacts

- **[optional]** pdd.sectionB.declaredImpacts: _[to be populated]_


### B.3 Impact Claims

- **[optional]** pdd.sectionB.impactClaims: _[to be populated]_


### B.4 Crediting And Monitoring Periods

- **[optional]** pdd.sectionB.creditingAndMonitoringPeriods: _[to be populated]_


### B.5 Data And Parameter Requirements

- **[optional]** pdd.sectionB.dataParameterTables: _[to be populated]_


Each data or monitoring parameter renders as one table under this subsection.

### B.6 Ex Ante Estimates

- **[optional]** pdd.sectionB.exAnteEstimates: _[to be populated]_


## Section C. Stakeholder Engagement

- **[required]** Document IPFS URI: _[to be populated]_
- **[required]** Document schema IRI: _[to be populated]_
- **[required]** Encrypted: _[to be populated]_
- **[required]** Document author: _[to be populated]_
- **[required]** Authenticity proof: _[to be populated]_
- **[required]** Reporting agent IRI: _[to be populated]_
- **[required]** Project subject IRI: _[to be populated]_
- **[required]** Report schema IRI: _[to be populated]_
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
- **[required]** Stakeholder engagement modalities: _[to be populated]_
- **[optional]** Stakeholder comment summary: _[to be populated]_
- **[optional]** Stakeholder comment consideration: _[to be populated]_


### C.1 Stakeholder Engagement Modalities

- **[optional]** pdd.sectionC.stakeholderEngagementModalities: _[to be populated]_


### C.2 Stakeholder Comment Summary

- **[optional]** pdd.sectionC.stakeholderCommentSummary: _[to be populated]_


### C.3 Stakeholder Comment Consideration

- **[optional]** pdd.sectionC.stakeholderCommentConsideration: _[to be populated]_


## Validation Review Summary

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


## PDD Certificate Issuance Request

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


## Appendix A. Document Metadata

- **[optional]** metadataAppendix: _[to be populated]_


## Appendix B. Field-To-Predicate Map

- **[optional]** predicateMapAppendix: _[to be populated]_


## Appendix C. Source Graph And Hash Evidence

- **[optional]** sourceEvidenceAppendix: _[to be populated]_
