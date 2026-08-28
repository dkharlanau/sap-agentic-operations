from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import subprocess
import sys
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.run_customer_governance_reference_case import run_reference_case

DEFAULT_CASE = ROOT / "examples" / "reference-cases" / "customer-governance-o2c" / "case.json"
DEFAULT_OUTPUT = ROOT / "build" / "reference-cases" / "customer-governance-o2c"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"expected JSON object: {path}")
    return value


def _run_json(args: list[str]) -> dict[str, Any]:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {' '.join(args)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    try:
        value = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise AssertionError(
            f"command did not emit JSON: {' '.join(args)}\nstdout:\n{completed.stdout}"
        ) from exc
    if not isinstance(value, dict):
        raise AssertionError(f"command JSON root is not an object: {' '.join(args)}")
    return value


def _run(args: list[str]) -> subprocess.CompletedProcess[str]:
    completed = subprocess.run(
        args,
        cwd=ROOT,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.returncode != 0:
        raise AssertionError(
            f"command failed ({completed.returncode}): {' '.join(args)}\n"
            f"stdout:\n{completed.stdout}\nstderr:\n{completed.stderr}"
        )
    return completed


def _validate_decisions(case: dict[str, Any], path: Path) -> dict[str, Any]:
    data = _load_json(path)
    if data.get("format") != "sao-reference-architecture-decisions/0.1":
        raise AssertionError("architecture decisions use an unsupported format")
    if data.get("case_id") != case["id"]:
        raise AssertionError("architecture decisions point to the wrong case")
    decisions = data.get("decisions")
    if not isinstance(decisions, list):
        raise AssertionError("architecture decisions must contain an array")
    required_concerns = {
        "clean-core-and-extension-placement",
        "integration-pattern",
        "failure-and-recovery",
        "cutover-authority-transition",
    }
    actual_concerns: set[str] = set()
    ids: set[str] = set()
    for decision in decisions:
        if not isinstance(decision, dict):
            raise AssertionError("every architecture decision must be an object")
        decision_id = str(decision.get("id") or "")
        if not decision_id or decision_id in ids:
            raise AssertionError(f"invalid or duplicate architecture decision id: {decision_id!r}")
        ids.add(decision_id)
        actual_concerns.add(str(decision.get("concern") or ""))
        if not decision.get("decision"):
            raise AssertionError(f"{decision_id}: decision text is required")
        refs = decision.get("evidence_refs")
        if not isinstance(refs, list) or not refs:
            raise AssertionError(f"{decision_id}: evidence_refs are required")
        for ref in refs:
            if not (ROOT / str(ref)).exists():
                raise AssertionError(f"{decision_id}: missing evidence ref {ref}")
    missing = sorted(required_concerns - actual_concerns)
    if missing:
        raise AssertionError("architecture decisions missing concerns: " + ", ".join(missing))
    return {
        "passed": True,
        "decisions": len(decisions),
        "concerns": sorted(actual_concerns),
    }


def _validate_traceability(case: dict[str, Any], path: Path) -> dict[str, Any]:
    data = _load_json(path)
    if data.get("format") != "sao-reference-traceability/0.1":
        raise AssertionError("traceability uses an unsupported format")
    if data.get("case_id") != case["id"]:
        raise AssertionError("traceability points to the wrong case")
    requirement = data.get("requirement")
    if not isinstance(requirement, dict) or not requirement.get("id") or not requirement.get("statement"):
        raise AssertionError("traceability requires one explicit business requirement")
    rows = data.get("rows")
    if not isinstance(rows, list) or not rows:
        raise AssertionError("traceability requires at least one row")
    owner_roles = set(case.get("ownership", {}))
    row_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict):
            raise AssertionError("traceability rows must be objects")
        row_id = str(row.get("id") or "")
        if not row_id or row_id in row_ids:
            raise AssertionError(f"invalid or duplicate traceability id: {row_id!r}")
        row_ids.add(row_id)
        for field in ("invariant", "control", "evidence", "tests", "owner"):
            if not row.get(field):
                raise AssertionError(f"{row_id}: missing {field}")
        for test_ref in row["tests"]:
            path_part = str(test_ref).split("#", 1)[0]
            if not (ROOT / path_part).exists():
                raise AssertionError(f"{row_id}: test reference does not exist: {test_ref}")
        unknown_owners = sorted(set(str(owner) for owner in row["owner"]) - owner_roles)
        if unknown_owners:
            raise AssertionError(f"{row_id}: unknown owner roles: {', '.join(unknown_owners)}")
    return {
        "passed": True,
        "requirement_id": requirement["id"],
        "rows": len(rows),
    }


def _validate_runbook(case: dict[str, Any], path: Path) -> dict[str, Any]:
    data = _load_json(path)
    if data.get("format") != "sao-ams-runbook/0.1":
        raise AssertionError("AMS runbook uses an unsupported format")
    if data.get("case_id") != case["id"]:
        raise AssertionError("AMS runbook points to the wrong case")
    if data.get("status") != "current-reference":
        raise AssertionError("AMS runbook is not current-reference")
    if data.get("production_status") != "not-approved-for-production":
        raise AssertionError("reference runbook must not imply production approval")
    provenance = data.get("provenance")
    if not isinstance(provenance, dict):
        raise AssertionError("AMS runbook provenance is required")
    for field in ("owner_role", "source_contract", "published_on", "review_due_on", "review_rule"):
        if not provenance.get(field):
            raise AssertionError(f"AMS runbook provenance missing {field}")
    source_contract = ROOT / str(provenance["source_contract"])
    if not source_contract.exists():
        raise AssertionError("AMS runbook source contract does not exist")
    due = date.fromisoformat(str(provenance["review_due_on"]))
    published = date.fromisoformat(str(provenance["published_on"]))
    if due <= published:
        raise AssertionError("AMS runbook review_due_on must be after published_on")
    if date.today() > due:
        raise AssertionError(f"AMS runbook review is overdue since {due.isoformat()}")
    if not data.get("steps") or not data.get("security_boundary") or not data.get("close_condition"):
        raise AssertionError("AMS runbook lacks execution, security or closeout contract")
    return {
        "passed": True,
        "version": data.get("version"),
        "review_due_on": due.isoformat(),
        "production_status": data.get("production_status"),
    }


def _architecture_fitness(case: dict[str, Any]) -> dict[str, Any]:
    context = ROOT / str(case["reference_artifacts"]["enterprise_context"])
    report = _run_json([
        sys.executable,
        "scripts/check_enterprise_context.py",
        str(context.relative_to(ROOT)),
        "--strict",
        "--json",
    ])
    if report.get("passed") is not True or report.get("errors") or report.get("warnings"):
        raise AssertionError(f"enterprise context fitness is not strict-green: {report}")
    return report


def _benchmark_assurance(case: dict[str, Any], output: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    contract = case["benchmark_assurance"]
    cases_file = str(contract["cases_file"])
    report = _run_json([
        sys.executable,
        "sao.py",
        "score-cases",
        "--cases",
        cases_file,
        "--predictions",
        str(contract["predictions"]),
        "--json",
    ])
    if report.get("failed") != 0 or report.get("score") != 1.0:
        raise AssertionError("reference SAO-Bench predictions are not fully green")
    by_id = {row["id"]: row for row in report.get("results", []) if isinstance(row, dict) and row.get("id")}
    mapped = []
    for case_id in contract["mapped_case_ids"]:
        result = by_id.get(case_id)
        if result is None:
            raise AssertionError(f"mapped benchmark case does not exist: {case_id}")
        if result.get("passed") is not True:
            raise AssertionError(f"mapped benchmark case failed: {case_id}")
        mapped.append({
            "id": case_id,
            "passed": True,
            "risk_tier": result.get("risk_tier"),
            "threats": result.get("threats", []),
        })
    mapped_report = {
        "format": "sao-reference-benchmark-map/0.1",
        "case_id": case["id"],
        "mapped_cases": mapped,
        "passed": len(mapped),
        "failed": 0,
    }

    dynamic = contract["dynamic_variants"]
    variants_path = output / "dynamic-variants.jsonl"
    _run([
        sys.executable,
        "sao.py",
        "variants",
        "--seed",
        str(dynamic["seed"]),
        "--per-template",
        str(dynamic["per_template"]),
        "--output",
        str(variants_path),
    ])
    rows = [json.loads(line) for line in variants_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if len(rows) != int(dynamic["expected_case_count"]):
        raise AssertionError(f"dynamic variant count drifted: {len(rows)}")
    templates = {str(row.get("generation", {}).get("template")) for row in rows}
    if templates != set(dynamic["templates"]):
        raise AssertionError(f"dynamic variant template set drifted: {sorted(templates)}")
    dynamic_report = _run_json([
        sys.executable,
        "sao.py",
        "score-cases",
        "--cases",
        str(variants_path),
        "--predictions",
        "reference",
        "--json",
    ])
    if dynamic_report.get("failed") != 0 or dynamic_report.get("passed") != len(rows):
        raise AssertionError("dynamic adversarial reference score is not fully green")
    dynamic_report["reference_case_id"] = case["id"]
    dynamic_report["published_seed"] = dynamic["seed"]
    dynamic_report["templates"] = sorted(templates)
    return report, {"mapped": mapped_report, "dynamic": dynamic_report}


def _copy_reference_inputs(case: dict[str, Any], output: Path) -> dict[str, str]:
    target_dir = output / "reference-inputs"
    target_dir.mkdir(parents=True, exist_ok=True)
    copied: dict[str, str] = {}
    sources = {
        "case.json": DEFAULT_CASE,
        "enterprise-context.json": ROOT / case["reference_artifacts"]["enterprise_context"],
        "architecture-decisions.json": ROOT / case["reference_artifacts"]["architecture_decisions"],
        "traceability.json": ROOT / case["reference_artifacts"]["traceability"],
        "ams-runbook.json": ROOT / case["reference_artifacts"]["ams_runbook"],
    }
    for name, source in sources.items():
        target = target_dir / name
        shutil.copy2(source, target)
        copied[name] = str(target.relative_to(output))
    return copied


def _write_json(path: Path, value: Any) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def _render_review(summary: dict[str, Any]) -> str:
    return "\n".join([
        "# Customer Governance → O2C Reference Review Set",
        "",
        "Status: **review-ready synthetic assurance**. This is not external practitioner validation and not production approval.",
        "",
        "## What is proven in this bundle",
        "",
        f"- Enterprise architecture fitness: **PASS** ({summary['architecture_fitness']['systems']} systems, {summary['architecture_fitness']['integrations']} integration).",
        f"- Explicit architecture decisions: **{summary['architecture_decisions']}**.",
        f"- Requirement/control traceability rows: **{summary['traceability_rows']}**.",
        f"- Incident + control-plane contracts: **{summary['reference_contracts_passed']}/{summary['reference_contracts']} PASS**.",
        f"- Mapped SAO-Bench cases: **{summary['mapped_benchmark_passed']}/{summary['mapped_benchmark_cases']} PASS**.",
        f"- Deterministic adversarial variants: **{summary['dynamic_variants_passed']}/{summary['dynamic_variants']} PASS** across six invariant templates.",
        f"- AMS runbook: version **{summary['runbook_version']}**, review due **{summary['runbook_review_due_on']}**.",
        "",
        "## Decision chain",
        "",
        "`business requirement → invariant → architecture/integration decision → observable evidence → incident classification → governed recovery → target business postcondition → AMS handover`",
        "",
        "The machine-readable `traceability.json` ties the business requirement to controls, evidence, tests and owner roles. `architecture-decisions.json` records clean-core/extension placement, integration, failure/recovery and cutover decisions with reversal triggers.",
        "",
        "## Runtime assurance",
        "",
        "The executable case includes a known-good governed correction plus deliberately unsafe or broken paths: missing current event, mapping/identity drift, technical failure, business rejection, stale target evidence, expired approval, failed postcondition, duplicate event delivery and untrusted tool-output instructions.",
        "",
        "A successful corrective write is only accepted when identity, policy, scoped approval, precondition, idempotency and business postcondition all hold. The generated SAO-Trace retains the before/after hashes and audit reference explaining why the transition happened.",
        "",
        "## Benchmark and adversarial evidence",
        "",
        "The reference set re-scores the current public SAO-Bench reference predictions and requires every benchmark case mapped to this vertical scenario to pass. It also generates a reproducible 12-case adversarial corpus from six templates and requires the reference control policy to pass all generated cases.",
        "",
        "## AMS handover",
        "",
        "The versioned runbook includes provenance, a review due date, stop conditions, recovery ownership and a clear production boundary. Runbook-like text found inside untrusted evidence remains evidence-only and cannot become control authority.",
        "",
        "## Limitations",
        "",
        "- Synthetic public reference only; no customer landscape or client data is used.",
        "- No production SAP connector, transaction, API or authorization role is claimed.",
        "- The simulator proves control semantics, not production SAP side effects.",
        "- Reference predictions and deterministic CI are author-side assurance, not independent validation.",
        "- External practitioner runs remain the next maturity gate before expanding the product horizontally.",
        "",
    ])


def build_review_set(case_path: Path, output: Path, *, force: bool = False) -> dict[str, Any]:
    case_path = case_path.resolve()
    output = output.resolve()
    base_packet = run_reference_case(case_path, output, force=force)
    case = _load_json(case_path)

    refs = case["reference_artifacts"]
    decisions = _validate_decisions(case, ROOT / refs["architecture_decisions"])
    traceability = _validate_traceability(case, ROOT / refs["traceability"])
    runbook = _validate_runbook(case, ROOT / refs["ams_runbook"])
    fitness = _architecture_fitness(case)
    benchmark, benchmark_layers = _benchmark_assurance(case, output)

    _write_json(output / "architecture-fitness.json", fitness)
    _write_json(output / "benchmark-report.json", benchmark)
    _write_json(output / "benchmark-mapped.json", benchmark_layers["mapped"])
    _write_json(output / "dynamic-variant-report.json", benchmark_layers["dynamic"])
    copied = _copy_reference_inputs(case, output)

    summary = {
        "reference_contracts": int(base_packet["summary"]["scenarios"]),
        "reference_contracts_passed": int(base_packet["summary"]["passed"]),
        "architecture_fitness": fitness["counts"],
        "architecture_decisions": int(decisions["decisions"]),
        "traceability_rows": int(traceability["rows"]),
        "mapped_benchmark_cases": int(benchmark_layers["mapped"]["passed"]),
        "mapped_benchmark_passed": int(benchmark_layers["mapped"]["passed"]),
        "dynamic_variants": int(benchmark_layers["dynamic"]["cases"]),
        "dynamic_variants_passed": int(benchmark_layers["dynamic"]["passed"]),
        "runbook_version": runbook["version"],
        "runbook_review_due_on": runbook["review_due_on"],
    }
    review_path = output / "reference-review.md"
    review_path.write_text(_render_review(summary), encoding="utf-8")

    manifest: dict[str, dict[str, Any]] = {}
    for path in sorted(output.rglob("*")):
        if path.is_file() and path.name != "reference-review-set.json":
            relative = str(path.relative_to(output))
            manifest[relative] = {
                "sha256": _sha256(path),
                "bytes": path.stat().st_size,
            }

    review_set = {
        "format": "sao-reference-review-set/0.1",
        "case_id": case["id"],
        "status": "review-ready-synthetic",
        "summary": summary,
        "assertions": {
            "architecture_fitness_strict_green": fitness["passed"] is True,
            "architecture_decisions_complete": decisions["passed"] is True,
            "requirement_control_traceability_complete": traceability["passed"] is True,
            "incident_and_control_plane_contracts_green": base_packet["summary"]["all_contracts_passed"] is True,
            "mapped_benchmark_cases_green": benchmark_layers["mapped"]["failed"] == 0,
            "dynamic_adversarial_variants_green": benchmark_layers["dynamic"]["failed"] == 0,
            "ams_runbook_current": runbook["passed"] is True,
        },
        "reference_inputs": copied,
        "artifacts": manifest,
        "validation_boundary": {
            "external_practitioner_validation": False,
            "production_sap_connectivity": False,
            "production_write_authorization": False,
            "business_roi_validated": False,
        },
    }
    if not all(review_set["assertions"].values()):
        raise AssertionError("one or more reference review assertions failed")
    _write_json(output / "reference-review-set.json", review_set)
    print(json.dumps({
        "case": case["id"],
        "status": review_set["status"],
        "assertions": review_set["assertions"],
        "output": str(output),
    }, indent=2))
    return review_set


def main() -> int:
    parser = argparse.ArgumentParser(description="Build the complete synthetic Customer Governance → O2C SAO review set.")
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    build_review_set(args.case, args.output, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
