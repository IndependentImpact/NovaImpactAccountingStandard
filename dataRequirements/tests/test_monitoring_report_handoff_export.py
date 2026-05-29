import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT = (
    REPO_ROOT
    / "dataRequirements/shape2flutter/monitoring_report/tool/export_monitoring_report_markdown.py"
)

DCTERMS = "http://purl.org/dc/terms/"
DATA = "https://jellyfiiish.xyz/ns/"
HEDERA = "https://hashgraphontology.xyz/core/"
IND = "http://independentimpact.org/indicator-owl/"
NIAS = "https://nova.org.za/novaimpactaccountingstandard/"
TIME = "http://www.w3.org/2006/time#"


class MonitoringReportHandoffExportTests(unittest.TestCase):
    def test_monitoring_form_is_wrapped_and_rendered_final(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            monitoring_json = tmp_path / "monitoring-report-form.json"
            package_jsonld = tmp_path / "monitoring-package.jsonld"
            output = tmp_path / "monitoring-report.md"

            monitoring_json.write_text(
                json.dumps(_monitoring_form_payload()),
                encoding="utf-8",
            )

            subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--monitoring-json",
                    str(monitoring_json),
                    "--monitoring-report-id",
                    f"{NIAS}test/handoff-monitoring-report",
                    "--monitoring-package-output",
                    str(package_jsonld),
                    "--document-author",
                    f"{NIAS}test/monitoring-party-1",
                    "--resource-ipfs-uri",
                    "ipfs://bafyhandoffmonitoringreport",
                    "--workflow-step-label",
                    "Submit monitoring report handoff",
                    "--source-artifact-id",
                    "monitoring-report-form.json",
                    "--generated-at",
                    "2026-05-28T00:00:00Z",
                    "--render-mode",
                    "final",
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
            self.assertIn("## Monitoring Report", rendered)
            self.assertIn("ipfs://bafyhandoffmonitoringreport", rendered)
            self.assertIn("Approved monitoring dataset Q2 2026", rendered)
            self.assertIn("Submit monitoring report handoff", rendered)

            package = json.loads(package_jsonld.read_text(encoding="utf-8"))
            report_node = next(
                node
                for node in package
                if node["@id"] == f"{NIAS}test/handoff-monitoring-report"
            )
            self.assertIn(DATA + "Document", report_node["@type"])
            self.assertIn(NIAS + "MonitoringReport", report_node["@type"])
            self.assertEqual(
                report_node[f"{NIAS}documentSchema"][0]["@id"],
                f"{NIAS}document-schema/MonitoringReport-6.0.0",
            )
            self.assertEqual(
                report_node[f"{NIAS}alignedWithPDD"][0]["@id"],
                f"{NIAS}test/pdd-version-2",
            )


def _monitoring_form_payload():
    return {
        f"{NIAS}hasWorkflowSubmission": {
            f"{NIAS}submittedDocument": f"{NIAS}test/handoff-monitoring-report",
            f"{NIAS}workflow": f"{NIAS}workflows/monitoring-report",
            f"{NIAS}workflowStep": f"{NIAS}workflow-steps/monitoring-report",
            f"{NIAS}workflowSubject": f"{NIAS}test/project-1",
            f"{NIAS}workflowDocumentSubmittedBy": f"{NIAS}test/monitoring-party-1",
            f"{NIAS}workflowDocumentRecipient": f"{NIAS}test/registry-1",
            f"{NIAS}workflowSubmissionConsensusMessage": {
                f"{HEDERA}inTopic": f"{NIAS}test/topic-1",
                f"{HEDERA}hasSequenceNumber": 51,
                f"{HEDERA}hasConsensusTimestamp": "2026-07-01T00:00:00Z",
            },
        },
        f"{NIAS}alignedWithPDD": f"{NIAS}test/pdd-version-2",
        f"{NIAS}reportedIndicatorLabel": "Households served",
        f"{NIAS}forPeriod": {
            f"{TIME}hasBeginning": {
                f"{TIME}inXSDDateTimeStamp": "2026-04-01T00:00:00Z",
            },
            f"{TIME}hasEnd": {
                f"{TIME}inXSDDateTimeStamp": "2026-06-30T23:59:59Z",
            },
        },
        f"{NIAS}reportedObservation": {
            f"{IND}observesIndicator": f"{NIAS}test/indicator-households-served",
            f"{IND}obsValue": 42,
            f"{IND}hasUnit": "http://qudt.org/vocab/unit/NUM",
        },
        f"{NIAS}usesDataset": [
            {
                f"{DCTERMS}title": "Approved monitoring dataset Q2 2026",
                f"{NIAS}dataLineageReview": {
                    f"{NIAS}documentMessageId": "0.0.1001-1704067200-000000005",
                    f"{NIAS}resourceIpfsUri": "ipfs://bafyhandoffdatareview",
                },
                f"{NIAS}finalDatasetArtifact": {
                    f"{NIAS}resourceIpfsUri": "ipfs://bafyhandoffdataset",
                },
            }
        ],
        f"{NIAS}calculationCode": {
            f"{NIAS}resourceIpfsUri": "ipfs://bafyhandoffcalculationcode",
        },
        f"{NIAS}impactResultResource": {
            f"{NIAS}resourceIpfsUri": "ipfs://bafyhandoffimpactresult",
        },
        f"{NIAS}calculationReport": {
            f"{NIAS}resourceIpfsUri": "ipfs://bafyhandoffcalculationreport",
        },
        f"{NIAS}requestedIssuanceAccountId": "0.0.4004",
    }


if __name__ == "__main__":
    unittest.main()
