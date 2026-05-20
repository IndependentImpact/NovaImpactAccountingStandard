import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]

SHAPE_FILES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-reference-shapes.ttl",
    REPO_ROOT / "dataRequirements/impact-declaration-shapes.ttl",
    REPO_ROOT / "dataRequirements/license-shapes.ttl",
]

ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

FIXTURES = REPO_ROOT / "dataRequirements/fixtures/legacy"


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


class LicenseShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shapes_graph = _load_graph(SHAPE_FILES)
        cls.ontology_graph = _load_graph(ONTOLOGY_FILES)

    def _assert_valid_fixture(self, fixture_name: str):
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

        self.assertTrue(
            conforms,
            msg=f"Fixture {fixture_name} should conform.\n{validation_text}",
        )

    def test_agent_details_full_valid(self):
        self._assert_valid_fixture("agent-details-full.ttl")

    def test_license_application_valid(self):
        self._assert_valid_fixture("license-application.ttl")

    def test_license_application_review_valid(self):
        self._assert_valid_fixture("license-application-review.ttl")

    def test_agent_license_valid(self):
        self._assert_valid_fixture("agent-license.ttl")

    def test_project_registration_request_valid(self):
        self._assert_valid_fixture("project-registration-request.ttl")

    def test_methodology_applicability_valid(self):
        self._assert_valid_fixture("methodology-applicability.ttl")


if __name__ == "__main__":
    unittest.main()
