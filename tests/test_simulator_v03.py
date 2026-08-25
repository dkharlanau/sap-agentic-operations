import json
import unittest
from pathlib import Path

from simulator.v03 import EnterpriseLab


FIXTURE = Path("simulator/fixtures/enterprise-v03.json")


def make_lab():
    return EnterpriseLab(json.loads(FIXTURE.read_text(encoding="utf-8")))


def release_envelope(lab: EnterpriseLab, *, key="release-1", before_hash=None, identity_version=None,
                     approval=True, approval_expires=999, policy_result="require_approval"):
    before_hash = before_hash or lab.object_hash("order-100")
    return {
        "correlation_id": f"corr-{key}",
        "identity_version": lab.identity_version if identity_version is None else identity_version,
        "object": {"canonical_id": "order-100"},
        "operation": {"name": "release_business_block", "parameters": {}},
        "policy": {"policy_ref": "policy://release-block/r3", "result": policy_result},
        "approval": ({
            "approval_id": f"ap-{key}",
            "canonical_id": "order-100",
            "operation": "release_business_block",
            "bound_state_hash": before_hash,
            "expires_tick": approval_expires,
        } if approval else None),
        "precondition": {"state_hash": before_hash},
        "postcondition": {"expected_state": {"attributes": {"business_block": False}}},
        "idempotency_key": key,
    }


class IdentityAndPolicyTests(unittest.TestCase):
    def test_identity_resolution_is_versioned(self):
        lab = make_lab()
        resolved = lab.resolve_identity("synthetic-s4", "SO-100")
        self.assertEqual(resolved["status"], "resolved")
        self.assertEqual(resolved["canonical_id"], "order-100")
        old_version = resolved["identity_version"]
        lab.register_mapping("order-100", "synthetic-s4", "SO-777")
        self.assertGreater(lab.identity_version, old_version)

    def test_mapping_change_invalidates_planned_write(self):
        lab = make_lab()
        envelope = release_envelope(lab)
        lab.register_mapping("order-100", "synthetic-s4", "SO-777")
        result = lab.execute(envelope)
        self.assertEqual(result.status, "rejected")
        self.assertEqual(result.reason, "stale_identity_mapping")

    def test_runtime_policy_change_overrides_planned_allow(self):
        lab = make_lab()
        envelope = release_envelope(lab, policy_result="allow")
        lab.set_policy("policy://release-block/r3", "block")
        result = lab.execute(envelope)
        self.assertEqual(result.reason, "policy_blocked")
        self.assertTrue(lab.read_object("order-100")["attributes"]["business_block"])

    def test_expired_approval_is_rejected(self):
        lab = make_lab()
        envelope = release_envelope(lab, approval_expires=100)
        lab.advance(1)
        result = lab.execute(envelope)
        self.assertEqual(result.reason, "approval_expired")


class EventLedgerTests(unittest.TestCase):
    def test_mapping_change_quarantines_pending_message(self):
        lab = make_lab()
        lab.inject_fault("delay_message", target="EV-1", value=2)
        lab.emit_message(
            event_id="EV-1",
            canonical_id="bp-200",
            operation="set_attribute",
            parameters={"field": "payment_terms", "value": "0002"},
            correlation_id="corr-ev1",
        )
        lab.register_mapping("bp-200", "synthetic-s4", "BP-9999")
        lab.advance(2)
        delivered = lab.deliver_due_messages()
        self.assertEqual(delivered[0]["status"], "quarantined")
        self.assertEqual(delivered[0]["reason"], "identity_version_changed")
        self.assertEqual(lab.read_object("bp-200")["attributes"]["payment_terms"], "0001")

    def test_drop_fault_keeps_business_state_unchanged(self):
        lab = make_lab()
        lab.inject_fault("drop_message", target="EV-DROP")
        lab.emit_message(
            event_id="EV-DROP",
            canonical_id="bp-200",
            operation="set_attribute",
            parameters={"field": "payment_terms", "value": "0002"},
            correlation_id="corr-drop",
        )
        self.assertEqual(lab.deliver_due_messages(), [])
        self.assertEqual(lab.events[0]["status"], "dropped")
        self.assertEqual(lab.read_object("bp-200")["attributes"]["payment_terms"], "0001")

    def test_duplicate_fault_is_visible_in_ledger(self):
        lab = make_lab()
        lab.inject_fault("duplicate_message", target="EV-DUP")
        ids = lab.emit_message(
            event_id="EV-DUP",
            canonical_id="bp-200",
            operation="set_attribute",
            parameters={"field": "payment_terms", "value": "0002"},
            correlation_id="corr-dup",
        )
        self.assertEqual(len(ids), 2)
        self.assertEqual(lab.events[1]["duplicate_of"], lab.events[0]["ledger_id"])


