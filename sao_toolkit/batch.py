from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .evidence import EvidencePackError, load_pack
from .incident import analyze_incident


def discover_packs(root: str | Path) -> list[Path]:
    base = Path(root).resolve()
    if (base / "incident.json").exists():
        return [base]
    return sorted(
        path.parent
        for path in base.rglob("incident.json")
        if "sao-output" not in path.parts
    )


def analyze_batch(root: str | Path) -> dict[str, Any]:
    packs = discover_packs(root)
    results: list[dict[str, Any]] = []
    for pack_path in packs:
        try:
            report = analyze_incident(load_pack(pack_path))
            obj = report.get("object", {})
            results.append(
                {
                    "path": str(pack_path),
                    "incident_id": report.get("incident_id"),
                    "kind": report.get("kind"),
                    "object_type": obj.get("type"),
                    "source_id": obj.get("source_id"),
                    "target_id": (report.get("identity") or {}).get("target_id")
                    or obj.get("target_id"),
                    "status": report.get("status"),
                    "classification": report.get("classification"),
                    "safe_next_actions": report.get("safe_next_actions", []),
                    "unsafe_actions": report.get("unsafe_actions", []),
                    "missing_evidence": report.get("missing_evidence", []),
                    "error": None,
                }
            )
        except (EvidencePackError, OSError, ValueError) as exc:
            results.append(
                {
                    "path": str(pack_path),
                    "incident_id": pack_path.name,
                    "status": "invalid_pack",
                    "classification": "invalid_evidence_pack",
                    "safe_next_actions": ["repair_evidence_pack"],
                    "unsafe_actions": [],
                    "missing_evidence": [],
                    "error": str(exc),
                }
            )

    by_status = Counter(str(row.get("status")) for row in results)
    by_classification = Counter(str(row.get("classification")) for row in results)
    unresolved = [
        row
        for row in results
        if row.get("status") not in {"resolved_read_only"}
    ]
    return {
        "format": "sao-batch-report/0.1",
        "root": str(Path(root).resolve()),
        "incidents": len(results),
        "resolved": sum(row.get("status") == "resolved_read_only" for row in results),
        "needs_attention": len(unresolved),
        "by_status": dict(sorted(by_status.items())),
        "by_classification": dict(sorted(by_classification.items())),
        "results": results,
    }


def _markdown(report: dict[str, Any]) -> str:
    lines = [
        "# SAO Batch Triage",
        "",
        f"- Incidents: **{report['incidents']}**",
        f"- Resolved from supplied evidence: **{report['resolved']}**",
        f"- Need attention: **{report['needs_attention']}**",
        "",
        "## Failure classes",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for name, count in report["by_classification"].items():
        lines.append(f"| `{name}` | {count} |")
    lines += [
        "",
        "## Incidents",
        "",
        "| Incident | Object | Status | Classification | First safe next action |",
        "|---|---|---|---|---|",
    ]
    for row in report["results"]:
        action = (row.get("safe_next_actions") or [""])[0]
        obj = row.get("source_id") or ""
        lines.append(
            f"| {row.get('incident_id','')} | `{obj}` | `{row.get('status','')}` | "
            f"`{row.get('classification','')}` | `{action}` |"
        )
    lines += [
        "",
        "---",
        "Batch triage summarizes deterministic per-incident Evidence Pack analysis. It does not execute recovery actions.",
        "",
    ]
    return "\n".join(lines)


def write_batch_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "batch-report.json"
    md_path = root / "batch-report.md"
    csv_path = root / "batch-report.csv"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    md_path.write_text(_markdown(report), encoding="utf-8")
    fields = [
        "incident_id",
        "kind",
        "object_type",
        "source_id",
        "target_id",
        "status",
        "classification",
        "first_safe_next_action",
        "missing_evidence_count",
        "path",
        "error",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in report["results"]:
            writer.writerow(
                {
                    "incident_id": row.get("incident_id"),
                    "kind": row.get("kind"),
                    "object_type": row.get("object_type"),
                    "source_id": row.get("source_id"),
                    "target_id": row.get("target_id"),
                    "status": row.get("status"),
                    "classification": row.get("classification"),
                    "first_safe_next_action": (row.get("safe_next_actions") or [""])[0],
                    "missing_evidence_count": len(row.get("missing_evidence") or []),
                    "path": row.get("path"),
                    "error": row.get("error"),
                }
            )
    return {"json": json_path, "markdown": md_path, "csv": csv_path}
