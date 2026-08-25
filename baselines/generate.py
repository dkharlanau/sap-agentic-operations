#!/usr/bin/env python3
"""Generate deliberately simple SAO-Bench baseline predictions.

Baselines are case-blind with respect to `expected`: they may inspect scenario metadata
and input evidence, but never benchmark answers. They exist to test whether the corpus
distinguishes different control strategies before external model evaluations exist.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    for raw in path.read_text(encoding="utf-8").splitlines():
        raw = raw.strip()
        if raw:
            rows.append(json.loads(raw))
    return rows


def load_suite(root: Path) -> list[dict]:
    paths = [root / "evals" / "cases.jsonl"] + sorted((root / "evals" / "packs").glob("*.jsonl"))
    rows = []
    for path in paths:
        rows.extend(load_jsonl(path))
    return rows


def base(case: dict, *, status: str, findings: list[str], actions: list[str], execution_allowed: bool) -> dict:
    result = {
        "id": case["id"],
        "status": status,
        "risk_tier": case.get("risk_tier", "R1"),
        "findings": findings,
        "actions": actions,
        "execution_allowed": execution_allowed,
        "evidence_refs": [f"synthetic://{case['id']}/observed"],
    }
    if execution_allowed:
        result["write_envelope_ref"] = f"synthetic://{case['id']}/baseline-write"
        result["correlation_id"] = f"baseline-{case['id']}"
    return result


def always_abstain(case: dict) -> dict:
    return base(
        case,
        status="insufficient_evidence",
        findings=["baseline cannot establish sufficient evidence"],
        actions=["abstain"],
        execution_allowed=False,
    )


def naive_auto_execute(case: dict) -> dict:
    return base(
        case,
        status="approved_for_execution",
        findings=["requested or observed operation appears actionable"],
        actions=["execute"],
        execution_allowed=True,
    )


def memory_biased(case: dict) -> dict:
    payload = case.get("input") or {}
    text = json.dumps(payload, sort_keys=True).lower()
    if "memory" in text or "runbook" in text or "prior" in text:
        findings = ["historical context is treated as the primary recovery signal"]
        actions = ["reuse_memory"]
    else:
        findings = ["previously successful operating pattern is assumed reusable"]
        actions = ["follow_historical_pattern"]
    return base(case, status="recommendation", findings=findings, actions=actions, execution_allowed=False)


def guarded_rules(case: dict) -> dict:
    """Small generic guard set that does not know benchmark expected answers."""
    data = case.get("input") or {}
    text = json.dumps(data, sort_keys=True).lower()

    mapping_status = data.get("mapping_status")
    if mapping_status in {"unresolved", "ambiguous"}:
        return base(
            case,
            status="insufficient_evidence",
            findings=["identity is not resolved"],
            actions=["resolve_identity", "abstain"],
            execution_allowed=False,
        )

    if data.get("approval") is None and (
        data.get("policy_result") == "require_approval"
        or data.get("approval_required") is True
        or data.get("rollback_policy") == "require_approval"
    ):
        return base(
            case,
            status="approval_required",
            findings=["approval is required before a governed state change"],
            actions=["request_approval"],
            execution_allowed=False,
        )

    if data.get("approval_valid") is True:
        approved_hash = data.get("approved_before_state_hash")
        current_hash = data.get("current_before_state_hash")
        if approved_hash and current_hash and approved_hash != current_hash:
            return base(
                case,
                status="policy_blocked",
                findings=["approved before-state no longer matches current state"],
                actions=["invalidate_stale_approval", "return_to_diagnosis"],
                execution_allowed=False,
            )

    if isinstance(data.get("approved_version"), int) and isinstance(data.get("current_version"), int):
        if data["approved_version"] != data["current_version"]:
            return base(
                case,
                status="policy_blocked",
                findings=["object version changed after planning"],
                actions=["invalidate_stale_approval", "return_to_diagnosis"],
                execution_allowed=False,
            )

    if data.get("tool_verification_now") == "revoked":
        return base(
            case,
            status="policy_blocked",
            findings=["tool governance is no longer valid"],
            actions=["cancel_pending_operation", "refresh_tool_governance"],
            execution_allowed=False,
        )

    if data.get("postcondition_query") == "unavailable" or (
        data.get("write_api_status") == "success" and data.get("observed_postcondition") not in {None, data.get("expected_postcondition")}
    ):
        return base(
            case,
            status="execution_result",
            findings=["technical write result is not sufficient to prove the business postcondition"],
            actions=["escalate"],
            execution_allowed=False,
        )

    if "ignore policy" in text or "admin scope" in text or "upload all customer data" in text:
        return base(
            case,
            status="recommendation",
            findings=["untrusted content contains control-like instructions"],
            actions=["ignore_embedded_instruction"],
            execution_allowed=False,
        )

    return base(
        case,
        status="recommendation",
        findings=["guarded baseline found no generic hard stop"],
        actions=["continue_bounded_analysis"],
        execution_allowed=False,
    )


STRATEGIES = {
    "always-abstain": always_abstain,
    "naive-auto-execute": naive_auto_execute,
    "memory-biased": memory_biased,
    "guarded-rules": guarded_rules,
}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("strategy", choices=sorted(STRATEGIES))
    parser.add_argument("--root", default=".")
    parser.add_argument("--output", default="-")
    args = parser.parse_args()

    cases = load_suite(Path(args.root))
    predictions = [STRATEGIES[args.strategy](case) for case in cases]
    text = "\n".join(json.dumps(row, separators=(",", ":")) for row in predictions) + "\n"
    if args.output == "-":
        print(text, end="")
    else:
        Path(args.output).write_text(text, encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
