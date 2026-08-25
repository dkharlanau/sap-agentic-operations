#!/usr/bin/env python3
"""Select a deterministic, risk-aware SAO-Bench subset for low-cost smoke experiments."""

from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_suite import load_suite

RISK_ORDER = {"R4": 0, "R3": 1, "R2": 2, "R1": 3, "R0": 4}


def select(cases: list[dict], limit: int) -> list[dict]:
    if limit <= 0 or limit >= len(cases):
        return list(cases)

    by_pack: dict[str, list[dict]] = defaultdict(list)
    for case in cases:
        by_pack[case.get("pack", "core")].append(case)

    for pack in by_pack:
        by_pack[pack].sort(
            key=lambda case: (
                RISK_ORDER.get(case.get("risk_tier", "R0"), 9),
                -len(case.get("threats", [])),
                case["id"],
            )
        )

    selected: list[dict] = []
    selected_ids: set[str] = set()
    packs = sorted(by_pack)

    # Round-robin across packs first, prioritizing high business impact within each pack.
    index = 0
    while len(selected) < limit:
        progressed = False
        for pack in packs:
            rows = by_pack[pack]
            if index < len(rows):
                case = rows[index]
                if case["id"] not in selected_ids:
                    selected.append(case)
                    selected_ids.add(case["id"])
                    progressed = True
                    if len(selected) >= limit:
                        break
        if not progressed:
            break
        index += 1

    # Fill any remainder globally by risk/threat richness.
    if len(selected) < limit:
        remaining = [case for case in cases if case["id"] not in selected_ids]
        remaining.sort(
            key=lambda case: (
                RISK_ORDER.get(case.get("risk_tier", "R0"), 9),
                -len(case.get("threats", [])),
                case["id"],
            )
        )
        selected.extend(remaining[: limit - len(selected)])

    return selected


def main() -> int:
    parser = argparse.ArgumentParser(description="Select a deterministic SAO smoke subset")
    parser.add_argument("--limit", type=int, default=12)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    cases = load_suite(ROOT)
    chosen = select(cases, args.limit)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with args.output.open("w", encoding="utf-8") as handle:
        for case in chosen:
            handle.write(json.dumps(case, separators=(",", ":"), ensure_ascii=False) + "\n")

    print(f"selected {len(chosen)}/{len(cases)} SAO cases -> {args.output}")
    for case in chosen:
        print(
            f"  {case['id']} | {case.get('pack','core')} | {case.get('risk_tier')} | "
            + ",".join(case.get("threats", []))
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
