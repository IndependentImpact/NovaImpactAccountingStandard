import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "dataRequirements/shape2flutter/pdd_workflow_shell/tool/export_pdd_workflow_markdown.py"
)

NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
CLAIM = "http://w3id.org/claimont#"
AIAO = "http://w3id.org/aiao#"
IMPACTONT = "http://w3id.org/impactont#"
DCTERMS = "http://purl.org/dc/terms/"
SCHEMA = "https://schema.org/"


class PddWorkflowShellExportTests(unittest.TestCase):
    def test_draft_export_handoff_renders_section_content(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            pdd_a = tmp_path / "pdd-a.json"
            pdd_b = tmp_path / "pdd-b.json"
            pdd_c = tmp_path / "pdd-c.json"
            output = tmp_path / "pdd.md"

            pdd_a.write_text(json.dumps(_pdd_a_payload()), encoding="utf-8")
            pdd_b.write_text(json.dumps(_pdd_b_payload()), encoding="utf-8")
            pdd_c.write_text(json.dumps(_pdd_c_payload()), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pdd-a-json",
                    str(pdd_a),
                    "--pdd-b-json",
                    str(pdd_b),
                    "--pdd-c-json",
                    str(pdd_c),
                    "--render-mode",
                    "draft",
                    "--output",
                    str(output),
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
                check=True,
            )

            self.assertEqual(completed.stdout, "")
            markdown = output.read_text(encoding="utf-8")
            self.assertIn("### Workflow Export Pilot", markdown)
            self.assertIn("Increase carbon sequestration.", markdown)
            self.assertIn("Community workshop and household survey.", markdown)
            self.assertNotIn("- Community workshop and household survey.", markdown)

    def test_final_export_requires_approved_reviews(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            pdd_a = tmp_path / "pdd-a.json"
            pdd_b = tmp_path / "pdd-b.json"
            pdd_c = tmp_path / "pdd-c.json"
            review_a = tmp_path / "review-a.json"
            review_b = tmp_path / "review-b.json"
            review_c = tmp_path / "review-c.json"

            pdd_a.write_text(json.dumps(_pdd_a_payload()), encoding="utf-8")
            pdd_b.write_text(json.dumps(_pdd_b_payload()), encoding="utf-8")
            pdd_c.write_text(json.dumps(_pdd_c_payload()), encoding="utf-8")
            review_a.write_text(json.dumps(_approved_review_payload("pddA")), encoding="utf-8")
            rejected = _approved_review_payload("pddB")
            rejected[f"{NIAS}finalReviewDecision"] = f"{NIAS}review-reject"
            review_b.write_text(json.dumps(rejected), encoding="utf-8")
            review_c.write_text(json.dumps(_approved_review_payload("pddC")), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--pdd-a-json",
                    str(pdd_a),
                    "--pdd-b-json",
                    str(pdd_b),
                    "--pdd-c-json",
                    str(pdd_c),
                    "--review-a-json",
                    str(review_a),
                    "--review-b-json",
                    str(review_b),
                    "--review-c-json",
                    str(review_c),
                    "--render-mode",
                    "final",
                ],
                capture_output=True,
                text=True,
                encoding="utf-8",
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("Workflow gate failed for final export", completed.stderr)
            self.assertIn(
                "PDD-B validation review is not approved.",
                completed.stderr,
            )


def _pdd_a_payload():
    return {
        f"{NIAS}reportContent": [
            {
                f"{CLAIM}isMadeBy": f"{NIAS}users/project-developer-1",
                f"{CLAIM}hasSubject": [
                    {
                        f"{NIAS}title": "Workflow Export Pilot",
                        f"{AIAO}hasObjective": [{f"{SCHEMA}description": "Restore habitat."}],
                        f"{IMPACTONT}hasSpatialLocation": [
                            {f"{NIAS}resourceIpfsUri": "ipfs://workflow-export-location"}
                        ],
                        f"{NIAS}technologyOrMeasure": [
                            {
                                f"{NIAS}techMeasType": f"{NIAS}facility",
                                f"{SCHEMA}description": "Nursery and replanting.",
                            }
                        ],
                        f"{NIAS}projectParty": [
                            {
                                f"{NIAS}partyName": "Community Cooperative",
                                f"{NIAS}isHostParty": True,
                                f"{NIAS}isParticipantParty": True,
                            }
                        ],
                        f"{NIAS}legalMatters": "Permits granted.",
                        f"{NIAS}publicFundingStatus": f"{NIAS}no",
                        f"{NIAS}projectHistory": "Started in 2024.",
                        f"{NIAS}debundlingAssessment": "No overlap.",
                    }
                ],
                f"{DCTERMS}conformsTo": f"{NIAS}document-schema/PDDxA-1.0.0",
            }
        ]
    }


def _pdd_b_payload():
    return {
        f"{NIAS}reportContent": [
            {
                f"{CLAIM}isMadeBy": f"{NIAS}users/project-developer-1",
                f"{NIAS}hasDeclaredImpact": [
                    {
                        f"{SCHEMA}description": "Increase carbon sequestration.",
                        f"{NIAS}impactIntentionality": f"{NIAS}intentional",
                        f"{NIAS}beneficialOrAdverse": f"{NIAS}beneficial",
                        f"{NIAS}monitored": f"{NIAS}yes",
                    }
                ],
                f"{NIAS}impactClaim": [
                    {
                        f"{CLAIM}hasSubject": f"{NIAS}projects/pdd-alpha",
                    }
                ],
                f"{NIAS}usesMethodology": [
                    f"{NIAS}methodologies/default-pdd-methodology"
                ],
            }
        ]
    }


def _pdd_c_payload():
    return {
        f"{NIAS}stakeholderEngagementModalities": "Community workshop and household survey.",
        f"{NIAS}stakeholderCommentSummary": "Requested stronger local monitoring visibility.",
        f"{NIAS}stakeholderCommentConsideration": "Updated monitoring plan with community scorecards.",
    }


def _approved_review_payload(step_name):
    return {
        f"{NIAS}finalReviewDecision": f"{NIAS}review-approve",
        f"{NIAS}isReviewOf": f"{NIAS}documents/pdd-alpha/{step_name}",
    }


if __name__ == "__main__":
    unittest.main()
