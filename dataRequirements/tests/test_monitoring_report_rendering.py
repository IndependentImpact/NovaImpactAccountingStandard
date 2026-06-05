import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "dataRequirements/document-rendering/tool/render_monitoring_report_markdown.py"
FIXTURES = REPO_ROOT / "dataRequirements/document-rendering/fixtures"
INPUT = FIXTURES / "monitoring-report-input.jsonld"
INVALID_STRUCTURAL = FIXTURES / "monitoring-report-invalid-structural.jsonld"
ARTIFACT_ANCHOR_SHAPES = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"
ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]
SHA256_HASH_PATTERN = r"^sha256:[a-f0-9]{64}$"


class MonitoringReportRenderingTests(unittest.TestCase):
    def _base_command(self):
        return [sys.executable, str(SCRIPT)]

    def _render_blank(self):
        completed = subprocess.run(
            self._base_command(),
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        return completed.stdout

    def _render_draft(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--input-jsonld",
                str(INPUT),
                "--source-artifact-id",
                "monitoring-report-input.jsonld",
                "--generated-at",
                "2026-05-28T00:00:00Z",
                "--render-mode",
                "draft",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        return completed.stdout

    def test_blank_template_contains_expected_monitoring_sections(self):
        rendered = self._render_blank()

        self.assertIn("## Monitoring Report", rendered)
        self.assertIn("## Report Envelope", rendered)
        self.assertIn("## Monitoring Period", rendered)
        self.assertIn("## Measured Impact Observation", rendered)
        self.assertIn("## Dataset Evidence", rendered)
        self.assertIn("## Calculation Resources", rendered)
        self.assertIn("**[required]**", rendered)

    def test_draft_rendering_contains_monitoring_content(self):
        rendered = self._render_draft()

        self.assertIn("renderMode: draft", rendered)
        self.assertIn("| monitoring-report | MonitoringReport-6.0.0 | monitoring-party-1 | pdd-version-1 |", rendered)
        self.assertIn("| monitoring-report | Tonnes of CO2e avoided | 2026-01-01T00:00:00Z | 2026-03-31T23:59:59Z |", rendered)
        self.assertIn("| monitoring-report | impact-observation | indicator-co2e-avoided | 123.45 | TONNE |", rendered)
        self.assertIn("ipfs://bafycalculationreport", rendered)

    def test_final_rendering_accepts_conformant_input(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--input-jsonld",
                str(INPUT),
                "--source-artifact-id",
                "monitoring-report-input.jsonld",
                "--generated-at",
                "2026-05-28T00:00:00Z",
                "--render-mode",
                "final",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

        self.assertIn("renderMode: final", completed.stdout)
        self.assertIn("reportType: monitoring", completed.stdout)
        self.assertIn("pdd-version-1", completed.stdout)

    def test_final_rendering_rejects_structurally_invalid_input(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--input-jsonld",
                str(INVALID_STRUCTURAL),
                "--render-mode",
                "final",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )

        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("structurally conformant Monitoring Report input", completed.stderr)
        self.assertIn("A monitoring report must reference the validated PDD version", completed.stderr)

    def test_final_export_writes_deterministic_markdown_and_sidecars(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "exported"
            subprocess.run(
                [
                    *self._base_command(),
                    "--input-jsonld",
                    str(INPUT),
                    "--source-artifact-id",
                    "monitoring-report-input.jsonld",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "markdown",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            markdown = output_dir / "monitoring-report.md"
            metadata = output_dir / "monitoring-report.metadata.jsonld"
            validation = output_dir / "monitoring-report.validation.json"

            self.assertTrue(markdown.exists())
            self.assertTrue(metadata.exists())
            self.assertTrue(validation.exists())
            self.assertIn("## Monitoring Report", markdown.read_text(encoding="utf-8"))

            metadata_payload = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertEqual(metadata_payload["nias:reportType"], "monitoring")
            self.assertEqual(
                [artifact["artifact"] for artifact in metadata_payload["nias:artifacts"]],
                ["markdown"],
            )
            anchors = metadata_payload["nias:artifactAnchor"]
            self.assertEqual(len(anchors), 7)
            self.assertEqual(anchors[0]["nias:anchorKey"], "monitoring.packageSummary")
            self.assertEqual(anchors[-1]["nias:anchorKey"], "monitoring.workflowEvidence")
            for anchor in anchors:
                with self.subTest(anchor=anchor["nias:anchorKey"]):
                    self.assertEqual(anchor["@type"], "nias:ArtifactAnchor")
                    self.assertEqual(
                        anchor["dcterms:isPartOf"]["@id"],
                        metadata_payload["@id"],
                    )
                    self.assertRegex(anchor["nias:contentHash"], SHA256_HASH_PATTERN)

            metadata_graph = Graph()
            metadata_graph.parse(metadata, format="json-ld")
            shape_graph = Graph()
            shape_graph.parse(ARTIFACT_ANCHOR_SHAPES)
            ontology_graph = Graph()
            for ontology_path in ONTOLOGY_FILES:
                ontology_graph.parse(ontology_path)
            conforms, _, validation_text = validate(
                data_graph=metadata_graph,
                shacl_graph=shape_graph,
                ont_graph=ontology_graph,
                inference="none",
                abort_on_first=False,
                allow_infos=False,
                allow_warnings=False,
                advanced=True,
            )
            self.assertTrue(conforms, msg=validation_text)

            validation_payload = json.loads(validation.read_text(encoding="utf-8"))
            self.assertEqual(validation_payload["status"], "passed")
            self.assertEqual(validation_payload["renderMode"], "final")
            self.assertEqual(validation_payload["reportType"], "monitoring")


if __name__ == "__main__":
    unittest.main()
