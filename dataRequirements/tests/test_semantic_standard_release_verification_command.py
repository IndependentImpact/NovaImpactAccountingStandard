import os
import subprocess
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
CHECK_SCRIPT = REPO_ROOT / "dataRequirements/check-semantic-standard-release.sh"
RELEASE_PACKAGE_DOC = (
    REPO_ROOT / "dataRequirements/releases/1.0.0/semantic-standard-release-package.md"
)

EXPECTED_MODULES = [
    "dataRequirements.tests.test_semantic_standard_release_package",
    "dataRequirements.tests.test_concept_schemes",
    "dataRequirements.tests.test_phase7_validation",
    "dataRequirements.tests.test_vvs_requirements",
    "dataRequirements.tests.test_requirement_anchor_traceability",
    "dataRequirements.tests.test_pdd_output_compilation",
    "dataRequirements.tests.test_monitoring_report_rendering",
    "dataRequirements.tests.test_validation_verification_report_rendering",
]


class SemanticStandardReleaseVerificationCommandTests(unittest.TestCase):
    def test_verification_script_is_executable(self):
        self.assertTrue(CHECK_SCRIPT.exists())
        self.assertTrue(os.access(CHECK_SCRIPT, os.X_OK))

    def test_verification_script_lists_expected_modules(self):
        completed = subprocess.run(
            [str(CHECK_SCRIPT), "--list-modules"],
            cwd=REPO_ROOT,
            check=True,
            text=True,
            capture_output=True,
        )
        modules = [line.strip() for line in completed.stdout.splitlines() if line.strip()]
        self.assertEqual(modules, EXPECTED_MODULES)

    def test_release_package_doc_includes_verification_entry_point(self):
        content = RELEASE_PACKAGE_DOC.read_text(encoding="utf-8")
        self.assertIn("check-semantic-standard-release.sh", content)
        self.assertIn("python3 -m unittest", content)


if __name__ == "__main__":
    unittest.main()
