from __future__ import annotations

import json
import unittest
from pathlib import Path

from simulator.v03 import EnterpriseLab


FIXTURE = Path("simulator/fixtures/enterprise-v03.json")


def make_lab() -> EnterpriseLab:
    return EnterpriseLab(json.loads(FIXTURE.read_text(encoding="utf-8")))


def delivery_control_envelope(lab: EnterpriseLab, *, key: str) -> dict:
    before_hash = lab.object_hash("customer-100")
    return {
        "correlation_id": f"corr-{key}",
        "identity_version": lab.identity_version,
        "object": {"canonical_id": "customer-100"},
        "operation": {
            "name": "set_delivery_control",
            "parameters": {"delivery_control": "NEW"},
        },
        "policy": {
            "policy_ref": "policy://delivery-control/r3",
            "result": "require_approval",
        },
        "approval": {
            "approval_id": f"approval-{key}",
            "canonical_id": "customer-100",
            "operation": "set_delivery_control",
            "bound_state_hash": before_hash,
            "expires_tick": lab.tick + 10,
        },
        "precondition": {
            "state_hash": before_hash,
            "expected_state": {"attributes": {"delivery_control": "OLD"}},
        },
        "postcondition": {
            "expected_state": {"attributes": {"delivery_control": "NEW"}},
        },
        "idempotency_key": key,
    }


class CustomerControlPlaneTest(unittest.TestCase):
    def test_mdg_and_s4_ids_resolve_to_same_canonical_customer(self) -> None:
        lab = make_lab()
        self.assertEqual(
            lab.resolve_identity("synthetic-mdg", "C-100")["canonical_id"],
            "customer-100",
        )
        self.assertEqual(
            lab.resolve_identity("synthetic-s4", "BP-501")["canonical_id"],
            "customer-100",
        )

    def test_delivery_control_recovery_requires_governed_write_envelope(self) -> None:
        lab = make_lab()
        before = lab.read_object("customer-100")
        self.assertEqual(before["attributes"]["delivery_control"], "OLD")

        result = lab.execute(delivery_control_envelope(lab, key="customer-control-test"))

        self.assertEqual(result.status, "executed")
        self.assertEqual(result.outcome, "postcondition_verified")
        self.assertEqual(result.postcondition, "passed")
        after = lab.read_object("customer-100")
        self.assertEqual(after["attributes"]["delivery_control"], "NEW")
        self.assertEqual(after["version"], before["version"] + 1)


if __name__ == "__main__":
    unittest.main()