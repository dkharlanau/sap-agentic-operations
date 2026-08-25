from __future__ import annotations

import csv
import json
import shutil
import tempfile
import unittest
from pathlib import Path

from sao_toolkit.demo import create_demo_pack, scenario_names
from sao_toolkit.evidence import EvidencePackError, create_empty_pack, load_pack
from sao_toolkit.incident import analyze_incident
from sao_toolkit.reporting import write_incident_outputs
from sao_toolkit.workbench import write_workbench

ROOT = Path(__file__).resolve().parents[1]
DEMO = ROOT / "examples" / "evidence-packs" / "customer-replication-missing-event"


def write_csv(path: Path, headers: list[str], rows: list[list[str]]) -> None:
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


class IncidentToolkitTests(unittest.TestCase):
    def temp_root(self) -> Path:
        tmp = Path(tempfile.mkdtemp(prefix="sao-test-"))
        self.addCleanup(lambda: shutil.rmtree(tmp, ignore_errors=True))
        return tmp

    def copy_demo(self) -> Path:
        pack = self.temp_root() / "pack"
        shutil.copytree(DEMO, pack)
        return pack

    def test_demo_detects_old_success_not_current_change(self) -> None:
        pack = load_pack(self.copy_demo())
        report = analyze_incident(pack)
        self.assertEqual(report["status"], "insufficient_evidence")
        self.assertEqual(report["classification"], "current_outbound_event_not_proven")
        self.assertIn("reprocess_old_successful_message", report["unsafe_actions"])
        self.assertIn(
            "determine_whether_current_outbound_event_was_created",
            report["safe_next_actions"],
        )

    def test_generated_demo_lab_contains_multiple_failure_modes(self) -> None:
        self.assertGreaterEqual(len(scenario_names()), 9)
        root = self.temp_root() / "mapping"
        create_demo_pack(root, scenario="mapping-drift")
        report = analyze_incident(load_pack(root))
        self.assertEqual(report["classification"], "mapping_version_drift")

    def test_current_message_and_matching_target_resolves_read_only(self) -> None:
        root = self.copy_demo()
        write_csv(
            root / "messages.csv",
            [
                "message_id",
                "change_id",
                "object_id",
                "status",
                "created_at",
                "target_id",
                "business_status",
                "mapping_version",
            ],
            [["MSG-200", "CHG-200", "C-100", "success", "2026-08-25T10:16:00Z", "BP-501", "accepted", "M1"]],
        )
        write_csv(
            root / "target_state.csv",
            ["object_id", "attribute", "value", "observed_at"],
            [["BP-501", "delivery_control", "NEW", "2026-08-25T10:20:00Z"]],
        )
        report = analyze_incident(load_pack(root))
        self.assertEqual(report["status"], "resolved_read_only")
        self.assertEqual(report["classification"], "business_state_verified")
        self.assertFalse(report["execution_allowed"])

    def test_mapping_drift_blocks_historical_replay(self) -> None:
        root = self.copy_demo()
        write_csv(
            root / "messages.csv",
            [
                "message_id",
                "change_id",
                "object_id",
                "status",
                "created_at",
                "target_id",
                "business_status",
                "mapping_version",
            ],
            [["MSG-200", "CHG-200", "C-100", "success", "2026-08-25T10:16:00Z", "BP-501", "accepted", "M1"]],
        )
        write_csv(
            root / "identity_map.csv",
            ["source_id", "target_id", "status", "mapping_version", "effective_from"],
            [["C-100", "BP-501", "resolved", "M2", "2026-08-25T10:30:00Z"]],
        )
        report = analyze_incident(load_pack(root))
        self.assertEqual(report["classification"], "mapping_version_drift")
        self.assertIn("replay_using_current_mapping", report["unsafe_actions"])

    def test_business_rejection_is_not_transport_resolution(self) -> None:
        root = self.copy_demo()
        write_csv(
            root / "messages.csv",
            [
                "message_id",
                "change_id",
                "object_id",
                "status",
                "created_at",
                "target_id",
                "business_status",
                "mapping_version",
            ],
            [["MSG-200", "CHG-200", "C-100", "success", "2026-08-25T10:16:00Z", "BP-501", "rejected", "M1"]],
        )
        report = analyze_incident(load_pack(root))
        self.assertEqual(report["status"], "recommendation")
        self.assertEqual(report["classification"], "business_processing_rejection")
        self.assertIn("declare_resolved", report["unsafe_actions"])

    def test_report_outputs_are_created(self) -> None:
        root = self.copy_demo()
        report = analyze_incident(load_pack(root))
        json_path, md_path = write_incident_outputs(report, root / "out")
        self.assertTrue(json_path.exists())
        self.assertTrue(md_path.exists())
        loaded = json.loads(json_path.read_text(encoding="utf-8"))
        self.assertEqual(loaded["incident_id"], report["incident_id"])
        self.assertIn("Safe next actions", md_path.read_text(encoding="utf-8"))

    def test_workbench_static_html_is_created(self) -> None:
        root = self.copy_demo()
        target = write_workbench(root, root / "workbench.html")
        text = target.read_text(encoding="utf-8")
        self.assertIn("Evidence chain", text)
        self.assertIn("current_outbound_event_not_proven", text)
        self.assertIn("Not justified by current evidence", text)

    def test_empty_pack_initializer_creates_valid_contract_files(self) -> None:
        root = self.temp_root() / "new-incident"
        create_empty_pack(
            root,
            incident_id="INC-001",
            object_type="customer",
            source_id="C-1",
            target_id="BP-1",
            authority_system="MDG",
            attribute="tax_class",
        )
        pack = load_pack(root)
        self.assertEqual(pack.incident_id, "INC-001")
        self.assertEqual(pack.manifest["authority"]["system"], "MDG")
        self.assertTrue((root / "README.txt").exists())

    def test_invalid_manifest_is_rejected(self) -> None:
        root = self.copy_demo()
        manifest = json.loads((root / "incident.json").read_text(encoding="utf-8"))
        manifest["format"] = "other"
        (root / "incident.json").write_text(json.dumps(manifest), encoding="utf-8")
        with self.assertRaises(EvidencePackError):
            load_pack(root)


if __name__ == "__main__":
    unittest.main()
