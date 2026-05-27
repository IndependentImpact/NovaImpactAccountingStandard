import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "tooling/generate_glossary_markdown.py"
DEFAULT_TTL = REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl"


class GlossaryMarkdownGenerationTests(unittest.TestCase):
    def test_script_generates_markdown_with_expected_structure(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "glossary.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--ttl",
                    str(DEFAULT_TTL),
                    "--output",
                    str(output_path),
                ],
                check=True,
                cwd=REPO_ROOT,
            )

            rendered = output_path.read_text(encoding="utf-8")
            self.assertTrue(rendered.startswith("## Glossary\n"))
            self.assertIn("### Document authenticity proof mechanisms", rendered)
            self.assertIn("| Term | Definition | IRI |", rendered)
            self.assertIn("| Verifiable credential |", rendered)
            self.assertIn("https://nova.org.za/novaimpactaccountingstandard/vc", rendered)

    def test_script_check_mode_detects_drift(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "glossary.md"
            output_path.write_text("## Glossary\n\nOutdated\n", encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--ttl",
                    str(DEFAULT_TTL),
                    "--output",
                    str(output_path),
                    "--check",
                ],
                cwd=REPO_ROOT,
                text=True,
                capture_output=True,
                encoding="utf-8",
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("differs from generated output", completed.stderr)

    def test_generated_markdown_tables_use_valid_table_headers(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "glossary.md"
            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--ttl",
                    str(DEFAULT_TTL),
                    "--output",
                    str(output_path),
                ],
                check=True,
                cwd=REPO_ROOT,
            )
            lines = output_path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines[:-1]):
                if line == "| Term | Definition | IRI |":
                    self.assertEqual(lines[index + 1], "| --- | --- | --- |")


if __name__ == "__main__":
    unittest.main()
