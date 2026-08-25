#!/usr/bin/env python3
"""Build the public SAO result ledger index from committed experiment manifests."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MANIFEST_DIR = ROOT / "results" / "manifests"


def load_manifest(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: manifest must be an object")
    for field in ("experiment_id", "result_kind", "benchmark", "runtime", "artifacts"):
        if field not in data:
            raise ValueError(f"{path}: missing {field}")
    if not isinstance(data["benchmark"], dict) or not isinstance(data["runtime"], dict):
        raise ValueError(f"{path}: benchmark/runtime must be objects")
    return data


def entry_from_manifest(path: Path, data: dict[str, Any]) -> dict[str, Any]:
    benchmark = data["benchmark"]
    runtime = data["runtime"]
    return {
        "experiment_id": data["experiment_id"],
        "result_kind": data["result_kind"],
        "manifest": str(path.relative_to(ROOT)),
        "created_at": data.get("created_at"),
        "benchmark": {
            "version": benchmark.get("version", "unknown"),
            "commit": benchmark.get("commit", "unknown"),
            "case_count": benchmark.get("case_count"),
            "corpus_sha256": benchmark.get("corpus_sha256"),
            "evaluator_sha256": benchmark.get("evaluator_sha256"),
        },
        "runtime": {
            "name": runtime.get("name", "unknown"),
            "version": runtime.get("version", "unknown"),
            "adapter": runtime.get("adapter"),
        },
        "model": data.get("model"),
        "artifacts": data.get("artifacts", {}),
        "notes": data.get("notes"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SAO public result index")
    parser.add_argument("--manifest-dir", type=Path, default=DEFAULT_MANIFEST_DIR)
    parser.add_argument("--output", type=Path, default=ROOT / "results" / "index.json")
    parser.add_argument("--include-example-self-test", action="store_true")
    args = parser.parse_args()

    paths = sorted(args.manifest_dir.glob("*.json")) if args.manifest_dir.exists() else []
    if args.include_example_self_test:
        example = ROOT / "experiments" / "examples" / "reference-self-test.json"
        if example.exists():
            paths.append(example)

    entries = []
    seen = set()
    try:
        for path in paths:
            data = load_manifest(path)
            experiment_id = data["experiment_id"]
            if experiment_id in seen:
                raise ValueError(f"duplicate experiment_id: {experiment_id}")
            seen.add(experiment_id)
            entries.append(entry_from_manifest(path, data))
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    entries.sort(key=lambda item: (item.get("created_at") or "", item["experiment_id"]))
    external_count = sum(item["result_kind"] == "runtime_evaluation" for item in entries)
    index = {
        "schema_version": "0.1",
        "project": "SAP Agentic Operations",
        "entries": entries,
        "policy": {
            "leaderboard_enabled": external_count >= 2,
            "minimum_external_runtime_results_for_leaderboard": 2,
        },
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(index, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote {len(entries)} result entries: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
