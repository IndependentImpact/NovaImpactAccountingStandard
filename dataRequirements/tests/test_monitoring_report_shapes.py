import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]

SHAPE_FILES = [
    REPO_ROOT / "dataRequirements/common-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-reference-shapes.ttl",
    REPO_ROOT / "dataRequirements/document-shapes.ttl",
    REPO_ROOT / "dataRequirements/monitoring-report-shapes.ttl",
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


class MonitoringReportShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.shapes_graph = _load_graph(SHAPE_FILES)
        cls.ontology_graph = _load_graph(ONTOLOGY_FILES)

    def test_legacy_monitoring_report_fixture_conforms(self):
        data_graph = Graph()
        data_graph.parse(FIXTURES / "monitoring-report.ttl")

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

        self.assertTrue(conforms, msg=validation_text)


if __name__ == "__main__":
    unittest.main()
