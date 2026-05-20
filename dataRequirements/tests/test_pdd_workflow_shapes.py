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
    REPO_ROOT / "dataRequirements/document-reference-shapes.ttl",
    REPO_ROOT / "dataRequirements/report-shapes.ttl",
    REPO_ROOT / "dataRequirements/stakeholder-engagement-shapes.ttl",
    REPO_ROOT / "dataRequirements/review-shapes.ttl",
    REPO_ROOT / "dataRequirements/pdd-certificate-shapes.ttl",
]

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

FIXTURES = REPO_ROOT / "dataRequirements/fixtures/pdd-workflow"


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


class PddWorkflowShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shapes_graph = _load_graph(SHAPE_FILES)
        cls.ontology_graph = _load_graph(ONTOLOGY_FILES)

    def _assert_fixture(self, fixture_name: str, expected: bool):
        data_graph = Graph()
        data_graph.parse(FIXTURES / fixture_name)

        conforms, _, validation_text = validate(
            data_graph=data_graph,
            shacl_graph=self.shapes_graph,
            ont_graph=self.ontology_graph,
            inference="none",
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

    def test_pdd_section_a_valid(self):
        self._assert_fixture("pdd-section-a-valid.ttl", expected=True)

    def test_pdd_section_b_valid(self):
        self._assert_fixture("pdd-section-b-valid.ttl", expected=True)

    def test_pdd_section_c_valid(self):
        self._assert_fixture("pdd-section-c-valid.ttl", expected=True)

    def test_pdd_section_review_valid(self):
        self._assert_fixture("pdd-section-review-valid.ttl", expected=True)

    def test_pdd_cir_valid(self):
        self._assert_fixture("pdd-cir-valid.ttl", expected=True)

    def test_pdd_section_a_missing_party_invalid(self):
        self._assert_fixture("pdd-section-a-invalid-missing-party.ttl", expected=False)

    def test_pdd_section_b_missing_impact_invalid(self):
        self._assert_fixture("pdd-section-b-invalid-missing-impact.ttl", expected=False)


if __name__ == "__main__":
    unittest.main()
