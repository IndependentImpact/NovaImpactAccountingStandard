import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from rdflib import Graph


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "dataRequirements/document-rendering/tool/render_pdd_markdown.py"
INPUT = REPO_ROOT / "dataRequirements/document-rendering/fixtures/pdd-alpha-input.jsonld"
FIXTURE = REPO_ROOT / "dataRequirements/document-rendering/fixtures/pdd-alpha-rendered.md"
VALID_TTL_INPUT = REPO_ROOT / "dataRequirements/fixtures/phase7/impact-monitored-valid.ttl"


class PddFilledRenderingTests(unittest.TestCase):
    def _render_filled(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input-jsonld",
                str(INPUT),
                "--source-artifact-id",
                "pdd-alpha-input.jsonld",
                "--generated-at",
                "2026-05-25T00:00:00Z",
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

    def test_filled_rendering_matches_fixture(self):
        self.assertEqual(self._render_filled(), FIXTURE.read_text(encoding="utf-8"))

    def test_filled_rendering_includes_pdd_sections_and_labels(self):
        rendered = self._render_filled()
        self.assertIn("# Nova Impact Accounting Standard", rendered)
        self.assertIn("## Project Design Document", rendered)
        self.assertIn("## Table Of Contents", rendered)
        self.assertNotIn("| Project title | PDD Alpha Mangrove Restoration |", rendered)
        self.assertIn("| Methodology and version | Default PDD Methodology |", rendered)
        self.assertIn("## Appendix A. Document And Process Metadata", rendered)
        self.assertIn("## Section A. Description Of Project", rendered)
        self.assertIn("## Section B. Impact Claims And Monitoring", rendered)
        self.assertIn("## Section C. Stakeholder Engagement", rendered)
        self.assertNotIn("### A.1 Validation Review Summary", rendered)
        self.assertNotIn("### A.2 PDD Certificate Issuance Request", rendered)
        self.assertNotIn("pdd.validation.sectionA", rendered)
        self.assertNotIn("pdd.certificateIssuanceRequest", rendered)
        self.assertIn("#### Technology Or Measure 1", rendered)
        self.assertIn("| Type | Facility |", rendered)
        self.assertIn(
            "| Description | Community-led mangrove nursery and replanting measures. |",
            rendered,
        )
        self.assertIn("#### Declared Impact 1", rendered)
        self.assertIn("| Intentionality | Intentional |", rendered)
        self.assertIn("| Beneficial or adverse | Beneficial |", rendered)
        self.assertIn("| Unit | kWh |", rendered)

    def test_filled_rendering_uses_native_latex_toc_marker(self):
        rendered = self._render_filled()
        toc = rendered.split("## Table Of Contents", 1)[1].split("\\newpage", 1)[0]
        self.assertIn("\\tableofcontents", toc)
        self.assertNotIn("| Section | Page |", toc)
        self.assertNotRegex(toc, r"(?m)^\\s*- ")

    def test_filled_rendering_keeps_document_metadata_in_appendix(self):
        rendered = self._render_filled()
        pdd_body = rendered.split("## Section A. Description Of Project", 1)[1].split(
            "## Appendix A. Document And Process Metadata", 1
        )[0]
        appendix = rendered.split("## Appendix A. Document And Process Metadata", 1)[1]
        self.assertNotIn("Document IPFS URI", pdd_body)
        self.assertIn("| Document schema IRI | PDDxA-1.0.0 |", appendix)
        self.assertIn("| Validation status | draft (validation not enforced) |", appendix)

    def test_filled_rendering_body_has_no_raw_json(self):
        rendered = self._render_filled()
        body = rendered.split("\n---\n", 1)[1]
        self.assertNotIn('{"', body)
        self.assertNotIn('["', body)

    def test_final_rendering_rejects_non_conformant_input(self):
        completed = subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                "--input-jsonld",
                str(INPUT),
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
            "Final render mode requires SHACL-conformant input.",
            completed.stderr,
        )

    def test_final_rendering_accepts_conformant_input(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            final_input = Path(tmpdir) / "impact-monitored-valid.jsonld"
            graph = Graph()
            graph.parse(VALID_TTL_INPUT, format="turtle")
            graph.serialize(destination=final_input, format="json-ld")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input-jsonld",
                    str(final_input),
                    "--render-mode",
                    "final",
                    "--source-artifact-id",
                    "impact-monitored-valid.jsonld",
                    "--generated-at",
                    "2026-05-26T00:00:00Z",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )
            self.assertIn("renderMode: final", completed.stdout)
            self.assertIn(
                "| Validation status | final (SHACL validation passed) |",
                completed.stdout,
            )


if __name__ == "__main__":
    unittest.main()
