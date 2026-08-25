#!/usr/bin/env python3
"""Generate a deterministic integrity manifest for an SAO-Bench snapshot."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def sha256_file(path: Path) -> str:
    return "sha256:" + hashlib.sha256(path.read_bytes()).hexdigest()


def aggregate_hash(paths: list[Path]) -> str:
    digest = hashlib.sha256()
    for path in sorted(paths, key=lambda p: str(p.relative_to(ROOT))):
        rel = str(path.relative_to(ROOT)).replace("\\", "/")
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(path.read_bytes())
        digest.update(b"\0")
    return "sha256:" + digest.hexdigest()


def git_commit() -> str:
    return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()


def count_jsonl(paths: list[Path]) -> int:
    count = 0
    for path in paths:
        for raw in path.read_text(encoding="utf-8").splitlines():
            if raw.strip():
                json.loads(raw)
                count += 1
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", default="0.3-dev")
    parser.add_argument("--commit", default=None)
    parser.add_argument("--output", default="-")
    args = parser.parse_args()

    corpus = [ROOT / "evals" / "cases.jsonl"] + sorted((ROOT / "evals" / "packs").glob("*.jsonl"))
    schemas = sorted((ROOT / "schemas").glob("*.json"))
    evaluators = [
        ROOT / "scripts" / "evaluate_suite.py",
        ROOT / "scripts" / "validate_suite_contracts.py",
    ]

    manifest = {
        "format": "sao-release-manifest/0.1",
        "benchmark": "SAO-Bench",
        "version": args.version,
        "commit": args.commit or git_commit(),
        "case_count": count_jsonl(corpus),
        "corpus": {
            "sha256": aggregate_hash(corpus),
            "files": [
                {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(path)}
                for path in corpus
            ],
        },
        "schemas": {
            "sha256": aggregate_hash(schemas),
            "files": [
                {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(path)}
                for path in schemas
            ],
        },
        "evaluator": {
            "sha256": aggregate_hash(evaluators),
            "files": [
                {"path": str(path.relative_to(ROOT)).replace("\\", "/"), "sha256": sha256_file(path)}
                for path in evaluators
            ],
        },
    }

    text = json.dumps(manifest, indent=2) + "\n"
    if args.output == "-":
        print(text, end="")
    else:
        output = Path(args.output)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(text, encoding="utf-8")
        print(f"wrote {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
