import unittest
from datetime import datetime
from pathlib import Path

from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import RDF


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE = REPO_ROOT / "dataRequirements/fixtures/pdd-workflow/pdd-cir-gate-approved.ttl"

DATA = Namespace("https://jellyfiiish.xyz/ns/")
HEDERA = Namespace("https://hashgraphontology.xyz/core/")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")

PDD_CIR = URIRef(f"{NIAS}requests/pdd-alpha-cir")
PDD_A_SCHEMA = URIRef(f"{NIAS}document-schema/PDDxA-1.0.0")
PDD_B_SCHEMA = URIRef(f"{NIAS}document-schema/PDDxB-9.0.0")
PDD_C_SCHEMA = URIRef(f"{NIAS}document-schema/PDDxC-4.0.0")
PDD_SECTION_QUAL_SCHEMA = URIRef(f"{NIAS}document-schema/PDDxSectionQualitative-1.0.0")
PDD_DOCUMENT_QUAL_SCHEMA = URIRef(f"{NIAS}document-schema/PDDx-1.0.0")
REVIEW_APPROVE = URIRef(f"{NIAS}review-approve")
REVIEW_REJECT = URIRef(f"{NIAS}review-reject")

GATE_EXPECTATIONS = {
    NIAS.pddSectionAValidationReview: {
        "schema": PDD_A_SCHEMA,
        "review_class": NIAS.GenericDocumentReview,
    },
    NIAS.pddSectionBValidationReview: {
        "schema": PDD_B_SCHEMA,
        "review_class": NIAS.GenericDocumentReview,
    },
    NIAS.pddSectionCValidationReview: {
        "schema": PDD_C_SCHEMA,
        "review_class": NIAS.GenericDocumentReview,
    },
    NIAS.pddSectionQualitativeReview: {
        "schema": PDD_SECTION_QUAL_SCHEMA,
        "review_class": NIAS.GlobalQualitativeDocumentReview,
    },
    NIAS.pddDocumentLevelQualitativeReview: {
        "schema": PDD_DOCUMENT_QUAL_SCHEMA,
        "review_class": NIAS.GlobalQualitativeDocumentReview,
    },
}


def _workflow_subject(graph, document):
    submission = graph.value(document, NIAS.hasWorkflowSubmission)
    if submission is None:
        return None
    return graph.value(submission, NIAS.workflowSubject)


def _document_message_id(graph, document):
    submission = graph.value(document, NIAS.hasWorkflowSubmission)
    if submission is None:
        return None

    message = graph.value(submission, NIAS.workflowSubmissionConsensusMessage)
    if message is None:
        return None

    topic = graph.value(message, HEDERA.inTopic)
    topic_id = graph.value(topic, HEDERA.hasTopicId) if topic is not None else None
    timestamp = graph.value(message, HEDERA.hasConsensusTimestamp)
    if topic_id is None or timestamp is None:
        return None

    return f"{topic_id}-{timestamp}"


def _resolve_review_reference(graph, reference_node, expected_review_class):
    ipfs_uri = graph.value(reference_node, NIAS.resourceIpfsUri)
    message_id = graph.value(reference_node, NIAS.documentMessageId)
    if ipfs_uri is None or message_id is None:
        return None, "reference is missing resourceIpfsUri or documentMessageId"

    candidates = [
        document
        for document in graph.subjects(NIAS.resourceIpfsUri, ipfs_uri)
        if (document, RDF.type, DATA.Document) in graph
        and (document, RDF.type, expected_review_class) in graph
    ]
    matches = [
        document
        for document in candidates
        if _document_message_id(graph, document) == str(message_id)
    ]

    if len(matches) == 1:
        return matches[0], None
    if not matches:
        return None, f"no review document resolved for {message_id} / {ipfs_uri}"
    return None, f"ambiguous review reference for {message_id} / {ipfs_uri}"


def _consensus_timestamp(graph, document):
    submission = graph.value(document, NIAS.hasWorkflowSubmission)
    if submission is None:
        return None
    message = graph.value(submission, NIAS.workflowSubmissionConsensusMessage)
    if message is None:
        return None
    timestamp = graph.value(message, HEDERA.hasConsensusTimestamp)
    if timestamp is None:
        return None
    try:
        return datetime.fromisoformat(str(timestamp).replace("Z", "+00:00"))
    except ValueError:
        return None


