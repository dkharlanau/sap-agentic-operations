#!/usr/bin/env python3
"""Compare two SAO benchmark reports and surface control regressions/fixes."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or not isinstance(data.get("results"), list):
        raise ValueError(f"{path}: not a SAO suite report")
    return data


def result_map(report: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for item in report.get("results", []):
        if isinstance(item, dict) and isinstance(item.get("id"), str):
            rows[item["id"]] = item
    return rows


def rate_map(report: dict[str, Any], field: str) -> dict[str, float]:
    raw = report.get(field, {})
    if not isinstance(raw, dict):
        return {}
    result: dict[str, float] = {}
    for key, value in raw.items():
        if isinstance(value, dict) and isinstance(value.get("rate"), (int, float)):
            result[str(key)] = float(value["rate"])
    return result


def deltas(left: dict[str, float], right: dict[str, float]) -> dict[str, float]:
    keys = sorted(set(left) | set(right))
    return {key: round(right.get(key, 0.0) - left.get(key, 0.0), 4) for key in keys}


def build_diff(before: dict[str, Any], after: dict[str, Any]) -> dict[str, Any]:
    a = result_map(before)
    b = result_map(after)
    common = sorted(set(a) & set(b))
    fixed: list[str] = []
    regressed: list[str] = []
    unchanged_pass: list[str] = []
    unchanged_fail: list[str] = []
    changed_failure_detail: list[dict[str, Any]] = []

    for case_id in common:
        a_pass = bool(a[case_id].get("passed"))
        b_pass = bool(b[case_id].get("passed"))
        if not a_pass and b_pass:
            fixed.append(case_id)
        elif a_pass and not b_pass:
            regressed.append(case_id)
        elif a_pass and b_pass:
            unchanged_pass.append(case_id)
        else:
            unchanged_fail.append(case_id)
            if a[case_id].get("failures") != b[case_id].get("failures"):
                changed_failure_detail.append(
                    {
                        "id": case_id,
                        "before": a[case_id].get("failures", []),
                        "after": b[case_id].get("failures", []),
                    }
                )

    score_before = float(before.get("score", 0.0))
    score_after = float(after.get("score", 0.0))
    unsafe_before = int(before.get("unsafe_execution_failures", 0))
    unsafe_after = int(after.get("unsafe_execution_failures", 0))

    return {
        "format": "sao-result-diff/0.1",
        "before": {
            "benchmark": before.get("benchmark"),
            "version": before.get("suite_version"),
            "cases": before.get("cases"),
            "score": score_before,
            "unsafe_execution_failures": unsafe_before,
        },
        "after": {
            "benchmark": after.get("benchmark"),
            "version": after.get("suite_version"),
            "cases": after.get("cases"),
            "score": score_after,
            "unsafe_execution_failures": unsafe_after,
        },
        "score_delta": round(score_after - score_before, 4),
        "unsafe_execution_failure_delta": unsafe_after - unsafe_before,
        "fixed_cases": fixed,
        "regressed_cases": regressed,
        "unchanged_pass_cases": unchanged_pass,
        "unchanged_fail_cases": unchanged_fail,
        "changed_failure_details": changed_failure_detail,
        "added_case_ids": sorted(set(b) - set(a)),
        "removed_case_ids": sorted(set(a) - set(b)),
        "by_pack_rate_delta": deltas(rate_map(before, "by_pack"), rate_map(after, "by_pack")),
        "by_risk_tier_rate_delta": deltas(
            rate_map(before, "by_risk_tier"), rate_map(after, "by_risk_tier")
        ),
        "by_threat_rate_delta": deltas(rate_map(before, "by_threat"), rate_map(after, "by_threat")),
        "regression": bool(regressed) or unsafe_after > unsafe_before,
    }


def render(diff: dict[str, Any]) -> str:
    lines = [
        "SAO result diff",
        f"score: {diff['before']['score']:.1%} -> {diff['after']['score']:.1%} ({diff['score_delta']:+.1%})",
        f"unsafe execution failures: {diff['before']['unsafe_execution_failures']} -> {diff['after']['unsafe_execution_failures']}",
        f"fixed cases: {len(diff['fixed_cases'])}",
        f"regressed cases: {len(diff['regressed_cases'])}",
    ]
    if diff["fixed_cases"]:
        lines.append("  fixed: " + ", ".join(diff["fixed_cases"]))
    if diff["regressed_cases"]:
        lines.append("  regressed: " + ", ".join(diff["regressed_cases"]))
    if diff["added_case_ids"]:
        lines.append("  added cases: " + ", ".join(diff["added_case_ids"]))
    if diff["removed_case_ids"]:
        lines.append("  removed cases: " + ", ".join(diff["removed_case_ids"]))
    lines.append("regression: " + ("YES" if diff["regression"] else "no"))
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="Diff two SAO suite reports")
    parser.add_argument("before", type=Path)
    parser.add_argument("after", type=Path)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--fail-on-regression", action="store_true")
    args = parser.parse_args()

    try:
        diff = build_diff(load(args.before), load(args.after))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    print(json.dumps(diff, indent=2, sort_keys=True) if args.json else render(diff))
    return 1 if args.fail_on_regression and diff["regression"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
