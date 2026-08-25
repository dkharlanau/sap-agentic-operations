"""Trust-aware context primitives for SAO simulator experiments."""

from __future__ import annotations

import copy
from typing import Any


class ContextStore:
    """Separates business evidence, durable memory, and control authority."""

    CONTROL_TRUST = {"trusted_control", "trusted_runbook"}

    def __init__(self):
        self.evidence: list[dict] = []
        self.memory: list[dict] = []

    def ingest_evidence(self, evidence_id: str, content: Any, *, trust: str = "business_data", tick: int = 0) -> dict:
        record = {
            "evidence_id": evidence_id,
            "tick": tick,
            "trust": trust,
            "content": copy.deepcopy(content),
            "control_instructions_trusted": trust == "trusted_control",
        }
        self.evidence.append(record)
        return copy.deepcopy(record)

    def store_memory(
        self,
        key: str,
        value: Any,
        *,
        source_trust: str,
        stored_tick: int,
        policy_ref: str | None = None,
        policy_version: int | None = None,
    ) -> dict:
        record = {
            "key": key,
            "value": copy.deepcopy(value),
            "stored_tick": stored_tick,
            "source_trust": source_trust,
            "eligible_for_control": source_trust in self.CONTROL_TRUST,
            "policy_ref": policy_ref,
            "policy_version": policy_version,
        }
        self.memory.append(record)
        return copy.deepcopy(record)

    def read_memory_for_action(self, key: str, *, current_policy: dict | None = None) -> dict:
        candidates = [row for row in self.memory if row["key"] == key]
        if not candidates:
            return {"status": "missing"}
        record = candidates[-1]
        if not record["eligible_for_control"]:
            return {"status": "untrusted", "record": copy.deepcopy(record)}
        if current_policy is not None:
            current_ref = current_policy.get("policy_ref")
            current_version = current_policy.get("version")
            if record.get("policy_ref") != current_ref or record.get("policy_version") != current_version:
                return {
                    "status": "stale",
                    "record": copy.deepcopy(record),
                    "current_policy": copy.deepcopy(current_policy),
                }
        return {"status": "usable", "record": copy.deepcopy(record)}

    def latest_evidence(self, evidence_id: str) -> dict | None:
        for row in reversed(self.evidence):
            if row["evidence_id"] == evidence_id:
                return copy.deepcopy(row)
        return None