class StateChangeTests(unittest.TestCase):
    def test_race_condition_rejects_second_actor_stale_precondition(self):
        lab = make_lab()
        original_hash = lab.object_hash("order-100")
        first = lab.execute(release_envelope(lab, key="actor-a", before_hash=original_hash))
        self.assertEqual(first.status, "executed")
        second = lab.execute(release_envelope(lab, key="actor-b", before_hash=original_hash))
        self.assertIn(second.reason, {"approval_bound_to_stale_state", "stale_precondition"})

    def test_idempotency_key_cannot_be_reused_for_different_operation(self):
        lab = make_lab()
        first = lab.execute(release_envelope(lab, key="shared-key"))
        self.assertEqual(first.status, "executed")
        before_hash = lab.object_hash("order-100")
        envelope = {
            "correlation_id": "corr-terms",
            "identity_version": lab.identity_version,
            "object": {"canonical_id": "order-100"},
            "operation": {"name": "set_payment_terms", "parameters": {"payment_terms": "0002"}},
            "policy": {"policy_ref": "policy://payment-terms/r3", "result": "require_approval"},
            "approval": {
                "approval_id": "ap-terms",
                "canonical_id": "order-100",
                "operation": "set_payment_terms",
                "bound_state_hash": before_hash,
                "expires_tick": 999,
            },
            "precondition": {"state_hash": before_hash},
            "postcondition": {"expected_state": {"attributes": {"payment_terms": "0002"}}},
            "idempotency_key": "shared-key",
        }
        result = lab.execute(envelope)
        self.assertEqual(result.reason, "idempotency_key_collision")

    def test_postcondition_fault_is_not_reported_as_success(self):
        lab = make_lab()
        lab.inject_fault("postcondition_fail", target="order-100")
        result = lab.execute(release_envelope(lab, key="post-fail"))
        self.assertEqual(result.status, "failed")
        self.assertEqual(result.outcome, "postcondition_failed")
        self.assertEqual(result.postcondition, "failed")

    def test_compensation_requires_its_own_approval(self):
        lab = make_lab()
        result = lab.execute(release_envelope(lab, key="to-compensate"))
        self.assertEqual(result.status, "executed")
        rejected = lab.compensate(result.audit_id)
        self.assertEqual(rejected.reason, "compensation_approval_required")
        compensated = lab.compensate(result.audit_id, approval={
            "approval_id": "rollback-ap",
            "execution_audit_id": result.audit_id,
        })
        self.assertEqual(compensated.outcome, "compensated")
        self.assertTrue(lab.read_object("order-100")["attributes"]["business_block"])

    def test_audit_export_preserves_rejections_and_execution(self):
        lab = make_lab()
        lab.execute(release_envelope(lab, key="no-ap", approval=False))
        lab.execute(release_envelope(lab, key="with-ap"))
        kinds = [row["kind"] for row in lab.export_audit()]
        self.assertIn("rejection", kinds)
        self.assertIn("execution", kinds)


if __name__ == "__main__":
    unittest.main()
