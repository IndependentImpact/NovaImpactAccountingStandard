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
    / "dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py"
)
FIXTURES = REPO_ROOT / "dataRequirements/document-rendering/fixtures"
INPUT = FIXTURES / "validation-verification-report-input.jsonld"
EVIDENCE = FIXTURES / "validation-verification-report-evidence.jsonld"
INVALID_STRUCTURAL = (
    FIXTURES / "validation-verification-report-invalid-structural.jsonld"
)
INVALID_VVS_EVIDENCE = (
    FIXTURES / "validation-verification-report-invalid-vvs-evidence.jsonld"
)
VALIDATION_BLANK_FIXTURE = FIXTURES / "validation-report-blank-template.md"
VERIFICATION_BLANK_FIXTURE = FIXTURES / "verification-report-blank-template.md"
VALIDATION_RENDERED_FIXTURE = FIXTURES / "validation-report-rendered.md"
VERIFICATION_RENDERED_FIXTURE = FIXTURES / "verification-report-rendered.md"


class ValidationVerificationReportRenderingTests(unittest.TestCase):
    def _base_command(self):
        return [sys.executable, str(SCRIPT)]

    def _render_blank(self, report_type="validation"):
        completed = subprocess.run(
            [*self._base_command(), "--report-type", report_type],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        return completed.stdout

    def _render_draft(self, report_type="validation"):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--report-type",
                report_type,
                "--input-jsonld",
                str(INPUT),
                "--evidence-jsonld",
                str(EVIDENCE),
                "--source-artifact-id",
                "validation-verification-report-input.jsonld",
                "--generated-at",
                "2026-05-28T00:00:00Z",
                "--render-mode",
                "draft",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        return completed.stdout

    def test_validation_blank_template_matches_fixture(self):
        self.assertEqual(
            self._render_blank("validation"),
            VALIDATION_BLANK_FIXTURE.read_text(encoding="utf-8"),
        )

    def test_verification_blank_template_matches_fixture(self):
        self.assertEqual(
            self._render_blank("verification"),
            VERIFICATION_BLANK_FIXTURE.read_text(encoding="utf-8"),
        )

    def test_blank_templates_contain_expected_report_sections(self):
        validation = self._render_blank("validation")
        verification = self._render_blank("verification")
        self.assertIn("## Validation Report", validation)
        self.assertNotIn("## Verification Report", validation)
        self.assertIn("## Verification Report", verification)
        self.assertNotIn("## Validation Report", verification)
        rendered = validation
        self.assertIn("\\tableofcontents", rendered)
        self.assertNotIn("| Section | Page |", rendered)
        self.assertIn("## Review Decision Register", rendered)
        self.assertIn("## Anchor Review Findings", rendered)
        self.assertIn("## VVS Requirement Coverage Summary", rendered)
        self.assertIn("## Appendix A. Review Document And Workflow Evidence", rendered)
        self.assertNotIn("\n## Workflow And Consensus Evidence\n", rendered)
        self.assertIn("**[required for final]**", rendered)

    def test_validation_draft_rendering_matches_fixture(self):
        self.assertEqual(
            self._render_draft("validation"),
            VALIDATION_RENDERED_FIXTURE.read_text(encoding="utf-8"),
        )

    def test_verification_draft_rendering_matches_fixture(self):
        self.assertEqual(
            self._render_draft("verification"),
            VERIFICATION_RENDERED_FIXTURE.read_text(encoding="utf-8"),
        )

    def test_validation_draft_rendering_filters_reviews_and_vvs_coverage(self):
        rendered = self._render_draft("validation")
        self.assertRegex(rendered, r"#### Review documents\s+1\s")
        self.assertRegex(rendered, r"#### Anchor reviews\s+1\s")
        self.assertIn("| vv-validation-review-1 | Validation review | Approve | 1 |", rendered)
        self.assertIn("pdd.sectionB.declaredImpacts", rendered)
        self.assertNotIn("vv-verification-review-1", rendered)
        self.assertIn("| REQ-PDD-001 | validation | PddSectionAReport |", rendered)
        self.assertNotIn("REQ-MR-001", rendered)
        self.assertIn("Validate PDD impact declaration", rendered)

    def test_verification_draft_rendering_filters_reviews_and_vvs_coverage(self):
        rendered = self._render_draft("verification")
        self.assertRegex(rendered, r"#### Review documents\s+1\s")
        self.assertRegex(rendered, r"#### Anchor reviews\s+1\s")
        self.assertNotIn("vv-validation-review-1 | Validation review", rendered)
        self.assertIn("| vv-verification-review-1 | Verification review | Approve | 1 |", rendered)
        self.assertIn("monitoring.report.impactSummary", rendered)
        self.assertNotIn("REQ-PDD-001", rendered)
        self.assertIn("| REQ-MR-001 | verification | MonitoringReport |", rendered)
        self.assertIn("Verify monitoring report and VIC issuance request", rendered)

    def test_workflow_and_document_envelope_render_in_appendix_only(self):
        rendered = self._render_draft("validation")
        self.assertLess(
            rendered.index("## VVS Requirement Coverage Summary"),
            rendered.index("## Appendix A. Review Document And Workflow Evidence"),
        )
        body = rendered.split("## Appendix A. Review Document And Workflow Evidence", 1)[0]
        self.assertNotIn("Workflow step", body)
        self.assertNotIn("IPFS URI", body)
        self.assertIn("Workflow step", rendered)
        self.assertIn("IPFS URI", rendered)

    def test_final_validation_rendering_accepts_conformant_input(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--report-type",
                "validation",
                "--input-jsonld",
                str(INPUT),
                "--evidence-jsonld",
                str(EVIDENCE),
                "--source-artifact-id",
                "validation-verification-report-input.jsonld",
                "--generated-at",
                "2026-05-28T00:00:00Z",
                "--render-mode",
                "final",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertIn("renderMode: final", completed.stdout)
        self.assertIn("reportType: validation", completed.stdout)
        self.assertIn("| REQ-PDD-003 | validation | PddSectionCReport | ReqPdd003Shape | passed |", completed.stdout)
        self.assertNotIn("REQ-MR-001", completed.stdout)

    def test_final_verification_rendering_accepts_conformant_input(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--report-type",
                "verification",
                "--input-jsonld",
                str(INPUT),
                "--evidence-jsonld",
                str(EVIDENCE),
                "--source-artifact-id",
                "validation-verification-report-input.jsonld",
                "--generated-at",
                "2026-05-28T00:00:00Z",
                "--render-mode",
                "final",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertIn("renderMode: final", completed.stdout)
        self.assertIn("reportType: verification", completed.stdout)
        self.assertIn("| REQ-MR-001 | verification | MonitoringReport | ReqMr001Shape | passed |", completed.stdout)
        self.assertNotIn("REQ-PDD-001", completed.stdout)

    def test_final_validation_rendering_ignores_invalid_verification_evidence(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--report-type",
                "validation",
                "--input-jsonld",
                str(INPUT),
                "--evidence-jsonld",
                str(EVIDENCE),
                "--evidence-jsonld",
                str(INVALID_VVS_EVIDENCE),
                "--render-mode",
                "final",
            ],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertIn("reportType: validation", completed.stdout)
        self.assertIn("REQ-PDD-001", completed.stdout)
        self.assertNotIn("REQ-MR-001", completed.stdout)

    def test_final_rendering_rejects_structurally_invalid_review_input(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--report-type",
                "validation",
                "--input-jsonld",
                str(INVALID_STRUCTURAL),
                "--evidence-jsonld",
                str(EVIDENCE),
                "--render-mode",
                "final",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("structurally conformant review input", completed.stderr)
        self.assertIn(
            "A document review must have a final approve/reject decision.",
            completed.stderr,
        )

    def test_final_rendering_rejects_vvs_invalid_evidence(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--report-type",
                "verification",
                "--input-jsonld",
                str(INPUT),
                "--evidence-jsonld",
                str(INVALID_VVS_EVIDENCE),
                "--render-mode",
                "final",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn("VVS requirement-conformant evidence", completed.stderr)
        self.assertIn("REQ-MR-001", completed.stderr)
        self.assertIn("REQ-MR-002", completed.stderr)

    def test_final_rendering_requires_at_least_one_vvs_target(self):
        completed = subprocess.run(
            [
                *self._base_command(),
                "--report-type",
                "validation",
                "--input-jsonld",
                str(INPUT),
                "--render-mode",
                "final",
            ],
            check=False,
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=REPO_ROOT,
        )
        self.assertNotEqual(completed.returncode, 0)
        self.assertIn(
            "requires at least one validation VVS-targeted evidence artifact",
            completed.stderr,
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

    def test_final_export_writes_deterministic_targets_and_sidecars(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            fake_pandoc = tmp_path / "pandoc"
            self._write_fake_pandoc(fake_pandoc)

            output_dir = tmp_path / "exported"
            env = os.environ.copy()
            env["PATH"] = f"{tmp_path}{os.pathsep}{env.get('PATH', '')}"
            env["PANDOC_BIN"] = str(fake_pandoc)

            subprocess.run(
                [
                    *self._base_command(),
                    "--report-type",
                    "validation",
                    "--input-jsonld",
                    str(INPUT),
                    "--evidence-jsonld",
                    str(EVIDENCE),
                    "--source-artifact-id",
                    "validation-verification-report-input.jsonld",
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

            markdown = output_dir / "validation-report.md"
            pdf = output_dir / "validation-report.pdf"
            html = output_dir / "validation-report.html"
            metadata = output_dir / "validation-report.metadata.jsonld"
            validation = output_dir / "validation-report.validation.json"

            self.assertTrue(markdown.exists())
            self.assertTrue(pdf.exists())
            self.assertTrue(html.exists())
            self.assertTrue(metadata.exists())
            self.assertTrue(validation.exists())

            self.assertIn(
                "## VVS Requirement Coverage Summary",
                markdown.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "## Review Decision Register",
                html.read_text(encoding="utf-8"),
            )
            pdf_bytes = pdf.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
            self.assertIn(b"%%EOF", pdf_bytes[-1024:])
            self.assertIn(b"Document ID: validation-report-", pdf_bytes)

            metadata_payload = json.loads(metadata.read_text(encoding="utf-8"))
            artifact_types = {
                artifact["artifact"]
                for artifact in metadata_payload["nias:artifacts"]
            }
            self.assertEqual(artifact_types, {"markdown", "pdf", "website"})
            self.assertEqual(metadata_payload["nias:reviewedArtifactType"], "pdd")
            self.assertEqual(
                metadata_payload["nias:reviewedArtifactContentCid"],
                "bafypddartifactcontentcid",
            )
            self.assertEqual(
                metadata_payload["nias:reviewedSubmissionTopicId"],
                "0.0.1000",
            )

            validation_payload = json.loads(validation.read_text(encoding="utf-8"))
            self.assertEqual(validation_payload["status"], "passed")
            self.assertEqual(validation_payload["renderMode"], "final")
            self.assertEqual(validation_payload["reportType"], "validation")

    def test_final_verification_export_writes_verification_named_targets(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "exported"
            subprocess.run(
                [
                    *self._base_command(),
                    "--report-type",
                    "verification",
                    "--input-jsonld",
                    str(INPUT),
                    "--evidence-jsonld",
                    str(EVIDENCE),
                    "--source-artifact-id",
                    "validation-verification-report-input.jsonld",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
                    "--output-dir",
                    str(output_dir),
                    "--output-target",
                    "markdown",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            markdown = output_dir / "verification-report.md"
            metadata = output_dir / "verification-report.metadata.jsonld"
            validation = output_dir / "verification-report.validation.json"

            self.assertTrue(markdown.exists())
            self.assertTrue(metadata.exists())
            self.assertTrue(validation.exists())
            self.assertFalse((output_dir / "validation-report.md").exists())
            self.assertIn(
                "## Verification Report",
                markdown.read_text(encoding="utf-8"),
            )

            validation_payload = json.loads(validation.read_text(encoding="utf-8"))
            self.assertEqual(validation_payload["status"], "passed")
            self.assertEqual(validation_payload["renderMode"], "final")
            self.assertEqual(validation_payload["reportType"], "verification")

    def test_final_rendering_requires_reviewed_artifact_identity_fields(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            invalid = tmp_path / "vv-missing-reviewed-content-cid.jsonld"
            payload = json.loads(INPUT.read_text(encoding="utf-8"))
            review = next(
                node
                for node in payload
                if node.get("@id")
                == "https://nova.org.za/novaimpactaccountingstandard/test/vv-validation-review-1"
            )
            review.pop(
                "https://nova.org.za/novaimpactaccountingstandard/reviewedArtifactContentCid",
                None,
            )
            invalid.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    *self._base_command(),
                    "--report-type",
                    "validation",
                    "--input-jsonld",
                    str(invalid),
                    "--evidence-jsonld",
                    str(EVIDENCE),
                    "--render-mode",
                    "final",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "reviewedArtifactContentCid is required in final render mode.",
                completed.stderr,
            )

    def test_final_verification_rendering_requires_reviewed_dlr_content_cid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            invalid = tmp_path / "vv-missing-reviewed-dlr-cid.jsonld"
            payload = json.loads(INPUT.read_text(encoding="utf-8"))
            review = next(
                node
                for node in payload
                if node.get("@id")
                == "https://nova.org.za/novaimpactaccountingstandard/test/vv-verification-review-1"
            )
            review.pop(
                "https://nova.org.za/novaimpactaccountingstandard/reviewedDlrContentCid",
                None,
            )
            invalid.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
            completed = subprocess.run(
                [
                    *self._base_command(),
                    "--report-type",
                    "verification",
                    "--input-jsonld",
                    str(invalid),
                    "--evidence-jsonld",
                    str(EVIDENCE),
                    "--render-mode",
                    "final",
                ],
                check=False,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn(
                "reviewedDlrContentCid is required in final render mode.",
                completed.stderr,
            )


if __name__ == "__main__":
    unittest.main()
