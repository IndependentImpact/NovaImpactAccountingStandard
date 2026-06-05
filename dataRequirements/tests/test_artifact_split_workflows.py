import unittest
from pathlib import Path

import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]
WORKFLOWS = REPO_ROOT / "dataRequirements/shape2flutter/workflows"
SHAPE2FLUTTER_ROOT = REPO_ROOT / "dataRequirements/shape2flutter"


class ArtifactSplitWorkflowTests(unittest.TestCase):
    def _workflow(self, filename: str) -> dict:
        return yaml.safe_load((WORKFLOWS / filename).read_text(encoding="utf-8"))

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
                "PddSectionCStakeholderEngagementShape",
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
            ["GenericDocumentReviewShape"],
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


if __name__ == "__main__":
    unittest.main()
