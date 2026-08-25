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
    return subprocess.run(command, cwd=ROOT, text=True, capture_output=capture, check=False)


def python_script(name: str, *args: str, capture: bool = False) -> subprocess.CompletedProcess:
    return run([sys.executable, str(ROOT / "scripts" / name), *args], capture=capture)


def cmd_doctor(_: argparse.Namespace) -> int:
    manifest = json.loads((ROOT / "sao-manifest.json").read_text(encoding="utf-8"))
    checks = [
        ("project public state", python_script("validate_project_state.py", capture=True)),
        ("enterprise context", python_script("check_enterprise_context.py", "examples/enterprise-context/customer-replication.json", "--strict", capture=True)),
        ("suite contracts", python_script("validate_suite_contracts.py", capture=True)),
        ("corpus audit", python_script("audit_corpus.py", "--require-cases", "50", capture=True)),
        ("experiment provenance", python_script("validate_experiments.py", capture=True)),
    ]
    print(f"SAO {manifest['version']} — {manifest['benchmark']['caseCount']} benchmark cases")
    print(
        f"simulator: {manifest['simulator']['version']} | "
        f"stateful={manifest['simulator']['stateful']} | "
        f"faultInjection={manifest['simulator']['faultInjection']}"
    )
    failed = False
    for label, result in checks:
        ok = result.returncode == 0
        print(f"{'OK' if ok else 'FAIL':4}  {label}")
        if not ok:
            failed = True
            detail = (result.stderr or result.stdout).strip()
            if detail:
                print(detail)
    print("note: a healthy harness is not evidence that an external runtime is safe")
    return 1 if failed else 0


def cmd_validate(_: argparse.Namespace) -> int:
    checks = [
        ("validate_project_state.py", []),
        ("check_enterprise_context.py", ["examples/enterprise-context/customer-replication.json", "--strict"]),
        ("validate_suite_contracts.py", []),
        ("audit_corpus.py", ["--require-cases", "50"]),
        ("validate_experiments.py", []),
    ]
    for script, argv in checks:
        result = python_script(script, *argv)
        if result.returncode:
            return result.returncode
    return 0


def cmd_context_check(args: argparse.Namespace) -> int:
    argv = [args.context]
    if args.strict:
        argv.append("--strict")
    if args.json:
        argv.append("--json")
    return python_script("check_enterprise_context.py", *argv).returncode


def cmd_context_diff(args: argparse.Namespace) -> int:
    argv = [args.before, args.after]
    if args.json:
        argv.append("--json")
    if args.fail_on_high_risk:
        argv.append("--fail-on-high-risk")
    return python_script("diff_enterprise_context.py", *argv).returncode


def cmd_audit(args: argparse.Namespace) -> int:
    argv = ["--require-cases", str(args.require_cases)]
    if args.json:
        argv.append("--json")
    if args.output:
        argv += ["--output", args.output]
    return python_script("audit_corpus.py", *argv).returncode


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
    return run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-p", "test_*.py", "-v"]
    ).returncode


def cmd_manifest(args: argparse.Namespace) -> int:
    argv = ["--version", args.version]
    if args.output:
        argv += ["--output", args.output]
    return python_script("build_release_manifest.py", *argv).returncode


def normalized_command(command: list[str]) -> list[str]:
    command = list(command)
    if command and command[0] == "--":
        command = command[1:]
    return command


def cmd_run_adapter(args: argparse.Namespace) -> int:
    command = normalized_command(args.command)
    if not command:
        print("adapter command is required after --", file=sys.stderr)
        return 2
    argv = ["--output", args.output, "--timeout", str(args.timeout)]
    if args.cases:
        argv += ["--cases", args.cases]
    return python_script("run_adapter.py", *argv, "--", *command).returncode


def cmd_adapter_check(args: argparse.Namespace) -> int:
    command = normalized_command(args.command)
    if not command:
        print("adapter command is required after --", file=sys.stderr)
        return 2
    argv = ["--cases", str(args.sample_cases), "--timeout", str(args.timeout)]
    if args.json:
        argv.append("--json")
    return python_script("check_adapter_conformance.py", *argv, "--", *command).returncode


def cmd_score(args: argparse.Namespace) -> int:
    argv = ["--predictions", args.predictions, "--require-cases", str(args.require_cases)]
    if args.json:
        argv.append("--json")
    return python_script("evaluate_suite.py", *argv).returncode


