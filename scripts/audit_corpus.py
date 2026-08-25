#!/usr/bin/env python3
"""Audit SAO-Bench corpus structure, coverage, and exact semantic duplicates.

The audit is intentionally deterministic and standard-library only. It is a
release-readiness check, not a semantic judge of whether benchmark truth is
correct. Human review is still required before a frozen release.
"""

from __future__ import annotations

import argparse
import collections
import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CORE = ROOT / "evals" / "cases.jsonl"
PACK_DIR = ROOT / "evals" / "packs"
VALID_RISKS = {f"R{i}" for i in range(5)}
VALID_THREATS = {f"T{i}" for i in range(1, 11)}


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw.strip():
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict):
            raise SystemExit(f"{path}:{line_no}: case must be a JSON object")
        row["_source"] = str(path.relative_to(ROOT))
        row["_line"] = line_no
        rows.append(row)
    return rows


def load_cases() -> list[dict[str, Any]]:
    paths = [CORE] + sorted(PACK_DIR.glob("*.jsonl"))
    rows: list[dict[str, Any]] = []
    for path in paths:
        rows.extend(load_jsonl(path))
    return rows


def normalized_expected(case: dict[str, Any]) -> str:
    expected = case.get("expected", {})
    payload = {
        "scenario": case.get("scenario"),
        "expected": expected,
    }
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def semantic_fingerprint(case: dict[str, Any]) -> str:
    return hashlib.sha256(normalized_expected(case).encode("utf-8")).hexdigest()


def audit(cases: list[dict[str, Any]]) -> dict[str, Any]:
    errors: list[str] = []
    warnings: list[str] = []
    ids: dict[str, dict[str, Any]] = {}
    fingerprints: dict[str, list[str]] = collections.defaultdict(list)
    packs: collections.Counter[str] = collections.Counter()
    scenarios: collections.Counter[str] = collections.Counter()
    risks: collections.Counter[str] = collections.Counter()
    threats: collections.Counter[str] = collections.Counter()
    statuses: collections.Counter[str] = collections.Counter()
    executable = 0
    abstaining = 0

    for case in cases:
        source = f"{case.get('_source')}:{case.get('_line')}"
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id.strip():
            errors.append(f"{source}: missing non-empty id")
            continue
        if case_id in ids:
            prev = ids[case_id]
            errors.append(
                f"duplicate id {case_id}: {prev.get('_source')}:{prev.get('_line')} and {source}"
            )
        ids[case_id] = case

        scenario = case.get("scenario")
        if not isinstance(scenario, str) or not scenario.strip():
            errors.append(f"{case_id}: missing scenario")
        else:
            scenarios[scenario] += 1

        pack = case.get("pack") or ("core" if case.get("_source") == "evals/cases.jsonl" else None)
        if not isinstance(pack, str) or not pack.strip():
            warnings.append(f"{case_id}: no pack declared")
            pack = "unclassified"
        packs[pack] += 1

        risk = case.get("risk_tier")
        if risk not in VALID_RISKS:
            errors.append(f"{case_id}: invalid or missing risk_tier {risk!r}")
        else:
            risks[risk] += 1

        case_threats = case.get("threats")
        if not isinstance(case_threats, list) or not case_threats:
            warnings.append(f"{case_id}: no threat classes declared")
        else:
            for threat in case_threats:
                if threat not in VALID_THREATS:
                    errors.append(f"{case_id}: invalid threat class {threat!r}")
                else:
                    threats[threat] += 1

        expected = case.get("expected")
        if not isinstance(expected, dict):
            errors.append(f"{case_id}: expected must be an object")
            continue

        status = expected.get("status")
        if not isinstance(status, str) or not status:
            errors.append(f"{case_id}: expected.status is required")
        else:
            statuses[status] += 1
            if status in {"insufficient_evidence", "policy_blocked"}:
                abstaining += 1

        allowed = expected.get("execution_allowed")
        if allowed is True:
            executable += 1
            if not expected.get("required_actions"):
                warnings.append(f"{case_id}: executable case has no required_actions")
        elif allowed is None:
            warnings.append(f"{case_id}: expected.execution_allowed is not explicit")

        must_identify = expected.get("must_identify")
        required_actions = expected.get("required_actions")
        must_not = expected.get("must_not")
        if not any(
            isinstance(value, list) and value
            for value in (must_identify, required_actions, must_not)
        ):
            warnings.append(f"{case_id}: expected result has no explicit control invariant")

        fingerprints[semantic_fingerprint(case)].append(case_id)

    exact_semantic_duplicates = [
        sorted(case_ids) for case_ids in fingerprints.values() if len(case_ids) > 1
    ]
    for case_ids in exact_semantic_duplicates:
        warnings.append("exact semantic duplicate expectation: " + ", ".join(case_ids))

    missing_risks = sorted(VALID_RISKS - set(risks))
    missing_threats = sorted(VALID_THREATS - set(threats))
    if missing_risks:
        warnings.append("risk tiers with no cases: " + ", ".join(missing_risks))
    if missing_threats:
        warnings.append("threat classes with no cases: " + ", ".join(missing_threats))

    return {
        "format": "sao-corpus-audit/0.1",
        "case_count": len(cases),
        "pack_counts": dict(sorted(packs.items())),
        "scenario_counts": dict(sorted(scenarios.items())),
        "risk_counts": dict(sorted(risks.items())),
        "threat_counts": dict(sorted(threats.items())),
        "status_counts": dict(sorted(statuses.items())),
        "execution_allowed_cases": executable,
        "abstention_or_policy_block_cases": abstaining,
        "exact_semantic_duplicate_groups": exact_semantic_duplicates,
        "errors": errors,
        "warnings": warnings,
        "release_gate": {
            "structural_validity": "pass" if not errors else "fail",
            "human_corpus_review": "required",
            "external_runtime_evidence": "required_for_broad_validity_claims",
        },
    }


def render_text(report: dict[str, Any]) -> str:
    lines = [
        "SAO-Bench corpus audit",
        f"cases: {report['case_count']}",
        "packs: " + ", ".join(f"{k}={v}" for k, v in report["pack_counts"].items()),
        "risks: " + ", ".join(f"{k}={v}" for k, v in report["risk_counts"].items()),
        "threats: " + ", ".join(f"{k}={v}" for k, v in report["threat_counts"].items()),
        f"execution-allowed cases: {report['execution_allowed_cases']}",
        f"abstention/policy-block cases: {report['abstention_or_policy_block_cases']}",
    ]
    if report["errors"]:
        lines.append("errors:")
        lines.extend(f"  - {item}" for item in report["errors"])
    if report["warnings"]:
        lines.append("warnings:")
        lines.extend(f"  - {item}" for item in report["warnings"])
    lines.append(
        "release note: structural validity is not semantic validation; human corpus review remains required"
    )
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true", help="emit JSON report")
    parser.add_argument("--output", type=Path, help="write report to file")
    parser.add_argument("--require-cases", type=int, default=50)
    args = parser.parse_args()

    report = audit(load_cases())
    if report["case_count"] < args.require_cases:
        report["errors"].append(
            f"case count {report['case_count']} is below required minimum {args.require_cases}"
        )
        report["release_gate"]["structural_validity"] = "fail"

    payload = (
        json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
        if args.json
        else render_text(report) + "\n"
    )
    if args.output:
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
