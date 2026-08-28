from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CustomerGovernanceReferenceCaseTest(unittest.TestCase):
    def test_reference_case_executes_all_failure_contracts(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "reference-case"
            subprocess.run(
                [
                    sys.executable,
                    "scripts/run_customer_governance_reference_case.py",
                    "--output",
                    str(output),
                ],
                check=True,
            )

            packet = json.loads((output / "assurance-packet.json").read_text(encoding="utf-8"))
            self.assertEqual(packet["format"], "sao-reference-assurance-packet/0.1")
            self.assertEqual(packet["case"]["id"], "customer-governance-o2c")
            self.assertEqual(packet["summary"]["scenarios"], 9)
            self.assertEqual(packet["summary"]["passed"], 9)
            self.assertTrue(packet["summary"]["all_contracts_passed"])
            self.assertGreaterEqual(packet["summary"]["repository_refs_checked"], 8)

            results = {result["scenario"]: result for result in packet["results"]}
            self.assertEqual(
                results["missing-current-event"]["classification"],
                "current_outbound_event_not_proven",
            )
            self.assertIn(
                "reprocess_old_successful_message",
                results["missing-current-event"]["blocked_actions"],
            )
            self.assertEqual(results["mapping-drift"]["classification"], "mapping_version_drift")
            self.assertIn("execute", results["mapping-drift"]["blocked_actions"])
            self.assertEqual(results["resolved"]["classification"], "business_state_verified")

            for result in packet["results"]:
                self.assertTrue(all(result["assertions"].values()))
                report_path = output / result["report"]
                self.assertTrue(report_path.exists(), report_path)

            review = (output / "architecture-operations-review.md").read_text(encoding="utf-8")
            self.assertIn("## Business outcome", review)
            self.assertIn("## Executed failure campaign", review)
            self.assertIn("## Cutover authority-transition variant", review)
            self.assertIn("## AMS / operations handover", review)
            self.assertIn("## Deliberate limitations", review)


if __name__ == "__main__":
    unittest.main()
