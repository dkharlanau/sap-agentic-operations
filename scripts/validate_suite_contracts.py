#!/usr/bin/env python3
"""Validate SAO-Bench structural and coverage contracts without external dependencies."""

from __future__ import annotations

import json
import re
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
THREAT_RE = re.compile(r"^T(?:10|[1-9])$")
SAFE_NON_EXECUTION = {"insufficient_evidence", "policy_blocked", "approval_required"}
POLICY_BOUNDARY = {"policy_blocked", "approval_required", "approved_for_execution"}


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open("r", encoding="utf-8") as handle:
        for line_no, raw in enumerate(handle, 1):
            raw = raw.strip()
            if not raw:
                continue
            try:
                row = json.loads(raw)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            row["_source"] = f"{path.relative_to(ROOT)}:{line_no}"
            rows.append(row)
    return rows


def main() -> int:
    decision_schema = json.loads((ROOT / "schemas" / "decision.schema.json").read_text(encoding="utf-8"))
    allowed_status = set(decision_schema["properties"]["status"]["enum"])
    allowed_risk = set(decision_schema["properties"]["risk_tier"]["enum"])

    paths = [ROOT / "evals" / "cases.jsonl"] + sorted((ROOT / "evals" / "packs").glob("*.jsonl"))
    rows = []
    for path in paths:
        rows.extend(load_jsonl(path))

    errors = []
    seen = set()
    pack_statuses = defaultdict(set)
    pack_counts = defaultdict(int)

    for row in rows:
        source = row["_source"]
        case_id = row.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{source}: missing id")
            continue
        if case_id in seen:
            errors.append(f"{source}: duplicate case id {case_id}")
        seen.add(case_id)

        risk = row.get("risk_tier")
        if risk not in allowed_risk:
            errors.append(f"{source}: invalid risk_tier {risk!r}")

        threats = row.get("threats")
        if not isinstance(threats, list) or not threats:
            errors.append(f"{source}: threats must be a non-empty list")
        elif any(not isinstance(x, str) or not THREAT_RE.match(x) for x in threats):
            errors.append(f"{source}: invalid threat class in {threats!r}")

        expected = row.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{source}: missing expected object")
            continue
        status = expected.get("status")
        if status not in allowed_status:
            errors.append(f"{source}: expected.status {status!r} not allowed by decision schema")
        execution_allowed = expected.get("execution_allowed")
        if not isinstance(execution_allowed, bool):
            errors.append(f"{source}: expected.execution_allowed must be boolean")
        if status in SAFE_NON_EXECUTION and execution_allowed is not False:
            errors.append(f"{source}: {status} must set execution_allowed=false")
        if execution_allowed is True and status != "approved_for_execution":
            errors.append(f"{source}: execution_allowed=true requires status=approved_for_execution")
        if status == "approved_for_execution" and execution_allowed is not True:
            errors.append(f"{source}: approved_for_execution requires execution_allowed=true")

        for field in ("must_identify", "required_actions"):
            value = expected.get(field)
            if not isinstance(value, list) or not value or not all(isinstance(x, str) and x for x in value):
                errors.append(f"{source}: expected.{field} must be a non-empty string list")
        if "must_not" in expected:
            value = expected["must_not"]
            if not isinstance(value, list) or not all(isinstance(x, str) and x for x in value):
                errors.append(f"{source}: expected.must_not must be a string list")

        pack = row.get("pack", "core")
        pack_counts[pack] += 1
        pack_statuses[pack].add(status)

    if len(rows) < 50:
        errors.append(f"suite coverage: expected >=50 cases, got {len(rows)}")

    for pack in sorted(k for k in pack_counts if k != "core"):
        statuses = pack_statuses[pack]
        if "insufficient_evidence" not in statuses:
            errors.append(f"pack {pack}: must contain at least one insufficient_evidence case")
        if not (statuses & POLICY_BOUNDARY):
            errors.append(f"pack {pack}: must contain an explicit policy/approval/execution boundary")

    if errors:
        print("SAO suite contract validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"SAO suite contract validation passed: {len(rows)} cases across {len(pack_counts)} packs")
    for pack in sorted(pack_counts):
        print(f"  {pack}: {pack_counts[pack]} cases; statuses={','.join(sorted(pack_statuses[pack]))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
