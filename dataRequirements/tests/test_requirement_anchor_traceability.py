import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Literal, Namespace, URIRef
from rdflib.namespace import DCTERMS, RDF


REPO_ROOT = Path(__file__).resolve().parents[2]

FIXTURE = REPO_ROOT / "dataRequirements/fixtures/vvs/requirement-anchor-traceability.ttl"
ARTIFACT_ANCHOR_SHAPES = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"
REQUIREMENT_COVERAGE_PROOF_SHAPES = (
    REPO_ROOT / "dataRequirements/requirement-coverage-proof-shapes.ttl"
)
EXACT_MAPPING = REPO_ROOT / "dataRequirements/mappings/vvs-requirement-anchor-map.ttl"
ANCHOR_DEFINITION_FILES = [
    REPO_ROOT / "dataRequirements/mappings/pdd-anchor-definitions.ttl",
    REPO_ROOT / "dataRequirements/mappings/monitoring-anchor-definitions.ttl",
    REPO_ROOT / "dataRequirements/mappings/dlr-anchor-definitions.ttl",
]
ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]
VVS_REQUIREMENTS = REPO_ROOT / "glossary/ValidationVerificationStandard.ttl"

DATA = Namespace("https://jellyfiiish.xyz/ns/")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
TRACE = Namespace(
    "https://nova.org.za/novaimpactaccountingstandard/fixtures/requirement-anchor-traceability/"
)

PDD_ARTIFACT = URIRef(f"{TRACE}pdd-submission-v1")
DLR_ARTIFACT = URIRef(f"{TRACE}dlr-submission-v1")
MONITORING_ARTIFACT = URIRef(f"{TRACE}monitoring-submission-v1")


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


