import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "tooling/document-rendering/export_validation_verification_report_markdown.py"
)
VALIDATION_WRAPPER = (
    REPO_ROOT
    / "dataRequirements/shape2flutter/validation_report/tool/export_validation_report_markdown.py"
)
VERIFICATION_WRAPPER = (
    REPO_ROOT
    / "dataRequirements/shape2flutter/verification_report/tool/export_verification_report_markdown.py"
)
FIXTURES = REPO_ROOT / "dataRequirements/document-rendering/fixtures"
VALIDATION_EVIDENCE = FIXTURES / "validation-report-evidence.jsonld"
VERIFICATION_EVIDENCE = FIXTURES / "verification-report-evidence.jsonld"

DATA = "https://jellyfiiish.xyz/ns/"
HEDERA = "https://hashgraphontology.xyz/core/"
NIAS = "https://nova.org.za/novaimpactaccountingstandard/"


class ValidationVerificationHandoffExportTests(unittest.TestCase):
    def test_split_wrappers_do_not_depend_on_archived_combined_exporter(self):
        for wrapper_path in (VALIDATION_WRAPPER, VERIFICATION_WRAPPER):
            source = wrapper_path.read_text(encoding="utf-8")
            self.assertIn(
                "tooling/document-rendering/export_validation_verification_report_markdown.py",
                source,
            )
            self.assertNotIn(
                "validation_verification_report/tool/export_validation_verification_report_markdown.py",
                source,
            )

    def _write_fake_pandoc(self, path: Path):
        path.write_text(
            "\n".join(
                [
                    "#!/usr/bin/env python3",
                    "import pathlib",
                    "import sys",
                    "args = sys.argv[1:]",
                    "source = pathlib.Path(args[0])",
                    "output = pathlib.Path(args[args.index('--output') + 1])",
                    "if output.suffix == '.html':",
                    "    output.write_text('<html><body>' + source.read_text(encoding='utf-8') + '</body></html>', encoding='utf-8')",
                    "else:",
                    "    output.write_bytes(source.read_text(encoding='utf-8').encode('utf-8'))",
                ]
            )
            + "\n",
            encoding="utf-8",
        )
        path.chmod(0o755)

    def test_validation_review_form_is_wrapped_and_rendered_final(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            review_json = tmp_path / "validation-review-form.json"
            package_jsonld = tmp_path / "review-package.jsonld"
            output = tmp_path / "validation-report.md"

            review_json.write_text(
                json.dumps(_review_form_payload("validation")),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--report-type",
                    "validation",
                    "--review-json",
                    str(review_json),
                    "--review-id",
                    f"{NIAS}test/handoff-validation-review",
                    "--evidence-jsonld",
                    str(VALIDATION_EVIDENCE),
                    "--document-author",
                    f"{NIAS}test/validator-1",
                    "--resource-ipfs-uri",
                    "ipfs://bafyhandoffvalidationreview",
                    "--workflow-step-label",
                    "Validate PDD handoff",
                    "--source-artifact-id",
                    "validation-review-form.json",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--review-package-output",
                    str(package_jsonld),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            rendered = output.read_text(encoding="utf-8")
            self.assertIn("## Validation Report", rendered)
            self.assertIn("| handoff-validation-review | Validation review | Approve | 1 |", rendered)
            self.assertIn("Validate PDD handoff", rendered)
            self.assertIn("ipfs://bafyhandoffvalidationreview", rendered)

            package = json.loads(package_jsonld.read_text(encoding="utf-8"))
            review_node = next(
                node
                for node in package
                if node["@id"] == f"{NIAS}test/handoff-validation-review"
            )
            self.assertIn(DATA + "Document", review_node["@type"])
            self.assertIn(NIAS + "GenericDocumentReview", review_node["@type"])
            self.assertEqual(
                review_node[f"{NIAS}documentSchema"][0]["@id"],
                f"{NIAS}document-schema/GenericDocumentReview-5.0.0",
            )
            self.assertIn(f"{NIAS}hasWorkflowSubmission", review_node)
            field_node = next(
                node
                for node in package
                if node["@id"] == f"{NIAS}test/handoff-validation-review/field-review-1"
            )
            self.assertNotIn(f"{NIAS}fieldKey", field_node)
            self.assertIn(f"{NIAS}reviewTarget", field_node)

    def test_verification_review_form_writes_verification_outputs(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            fake_pandoc = tmp_path / "pandoc"
            self._write_fake_pandoc(fake_pandoc)
            review_json = tmp_path / "verification-review-form.json"
            output_dir = tmp_path / "exported"
            env = os.environ.copy()
            env["PATH"] = f"{tmp_path}{os.pathsep}{env.get('PATH', '')}"
            env.pop("PANDOC_BIN", None)

            review_json.write_text(
                json.dumps(_review_form_payload("verification")),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--report-type",
                    "verification",
                    "--review-json",
                    str(review_json),
                    "--review-id",
                    f"{NIAS}test/handoff-verification-review",
                    "--evidence-jsonld",
                    str(VERIFICATION_EVIDENCE),
                    "--document-author",
                    f"{NIAS}test/verifier-1",
                    "--resource-ipfs-uri",
                    "ipfs://bafyhandoffverificationreview",
                    "--workflow-step-label",
                    "Verify monitoring report handoff",
                    "--source-artifact-id",
                    "verification-review-form.json",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "markdown",
                    "--output-target",
                    "pdf",
                    "--output-target",
                    "html",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
                env=env,
            )

            markdown = output_dir / "verification-report.md"
            pdf = output_dir / "verification-report.pdf"
            html = output_dir / "verification-report.html"
            self.assertTrue(markdown.exists())
            self.assertTrue(pdf.exists())
            self.assertTrue(html.exists())
            self.assertTrue((output_dir / "verification-report.metadata.jsonld").exists())
            self.assertTrue((output_dir / "verification-report.validation.json").exists())
            rendered = markdown.read_text(encoding="utf-8")
            self.assertIn("## Verification Report", rendered)
            self.assertIn("| handoff-verification-review | Verification review | Approve | 1 |", rendered)
            self.assertNotIn("handoff-validation-review", rendered)
            self.assertIn("Verification Report", html.read_text(encoding="utf-8"))

    def test_validation_activity_wrapper_uses_validation_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            review_json = tmp_path / "validation-review-form.json"
            package_jsonld = tmp_path / "validation-package.jsonld"
            output = tmp_path / "validation-report.md"

            payload = _review_form_payload("validation")
            del payload[f"{NIAS}hasWorkflowSubmission"][f"{NIAS}workflow"]
            review_json.write_text(json.dumps(payload), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(VALIDATION_WRAPPER),
                    "--review-json",
                    str(review_json),
                    "--review-id",
                    f"{NIAS}test/wrapper-validation-review",
                    "--evidence-jsonld",
                    str(VALIDATION_EVIDENCE),
                    "--document-author",
                    f"{NIAS}test/validator-1",
                    "--resource-ipfs-uri",
                    "ipfs://bafywrappervalidationreview",
                    "--workflow-step-label",
                    "Validate PDD wrapper",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--review-package-output",
                    str(package_jsonld),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            rendered = output.read_text(encoding="utf-8")
            self.assertIn("## Validation Report", rendered)
            self.assertNotIn("## Verification Report", rendered)

            package = json.loads(package_jsonld.read_text(encoding="utf-8"))
            submission = next(
                node
                for node in package
                if node["@id"].endswith("/workflow-submission")
            )
            self.assertEqual(
                submission[f"{NIAS}workflow"][0]["@id"],
                f"{NIAS}workflows/validation-report",
            )

    def test_verification_activity_wrapper_uses_verification_defaults(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            review_json = tmp_path / "verification-review-form.json"
            package_jsonld = tmp_path / "verification-package.jsonld"
            output = tmp_path / "verification-report.md"

            payload = _review_form_payload("verification")
            del payload[f"{NIAS}hasWorkflowSubmission"][f"{NIAS}workflow"]
            review_json.write_text(json.dumps(payload), encoding="utf-8")

            subprocess.run(
                [
                    sys.executable,
                    str(VERIFICATION_WRAPPER),
                    "--review-json",
                    str(review_json),
                    "--review-id",
                    f"{NIAS}test/wrapper-verification-review",
                    "--evidence-jsonld",
                    str(VERIFICATION_EVIDENCE),
                    "--document-author",
                    f"{NIAS}test/verifier-1",
                    "--resource-ipfs-uri",
                    "ipfs://bafywrapperverificationreview",
                    "--workflow-step-label",
                    "Verify monitoring report wrapper",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--review-package-output",
                    str(package_jsonld),
                    "--output",
                    str(output),
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            rendered = output.read_text(encoding="utf-8")
            self.assertIn("## Verification Report", rendered)
            self.assertNotIn("## Validation Report", rendered)

            package = json.loads(package_jsonld.read_text(encoding="utf-8"))
            submission = next(
                node
                for node in package
                if node["@id"].endswith("/workflow-submission")
            )
            self.assertEqual(
                submission[f"{NIAS}workflow"][0]["@id"],
                f"{NIAS}workflows/verification-report",
            )

    def test_validation_review_missing_reviewed_artifact_fails(self):
        payload = _review_form_payload("validation")
        del payload[f"{NIAS}fieldReview"][0][f"{NIAS}reviewTarget"][f"{NIAS}reviewedArtifact"]
        self._assert_export_fails(
            payload,
            "validation",
            SCRIPT,
            "Field review 1 reviewedArtifact is required.",
        )

    def test_validation_review_missing_reviewed_submission_topic_id_fails(self):
        payload = _review_form_payload("validation")
        del payload[f"{NIAS}reviewedSubmissionTopicId"]
        self._assert_export_fails(
            payload,
            "validation",
            SCRIPT,
            "reviewedSubmissionTopicId is required.",
        )

    def test_validation_review_missing_reviewed_anchor_fails(self):
        payload = _review_form_payload("validation")
        del payload[f"{NIAS}fieldReview"][0][f"{NIAS}reviewTarget"][f"{NIAS}reviewedAnchor"]
        self._assert_export_fails(
            payload,
            "validation",
            SCRIPT,
            "Field review 1 reviewedAnchor is required.",
        )

    def test_validation_review_missing_field_title_fails(self):
        payload = _review_form_payload("validation")
        del payload[f"{NIAS}fieldReview"][0][f"{NIAS}fieldTitle"]
        self._assert_export_fails(
            payload,
            "validation",
            SCRIPT,
            "Field review 1 fieldTitle is required.",
        )

    def test_validation_review_missing_reviewer_feedback_fails(self):
        payload = _review_form_payload("validation")
        del payload[f"{NIAS}fieldReview"][0][f"{NIAS}reviewerFeedback"]
        self._assert_export_fails(
            payload,
            "validation",
            SCRIPT,
            "Field review 1 reviewerFeedback is required.",
        )

    def test_validation_review_missing_final_decision_fails(self):
        payload = _review_form_payload("validation")
        del payload[f"{NIAS}finalReviewDecision"]
        self._assert_export_fails(
            payload,
            "validation",
            SCRIPT,
            "finalReviewDecision is required.",
        )

    def test_verification_review_missing_account_id_fails(self):
        payload = _review_form_payload("verification")
        del payload[f"{NIAS}requestedIssuanceAccountId"]
        self._assert_export_fails(
            payload,
            "verification",
            VERIFICATION_WRAPPER,
            "requestedIssuanceAccountId is required.",
        )

    def test_verification_review_invalid_account_format_fails(self):
        payload = _review_form_payload("verification")
        payload[f"{NIAS}requestedIssuanceAccountId"] = "invalid-account"
        self._assert_export_fails(
            payload,
            "verification",
            VERIFICATION_WRAPPER,
            "requestedIssuanceAccountId must match shard.realm.num.",
        )

    def test_verification_review_missing_reviewed_dlr_content_cid_fails(self):
        payload = _review_form_payload("verification")
        del payload[f"{NIAS}reviewedDlrContentCid"]
        self._assert_export_fails(
            payload,
            "verification",
            VERIFICATION_WRAPPER,
            "reviewedDlrContentCid is required.",
        )

    def _assert_export_fails(self, payload, report_type, script, expected_message):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            review_json = tmp_path / f"{report_type}-review-form.json"
            output = tmp_path / f"{report_type}-report.md"

            review_json.write_text(json.dumps(payload), encoding="utf-8")

            completed = subprocess.run(
                [
                    sys.executable,
                    str(script),
                    "--review-json",
                    str(review_json),
                    "--review-id",
                    f"{NIAS}test/{report_type}-review",
                    "--evidence-jsonld",
                    str(
                        VALIDATION_EVIDENCE
                        if report_type == "validation"
                        else VERIFICATION_EVIDENCE
                    ),
                    "--document-author",
                    (
                        f"{NIAS}test/validator-1"
                        if report_type == "validation"
                        else f"{NIAS}test/verifier-1"
                    ),
                    "--resource-ipfs-uri",
                    f"ipfs://bafy{report_type}review",
                    "--workflow-step-label",
                    f"{report_type.title()} review",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--output",
                    str(output),
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(expected_message, completed.stderr)


def _review_form_payload(report_type):
    reviewer = "validator-1" if report_type == "validation" else "verifier-1"
    workflow_step = "validation-review" if report_type == "validation" else "verification-review"
    payload = {
        f"{NIAS}hasWorkflowSubmission": {
            f"{NIAS}submittedDocument": f"{NIAS}test/handoff-{report_type}-review",
            f"{NIAS}workflow": f"{NIAS}test/vv-workflow",
            f"{NIAS}workflowStep": f"{NIAS}test/{workflow_step}",
            f"{NIAS}workflowSubject": f"{NIAS}test/project-1",
            f"{NIAS}workflowDocumentSubmittedBy": f"{NIAS}test/{reviewer}",
            f"{NIAS}workflowDocumentRecipient": f"{NIAS}test/registry-1",
            f"{NIAS}workflowSubmissionConsensusMessage": {
                f"{HEDERA}inTopic": f"{NIAS}test/topic-1",
                f"{HEDERA}hasSequenceNumber": 31,
                f"{HEDERA}hasConsensusTimestamp": "2026-05-27T10:00:00Z",
            },
        },
        f"{NIAS}fieldReview": [
            {
                f"{NIAS}reviewTarget": {
                    f"{NIAS}reviewedArtifact": (
                        f"{NIAS}test/pdd-artifact-1"
                        if report_type == "validation"
                        else f"{NIAS}test/monitoring-report-1"
                    ),
                    f"{NIAS}reviewedAnchor": (
                        f"{NIAS}test/pdd-artifact-1/anchors/pdd.sectionB.declaredImpacts"
                        if report_type == "validation"
                        else f"{NIAS}test/monitoring-report-1/anchors/monitoring.report.impactSummary"
                    ),
                },
                f"{NIAS}fieldTitle": f"{report_type.title()} field",
                f"{NIAS}fieldPrompt": "Review the supplied evidence.",
                f"{NIAS}originalResponse": "Evidence package submitted.",
                f"{NIAS}reviewerDecision": f"{NIAS}review-approve",
                f"{NIAS}reviewerFeedback": "Evidence is acceptable.",
            }
        ],
        f"{NIAS}finalReviewDecision": f"{NIAS}review-approve",
        f"{NIAS}artifactContentCid": f"bafy{report_type}artifactcid",
        f"{NIAS}artifactSchemaCid": f"bafy{report_type}schemacid",
        f"{NIAS}artifactSchemaVersionLabel": f"nias:{report_type}-schema:main:2026-05-28:bafy{report_type[:4]}",
        f"{NIAS}reviewedArtifactType": "pdd" if report_type == "validation" else "monitoring-report",
        f"{NIAS}reviewedArtifactContentCid": (
            "bafypddartifactcontentcid"
            if report_type == "validation"
            else "bafymonitoringartifactcontentcid"
        ),
        f"{NIAS}reviewedSubmissionTopicId": "0.0.1001",
        f"{NIAS}reviewedSubmissionConsensusTimestamp": "2026-05-27T10:00:00Z",
    }
    if report_type == "verification":
        payload[f"{NIAS}requestedIssuanceAccountId"] = "0.0.3003"
        payload[f"{NIAS}reviewedDlrContentCid"] = "bafydlrcontentcid"
    return payload


if __name__ == "__main__":
    unittest.main()
