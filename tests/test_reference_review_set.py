from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from scripts.build_customer_governance_review_set import build_review_set


CASE = Path("examples/reference-cases/customer-governance-o2c/case.json")


class CustomerGovernanceReferenceReviewSetTest(unittest.TestCase):
    def test_complete_review_set_is_reproducible_and_truthful(self) -> None:
        with tempfile.TemporaryDirectory() as temp_dir:
            output = Path(temp_dir) / "review-set"
            review_set = build_review_set(CASE, output)

            self.assertEqual(review_set["format"], "sao-reference-review-set/0.1")
            self.assertEqual(review_set["case_id"], "customer-governance-o2c")
            self.assertEqual(review_set["status"], "review-ready-synthetic")
            self.assertTrue(all(review_set["assertions"].values()))

            summary = review_set["summary"]
            self.assertEqual(summary["reference_contracts"], 14)
            self.assertEqual(summary["reference_contracts_passed"], 14)
            self.assertEqual(summary["architecture_decisions"], 4)
            self.assertEqual(summary["traceability_rows"], 7)
            self.assertEqual(summary["mapped_benchmark_cases"], 10)
            self.assertEqual(summary["mapped_benchmark_passed"], 10)
            self.assertEqual(summary["dynamic_variants"], 12)
            self.assertEqual(summary["dynamic_variants_passed"], 12)
            self.assertGreaterEqual(summary["architecture_fitness"]["systems"], 2)
            self.assertGreaterEqual(summary["architecture_fitness"]["integrations"], 1)
            self.assertEqual(summary["runbook_version"], "1.0.0")

            boundary = review_set["validation_boundary"]
            self.assertFalse(boundary["external_practitioner_validation"])
            self.assertFalse(boundary["production_sap_connectivity"])
            self.assertFalse(boundary["production_write_authorization"])
            self.assertFalse(boundary["business_roi_validated"])

            expected_files = [
                "assurance-packet.json",
                "architecture-operations-review.md",
                "architecture-fitness.json",
                "benchmark-report.json",
                "benchmark-mapped.json",
                "dynamic-variants.jsonl",
                "dynamic-variant-report.json",
                "reference-review.md",
                "reference-review-set.json",
                "reference-inputs/case.json",
                "reference-inputs/enterprise-context.json",
                "reference-inputs/architecture-decisions.json",
                "reference-inputs/traceability.json",
                "reference-inputs/ams-runbook.json",
                "control-plane/approved-governed-recovery.trace.jsonl",
            ]
            for relative in expected_files:
                self.assertTrue((output / relative).exists(), relative)

            fitness = json.loads((output / "architecture-fitness.json").read_text(encoding="utf-8"))
            self.assertTrue(fitness["passed"])
            self.assertEqual(fitness["errors"], [])
            self.assertEqual(fitness["warnings"], [])

            mapped = json.loads((output / "benchmark-mapped.json").read_text(encoding="utf-8"))
            self.assertEqual(mapped["passed"], 10)
            self.assertEqual(mapped["failed"], 0)

            dynamic = json.loads((output / "dynamic-variant-report.json").read_text(encoding="utf-8"))
            self.assertEqual(dynamic["cases"], 12)
            self.assertEqual(dynamic["passed"], 12)
            self.assertEqual(dynamic["failed"], 0)
            self.assertEqual(dynamic["unsafe_execution_failures"], 0)

            review = (output / "reference-review.md").read_text(encoding="utf-8")
            self.assertIn("review-ready synthetic assurance", review)
            self.assertIn("## Benchmark and adversarial evidence", review)
            self.assertIn("## AMS handover", review)
            self.assertIn("## Limitations", review)


if __name__ == "__main__":
    unittest.main()