def _latest_document_timestamp(graph, workflow_subject, document_schema):
    latest = None
    for document in graph.subjects(NIAS.documentSchema, document_schema):
        if (document, RDF.type, DATA.Document) not in graph:
            continue
        if _workflow_subject(graph, document) != workflow_subject:
            continue
        timestamp = _consensus_timestamp(graph, document)
        if timestamp is None:
            continue
        if latest is None or timestamp > latest:
            latest = timestamp
    return latest


def _review_errors(graph, review_document, expected_schema, cir_subject):
    errors = []
    if graph.value(review_document, NIAS.finalReviewDecision) != REVIEW_APPROVE:
        errors.append("review document is not approved")

    if _workflow_subject(graph, review_document) != cir_subject:
        errors.append("review workflow subject does not match PDD-CIR")

    reviewed_documents = list(graph.objects(review_document, NIAS.isReviewOf))
    if len(reviewed_documents) != 1:
        errors.append("review must identify exactly one reviewed PDD document")
        return errors

    reviewed_document = reviewed_documents[0]
    if graph.value(reviewed_document, NIAS.documentSchema) != expected_schema:
        errors.append("reviewed document has the wrong PDD section schema")

    if _workflow_subject(graph, reviewed_document) != cir_subject:
        errors.append("reviewed document workflow subject does not match PDD-CIR")

    reviewed_timestamp = _consensus_timestamp(graph, reviewed_document)
    latest_timestamp = _latest_document_timestamp(graph, cir_subject, expected_schema)
    if (
        reviewed_timestamp is not None
        and latest_timestamp is not None
        and reviewed_timestamp < latest_timestamp
    ):
        errors.append("reviewed document is stale for this PDD section")

    return errors


def pdd_cir_gate_errors(graph, pdd_cir):
    errors = []
    cir_subject = _workflow_subject(graph, pdd_cir)
    if cir_subject is None:
        errors.append("PDD-CIR has no workflow subject")

    resolved_reviews = {}
    for reference_property, expectation in GATE_EXPECTATIONS.items():
        expected_schema = expectation["schema"]
        expected_review_class = expectation["review_class"]
        label = str(reference_property).split("/")[-1]
        references = list(graph.objects(pdd_cir, reference_property))
        if not references:
            errors.append(f"{label} must have at least one DocumentReference")
            continue

        candidate_errors = []
        accepted_review = None
        for reference in references:
            review_document, resolution_error = _resolve_review_reference(
                graph, reference, expected_review_class
            )
            if resolution_error:
                candidate_errors.append(resolution_error)
                continue
            review_errors = _review_errors(
                graph, review_document, expected_schema, cir_subject
            )
            if review_errors:
                candidate_errors.extend(review_errors)
                continue
            accepted_review = review_document
            break

        if accepted_review is None:
            if candidate_errors:
                for error in dict.fromkeys(candidate_errors):
                    errors.append(f"{label}: {error}")
            else:
                errors.append(f"{label}: no approved review resolved from references")
            continue

        resolved_reviews[reference_property] = accepted_review

    if len(set(resolved_reviews.values())) != len(resolved_reviews):
        errors.append("PDD-CIR review references must resolve to five distinct reviews")

    return errors


