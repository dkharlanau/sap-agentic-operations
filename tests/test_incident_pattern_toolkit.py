from __future__ import annotations

import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
if str(SCRIPTS) not in sys.path:
    sys.path.insert(0, str(SCRIPTS))

from build_incident_patterns import PatternRegistryError, build_incident_pattern_pages, load_registry
from sao_toolkit.demo import scenario_names


class IncidentPatternToolkitTests(unittest.TestCase):
    def temp_root(self) -> Path:
        root = Path(tempfile.mkdtemp(prefix="sao-pattern-test-"))
        self.addCleanup(lambda: shutil.rmtree(root, ignore_errors=True))
        return root

    def test_registry_is_bounded_to_existing_nonresolved_scenarios(self) -> None:
        registry = load_registry()
        patterns = registry["patterns"]
        self.assertEqual(len(patterns), 8)
        runnable = set(scenario_names())
        scenarios = {item["scenario"] for item in patterns}
        self.assertTrue(scenarios <= runnable)
        self.assertNotIn("resolved", scenarios)
        self.assertEqual(len(scenarios), len(patterns))

    def test_generated_pages_are_bound_to_current_incident_engine(self) -> None:
        output = self.temp_root() / "patterns"
        records = build_incident_pattern_pages(output)
        expected = {
            "missing-current-event": "current_outbound_event_not_proven",
            "business-rejection": "business_processing_rejection",
            "mapping-drift": "mapping_version_drift",
            "target-mismatch": "target_state_mismatch_after_current_event",
            "technical-failure": "technical_message_failure",
            "identity-unresolved": "identity_ambiguous_or_unresolved",
            "stale-target-observation": "target_observation_stale",
            "target-identity-mismatch": "message_target_identity_mismatch",
        }
        self.assertEqual({item["scenario"] for item in records}, set(expected))
        for record in records:
            self.assertEqual(record["engine"]["classification"], expected[record["scenario"]])
            self.assertFalse(record["engine"]["execution_allowed"])
            page = (output / f"{record['slug']}.md").read_text(encoding="utf-8")
            self.assertIn(record["engine"]["classification"], page)
            self.assertIn("Synthetic verified pattern", page)
            self.assertIn(f"sao demo --scenario {record['scenario']}", page)
        machine = json.loads((output / "patterns.json").read_text(encoding="utf-8"))
        self.assertEqual(len(machine["patterns"]), 8)
        self.assertIn("evidence-gated", (output / "index.md").read_text(encoding="utf-8"))

    def test_registry_rejects_unknown_scenario(self) -> None:
        registry = load_registry()
        registry["patterns"][0]["scenario"] = "not-a-real-scenario"
        candidate = self.temp_root() / "registry.json"
        candidate.write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaisesRegex(PatternRegistryError, "unknown scenario"):
            load_registry(candidate)

    def test_registry_rejects_resolved_control_as_acquisition_page(self) -> None:
        registry = load_registry()
        registry["patterns"][0]["scenario"] = "resolved"
        candidate = self.temp_root() / "registry.json"
        candidate.write_text(json.dumps(registry), encoding="utf-8")
        with self.assertRaisesRegex(PatternRegistryError, "not an incident-pattern acquisition page"):
            load_registry(candidate)


if __name__ == "__main__":
    unittest.main()
