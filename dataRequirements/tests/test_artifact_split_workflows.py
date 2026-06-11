import unittest
from pathlib import Path

import yaml
from rdflib import Graph, Namespace, URIRef
from rdflib.namespace import RDF


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / "dataRequirements/shape2flutter/workflows"
SHAPE2FLUTTER_ROOT = REPO_ROOT / "dataRequirements/shape2flutter"

NIAS = Namespace("https://nova.org.za/novaimpactaccountingstandard/")
SH = Namespace("http://www.w3.org/ns/shacl#")

PRIMARY_WORKFLOW_BUNDLES = {
    "pdd-design.yaml": "dataRequirements/shape2flutter/pdd-design-ui-shapes.ttl",
    "validation-report.yaml": "dataRequirements/shape2flutter/validation-report-ui-shapes.ttl",
    "monitoring-report.yaml": "dataRequirements/shape2flutter/monitoring-report-ui-shapes.ttl",
    "verification-report.yaml": "dataRequirements/shape2flutter/verification-report-ui-shapes.ttl",
}


class ArtifactSplitWorkflowTests(unittest.TestCase):
    def _workflow(self, filename: str) -> dict:
        return yaml.safe_load((WORKFLOWS / filename).read_text(encoding="utf-8"))

    def _canonical_source_graph(self, workflow: dict) -> Graph:
        graph = Graph()
        for relative_path in workflow["canonical_bundle"]["canonical_shape_sources"]:
            graph.parse(REPO_ROOT / relative_path, format="turtle")
        return graph

    def test_split_workflow_files_exist(self):
        expected = {
            "pdd-design.yaml",
            "validation-report.yaml",
            "monitoring-report.yaml",
            "verification-report.yaml",
        }

        for filename in expected:
            with self.subTest(filename=filename):
                self.assertTrue((WORKFLOWS / filename).exists())

    def test_workflow_ids_are_unique(self):
        workflow_ids = []
        for path in WORKFLOWS.glob("*.yaml"):
            workflow_ids.append(self._workflow(path.name)["workflow_id"])

        self.assertEqual(len(workflow_ids), len(set(workflow_ids)))

    def test_all_workflows_declare_common_artifact_identity_fields(self):
        expected_common_fields = {
            "artifactContentCid",
            "artifactSchemaCid",
            "artifactSchemaVersionLabel",
            "artifactAuthor",
            "workflowSubject",
            "submissionTopicId",
            "submissionConsensusTimestamp",
            "submissionEventKey",
            "submissionMessageUrl",
        }

        for filename in [
            "pdd-design.yaml",
            "validation-report.yaml",
            "monitoring-report.yaml",
            "verification-report.yaml",
        ]:
            with self.subTest(filename=filename):
                workflow = self._workflow(filename)
                self.assertTrue(
                    expected_common_fields.issubset(
                        set(workflow["artifact_identity_fields"])
                    )
                )

    def test_pdd_design_workflow_contains_only_pdd_capture_steps(self):
        workflow = self._workflow("pdd-design.yaml")

        self.assertEqual(workflow["artifact_type"], "pdd")
        self.assertEqual(workflow["owner_role"], "project-developer")
        self.assertNotIn("reviewed_artifact", workflow)
        self.assertEqual(workflow["outputs"], ["pdd"])
        self.assertEqual(
            [step["form"] for step in workflow["steps"]],
            [
                "PddSectionAReportShape",
                "PddSectionBReportShape",
                "PddSectionCShape",
            ],
        )
        self.assertFalse(
            any("Review" in step["form"] for step in workflow["steps"]),
            msg="PDD design must not own validation review forms.",
        )

    def test_validation_report_workflow_reviews_pdd(self):
        workflow = self._workflow("validation-report.yaml")

        self.assertEqual(workflow["artifact_type"], "validation-report")
        self.assertEqual(workflow["owner_role"], "validator")
        self.assertEqual(workflow["reviewed_artifact"], "pdd")
        self.assertEqual(workflow["outputs"], ["validation-report"])
        self.assertEqual(
            [step["form"] for step in workflow["steps"]],
            ["GlobalQualitativeDocumentReviewShape"],
        )

    def test_monitoring_report_workflow_reports_against_pdd(self):
        workflow = self._workflow("monitoring-report.yaml")

        self.assertEqual(workflow["artifact_type"], "monitoring-report")
        self.assertEqual(workflow["owner_role"], "monitoring-party")
        self.assertEqual(workflow["reviewed_artifact"], "pdd")
        self.assertEqual(workflow["outputs"], ["monitoring-report"])
        self.assertEqual(
            [step["form"] for step in workflow["steps"]],
            ["MonitoringReportShape"],
        )

    def test_verification_report_workflow_reviews_monitoring_report(self):
        workflow = self._workflow("verification-report.yaml")

        self.assertEqual(workflow["artifact_type"], "verification-report")
        self.assertEqual(workflow["owner_role"], "verifier")
        self.assertEqual(workflow["reviewed_artifact"], "monitoring-report")
        self.assertEqual(workflow["outputs"], ["verification-report"])
        self.assertEqual(
            [step["form"] for step in workflow["steps"]],
            ["VerifiedImpactCertificateIssuanceRequestReviewShape"],
        )

    def test_split_ui_bundle_files_exist(self):
        expected = {
            "pdd-design-ui-shapes.ttl",
            "monitoring-report-ui-shapes.ttl",
            "validation-report-ui-shapes.ttl",
            "verification-report-ui-shapes.ttl",
        }

        for filename in expected:
            with self.subTest(filename=filename):
                self.assertTrue((SHAPE2FLUTTER_ROOT / filename).exists())

    def test_pdd_design_ui_bundle_contains_only_pdd_capture_forms(self):
        bundle = (SHAPE2FLUTTER_ROOT / "pdd-design-ui-shapes.ttl").read_text(
            encoding="utf-8"
        )

        for expected_shape in [
            "PddSectionAUiShape",
            "PddSectionBUiShape",
            "PddSectionCUiShape",
        ]:
            with self.subTest(expected_shape=expected_shape):
                self.assertIn(expected_shape, bundle)

        for excluded_shape in [
            "PddCertificateIssuanceRequestUiShape",
            "PddSectionAValidationReviewUiShape",
            "PddSectionBValidationReviewUiShape",
            "PddSectionCValidationReviewUiShape",
            "DocumentFieldReviewUiShape",
            "ReviewTargetUiShape",
        ]:
            with self.subTest(excluded_shape=excluded_shape):
                self.assertNotIn(excluded_shape, bundle)

    def test_pdd_design_build_script_uses_pdd_design_bundle(self):
        design_script = (SHAPE2FLUTTER_ROOT / "build-pdd-design.sh").read_text(
            encoding="utf-8"
        )

        self.assertIn("pdd-design-ui-shapes.ttl", design_script)
        self.assertIn("pdd-design", design_script)
        self.assertNotIn("pdd-workflow-ui-shapes.ttl", design_script)

    def test_validation_and_verification_build_scripts_use_split_bundles(self):
        validation_script = (
            SHAPE2FLUTTER_ROOT / "build-validation-report.sh"
        ).read_text(encoding="utf-8")
        verification_script = (
            SHAPE2FLUTTER_ROOT / "build-verification-report.sh"
        ).read_text(encoding="utf-8")

        self.assertIn("validation-report-ui-shapes.ttl", validation_script)
        self.assertNotIn("validation-verification-ui-shapes.ttl", validation_script)
        self.assertIn("verification-report-ui-shapes.ttl", verification_script)
        self.assertNotIn("validation-verification-ui-shapes.ttl", verification_script)

    def test_primary_workflows_declare_canonical_bundle_contract(self):
        for filename, expected_ui_bundle in PRIMARY_WORKFLOW_BUNDLES.items():
            with self.subTest(filename=filename):
                workflow = self._workflow(filename)
                canonical_bundle = workflow["canonical_bundle"]

                self.assertEqual(
                    canonical_bundle["ui_shape_bundle"],
                    expected_ui_bundle,
                )
                self.assertEqual(
                    canonical_bundle["generated_output_status"],
                    "downstream-generated",
                )
                self.assertGreater(
                    len(canonical_bundle["canonical_shape_sources"]),
                    0,
                )

    def test_primary_workflow_canonical_sources_exist_and_parse(self):
        for filename in PRIMARY_WORKFLOW_BUNDLES:
            workflow = self._workflow(filename)
            for relative_path in workflow["canonical_bundle"]["canonical_shape_sources"]:
                with self.subTest(filename=filename, relative_path=relative_path):
                    path = REPO_ROOT / relative_path
                    self.assertTrue(path.exists())
                    self.assertNotIn("/generated/", relative_path)
                    graph = Graph()
                    graph.parse(path, format="turtle")
                    self.assertGreater(len(graph), 0)

    def test_primary_workflow_forms_are_backed_by_canonical_node_shapes(self):
        for filename in PRIMARY_WORKFLOW_BUNDLES:
            workflow = self._workflow(filename)
            canonical_graph = self._canonical_source_graph(workflow)

            for step in workflow["steps"]:
                shape = URIRef(f"{NIAS}{step['form']}")
                with self.subTest(filename=filename, form=step["form"]):
                    self.assertIn(
                        (shape, RDF.type, SH.NodeShape),
                        canonical_graph,
                        msg=(
                            f"{step['form']} must be defined as a sh:NodeShape "
                            "in the workflow's canonical_shape_sources."
                        ),
                    )

    def test_primary_workflow_ui_bundles_exist_and_parse(self):
        for filename, relative_path in PRIMARY_WORKFLOW_BUNDLES.items():
            with self.subTest(filename=filename, relative_path=relative_path):
                path = REPO_ROOT / relative_path
                self.assertTrue(path.exists())
                graph = Graph()
                graph.parse(path, format="turtle")
                self.assertGreater(len(graph), 0)

    def test_validation_report_ui_shape_language_is_pdd_specific(self):
        bundle = (SHAPE2FLUTTER_ROOT / "validation-report-ui-shapes.ttl").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "1.1 Global PDD qualitative evaluation (validation guiding questions GQ-001, GQ-002, GQ-005, GQ-007)",
            bundle,
        )
        self.assertIn(
            "2.0 PDD section-level qualitative evaluation (validation guiding question GQ-005)",
            bundle,
        )
        self.assertIn(
            "3.0 PDD paragraph-level validation findings (per PDD anchor definitions)",
            bundle,
        )
        self.assertIn(
            "4.0 Final validation decision (approve or reject the PDD)",
            bundle,
        )
        self.assertIn("IRI of the PDD version being validated.", bundle)
        self.assertIn(
            "IRI of the specific PDD anchor (section or paragraph) being validated. Refer to pdd-anchor-definitions.ttl.",
            bundle,
        )
        self.assertNotIn("Monitoring Report version being verified", bundle)

    def test_verification_report_ui_shape_language_is_monitoring_specific(self):
        bundle = (SHAPE2FLUTTER_ROOT / "verification-report-ui-shapes.ttl").read_text(
            encoding="utf-8"
        )

        self.assertIn(
            "1.0 Verification workflow submission context",
            bundle,
        )
        self.assertIn(
            "1.1 Monitoring Report global qualitative evaluation (verification guiding questions GQ-003, GQ-004, GQ-006, GQ-008)",
            bundle,
        )
        self.assertIn(
            "2.0 Monitoring Report paragraph-level verification findings (per MR/DLR anchor definitions)",
            bundle,
        )
        self.assertIn(
            "3.0 Final verification decision (approve or reject the Monitoring Report)",
            bundle,
        )
        self.assertIn(
            "IRI of the Monitoring Report version being verified.",
            bundle,
        )
        self.assertIn(
            "IRI of the specific Monitoring Report or Data Lineage Report anchor being verified. Refer to monitoring-anchor-definitions.ttl and dlr-anchor-definitions.ttl.",
            bundle,
        )
        self.assertNotIn("PDD version being validated", bundle)


if __name__ == "__main__":
    unittest.main()
