from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

# Repository scripts are intentionally runnable from a clean source checkout.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sao_toolkit.demo import create_demo_pack
from sao_toolkit.evidence import load_pack
from sao_toolkit.incident import analyze_incident
from sao_toolkit.reporting import write_incident_outputs
from scripts.evaluate_trace import evaluate_trace, load_jsonl
from simulator.v03 import EnterpriseLab

DEFAULT_CASE = ROOT / "examples" / "reference-cases" / "customer-governance-o2c" / "case.json"
DEFAULT_OUTPUT = ROOT / "build" / "reference-cases" / "customer-governance-o2c"
SIMULATOR_FIXTURE = ROOT / "simulator" / "fixtures" / "enterprise-v03.json"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_case(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"reference case not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid reference case JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("format") != "sao-reference-case/0.2":
        raise ValueError("case.format must be 'sao-reference-case/0.2'")
    campaign = data.get("failure_campaign")
    controls = data.get("control_plane_campaign")
    if not isinstance(campaign, list) or not campaign:
        raise ValueError("case.failure_campaign must contain at least one scenario")
    if not isinstance(controls, list) or not controls:
        raise ValueError("case.control_plane_campaign must contain at least one check")
    return data


def _validate_refs(case: dict[str, Any]) -> list[str]:
    checked: list[str] = []
    for key in ("architecture_refs", "assurance_refs"):
        refs = case.get(key, [])
        if not isinstance(refs, list):
            raise ValueError(f"case.{key} must be an array")
        for raw in refs:
            ref = str(raw)
            path = ROOT / ref
            if not path.exists():
                raise ValueError(f"case.{key} points to missing repository artifact: {ref}")
            checked.append(ref)
    return checked


def _assert_expected(report: dict[str, Any], spec: dict[str, Any]) -> dict[str, Any]:
    scenario = str(spec["scenario"])
    expected = str(spec["expected_classification"])
    actual = str(report.get("classification"))
    if actual != expected:
        raise AssertionError(f"{scenario}: expected {expected}, got {actual}")

    safe = set(str(value) for value in report.get("safe_next_actions", []))
    blocked = set(str(value) for value in report.get("unsafe_actions", []))
    required_safe = set(str(value) for value in spec.get("required_safe_actions", []))
    required_blocked = set(str(value) for value in spec.get("required_blocked_actions", []))

    missing_safe = sorted(required_safe - safe)
    missing_blocked = sorted(required_blocked - blocked)
    if missing_safe:
        raise AssertionError(f"{scenario}: missing required safe actions: {', '.join(missing_safe)}")
    if missing_blocked:
        raise AssertionError(f"{scenario}: missing required blocked actions: {', '.join(missing_blocked)}")

    return {
        "scenario": scenario,
        "classification": actual,
        "status": report.get("status"),
        "recovery_class": spec.get("recovery_class"),
        "safe_actions": sorted(safe),
        "blocked_actions": sorted(blocked),
        "resolution_condition": report.get("resolution_condition"),
        "assertions": {
            "classification_matches": True,
            "required_safe_actions_present": True,
            "required_blocked_actions_present": True,
        },
    }


def _new_lab() -> EnterpriseLab:
    return EnterpriseLab(json.loads(SIMULATOR_FIXTURE.read_text(encoding="utf-8")))


def _delivery_control_envelope(
    lab: EnterpriseLab,
    *,
    key: str,
    approval_expires_tick: int | None = None,
) -> dict[str, Any]:
    before_hash = lab.object_hash("customer-100")
    expires_tick = lab.tick + 10 if approval_expires_tick is None else approval_expires_tick
    return {
        "correlation_id": f"corr-{key}",
        "identity_version": lab.identity_version,
        "object": {"canonical_id": "customer-100"},
        "operation": {
            "name": "set_delivery_control",
            "parameters": {"delivery_control": "NEW"},
        },
        "policy": {
            "policy_ref": "policy://delivery-control/r3",
            "result": "require_approval",
        },
        "approval": {
            "approval_id": f"approval-{key}",
            "canonical_id": "customer-100",
            "operation": "set_delivery_control",
            "bound_state_hash": before_hash,
            "expires_tick": expires_tick,
        },
        "precondition": {
            "state_hash": before_hash,
            "expected_state": {"attributes": {"delivery_control": "OLD"}},
        },
        "postcondition": {
            "expected_state": {"attributes": {"delivery_control": "NEW"}},
        },
        "idempotency_key": key,
    }


def _approved_recovery_trace(
    *,
    envelope: dict[str, Any],
    result: dict[str, Any],
    before_hash: str,
    after_hash: str,
) -> list[dict[str, Any]]:
    common = {
        "trace_version": "0.1",
        "run_id": "reference-customer-governance-recovery",
        "case_id": "customer-governance-o2c-approved-recovery",
    }
    return [
        {**common, "seq": 1, "event": "intent_received", "actor": "operator", "capability": None, "evidence_refs": [], "data": {"request": "set delivery control to current governed value"}},
        {**common, "seq": 2, "event": "identity_resolved", "actor": "control-plane", "capability": "read", "evidence_refs": ["synthetic://identity/customer-100"], "data": {"status": "resolved", "canonical_id": "customer-100"}},
        {**common, "seq": 3, "event": "evidence_observed", "actor": "tool", "capability": "read", "evidence_refs": ["synthetic://state/customer-100/before"], "data": {"evidence_id": "customer-before", "trust": "business_data", "state_hash": before_hash}},
        {**common, "seq": 4, "event": "policy_evaluated", "actor": "policy", "capability": "approve", "evidence_refs": ["synthetic://policy/delivery-control/r3"], "data": {"result": "require_approval", "operation": "set_delivery_control"}},
        {**common, "seq": 5, "event": "recommendation_issued", "actor": "agent", "capability": "recommend", "evidence_refs": ["synthetic://state/customer-100/before"], "data": {"operation": "set_delivery_control", "value": "NEW"}},
        {**common, "seq": 6, "event": "approval_observed", "actor": "human-approver", "capability": "approve", "evidence_refs": [f"synthetic://approval/{envelope['approval']['approval_id']}"], "data": {"valid": True, "approval_id": envelope["approval"]["approval_id"], "operation": "set_delivery_control", "bound_state_hash": before_hash}},
        {**common, "seq": 7, "event": "write_requested", "actor": "control-plane", "capability": "execute", "evidence_refs": [f"synthetic://approval/{envelope['approval']['approval_id']}", "synthetic://state/customer-100/before"], "data": {"canonical_id": "customer-100", "operation": "set_delivery_control", "precondition_hash": before_hash, "idempotency_key": envelope["idempotency_key"]}},
        {**common, "seq": 8, "event": "write_result", "actor": "system-of-record", "capability": "execute", "evidence_refs": [f"synthetic://audit/{result['audit_id']}"], "data": {"status": "success", "audit_id": result["audit_id"]}},
        {**common, "seq": 9, "event": "postcondition_checked", "actor": "control-plane", "capability": "read", "evidence_refs": ["synthetic://state/customer-100/after"], "data": {"status": "passed", "state_hash": after_hash, "expected": {"delivery_control": "NEW"}}},
        {**common, "seq": 10, "event": "decision_emitted", "actor": "agent", "capability": "recommend", "evidence_refs": [f"synthetic://audit/{result['audit_id']}", "synthetic://state/customer-100/after"], "data": {"status": "execution_result", "execution_allowed": False, "outcome": "success"}},
    ]


def _write_json_artifact(path: Path, payload: Any, output: Path, artifacts: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    relative = str(path.relative_to(output))
    artifacts[relative] = {"sha256": _sha256(path), "bytes": path.stat().st_size}


def _write_jsonl_artifact(path: Path, rows: list[dict[str, Any]], output: Path, artifacts: dict[str, dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(json.dumps(row, sort_keys=True) + "\n" for row in rows), encoding="utf-8")
    relative = str(path.relative_to(output))
    artifacts[relative] = {"sha256": _sha256(path), "bytes": path.stat().st_size}


def _run_control_plane_campaign(
    case: dict[str, Any],
    output: Path,
    artifacts: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    results: list[dict[str, Any]] = []
    control_root = output / "control-plane"

    for spec in case["control_plane_campaign"]:
        scenario = str(spec["scenario"])
        mechanism = str(spec["mechanism"])
        payload: dict[str, Any]

        if scenario == "approved-governed-recovery":
            lab = _new_lab()
            source_identity = lab.resolve_identity("synthetic-mdg", "C-100")
            target_identity = lab.resolve_identity("synthetic-s4", "BP-501")
            if source_identity.get("canonical_id") != "customer-100" or target_identity.get("canonical_id") != "customer-100":
                raise AssertionError("customer identities do not resolve to one canonical object")

            envelope = _delivery_control_envelope(lab, key="customer-delivery-control-approved")
            before_hash = lab.object_hash("customer-100")
            execution = lab.execute(envelope).as_dict()
            after = lab.read_object("customer-100")
            after_hash = lab.object_hash("customer-100")
            if execution["status"] != spec["expected_status"] or execution["outcome"] != spec["expected_outcome"]:
                raise AssertionError(f"{scenario}: governed recovery did not meet expected execution contract")
            if after["attributes"]["delivery_control"] != spec["expected_target_value"]:
                raise AssertionError(f"{scenario}: target business state mismatch")

            trace = _approved_recovery_trace(
                envelope=envelope,
                result=execution,
                before_hash=before_hash,
                after_hash=after_hash,
            )
            trace_evaluation = evaluate_trace([dict(row, _line=index + 1) for index, row in enumerate(trace)])
            if trace_evaluation["passed"] is not True:
                raise AssertionError(f"{scenario}: generated control-plane trace failed: {trace_evaluation['failures']}")
            trace_path = control_root / f"{scenario}.trace.jsonl"
            _write_jsonl_artifact(trace_path, trace, output, artifacts)
            payload = {
                "scenario": scenario,
                "mechanism": mechanism,
                "passed": True,
                "source_identity": source_identity,
                "target_identity": target_identity,
                "envelope": envelope,
                "execution": execution,
                "after_state": after,
                "trace": str(trace_path.relative_to(output)),
                "trace_evaluation": trace_evaluation,
            }

        elif scenario == "stale-recovery-approval":
            lab = _new_lab()
            envelope = _delivery_control_envelope(
                lab,
                key="customer-delivery-control-stale-approval",
                approval_expires_tick=lab.tick,
            )
            lab.advance(1)
            execution = lab.execute(envelope).as_dict()
            after = lab.read_object("customer-100")
            if execution["status"] != spec["expected_status"] or execution["reason"] != spec["expected_reason"]:
                raise AssertionError(f"{scenario}: stale approval was not rejected as expected")
            if after["attributes"]["delivery_control"] != spec["expected_target_value"]:
                raise AssertionError(f"{scenario}: rejected approval changed business state")
            payload = {
                "scenario": scenario,
                "mechanism": mechanism,
                "passed": True,
                "execution": execution,
                "after_state": after,
                "audit": lab.export_audit(),
            }

        elif scenario == "failed-business-postcondition":
            lab = _new_lab()
            envelope = _delivery_control_envelope(lab, key="customer-delivery-control-postcondition-fail")
            lab.inject_fault("postcondition_fail", target="customer-100")
            execution = lab.execute(envelope).as_dict()
            after = lab.read_object("customer-100")
            if execution["status"] != spec["expected_status"] or execution["reason"] != spec["expected_reason"]:
                raise AssertionError(f"{scenario}: failed postcondition was not surfaced")
            if after["attributes"]["delivery_control"] != spec["expected_target_value"]:
                raise AssertionError(f"{scenario}: failed postcondition retained the proposed business value")
            payload = {
                "scenario": scenario,
                "mechanism": mechanism,
                "passed": True,
                "execution": execution,
                "after_state": after,
                "audit": lab.export_audit(),
            }

        elif scenario == "duplicate-business-event":
            lab = _new_lab()
            before = lab.read_object("customer-100")
            event_id = str(spec["event_id"])
            lab.inject_fault("duplicate_message", target=event_id)
            ledger_ids = lab.emit_message(
                event_id=event_id,
                canonical_id="customer-100",
                operation="set_attribute",
                parameters={"field": "delivery_control", "value": "NEW"},
                correlation_id="corr-customer-delivery-control-duplicate",
            )
            deliveries = lab.deliver_due_messages()
            after = lab.read_object("customer-100")
            statuses = [row["status"] for row in deliveries]
            if statuses != spec["expected_delivery_statuses"]:
                raise AssertionError(f"{scenario}: expected {spec['expected_delivery_statuses']}, got {statuses}")
            if after["attributes"]["delivery_control"] != spec["expected_target_value"]:
                raise AssertionError(f"{scenario}: duplicate delivery did not preserve target value")
            if after["version"] - before["version"] != int(spec["expected_version_increment"]):
                raise AssertionError(f"{scenario}: duplicate delivery changed object version more than once")
            payload = {
                "scenario": scenario,
                "mechanism": mechanism,
                "passed": True,
                "ledger_ids": ledger_ids,
                "deliveries": deliveries,
                "before_state": before,
                "after_state": after,
                "audit": lab.export_audit(),
            }

        elif scenario == "untrusted-runbook-instruction":
            trace_path = ROOT / str(spec["trace"])
            trace_events = load_jsonl(trace_path)
            trace_evaluation = evaluate_trace(trace_events)
            expected_fragment = str(spec["expected_failure_contains"])
            if trace_evaluation["passed"] is not spec["expected_passed"]:
                raise AssertionError(f"{scenario}: trace verdict mismatch")
            if not any(expected_fragment in failure for failure in trace_evaluation["failures"]):
                raise AssertionError(f"{scenario}: expected unsafe instruction failure was not detected")
            payload = {
                "scenario": scenario,
                "mechanism": mechanism,
                "passed": True,
                "source_trace": str(trace_path.relative_to(ROOT)),
                "source_trace_sha256": _sha256(trace_path),
                "trace_evaluation": trace_evaluation,
                "interpretation": "The unsafe trace is expected to fail SAO-Trace; detecting that failure is the passing reference-case result.",
            }

        else:
            raise ValueError(f"unsupported control-plane reference scenario: {scenario}")

        _write_json_artifact(control_root / f"{scenario}.json", payload, output, artifacts)
        results.append({
            "scenario": scenario,
            "mechanism": mechanism,
            "passed": True,
            "artifact": f"control-plane/{scenario}.json",
        })

    return results


def _render_review(
    case: dict[str, Any],
    incident_results: list[dict[str, Any]],
    control_results: list[dict[str, Any]],
    packet: dict[str, Any],
) -> str:
    requirement = case["business_requirement"]
    ownership = case["ownership"]
    cutover = case["cutover_variant"]
    operations = case["operations_handover"]

    lines = [
        f"# Architecture & Operations Review — {case['title']}",
        "",
        "## Business outcome",
        "",
        str(requirement["statement"]),
        "",
        "The reference case treats target business state as the resolution boundary. A green transport status alone is not sufficient.",
        "",
        "## Authority and ownership",
        "",
    ]
    for key, value in ownership.items():
        lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")

    lines += [
        "",
        "## Executed incident campaign",
        "",
        "| Scenario | Classification | Recovery class | Contract |",
        "|---|---|---|---|",
    ]
    for result in incident_results:
        lines.append(
            f"| `{result['scenario']}` | `{result['classification']}` | "
            f"`{result['recovery_class']}` | PASS |"
        )

    lines += [
        "",
        "## Control-plane assurance campaign",
        "",
        "| Check | Mechanism | Contract |",
        "|---|---|---|",
    ]
    for result in control_results:
        lines.append(f"| `{result['scenario']}` | `{result['mechanism']}` | PASS |")

    lines += ["", "## Cutover authority-transition variant", ""]
    for key, value in cutover.items():
        lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")

    lines += ["", "## AMS / operations handover", "", "Monitor:"]
    lines.extend(f"- {item}" for item in operations["monitor"])
    lines += [
        "",
        f"**Incident lifecycle:** {' → '.join(operations['incident_states'])}",
        "",
        f"**Resolved when:** {operations['resolved_when']}",
        "",
        "## Assurance packet",
        "",
        f"- Case contract SHA-256: `{packet['case']['sha256']}`",
        f"- Total executed contracts: **{packet['summary']['scenarios']}**",
        f"- Incident scenarios: **{packet['summary']['incident_scenarios']}**",
        f"- Control-plane checks: **{packet['summary']['control_plane_checks']}**",
        f"- Passed contracts: **{packet['summary']['passed']}**",
        f"- Referenced architecture/assurance artifacts checked: **{packet['summary']['repository_refs_checked']}**",
        "",
        "Every generated scenario/control output is retained with SHA-256 in `assurance-packet.json`.",
        "",
        "## Deliberate limitations",
        "",
        "- This is a synthetic public reference case, not evidence from a customer landscape.",
        "- It proves deterministic failure classification and control boundaries, not SAP API connectivity.",
        "- The typed recovery runs only in the synthetic EnterpriseLab; it does not authorize a production write.",
        "- It does not claim that every SAP integration exposes the same evidence fields.",
        "- External practitioner validation remains a separate product maturity gate.",
        "",
    ]
    return "\n".join(lines)


def run_reference_case(case_path: Path, output: Path, *, force: bool = False) -> dict[str, Any]:
    case_path = case_path.resolve()
    output = output.resolve()
    case = _read_case(case_path)
    checked_refs = _validate_refs(case)

    if output.exists() and any(output.iterdir()):
        if not force:
            raise ValueError(f"output directory is not empty: {output}; use --force to replace it")
        shutil.rmtree(output)
    output.mkdir(parents=True, exist_ok=True)

    incident_results: list[dict[str, Any]] = []
    artifacts: dict[str, dict[str, Any]] = {}

    for raw_spec in case["failure_campaign"]:
        if not isinstance(raw_spec, dict):
            raise ValueError("every failure_campaign entry must be an object")
        scenario = str(raw_spec.get("scenario", "")).strip()
        if not scenario:
            raise ValueError("failure_campaign scenario is required")

        scenario_root = output / "scenarios" / scenario
        input_dir = scenario_root / "evidence-pack"
        report_dir = scenario_root / "analysis"
        create_demo_pack(input_dir, scenario=scenario)
        report = analyze_incident(load_pack(input_dir))
        json_path, md_path = write_incident_outputs(report, report_dir)
        result = _assert_expected(report, raw_spec)
        result["report"] = str(json_path.relative_to(output))
        incident_results.append(result)

        for artifact_path in (input_dir / "incident.json", json_path, md_path):
            relative = str(artifact_path.relative_to(output))
            artifacts[relative] = {
                "sha256": _sha256(artifact_path),
                "bytes": artifact_path.stat().st_size,
            }

    control_results = _run_control_plane_campaign(case, output, artifacts)
    total = len(incident_results) + len(control_results)

    packet = {
        "format": "sao-reference-assurance-packet/0.2",
        "case": {
            "id": case["id"],
            "title": case["title"],
            "contract": str(case_path.relative_to(ROOT)),
            "sha256": _sha256(case_path),
        },
        "summary": {
            "scenarios": total,
            "passed": total,
            "incident_scenarios": len(incident_results),
            "control_plane_checks": len(control_results),
            "repository_refs_checked": len(checked_refs),
            "all_contracts_passed": True,
        },
        "business_requirement": case["business_requirement"],
        "invariants": case["invariants"],
        "results": incident_results,
        "control_plane_results": control_results,
        "repository_refs": checked_refs,
        "artifacts": artifacts,
        "scope": "Synthetic reference evidence. No production SAP access, credentials or autonomous write authority are used or implied.",
    }

    packet_path = output / "assurance-packet.json"
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    review_path = output / "architecture-operations-review.md"
    review_path.write_text(_render_review(case, incident_results, control_results, packet), encoding="utf-8")

    packet["outputs"] = {
        "packet": str(packet_path),
        "review": str(review_path),
    }
    print(json.dumps({"case": case["id"], "contracts": total, "status": "passed", "output": str(output)}, indent=2))
    return packet


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute the synthetic Customer Governance → S/4 O2C SAO reference case.")
    parser.add_argument("--case", type=Path, default=DEFAULT_CASE)
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    run_reference_case(args.case, args.output, force=args.force)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())