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
            encoding="utf-8",
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
        self.assertIn("# Nova Impact Accounting Standard", rendered)
        self.assertIn("## Project Design Document", rendered)
        self.assertIn("## Table Of Contents", rendered)
        self.assertIn("## Section A. Description Of Project", rendered)
        self.assertIn("## Section B. Impact Claims And Monitoring", rendered)
        self.assertIn("## Section C. Stakeholder Engagement", rendered)

    def test_generated_blank_template_has_title_page_table(self):
        rendered = self._render_template()
        self.assertNotIn("| Standard | Nova Impact Accounting Standard |", rendered)
        self.assertNotIn("| Project title | _[required: project title]_ |", rendered)
        self.assertIn("| Methodology and version | _[required: methodology reference(s)]_ |", rendered)
        self.assertIn(
            "| Section A. Description Of Project | \\pageref{section-a.-description-of-project} |",
            rendered,
        )
        self.assertNotIn("- [Section A. Description Of Project]", rendered)

    def test_document_metadata_is_not_rendered_in_pdd_sections(self):
        rendered = self._render_template()
        section_a = rendered.split("## Section A. Description Of Project", 1)[1].split(
            "## Appendix A. Document And Process Metadata", 1
        )[0]
        appendix = rendered.split("## Appendix A. Document And Process Metadata", 1)[1]
        self.assertNotIn("Document IPFS URI", section_a)
        self.assertNotIn("Document schema IRI", section_a)
        self.assertNotIn("Encrypted", section_a)
        self.assertNotIn("Authenticity proof", section_a)
        self.assertIn("Document IPFS URI", appendix)
        self.assertIn("Authenticity proof", appendix)


if __name__ == "__main__":
    unittest.main()
