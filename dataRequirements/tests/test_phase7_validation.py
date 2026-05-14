import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]

SHAPE_FILES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
    REPO_ROOT / "dataRequirements/project-design-shapes.ttl",
    REPO_ROOT / "dataRequirements/impact-declaration-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-shapes.ttl",
    REPO_ROOT / "dataRequirements/report-shapes.ttl",
]

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

FIXTURES = REPO_ROOT / "dataRequirements/fixtures/phase7"


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


class Phase7ValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shapes_graph = _load_graph(SHAPE_FILES)
        cls.ontology_graph = _load_graph(ONTOLOGY_FILES)

    def _assert_fixture(self, fixture_name: str, expected: bool):
        fixture_path = FIXTURES / fixture_name
        data_graph = Graph()
        data_graph.parse(fixture_path)

        conforms, _, validation_text = validate(
            data_graph=data_graph,
            shacl_graph=self.shapes_graph,
            ont_graph=self.ontology_graph,
            inference="rdfs",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )

        self.assertEqual(
            conforms,
            expected,
            msg=f"Fixture {fixture_name} expected {expected} but got {conforms}.\n{validation_text}",
        )

    def test_controlled_vocab_invalid(self):
        self._assert_fixture("impact-controlled-vocab-invalid.ttl", expected=False)

    def test_monitored_branch_valid(self):
        self._assert_fixture("impact-monitored-valid.ttl", expected=True)

    def test_unmonitored_branch_valid(self):
        self._assert_fixture("impact-unmonitored-valid.ttl", expected=True)

    def test_invalid_period_outside_crediting_period(self):
        self._assert_fixture("impact-invalid-monitoring-period.ttl", expected=False)

    def test_invalid_ipfs_uri(self):
        self._assert_fixture("document-invalid-ipfs-uri.ttl", expected=False)

    def test_invalid_namespace_iri(self):
        self._assert_fixture("document-invalid-namespace-iri.ttl", expected=False)

    def test_missing_workflow_submission_fields(self):
        self._assert_fixture("document-missing-workflow-fields.ttl", expected=False)


if __name__ == "__main__":
    unittest.main()
