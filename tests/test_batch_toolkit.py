from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from sao_toolkit.batch import analyze_batch, write_batch_outputs
from sao_toolkit.demo import create_demo_pack


class BatchToolkitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sao-batch-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))

    def test_batch_aggregates_failure_classes_and_resolved_cases(self) -> None:
        create_demo_pack(self.root / "missing", scenario="missing-current-event")
        create_demo_pack(self.root / "rejected", scenario="business-rejection")
        create_demo_pack(self.root / "resolved", scenario="resolved")
        report = analyze_batch(self.root)
        self.assertEqual(report["incidents"], 3)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["needs_attention"], 2)
        self.assertEqual(report["by_classification"]["business_state_verified"], 1)
        self.assertEqual(report["by_classification"]["business_processing_rejection"], 1)
        self.assertEqual(report["by_classification"]["current_outbound_event_not_proven"], 1)

    def test_batch_writes_csv_json_and_markdown(self) -> None:
        create_demo_pack(self.root / "mapping", scenario="mapping-drift")
        report = analyze_batch(self.root)
        paths = write_batch_outputs(report, self.root / "out")
        for path in paths.values():
            self.assertTrue(path.exists())
        self.assertIn("mapping_version_drift", paths["markdown"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
