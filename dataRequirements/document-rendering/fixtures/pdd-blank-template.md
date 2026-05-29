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
toc: true
toc-depth: 3
toc-title: "Table of Contents"
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


\thispagestyle{pddtitle}

\newpage

\pagenumbering{roman}
\setcounter{page}{1}

## Table Of Contents

\tableofcontents

\newpage

\pagenumbering{arabic}
\setcounter{page}{1}

## Section A. Description Of Project



### A.1 Purpose And General Description

| Field | Value |
| --- | --- |
| Project title | **[required]** _[to be populated]_ |
| Objective | **[required]** _[to be populated]_ |


### A.2 Location Of Project

| Field | Value |
| --- | --- |
| Project locations | **[required]** _[location, boundary, map, or resource reference]_ |


### A.3 Technologies And Measures

#### Technology Or Measure

| Field | Value |
| --- | --- |
| Type | **[required]** _[facility, system, equipment, or other]_ |
| Description | **[required]** _[to be populated]_ |
| Current age in years | **[required]** _[to be populated]_ |
| Estimated lifespan in years | **[required]** _[to be populated]_ |
| Additional information | **[optional]** _[to be populated]_ |


### A.4 Project Parties

#### Project Party

| Field | Value |
| --- | --- |
| Party name | **[required]** _[to be populated]_ |
| Host party | **[required]** _[yes/no]_ |
| Participant party | **[required]** _[yes/no]_ |
| Public or private | **[required]** _[to be populated]_ |
| Additional information | **[optional]** _[to be populated]_ |


### A.5 Legal Matters, Funding, History, And Eligibility

| Field | Value |
| --- | --- |
| Legal matters | **[required]** _[to be populated]_ |
| Public funding | **[required]** _[yes/no]_ |
| Public funding sources | **[optional]** _[to be populated]_ |
| Project history | **[required]** _[to be populated]_ |
| Debundling assessment | **[required]** _[to be populated]_ |
| Eligibility description | **[optional]** _[to be populated]_ |


## Section B. Impact Claims And Monitoring



### B.1 Methodology References

| Methodology reference and version |
| --- |
| **[required]** _[to be populated]_ |


### B.2 Declared Impacts

#### Declared Impact

| Field | Value |
| --- | --- |
| Intentionality | **[required]** _[intentional or unintentional]_ |
| Beneficial or adverse | **[required]** _[beneficial or adverse]_ |
| Impact description | **[required]** _[to be populated]_ |
| Monitored | **[required]** _[yes/no]_ |
| Not monitored justification | **[optional]** _[to be populated]_ |
| Additionality justification | **[optional]** _[to be populated]_ |
| Baseline or counterfactual state | **[optional]** _[indicator, value, unit, date/time]_ |
| Project or real state | **[optional]** _[indicator, value, unit, date/time]_ |
| Provenance resources | **[optional]** _[to be populated]_ |


### B.3 Impact Claims

#### Impact Claim

| Field | Value |
| --- | --- |
| Impact claim subject | **[required]** _[project or activity]_ |
| Methodology references | **[required]** _[to be populated]_ |


### B.4 Crediting And Monitoring Periods

#### Crediting And Monitoring Period

| Field | Value |
| --- | --- |
| Crediting period start | **[optional]** _[to be populated]_ |
| Crediting period end | **[optional]** _[to be populated]_ |
| Renewable crediting period | **[optional]** _[yes/no]_ |
| Monitoring periods | **[optional]** _[start and end date/time]_ |


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

| Field | Value |
| --- | --- |
| Ex-ante impact estimate | **[optional]** _[to be populated]_ |


## Section C. Stakeholder Engagement



### C.1 Stakeholder Engagement Modalities

| Field | Value |
| --- | --- |
| Stakeholder engagement modalities | **[required]** _[to be populated]_ |


### C.2 Stakeholder Comment Summary

| Field | Value |
| --- | --- |
| Stakeholder comment summary | **[optional]** _[to be populated]_ |


### C.3 Stakeholder Comment Consideration

| Field | Value |
| --- | --- |
| Stakeholder comment consideration | **[optional]** _[to be populated]_ |


\newpage

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


\newpage

## Appendix B. Field-To-Predicate Map

| Field | Value |
| --- | --- |
| Predicate map appendix | **[optional]** _[to be populated]_ |


\newpage

## Appendix C. Source Graph And Hash Evidence

| Field | Value |
| --- | --- |
| Source graph identifier | **[optional]** _[to be populated]_ |
