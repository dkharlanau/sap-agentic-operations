"""Stateful synthetic enterprise control-plane simulator for SAO experiments.

This module intentionally models enterprise control properties, not SAP product internals.
It provides deterministic identity, policy, event, fault, approval, idempotency,
postcondition and compensation behavior suitable for agent-safety experiments.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from typing import Any


class ControlViolation(Exception):
    """Raised when a request cannot even enter the governed execution path."""


def stable_hash(value: Any) -> str:
    payload = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return "sha256:" + hashlib.sha256(payload).hexdigest()


def subset_matches(actual: dict, expected: dict) -> bool:
    for key, value in expected.items():
        if key not in actual:
            return False
        if isinstance(value, dict) and isinstance(actual[key], dict):
            if not subset_matches(actual[key], value):
                return False
        elif actual[key] != value:
            return False
    return True


@dataclass
class LabResult:
    status: str
    outcome: str
    correlation_id: str
    object_id: str | None = None
    reason: str | None = None
    before_hash: str | None = None
    after_hash: str | None = None
    audit_id: str | None = None
    postcondition: str = "not_run"

    def as_dict(self) -> dict:
        return self.__dict__.copy()


class EnterpriseLab:
    """Deterministic testbed for enterprise-agent state-change controls."""

    ALLOWED_OPERATIONS = {"release_business_block", "set_payment_terms"}
    ALLOWED_FIELDS = {"business_block", "payment_terms"}

    def __init__(self, state: dict):
        self.state = copy.deepcopy(state)
        self.tick = int(self.state.get("clock", 0))
        self.identity_version = int(self.state.get("identity_version", 1))
        self.identity = copy.deepcopy(self.state.get("identity", {}))
        self.policies = copy.deepcopy(self.state.get("policies", {}))
        self.events: list[dict] = []
        self.audit: list[dict] = []
        self.completed_idempotency: dict[str, dict] = {}
        self.processed_event_ids: dict[str, dict] = {}
        self.faults: list[dict] = []
        self._event_seq = 0
        self._audit_seq = 0

    def advance(self, ticks: int = 1) -> int:
        if ticks < 0:
            raise ValueError("ticks must be non-negative")
        self.tick += ticks
        return self.tick

    def register_mapping(self, canonical_id: str, system: str, system_id: str) -> int:
        self.identity.setdefault(canonical_id, {})[system] = system_id
        self.identity_version += 1
        self._append_audit(
            kind="identity_change",
            correlation_id=f"identity-{self.identity_version}",
            object_id=canonical_id,
            detail={"system": system, "system_id": system_id, "identity_version": self.identity_version},
        )
        return self.identity_version

    def resolve_identity(self, system: str, system_id: str) -> dict:
        matches = [
            canonical_id
            for canonical_id, refs in self.identity.items()
            if refs.get(system) == system_id
        ]
        if len(matches) == 1:
            return {"status": "resolved", "canonical_id": matches[0], "identity_version": self.identity_version}
        if len(matches) > 1:
            return {"status": "ambiguous", "candidates": sorted(matches), "identity_version": self.identity_version}
        return {"status": "unresolved", "identity_version": self.identity_version}

    def read_object(self, canonical_id: str) -> dict:
        try:
            return copy.deepcopy(self.state["objects"][canonical_id])
        except KeyError as exc:
            raise ControlViolation(f"unknown object: {canonical_id}") from exc

    def object_hash(self, canonical_id: str) -> str:
        return stable_hash(self.read_object(canonical_id))

    def set_policy(self, policy_ref: str, result: str) -> None:
        if result not in {"allow", "block", "require_approval"}:
            raise ValueError("invalid policy result")
        self.policies[policy_ref] = {"result": result, "version": self.tick}
        self._append_audit(
            kind="policy_change",
            correlation_id=f"policy-{policy_ref}-{self.tick}",
            object_id=None,
            detail={"policy_ref": policy_ref, "result": result},
        )

    def inject_fault(self, fault_type: str, *, target: str | None = None, count: int = 1, value: Any = None) -> None:
        self.faults.append({"type": fault_type, "target": target, "remaining": count, "value": value})

    def _take_fault(self, fault_type: str, target: str | None = None) -> dict | None:
        for fault in self.faults:
            if fault["remaining"] <= 0 or fault["type"] != fault_type:
                continue
            if fault["target"] not in {None, target}:
                continue
            fault["remaining"] -= 1
            return fault
        return None

    def emit_message(
        self,
        *,
        event_id: str,
        canonical_id: str,
        operation: str,
        parameters: dict,
        correlation_id: str,
    ) -> list[str]:
        if canonical_id not in self.state.get("objects", {}):
            raise ControlViolation(f"unknown object: {canonical_id}")

        self._event_seq += 1
        event = {
            "ledger_id": f"evt-{self._event_seq:04d}",
            "event_id": event_id,
            "canonical_id": canonical_id,
            "operation": operation,
            "parameters": copy.deepcopy(parameters),
            "correlation_id": correlation_id,
            "identity_version": self.identity_version,
            "emitted_tick": self.tick,
            "deliver_at": self.tick,
            "status": "pending",
        }

        delay = self._take_fault("delay_message", event_id)
        if delay:
            event["deliver_at"] += int(delay.get("value") or 1)

        if self._take_fault("drop_message", event_id):
            event["status"] = "dropped"

        self.events.append(event)
        ids = [event["ledger_id"]]

        if self._take_fault("duplicate_message", event_id):
            self._event_seq += 1
            duplicate = copy.deepcopy(event)
            duplicate["ledger_id"] = f"evt-{self._event_seq:04d}"
            duplicate["status"] = "pending" if event["status"] != "dropped" else "dropped"
            duplicate["duplicate_of"] = event["ledger_id"]
            self.events.append(duplicate)
            ids.append(duplicate["ledger_id"])

        return ids

    @staticmethod
    def _event_fingerprint(event: dict) -> str:
        return stable_hash({
            "canonical_id": event["canonical_id"],
            "operation": event["operation"],
            "parameters": event["parameters"],
            "identity_version": event["identity_version"],
        })

    def deliver_due_messages(self) -> list[dict]:
        results = []
        for event in sorted(self.events, key=lambda x: (x["deliver_at"], x["ledger_id"])):
            if event["status"] != "pending" or event["deliver_at"] > self.tick:
                continue

            if event["identity_version"] != self.identity_version:
                event["status"] = "quarantined"
                event["reason"] = "identity_version_changed"
                results.append(copy.deepcopy(event))
                continue

            fingerprint = self._event_fingerprint(event)
            previous_event = self.processed_event_ids.get(event["event_id"])
            if previous_event:
                event["processed_by"] = previous_event["ledger_id"]
                if previous_event["fingerprint"] == fingerprint:
                    event["status"] = "duplicate_ignored"
                    event["reason"] = "event_id_already_processed"
                    audit_kind = "duplicate_event_ignored"
                else:
                    event["status"] = "quarantined"
                    event["reason"] = "event_id_payload_collision"
                    audit_kind = "event_id_collision"
                self._append_audit(
                    kind=audit_kind,
                    correlation_id=event["correlation_id"],
                    object_id=event["canonical_id"],
                    detail={
                        "event_id": event["event_id"],
                        "ledger_id": event["ledger_id"],
                        "processed_by": previous_event["ledger_id"],
                        "reason": event["reason"],
                    },
                )
                results.append(copy.deepcopy(event))
                continue

            obj = self.state["objects"][event["canonical_id"]]
            if event["operation"] == "set_attribute":
                field = event["parameters"].get("field")
                if field not in self.ALLOWED_FIELDS:
                    event["status"] = "rejected"
                    event["reason"] = "field_not_allowed"
                    results.append(copy.deepcopy(event))
                    continue
                obj["attributes"][field] = event["parameters"].get("value")
                obj["version"] += 1
                event["status"] = "delivered"
                self.processed_event_ids[event["event_id"]] = {
                    "ledger_id": event["ledger_id"],
                    "fingerprint": fingerprint,
                }
            else:
                event["status"] = "rejected"
                event["reason"] = "operation_not_supported"

            results.append(copy.deepcopy(event))
        return results

    def execute(self, envelope: dict) -> LabResult:
        correlation_id = str(envelope.get("correlation_id") or "missing")
        object_spec = envelope.get("object") or {}
        canonical_id = object_spec.get("canonical_id")
        operation = envelope.get("operation") or {}
        operation_name = operation.get("name")
        idempotency_key = envelope.get("idempotency_key")

        if not canonical_id or canonical_id not in self.state.get("objects", {}):
            raise ControlViolation("execution requires a known canonical object")
        if operation_name not in self.ALLOWED_OPERATIONS:
            raise ControlViolation(f"operation is not allow-listed: {operation_name}")
        if not idempotency_key:
            raise ControlViolation("execution requires an idempotency key")

        before = self.read_object(canonical_id)
        before_hash = stable_hash(before)

        previous = self.completed_idempotency.get(idempotency_key)
        operation_fingerprint = stable_hash({
            "canonical_id": canonical_id,
            "operation": operation_name,
            "parameters": operation.get("parameters") or {},
        })
        if previous:
            if previous["operation_fingerprint"] != operation_fingerprint:
                return self._reject(canonical_id, correlation_id, before_hash, "idempotency_key_collision")
            return LabResult(
                status="executed",
                outcome="already_completed",
                correlation_id=correlation_id,
                object_id=canonical_id,
                before_hash=before_hash,
                after_hash=before_hash,
                audit_id=previous["audit_id"],
                postcondition="previously_verified",
            )

        bound_identity_version = envelope.get("identity_version")
        if bound_identity_version is not None and bound_identity_version != self.identity_version:
            return self._reject(canonical_id, correlation_id, before_hash, "stale_identity_mapping")

        policy_ref = (envelope.get("policy") or {}).get("policy_ref")
        declared_policy_result = (envelope.get("policy") or {}).get("result")
        registry_policy = self.policies.get(policy_ref) if policy_ref else None
        effective_policy = (registry_policy or {}).get("result", declared_policy_result)

        if effective_policy == "block":
            return self._reject(canonical_id, correlation_id, before_hash, "policy_blocked")
        if effective_policy not in {"allow", "require_approval"}:
            return self._reject(canonical_id, correlation_id, before_hash, "invalid_policy_result")

        approval = envelope.get("approval")
        if effective_policy == "require_approval":
            if not isinstance(approval, dict) or not approval.get("approval_id"):
                return self._reject(canonical_id, correlation_id, before_hash, "approval_required")
            if approval.get("expires_tick") is not None and self.tick > int(approval["expires_tick"]):
                return self._reject(canonical_id, correlation_id, before_hash, "approval_expired")
            bound_hash = approval.get("bound_state_hash")
            if bound_hash and bound_hash != before_hash:
                return self._reject(canonical_id, correlation_id, before_hash, "approval_bound_to_stale_state")
            if approval.get("canonical_id") not in {None, canonical_id}:
                return self._reject(canonical_id, correlation_id, before_hash, "approval_object_scope_mismatch")
            if approval.get("operation") not in {None, operation_name}:
                return self._reject(canonical_id, correlation_id, before_hash, "approval_operation_scope_mismatch")

        precondition = envelope.get("precondition") or {}
        if precondition.get("state_hash") and precondition["state_hash"] != before_hash:
            return self._reject(canonical_id, correlation_id, before_hash, "stale_precondition")
        if isinstance(precondition.get("expected_state"), dict) and not subset_matches(before, precondition["expected_state"]):
            return self._reject(canonical_id, correlation_id, before_hash, "precondition_mismatch")

        before_state = copy.deepcopy(before)

        if operation_name == "release_business_block":
            self.state["objects"][canonical_id]["attributes"]["business_block"] = False
        elif operation_name == "set_payment_terms":
            self.state["objects"][canonical_id]["attributes"]["payment_terms"] = operation.get("parameters", {}).get("payment_terms")
        self.state["objects"][canonical_id]["version"] += 1

        if self._take_fault("postcondition_fail", canonical_id):
            self.state["objects"][canonical_id] = copy.deepcopy(before_state)
            self.state["objects"][canonical_id]["version"] = before_state["version"] + 1

        after = self.read_object(canonical_id)
        after_hash = stable_hash(after)
        expected_post = (envelope.get("postcondition") or {}).get("expected_state") or {}
        verified = subset_matches(after, expected_post)

        audit_id = self._append_audit(
            kind="execution",
            correlation_id=correlation_id,
            object_id=canonical_id,
            detail={
                "operation": operation_name,
                "before_hash": before_hash,
                "after_hash": after_hash,
                "before_state": before_state,
                "after_state": copy.deepcopy(after),
                "postcondition": "passed" if verified else "failed",
                "idempotency_key": idempotency_key,
            },
        )

        result = LabResult(
            status="executed" if verified else "failed",
            outcome="postcondition_verified" if verified else "postcondition_failed",
            correlation_id=correlation_id,
            object_id=canonical_id,
            reason=None if verified else "business_postcondition_failed",
            before_hash=before_hash,
            after_hash=after_hash,
            audit_id=audit_id,
            postcondition="passed" if verified else "failed",
        )
        if verified:
            self.completed_idempotency[idempotency_key] = {
                "operation_fingerprint": operation_fingerprint,
                "audit_id": audit_id,
            }
        return result

    def compensate(self, audit_id: str, *, approval: dict | None = None) -> LabResult:
        record = next((x for x in self.audit if x["audit_id"] == audit_id and x["kind"] == "execution"), None)
        if not record:
            raise ControlViolation("unknown execution audit record")

        object_id = record["object_id"]
        current_hash = self.object_hash(object_id)
        policy = self.policies.get("policy://compensation", {"result": "require_approval"})
        if policy["result"] == "require_approval":
            if not approval or not approval.get("approval_id"):
                return self._reject(object_id, f"compensate-{audit_id}", current_hash, "compensation_approval_required")
            if approval.get("execution_audit_id") not in {None, audit_id}:
                return self._reject(object_id, f"compensate-{audit_id}", current_hash, "compensation_scope_mismatch")

        before_state = copy.deepcopy(record["detail"]["before_state"])
        self.state["objects"][object_id] = before_state
        after_hash = self.object_hash(object_id)
        compensation_audit = self._append_audit(
            kind="compensation",
            correlation_id=f"compensate-{audit_id}",
            object_id=object_id,
            detail={"source_audit_id": audit_id, "restored_hash": after_hash},
        )
        return LabResult(
            status="executed",
            outcome="compensated",
            correlation_id=f"compensate-{audit_id}",
            object_id=object_id,
            before_hash=current_hash,
            after_hash=after_hash,
            audit_id=compensation_audit,
            postcondition="passed",
        )

    def export_audit(self) -> list[dict]:
        return copy.deepcopy(self.audit)

    def _append_audit(self, *, kind: str, correlation_id: str, object_id: str | None, detail: dict) -> str:
        self._audit_seq += 1
        audit_id = f"audit-{self._audit_seq:04d}"
        self.audit.append({
            "audit_id": audit_id,
            "tick": self.tick,
            "kind": kind,
            "correlation_id": correlation_id,
            "object_id": object_id,
            "detail": copy.deepcopy(detail),
        })
        return audit_id

    def _reject(self, object_id: str, correlation_id: str, before_hash: str, reason: str) -> LabResult:
        audit_id = self._append_audit(
            kind="rejection",
            correlation_id=correlation_id,
            object_id=object_id,
            detail={"reason": reason, "before_hash": before_hash},
        )
        return LabResult(
            status="rejected",
            outcome="not_executed",
            correlation_id=correlation_id,
            object_id=object_id,
            reason=reason,
            before_hash=before_hash,
            audit_id=audit_id,
        )