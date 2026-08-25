#!/usr/bin/env python3
"""Validate SAO experiment manifests using the repository's stable core invariants."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HEX40 = re.compile(r"^[0-9a-f]{40}$")
SHA256 = re.compile(r"^sha256:[0-9a-f]{64}$")
RESULT_KINDS = {"reference_self_test", "runtime_evaluation", "simulator_experiment"}


def error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def validate(path: Path) -> list[str]:
    errors: list[str] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{path.relative_to(ROOT)}: {exc}"]

    required = {"schema_version", "experiment_id", "result_kind", "created_at", "benchmark", "runtime", "artifacts"}
    missing = sorted(required - set(data))
    if missing:
        error(errors, path, "missing fields: " + ", ".join(missing))
        return errors

    if data["schema_version"] != "0.1":
        error(errors, path, "schema_version must be 0.1")
    if not isinstance(data["experiment_id"], str) or len(data["experiment_id"]) < 3:
        error(errors, path, "experiment_id must be a non-trivial string")
    if data["result_kind"] not in RESULT_KINDS:
        error(errors, path, f"invalid result_kind {data['result_kind']!r}")
    try:
        datetime.fromisoformat(str(data["created_at"]).replace("Z", "+00:00"))
    except ValueError:
        error(errors, path, "created_at must be ISO-8601 date-time")

    benchmark = data.get("benchmark")
    if not isinstance(benchmark, dict):
        error(errors, path, "benchmark must be an object")
    else:
        if benchmark.get("name") != "SAO-Bench":
            error(errors, path, "benchmark.name must be SAO-Bench")
        if not isinstance(benchmark.get("version"), str) or not benchmark["version"]:
            error(errors, path, "benchmark.version is required")
        commit = benchmark.get("commit")
        if not isinstance(commit, str) or not HEX40.fullmatch(commit):
            error(errors, path, "benchmark.commit must be a 40-character lowercase Git SHA")
        count = benchmark.get("case_count")
        if count is not None and (not isinstance(count, int) or count < 1):
            error(errors, path, "benchmark.case_count must be a positive integer")
        for field in ("corpus_sha256", "evaluator_sha256"):
            value = benchmark.get(field)
            if value is not None and (not isinstance(value, str) or not SHA256.fullmatch(value)):
                error(errors, path, f"benchmark.{field} must be sha256:<64 lowercase hex> or null")

    runtime = data.get("runtime")
    if not isinstance(runtime, dict) or not runtime.get("name") or not runtime.get("version"):
        error(errors, path, "runtime requires name and version")

    artifacts = data.get("artifacts")
    if not isinstance(artifacts, dict) or not artifacts.get("predictions") or not artifacts.get("report"):
        error(errors, path, "artifacts requires predictions and report references")

    if data["result_kind"] == "runtime_evaluation":
        for field in ("agent_config_sha256", "tool_manifest_sha256"):
            value = data.get(field)
            if not isinstance(value, str) or not SHA256.fullmatch(value):
                error(errors, path, f"runtime_evaluation requires {field}=sha256:<64 lowercase hex>")
        for field in ("capability_profile", "policy_profile"):
            if not isinstance(data.get(field), str) or not data[field]:
                error(errors, path, f"runtime_evaluation requires {field}")

    if data["result_kind"] == "simulator_experiment":
        simulator = data.get("simulator")
        if not isinstance(simulator, dict) or not simulator.get("version") or not simulator.get("fixture"):
            error(errors, path, "simulator_experiment requires simulator.version and simulator.fixture")

    return errors


def main() -> int:
    # Ensure the formal schema itself remains parseable even though this validator avoids
    # an external jsonschema dependency for repository CI portability.
    try:
        json.loads((ROOT / "schemas" / "experiment.schema.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid experiment schema: {exc}", file=sys.stderr)
        return 1

    manifests = sorted((ROOT / "experiments").glob("**/*.json"))
    if not manifests:
        print("no experiment manifests found", file=sys.stderr)
        return 1

    errors = []
    seen_ids = set()
    for path in manifests:
        errors.extend(validate(path))
        try:
            experiment_id = json.loads(path.read_text(encoding="utf-8")).get("experiment_id")
        except Exception:
            continue
        if experiment_id in seen_ids:
            errors.append(f"{path.relative_to(ROOT)}: duplicate experiment_id {experiment_id}")
        seen_ids.add(experiment_id)

    if errors:
        print("SAO experiment validation failed:", file=sys.stderr)
        for item in errors:
            print(f"- {item}", file=sys.stderr)
        return 1

    print(f"SAO experiment validation passed: {len(manifests)} manifest(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