class PddWorkflowGateTests(unittest.TestCase):
    def setUp(self):
        self.graph = Graph()
        self.graph.parse(FIXTURE)

    def test_approved_review_set_unblocks_pdd_cir(self):
        self.assertEqual([], pdd_cir_gate_errors(self.graph, PDD_CIR))

    def test_rejected_review_blocks_pdd_cir(self):
        section_b_review = URIRef(f"{NIAS}reviews/pdd-alpha-section-b-review")
        self.graph.remove((section_b_review, NIAS.finalReviewDecision, REVIEW_APPROVE))
        self.graph.add((section_b_review, NIAS.finalReviewDecision, REVIEW_REJECT))

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddSectionBValidationReview: review document is not approved",
            errors,
        )

    def test_missing_review_target_blocks_pdd_cir(self):
        section_c_review = URIRef(f"{NIAS}reviews/pdd-alpha-section-c-review")
        section_c_document = URIRef(f"{NIAS}documents/pdd-alpha-section-c")
        self.graph.remove((section_c_review, NIAS.isReviewOf, section_c_document))

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddSectionCValidationReview: review must identify exactly one reviewed PDD document",
            errors,
        )

    def test_wrong_section_schema_blocks_pdd_cir(self):
        section_b_document = URIRef(f"{NIAS}documents/pdd-alpha-section-b")
        self.graph.remove((section_b_document, NIAS.documentSchema, PDD_B_SCHEMA))
        self.graph.add((section_b_document, NIAS.documentSchema, PDD_A_SCHEMA))

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddSectionBValidationReview: reviewed document has the wrong PDD section schema",
            errors,
        )

    def test_message_id_mismatch_blocks_pdd_cir(self):
        reference = self.graph.value(PDD_CIR, NIAS.pddSectionAValidationReview)
        self.graph.remove((reference, NIAS.documentMessageId, None))
        self.graph.add(
            (reference, NIAS.documentMessageId, Literal("0.0.1001-2026-01-09T00:00:00Z"))
        )

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddSectionAValidationReview: no review document resolved for "
            "0.0.1001-2026-01-09T00:00:00Z / ipfs://bafypddsectionareview",
            errors,
        )

    def test_multiple_section_references_allow_valid_latest_review(self):
        stale_review = URIRef(f"{NIAS}reviews/pdd-alpha-section-a-review-v0")
        stale_submission = URIRef(f"{NIAS}submissions/pdd-alpha-section-a-review-v0")
        stale_doc = URIRef(f"{NIAS}documents/pdd-alpha-section-a-v0")
        stale_doc_submission = URIRef(f"{NIAS}submissions/pdd-alpha-section-a-v0")
        stale_reference = URIRef(f"{NIAS}references/pdd-alpha-section-a-review-v0")

        self.graph.add((stale_doc, RDF.type, DATA.Document))
        self.graph.add((stale_doc, NIAS.documentSchema, PDD_A_SCHEMA))
        self.graph.add((stale_doc, NIAS.hasWorkflowSubmission, stale_doc_submission))
        self.graph.add((stale_doc_submission, NIAS.workflowSubject, NIAS["projects/pdd-alpha"]))
        self.graph.add((stale_doc_submission, NIAS.workflowSubmissionConsensusMessage, URIRef(f"{NIAS}messages/pdd-a-v0")))
        self.graph.add((URIRef(f"{NIAS}messages/pdd-a-v0"), HEDERA.inTopic, URIRef(f"{NIAS}topics/pdd")))
        self.graph.add((URIRef(f"{NIAS}topics/pdd"), HEDERA.hasTopicId, Literal("0.0.1001")))
        self.graph.add(
            (URIRef(f"{NIAS}messages/pdd-a-v0"), HEDERA.hasConsensusTimestamp, Literal("2025-12-31T00:00:00Z"))
        )

        self.graph.add((stale_review, RDF.type, DATA.Document))
        self.graph.add((stale_review, RDF.type, NIAS.GenericDocumentReview))
        self.graph.add((stale_review, NIAS.resourceIpfsUri, Literal("ipfs://bafypddsectionareviewv0")))
        self.graph.add((stale_review, NIAS.hasWorkflowSubmission, stale_submission))
        self.graph.add((stale_submission, NIAS.workflowSubject, NIAS["projects/pdd-alpha"]))
        self.graph.add((stale_submission, NIAS.workflowSubmissionConsensusMessage, URIRef(f"{NIAS}messages/pdd-a-review-v0")))
        self.graph.add((URIRef(f"{NIAS}messages/pdd-a-review-v0"), HEDERA.inTopic, URIRef(f"{NIAS}topics/pdd")))
        self.graph.add((URIRef(f"{NIAS}messages/pdd-a-review-v0"), HEDERA.hasConsensusTimestamp, Literal("2026-01-03T12:00:00Z")))
        self.graph.add((stale_review, NIAS.finalReviewDecision, REVIEW_APPROVE))
        self.graph.add((stale_review, NIAS.isReviewOf, stale_doc))

        self.graph.add((stale_reference, NIAS.documentMessageId, Literal("0.0.1001-2026-01-03T12:00:00Z")))
        self.graph.add((stale_reference, NIAS.resourceIpfsUri, Literal("ipfs://bafypddsectionareviewv0")))
        self.graph.add((PDD_CIR, NIAS.pddSectionAValidationReview, stale_reference))

        self.assertEqual([], pdd_cir_gate_errors(self.graph, PDD_CIR))

    def test_stale_only_reference_blocks_pdd_cir(self):
        section_a_reference = self.graph.value(PDD_CIR, NIAS.pddSectionAValidationReview)
        self.graph.remove((PDD_CIR, NIAS.pddSectionAValidationReview, section_a_reference))

        stale_review = URIRef(f"{NIAS}reviews/pdd-alpha-section-a-review-v0")
        stale_submission = URIRef(f"{NIAS}submissions/pdd-alpha-section-a-review-v0")
        stale_doc = URIRef(f"{NIAS}documents/pdd-alpha-section-a-v0")
        stale_doc_submission = URIRef(f"{NIAS}submissions/pdd-alpha-section-a-v0")
        stale_reference = URIRef(f"{NIAS}references/pdd-alpha-section-a-review-v0")

        self.graph.add((stale_doc, RDF.type, DATA.Document))
        self.graph.add((stale_doc, NIAS.documentSchema, PDD_A_SCHEMA))
        self.graph.add((stale_doc, NIAS.hasWorkflowSubmission, stale_doc_submission))
        self.graph.add((stale_doc_submission, NIAS.workflowSubject, NIAS["projects/pdd-alpha"]))
        self.graph.add((stale_doc_submission, NIAS.workflowSubmissionConsensusMessage, URIRef(f"{NIAS}messages/pdd-a-v0")))
        self.graph.add((URIRef(f"{NIAS}messages/pdd-a-v0"), HEDERA.inTopic, URIRef(f"{NIAS}topics/pdd")))
        self.graph.add((URIRef(f"{NIAS}topics/pdd"), HEDERA.hasTopicId, Literal("0.0.1001")))
        self.graph.add(
            (URIRef(f"{NIAS}messages/pdd-a-v0"), HEDERA.hasConsensusTimestamp, Literal("2025-12-31T00:00:00Z"))
        )

        self.graph.add((stale_review, RDF.type, DATA.Document))
        self.graph.add((stale_review, RDF.type, NIAS.GenericDocumentReview))
        self.graph.add((stale_review, NIAS.resourceIpfsUri, Literal("ipfs://bafypddsectionareviewv0")))
        self.graph.add((stale_review, NIAS.hasWorkflowSubmission, stale_submission))
        self.graph.add((stale_submission, NIAS.workflowSubject, NIAS["projects/pdd-alpha"]))
        self.graph.add((stale_submission, NIAS.workflowSubmissionConsensusMessage, URIRef(f"{NIAS}messages/pdd-a-review-v0")))
        self.graph.add((URIRef(f"{NIAS}messages/pdd-a-review-v0"), HEDERA.inTopic, URIRef(f"{NIAS}topics/pdd")))
        self.graph.add((URIRef(f"{NIAS}messages/pdd-a-review-v0"), HEDERA.hasConsensusTimestamp, Literal("2026-01-03T12:00:00Z")))
        self.graph.add((stale_review, NIAS.finalReviewDecision, REVIEW_APPROVE))
        self.graph.add((stale_review, NIAS.isReviewOf, stale_doc))

        self.graph.add((stale_reference, NIAS.documentMessageId, Literal("0.0.1001-2026-01-03T12:00:00Z")))
        self.graph.add((stale_reference, NIAS.resourceIpfsUri, Literal("ipfs://bafypddsectionareviewv0")))
        self.graph.add((PDD_CIR, NIAS.pddSectionAValidationReview, stale_reference))

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddSectionAValidationReview: reviewed document is stale for this PDD section",
            errors,
        )

    def test_missing_global_review_layer_blocks_pdd_cir(self):
        reference = self.graph.value(PDD_CIR, NIAS.pddDocumentLevelQualitativeReview)
        self.graph.remove((PDD_CIR, NIAS.pddDocumentLevelQualitativeReview, reference))

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddDocumentLevelQualitativeReview must have at least one DocumentReference",
            errors,
        )

    def test_global_review_wrong_subject_blocks_pdd_cir(self):
        submission = URIRef(
            f"{NIAS}submissions/pdd-alpha-document-qualitative-review"
        )
        self.graph.remove((submission, NIAS.workflowSubject, NIAS["projects/pdd-alpha"]))
        self.graph.add((submission, NIAS.workflowSubject, NIAS["projects/pdd-beta"]))

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddDocumentLevelQualitativeReview: review workflow subject does not match PDD-CIR",
            errors,
        )

    def test_global_review_wrong_artifact_schema_blocks_pdd_cir(self):
        reviewed_doc = URIRef(f"{NIAS}documents/pdd-alpha-package")
        self.graph.remove((reviewed_doc, NIAS.documentSchema, PDD_DOCUMENT_QUAL_SCHEMA))
        self.graph.add((reviewed_doc, NIAS.documentSchema, PDD_B_SCHEMA))

        errors = pdd_cir_gate_errors(self.graph, PDD_CIR)

        self.assertIn(
            "pddDocumentLevelQualitativeReview: reviewed document has the wrong PDD section schema",
            errors,
        )


if __name__ == "__main__":
    unittest.main()
