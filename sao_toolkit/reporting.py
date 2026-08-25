from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def render_incident_markdown(report: dict[str, Any]) -> str:
    obj = report.get("object", {})
    authority = report.get("authority", {})
    lines = [
        f"# SAO Incident Report — {report.get('incident_id', 'unknown')}",
        "",
        f"**Status:** `{report.get('status')}`  ",
        f"**Classification:** `{report.get('classification')}`  ",
        f"**Object:** {obj.get('type', 'unknown')} `{obj.get('source_id', '?')}`  ",
        f"**Authority:** {authority.get('system', 'unknown')}",
        "",
        "## Findings",
        "",
    ]
    findings = report.get("findings") or []
    lines.extend([f"- {item}" for item in findings] or ["- No bounded finding was produced."])

    change = report.get("authoritative_change")
    if isinstance(change, dict):
        lines += [
            "",
            "## Current authoritative change",
            "",
            f"- Change ID: `{change.get('change_id')}`",
            f"- Attribute: `{change.get('attribute')}`",
            f"- Value: `{change.get('value')}`",
            f"- Changed at: `{change.get('changed_at')}`",
        ]

    identity = report.get("identity")
    if isinstance(identity, dict):
        lines += [
            "",
            "## Identity",
            "",
            f"- Status: `{identity.get('status')}`",
            f"- Source: `{identity.get('source_id')}`",
            f"- Target: `{identity.get('target_id')}`",
            f"- Mapping version: `{identity.get('mapping_version')}`",
        ]

    message = report.get("current_message")
    if isinstance(message, dict):
        lines += [
            "",
            "## Current message",
            "",
            f"- Message: `{message.get('message_id')}`",
            f"- Technical status: `{message.get('status')}`",
            f"- Business status: `{message.get('business_status')}`",
            f"- Mapping version: `{message.get('mapping_version')}`",
            f"- Causality: `{message.get('causality')}`",
        ]

    target = report.get("target_state")
    if isinstance(target, dict):
        lines += [
            "",
            "## Observed target state",
            "",
            f"- Target: `{target.get('target_id')}`",
            f"- Attribute: `{target.get('attribute')}`",
            f"- Value: `{target.get('value')}`",
            f"- Observed at: `{target.get('observed_at')}`",
        ]

    lines += ["", "## Missing evidence", ""]
    lines.extend([f"- {item}" for item in report.get("missing_evidence", [])] or ["- None identified."])

    lines += ["", "## Safe next actions", ""]
    lines.extend([f"- `{item}`" for item in report.get("safe_next_actions", [])] or ["- No action recommended."])

    lines += ["", "## Actions explicitly not justified by current evidence", ""]
    lines.extend([f"- `{item}`" for item in report.get("unsafe_actions", [])] or ["- None listed."])

    lines += [
        "",
        "## Resolution condition",
        "",
        str(report.get("resolution_condition") or "Not defined."),
        "",
        "## Evidence references",
        "",
    ]
    lines.extend([f"- `{item}`" for item in report.get("evidence_refs", [])] or ["- None."])
    lines += [
        "",
        "---",
        "This report is a deterministic analysis of the supplied evidence pack. It does not execute SAP changes and does not replace landscape-specific authorization or business ownership.",
        "",
    ]
    return "\n".join(lines)


def write_incident_outputs(report: dict[str, Any], output_dir: str | Path) -> tuple[Path, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "incident-report.json"
    md_path = root / "incident-report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(render_incident_markdown(report), encoding="utf-8")
    return json_path, md_path
