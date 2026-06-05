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
---

# Nova Impact Accounting Standard

## Monitoring Report

{{ render: titlePage.reportTitle }}

{{ render: titlePage.packageSummary }}

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

{{ render: monitoring.documentEnvelope }}

## Monitoring Period

{{ render: monitoring.period }}

## Measured Impact Observation

{{ render: monitoring.observation }}

## Dataset Evidence

{{ render: monitoring.datasets }}

## Calculation Resources

{{ render: monitoring.resources }}

\newpage

## Appendix A. Workflow Evidence

{{ render: workflow.consensusEvidence }}

\newpage

## Appendix B. Source Graph And Hash Evidence

{{ render: sourceEvidenceAppendix }}

\newpage

## Appendix C. Field-To-Predicate Map

{{ render: predicateMapAppendix }}

## Rendering Map

| Report section | Source shape | Publication location | Render directive |
| --- | --- | --- | --- |
| Package summary | `MonitoringReportShape` | Title page | `{{ render: titlePage.packageSummary }}` |
| Document envelope | `DocumentShape` / `MonitoringReportShape` | Report Envelope | `{{ render: monitoring.documentEnvelope }}` |
| Monitoring period | `DateTimeIntervalShape` | Monitoring Period | `{{ render: monitoring.period }}` |
| Measured impact | `IndicatorObservationShape` | Measured Impact Observation | `{{ render: monitoring.observation }}` |
| Dataset evidence | `DatasetShape` / `DocumentReferenceShape` | Dataset Evidence | `{{ render: monitoring.datasets }}` |
| Calculation resources | `ResourceArtifactShape` | Calculation Resources | `{{ render: monitoring.resources }}` |
| Workflow evidence | `WorkflowDocumentSubmissionShape` / `HederaTopicMessageShape` | Appendix A. Workflow Evidence | `{{ render: workflow.consensusEvidence }}` |

## Rendering Boundary

The Monitoring Report is a separate monitoring-party publication. It references
the PDD version it reports against and supplies measured impact, dataset, and
calculation evidence. Validation Reports and Verification Reports remain
separate linked artifacts and are not embedded in this output.

## Sidecar Output Rules

Final monitoring exports should produce:

- `monitoring-report.md`
- `monitoring-report.pdf`
- `monitoring-report.html`
- `monitoring-report.metadata.jsonld`
- `monitoring-report.validation.json`

The Markdown/PDF/HTML outputs are human-readable projections. The sidecar files
carry machine-readable provenance, validation, source graph, hash, canonical
artifact anchors, and artifact metadata.
