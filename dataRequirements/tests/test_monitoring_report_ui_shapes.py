import unittest
from pathlib import Path

from rdflib import Graph, Namespace, URIRef


REPO_ROOT = Path(__file__).resolve().parents[2]
SHAPES_FILE = REPO_ROOT / "dataRequirements/shape2flutter/monitoring-report-ui-shapes.ttl"
BUILD_SCRIPT = REPO_ROOT / "dataRequirements/shape2flutter/build-monitoring-report.sh"

IND = Namespace("http://independentimpact.org/indicator-owl/")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
NIAS_UI = Namespace("https://nova.org.za/novaimpactaccountingstandard/shape2flutter/")
SH = Namespace("http://www.w3.org/ns/shacl#")
TIME = Namespace("http://www.w3.org/2006/time#")


class MonitoringReportUiShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse(SHAPES_FILE)

    def _property_paths(self, shape: URIRef):
        paths = []
        for property_shape in self.graph.objects(shape, SH.property):
            paths.append(self.graph.value(property_shape, SH.path))
        return paths

    def test_monitoring_report_ui_shape_exposes_required_capture_fields(self):
        paths = self._property_paths(NIAS_UI.MonitoringReportUiShape)

        self.assertEqual(
            paths,
            [
                NIAS.hasWorkflowSubmission,
                NIAS.alignedWithPDD,
                NIAS.reportedIndicatorLabel,
                NIAS.forPeriod,
                NIAS.reportedObservation,
                NIAS.usesDataset,
                NIAS.calculationCode,
                NIAS.impactResultResource,
                NIAS.calculationReport,
                NIAS.requestedIssuanceAccountId,
            ],
        )

    def test_nested_dataset_and_observation_shapes_are_present(self):
        self.assertEqual(
            set(self._property_paths(NIAS_UI.DatasetUiShape)),
            {URIRef("http://purl.org/dc/terms/title"), NIAS.dataLineageReview, NIAS.finalDatasetArtifact},
        )
        self.assertEqual(
            set(self._property_paths(NIAS_UI.IndicatorObservationUiShape)),
            {IND.observesIndicator, IND.obsValue, IND.hasUnit, IND.timePeriod},
        )
        self.assertEqual(
            set(self._property_paths(NIAS_UI.DateTimeIntervalUiShape)),
            {TIME.hasBeginning, TIME.hasEnd},
        )

    def test_build_script_targets_monitoring_report_bundle(self):
        script = BUILD_SCRIPT.read_text(encoding="utf-8")

        self.assertIn("monitoring-report-ui-shapes.ttl", script)
        self.assertIn("nias-shape2flutter/monitoring-report", script)
        self.assertIn("shape2flutter monitoring report output", script)


if __name__ == "__main__":
    unittest.main()
