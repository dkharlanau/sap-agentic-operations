#!/usr/bin/env python3
"""Minimal stateful enterprise simulator for SAO write-safety experiments.

This is deliberately not an SAP emulator. It models only the control properties
needed to test agent decisions around a system of record.
"""

from __future__ import annotations

import copy
import hashlib
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any


class ControlViolation(Exception):
    pass


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
class ExecutionResult:
    status: str
    outcome: str
    correlation_id: str
    object_id: str
    before_hash: str
    after_hash: str | None = None
    postcondition: str = "not_run"
    reason: str | None = None

    def as_dict(self) -> dict:
        return self.__dict__.copy()


class SyntheticEnterprise:
    ALLOWED_OPERATIONS = {"release_business_block"}

    def __init__(self, state: dict):
        self.state = copy.deepcopy(state)
        self.completed_idempotency_keys: set[str] = set()
        self.audit: list[dict] = []

    @classmethod
    def from_file(cls, path: str | Path) -> "SyntheticEnterprise":
        return cls(json.loads(Path(path).read_text(encoding="utf-8")))

    def read_object(self, canonical_id: str) -> dict:
        try:
            return copy.deepcopy(self.state["objects"][canonical_id])
        except KeyError as exc:
            raise ControlViolation(f"unknown object: {canonical_id}") from exc

    def object_hash(self, canonical_id: str) -> str:
        return stable_hash(self.read_object(canonical_id))

    def execute(self, envelope: dict) -> ExecutionResult:
        correlation_id = str(envelope.get("correlation_id", "missing"))
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

        if idempotency_key in self.completed_idempotency_keys:
            return ExecutionResult(
                status="executed",
                outcome="already_completed",
                correlation_id=correlation_id,
                object_id=canonical_id,
                before_hash=before_hash,
                after_hash=before_hash,
                postcondition="previously_verified",
            )

        policy = envelope.get("policy") or {}
        policy_result = policy.get("result")
        if policy_result == "block":
            return self._rejected(canonical_id, correlation_id, before_hash, "policy_blocked")
        if policy_result not in {"allow", "require_approval"}:
            return self._rejected(canonical_id, correlation_id, before_hash, "invalid_policy_result")

        if policy_result == "require_approval":
            approval = envelope.get("approval")
            if not isinstance(approval, dict) or not approval.get("approval_id"):
                return self._rejected(canonical_id, correlation_id, before_hash, "approval_required")
            bound_hash = approval.get("bound_state_hash")
            if bound_hash and bound_hash != before_hash:
                return self._rejected(canonical_id, correlation_id, before_hash, "approval_bound_to_stale_state")

        precondition = envelope.get("precondition") or {}
        expected_hash = precondition.get("state_hash")
        if expected_hash and expected_hash != before_hash:
            return self._rejected(canonical_id, correlation_id, before_hash, "stale_precondition")
        expected_state = precondition.get("expected_state")
        if isinstance(expected_state, dict) and not subset_matches(before, expected_state):
            return self._rejected(canonical_id, correlation_id, before_hash, "precondition_mismatch")

        # Typed business operation. No generic patch/update primitive is exposed.
        if operation_name == "release_business_block":
            self.state["objects"][canonical_id]["attributes"]["business_block"] = False
            self.state["objects"][canonical_id]["version"] += 1

        after = self.read_object(canonical_id)
        after_hash = stable_hash(after)
        expected_post = (envelope.get("postcondition") or {}).get("expected_state") or {}
        verified = subset_matches(after, expected_post)

        result = ExecutionResult(
            status="executed" if verified else "failed",
            outcome="postcondition_verified" if verified else "postcondition_failed",
            correlation_id=correlation_id,
            object_id=canonical_id,
            before_hash=before_hash,
            after_hash=after_hash,
            postcondition="passed" if verified else "failed",
            reason=None if verified else "business_postcondition_failed",
        )

        self.audit.append({
            "correlation_id": correlation_id,
            "object_id": canonical_id,
            "operation": operation_name,
            "before_hash": before_hash,
            "after_hash": after_hash,
            "postcondition": result.postcondition,
        })

        if verified:
            self.completed_idempotency_keys.add(idempotency_key)
        return result

    def _rejected(self, canonical_id: str, correlation_id: str, before_hash: str, reason: str) -> ExecutionResult:
        result = ExecutionResult(
            status="rejected",
            outcome="not_executed",
            correlation_id=correlation_id,
            object_id=canonical_id,
            before_hash=before_hash,
            reason=reason,
        )
        self.audit.append({
            "correlation_id": correlation_id,
            "object_id": canonical_id,
            "operation": "rejected",
            "before_hash": before_hash,
            "reason": reason,
        })
        return result
