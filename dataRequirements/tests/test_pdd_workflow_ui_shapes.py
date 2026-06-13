import unittest
from pathlib import Path

from rdflib import Graph, Namespace


REPO_ROOT = Path(__file__).resolve().parents[2]
SHAPES_FILE = REPO_ROOT / "dataRequirements/shape2flutter/pdd-workflow-ui-shapes.ttl"

CLAIM = Namespace("http://w3id.org/claimont#")
NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
NIAS_UI = Namespace("https://nova.org.za/novaimpactaccountingstandard/shape2flutter/")
SH = Namespace("http://www.w3.org/ns/shacl#")


class PddWorkflowUiShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.graph = Graph()
        cls.graph.parse(SHAPES_FILE)

    def _property_paths(self, shape):
        return [self.graph.value(prop, SH.path) for prop in self.graph.objects(shape, SH.property)]

    def test_pdd_section_a_content_omits_document_schema_field(self):
        self.assertEqual(
            self._property_paths(NIAS_UI.PddSectionAReportContentUiShape),
            [CLAIM.isMadeBy, CLAIM.hasSubject],
        )

    def test_pdd_section_b_content_omits_duplicate_identity_fields(self):
        self.assertEqual(
            self._property_paths(NIAS_UI.PddSectionBReportContentUiShape),
            [NIAS.hasDeclaredImpact, NIAS.impactClaim, NIAS.usesMethodology],
        )

    def test_pdd_section_c_omits_duplicate_identity_fields(self):
        self.assertEqual(
            self._property_paths(NIAS_UI.PddSectionCUiShape),
            [
                NIAS.stakeholderEngagementModalities,
                NIAS.stakeholderCommentSummary,
                NIAS.stakeholderCommentConsideration,
            ],
        )

    def test_document_field_review_omits_review_target_subform(self):
        paths = self._property_paths(NIAS_UI.DocumentFieldReviewUiShape)

        self.assertNotIn(NIAS.reviewTarget, paths)
        self.assertEqual(
            paths,
            [
                NIAS.fieldTitle,
                NIAS.fieldPrompt,
                NIAS.originalResponse,
                NIAS.reviewerDecision,
                NIAS.reviewerFeedback,
            ],
        )


if __name__ == "__main__":
    unittest.main()
