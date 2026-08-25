#!/usr/bin/env python3
"""Diff two SAO Enterprise Context Graph snapshots and surface architecture drift."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

CAPABILITY_ORDER = {"read": 0, "recommend": 1, "approve": 2, "execute": 3}


def load(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected object")
    return value


def index(rows: object) -> dict[str, dict]:
    if not isinstance(rows, list):
        return {}
    return {str(row["id"]): row for row in rows if isinstance(row, dict) and row.get("id")}


def add(changes: list[dict], severity: str, kind: str, subject: str, before: object, after: object, rationale: str) -> None:
    changes.append({
        "severity": severity,
        "kind": kind,
        "subject": subject,
        "before": before,
        "after": after,
        "rationale": rationale,
    })


def authority_signature(obj: dict) -> list[tuple]:
    result = []
    for item in obj.get("authority") or []:
        if isinstance(item, dict):
            result.append((item.get("scope"), item.get("system_id"), item.get("effective_from"), item.get("effective_to")))
    return sorted(result)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff two SAO enterprise architecture contexts")
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--json", action="store_true", dest="json_output")
    parser.add_argument("--fail-on-high-risk", action="store_true")
    args = parser.parse_args()

    try:
        before = load(args.before)
        after = load(args.after)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    changes: list[dict] = []

    before_systems = index(before.get("systems"))
    after_systems = index(after.get("systems"))
    for sid in sorted(set(before_systems) | set(after_systems)):
        b = before_systems.get(sid)
        a = after_systems.get(sid)
        if b is None:
            add(changes, "low", "system_added", sid, None, a, "New system entered the architecture context.")
        elif a is None:
            add(changes, "high", "system_removed", sid, b, None, "Removing a system can invalidate ownership, integration and evidence assumptions.")
        elif b.get("role") != a.get("role"):
            add(changes, "high", "system_role_changed", sid, b.get("role"), a.get("role"), "System role changes can alter system-of-record and governance semantics.")
        elif b.get("clean_core_boundary") != a.get("clean_core_boundary"):
            add(changes, "medium", "extension_boundary_changed", sid, b.get("clean_core_boundary"), a.get("clean_core_boundary"), "Extension placement changed and should be reviewed for lifecycle/coupling consequences.")

    before_objects = index(before.get("objects"))
    after_objects = index(after.get("objects"))
    for oid in sorted(set(before_objects) & set(after_objects)):
        b = before_objects[oid]
        a = after_objects[oid]
        bsig = authority_signature(b)
        asig = authority_signature(a)
        if bsig != asig:
            add(changes, "high", "authority_changed", oid, bsig, asig, "Business/data authority changed; dependent integrations, policies and agent assumptions require review.")
        b_ids = {(item.get("system_id"), item.get("identity"), item.get("mapping_version")) for item in b.get("system_identities") or [] if isinstance(item, dict)}
        a_ids = {(item.get("system_id"), item.get("identity"), item.get("mapping_version")) for item in a.get("system_identities") or [] if isinstance(item, dict)}
        if b_ids != a_ids:
            add(changes, "medium", "identity_mapping_changed", oid, sorted(b_ids), sorted(a_ids), "Cross-system identity or mapping-version semantics changed.")

    before_integrations = index(before.get("integrations"))
    after_integrations = index(after.get("integrations"))
    for iid in sorted(set(before_integrations) | set(after_integrations)):
        b = before_integrations.get(iid)
        a = after_integrations.get(iid)
        if b is None:
            add(changes, "medium", "integration_added", iid, None, a, "New integration adds coupling, failure and recovery paths.")
            continue
        if a is None:
            add(changes, "high", "integration_removed", iid, b, None, "Removed integration may break business-state propagation or reconciliation.")
            continue
        for field, severity, rationale in [
            ("producer", "high", "Producer/system authority path changed."),
            ("consumer", "high", "Consumer/system-of-record path changed."),
            ("interaction", "high", "Interaction style changes delivery/failure semantics."),
            ("correlation_key", "high", "Correlation change can break causality and supportability."),
            ("ordering", "medium", "Ordering semantics changed."),
            ("idempotency", "high", "Idempotency semantics changed and can affect duplicate/retry safety."),
            ("postcondition", "high", "Business success/verification semantics changed."),
            ("recovery_owner", "medium", "Operational recovery ownership changed."),
        ]:
            if b.get(field) != a.get(field):
                add(changes, severity, f"integration_{field}_changed", iid, b.get(field), a.get(field), rationale)

    before_controls = index(before.get("controls"))
    after_controls = index(after.get("controls"))
    for cid in sorted(set(before_controls) | set(after_controls)):
        b = before_controls.get(cid)
        a = after_controls.get(cid)
        if b is None:
            add(changes, "low", "control_added", cid, None, a, "New explicit control added.")
        elif a is None:
            add(changes, "high", "control_removed", cid, b, None, "Removing a control can leave a business invariant unprotected.")
        elif (b.get("kind"), b.get("statement")) != (a.get("kind"), a.get("statement")):
            add(changes, "medium", "control_changed", cid, {"kind": b.get("kind"), "statement": b.get("statement")}, {"kind": a.get("kind"), "statement": a.get("statement")}, "Control semantics changed and should be revalidated against tests/evals.")

    before_evidence = index(before.get("evidence"))
    after_evidence = index(after.get("evidence"))
    for eid in sorted(set(before_evidence) - set(after_evidence)):
        add(changes, "medium", "evidence_removed", eid, before_evidence[eid], None, "Removing evidence can reduce diagnosability, auditability or proof of business outcome.")

    b_agent = before.get("agent_boundary") if isinstance(before.get("agent_boundary"), dict) else {}
    a_agent = after.get("agent_boundary") if isinstance(after.get("agent_boundary"), dict) else {}
    b_cap = b_agent.get("max_capability")
    a_cap = a_agent.get("max_capability")
    if b_cap != a_cap:
        b_level = CAPABILITY_ORDER.get(str(b_cap), -1)
        a_level = CAPABILITY_ORDER.get(str(a_cap), -1)
        severity = "high" if a_level > b_level else "medium"
        add(changes, severity, "agent_capability_changed", "agent_boundary", b_cap, a_cap, "Capability increase is a material authorization/assurance change." if severity == "high" else "Capability boundary changed.")
    if b_agent.get("execution_gate") != a_agent.get("execution_gate"):
        add(changes, "high", "execution_gate_changed", "agent_boundary", b_agent.get("execution_gate"), a_agent.get("execution_gate"), "Execution gate changes alter the conditions under which enterprise state may change.")

    b_cut = before.get("cutover") if isinstance(before.get("cutover"), dict) else {}
    a_cut = after.get("cutover") if isinstance(after.get("cutover"), dict) else {}
    for field, severity in [("phase", "high"), ("authority_transition", "high"), ("delta_watermark", "medium"), ("mapping_version", "medium")]:
        if b_cut.get(field) != a_cut.get(field):
            add(changes, severity, f"cutover_{field}_changed", "cutover", b_cut.get(field), a_cut.get(field), "Cutover context changed; in-flight/reconciliation/recovery assumptions should be re-evaluated.")

    counts = {"high": 0, "medium": 0, "low": 0}
    for change in changes:
        counts[change["severity"]] += 1

    report = {
        "format": "sao-enterprise-context-diff/0.1",
        "before": {"path": str(args.before), "context_id": before.get("context_id")},
        "after": {"path": str(args.after), "context_id": after.get("context_id")},
        "summary": {"changes": len(changes), **counts},
        "changes": changes,
        "high_risk_review_required": counts["high"] > 0,
        "disclaimer": "Severity indicates review priority, not automatic architecture rejection. Human architectural judgment remains required.",
    }

    if args.json_output:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Enterprise Context diff: {len(changes)} change(s); high={counts['high']} medium={counts['medium']} low={counts['low']}")
        for item in changes:
            print(f"[{item['severity'].upper()}] {item['kind']} — {item['subject']}: {item['rationale']}")

    return 1 if args.fail_on_high_risk and counts["high"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
