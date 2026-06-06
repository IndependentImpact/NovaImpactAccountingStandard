import json
import subprocess
import sys
import tempfile
import unittest
from types import SimpleNamespace
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
            self.assertIn(
                "| Project title | https://nova.org.za/novaimpactaccountingstandard/title |",
                markdown,
            )

    def test_draft_export_preserves_repeated_form_values(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            pdd_a = tmp_path / "pdd-a.json"
            pdd_b = tmp_path / "pdd-b.json"
            pdd_c = tmp_path / "pdd-c.json"
            output = tmp_path / "pdd.md"

            pdd_a.write_text(json.dumps(_pdd_a_payload(repeated=True)), encoding="utf-8")
            pdd_b.write_text(json.dumps(_pdd_b_payload(repeated=True)), encoding="utf-8")
            pdd_c.write_text(json.dumps(_pdd_c_payload()), encoding="utf-8")

            subprocess.run(
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

            markdown = output.read_text(encoding="utf-8")
            self.assertIn("ipfs://workflow-export-location-2", markdown)
            self.assertIn("| Type | facility |", markdown)
            self.assertIn("| Type | system |", markdown)
            self.assertIn("Soil carbon monitoring.", markdown)
            self.assertIn("University Partner", markdown)
            self.assertIn("#### Declared Impact 2", markdown)
            self.assertIn("Improve biodiversity.", markdown)

    def test_final_export_no_longer_uses_validation_review_gate(self):
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
            self.assertNotIn("Workflow gate failed for final export", completed.stderr)
            self.assertNotIn("validation review is not approved", completed.stderr)
            self.assertIn(
                "Final render mode requires SHACL-conformant input.",
                completed.stderr,
            )

    def test_final_export_writes_identity_fields_in_metadata_sidecar(self):
        from dataRequirements.shape2flutter.pdd_workflow_shell.tool.export_pdd_workflow_markdown import (
            build_renderer_payload,
        )

        args = SimpleNamespace(
            artifact_schema_cid="bafypddschemacid",
            artifact_content_cid="bafypddartifactcontentcid",
            artifact_schema_version_label=None,
            schema_track="main",
            submission_topic_id="0.0.1000",
            submission_consensus_timestamp="2026-05-20T10:00:00Z",
        )
        payload = build_renderer_payload(
            _pdd_a_payload(),
            _pdd_b_payload(),
            _pdd_c_payload(),
            args,
            "2026-05-20T10:00:00Z",
        )
        section_a = next(
            node
            for node in payload["@graph"]
            if node.get("@id") == f"{NIAS}reports/pdd-section-a"
        )
        self.assertIn(f"{NIAS}artifactContentCid", section_a)
        self.assertIn(f"{NIAS}artifactSchemaCid", section_a)
        self.assertIn(f"{NIAS}artifactSchemaVersionLabel", section_a)
        self.assertIn(f"{NIAS}artifactAuthor", section_a)
        self.assertIn(f"{NIAS}submissionTopicId", section_a)
        self.assertIn(f"{NIAS}submissionConsensusTimestamp", section_a)


def _pdd_a_payload(repeated=False):
    locations = [
        {f"{NIAS}resourceIpfsUri": "ipfs://workflow-export-location"}
    ]
    technologies = [
        {
            f"{NIAS}techMeasType": f"{NIAS}facility",
            f"{SCHEMA}description": "Nursery and replanting.",
        }
    ]
    parties = [
        {
            f"{NIAS}partyName": "Community Cooperative",
            f"{NIAS}isHostParty": True,
            f"{NIAS}isParticipantParty": True,
        }
    ]
    if repeated:
        locations.append({f"{NIAS}resourceIpfsUri": "ipfs://workflow-export-location-2"})
        technologies.append(
            {
                f"{NIAS}techMeasType": f"{NIAS}system",
                f"{SCHEMA}description": "Soil carbon monitoring.",
            }
        )
        parties.append(
            {
                f"{NIAS}partyName": "University Partner",
                f"{NIAS}isHostParty": False,
                f"{NIAS}isParticipantParty": True,
            }
        )
    return {
        f"{NIAS}reportContent": [
            {
                f"{CLAIM}isMadeBy": f"{NIAS}users/project-developer-1",
                f"{CLAIM}hasSubject": [
                    {
                        f"{NIAS}title": "Workflow Export Pilot",
                        f"{AIAO}hasObjective": [{f"{SCHEMA}description": "Restore habitat."}],
                        f"{IMPACTONT}hasSpatialLocation": locations,
                        f"{NIAS}technologyOrMeasure": technologies,
                        f"{NIAS}projectParty": parties,
                        f"{NIAS}legalMatters": "Permits granted.",
                        f"{NIAS}publicFundingStatus": False,
                        f"{NIAS}projectHistory": "Started in 2024.",
                        f"{NIAS}debundlingAssessment": "No overlap.",
                    }
                ],
                f"{DCTERMS}conformsTo": f"{NIAS}document-schema/PDDxA-1.0.0",
            }
        ]
    }


def _pdd_b_payload(repeated=False):
    impacts = [
        {
            f"{SCHEMA}description": "Increase carbon sequestration.",
            f"{NIAS}impactIntentionality": f"{NIAS}intentional",
            f"{NIAS}beneficialOrAdverse": f"{NIAS}beneficial",
            f"{NIAS}monitored": True,
        }
    ]
    claims = [
        {
            f"{CLAIM}hasSubject": f"{NIAS}projects/pdd-alpha",
        }
    ]
    if repeated:
        impacts.append(
            {
                f"{SCHEMA}description": "Improve biodiversity.",
                f"{NIAS}impactIntentionality": f"{NIAS}intentional",
                f"{NIAS}beneficialOrAdverse": f"{NIAS}beneficial",
                f"{NIAS}monitored": True,
            }
        )
        claims.append(
            {
                f"{CLAIM}hasSubject": f"{NIAS}projects/pdd-alpha",
                f"{NIAS}usesMethodology": [
                    f"{NIAS}methodologies/biodiversity-methodology"
                ],
            }
        )
    return {
        f"{NIAS}reportContent": [
            {
                f"{CLAIM}isMadeBy": f"{NIAS}users/project-developer-1",
                f"{NIAS}hasDeclaredImpact": impacts,
                f"{NIAS}impactClaim": claims,
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
