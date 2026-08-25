#!/usr/bin/env python3
"""Zero-dependency command entry point for SAP Agentic Operations.

The CLI intentionally delegates to the repository's auditable scripts rather than
creating a second implementation of benchmark truth.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def run(command: list[str], *, capture: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(
        command,
        cwd=ROOT,
        text=True,
        capture_output=capture,
        check=False,
    )


def python_script(name: str, *args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return run([sys.executable, str(ROOT / "scripts" / name), *args], capture=capture)


def cmd_doctor(_: argparse.Namespace) -> int:
    manifest = json.loads((ROOT / "sao-manifest.json").read_text(encoding="utf-8"))
    checks = [
        ("suite contracts", python_script("validate_suite_contracts.py", capture=True)),
        ("experiment provenance", python_script("validate_experiments.py", capture=True)),
    ]
    print(f"SAO {manifest['version']} — {manifest['benchmark']['caseCount']} benchmark cases")
    print(f"simulator: {manifest['simulator']['version']} | stateful={manifest['simulator']['stateful']} | faultInjection={manifest['simulator']['faultInjection']}")
    failed = False
    for label, result in checks:
        ok = result.returncode == 0
        print(f"{'OK' if ok else 'FAIL':4}  {label}")
        if not ok:
            failed = True
            detail = (result.stderr or result.stdout).strip()
            if detail:
                print(detail)
    return 1 if failed else 0


def cmd_validate(_: argparse.Namespace) -> int:
    result = python_script("validate_suite_contracts.py")
    if result.returncode:
        return result.returncode
    return python_script("validate_experiments.py").returncode


def cmd_self_test(args: argparse.Namespace) -> int:
    argv = ["--predictions", "reference", "--require-cases", str(args.require_cases)]
    if args.json:
        argv.append("--json")
    return python_script("evaluate_suite.py", *argv).returncode


def cmd_baselines(args: argparse.Namespace) -> int:
    result = python_script("check_baselines.py", capture=True)
    if result.stdout:
        if args.output:
            Path(args.output).write_text(result.stdout, encoding="utf-8")
            print(f"wrote {args.output}")
        else:
            print(result.stdout, end="")
    if result.stderr:
        print(result.stderr, end="", file=sys.stderr)
    return result.returncode


def cmd_tests(_: argparse.Namespace) -> int:
    return run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]).returncode


def cmd_manifest(args: argparse.Namespace) -> int:
    argv = ["--version", args.version]
    if args.output:
        argv += ["--output", args.output]
    return python_script("build_release_manifest.py", *argv).returncode


def cmd_run_adapter(args: argparse.Namespace) -> int:
    command = list(args.command)
    if command and command[0] == "--":
        command = command[1:]
    if not command:
        print("adapter command is required after --", file=sys.stderr)
        return 2
    return python_script(
        "run_adapter.py",
        "--output",
        args.output,
        "--timeout",
        str(args.timeout),
        "--",
        *command,
    ).returncode


def cmd_score(args: argparse.Namespace) -> int:
    argv = ["--predictions", args.predictions, "--require-cases", str(args.require_cases)]
    if args.json:
        argv.append("--json")
    return python_script("evaluate_suite.py", *argv).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sao", description="SAP Agentic Operations assurance lab")
    sub = parser.add_subparsers(dest="command_name", required=True)

    p = sub.add_parser("doctor", help="show project state and run lightweight integrity checks")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("validate", help="validate benchmark and experiment contracts")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("self-test", help="run the reference benchmark self-test")
    p.add_argument("--require-cases", type=int, default=50)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_self_test)

    p = sub.add_parser("baselines", help="profile deterministic benchmark control baselines")
    p.add_argument("--output")
    p.set_defaults(func=cmd_baselines)

    p = sub.add_parser("tests", help="run stateful simulator and adapter safety tests")
    p.set_defaults(func=cmd_tests)

    p = sub.add_parser("manifest", help="build a benchmark integrity manifest")
    p.add_argument("--version", default="0.3-dev")
    p.add_argument("--output")
    p.set_defaults(func=cmd_manifest)

    p = sub.add_parser("run-adapter", help="run an external adapter over the complete suite")
    p.add_argument("--output", required=True)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run_adapter)

    p = sub.add_parser("score", help="score an existing prediction JSONL")
    p.add_argument("predictions")
    p.add_argument("--require-cases", type=int, default=50)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_score)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
