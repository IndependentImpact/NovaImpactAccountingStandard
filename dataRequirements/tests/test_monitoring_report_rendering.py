import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "dataRequirements/document-rendering/tool/render_monitoring_report_markdown.py"
FIXTURES = REPO_ROOT / "dataRequirements/document-rendering/fixtures"
INPUT = FIXTURES / "monitoring-report-input.jsonld"
INVALID_STRUCTURAL = FIXTURES / "monitoring-report-invalid-structural.jsonld"
BLANK_TEMPLATE_FIXTURE = FIXTURES / "monitoring-report-blank-template.md"
RENDERED_FIXTURE = FIXTURES / "monitoring-report-rendered.md"
ARTIFACT_ANCHOR_SHAPES = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"
MONITORING_ANCHOR_DEFINITIONS = (
    REPO_ROOT / "dataRequirements/mappings/monitoring-anchor-definitions.ttl"
)
ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]
SHA256_HASH_PATTERN = r"^sha256:[a-f0-9]{64}$"
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")


class MonitoringReportRenderingTests(unittest.TestCase):
    def _canonical_anchor_keys(self, definitions_path: Path):
        graph = Graph()
        graph.parse(definitions_path, format="turtle")
        records = []
        for anchor in graph.subjects(RDF.type, NIAS.AnchorDefinition):
            key = graph.value(anchor, NIAS.anchorKey)
            order = graph.value(anchor, NIAS.renderOrder)
            if key is None:
                continue
            records.append((int(order.toPython()) if order is not None else 999999, str(key)))
        return [key for _, key in sorted(records)]

    def _write_fake_pandoc(self, path: Path):
        path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import pathlib",
                    "import sys",
                    "args = sys.argv[1:]",
                    "source = pathlib.Path(args[0])",
                    "output = pathlib.Path(args[args.index('--output') + 1])",
                    "if output.suffix == '.html':",
                    "    output.write_text('<html><body>' + source.read_text(encoding='utf-8') + '</body></html>', encoding='utf-8')",
                    "else:",
                    "    output.write_bytes(source.read_text(encoding='utf-8').encode('utf-8'))",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        path.chmod(0o755)

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

    def test_blank_template_matches_fixture(self):
        self.assertEqual(
            self._render_blank(),
            BLANK_TEMPLATE_FIXTURE.read_text(encoding="utf-8"),
        )

    def test_blank_template_contains_expected_monitoring_sections(self):
        rendered = self._render_blank()

        self.assertIn("## Monitoring Report", rendered)
        self.assertIn("## Report Envelope", rendered)
        self.assertIn("## Monitoring Period", rendered)
        self.assertIn("## Measured Impact Observation", rendered)
        self.assertIn("## Dataset Evidence", rendered)
        self.assertIn("## Calculation Resources", rendered)
        self.assertIn("**[required]**", rendered)

    def test_draft_rendering_matches_fixture(self):
        self.assertEqual(
            self._render_draft(),
            RENDERED_FIXTURE.read_text(encoding="utf-8"),
        )

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
                metadata_payload["nias:artifactContentCid"],
                "bafymonitoringartifactcontentcid",
            )
            self.assertEqual(
                metadata_payload["nias:alignedPddContentCid"],
                "bafypddartifactcontentcid",
            )
            self.assertEqual(
                metadata_payload["nias:linkedDlrContentCid"],
                "bafydlrcontentcid",
            )
            self.assertEqual(
                [artifact["artifact"] for artifact in metadata_payload["nias:artifacts"]],
                ["markdown"],
            )
            anchors = metadata_payload["nias:artifactAnchor"]
            self.assertEqual(
                [anchor["nias:anchorKey"] for anchor in anchors],
                self._canonical_anchor_keys(MONITORING_ANCHOR_DEFINITIONS),
            )
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

    def test_final_export_supports_markdown_and_pdf_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            fake_pandoc = tmp_path / "pandoc"
            self._write_fake_pandoc(fake_pandoc)
            output_dir = tmp_path / "exported"
            env = os.environ.copy()
            env["PATH"] = f"{tmp_path}{os.pathsep}{env.get('PATH', '')}"
            env["PANDOC_BIN"] = str(fake_pandoc)

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
                    "--output-target",
                    "pdf",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env=env,
            )
            self.assertTrue((output_dir / "monitoring-report.md").exists())
            pdf_bytes = (output_dir / "monitoring-report.pdf").read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
            self.assertIn(b"%%EOF", pdf_bytes[-1024:])

    def test_final_rendering_requires_linked_dlr_content_cid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            invalid = tmp_path / "monitoring-missing-dlr.jsonld"
            payload = json.loads(INPUT.read_text(encoding="utf-8"))
            report = next(
                node
                for node in payload
                if node.get("@id")
                == "https://nova.org.za/novaimpactaccountingstandard/rendering/monitoring-report"
            )
            report.pop(
                "https://nova.org.za/novaimpactaccountingstandard/linkedDlrContentCid",
                None,
            )
            invalid.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    *self._base_command(),
                    "--input-jsonld",
                    str(invalid),
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
            self.assertIn(
                "A monitoring report must include the linked DLR content CID.",
                completed.stderr,
            )


if __name__ == "__main__":
    unittest.main()
