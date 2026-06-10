import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from pyshacl import validate
from rdflib import Graph, Namespace
from rdflib.namespace import RDF


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "tooling/document-rendering/render_validation_verification_report_markdown.py"
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
ARTIFACT_ANCHOR_SHAPES = REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl"
REQUIREMENT_COVERAGE_PROOF_SHAPES = (
    REPO_ROOT / "dataRequirements/requirement-coverage-proof-shapes.ttl"
)
VVS_REQUIREMENT_ANCHOR_MAP = (
    REPO_ROOT / "dataRequirements/mappings/vvs-requirement-anchor-map.ttl"
)
ANCHOR_DEFINITION_FILES = [
    REPO_ROOT / "dataRequirements/mappings/pdd-anchor-definitions.ttl",
    REPO_ROOT / "dataRequirements/mappings/monitoring-anchor-definitions.ttl",
    REPO_ROOT / "dataRequirements/mappings/dlr-anchor-definitions.ttl",
]
ONTOLOGY_FILES = [
    REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
    REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
]

NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")


def _load_graph(paths):
    graph = Graph()
    for path in paths:
        graph.parse(path)
    return graph


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

    def _assert_coverage_sidecar_conforms(self, sidecar_path: Path):
        coverage_graph = Graph().parse(sidecar_path, format="json-ld")
        conforms, _, validation_text = validate(
            data_graph=coverage_graph,
            shacl_graph=_load_graph(
                [
                    ARTIFACT_ANCHOR_SHAPES,
                    REQUIREMENT_COVERAGE_PROOF_SHAPES,
                ]
            ),
            ont_graph=_load_graph(ONTOLOGY_FILES),
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )
        self.assertTrue(conforms, msg=validation_text)
        return coverage_graph

    def _canonical_anchor_keys_for_report(self, report_type: str):
        mandate = NIAS.validation if report_type == "validation" else NIAS.verification
        mapping_graph = Graph().parse(VVS_REQUIREMENT_ANCHOR_MAP, format="turtle")
        anchor_graph = _load_graph(ANCHOR_DEFINITION_FILES)
        keys = set()
        for mapping in mapping_graph.subjects(RDF.type, NIAS.RequirementMapping):
            if (mapping, NIAS.reviewMandate, mandate) not in mapping_graph:
                continue
            anchor = mapping_graph.value(mapping, NIAS.mappedAnchor)
            anchor_key = anchor_graph.value(anchor, NIAS.anchorKey)
            if anchor_key is not None:
                keys.add(str(anchor_key))
        return keys

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
        self.assertIn("## Section 1. Global Evaluation", rendered)
        self.assertIn("## Section 3. Paragraph-Level Validation Findings", rendered)
        self.assertIn("## Section 4. VVS Requirement Coverage Summary", rendered)
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
        self.assertIn(
            "| REQ-PDD-001 | validation | pdd.sectionA - Section A. Description Of Project; pdd.sectionA.technologiesAndMeasures - A.3 Technologies And Measures |",
            rendered,
        )
        self.assertNotIn("REQ-MR-001", rendered)
        self.assertIn("Validate PDD impact declaration", rendered)

    def test_verification_draft_rendering_filters_reviews_and_vvs_coverage(self):
        rendered = self._render_draft("verification")
        self.assertRegex(rendered, r"#### Review documents\s+1\s")
        self.assertRegex(rendered, r"#### Anchor reviews\s+1\s")
        self.assertNotIn("vv-validation-review-1 | Validation review", rendered)
        self.assertIn("| vv-verification-review-1 | Verification review | Approve | 1 |", rendered)
        self.assertIn("monitoring.observation", rendered)
        self.assertNotIn("REQ-PDD-001", rendered)
        self.assertIn(
            "| REQ-MR-001 | verification | pdd.sectionB.declaredImpacts - B.2 Declared Impacts; monitoring.observation - Measured Impact Observation |",
            rendered,
        )
        self.assertIn("Verify monitoring report and VIC issuance request", rendered)

    def test_workflow_and_document_envelope_render_in_appendix_only(self):
        rendered = self._render_draft("validation")
        self.assertLess(
            rendered.index("## Section 4. VVS Requirement Coverage Summary"),
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
        self.assertIn("| REQ-PDD-003 | validation | pdd.sectionC - Section C. Stakeholder Engagement | ReqPdd003Shape | passed |", completed.stdout)
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
        self.assertIn("| REQ-MR-001 | verification | pdd.sectionB.declaredImpacts - B.2 Declared Impacts; monitoring.observation - Measured Impact Observation | ReqMr001Shape | passed |", completed.stdout)
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
            coverage = output_dir / "validation-report.requirement-coverage.jsonld"
            validation = output_dir / "validation-report.validation.json"

            self.assertTrue(markdown.exists())
            self.assertTrue(pdf.exists())
            self.assertTrue(html.exists())
            self.assertTrue(metadata.exists())
            self.assertTrue(coverage.exists())
            self.assertTrue(validation.exists())

            self.assertIn(
                "## Section 4. VVS Requirement Coverage Summary",
                markdown.read_text(encoding="utf-8"),
            )
            self.assertIn(
                "## Section 1. Global Evaluation",
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
            self.assertEqual(
                metadata_payload["nias:requirementCoverageProofSidecar"]["path"],
                "validation-report.requirement-coverage.jsonld",
            )
            self.assertEqual(
                metadata_payload["nias:requirementCoverageProofSidecar"]["proofCount"],
                1,
            )

            validation_payload = json.loads(validation.read_text(encoding="utf-8"))
            self.assertEqual(validation_payload["status"], "passed")
            self.assertEqual(validation_payload["renderMode"], "final")
            self.assertEqual(validation_payload["reportType"], "validation")
            self.assertEqual(
                validation_payload["requirementCoverageProofSidecar"]["path"],
                "validation-report.requirement-coverage.jsonld",
            )

            coverage_graph = self._assert_coverage_sidecar_conforms(coverage)
            proofs = list(
                coverage_graph.subjects(RDF.type, NIAS.RequirementCoverageProof)
            )
            self.assertEqual(len(proofs), 1)
            proof = proofs[0]
            self.assertEqual(
                str(coverage_graph.value(proof, NIAS.coverageRequirementId)),
                "REQ-PDD-002",
            )
            self.assertEqual(
                str(coverage_graph.value(proof, NIAS.coverageAnchorKey)),
                "pdd.sectionB.declaredImpacts",
            )
            self.assertIn(
                str(coverage_graph.value(proof, NIAS.coverageAnchorKey)),
                self._canonical_anchor_keys_for_report("validation"),
            )
            self.assertEqual(
                str(
                    coverage_graph.value(
                        proof,
                        NIAS.coverageReviewedArtifactContentCid,
                    )
                ),
                "bafypddartifactcontentcid",
            )

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
                    "--output-target",
                    "pdf",
                ],
                check=True,
                capture_output=True,
                text=True,
                encoding="utf-8",
                cwd=REPO_ROOT,
            )

            markdown = output_dir / "verification-report.md"
            pdf = output_dir / "verification-report.pdf"
            metadata = output_dir / "verification-report.metadata.jsonld"
            coverage = output_dir / "verification-report.requirement-coverage.jsonld"
            validation = output_dir / "verification-report.validation.json"

            self.assertTrue(markdown.exists())
            self.assertTrue(pdf.exists())
            self.assertTrue(metadata.exists())
            self.assertTrue(coverage.exists())
            self.assertTrue(validation.exists())
            self.assertFalse((output_dir / "validation-report.md").exists())
            self.assertIn(
                "## Verification Report",
                markdown.read_text(encoding="utf-8"),
            )
            pdf_bytes = pdf.read_bytes()
            self.assertTrue(pdf_bytes.startswith(b"%PDF-"))
            self.assertIn(b"%%EOF", pdf_bytes[-1024:])

            validation_payload = json.loads(validation.read_text(encoding="utf-8"))
            self.assertEqual(validation_payload["status"], "passed")
            self.assertEqual(validation_payload["renderMode"], "final")
            self.assertEqual(validation_payload["reportType"], "verification")
            metadata_payload = json.loads(metadata.read_text(encoding="utf-8"))
            self.assertIn(
                "pdf",
                {
                    artifact["artifact"]
                    for artifact in metadata_payload["nias:artifacts"]
                },
            )
            self.assertEqual(metadata_payload["nias:artifactContentCid"], "bafyverificationartifactcid")
            self.assertEqual(metadata_payload["nias:reviewedArtifactType"], "monitoring-report")
            self.assertEqual(
                metadata_payload["nias:reviewedArtifactContentCid"],
                "bafymonitoringartifactcontentcid",
            )
            self.assertEqual(metadata_payload["nias:reviewedSubmissionTopicId"], "0.0.1001")
            self.assertEqual(
                metadata_payload["nias:reviewedSubmissionConsensusTimestamp"],
                "2026-05-24T10:00:00Z",
            )
            self.assertEqual(metadata_payload["nias:reviewedDlrContentCid"], "bafydlrcontentcid")
            self.assertEqual(
                metadata_payload["nias:requirementCoverageProofSidecar"]["path"],
                "verification-report.requirement-coverage.jsonld",
            )
            self.assertEqual(
                metadata_payload["nias:requirementCoverageProofSidecar"]["proofCount"],
                2,
            )

            coverage_graph = self._assert_coverage_sidecar_conforms(coverage)
            proofs = list(
                coverage_graph.subjects(RDF.type, NIAS.RequirementCoverageProof)
            )
            self.assertEqual(len(proofs), 2)
            self.assertEqual(
                {
                    str(coverage_graph.value(proof, NIAS.coverageRequirementId))
                    for proof in proofs
                },
                {"REQ-CROSS-001", "REQ-MR-001"},
            )
            self.assertEqual(
                {
                    str(coverage_graph.value(proof, NIAS.coverageAnchorKey))
                    for proof in proofs
                },
                {"monitoring.observation"},
            )
            proof_anchor_keys = {
                str(coverage_graph.value(proof, NIAS.coverageAnchorKey))
                for proof in proofs
            }
            self.assertTrue(
                proof_anchor_keys.issubset(
                    self._canonical_anchor_keys_for_report("verification")
                )
            )

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
            # reviewedArtifactContentCid is now shape-enforced; the structural
            # SHACL check fires before the renderer's final-mode guard.
            self.assertIn(
                "reviewedArtifactContentCid",
                completed.stderr,
            )

    def test_final_verification_rendering_requires_reviewed_mr_content_cid(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            invalid = tmp_path / "vv-missing-reviewed-monitoring-content-cid.jsonld"
            payload = json.loads(INPUT.read_text(encoding="utf-8"))
            review = next(
                node
                for node in payload
                if node.get("@id")
                == "https://nova.org.za/novaimpactaccountingstandard/test/vv-verification-review-1"
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
            # reviewedArtifactContentCid is now shape-enforced; the structural
            # SHACL check fires before the renderer's final-mode guard.
            self.assertIn(
                "reviewedArtifactContentCid",
                completed.stderr,
            )

    def test_final_verification_rendering_requires_reviewed_mr_submission_topic_id(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            invalid = tmp_path / "vv-missing-reviewed-monitoring-topic-id.jsonld"
            payload = json.loads(INPUT.read_text(encoding="utf-8"))
            review = next(
                node
                for node in payload
                if node.get("@id")
                == "https://nova.org.za/novaimpactaccountingstandard/test/vv-verification-review-1"
            )
            review.pop(
                "https://nova.org.za/novaimpactaccountingstandard/reviewedSubmissionTopicId",
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
                "reviewedSubmissionTopicId is required in final render mode.",
                completed.stderr,
            )

    def test_final_verification_rendering_requires_reviewed_mr_submission_consensus_timestamp(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            invalid = tmp_path / "vv-missing-reviewed-monitoring-timestamp.jsonld"
            payload = json.loads(INPUT.read_text(encoding="utf-8"))
            review = next(
                node
                for node in payload
                if node.get("@id")
                == "https://nova.org.za/novaimpactaccountingstandard/test/vv-verification-review-1"
            )
            review.pop(
                "https://nova.org.za/novaimpactaccountingstandard/reviewedSubmissionConsensusTimestamp",
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
                "reviewedSubmissionConsensusTimestamp is required in final render mode.",
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

    def test_final_verification_rendering_accepts_linked_dlr_content_cid_alias(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            aliased = tmp_path / "vv-linked-dlr-cid-alias.jsonld"
            payload = json.loads(INPUT.read_text(encoding="utf-8"))
            review = next(
                node
                for node in payload
                if node.get("@id")
                == "https://nova.org.za/novaimpactaccountingstandard/test/vv-verification-review-1"
            )
            reviewed_dlr_key = "https://nova.org.za/novaimpactaccountingstandard/reviewedDlrContentCid"
            linked_dlr_key = "https://nova.org.za/novaimpactaccountingstandard/linkedDlrContentCid"
            review[linked_dlr_key] = review.pop(reviewed_dlr_key)
            aliased.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")

            output_dir = tmp_path / "output"
            subprocess.run(
                [
                    *self._base_command(),
                    "--report-type",
                    "verification",
                    "--input-jsonld",
                    str(aliased),
                    "--evidence-jsonld",
                    str(EVIDENCE),
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
            metadata_payload = json.loads(
                (output_dir / "verification-report.metadata.jsonld").read_text(encoding="utf-8")
            )
            self.assertEqual(metadata_payload["nias:reviewedDlrContentCid"], "bafydlrcontentcid")


if __name__ == "__main__":
    unittest.main()
