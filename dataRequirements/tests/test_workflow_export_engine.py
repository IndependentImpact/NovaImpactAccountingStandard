import unittest
from pathlib import Path
import sys

REPO_ROOT = Path(__file__).resolve().parents[2]
TOOL_DIR = REPO_ROOT / "dataRequirements/document-rendering/tool"
sys.path.insert(0, str(TOOL_DIR))
from export_workflow_report import evaluate_final_gate_failures, load_export_config

NIAS = "https://nova.org.za/novaimpactaccountingstandard/"


class WorkflowExportEngineTests(unittest.TestCase):
    def test_pdd_export_config_has_expected_final_gates(self):
        config = load_export_config(
            REPO_ROOT / "dataRequirements/document-rendering/config/pdd-export.yaml"
        )
        gates = config["final_gate_requirements"]
        self.assertEqual(set(gates.keys()), {"a", "b", "c"})
        self.assertEqual(gates["a"]["required_review_of"], f"{NIAS}documents/pdd-alpha/pddA")

    def test_final_gate_failures_are_config_driven(self):
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
        self.assertIn("PDD-B validation review is not approved.", failures)
        self.assertIn("PDD-C validation review has not been submitted.", failures)

    def test_second_report_type_uses_shared_export_config(self):
        config = load_export_config(
            REPO_ROOT
            / "dataRequirements/document-rendering/config/validation-verification-export.yaml"
        )
        self.assertEqual(
            config["renderer_script"],
            "dataRequirements/document-rendering/tool/render_validation_verification_report_markdown.py",
        )
        self.assertEqual(config["default_output_targets"], ["markdown"])


if __name__ == "__main__":
    unittest.main()