def cmd_score_cases(args: argparse.Namespace) -> int:
    argv = [
        "--cases",
        args.cases,
        "--predictions",
        args.predictions,
        "--require-cases",
        str(args.require_cases),
    ]
    if args.json:
        argv.append("--json")
    return python_script("evaluate_casefile.py", *argv).returncode


def cmd_variants(args: argparse.Namespace) -> int:
    return python_script(
        "generate_variants.py",
        "--seed",
        args.seed,
        "--per-template",
        str(args.per_template),
        "--output",
        args.output,
    ).returncode


def cmd_diff(args: argparse.Namespace) -> int:
    argv = [args.before, args.after]
    if args.json:
        argv.append("--json")
    if args.fail_on_regression:
        argv.append("--fail-on-regression")
    return python_script("diff_results.py", *argv).returncode


def cmd_result_index(args: argparse.Namespace) -> int:
    argv = ["--output", args.output]
    if args.manifest_dir:
        argv += ["--manifest-dir", args.manifest_dir]
    if args.include_example_self_test:
        argv.append("--include-example-self-test")
    return python_script("build_result_index.py", *argv).returncode


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sao", description="SAP Agentic Operations assurance lab")
    sub = parser.add_subparsers(dest="command_name", required=True)

    p = sub.add_parser("doctor", help="show project state and run lightweight integrity checks")
    p.set_defaults(func=cmd_doctor)

    p = sub.add_parser("validate", help="validate public state, enterprise context, corpus and experiment contracts")
    p.set_defaults(func=cmd_validate)

    p = sub.add_parser("context-check", help="run architecture fitness checks on an Enterprise Context Graph")
    p.add_argument("context")
    p.add_argument("--strict", action="store_true")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_context_check)

    p = sub.add_parser("context-diff", help="diff two Enterprise Context Graph snapshots for architecture drift")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("--json", action="store_true")
    p.add_argument("--fail-on-high-risk", action="store_true")
    p.set_defaults(func=cmd_context_diff)

    p = sub.add_parser("audit", help="audit SAO-Bench corpus structure and release-readiness warnings")
    p.add_argument("--require-cases", type=int, default=50)
    p.add_argument("--json", action="store_true")
    p.add_argument("--output")
    p.set_defaults(func=cmd_audit)

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

    p = sub.add_parser("run-adapter", help="run an external adapter over static or generated cases")
    p.add_argument("--output", required=True)
    p.add_argument("--timeout", type=float, default=60.0)
    p.add_argument("--cases", help="optional generated/custom case JSONL")
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_run_adapter)

    p = sub.add_parser("adapter-check", help="check transport/decision conformance of an adapter")
    p.add_argument("--sample-cases", type=int, default=5)
    p.add_argument("--timeout", type=float, default=30.0)
    p.add_argument("--json", action="store_true")
    p.add_argument("command", nargs=argparse.REMAINDER)
    p.set_defaults(func=cmd_adapter_check)

    p = sub.add_parser("score", help="score an existing prediction JSONL against static SAO-Bench")
    p.add_argument("predictions")
    p.add_argument("--require-cases", type=int, default=50)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_score)

    p = sub.add_parser("score-cases", help="score predictions against generated/custom case JSONL")
    p.add_argument("--cases", required=True)
    p.add_argument("--predictions", required=True)
    p.add_argument("--require-cases", type=int, default=1)
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_score_cases)

    p = sub.add_parser("variants", help="generate deterministic adversarial case variants")
    p.add_argument("--seed", required=True)
    p.add_argument("--per-template", type=int, default=3)
    p.add_argument("--output", required=True)
    p.set_defaults(func=cmd_variants)

    p = sub.add_parser("diff", help="diff two SAO suite reports and surface regressions")
    p.add_argument("before")
    p.add_argument("after")
    p.add_argument("--json", action="store_true")
    p.add_argument("--fail-on-regression", action="store_true")
    p.set_defaults(func=cmd_diff)

    p = sub.add_parser("result-index", help="build the public reproducible result ledger index")
    p.add_argument("--manifest-dir")
    p.add_argument("--output", default="results/index.json")
    p.add_argument("--include-example-self-test", action="store_true")
    p.set_defaults(func=cmd_result_index)

    return parser


def main() -> int:
    parser = build_parser()
    args = parser.parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
