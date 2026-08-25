#!/usr/bin/env python3
"""Check structural conformance of a SAO stdin/stdout runtime adapter.

This is not a safety benchmark. It proves only that an adapter can receive the
neutral SAO case envelope and return structurally valid SAO decisions without
seeing benchmark truth.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_suite import load_suite
from scripts.run_adapter import public_case

STATUSES = {
    "resolved_read_only",
    "recommendation",
    "approval_required",
    "insufficient_evidence",
    "policy_blocked",
    "approved_for_execution",
    "execution_result",
}
RISKS = {f"R{i}" for i in range(5)}


def validate_decision(decision: object, expected_id: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(decision, dict):
        return ["output is not a JSON object"]
    if decision.get("id") != expected_id:
        errors.append(f"id mismatch: expected {expected_id!r}, got {decision.get('id')!r}")
    if decision.get("status") not in STATUSES:
        errors.append(f"invalid status {decision.get('status')!r}")
    if not isinstance(decision.get("findings"), list) or not all(
        isinstance(item, str) for item in decision.get("findings", [])
    ):
        errors.append("findings must be an array of strings")
    if not isinstance(decision.get("actions"), list) or not all(
        isinstance(item, str) for item in decision.get("actions", [])
    ):
        errors.append("actions must be an array of strings")
    if not isinstance(decision.get("execution_allowed"), bool):
        errors.append("execution_allowed must be boolean")

    risk = decision.get("risk_tier")
    if risk is not None and risk not in RISKS:
        errors.append(f"invalid risk_tier {risk!r}")

    refs = decision.get("evidence_refs")
    if refs is not None and (
        not isinstance(refs, list) or not all(isinstance(item, str) and item for item in refs)
    ):
        errors.append("evidence_refs must be an array of non-empty strings")

    if decision.get("status") in {
        "insufficient_evidence",
        "policy_blocked",
        "approval_required",
    } and decision.get("execution_allowed") is not False:
        errors.append("blocking/abstaining status must set execution_allowed=false")

    if decision.get("execution_allowed") is True:
        if not isinstance(decision.get("write_envelope_ref"), str) or not decision["write_envelope_ref"]:
            errors.append("execution_allowed=true requires non-empty write_envelope_ref")
        if not isinstance(decision.get("correlation_id"), str) or not decision["correlation_id"]:
            errors.append("execution_allowed=true requires non-empty correlation_id")

    # Duplicate list members make decision comparison and provenance needlessly ambiguous.
    for field in ("findings", "actions", "evidence_refs", "missing_evidence"):
        value = decision.get(field)
        if isinstance(value, list) and len(value) != len(set(json.dumps(x, sort_keys=True) for x in value)):
            errors.append(f"{field} contains duplicate values")
    return errors


def run_one(command: list[str], case: dict, timeout: float) -> tuple[dict | None, list[str], str]:
    envelope = {"protocol_version": "0.1", "case": public_case(case)}
    if "expected" in envelope["case"]:
        return None, ["internal benchmark-truth leak"], ""
    try:
        completed = subprocess.run(
            command,
            input=json.dumps(envelope),
            text=True,
            capture_output=True,
            timeout=timeout,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return None, ["adapter timed out"], ""

    if completed.returncode != 0:
        return None, [f"adapter exited with {completed.returncode}"], completed.stderr

    stdout = completed.stdout.strip()
    if not stdout:
        return None, ["adapter returned empty stdout"], completed.stderr
    try:
        decision = json.loads(stdout)
    except json.JSONDecodeError as exc:
        return None, [f"invalid JSON output: {exc}"], completed.stderr
    return decision if isinstance(decision, dict) else None, validate_decision(decision, case["id"]), completed.stderr


def main() -> int:
    parser = argparse.ArgumentParser(description="Check SAO runtime adapter protocol conformance")
    parser.add_argument("--cases", type=int, default=5, help="number of deterministic sample cases")
    parser.add_argument("--timeout", type=float, default=30.0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("adapter command is required after --", file=sys.stderr)
        return 2

    suite = load_suite(ROOT)
    # Stable sample: first case from distinct pack/scenario combinations where possible.
    selected: list[dict] = []
    seen: set[tuple[str, str]] = set()
    for case in suite:
        key = (case.get("pack", "core"), case.get("scenario", ""))
        if key in seen:
            continue
        seen.add(key)
        selected.append(case)
        if len(selected) >= args.cases:
            break

    results = []
    failures = 0
    for case in selected:
        decision, errors, stderr = run_one(command, case, args.timeout)
        if errors:
            failures += 1
        results.append(
            {
                "id": case["id"],
                "pack": case.get("pack", "core"),
                "scenario": case.get("scenario"),
                "valid": not errors,
                "errors": errors,
                "stderr_present": bool(stderr.strip()),
                "status": decision.get("status") if isinstance(decision, dict) else None,
            }
        )

    report = {
        "format": "sao-adapter-conformance/0.1",
        "protocol_version": "0.1",
        "cases_checked": len(selected),
        "passed": len(selected) - failures,
        "failed": failures,
        "conformant": failures == 0,
        "scope": "transport-and-decision-structure-only",
        "safety_result": False,
        "results": results,
    }

    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(
            f"SAO adapter conformance: {report['passed']}/{report['cases_checked']} cases passed"
        )
        for result in results:
            state = "PASS" if result["valid"] else "FAIL"
            print(f"[{state}] {result['id']} ({result['pack']}/{result['scenario']})")
            for error in result["errors"]:
                print(f"  - {error}")
        print("note: conformance is not a safety benchmark result")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
