from __future__ import annotations

import csv
import json
from collections import Counter
from pathlib import Path
from typing import Any

from .evidence import EvidencePack, EvidencePackError
from .incident import analyze_incident

REQUIRED = [
    "incident_id",
    "object_type",
    "source_id",
    "target_id",
    "attribute",
    "authority_system",
    "current_change_id",
    "source_value",
    "source_changed_at",
    "message_id",
    "message_change_id",
    "message_status",
    "message_created_at",
    "message_target_id",
    "business_status",
    "event_mapping_version",
    "identity_status",
    "current_mapping_version",
    "target_value",
    "target_observed_at",
]


def _pack_from_row(row: dict[str, str], row_index: int) -> EvidencePack:
    incident_id = row.get("incident_id") or f"row-{row_index}"
    source_id = row.get("source_id", "")
    target_id = row.get("target_id", "")
    attribute = row.get("attribute", "")
    manifest = {
        "format": "sao-evidence-pack",
        "version": "0.1",
        "incident_id": incident_id,
        "kind": "quick-check",
        "object": {
            "type": row.get("object_type") or "business-object",
            "source_id": source_id,
            "target_id": target_id,
        },
        "authority": {
            "system": row.get("authority_system") or "UNKNOWN",
            "attribute": attribute,
        },
        "resolution_condition": "Target business state matches the current authoritative change and is observed after the causally related message.",
        "recovery": {"regeneration_supported": True},
    }
    source_changes = []
    if row.get("current_change_id") or row.get("source_value") or row.get("source_changed_at"):
        source_changes.append(
            {
                "change_id": row.get("current_change_id", ""),
                "object_id": source_id,
                "attribute": attribute,
                "value": row.get("source_value", ""),
                "changed_at": row.get("source_changed_at", ""),
            }
        )
    messages = []
    if row.get("message_id"):
        messages.append(
            {
                "message_id": row.get("message_id", ""),
                "change_id": row.get("message_change_id", ""),
                "object_id": source_id,
                "status": row.get("message_status", ""),
                "created_at": row.get("message_created_at", ""),
                "target_id": row.get("message_target_id") or target_id,
                "business_status": row.get("business_status", ""),
                "mapping_version": row.get("event_mapping_version", ""),
            }
        )
    target_state = []
    if target_id and (row.get("target_value") or row.get("target_observed_at")):
        target_state.append(
            {
                "object_id": target_id,
                "attribute": attribute,
                "value": row.get("target_value", ""),
                "observed_at": row.get("target_observed_at", ""),
            }
        )
    identity_map = [
        {
            "source_id": source_id,
            "target_id": target_id if row.get("identity_status", "").lower() == "resolved" else "",
            "status": row.get("identity_status", "") or "unresolved",
            "mapping_version": row.get("current_mapping_version", ""),
            "effective_from": "1970-01-01T00:00:00Z",
        }
    ]
    return EvidencePack(
        root=Path("."),
        manifest=manifest,
        tables={
            "source_changes": source_changes,
            "messages": messages,
            "target_state": target_state,
            "identity_map": identity_map,
        },
    )


def analyze_quickcheck(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    if not source.exists():
        raise EvidencePackError(f"quick-check CSV not found: {source}")
    with source.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        missing = [name for name in REQUIRED if name not in headers]
        if missing:
            raise EvidencePackError(
                "quick-check CSV missing required columns: " + ", ".join(missing)
            )
        rows = [
            {key: (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader
        ]

    results = []
    for index, row in enumerate(rows, 1):
        report = analyze_incident(_pack_from_row(row, index))
        results.append(
            {
                "incident_id": report.get("incident_id"),
                "source_id": (report.get("object") or {}).get("source_id"),
                "target_id": (report.get("identity") or {}).get("target_id")
                or (report.get("object") or {}).get("target_id"),
                "status": report.get("status"),
                "classification": report.get("classification"),
                "first_safe_next_action": (report.get("safe_next_actions") or [""])[0],
                "missing_evidence": report.get("missing_evidence", []),
                "unsafe_actions": report.get("unsafe_actions", []),
                "findings": report.get("findings", []),
            }
        )
    counts = Counter(row["classification"] for row in results)
    return {
        "format": "sao-quickcheck-report/0.1",
        "input": str(source.resolve()),
        "rows": len(results),
        "resolved": sum(row["status"] == "resolved_read_only" for row in results),
        "needs_attention": sum(row["status"] != "resolved_read_only" for row in results),
        "by_classification": dict(sorted(counts.items())),
        "results": results,
    }


def write_quickcheck_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "quickcheck-report.json"
    csv_path = root / "quickcheck-report.csv"
    md_path = root / "quickcheck-report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        fields = ["incident_id", "source_id", "target_id", "status", "classification", "first_safe_next_action"]
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["results"])
    lines = [
        "# SAO Quick Check",
        "",
        f"- Rows: **{report['rows']}**",
        f"- Resolved: **{report['resolved']}**",
        f"- Need attention: **{report['needs_attention']}**",
        "",
        "| Incident | Source | Target | Status | Classification | Next action |",
        "|---|---|---|---|---|---|",
    ]
    for row in report["results"]:
        lines.append(
            f"| {row['incident_id']} | `{row.get('source_id') or ''}` | `{row.get('target_id') or ''}` | "
            f"`{row['status']}` | `{row['classification']}` | `{row['first_safe_next_action']}` |"
        )
    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "markdown": md_path}


def create_quickcheck_demo(path: str | Path, *, force: bool = False) -> Path:
    target = Path(path).resolve()
    if target.exists() and not force:
        raise EvidencePackError(f"output file already exists: {target}; use --force to replace")
    target.parent.mkdir(parents=True, exist_ok=True)
    rows = [
        ["INC-1","customer","C-100","BP-501","delivery_control","MDG","CHG-200","NEW","2026-08-25T10:15:00Z","MSG-100","CHG-100","success","2026-08-25T09:45:00Z","BP-501","accepted","M1","resolved","M1","OLD","2026-08-25T10:20:00Z"],
        ["INC-2","customer","C-200","BP-502","delivery_control","MDG","CHG-201","NEW","2026-08-25T10:15:00Z","MSG-201","CHG-201","success","2026-08-25T10:16:00Z","BP-502","rejected","M1","resolved","M1","OLD","2026-08-25T10:20:00Z"],
        ["INC-3","customer","C-300","BP-503","delivery_control","MDG","CHG-202","NEW","2026-08-25T10:15:00Z","MSG-202","CHG-202","success","2026-08-25T10:16:00Z","BP-503","accepted","M1","resolved","M1","NEW","2026-08-25T10:20:00Z"],
    ]
    with target.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(REQUIRED)
        writer.writerows(rows)
    return target
