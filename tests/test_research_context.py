from __future__ import annotations

import copy
import tempfile
import unittest
from pathlib import Path

from sao_toolkit.research_context import (
    ResearchContextError,
    load_packet,
    packet_summary,
    render_review,
    markdown_url,
    validate_packet,
    write_review,
)

ROOT = Path(__file__).resolve().parents[1]
EXAMPLE = ROOT / "examples" / "research-evidence" / "sti-enterprise-agents.json"


class ResearchContextTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.packet = load_packet(EXAMPLE)

    def test_reference_packet_is_valid_and_non_operational(self) -> None:
        summary = packet_summary(self.packet)
        self.assertTrue(summary["valid"], summary["errors"])
        self.assertEqual(summary["trust_level"], "external_research_context")
        self.assertTrue(summary["requires_human_review"])
        self.assertFalse(summary["execution_allowed"])
        self.assertEqual(summary["claims"], 3)

    def test_tampering_is_rejected(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["claims"][0]["text"] = "Changed after export"
        self.assertIn(
            "integrity.digest does not match the canonical packet payload",
            validate_packet(packet),
        )

    def test_weakened_boundary_is_rejected(self) -> None:
        packet = copy.deepcopy(self.packet)
        packet["operational_boundary"]["prohibited_uses"].remove("authorization")
        errors = validate_packet(packet)
        self.assertIn("operational_boundary must prohibit authorization", errors)

    def test_review_card_preserves_claim_origin_and_boundary(self) -> None:
        report = render_review(self.packet)
        self.assertIn("External research evidence review", report)
        self.assertIn("project_interpretation", report)
        self.assertIn("Execution allowed by this packet:** no", report)
        self.assertIn("Do not grant capability", report)
        self.assertIn(self.packet["source"]["canonical_url"], report)

    def test_write_review_refuses_accidental_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "review.md"
            write_review(self.packet, output)
            with self.assertRaisesRegex(ResearchContextError, "output already exists"):
                write_review(self.packet, output)
            write_review(self.packet, output, force=True)

    def test_markdown_urls_cannot_break_link_destination(self) -> None:
        self.assertEqual(
            markdown_url("https://example.com/a path_(v1)\nignored"),
            "https://example.com/a%20path_%28v1%29ignored",
        )


if __name__ == "__main__":
    unittest.main()
