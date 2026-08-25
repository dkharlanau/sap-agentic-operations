from __future__ import annotations

import csv
import shutil
import tempfile
import unittest
from pathlib import Path

from sao_toolkit.normalize import NormalizeError, create_we02_like_demo, normalize_csv


class NormalizeToolkitTests(unittest.TestCase):
    def setUp(self) -> None:
        self.root = Path(tempfile.mkdtemp(prefix="sao-normalize-test-"))
        self.addCleanup(lambda: shutil.rmtree(self.root, ignore_errors=True))

    def test_we02_like_demo_maps_status_and_constant_mapping_version(self) -> None:
        create_we02_like_demo(self.root)
        result = normalize_csv(
            table="messages",
            input_path=self.root / "we02_export.csv",
            mapping_path=self.root / "messages.mapping.json",
            output_path=self.root / "messages.csv",
        )
        self.assertEqual(result["rows"], 2)
        with (self.root / "messages.csv").open(encoding="utf-8", newline="") as handle:
            rows = list(csv.DictReader(handle))
        self.assertEqual(rows[0]["message_id"], "000000001")
        self.assertEqual(rows[0]["status"], "success")
        self.assertEqual(rows[1]["status"], "failed")
        self.assertEqual(rows[0]["mapping_version"], "M1")

    def test_missing_required_mapping_is_rejected(self) -> None:
        create_we02_like_demo(self.root)
        (self.root / "bad.json").write_text('{"columns":{"message_id":"DOCNUM"}}', encoding="utf-8")
        with self.assertRaises(NormalizeError):
            normalize_csv(
                table="messages",
                input_path=self.root / "we02_export.csv",
                mapping_path=self.root / "bad.json",
                output_path=self.root / "messages.csv",
            )


if __name__ == "__main__":
    unittest.main()
