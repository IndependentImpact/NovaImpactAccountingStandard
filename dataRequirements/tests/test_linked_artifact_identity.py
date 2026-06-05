import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURES = REPO_ROOT / "dataRequirements/document-rendering/fixtures"
PDD_RENDERER = REPO_ROOT / "dataRequirements/document-rendering/tool/render_pdd_markdown.py"
MR_RENDERER = REPO_ROOT / "dataRequirements/document-rendering/tool/render_monitoring_report_markdown.py"
VV_RENDERER = REPO_ROOT / "dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py"


class LinkedArtifactIdentityTests(unittest.TestCase):
    def test_pdd_metadata_exposes_author_and_submission_identity(self):
        import importlib.util
        from rdflib import Graph

        spec = importlib.util.spec_from_file_location(
            "render_pdd_markdown",
            str(REPO_ROOT / "dataRequirements/document-rendering/tool/render_pdd_markdown.py"),
        )
        module = importlib.util.module_from_spec(spec)
        assert spec.loader is not None
        sys.path.insert(0, str(REPO_ROOT / "dataRequirements/document-rendering/tool"))
        spec.loader.exec_module(module)
        graph = Graph().parse(str(FIXTURES / "pdd-alpha-input.jsonld"), format="json-ld")
        metadata = module._pdd_identity_metadata(graph)
        self.assertIn("nias:artifactSchemaCid", metadata)
        self.assertIn("nias:artifactSchemaVersionLabel", metadata)
        self.assertIn("nias:artifactAuthor", metadata)
        self.assertIn("nias:submissionTopicId", metadata)
        self.assertIn("nias:submissionConsensusTimestamp", metadata)
        self.assertIn("nias:submissionEventKey", metadata)
        self.assertIn("nias:submissionMessageUrl", metadata)

    def test_validation_and_verification_metadata_record_exact_reviewed_artifacts(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "validation"
            subprocess.run(
                [
                    sys.executable,
                    str(VV_RENDERER),
                    "--report-type",
                    "validation",
                    "--input-jsonld",
                    str(FIXTURES / "validation-verification-report-input.jsonld"),
                    "--evidence-jsonld",
                    str(FIXTURES / "validation-verification-report-evidence.jsonld"),
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
                cwd=REPO_ROOT,
            )
            validation_metadata = json.loads(
                (output_dir / "validation-report.metadata.jsonld").read_text(encoding="utf-8")
            )
            self.assertEqual(validation_metadata["nias:reviewedArtifactType"], "pdd")
            self.assertIn("nias:artifactSchemaCid", validation_metadata)
            self.assertIn("nias:artifactSchemaVersionLabel", validation_metadata)
            self.assertIn("nias:artifactAuthor", validation_metadata)
            self.assertIn("nias:submissionEventKey", validation_metadata)
            self.assertIn("nias:submissionMessageUrl", validation_metadata)
            self.assertIn("nias:reviewedArtifactContentCid", validation_metadata)
            self.assertIn("nias:reviewedArtifactSchemaCid", validation_metadata)
            self.assertIn("nias:reviewedArtifactSchemaVersionLabel", validation_metadata)
            self.assertIn("nias:reviewedSubmissionTopicId", validation_metadata)
            self.assertIn("nias:reviewedSubmissionConsensusTimestamp", validation_metadata)

            verification_output_dir = Path(tmpdir) / "verification"
            subprocess.run(
                [
                    sys.executable,
                    str(VV_RENDERER),
                    "--report-type",
                    "verification",
                    "--input-jsonld",
                    str(FIXTURES / "validation-verification-report-input.jsonld"),
                    "--evidence-jsonld",
                    str(FIXTURES / "validation-verification-report-evidence.jsonld"),
                    "--render-mode",
                    "final",
                    "--output-dir",
                    str(verification_output_dir),
                    "--output-target",
                    "markdown",
                ],
                check=True,
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            verification_metadata = json.loads(
                (verification_output_dir / "verification-report.metadata.jsonld").read_text(encoding="utf-8")
            )
            self.assertEqual(verification_metadata["nias:reviewedArtifactType"], "monitoring-report")
            self.assertIn("nias:artifactSchemaCid", verification_metadata)
            self.assertIn("nias:artifactSchemaVersionLabel", verification_metadata)
            self.assertIn("nias:artifactAuthor", verification_metadata)
            self.assertIn("nias:submissionEventKey", verification_metadata)
            self.assertIn("nias:submissionMessageUrl", verification_metadata)
            self.assertIn("nias:reviewedArtifactContentCid", verification_metadata)
            self.assertIn("nias:reviewedArtifactSchemaCid", verification_metadata)
            self.assertIn("nias:reviewedArtifactSchemaVersionLabel", verification_metadata)
            self.assertIn("nias:reviewedSubmissionTopicId", verification_metadata)
            self.assertIn("nias:reviewedSubmissionConsensusTimestamp", verification_metadata)
            self.assertIn("nias:reviewedDlrContentCid", verification_metadata)

    def test_monitoring_metadata_records_aligned_pdd_and_linked_dlr(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            output_dir = Path(tmpdir) / "monitoring"
            subprocess.run(
                [
                    sys.executable,
                    str(MR_RENDERER),
                    "--input-jsonld",
                    str(FIXTURES / "monitoring-report-input.jsonld"),
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
                cwd=REPO_ROOT,
            )
            metadata = json.loads(
                (output_dir / "monitoring-report.metadata.jsonld").read_text(encoding="utf-8")
            )
            self.assertIn("nias:artifactSchemaCid", metadata)
            self.assertIn("nias:artifactSchemaVersionLabel", metadata)
            self.assertIn("nias:artifactAuthor", metadata)
            self.assertIn("nias:submissionEventKey", metadata)
            self.assertIn("nias:submissionMessageUrl", metadata)
            self.assertIn("nias:alignedPddContentCid", metadata)
            self.assertIn("nias:alignedPddSubmissionTopicId", metadata)
            self.assertIn("nias:alignedPddSubmissionConsensusTimestamp", metadata)
            self.assertIn("nias:linkedDlrContentCid", metadata)

    def test_final_render_rejects_missing_reviewed_identity(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            invalid = tmp / "invalid-vv.jsonld"
            payload = json.loads((FIXTURES / "validation-verification-report-input.jsonld").read_text())
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
                    sys.executable,
                    str(VV_RENDERER),
                    "--report-type",
                    "validation",
                    "--input-jsonld",
                    str(invalid),
                    "--evidence-jsonld",
                    str(FIXTURES / "validation-verification-report-evidence.jsonld"),
                    "--render-mode",
                    "final",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            self.assertNotEqual(completed.returncode, 0)
            # reviewedArtifactContentCid is now shape-enforced; the structural
            # SHACL check fires before the renderer's final-mode guard.
            self.assertIn("reviewedArtifactContentCid", completed.stderr)

    def test_final_render_rejects_missing_dlr_reference(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp = Path(tmpdir)
            invalid = tmp / "invalid-vv-dlr.jsonld"
            payload = json.loads((FIXTURES / "validation-verification-report-input.jsonld").read_text())
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
                    sys.executable,
                    str(VV_RENDERER),
                    "--report-type",
                    "verification",
                    "--input-jsonld",
                    str(invalid),
                    "--evidence-jsonld",
                    str(FIXTURES / "validation-verification-report-evidence.jsonld"),
                    "--render-mode",
                    "final",
                ],
                check=False,
                capture_output=True,
                text=True,
                cwd=REPO_ROOT,
            )
            self.assertNotEqual(completed.returncode, 0)
            self.assertIn("reviewedDlrContentCid is required in final render mode.", completed.stderr)

    def test_shacl_rejects_review_in_ui_only_state(self):
        from pyshacl import validate
        from rdflib import Graph

        shapes_graph = Graph()
        for ttl in [
            REPO_ROOT / "dataRequirements/common-shapes.ttl",
            REPO_ROOT / "dataRequirements/artifact-anchor-shapes.ttl",
            REPO_ROOT / "dataRequirements/document-shapes.ttl",
            REPO_ROOT / "dataRequirements/document-reference-shapes.ttl",
            REPO_ROOT / "dataRequirements/review-shapes.ttl",
        ]:
            shapes_graph.parse(str(ttl))

        ontology_graph = Graph()
        for ttl in [
            REPO_ROOT / "glossary/NovaImpactAccountingStandardOntology.ttl",
            REPO_ROOT / "glossary/NovaImpactAccountingStandardGlossary.ttl",
        ]:
            ontology_graph.parse(str(ttl))

        # Build a minimal review document that has field reviews but no
        # hasWorkflowSubmission (UI-only state — the reviewer filled in
        # findings but the document was never submitted to the canonical
        # workflow pipeline).
        data_graph = Graph()
        data_graph.parse(
            data="""
@prefix data: <https://jellyfiiish.xyz/ns/> .
@prefix nias-cs: <https://nova.org.za/novaimpactaccountingstandard/> .
@prefix nias-o: <https://nova.org.za/novaimpactaccountingstandard/> .
@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .

<https://nova.org.za/novaimpactaccountingstandard/test/ui-only-review-1>
    a data:Document, nias-o:GenericDocumentReview ;
    nias-o:documentSchema <https://nova.org.za/novaimpactaccountingstandard/document-schema/GenericDocumentReview-5.0.0> ;
    nias-o:isEncrypted false ;
    nias-o:documentAuthor <https://nova.org.za/novaimpactaccountingstandard/test/reviewer-1> ;
    nias-o:authProof nias-o:none ;
    nias-o:resourceIpfsUri "ipfs://bafyuionlyreview"^^xsd:anyURI ;
    nias-o:fieldReview <https://nova.org.za/novaimpactaccountingstandard/test/ui-field-review-1> ;
    nias-o:reviewedArtifactType "pdd" ;
    nias-o:reviewedArtifactContentCid "bafyuionlyreviewedcid" ;
    nias-o:finalReviewDecision nias-cs:review-approve .
""",
            format="turtle",
        )

        conforms, _, _ = validate(
            data_graph=data_graph,
            shacl_graph=shapes_graph,
            ont_graph=ontology_graph,
            inference="none",
            abort_on_first=False,
            allow_infos=False,
            allow_warnings=False,
            advanced=True,
        )
        self.assertFalse(
            conforms,
            msg="A review document without hasWorkflowSubmission (UI-only state) must not conform.",
        )


if __name__ == '__main__':
    unittest.main()

