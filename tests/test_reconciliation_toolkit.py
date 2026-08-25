from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from sao_toolkit.reconciliation import (
    analyze_reconciliation,
    create_reconciliation_demo,
    write_reconciliation_outputs,
)


class ReconciliationToolkitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sao-reconcile-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))

    def test_demo_distinguishes_authoritative_mismatch_from_newer_target_snapshot(self) -> None:
        create_reconciliation_demo(self.root)
        report = analyze_reconciliation(self.root)
        classes = [row["classification"] for row in report["results"]]
        self.assertIn("authoritative_mismatch", classes)
        self.assertIn("non_authoritative_snapshot_is_newer", classes)
        self.assertIn("aligned", classes)
        newer_target = next(
            row for row in report["results"]
            if row["classification"] == "non_authoritative_snapshot_is_newer"
        )
        self.assertEqual(
            newer_target["unsafe_action"],
            "overwrite_newer_state_from_stale_snapshot",
        )

    def test_reconciliation_outputs_are_written(self) -> None:
        create_reconciliation_demo(self.root)
        report = analyze_reconciliation(self.root)
        outputs = write_reconciliation_outputs(report, self.root / "out")
        for path in outputs.values():
            self.assertTrue(path.exists())
        markdown = outputs["markdown"].read_text(encoding="utf-8")
        self.assertIn("authoritative_mismatch", markdown)
        self.assertIn("non_authoritative_snapshot_is_newer", markdown)


if __name__ == "__main__":
    unittest.main()
