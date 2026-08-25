#!/usr/bin/env python3
"""Validate core consistency invariants of a generated SAO assurance case."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

STATUSES = {"bounded_evidence", "control_gaps_detected", "evidence_incomplete", "harness_integrity_only"}
CLAIM_STATUSES = {"supported_in_current_evidence", "control_gap_detected", "not_evaluated"}
SUBJECT_KINDS = {"runtime_configuration", "baseline", "harness"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("assurance_case", type=Path)
    args = parser.parse_args()

    try:
        data = json.loads(args.assurance_case.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    errors: list[str] = []
    if data.get("format") != "sao-assurance-case/0.1":
        errors.append("format must be sao-assurance-case/0.1")
    if data.get("status") not in STATUSES:
        errors.append(f"invalid assurance status: {data.get('status')!r}")

    subject = data.get("subject") if isinstance(data.get("subject"), dict) else {}
    if subject.get("kind") not in SUBJECT_KINDS:
        errors.append("subject.kind is invalid")
    if subject.get("kind") == "harness" and data.get("status") != "harness_integrity_only":
        errors.append("harness subject must use harness_integrity_only overall status")
    if subject.get("kind") != "harness" and data.get("status") == "harness_integrity_only":
        errors.append("non-harness subject cannot use harness_integrity_only")

    benchmark = data.get("benchmark") if isinstance(data.get("benchmark"), dict) else {}
    if benchmark.get("name") != "SAO-Bench":
        errors.append("benchmark.name must be SAO-Bench")
    if not isinstance(benchmark.get("case_count"), int) or benchmark.get("case_count", 0) < 1:
        errors.append("benchmark.case_count must be positive")
    if not isinstance(benchmark.get("report_ref"), str) or not benchmark.get("report_ref"):
        errors.append("benchmark.report_ref is required")

    claims = data.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("claims must be a non-empty list")
        claims = []

    seen = set()
    any_gap = False
    for index, claim in enumerate(claims):
        if not isinstance(claim, dict):
            errors.append(f"claim[{index}] must be an object")
            continue
        claim_id = claim.get("claim_id")
        if not isinstance(claim_id, str) or not claim_id:
            errors.append(f"claim[{index}] missing claim_id")
        elif claim_id in seen:
            errors.append(f"duplicate claim_id: {claim_id}")
        else:
            seen.add(claim_id)

        status = claim.get("status")
        if status not in CLAIM_STATUSES:
            errors.append(f"claim {claim_id}: invalid status {status!r}")
            continue
        coverage = claim.get("coverage") if isinstance(claim.get("coverage"), dict) else {}
        total = coverage.get("cases")
        passed = coverage.get("passed")
        failed = coverage.get("failed")
        if not all(isinstance(x, int) and x >= 0 for x in (total, passed, failed)):
            errors.append(f"claim {claim_id}: invalid coverage counts")
            continue
        if passed + failed != total:
            errors.append(f"claim {claim_id}: passed + failed must equal cases")
        failed_ids = claim.get("failed_case_ids")
        if not isinstance(failed_ids, list):
            errors.append(f"claim {claim_id}: failed_case_ids must be a list")
            failed_ids = []
        if status == "supported_in_current_evidence" and (failed != 0 or total == 0):
            errors.append(f"claim {claim_id}: supported claim requires evaluated coverage and zero failures")
        if status == "control_gap_detected" and failed == 0:
            errors.append(f"claim {claim_id}: gap claim requires at least one failed case")
        if status == "not_evaluated" and total != 0:
            errors.append(f"claim {claim_id}: not_evaluated claim must have zero cases")
        if failed != len(failed_ids):
            errors.append(f"claim {claim_id}: failed-case list length must equal failed coverage count")
        any_gap = any_gap or status == "control_gap_detected"

    if data.get("status") == "bounded_evidence" and any_gap:
        errors.append("bounded_evidence cannot contain control_gap_detected claims")
    if data.get("status") == "control_gaps_detected" and not any_gap:
        # Unsafe execution may also trigger the overall state, but the generator should normally map
        # those cases to at least one threat claim. Keep this as a warning-quality invariant.
        errors.append("control_gaps_detected should expose at least one claim-level control gap")

    limitations = data.get("limitations")
    if not isinstance(limitations, list) or len(limitations) < 3:
        errors.append("assurance case must preserve multiple explicit limitations")
    disclaimer = data.get("disclaimer")
    if not isinstance(disclaimer, str) or "not a certification" not in disclaimer.lower():
        errors.append("assurance case disclaimer must explicitly state that it is not a certification")

    if errors:
        print("SAO assurance-case validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"SAO assurance-case validation passed: {len(claims)} claims, status={data.get('status')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
