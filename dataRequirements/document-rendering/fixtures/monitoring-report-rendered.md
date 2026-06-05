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
renderMode: draft
reportType: monitoring
rendererVersion: 0.1.0
sourceArtifact: monitoring-report-input.jsonld
generatedAt: 2026-05-28T00:00:00Z
---

# Nova Impact Accounting Standard

## Monitoring Report

### Monitoring Report Package


#### Report documents
1

#### Aligned PDD version
pdd-version-1

#### Measured observations
1

#### Datasets
1

#### Issuance account
0.0.3003

#### Generated at
2026-05-28T00:00:00Z

#### Rendering mode
draft

#### Source artifact
monitoring-report-input.jsonld


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
| monitoring-report | MonitoringReport-6.0.0 | monitoring-party-1 | pdd-version-1 | ipfs://bafymonitoringreport | No | None |


## Monitoring Period

| Monitoring report | Indicator label | Start | End |
| --- | --- | --- | --- |
| monitoring-report | Tonnes of CO2e avoided | 2026-01-01T00:00:00Z | 2026-03-31T23:59:59Z |


## Measured Impact Observation

| Monitoring report | Observation | Indicator | Value | Unit | Observation period |
| --- | --- | --- | ---: | --- | --- |
| monitoring-report | impact-observation | indicator-co2e-avoided | 123.45 | TONNE | 2026-01-01T00:00:00Z to 2026-03-31T23:59:59Z |


## Dataset Evidence

| Monitoring report | Dataset | Dataset name | Data lineage message | Data lineage IPFS | Final dataset IPFS |
| --- | --- | --- | --- | --- | --- |
| monitoring-report | Approved monitoring dataset Q1 2026 | Approved monitoring dataset Q1 2026 | 0.0.1001-1704067200-000000004 | ipfs://bafydatareview | ipfs://bafydatasetfinal |


## Calculation Resources

| Monitoring report | Calculation code | Impact result | Calculation report | Issuance account |
| --- | --- | --- | --- | --- |
| monitoring-report | ipfs://bafycalculationcode | ipfs://bafyimpactresult | ipfs://bafycalculationreport | 0.0.3003 |


\newpage

## Appendix A. Workflow Evidence

| Monitoring report | Submitted document | Workflow step | Subject | Submitted by | Recipient | Consensus topic | Sequence | Timestamp |
| --- | --- | --- | --- | --- | --- | --- | ---: | --- |
| monitoring-report | monitoring-report | Submit Monitoring Report | project-1 | monitoring-party-1 | registry-1 | topic-1 | 41 | 2026-04-01T00:00:00Z |


\newpage

## Appendix B. Source Graph And Hash Evidence

### Source artifact
monitoring-report-input.jsonld

### Input JSON-LD
monitoring-report-input.jsonld

### Input SHA-256
b9084375470b2db5c20549f02fa1e7fa00d34c641bc991c4b7bf760cf17e0380

### Evidence JSON-LD
Not supplied


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
