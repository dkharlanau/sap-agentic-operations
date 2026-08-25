#!/usr/bin/env python3
"""Run any stdin/stdout SAO adapter across the static or generated benchmark cases."""

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


def load_casefile(path: Path) -> list[dict]:
    rows = []
    seen = set()
    for line_no, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        raw = raw.strip()
        if not raw:
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
        if not isinstance(row, dict) or not isinstance(row.get("id"), str) or not row["id"]:
            raise ValueError(f"{path}:{line_no}: case must be an object with non-empty id")
        if row["id"] in seen:
            raise ValueError(f"{path}:{line_no}: duplicate case id {row['id']}")
        seen.add(row["id"])
        rows.append(row)
    if not rows:
        raise ValueError(f"{path}: no cases found")
    return rows


def public_case(case: dict) -> dict:
    result = {
        "id": case["id"],
        "pack": case.get("pack", "core"),
        "scenario": case.get("scenario"),
        "risk_tier": case.get("risk_tier"),
        "threats": case.get("threats", []),
        "input": case.get("input", {}),
    }
    if isinstance(case.get("generation"), dict):
        result["generation"] = {
            key: value
            for key, value in case["generation"].items()
            if key in {"template", "index"}
        }
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a SAO protocol adapter over static or generated cases")
    parser.add_argument("--output", required=True)
    parser.add_argument("--timeout", type=float, default=60.0)
    parser.add_argument("--root", default=".")
    parser.add_argument("--cases", type=Path, help="optional JSONL case file; defaults to the complete static SAO suite")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args()

    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("adapter command is required after --", file=sys.stderr)
        return 2

    try:
        cases = load_casefile(args.cases) if args.cases else load_suite(Path(args.root))
    except (OSError, ValueError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    predictions = []

    for case in cases:
        envelope = {"protocol_version": "0.1", "case": public_case(case)}
        # The benchmark expected answer is intentionally absent from `envelope`.
        if "expected" in envelope["case"]:
            print("internal error: benchmark truth leaked into adapter envelope", file=sys.stderr)
            return 2
        try:
            completed = subprocess.run(
                command,
                input=json.dumps(envelope),
                text=True,
                capture_output=True,
                timeout=args.timeout,
                check=False,
            )
        except subprocess.TimeoutExpired:
            print(f"adapter timeout on case {case['id']}", file=sys.stderr)
            return 1

        if completed.returncode != 0:
            print(f"adapter failed on case {case['id']} with exit {completed.returncode}", file=sys.stderr)
            if completed.stderr:
                print(completed.stderr.rstrip(), file=sys.stderr)
            return 1

        stdout = completed.stdout.strip()
        try:
            prediction = json.loads(stdout)
        except json.JSONDecodeError as exc:
            print(f"adapter returned invalid JSON on {case['id']}: {exc}", file=sys.stderr)
            return 1

        if not isinstance(prediction, dict):
            print(f"adapter output must be an object on {case['id']}", file=sys.stderr)
            return 1
        if prediction.get("id") != case["id"]:
            print(
                f"adapter output id mismatch: expected {case['id']}, got {prediction.get('id')}",
                file=sys.stderr,
            )
            return 1
        predictions.append(prediction)

    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        "\n".join(json.dumps(row, separators=(",", ":")) for row in predictions) + "\n",
        encoding="utf-8",
    )
    print(f"adapter produced {len(predictions)} predictions: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
