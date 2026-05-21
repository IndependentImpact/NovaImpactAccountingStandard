# Artifact Lookup Queries

These are logical Fluree query templates for UI dropdowns and workflow gates.
They use canonical NIAS IRIs and the shared `context.jsonld` prefixes.

Replace `$FLUREE_LEDGER`, `$project`, `$scheme`, and similar placeholders at
runtime. Query results should be normalized by the application into option
records:

```json
{
  "id": "canonical artifact IRI",
  "label": "human-readable label",
  "type": "artifact class IRI",
  "source": "query identifier"
}
```

## Active Document Schemas

Purpose: populate developer/admin UI controls that need to select a document
schema resource.

```json
{
  "@context": "dataRequirements/fluree/context.jsonld",
  "from": "$FLUREE_LEDGER",
  "select": {
    "?schema": [
      "dcterms:title",
      "nias-o:validatingShape"
    ]
  },
  "where": {
    "@id": "?schema",
    "@type": "nias-o:DocumentSchema",
    "nias-o:validatingShape": "?shape"
  }
}
```

## PDD Section Documents For A Project

Purpose: list submitted PDD-A, PDD-B, and PDD-C documents for a project.

Runtime inputs:

- `$project` - workflow subject IRI.
- `$schema` - one of `document-schema/PDDxA-1.0.0`,
  `document-schema/PDDxB-9.0.0`, or `document-schema/PDDxC-4.0.0`.

```json
{
  "@context": "dataRequirements/fluree/context.jsonld",
  "from": "$FLUREE_LEDGER",
  "select": {
    "?document": [
      "nias-o:resourceIpfsUri",
      "nias-o:documentSchema",
      {
        "nias-o:hasWorkflowSubmission": [
          "nias-o:workflowSubject",
          "nias-o:workflowSubmissionConsensusMessage"
        ]
      }
    ]
  },
  "where": [
    {
      "@id": "?document",
      "@type": "data:Document",
      "nias-o:documentSchema": {
        "@id": "$schema"
      },
      "nias-o:hasWorkflowSubmission": {
        "@id": "?submission"
      }
    },
    {
      "@id": "?submission",
      "nias-o:workflowSubject": {
        "@id": "$project"
      }
    }
  ]
}
```

## Approved PDD Validation Reviews

Purpose: populate PDD-CIR references and enforce the PDD-CIR workflow gate.

Runtime inputs:

- `$project` - workflow subject IRI.
- `$reviewedSchema` - expected reviewed document schema IRI for the section.

The application should format `documentMessageId` from the resolved review
submission's Hedera topic ID and consensus timestamp, matching the existing
`DocumentReferenceShape`.

```json
{
  "@context": "dataRequirements/fluree/context.jsonld",
  "from": "$FLUREE_LEDGER",
  "select": {
    "?review": [
      "nias-o:resourceIpfsUri",
      "nias-o:finalReviewDecision",
      {
        "nias-o:isReviewOf": [
          "nias-o:documentSchema",
          "nias-o:resourceIpfsUri"
        ]
      },
      {
        "nias-o:hasWorkflowSubmission": [
          "nias-o:workflowSubject",
          {
            "nias-o:workflowSubmissionConsensusMessage": [
              {
                "hedera:inTopic": [
                  "hedera:hasTopicId"
                ]
              },
              "hedera:hasConsensusTimestamp"
            ]
          }
        ]
      }
    ]
  },
  "where": [
    {
      "@id": "?review",
      "@type": "nias-o:GenericDocumentReview",
      "nias-o:finalReviewDecision": {
        "@id": "nias-cs:review-approve"
      },
      "nias-o:isReviewOf": {
        "@id": "?reviewedDocument"
      },
      "nias-o:hasWorkflowSubmission": {
        "@id": "?reviewSubmission"
      }
    },
    {
      "@id": "?reviewedDocument",
      "@type": "data:Document",
      "nias-o:documentSchema": {
        "@id": "$reviewedSchema"
      },
      "nias-o:hasWorkflowSubmission": {
        "@id": "?sourceSubmission"
      }
    },
    {
      "@id": "?reviewSubmission",
      "nias-o:workflowSubject": {
        "@id": "$project"
      }
    },
    {
      "@id": "?sourceSubmission",
      "nias-o:workflowSubject": {
        "@id": "$project"
      }
    }
  ]
}
```

Use this template with these schema inputs:

| Query ID | `$reviewedSchema` |
| --- | --- |
| `approved-pdd-a-validation-reviews` | `https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxA-1.0.0` |
| `approved-pdd-b-validation-reviews` | `https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxB-9.0.0` |
| `approved-pdd-c-validation-reviews` | `https://nova.org.za/novaimpactaccountingstandard/document-schema/PDDxC-4.0.0` |

## Indicator Concepts

Purpose: populate indicator selectors in PDD-B and monitoring report workflows.

```json
{
  "@context": "dataRequirements/fluree/context.jsonld",
  "from": "$FLUREE_LEDGER",
  "select": {
    "?indicator": [
      "skos:prefLabel",
      "skos:definition",
      "skos:inScheme"
    ]
  },
  "where": [
    {
      "@id": "?indicator",
      "@type": "skos:Concept",
      "skos:inScheme": {
        "@id": "$scheme"
      }
    }
  ]
}
```

## Methodologies By Knowledge Domain

Purpose: populate methodology selectors by domain.

```json
{
  "@context": "dataRequirements/fluree/context.jsonld",
  "from": "$FLUREE_LEDGER",
  "select": {
    "?methodology": [
      "skos:prefLabel",
      "dcterms:title",
      "skos:broader",
      "skos:inScheme"
    ]
  },
  "where": [
    {
      "@id": "?methodology",
      "@type": "skos:Concept",
      "skos:broader": {
        "@id": "$knowledgeDomain"
      }
    }
  ]
}
```

## Eligible PDD-CIR Artifacts

Purpose: return a single project-level gate summary for the workflow shell.

The service should call `approved-pdd-a-validation-reviews`,
`approved-pdd-b-validation-reviews`, and `approved-pdd-c-validation-reviews`,
then accept the gate only if each query returns at least one distinct approved
review and the selected three review documents are not the same artifact.

The returned normalized gate record should match
`dataRequirements/shape2flutter/pdd-workflow-gate.md`.
