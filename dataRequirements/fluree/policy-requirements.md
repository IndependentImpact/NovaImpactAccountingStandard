# Fluree Policy Requirements

This document defines access-control and workflow-gate requirements before
writing Fluree policy transactions.

Fluree policy syntax supports policy data in the ledger, the `f` vocabulary,
the `?$identity` variable, and policy values supplied at query time. The exact
policy transactions should be implemented after the application identity model
is finalized.

## Actors

| Actor | Canonical representation | Required capabilities |
| --- | --- | --- |
| Standard administrator | `nias-o:PlatformUser` with administrative role data | Bootstrap and update standard artifacts. |
| Project developer | `nias-o:PlatformUser` | Create and submit PDD-A, PDD-B, PDD-C, and PDD-CIR documents for their project. |
| PDD validator | `nias-o:PlatformUser` | Read assigned submitted PDD documents and create validation reviews. |
| Registry recipient | `infocomm:CommunicationParty` | Receive workflow submissions and certificate requests. |
| Public reader | unauthenticated or public identity | Read public, unencrypted standard artifacts and public project artifacts only. |

## Identity Requirements

- Every authenticated user must resolve to one `nias-o:PlatformUser`.
- The DID or Fluree identity used in request headers must be linked to that
  platform user.
- Workflow submissions must carry `nias-o:workflowDocumentSubmittedBy`.
- The policy layer must compare `nias-o:workflowDocumentSubmittedBy` with the
  authenticated platform user for write operations.

## Write Requirements

| Operation | Required rule |
| --- | --- |
| Bootstrap standard artifacts | Only standard administrators can write ontology, concept scheme, document schema, and canonical SHACL artifacts. |
| Submit PDD-A, PDD-B, PDD-C | A project developer can submit documents only for projects they control or are authorized to represent. |
| Submit validation review | A PDD validator can submit a `nias-o:GenericDocumentReview` only for an assigned submitted PDD document. |
| Submit PDD-CIR | A project developer can submit PDD-CIR only after the PDD-CIR gate returns approved PDD-A, PDD-B, and PDD-C review references. |
| Modify submitted documents | Submitted immutable artifacts should not be modified; corrections should create successor documents or new submissions. |
| Write generated references | `nias-o:DocumentReference` values used in workflow documents must point to existing ledger artifacts or accepted off-ledger artifacts indexed by the ledger. |

## Read Requirements

- Standard ontology, concept schemes, document schema resources, and SHACL
  shapes should be readable by all application users.
- Public, unencrypted project artifacts may be readable according to platform
  publication rules.
- Encrypted documents should expose metadata required for workflow routing, but
  not decrypted payload content.
- Validator read access should be scoped to assigned workflow subjects.
- Developer read access should include their own project documents and review
  results for those documents.

## PDD-CIR Gate Requirement

The PDD-CIR gate is defined in
`dataRequirements/shape2flutter/pdd-workflow-gate.md`.

Before a PDD-CIR transaction is accepted, the service or policy layer must
prove:

- the PDD-CIR has one A, one B, and one C validation review reference;
- each reference resolves by IPFS URI and message ID;
- each resolved review is a `nias-o:GenericDocumentReview`;
- each resolved review has `nias-o:finalReviewDecision` equal to
  `nias-cs:review-approve`;
- each review has `nias-o:isReviewOf` pointing to a submitted PDD document;
- reviewed document schemas are PDDxA, PDDxB, and PDDxC respectively;
- the PDD-CIR, reviews, and reviewed documents share the same
  `nias-o:workflowSubject`;
- the three review references resolve to distinct review documents.

## Candidate Policy Shapes

These are requirements, not final policy transactions:

- `nias:policy/bootstrap-standard-artifacts` - permits standard artifact writes
  only for administrators.
- `nias:policy/pdd-developer-submit` - permits PDD section submissions by
  authorized project developers.
- `nias:policy/pdd-validator-review` - permits validation review submissions by
  assigned validators.
- `nias:policy/pdd-cir-gate` - blocks PDD-CIR writes unless the approved review
  set exists.
- `nias:policy/document-immutability` - blocks in-place mutation of submitted
  document artifacts.
- `nias:policy/encrypted-document-read` - restricts encrypted payload access.

## Open Decisions

- Whether PDD validator assignment is represented as standard ontology data,
  platform application data, or both.
- Whether conflict-of-interest rules are part of NIAS itself or an
  Independent Impact operational policy.
- Whether the PDD-CIR gate is best implemented as Fluree write policy, service
  preflight validation, or both.
- How public/private/encrypted document visibility maps to VC-backed document
  access in the platform.
