#!/usr/bin/env python3
"""Build a provenance-rich SAO experiment manifest for a concrete run."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_bytes(data: bytes) -> str:
    return "sha256:" + hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def corpus_paths() -> list[Path]:
    return [ROOT / "evals" / "cases.jsonl"] + sorted((ROOT / "evals" / "packs").glob("*.jsonl"))


def corpus_sha256() -> str:
    digest = hashlib.sha256()
    for path in corpus_paths():
        rel = str(path.relative_to(ROOT)).encode("utf-8")
        data = path.read_bytes()
        digest.update(len(rel).to_bytes(4, "big"))
        digest.update(rel)
        digest.update(len(data).to_bytes(8, "big"))
        digest.update(data)
    return "sha256:" + digest.hexdigest()


def count_cases() -> int:
    count = 0
    for path in corpus_paths():
        count += sum(1 for line in path.read_text(encoding="utf-8").splitlines() if line.strip())
    return count


def git_commit() -> str:
    completed = subprocess.run(
        ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True, capture_output=True, check=False
    )
    value = completed.stdout.strip()
    if completed.returncode != 0 or len(value) != 40:
        raise RuntimeError("unable to resolve exact Git commit")
    return value


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def main() -> int:
    parser = argparse.ArgumentParser(description="Build SAO experiment manifest")
    parser.add_argument("--experiment-id", required=True)
    parser.add_argument(
        "--result-kind",
        required=True,
        choices=["reference_self_test", "runtime_evaluation", "simulator_experiment"],
    )
    parser.add_argument("--runtime-name", required=True)
    parser.add_argument("--runtime-version", required=True)
    parser.add_argument("--adapter")
    parser.add_argument("--model-provider")
    parser.add_argument("--model-name")
    parser.add_argument("--model-version")
    parser.add_argument("--agent-config", type=Path)
    parser.add_argument("--tool-manifest", type=Path)
    parser.add_argument("--capability-profile")
    parser.add_argument("--policy-profile")
    parser.add_argument("--predictions", required=True)
    parser.add_argument("--report", required=True)
    parser.add_argument("--audit")
    parser.add_argument("--runner")
    parser.add_argument("--region")
    parser.add_argument("--notes")
    parser.add_argument("--benchmark-version", default="0.3-dev")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.result_kind == "runtime_evaluation":
        missing = []
        if args.agent_config is None:
            missing.append("--agent-config")
        if args.tool_manifest is None:
            missing.append("--tool-manifest")
        if not args.capability_profile:
            missing.append("--capability-profile")
        if not args.policy_profile:
            missing.append("--policy-profile")
        if missing:
            parser.error("runtime_evaluation requires " + ", ".join(missing))

    model = None
    if args.model_provider or args.model_name or args.model_version:
        if not args.model_provider or not args.model_name:
            parser.error("model metadata requires both --model-provider and --model-name")
        model = {
            "provider": args.model_provider,
            "name": args.model_name,
            "version": args.model_version,
        }

    manifest = {
        "schema_version": "0.1",
        "experiment_id": args.experiment_id,
        "result_kind": args.result_kind,
        "created_at": now_utc(),
        "benchmark": {
            "name": "SAO-Bench",
            "version": args.benchmark_version,
            "commit": git_commit(),
            "case_count": count_cases(),
            "corpus_sha256": corpus_sha256(),
            "evaluator_sha256": sha256_file(ROOT / "scripts" / "evaluate_suite.py"),
        },
        "runtime": {
            "name": args.runtime_name,
            "version": args.runtime_version,
            "adapter": args.adapter,
        },
        "model": model,
        "agent_config_sha256": sha256_file(args.agent_config) if args.agent_config else None,
        "tool_manifest_sha256": sha256_file(args.tool_manifest) if args.tool_manifest else None,
        "capability_profile": args.capability_profile,
        "policy_profile": args.policy_profile,
        "simulator": None,
        "artifacts": {
            "predictions": args.predictions,
            "report": args.report,
            "audit": args.audit,
        },
        "environment": {
            "runner": args.runner,
            "region": args.region,
        },
        "notes": args.notes,
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(f"wrote SAO experiment manifest: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
