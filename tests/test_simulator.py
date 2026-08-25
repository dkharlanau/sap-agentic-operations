import unittest

from simulator.engine import SyntheticEnterprise


FIXTURE = "simulator/fixtures/order-block.json"


def envelope(enterprise: SyntheticEnterprise, *, approval=True, stale=False, idempotency_key="release-order-100-v4"):
    current_hash = enterprise.object_hash("order-100")
    bound_hash = "sha256:stale" if stale else current_hash
    return {
        "envelope_version": "0.1",
        "decision_id": "decision-test",
        "risk_tier": "R3",
        "object": {
            "canonical_type": "sales_order",
            "canonical_id": "order-100",
            "target_system": "synthetic-s4",
            "target_system_id": "SO-100",
        },
        "operation": {
            "name": "release_business_block",
            "parameters": {"reason": "synthetic_test"},
            "allowed_fields": ["business_block"],
        },
        "precondition": {"state_hash": bound_hash},
        "postcondition": {
            "expected_state": {"attributes": {"business_block": False}},
            "verification_method": "read_after_write",
        },
        "policy": {
            "result": "require_approval",
            "policy_ref": "policy://release-block/r3",
        },
        "approval": ({
            "approval_id": "approval-test",
            "approver": "human:test-owner",
            "approved_at": "2026-08-25T10:00:00Z",
            "bound_state_hash": bound_hash,
        } if approval else None),
        "expires_at": "2099-01-01T00:00:00Z",
        "idempotency_key": idempotency_key,
        "correlation_id": "corr-test",
        "compensation": {"available": True, "reference": "procedure://restore-block"},
    }


class SimulatorSafetyTests(unittest.TestCase):
    def setUp(self):
        self.enterprise = SyntheticEnterprise.from_file(FIXTURE)

    def test_missing_approval_rejects_write(self):
        result = self.enterprise.execute(envelope(self.enterprise, approval=False))
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.reason, "approval_required")
        self.assertTrue(self.enterprise.read_object("order-100")["attributes"]["business_block"])

    def test_stale_precondition_rejects_write(self):
        result = self.enterprise.execute(envelope(self.enterprise, stale=True))
        self.assertEqual(result.status, "rejected")
        self.assertIn(result.reason, {"approval_bound_to_stale_state", "stale_precondition"})
        self.assertTrue(self.enterprise.read_object("order-100")["attributes"]["business_block"])

    def test_exact_approved_write_executes_and_verifies(self):
        result = self.enterprise.execute(envelope(self.enterprise))
        self.assertEqual(result.status, "executed")
        self.assertEqual(result.postcondition, "passed")
        self.assertFalse(self.enterprise.read_object("order-100")["attributes"]["business_block"])

    def test_idempotency_prevents_duplicate_mutation(self):
        first = self.enterprise.execute(envelope(self.enterprise))
        self.assertEqual(first.status, "executed")
        version_after_first = self.enterprise.read_object("order-100")["version"]

        # Recreate a logically identical request with the same idempotency key.
        second = self.enterprise.execute(envelope(self.enterprise, idempotency_key="release-order-100-v4"))
        self.assertEqual(second.outcome, "already_completed")
        self.assertEqual(self.enterprise.read_object("order-100")["version"], version_after_first)


if __name__ == "__main__":
    unittest.main()
