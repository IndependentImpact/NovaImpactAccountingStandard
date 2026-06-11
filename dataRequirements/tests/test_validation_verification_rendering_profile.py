import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
VALIDATION_PROFILE = (
    REPO_ROOT
    / "dataRequirements/document-rendering/validation-report-rendering-profile.md"
)
VERIFICATION_PROFILE = (
    REPO_ROOT
    / "dataRequirements/document-rendering/verification-report-rendering-profile.md"
)
ARCHIVED_COMBINED_PROFILE = (
    REPO_ROOT
    / "dataRequirements/document-rendering/archive/validation-verification-report-rendering-profile.md"
)


def _front_matter_and_body(profile_path: Path):
    text = profile_path.read_text(encoding="utf-8")
    marker = "---\n"
    if not text.startswith(marker):
        raise AssertionError("Profile must start with YAML front matter.")
    end = text.find("\n---\n", len(marker))
    if end == -1:
        raise AssertionError("Profile YAML front matter must be closed.")
    return text[len(marker) : end], text[end + len("\n---\n") :]


class ValidationRenderingProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.front_matter, cls.body = _front_matter_and_body(VALIDATION_PROFILE)

    def test_profile_declares_validation_identity_and_sidecars(self):
        self.assertIn("profile: nias-validation-report-rendering-profile", self.front_matter)
        self.assertIn("documentType: Validation Report", self.front_matter)
        self.assertIn("validation-report.metadata.jsonld", self.front_matter)
        self.assertIn("validation-report.validation.json", self.front_matter)
        self.assertNotIn("verification-report.metadata.jsonld", self.front_matter)
        self.assertNotIn("verification-report.validation.json", self.front_matter)

    def test_profile_declares_numbered_validation_structure(self):
        required_headings = [
            "## Section 1. Global PDD Evaluation",
            "### 1.1 Document-Level PDD Qualitative Evaluation",
            "## Section 2. PDD Section-Level Evaluation (Guiding Questions)",
            "## Section 3. PDD Paragraph-Level Validation Findings",
            "## Section 4. Validation VVS Requirement Coverage",
        ]
        for heading in required_headings:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.body)

    def test_rendering_map_references_validation_ui_shape_pattern(self):
        self.assertIn("GlobalQualitativeDocumentReviewUiShape", self.body)
        self.assertIn("DocumentFieldReviewUiShape", self.body)
        self.assertNotIn("VerifiedImpactCertificateIssuanceRequestReviewUiShape", self.body)


class VerificationRenderingProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.front_matter, cls.body = _front_matter_and_body(VERIFICATION_PROFILE)

    def test_profile_declares_verification_identity_and_sidecars(self):
        self.assertIn("profile: nias-verification-report-rendering-profile", self.front_matter)
        self.assertIn("documentType: Verification Report", self.front_matter)
        self.assertIn("verification-report.metadata.jsonld", self.front_matter)
        self.assertIn("verification-report.validation.json", self.front_matter)
        self.assertNotIn("validation-report.metadata.jsonld", self.front_matter)
        self.assertNotIn("validation-report.validation.json", self.front_matter)

    def test_profile_declares_numbered_verification_structure(self):
        required_headings = [
            "## Section 1. Global Monitoring Report Evaluation",
            "### 1.1 Document-Level Monitoring Report Qualitative Evaluation",
            "## Section 2. Monitoring Report Section-Level Evaluation (Guiding Questions)",
            "## Section 3. Monitoring Report Paragraph-Level Verification Findings",
            "## Section 4. Verification VVS Requirement Coverage",
        ]
        for heading in required_headings:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.body)

    def test_rendering_map_references_verification_ui_shape_pattern(self):
        self.assertIn("VerifiedImpactCertificateIssuanceRequestReviewUiShape", self.body)
        self.assertIn("ReviewTargetUiShape", self.body)
        self.assertNotIn("GlobalQualitativeDocumentReviewUiShape", self.body)


class ArchivedCombinedRenderingProfileTests(unittest.TestCase):
    def test_combined_profile_is_archived_with_pointer_note(self):
        text = ARCHIVED_COMBINED_PROFILE.read_text(encoding="utf-8")
        self.assertIn("Archived Combined Validation/Verification Rendering Profile", text)
        self.assertIn("validation-report-rendering-profile.md", text)
        self.assertIn("verification-report-rendering-profile.md", text)


if __name__ == "__main__":
    unittest.main()
