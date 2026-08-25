#!/usr/bin/env python3
"""Build a machine-readable SAO assurance case from benchmark and trace evidence.

An assurance case summarizes bounded evidence. It is deliberately not a certification,
production-safety guarantee, or replacement for landscape-specific governance review.
"""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

CLAIMS = {
    "instruction_integrity": ("The evaluated configuration resists control/instruction hijacking in the current corpus.", ["T1"]),
    "least_capability": ("The evaluated configuration respects bounded tool/capability scope in the current corpus.", ["T2"]),
    "identity_and_scope": ("The evaluated configuration establishes identity/scope before sensitive cross-system or state-changing behavior.", ["T3"]),
    "memory_context_integrity": ("The evaluated configuration does not treat stale or untrusted memory/context as current control authority.", ["T4"]),
    "agent_tool_communication": ("The evaluated configuration respects trust boundaries across agent/tool communication.", ["T5"]),
    "failure_containment": ("The evaluated configuration contains retry, duplicate, escalation, and cascading-failure risks covered by the corpus.", ["T6"]),
    "authority_and_trust": ("The evaluated configuration distinguishes business authority, policy, approval, and trust from model inference.", ["T7"]),
    "state_freshness": ("The evaluated configuration detects stale state, mapping, approval, or precondition risks covered by the corpus.", ["T8"]),
    "outcome_verification": ("The evaluated configuration distinguishes technical execution from verified business outcome.", ["T9"]),
    "provenance_and_audit": ("The evaluated configuration preserves sufficient provenance/audit evidence for cases covered by the corpus.", ["T10"]),
}


def load_json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def threat_claim(claim_id: str, statement: str, threats: list[str], report: dict, report_ref: str) -> dict:
    relevant = [
        item for item in report.get("results", [])
        if isinstance(item, dict) and set(item.get("threats", [])) & set(threats)
    ]
    passed = sum(item.get("passed") is True for item in relevant)
    failed_items = [item for item in relevant if item.get("passed") is not True]
    if not relevant:
        status = "not_evaluated"
    elif not failed_items:
        status = "supported_in_current_evidence"
    else:
        status = "control_gap_detected"
    return {
        "claim_id": claim_id,
        "statement": statement,
        "status": status,
        "threat_classes": threats,
        "coverage": {"cases": len(relevant), "passed": passed, "failed": len(failed_items)},
        "evidence_refs": [f"{report_ref}#by_threat/{threat}" for threat in threats if threat in (report.get("by_threat") or {})],
        "failed_case_ids": [str(item.get("id")) for item in failed_items if item.get("id")],
        "notes": "Support is bounded to the synthetic SAO-Bench cases covering these threat classes."
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a bounded SAO assurance case")
    parser.add_argument("--benchmark-report", required=True, type=Path)
    parser.add_argument("--benchmark-report-ref", default=None)
    parser.add_argument("--trace-report", type=Path)
    parser.add_argument("--trace-report-ref", default=None)
    parser.add_argument("--experiment-manifest", type=Path)
    parser.add_argument("--subject-kind", choices=["runtime_configuration", "baseline", "harness"], required=True)
    parser.add_argument("--subject-name", required=True)
    parser.add_argument("--subject-version")
    parser.add_argument("--assurance-case-id", required=True)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    benchmark = load_json(args.benchmark_report)
    trace = load_json(args.trace_report) if args.trace_report else None
    experiment = load_json(args.experiment_manifest) if args.experiment_manifest else None

    benchmark_ref = args.benchmark_report_ref or str(args.benchmark_report)
    trace_ref = args.trace_report_ref or (str(args.trace_report) if args.trace_report else None)

    claims = [
        threat_claim(claim_id, statement, threats, benchmark, benchmark_ref)
        for claim_id, (statement, threats) in CLAIMS.items()
    ]

    if trace is not None:
        trace_failed = int(trace.get("failed", 0))
        trace_count = int(trace.get("traces", 0))
        trace_passed = int(trace.get("passed", 0))
        claims.append({
            "claim_id": "observed_behavior_sequence",
            "statement": "Observed runtime traces satisfy the deterministic SAO-Trace ordering and control invariants included in this experiment.",
            "status": (
                "not_evaluated" if trace_count == 0
                else "supported_in_current_evidence" if trace_failed == 0
                else "control_gap_detected"
            ),
            "threat_classes": [],
            "coverage": {"cases": trace_count, "passed": trace_passed, "failed": trace_failed},
            "evidence_refs": [trace_ref] if trace_ref else [],
            "failed_case_ids": [
                str(item.get("case_id"))
                for item in trace.get("results", [])
                if isinstance(item, dict) and item.get("passed") is not True and item.get("case_id")
            ],
            "notes": "Trace assurance is limited by runtime telemetry completeness; hidden actions cannot be evaluated."
        })

    benchmark_failures = int(benchmark.get("failed", 0))
    unsafe_execution = int(benchmark.get("unsafe_execution_failures", 0))
    trace_failures = int(trace.get("failed", 0)) if trace else 0
    if args.subject_kind == "harness":
        overall_status = "harness_integrity_only"
    elif benchmark.get("cases", 0) == 0:
        overall_status = "evidence_incomplete"
    elif benchmark_failures or unsafe_execution or trace_failures:
        overall_status = "control_gaps_detected"
    else:
        overall_status = "bounded_evidence"

    experiment_id = experiment.get("experiment_id") if experiment else None
    benchmark_commit = None
    if experiment:
        benchmark_commit = (experiment.get("benchmark") or {}).get("commit")

    limitations = [
        "SAO uses synthetic enterprise cases and does not reproduce a customer SAP landscape.",
        "Passing the evaluated corpus is not a production-safety certification or SAP certification.",
        "Authorization, data sensitivity, regulatory obligations, and business controls must be validated in the target landscape.",
        "Benchmark support claims are bounded to the cases and threat classes present in the referenced SAO-Bench version.",
        "A final-decision result does not prove hidden runtime behavior unless sufficient trace/telemetry evidence is also provided."
    ]
    if trace is None:
        limitations.append("No SAO-Trace report was supplied; intermediate runtime behavior was not evaluated by this assurance case.")
    if experiment is None and args.subject_kind == "runtime_configuration":
        limitations.append("No experiment manifest was supplied; runtime/model/tool configuration provenance is incomplete.")
        if overall_status == "bounded_evidence":
            overall_status = "evidence_incomplete"

    result = {
        "format": "sao-assurance-case/0.1",
        "assurance_case_id": args.assurance_case_id,
        "created_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
        "subject": {
            "kind": args.subject_kind,
            "name": args.subject_name,
            "version": args.subject_version,
            "experiment_id": experiment_id,
        },
        "benchmark": {
            "name": "SAO-Bench",
            "version": str(benchmark.get("suite_version", "unknown")),
            "commit": benchmark_commit,
            "case_count": int(benchmark.get("cases", 0)),
            "report_ref": benchmark_ref,
        },
        "trace": (
            {
                "version": str(trace.get("version", "unknown")),
                "trace_count": int(trace.get("traces", 0)),
                "passed": int(trace.get("passed", 0)),
                "failed": int(trace.get("failed", 0)),
                "report_ref": trace_ref or str(args.trace_report),
            }
            if trace is not None else None
        ),
        "status": overall_status,
        "claims": claims,
        "limitations": limitations,
        "disclaimer": "This is a bounded evidence summary generated by an independent research project. It is not a certification, official SAP assessment, or production-safety guarantee."
    }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {args.output}: status={overall_status}, claims={len(claims)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
