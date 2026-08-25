from __future__ import annotations

import shutil
import tempfile
import unittest
from pathlib import Path

from sao_toolkit.quickcheck import analyze_quickcheck, create_quickcheck_demo, write_quickcheck_outputs


class QuickCheckToolkitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sao-quickcheck-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))

    def test_demo_reuses_incident_semantics_for_multiple_rows(self) -> None:
        source = create_quickcheck_demo(self.root / "quick.csv")
        report = analyze_quickcheck(source)
        self.assertEqual(report["rows"], 3)
        self.assertEqual(report["resolved"], 1)
        self.assertEqual(report["needs_attention"], 2)
        self.assertEqual(report["by_classification"]["business_state_verified"], 1)
        self.assertEqual(report["by_classification"]["business_processing_rejection"], 1)
        self.assertEqual(report["by_classification"]["current_outbound_event_not_proven"], 1)

    def test_outputs_are_created(self) -> None:
        source = create_quickcheck_demo(self.root / "quick.csv")
        report = analyze_quickcheck(source)
        paths = write_quickcheck_outputs(report, self.root / "out")
        for path in paths.values():
            self.assertTrue(path.exists())
        self.assertIn("current_outbound_event_not_proven", paths["markdown"].read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
