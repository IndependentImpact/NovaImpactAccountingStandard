# PDD Workflow Gate Contract

This document defines the application-level gate that unlocks the PDD
certificate issuance request after PDD-A, PDD-B, and PDD-C validation.

The canonical SHACL shapes validate each document payload. The workflow gate is
different: it resolves references across submitted ledger artifacts and checks
whether those artifacts are approved reviews of the correct PDD section for the
same workflow subject.

## Gate Inputs

The gate receives:

- A candidate `nias-o:PddCertificateIssuanceRequest` document.
- One or more `nias-o:DocumentReference` values on:
  - `nias-o:pddSectionAValidationReview`.
  - `nias-o:pddSectionBValidationReview`.
  - `nias-o:pddSectionCValidationReview`.
- Ledger-resolved review documents referenced by those values.
- Ledger-resolved source PDD documents linked from each review by
  `nias-o:isReviewOf`.

## Required Review Set

The PDD-CIR can proceed only when the review references resolve to this set:

| PDD-CIR property | Review class | Reviewed document schema | Required decision |
| --- | --- | --- | --- |
| `nias-o:pddSectionAValidationReview` | `nias-o:GenericDocumentReview` | `document-schema/PDDxA-1.0.0` | `nias-cs:review-approve` |
| `nias-o:pddSectionBValidationReview` | `nias-o:GenericDocumentReview` | `document-schema/PDDxB-9.0.0` | `nias-cs:review-approve` |
| `nias-o:pddSectionCValidationReview` | `nias-o:GenericDocumentReview` | `document-schema/PDDxC-4.0.0` | `nias-cs:review-approve` |

## Gate Checks

For each section reference, the workflow shell or Fluree-backed service must:

1. Resolve the `DocumentReference` using `nias-o:resourceIpfsUri` and the
   ledger's message-id index for `nias-o:documentMessageId`.
2. Confirm the resolved artifact is a `data:Document` and a
   `nias-o:GenericDocumentReview`.
3. Confirm `nias-o:finalReviewDecision` is `nias-cs:review-approve`.
4. Follow `nias-o:isReviewOf` to the reviewed PDD document.
5. Confirm the reviewed document has the expected `nias-o:documentSchema` for
   that section.
6. Confirm the PDD-CIR, the review document, and the reviewed PDD document have
   the same `nias-o:workflowSubject` in their `nias-o:hasWorkflowSubmission`
   records.
7. Confirm the reviewed PDD document is the latest known artifact for that
   workflow subject and section schema (stale links fail).
8. Confirm the three resolved review documents are distinct.

The gate must accept multiple candidate references per section and pass when at
least one candidate resolves to an approved, current review for the expected
section. The gate fails if references are missing, unresolved, ambiguous,
rejected, stale, incomplete, linked to the wrong section schema, linked to a
different workflow subject, or duplicated across sections.

## Runtime Result

A successful gate returns a normalized review set to the PDD-CIR form:

```json
{
  "pddSectionAValidationReview": {
    "document": "https://nova.org.za/novaimpactaccountingstandard/reviews/...",
    "documentMessageId": "0.0.1001-2026-01-04T00:00:00Z",
    "resourceIpfsUri": "ipfs://..."
  },
  "pddSectionBValidationReview": {
    "document": "https://nova.org.za/novaimpactaccountingstandard/reviews/...",
    "documentMessageId": "0.0.1001-2026-01-05T00:00:00Z",
    "resourceIpfsUri": "ipfs://..."
  },
  "pddSectionCValidationReview": {
    "document": "https://nova.org.za/novaimpactaccountingstandard/reviews/...",
    "documentMessageId": "0.0.1001-2026-01-06T00:00:00Z",
    "resourceIpfsUri": "ipfs://..."
  }
}
```

The generated `PddCertificateIssuanceRequestUiShape` can then write the three
`DocumentReference` values, but the workflow shell is responsible for ensuring
that the values came from this gate rather than from unchecked free text.

## SHACL Boundary

This gate is intentionally not encoded as ordinary canonical SHACL today.
`DocumentReference` values are compact references, not embedded review
documents, so their approval status depends on ledger lookup. The canonical
SHACL can validate the PDD-CIR reference fields and the review document fields
individually, while this contract validates the cross-document workflow state.

If the Fluree deployment later exposes materialized approved-review resources,
this gate can be enforced by a Fluree transaction policy or service query using
the same canonical IRIs.
