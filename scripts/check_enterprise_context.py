#!/usr/bin/env python3
"""Validate SAO Enterprise Context Graph semantics without external dependencies.

This is intentionally not a full JSON Schema implementation. It checks architectural
references and fitness rules that are useful in CI and design reviews.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ASYNC_INTERACTIONS = {"async_event", "message"}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("context root must be a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SAO enterprise context architecture fitness")
    parser.add_argument("context", type=Path)
    parser.add_argument("--strict", action="store_true", help="treat warnings as failures")
    parser.add_argument("--json", action="store_true", dest="json_output")
    args = parser.parse_args()

    try:
        data = load(args.context)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    errors: list[str] = []
    warnings: list[str] = []

    required = ["schema_version", "context_id", "business_process", "business_invariants", "objects", "systems", "relations"]
    for field in required:
        if field not in data:
            errors.append(f"missing required field: {field}")

    systems = data.get("systems") if isinstance(data.get("systems"), list) else []
    objects = data.get("objects") if isinstance(data.get("objects"), list) else []
    invariants = data.get("business_invariants") if isinstance(data.get("business_invariants"), list) else []
    integrations = data.get("integrations") if isinstance(data.get("integrations"), list) else []
    controls = data.get("controls") if isinstance(data.get("controls"), list) else []
    evidence = data.get("evidence") if isinstance(data.get("evidence"), list) else []
    relations = data.get("relations") if isinstance(data.get("relations"), list) else []

    def ids(rows: list[dict], label: str) -> set[str]:
        result: set[str] = set()
        for index, row in enumerate(rows):
            if not isinstance(row, dict):
                errors.append(f"{label}[{index}] must be an object")
                continue
            row_id = row.get("id")
            if not isinstance(row_id, str) or not row_id:
                errors.append(f"{label}[{index}] missing non-empty id")
                continue
            if row_id in result:
                errors.append(f"duplicate {label} id: {row_id}")
            result.add(row_id)
        return result

    system_ids = ids(systems, "systems")
    object_ids = ids(objects, "objects")
    invariant_ids = ids(invariants, "business_invariants")
    integration_ids = ids(integrations, "integrations")
    control_ids = ids(controls, "controls")
    evidence_ids = ids(evidence, "evidence")

    all_ids = system_ids | object_ids | invariant_ids | integration_ids | control_ids | evidence_ids
    process = data.get("business_process")
    if isinstance(process, dict) and isinstance(process.get("id"), str):
        all_ids.add(process["id"])

    for obj in objects:
        if not isinstance(obj, dict):
            continue
        obj_id = obj.get("id", "<unknown>")
        authority = obj.get("authority")
        if not isinstance(authority, list) or not authority:
            warnings.append(f"{obj_id}: no explicit authority scope")
        else:
            for item in authority:
                if not isinstance(item, dict):
                    errors.append(f"{obj_id}: authority entry must be an object")
                    continue
                system_id = item.get("system_id")
                if system_id not in system_ids:
                    errors.append(f"{obj_id}: authority references unknown system {system_id!r}")
        identities = obj.get("system_identities") or []
        if isinstance(identities, list):
            for item in identities:
                if isinstance(item, dict) and item.get("system_id") not in system_ids:
                    errors.append(f"{obj_id}: identity references unknown system {item.get('system_id')!r}")

    for integration in integrations:
        if not isinstance(integration, dict):
            continue
        iid = integration.get("id", "<unknown>")
        producer = integration.get("producer")
        consumer = integration.get("consumer")
        if producer not in system_ids:
            errors.append(f"{iid}: producer references unknown system {producer!r}")
        if consumer not in system_ids:
            errors.append(f"{iid}: consumer references unknown system {consumer!r}")
        if not integration.get("postcondition"):
            warnings.append(f"{iid}: integration has no business postcondition")
        if not integration.get("recovery_owner"):
            warnings.append(f"{iid}: integration has no recovery owner")
        if integration.get("interaction") in ASYNC_INTERACTIONS:
            if not integration.get("correlation_key"):
                warnings.append(f"{iid}: async/message integration has no correlation key")
            if not integration.get("idempotency"):
                warnings.append(f"{iid}: async/message integration has no idempotency semantics")
            if not integration.get("ordering"):
                warnings.append(f"{iid}: async/message integration has no ordering statement")

    protected_invariants = {
        rel.get("from")
        for rel in relations
        if isinstance(rel, dict) and rel.get("type") == "protected_by" and rel.get("to") in control_ids
    }
    for invariant_id in invariant_ids:
        if invariant_id not in protected_invariants:
            warnings.append(f"{invariant_id}: business invariant is not linked to a protecting control")

    for index, relation in enumerate(relations):
        if not isinstance(relation, dict):
            errors.append(f"relations[{index}] must be an object")
            continue
        source = relation.get("from")
        target = relation.get("to")
        if source not in all_ids:
            errors.append(f"relation references unknown source {source!r}")
        if target not in all_ids:
            errors.append(f"relation references unknown target {target!r}")

    agent = data.get("agent_boundary")
    if isinstance(agent, dict):
        capability = agent.get("max_capability")
        if capability == "execute" and not agent.get("execution_gate"):
            errors.append("agent_boundary: execute capability requires an explicit execution_gate")
        if capability in {"approve", "execute"} and not agent.get("may_not_decide"):
            warnings.append("agent_boundary: elevated capability has no explicit may_not_decide boundary")
        for evidence_ref in agent.get("may_read") or []:
            if evidence_ref not in evidence_ids:
                errors.append(f"agent_boundary: may_read references unknown evidence {evidence_ref!r}")

    cutover = data.get("cutover")
    if isinstance(cutover, dict) and cutover.get("phase") not in {None, "steady-state"}:
        if not cutover.get("authority_transition"):
            warnings.append("cutover: non-steady-state phase has no authority_transition")
        if not cutover.get("delta_watermark"):
            warnings.append("cutover: non-steady-state phase has no delta_watermark")
        if not cutover.get("mapping_version"):
            warnings.append("cutover: non-steady-state phase has no mapping_version")
        if not cutover.get("reconciliation"):
            warnings.append("cutover: non-steady-state phase has no reconciliation definition")

    report = {
        "format": "sao-enterprise-context-fitness/0.1",
        "context": str(args.context),
        "context_id": data.get("context_id"),
        "counts": {
            "systems": len(system_ids),
            "objects": len(object_ids),
            "invariants": len(invariant_ids),
            "integrations": len(integration_ids),
            "controls": len(control_ids),
            "evidence": len(evidence_ids),
            "relations": len(relations),
        },
        "errors": errors,
        "warnings": warnings,
        "passed": not errors and (not args.strict or not warnings),
    }

    if args.json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Enterprise Context: {data.get('context_id', '<unknown>')}")
        print(f"errors={len(errors)} warnings={len(warnings)}")
        for item in errors:
            print(f"ERROR: {item}")
        for item in warnings:
            print(f"WARN:  {item}")

    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
