from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


class CustomerGovernanceReferenceCaseTest(unittest.TestCase):
    def test_reference_case_executes_incident_and_control_plane_contracts(self) -> None:
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
            self.assertEqual(packet["format"], "sao-reference-assurance-packet/0.2")
            self.assertEqual(packet["case"]["id"], "customer-governance-o2c")
            self.assertEqual(packet["summary"]["incident_scenarios"], 9)
            self.assertEqual(packet["summary"]["control_plane_checks"], 5)
            self.assertEqual(packet["summary"]["scenarios"], 14)
            self.assertEqual(packet["summary"]["passed"], 14)
            self.assertTrue(packet["summary"]["all_contracts_passed"])
            self.assertGreaterEqual(packet["summary"]["repository_refs_checked"], 10)

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

            controls = {result["scenario"]: result for result in packet["control_plane_results"]}
            self.assertEqual(
                set(controls),
                {
                    "approved-governed-recovery",
                    "stale-recovery-approval",
                    "failed-business-postcondition",
                    "duplicate-business-event",
                    "untrusted-runbook-instruction",
                },
            )
            self.assertTrue(all(result["passed"] for result in controls.values()))

            approved = json.loads(
                (output / controls["approved-governed-recovery"]["artifact"]).read_text(encoding="utf-8")
            )
            self.assertEqual(approved["execution"]["status"], "executed")
            self.assertEqual(approved["after_state"]["attributes"]["delivery_control"], "NEW")
            self.assertTrue(approved["trace_evaluation"]["passed"])
            self.assertTrue((output / approved["trace"]).exists())

            stale = json.loads(
                (output / controls["stale-recovery-approval"]["artifact"]).read_text(encoding="utf-8")
            )
            self.assertEqual(stale["execution"]["reason"], "approval_expired")
            self.assertEqual(stale["after_state"]["attributes"]["delivery_control"], "OLD")

            failed_post = json.loads(
                (output / controls["failed-business-postcondition"]["artifact"]).read_text(encoding="utf-8")
            )
            self.assertEqual(failed_post["execution"]["reason"], "business_postcondition_failed")
            self.assertEqual(failed_post["after_state"]["attributes"]["delivery_control"], "OLD")

            duplicate = json.loads(
                (output / controls["duplicate-business-event"]["artifact"]).read_text(encoding="utf-8")
            )
            self.assertEqual(
                [row["status"] for row in duplicate["deliveries"]],
                ["delivered", "duplicate_ignored"],
            )
            self.assertEqual(duplicate["after_state"]["version"] - duplicate["before_state"]["version"], 1)

            untrusted = json.loads(
                (output / controls["untrusted-runbook-instruction"]["artifact"]).read_text(encoding="utf-8")
            )
            self.assertFalse(untrusted["trace_evaluation"]["passed"])
            self.assertTrue(
                any(
                    "untrusted control-like evidence instruction" in failure
                    for failure in untrusted["trace_evaluation"]["failures"]
                )
            )

            for artifact in packet["artifacts"]:
                self.assertTrue((output / artifact).exists(), artifact)

            review = (output / "architecture-operations-review.md").read_text(encoding="utf-8")
            self.assertIn("## Business outcome", review)
            self.assertIn("## Executed incident campaign", review)
            self.assertIn("## Control-plane assurance campaign", review)
            self.assertIn("## Cutover authority-transition variant", review)
            self.assertIn("## AMS / operations handover", review)
            self.assertIn("## Deliberate limitations", review)


if __name__ == "__main__":
    unittest.main()