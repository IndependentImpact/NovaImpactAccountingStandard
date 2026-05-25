import re
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
PROFILE = REPO_ROOT / "dataRequirements/document-rendering/pdd-rendering-profile.md"


def _front_matter_and_body():
    text = PROFILE.read_text(encoding="utf-8")
    marker = "---\n"
    if not text.startswith(marker):
        raise AssertionError("Profile must start with YAML front matter.")
    end = text.find("\n---\n", len(marker))
    if end == -1:
        raise AssertionError("Profile YAML front matter must be closed.")
    return text[len(marker) : end], text[end + len("\n---\n") :]


def _parse_simple_front_matter(front_matter: str):
    parsed = {}
    current_list_key = None
    for raw_line in front_matter.splitlines():
        line = raw_line.rstrip()
        if not line:
            continue
        if line.startswith("  - "):
            if current_list_key is None:
                raise AssertionError(f"List item without key: {line}")
            parsed[current_list_key].append(line[4:].strip())
            continue
        current_list_key = None
        if ": " in line:
            key, value = line.split(": ", 1)
            parsed[key] = _parse_scalar(value)
            continue
        if line.endswith(":"):
            key = line[:-1]
            parsed[key] = []
            current_list_key = key
            continue
        raise AssertionError(f"Unsupported profile front matter line: {line}")
    return parsed


def _parse_scalar(value: str):
    if value == "true":
        return True
    if value == "false":
        return False
    return value


class PddRenderingProfileTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        front_matter, body = _front_matter_and_body()
        cls.metadata = _parse_simple_front_matter(front_matter)
        cls.body = body

    def test_front_matter_parses_and_identifies_profile(self):
        self.assertEqual(
            self.metadata["profile"],
            "nias-pdd-rendering-profile",
        )
        self.assertEqual(self.metadata["primaryInput"], "JSON-LD")
        self.assertEqual(self.metadata["pdfCompiler"], "pandoc")
        self.assertTrue(self.metadata["finalModeRequiresValidation"])
        self.assertEqual(
            self.metadata["repeatedParameterMode"],
            "table-per-parameter",
        )

    def test_output_targets_and_sidecars_are_declared(self):
        self.assertEqual(
            self.metadata["defaultOutputTargets"],
            ["markdown", "pdf", "html"],
        )
        self.assertEqual(
            self.metadata["sidecarOutputs"],
            ["pdd.metadata.jsonld", "pdd.validation.json"],
        )

    def test_every_pdd_workflow_section_has_rendering_entry(self):
        expected_directives = [
            "pdd.sectionA",
            "pdd.sectionB",
            "pdd.sectionC",
            "pdd.validation.sectionA",
            "pdd.validation.sectionB",
            "pdd.validation.sectionC",
            "pdd.certificateIssuanceRequest",
        ]
        for directive in expected_directives:
            with self.subTest(directive=directive):
                self.assertIn(f"{{{{ render: {directive} }}}}", self.body)

    def test_top_level_content_shapes_have_deterministic_heading_locations(self):
        expected_rows = {
            "PddSectionAReportContentUiShape": "Section A. Description Of Project",
            "ProjectDesignUiShape": "Section A.1 through Section A.5",
            "PddSectionBReportContentUiShape": "Section B. Impact Claims And Monitoring",
            "ImpactRequirementUiShape": "Section B.2 Declared Impacts",
            "DataParameterRequirementUiShape": "Section B.5 Data And Parameter Requirements",
            "PddSectionCUiShape": "Section C. Stakeholder Engagement",
            "DocumentFieldReviewUiShape": "Validation Review Summary",
            "DocumentReferenceUiShape": "PDD Certificate Issuance Request and Appendix A",
        }
        for shape, heading in expected_rows.items():
            with self.subTest(shape=shape):
                row_pattern = rf"\| `{re.escape(shape)}` \| [^|]+ \| {re.escape(heading)} \|"
                self.assertRegex(self.body, row_pattern)

    def test_profile_is_presentation_only(self):
        forbidden_terms = [
            "sh:minCount",
            "sh:maxCount",
            "sh:datatype",
            "sh:class",
            "required: true",
            "validationRule",
        ]
        profile_text = PROFILE.read_text(encoding="utf-8")
        for term in forbidden_terms:
            with self.subTest(term=term):
                self.assertNotIn(term, profile_text)

    def test_profile_body_resembles_conventional_pdd_outline(self):
        required_headings = [
            "## Section A. Description Of Project",
            "## Section B. Impact Claims And Monitoring",
            "## Section C. Stakeholder Engagement",
            "## Validation Review Summary",
            "## Appendix A. Document Metadata",
            "## Appendix B. Field-To-Predicate Map",
        ]
        for heading in required_headings:
            with self.subTest(heading=heading):
                self.assertIn(heading, self.body)


if __name__ == "__main__":
    unittest.main()
