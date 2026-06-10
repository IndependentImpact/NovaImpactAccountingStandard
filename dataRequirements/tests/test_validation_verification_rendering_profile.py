import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE = (
    REPO_ROOT
    / "dataRequirements/document-rendering/validation-verification-report-rendering-profile.md"
)


def _front_matter_and_body():
    text = PROFILE.read_text(encoding="utf-8")
    marker = "---\n"
    if not text.startswith(marker):
        raise AssertionError("Profile must start with YAML front matter.")
    end = text.find("\n---\n", len(marker))
    if end == -1:
        raise AssertionError("Profile YAML front matter must be closed.")
    return text[len(marker) : end], text[end + len("\n---\n") :]


class ValidationVerificationRenderingProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        _, cls.body = _front_matter_and_body()

    def test_profile_declares_numbered_validation_structure(self):
        required_headings = [
            "## Section 1. Global Evaluation",
            "### 1.1 Document-Level Qualitative Evaluation",
            "## Section 2. Section-Level Evaluation (Guiding Questions)",
            "## Section 3. Paragraph-Level Validation Findings",
            "## Section 4. VVS Requirement Coverage Summary",
        ]
        for heading in required_headings:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.body)

    def test_profile_declares_global_section_and_paragraph_directives(self):
        required_directives = [
            "{{ render: review.decisionRegister }}",
            "{{ render: review.documentQualitativeEvaluation }}",
            "{{ render: review.sectionQualitativeEvaluation }}",
            "{{ render: review.fieldFindings }}",
            "{{ render: vvs.requirementCoverage }}",
        ]
        for directive in required_directives:
            with self.subTest(directive=directive):
                self.assertIn(directive, self.body)

    def test_rendering_map_references_validation_ui_shape_pattern(self):
        self.assertIn("GlobalQualitativeDocumentReviewUiShape", self.body)
        self.assertIn("DocumentFieldReviewUiShape", self.body)
        self.assertIn("Section 3. Paragraph-Level Validation Findings", self.body)


if __name__ == "__main__":
    unittest.main()
