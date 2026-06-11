import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import SH


REPO_ROOT = Path(__file__).resolve().parents[2]

ARTIFACT_IDENTITY_CONTRACT_SHAPES = (
    REPO_ROOT / "dataRequirements/artifact-identity-contract-shapes.ttl"
)
PDD_ALPHA_FIXTURE = REPO_ROOT / "dataRequirements/document-rendering/fixtures/pdd-alpha-input.jsonld"
MONITORING_FIXTURE = (
    REPO_ROOT / "dataRequirements/document-rendering/fixtures/monitoring-report-input.jsonld"
)
VALIDATION_FIXTURE = (
    REPO_ROOT / "dataRequirements/document-rendering/fixtures/validation-report-input.jsonld"
)
VERIFICATION_FIXTURE = (
    REPO_ROOT / "dataRequirements/document-rendering/fixtures/verification-report-input.jsonld"
)
TRACEABILITY_FIXTURE = (
    REPO_ROOT / "dataRequirements/fixtures/vvs/requirement-anchor-traceability.ttl"
)
ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
TRACE = Namespace(
    "https://nova.org.za/novaimpactaccountingstandard/fixtures/requirement-anchor-traceability/"
)

PDD_SECTION_A = URIRef(f"{NIAS}reports/pdd-section-a")
MONITORING_REPORT = URIRef(f"{NIAS}rendering/monitoring-report")
VALIDATION_REVIEW = URIRef(f"{NIAS}test/vv-validation-review-1")
VERIFICATION_REVIEW = URIRef(f"{NIAS}test/vv-verification-review-1")


def _parse_format(path: Path):
    if path.suffix == ".jsonld":
        return "json-ld"
    if path.suffix == ".ttl":
        return "turtle"
    return None


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path, format=_parse_format(path))
    return graph


def _contract_shape_graph(shape, target):
    graph = _load_graph([ARTIFACT_IDENTITY_CONTRACT_SHAPES])
    graph.add((shape, SH.targetNode, target))
    return graph


def _validate_contract(data_graph, shape, target):
    return validate(
        data_graph=data_graph,
        shacl_graph=_contract_shape_graph(shape, target),
        ont_graph=_load_graph(ONTOLOGY_FILES),
        inference="none",
        abort_on_first=False,
        allow_infos=False,
        allow_warnings=False,
        advanced=True,
    )


class ArtifactIdentityContractTests(unittest.TestCase):
    def test_identity_contract_shapes_parse(self):
        graph = _load_graph([ARTIFACT_IDENTITY_CONTRACT_SHAPES])

        self.assertGreater(len(graph), 0)

    def test_submitted_pdd_artifact_identity_conforms(self):
        conforms, _, validation_text = _validate_contract(
            _load_graph([PDD_ALPHA_FIXTURE]),
            NIAS.SubmittedArtifactIdentityShape,
            PDD_SECTION_A,
        )

        self.assertTrue(conforms, msg=validation_text)

    def test_monitoring_artifact_identity_conforms_and_matches_aligned_pdd(self):
        conforms, _, validation_text = _validate_contract(
            _load_graph([MONITORING_FIXTURE]),
            NIAS.MonitoringArtifactIdentityShape,
            MONITORING_REPORT,
        )

        self.assertTrue(conforms, msg=validation_text)

    def test_validation_review_identity_conforms_against_reviewed_pdd(self):
        conforms, _, validation_text = _validate_contract(
            _load_graph([VALIDATION_FIXTURE]),
            NIAS.ReviewedArtifactIdentityShape,
            VALIDATION_REVIEW,
        )

        self.assertTrue(conforms, msg=validation_text)

    def test_verification_review_identity_conforms_against_reviewed_monitoring_report(self):
        conforms, _, validation_text = _validate_contract(
            _load_graph([VERIFICATION_FIXTURE]),
            NIAS.VerificationReviewIdentityShape,
            VERIFICATION_REVIEW,
        )

        self.assertTrue(conforms, msg=validation_text)

    def test_traceability_submitted_artifacts_conform_to_identity_contract(self):
        for artifact in [
            URIRef(f"{TRACE}pdd-submission-v1"),
            URIRef(f"{TRACE}dlr-submission-v1"),
            URIRef(f"{TRACE}monitoring-submission-v1"),
        ]:
            with self.subTest(artifact=artifact):
                conforms, _, validation_text = _validate_contract(
                    _load_graph([TRACEABILITY_FIXTURE]),
                    NIAS.SubmittedArtifactIdentityShape,
                    artifact,
                )

                self.assertTrue(conforms, msg=validation_text)

    def test_contract_rejects_incorrect_derived_submission_event_key(self):
        graph = _load_graph([PDD_ALPHA_FIXTURE])
        graph.remove((PDD_SECTION_A, NIAS.submissionEventKey, None))
        graph.add((PDD_SECTION_A, NIAS.submissionEventKey, Literal("wrong-event-key")))

        conforms, _, validation_text = _validate_contract(
            graph,
            NIAS.SubmittedArtifactIdentityShape,
            PDD_SECTION_A,
        )

        self.assertFalse(conforms)
        self.assertIn("submissionEventKey must equal", validation_text)

    def test_contract_rejects_reviewed_artifact_content_identity_mismatch(self):
        graph = _load_graph([VALIDATION_FIXTURE])
        graph.remove((VALIDATION_REVIEW, NIAS.reviewedArtifactContentCid, None))
        graph.add((VALIDATION_REVIEW, NIAS.reviewedArtifactContentCid, Literal("wrongcid")))

        conforms, _, validation_text = _validate_contract(
            graph,
            NIAS.ReviewedArtifactIdentityShape,
            VALIDATION_REVIEW,
        )

        self.assertFalse(conforms)
        self.assertIn("reviewed artifact metadata", validation_text)

    def test_contract_rejects_monitoring_aligned_pdd_identity_mismatch(self):
        graph = _load_graph([MONITORING_FIXTURE])
        graph.remove((MONITORING_REPORT, NIAS.alignedPddContentCid, None))
        graph.add((MONITORING_REPORT, NIAS.alignedPddContentCid, Literal("wrongcid")))

        conforms, _, validation_text = _validate_contract(
            graph,
            NIAS.MonitoringArtifactIdentityShape,
            MONITORING_REPORT,
        )

        self.assertFalse(conforms)
        self.assertIn("alignment identity", validation_text)


if __name__ == "__main__":
    unittest.main()
