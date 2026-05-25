import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "dataRequirements/document-rendering/tool/render_pdd_markdown.py"
INPUT = REPO_ROOT / "dataRequirements/document-rendering/fixtures/pdd-alpha-input.jsonld"
FIXTURE = REPO_ROOT / "dataRequirements/document-rendering/fixtures/pdd-alpha-rendered.md"


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
        self.assertIn("## Section A. Description Of Project", rendered)
        self.assertIn("## Section B. Impact Claims And Monitoring", rendered)
        self.assertIn("## Section C. Stakeholder Engagement", rendered)
        self.assertIn("Facility: Community-led mangrove nursery", rendered)
        self.assertIn("(Intentional, Beneficial)", rendered)
        self.assertIn("| Unit | kWh |", rendered)

    def test_filled_rendering_body_has_no_raw_json(self):
        rendered = self._render_filled()
        body = rendered.split("\n---\n", 1)[1]
        self.assertNotIn('{"', body)
        self.assertNotIn('["', body)


if __name__ == "__main__":
    unittest.main()
