from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import sys
from pathlib import Path
from typing import Any

# Repository scripts are intentionally runnable from a clean source checkout.
# Put the repository root on sys.path before importing the packaged toolkit;
# installed `sao` usage remains unaffected.
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sao_toolkit.demo import create_demo_pack
from sao_toolkit.evidence import load_pack
from sao_toolkit.incident import analyze_incident
from sao_toolkit.reporting import write_incident_outputs

DEFAULT_CASE = ROOT / "examples" / "reference-cases" / "customer-governance-o2c" / "case.json"
DEFAULT_OUTPUT = ROOT / "build" / "reference-cases" / "customer-governance-o2c"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _read_case(path: Path) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise ValueError(f"reference case not found: {path}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid reference case JSON: {exc}") from exc
    if not isinstance(data, dict) or data.get("format") != "sao-reference-case/0.1":
        raise ValueError("case.format must be 'sao-reference-case/0.1'")
    campaign = data.get("failure_campaign")
    if not isinstance(campaign, list) or not campaign:
        raise ValueError("case.failure_campaign must contain at least one scenario")
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


def _render_review(case: dict[str, Any], results: list[dict[str, Any]], packet: dict[str, Any]) -> str:
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
        "## Executed failure campaign",
        "",
        "| Scenario | Classification | Recovery class | Contract |",
        "|---|---|---|---|",
    ]
    for result in results:
        lines.append(
            f"| `{result['scenario']}` | `{result['classification']}` | "
            f"`{result['recovery_class']}` | PASS |"
        )

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
        f"- Executed scenarios: **{packet['summary']['scenarios']}**",
        f"- Passed scenario contracts: **{packet['summary']['passed']}**",
        f"- Referenced architecture/assurance artifacts checked: **{packet['summary']['repository_refs_checked']}**",
        "",
        "Every scenario output is retained with its own SHA-256 in `assurance-packet.json`.",
        "",
        "## Deliberate limitations",
        "",
        "- This is a synthetic public reference case, not evidence from a customer landscape.",
        "- It proves deterministic failure classification and recovery boundaries, not SAP API connectivity.",
        "- It does not authorize or execute a production write.",
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

    results: list[dict[str, Any]] = []
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
        results.append(result)

        for artifact_path in (input_dir / "incident.json", json_path, md_path):
            relative = str(artifact_path.relative_to(output))
            artifacts[relative] = {
                "sha256": _sha256(artifact_path),
                "bytes": artifact_path.stat().st_size,
            }

    packet = {
        "format": "sao-reference-assurance-packet/0.1",
        "case": {
            "id": case["id"],
            "title": case["title"],
            "contract": str(case_path.relative_to(ROOT)),
            "sha256": _sha256(case_path),
        },
        "summary": {
            "scenarios": len(results),
            "passed": len(results),
            "repository_refs_checked": len(checked_refs),
            "all_contracts_passed": True,
        },
        "business_requirement": case["business_requirement"],
        "invariants": case["invariants"],
        "results": results,
        "repository_refs": checked_refs,
        "artifacts": artifacts,
        "scope": "Synthetic reference evidence. No production SAP access, credentials or autonomous write authority are used or implied.",
    }

    packet_path = output / "assurance-packet.json"
    packet_path.write_text(json.dumps(packet, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    review_path = output / "architecture-operations-review.md"
    review_path.write_text(_render_review(case, results, packet), encoding="utf-8")

    packet["outputs"] = {
        "packet": str(packet_path),
        "review": str(review_path),
    }
    print(json.dumps({"case": case["id"], "scenarios": len(results), "status": "passed", "output": str(output)}, indent=2))
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
