import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_SCRIPT = REPO_ROOT / "dataRequirements/shape2flutter/check-pdd-workflow.sh"
README = REPO_ROOT / "dataRequirements/document-rendering/README.md"


class PddRenderingRegressionCommandTests(unittest.TestCase):
    def test_workflow_regression_script_runs_explicit_rendering_suite(self):
        script = CHECK_SCRIPT.read_text(encoding="utf-8")
        self.assertIn('log_step "Run PDD Markdown rendering regression tests"', script)
        self.assertIn('PYTHON_BIN="${PYTHON3_BIN:-python3}"', script)
        self.assertRegex(
            script,
            re.compile(
                r'"\$PYTHON_BIN" -m unittest discover\s+\\\n'
                r'\s+-s "\$ROOT_DIR/dataRequirements/tests" \\\n'
                r'\s+-p "test_pdd_\*\.py" \\\n'
                r'\s+-q'
            ),
        )

    def test_rendering_readme_covers_local_workflow_commands(self):
        readme = README.read_text(encoding="utf-8")
        required_snippets = [
            "render_pdd_markdown.py",
            "--render-mode final",
            "--output-target pdf",
            "export_pdd_workflow_markdown.py",
            "check-pdd-workflow.sh",
            "test_pdd_output_compilation.py",
        ]
        for snippet in required_snippets:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, readme)


if __name__ == "__main__":
    unittest.main()
