# Linked Artifact Boundary Decisions

This note is the normative implementation contract for linked-artifact identity across:
- PDD Design
- Validation Report
- Monitoring Report
- Verification Report

## Canonical identity model

- Canonical schema identifier: `artifactSchemaCid`
- Human-readable schema label: `artifactSchemaVersionLabel`
- PDD label format: `nias:pdd-schema:{track}:{yyyy-mm-dd}:{shortCid}`
- Monitoring label format: `nias:mr-schema:{track}:{yyyy-mm-dd}:{shortCid}`

The CID remains authoritative; labels are for readability only.

## Submission identity model

Store submission identity as:
- `submissionTopicId`
- `submissionConsensusTimestamp`

Derived values may also be recorded:
- `submissionEventKey = {topicId}@{consensusTimestamp}`
- `submissionMessageUrl = /api/v1/topics/{topicId}/messages/{consensusTimestamp}`

## Artifact identity vocabulary

Common artifact identity:
- `artifactContentCid`
- `artifactSchemaCid`
- `artifactSchemaVersionLabel`
- `artifactAuthor`
- `workflowSubject`
- `submissionTopicId`
- `submissionConsensusTimestamp`
- optional: `submissionEventKey`, `submissionMessageUrl`

Reviewed artifact identity:
- `reviewedArtifactType`
- `reviewedArtifactContentCid`
- `reviewedArtifactSchemaCid`
- `reviewedArtifactSchemaVersionLabel`
- `reviewedSubmissionTopicId`
- `reviewedSubmissionConsensusTimestamp`

Upstream alignment:
- `alignedPddContentCid`
- `alignedPddSubmissionTopicId`
- `alignedPddSubmissionConsensusTimestamp`

DLR linkage:
- `linkedDlrContentCid`
- `reviewedDlrContentCid`

## Activity-specific requirements

- PDD artifact version identity includes common artifact identity fields.
- Validation review targets a submitted PDD artifact and submission event.
- Monitoring artifact version identity includes common identity fields and must include aligned PDD identity plus `linkedDlrContentCid`.
- Verification review targets a submitted Monitoring Report artifact and submission event, and must include `reviewedDlrContentCid`.

## Local source of truth (pre-integration)

Before Fluree/IPFS/Hedera integration, the local source of truth is:
1. canonical JSON-LD package, and
2. simulated submission event fixture.

UI state, preview output, and renderer-only output are not canonical sources of truth.
