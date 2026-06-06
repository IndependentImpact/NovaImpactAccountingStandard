---
profile: nias-monitoring-report-rendering-profile
profileVersion: 0.1.0
standard: Nova Impact Accounting Standard
documentType: Monitoring Report
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
  - monitoring-report.metadata.jsonld
  - monitoring-report.validation.json
renderedDocumentType: Monitoring Report
---

# Nova Impact Accounting Standard

## Monitoring Report

### _[Monitoring Report package title]_


#### Report documents
**[required]** _[to be populated]_

#### Aligned PDD version
**[required]** _[to be populated]_

#### Monitoring period
**[required]** _[to be populated]_

#### Measured observations
**[required]** _[to be populated]_

#### Datasets
**[required]** _[to be populated]_

#### Issuance account
**[required]** _[to be populated]_

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

## Report Envelope

| Monitoring report | Schema | Author | Aligned PDD | IPFS URI | Encrypted | Auth proof |
| --- | --- | --- | --- | --- | --- | --- |
| **[required]** _[report document]_ | _[schema IRI]_ | _[author]_ | _[PDD version]_ | _[IPFS URI]_ | _[yes/no]_ | _[proof type]_ |


## Monitoring Period

| Monitoring report | Indicator label | Start | End |
| --- | --- | --- | --- |
| **[required]** _[report document]_ | _[indicator]_ | _[start]_ | _[end]_ |


## Measured Impact Observation

| Monitoring report | Observation | Indicator | Value | Unit | Observation period |
| --- | --- | --- | ---: | --- | --- |
| **[required]** _[report document]_ | _[observation]_ | _[indicator]_ | _[value]_ | _[unit]_ | _[period]_ |


## Dataset Evidence

| Monitoring report | Dataset | Dataset name | Data lineage message | Data lineage IPFS | Final dataset IPFS |
| --- | --- | --- | --- | --- | --- |
| **[required]** _[report document]_ | _[dataset]_ | _[name]_ | _[message ID]_ | _[IPFS URI]_ | _[IPFS URI]_ |


## Calculation Resources

| Monitoring report | Calculation code | Impact result | Calculation report | Issuance account |
| --- | --- | --- | --- | --- |
| **[required]** _[report document]_ | _[IPFS URI]_ | _[IPFS URI]_ | _[IPFS URI]_ | _[account]_ |


\newpage

## Appendix A. Workflow Evidence

| Monitoring report | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| **[required]** _[report document]_ | _[submitted document]_ | _[workflow step]_ | _[subject]_ | _[submitter]_ | _[recipient]_ | _[topic]_ | _[sequence]_ | _[timestamp]_ |


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

### Monitoring report type
rdf:type

### Document schema
nias-o:documentSchema

### Aligned PDD version
nias-o:alignedWithPDD

### Monitoring period
nias-o:forPeriod

### Reported observation
nias-o:reportedObservation

### Dataset evidence
nias-o:usesDataset

### Calculation code
nias-o:calculationCode

### Impact result
nias-o:impactResultResource

### Calculation report
nias-o:calculationReport

### Requested issuance account
nias-o:requestedIssuanceAccountId
