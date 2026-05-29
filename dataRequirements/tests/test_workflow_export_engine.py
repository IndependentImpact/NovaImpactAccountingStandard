import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = REPO_ROOT / "dataRequirements/document-rendering/tool"
sys.path.insert(0, str(TOOL_DIR))
from export_workflow_report import evaluate_final_gate_failures, load_export_config

NIAS = "https://nova.org.za/novaimpactaccountingstandard/"


class WorkflowExportEngineTests(unittest.TestCase):
    def test_pdd_export_config_has_no_validation_review_gate(self):
        config = load_export_config(
            REPO_ROOT / "dataRequirements/document-rendering/config/pdd-export.yaml"
        )
        self.assertNotIn("final_gate_requirements", config)

    def test_final_gate_failures_are_noop_without_gate_config(self):
        config = load_export_config(
            REPO_ROOT / "dataRequirements/document-rendering/config/pdd-export.yaml"
        )
        review_payloads = {
            "a": {
                f"{NIAS}finalReviewDecision": f"{NIAS}review-approve",
                f"{NIAS}isReviewOf": f"{NIAS}documents/pdd-alpha/pddA",
            },
            "b": {
                f"{NIAS}finalReviewDecision": f"{NIAS}review-reject",
                f"{NIAS}isReviewOf": f"{NIAS}documents/pdd-alpha/pddB",
            },
            "c": None,
        }
        failures = evaluate_final_gate_failures(config, review_payloads)
        self.assertEqual(failures, [])

    def test_validation_and_verification_use_split_export_configs(self):
        validation_config = load_export_config(
            REPO_ROOT
            / "dataRequirements/document-rendering/config/validation-report-export.yaml"
        )
        verification_config = load_export_config(
            REPO_ROOT
            / "dataRequirements/document-rendering/config/verification-report-export.yaml"
        )
        self.assertEqual(
            validation_config["renderer_script"],
            "dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py",
        )
        self.assertEqual(validation_config["default_output_targets"], ["markdown"])
        self.assertEqual(
            verification_config["renderer_script"],
            validation_config["renderer_script"],
        )
        self.assertEqual(verification_config["default_output_targets"], ["markdown"])
        self.assertEqual(
            validation_config["payload_filename"],
            "validation-report-review-package.jsonld",
        )
        self.assertEqual(
            verification_config["payload_filename"],
            "verification-report-review-package.jsonld",
        )

    def test_monitoring_report_export_config_uses_monitoring_renderer(self):
        config = load_export_config(
            REPO_ROOT
            / "dataRequirements/document-rendering/config/monitoring-report-export.yaml"
        )
        self.assertEqual(
            config["renderer_script"],
            "dataRequirements/document-rendering/tool/render_monitoring_report_markdown.py",
        )
        self.assertEqual(config["payload_filename"], "monitoring-report-package.jsonld")
        self.assertEqual(config["default_output_targets"], ["markdown"])


if __name__ == "__main__":
    unittest.main()
