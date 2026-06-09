import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = REPO_ROOT / "GenerateStandardText/tool/generate_skos_markdown.py"
GLOSSARY_DIR = REPO_ROOT / "glossary"

# Mapping of TTL input → (expected heading, expected scheme label, expected term)
TTL_FIXTURES = [
    (
        GLOSSARY_DIR / "NovaImpactAccountingStandardGlossary.ttl",
        "## Glossary",
        "Document authenticity proof mechanisms",
        "Verifiable credential",
    ),
    (
        GLOSSARY_DIR / "Principle.ttl",
        "## Principles",
        "Impact principles",
        "Purposefulness",
    ),
    (
        GLOSSARY_DIR / "GuidingReviewQuestions.ttl",
        "## Guiding And Review Questions",
        "Guiding and review question catalog",
        "GQ-001",
    ),
    (
        GLOSSARY_DIR / "ReputationRules.ttl",
        "## Reputation Lifecycle Terms",
        "Reputation lifecycle terms",
        "KSR gain",
    ),
    (
        GLOSSARY_DIR / "ScoringRules.ttl",
        "## Scoring Rules",
        "Scoring model terms",
        "ActSco",
    ),
    (
        GLOSSARY_DIR / "ValidationVerificationStandard.ttl",
        "## Requirement Status",
        "Requirement status",
        "Active",
    ),
]


class GenerateSkosMarkdownTests(unittest.TestCase):
    def _run_generator(self, ttl_path, output_path, section_heading, extra_args=None):
        cmd = [
            sys.executable,
            str(SCRIPT),
            "--ttl", str(ttl_path),
            "--output", str(output_path),
            "--section-heading", section_heading,
        ]
        if extra_args:
            cmd.extend(extra_args)
        return subprocess.run(cmd, cwd=REPO_ROOT, capture_output=True, text=True)

    def test_generates_markdown_for_all_ttl_sources(self):
        for ttl_path, heading, scheme_label, term in TTL_FIXTURES:
            with self.subTest(ttl=ttl_path.name):
                with tempfile.TemporaryDirectory() as tmp_dir:
                    output_path = Path(tmp_dir) / "out.md"
                    result = self._run_generator(ttl_path, output_path, heading)
                    self.assertEqual(result.returncode, 0, msg=result.stderr)
                    rendered = output_path.read_text(encoding="utf-8")
                    self.assertTrue(
                        rendered.startswith(heading + "\n"),
                        msg=f"Expected heading '{heading}', got:\n{rendered[:80]}",
                    )
                    self.assertIn(f"### {scheme_label}", rendered)
                    self.assertIn("| Term | Definition | IRI |", rendered)
                    self.assertIn(f"| {term} |", rendered)

    def test_check_mode_passes_when_output_is_current(self):
        ttl_path = GLOSSARY_DIR / "NovaImpactAccountingStandardGlossary.ttl"
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "out.md"
            self._run_generator(ttl_path, output_path, "## Glossary")
            result = self._run_generator(
                ttl_path, output_path, "## Glossary", extra_args=["--check"]
            )
            self.assertEqual(result.returncode, 0, msg=result.stderr)

    def test_check_mode_detects_drift(self):
        ttl_path = GLOSSARY_DIR / "NovaImpactAccountingStandardGlossary.ttl"
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "out.md"
            output_path.write_text("## Glossary\n\nOutdated content\n", encoding="utf-8")
            result = self._run_generator(
                ttl_path, output_path, "## Glossary", extra_args=["--check"]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("differs from generated output", result.stderr)

    def test_generated_tables_have_valid_headers(self):
        ttl_path = GLOSSARY_DIR / "ScoringRules.ttl"
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "out.md"
            self._run_generator(ttl_path, output_path, "## Scoring Rules")
            lines = output_path.read_text(encoding="utf-8").splitlines()
            for index, line in enumerate(lines[:-1]):
                if line == "| Term | Definition | IRI |":
                    self.assertEqual(lines[index + 1], "| --- | --- | --- |")

    def test_committed_generated_files_are_current(self):
        committed_outputs = [
            (
                GLOSSARY_DIR / "NovaImpactAccountingStandardGlossary.ttl",
                REPO_ROOT / "GenerateStandardText/02-a-Glossary.md",
                "## Glossary",
            ),
            (
                GLOSSARY_DIR / "Principle.ttl",
                REPO_ROOT / "GenerateStandardText/03-a-Principles.md",
                "## Principles",
            ),
            (
                GLOSSARY_DIR / "GuidingReviewQuestions.ttl",
                REPO_ROOT / "GenerateStandardText/03-b-GuidingAndReviewQuestions.md",
                "## Guiding And Review Questions",
            ),
            (
                GLOSSARY_DIR / "ReputationRules.ttl",
                REPO_ROOT / "GenerateStandardText/04-a-KnowledgeAndSkillsReputationRules.md",
                "## Reputation Lifecycle Terms",
            ),
            (
                GLOSSARY_DIR / "ScoringRules.ttl",
                REPO_ROOT / "GenerateStandardText/05-a-ScoringRules.md",
                "## Scoring Rules",
            ),
            (
                GLOSSARY_DIR / "ValidationVerificationStandard.ttl",
                REPO_ROOT / "GenerateStandardText/VVS-RequirementStatus.md",
                "## Requirement Status",
            ),
        ]
        for ttl_path, committed_path, heading in committed_outputs:
            with self.subTest(output=committed_path.name):
                self.assertTrue(
                    committed_path.exists(),
                    msg=f"Committed output missing: {committed_path}",
                )
                result = self._run_generator(
                    ttl_path, committed_path, heading, extra_args=["--check"]
                )
                self.assertEqual(
                    result.returncode,
                    0,
                    msg=f"{committed_path.name} is out of date. Run generate_all.sh to regenerate.\n{result.stderr}",
                )


if __name__ == "__main__":
    unittest.main()
