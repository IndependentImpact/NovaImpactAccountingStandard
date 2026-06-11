# Is an Explicit Workflow Construct Necessary?

## The Question

When a series of forms are interlinked — specifically where a later form
requires proof that a preceding form was successfully completed (for example, by
referencing its Hedera message ID or IPFS address) — do we need an explicit
`nias-o:Workflow` / `nias-o:WorkflowStep` construct, or can sequencing be
enforced purely through predecessor references?

---

## What the Standard Already Provides

### Predecessor References in Document Headers

The reusable `#DocumentHeaders&1.0.0` schema already captures:

- `id_msg_pred` — the Hedera message ID of the predecessor document.
- `url_ipfs_pred` — the IPFS URI of the predecessor document.
- `id_msg_lic` — the Hedera message ID of the submitter's license.
- `url_ipfs_lic` — the IPFS URI of the submitter's license.
- `id_subject` / `type_subject` — the entity (project or agent) that the
  document concerns.

These headers already create a verifiable chain: a SHACL shape for a later
document can require that `id_msg_pred` resolves to a document of a specific
type, meaning the system can enforce sequencing without any explicit workflow
object at all.

The README states this directly:

> "If it is required that actions be performed in a specific sequence, this is
> enforced by making a reference to the resulting artefact of a preceding step a
> requirement in a subsequent step."

### The Existing Workflow Classes

The ontology currently defines:

- `nias-o:Workflow` — a named set of steps that must be executed to achieve an
  outcome (`rdfs:subClassOf aiao:Control`).
- `nias-o:WorkflowStep` — a single step within a workflow
  (`rdfs:subClassOf aiao:Control`).
- `nias-o:WorkflowDocumentSubmission` — records which document was submitted to
  which step of which workflow for which subject, and by whom.

---

## The Core Argument: Predecessor References Are Sufficient for Sequencing

Sequence enforcement does not require an explicit workflow object. Consider the
Project and PDD (Project Design Document) workflow as a concrete example:

| Step | Document Schema | Prerequisite |
|------|----------------|--------------|
| 1 | Project Listing Application (`#PLA&1.0.0`) | None |
| 2 | PDD Section A (`#PDDxA&1.0.0`) | Approved PLA |
| 3 | PDD Section B (`#PDDxB&9.0.0`) | Approved PDDxA |
| 4 | PDD Section C (`#PDDxC&4.0.0`) | Approved PDDxB |
| 5 | PDD Certificate Issuance Request (`#PDDCIR&3.0.0`) | Approved PDDxC |
| 6 | Project Registration Request (`#ProjectRegistrationRequest&1.0.0`) | Approved PDDCIR |

Each step's SHACL shape can require that the predecessor reference in the
document headers points to a document of the correct type and with an approved
status. No named `nias-o:Workflow` or `nias-o:WorkflowStep` resource is needed
to enforce this chain. The predecessor link *is* the workflow, in a distributed
and content-addressed form.

This approach has several advantages:

1. **Simplicity.** Forms do not need to know which named workflow they belong
   to. They only need to reference the document they depend on.
2. **Composability.** The same form (for example, a monitoring report) can
   appear in multiple sequences without being duplicated or linked to a specific
   named workflow.
3. **Verifiability.** Every link in the chain is a content-addressed reference
   (Hedera message ID or IPFS URI), making the entire sequence auditable without
   consulting a central workflow registry.
4. **Alignment with the data model.** The SHACL migration path already notes
   that predecessor and license references should be used to enforce workflow
   sequence.

---

## What the Workflow Classes Still Provide

Even if predecessor references are sufficient for sequencing, the existing
workflow classes are not without value.

### Accountability and Audit Trail

`nias-o:WorkflowDocumentSubmission` records:

- which document was submitted,
- to which named workflow and step,
- for which subject (project or agent), and
- by which platform user.

This is an audit and accountability layer, not a sequencing layer. It answers
questions such as "Who submitted the monitoring report for project X?" and "Was
this document submitted under the correct license scope?". This record has value
independent of whether the workflow enforces any sequence.

### Grouping and Process Visibility

A named `nias-o:Workflow` resource can group all the steps of a recognised
process (for example, the Project and PDD Workflow, the License Application
Workflow, or the Verified Impact Certificate Workflow). This grouping is useful:

- for platform dashboards that need to show progress through a process,
- for standards that define multiple parallel or alternative sequences, and
- for compliance reporting that must name the process followed.

### Compatibility With Existing Data

The reference R functions and existing JSON-LD payloads already emit
`nias-o:workflow` and `nias-o:workflowStep` properties. Removing these classes
would require migrating all historical data and changing the existing
transformation logic.

---

## Conclusion: A Minimal Workflow Construct Is Justified

The answer to the question in the issue title is:

> **An explicit workflow is not needed to enforce sequencing.** Predecessor
> references encoded in document headers are sufficient for that purpose, and
> SHACL shapes can validate the chain without any named workflow object.

However, a **minimal** workflow construct remains useful for:

- accountability (recording who submitted what, under which license, to which
  named process step),
- process visibility (grouping steps into a recognisable named process), and
- compatibility with existing data and tooling.

The recommended approach is therefore:

1. **Use predecessor references as the primary sequencing mechanism.** Each
   SHACL shape for a step-N document should require that the predecessor
   reference resolves to an approved step-(N-1) document of the expected type.
   This is sufficient to enforce order without a workflow registry.

2. **Keep `nias-o:WorkflowDocumentSubmission` as a lightweight accountability
   wrapper.** It records the submitter, the subject, and a Hedera message ID for
   the submission event itself. This is distinct from the document content and
   its predecessor chain.

3. **Make `nias-o:Workflow` and `nias-o:WorkflowStep` optional metadata.**
   Forms within a standard may carry a workflow and step label for platform
   display and audit purposes, but the presence of these labels should not be
   what enforces order. The predecessor reference does that.

4. **Do not require a central workflow registry.** Any document schema that
   names a workflow and step should treat those names as controlled vocabulary
   labels (SKOS concepts or IRI-identified resources), not as live state
   machines that block submission. The state machine lives in the SHACL
   validation of predecessor references.

This keeps the workflow concept minimal, avoids coupling form submission to a
centralised workflow engine, and preserves the verifiability and composability
that content-addressed predecessor references provide.
