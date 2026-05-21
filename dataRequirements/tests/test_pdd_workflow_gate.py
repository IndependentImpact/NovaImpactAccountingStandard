import unittest
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
REVIEW_APPROVE = URIRef(f"{NIAS}review-approve")
REVIEW_REJECT = URIRef(f"{NIAS}review-reject")

GATE_EXPECTATIONS = {
    NIAS.pddSectionAValidationReview: PDD_A_SCHEMA,
    NIAS.pddSectionBValidationReview: PDD_B_SCHEMA,
    NIAS.pddSectionCValidationReview: PDD_C_SCHEMA,
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


def _resolve_review_reference(graph, reference_node):
    ipfs_uri = graph.value(reference_node, NIAS.resourceIpfsUri)
    message_id = graph.value(reference_node, NIAS.documentMessageId)
    if ipfs_uri is None or message_id is None:
        return None, "reference is missing resourceIpfsUri or documentMessageId"

    candidates = [
        document
        for document in graph.subjects(NIAS.resourceIpfsUri, ipfs_uri)
        if (document, RDF.type, DATA.Document) in graph
        and (document, RDF.type, NIAS.GenericDocumentReview) in graph
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


def pdd_cir_gate_errors(graph, pdd_cir):
    errors = []
    cir_subject = _workflow_subject(graph, pdd_cir)
    if cir_subject is None:
        errors.append("PDD-CIR has no workflow subject")

    resolved_reviews = {}
    for reference_property, expected_schema in GATE_EXPECTATIONS.items():
        label = str(reference_property).split("/")[-1]
        references = list(graph.objects(pdd_cir, reference_property))
        if len(references) != 1:
            errors.append(f"{label} must have exactly one DocumentReference")
            continue

        review_document, resolution_error = _resolve_review_reference(graph, references[0])
        if resolution_error:
            errors.append(f"{label}: {resolution_error}")
            continue

        resolved_reviews[reference_property] = review_document

        if graph.value(review_document, NIAS.finalReviewDecision) != REVIEW_APPROVE:
            errors.append(f"{label}: review document is not approved")

        if _workflow_subject(graph, review_document) != cir_subject:
            errors.append(f"{label}: review workflow subject does not match PDD-CIR")

        reviewed_documents = list(graph.objects(review_document, NIAS.isReviewOf))
        if len(reviewed_documents) != 1:
            errors.append(f"{label}: review must identify exactly one reviewed PDD document")
            continue

        reviewed_document = reviewed_documents[0]
        if graph.value(reviewed_document, NIAS.documentSchema) != expected_schema:
            errors.append(f"{label}: reviewed document has the wrong PDD section schema")

        if _workflow_subject(graph, reviewed_document) != cir_subject:
            errors.append(f"{label}: reviewed document workflow subject does not match PDD-CIR")

    if len(set(resolved_reviews.values())) != len(resolved_reviews):
        errors.append("PDD-CIR review references must resolve to three distinct reviews")

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


if __name__ == "__main__":
    unittest.main()
