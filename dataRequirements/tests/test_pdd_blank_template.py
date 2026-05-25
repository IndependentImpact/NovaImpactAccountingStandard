import subprocess
import sys
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "dataRequirements/document-rendering/tool/render_pdd_markdown.py"
FIXTURE = REPO_ROOT / "dataRequirements/document-rendering/fixtures/pdd-blank-template.md"


class PddBlankTemplateTests(unittest.TestCase):
    def _render_template(self):
        completed = subprocess.run(
            [sys.executable, str(SCRIPT)],
            check=True,
            capture_output=True,
            text=True,
            cwd=REPO_ROOT,
        )
        return completed.stdout

    def test_generated_blank_template_matches_fixture(self):
        self.assertEqual(
            self._render_template(),
            FIXTURE.read_text(encoding="utf-8"),
        )

    def test_generated_blank_template_has_required_optional_markers(self):
        rendered = self._render_template()
        self.assertIn("**[required]**", rendered)
        self.assertIn("**[optional]**", rendered)

    def test_generated_blank_template_keeps_core_pdd_headings(self):
        rendered = self._render_template()
        self.assertIn("## Section A. Description Of Project", rendered)
        self.assertIn("## Section B. Impact Claims And Monitoring", rendered)
        self.assertIn("## Section C. Stakeholder Engagement", rendered)


if __name__ == "__main__":
    unittest.main()