class RequirementAnchorTraceabilityFixtureTest(unittest.TestCase):
    """Submitted artifact anchor traceability for exact VVS mappings."""

    @classmethod
    def setUpClass(cls):
        cls.fixture_graph = _load_graph([FIXTURE])
        cls.anchor_graph = _load_graph(ANCHOR_DEFINITION_FILES)
        cls.mapping_graph = _load_graph([EXACT_MAPPING])
        cls.vvs_graph = _load_graph([VVS_REQUIREMENTS])

        cls.fixture_with_anchor_definitions = Graph()
        for graph in [cls.fixture_graph, cls.anchor_graph]:
            for triple in graph:
                cls.fixture_with_anchor_definitions.add(triple)

        cls.proof_graph = Graph()
        for graph in [
            cls.fixture_graph,
            cls.anchor_graph,
            cls.mapping_graph,
            cls.vvs_graph,
        ]:
            for triple in graph:
                cls.proof_graph.add(triple)

    def _single_value(self, graph: Graph, subject, predicate):
        values = list(graph.objects(subject, predicate))
        self.assertEqual(
            len(values),
            1,
            msg=f"{subject} must declare exactly one {predicate}.",
        )
        return values[0]

    def _field_reviews_for_anchor(self, artifact_anchor, mandate):
        matches = []
        for review_target in self.fixture_graph.subjects(
            NIAS.reviewedAnchor,
            artifact_anchor,
        ):
            for field_review in self.fixture_graph.subjects(
                NIAS.reviewTarget,
                review_target,
            ):
                for review in self.fixture_graph.subjects(
                    NIAS.fieldReview,
                    field_review,
                ):
                    if (review, NIAS.reviewMandate, mandate) in self.fixture_graph:
                        matches.append((review, field_review, review_target))
        return matches

    def _expected_artifact_for_anchor_key(self, anchor_key: str):
        if anchor_key.startswith("pdd."):
            return PDD_ARTIFACT
        if anchor_key.startswith("dlr."):
            return DLR_ARTIFACT
        if anchor_key.startswith("monitoring."):
            return MONITORING_ARTIFACT
        self.fail(f"Unexpected anchor key prefix in {anchor_key}")

    def test_traceability_fixture_parses(self):
        self.assertGreater(len(self.fixture_graph), 0)

    def test_submitted_artifact_anchors_and_review_targets_conform(self):
        conforms, _, validation_text = validate(
            data_graph=self.fixture_with_anchor_definitions,
            shacl_graph=_load_graph([ARTIFACT_ANCHOR_SHAPES]),
            ont_graph=_load_graph(ONTOLOGY_FILES),
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )
        self.assertTrue(conforms, msg=validation_text)

    def test_fixture_covers_pdd_dlr_and_monitoring_submitted_artifacts(self):
        reviewed_artifacts = set(
            self.fixture_graph.objects(None, NIAS.reviewedArtifact)
        )
        self.assertTrue(
            {PDD_ARTIFACT, DLR_ARTIFACT, MONITORING_ARTIFACT}.issubset(
                reviewed_artifacts
            )
        )
        for artifact in [PDD_ARTIFACT, DLR_ARTIFACT, MONITORING_ARTIFACT]:
            with self.subTest(artifact=artifact):
                self.assertIn((artifact, RDF.type, DATA.Document), self.fixture_graph)
                for predicate in [
                    NIAS.artifactContentCid,
                    NIAS.artifactSchemaCid,
                    NIAS.submissionTopicId,
                    NIAS.submissionConsensusTimestamp,
                ]:
                    self.assertIn((artifact, predicate, None), self.fixture_graph)

    def test_every_exact_mapping_traces_to_reviewed_submitted_content(self):
        mappings = set(self.mapping_graph.subjects(RDF.type, NIAS.RequirementMapping))
        self.assertGreater(len(mappings), 0)

        for mapping in sorted(mappings, key=str):
            requirement = self._single_value(
                self.mapping_graph,
                mapping,
                NIAS.mappedRequirement,
            )
            schema_anchor = self._single_value(
                self.mapping_graph,
                mapping,
                NIAS.mappedAnchor,
            )
            mapped_shape = self._single_value(
                self.mapping_graph,
                mapping,
                NIAS.mappedShape,
            )
            mandate = self._single_value(
                self.mapping_graph,
                mapping,
                NIAS.reviewMandate,
            )
            anchor_key = str(
                self._single_value(self.anchor_graph, schema_anchor, NIAS.anchorKey)
            )

            with self.subTest(mapping=mapping):
                self.assertIn(
                    (requirement, NIAS.implementedByShape, mapped_shape),
                    self.vvs_graph,
                )

                artifact_anchors = list(
                    self.fixture_graph.subjects(NIAS.anchorDefinition, schema_anchor)
                )
                self.assertGreater(
                    len(artifact_anchors),
                    0,
                    msg=(
                        f"{mapping} must trace to at least one concrete "
                        f"ArtifactAnchor for {schema_anchor}."
                    ),
                )

                for artifact_anchor in artifact_anchors:
                    concrete_anchor_key = self._single_value(
                        self.fixture_graph,
                        artifact_anchor,
                        NIAS.anchorKey,
                    )
                    self.assertEqual(str(concrete_anchor_key), anchor_key)

                    reviewed_artifact = self._single_value(
                        self.fixture_graph,
                        artifact_anchor,
                        DCTERMS.isPartOf,
                    )
                    self.assertEqual(
                        reviewed_artifact,
                        self._expected_artifact_for_anchor_key(anchor_key),
                    )

                    for predicate in [
                        NIAS.artifactContentCid,
                        NIAS.artifactSchemaCid,
                        NIAS.submissionTopicId,
                        NIAS.submissionConsensusTimestamp,
                    ]:
                        self.assertIn(
                            (reviewed_artifact, predicate, None),
                            self.fixture_graph,
                            msg=(
                                f"Submitted artifact {reviewed_artifact} must carry "
                                f"simulated identity field {predicate}."
                            ),
                        )

                    field_reviews = self._field_reviews_for_anchor(
                        artifact_anchor,
                        mandate,
                    )
                    self.assertGreater(
                        len(field_reviews),
                        0,
                        msg=(
                            f"{mapping} must trace from mapped schema anchor to a "
                            "field review with the same review mandate."
                        ),
                    )

                    for _, field_review, review_target in field_reviews:
                        self.assertEqual(
                            self._single_value(
                                self.fixture_graph,
                                review_target,
                                NIAS.reviewedArtifact,
                            ),
                            reviewed_artifact,
                        )
                        reviewed_content = self._single_value(
                            self.fixture_graph,
                            field_review,
                            NIAS.originalResponse,
                        )
                        self.assertTrue(str(reviewed_content).strip())

    def test_requirement_coverage_proofs_conform_to_shacl(self):
        shape_graph = _load_graph(
            [
                ARTIFACT_ANCHOR_SHAPES,
                REQUIREMENT_COVERAGE_PROOF_SHAPES,
            ]
        )
        conforms, _, validation_text = validate(
            data_graph=self.proof_graph,
            shacl_graph=shape_graph,
            ont_graph=_load_graph(ONTOLOGY_FILES),
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )
        self.assertTrue(conforms, msg=validation_text)

    def test_every_exact_mapping_has_one_materialized_coverage_proof(self):
        mappings = set(self.mapping_graph.subjects(RDF.type, NIAS.RequirementMapping))
        for mapping in mappings:
            with self.subTest(mapping=mapping):
                proofs = list(
                    self.fixture_graph.subjects(
                        NIAS.coverageRequirementMapping,
                        mapping,
                    )
                )
                self.assertEqual(
                    len(proofs),
                    1,
                    msg=f"{mapping} must have exactly one materialized coverage proof.",
                )

    def test_coverage_proof_shape_rejects_inconsistent_copied_values(self):
        proof = URIRef(f"{TRACE}proof-req-pdd-002-declared-impacts")
        invalid_graph = Graph()
        for triple in self.proof_graph:
            invalid_graph.add(triple)
        invalid_graph.remove((proof, NIAS.coverageAnchorKey, None))
        invalid_graph.add((proof, NIAS.coverageAnchorKey, Literal("pdd.sectionB.wrongAnchor")))

        shape_graph = _load_graph(
            [
                ARTIFACT_ANCHOR_SHAPES,
                REQUIREMENT_COVERAGE_PROOF_SHAPES,
            ]
        )
        conforms, _, validation_text = validate(
            data_graph=invalid_graph,
            shacl_graph=shape_graph,
            ont_graph=_load_graph(ONTOLOGY_FILES),
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )
        self.assertFalse(conforms)
        self.assertIn("anchor key and title must match", validation_text)


if __name__ == "__main__":
    unittest.main()
