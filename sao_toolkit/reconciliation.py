from __future__ import annotations

import csv
import json
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from .evidence import EvidencePackError

FORMAT = "sao-reconciliation-pack"
VERSION = "0.1"


def _time(value: str | None) -> datetime | None:
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value.strip().replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _read_csv(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        raise EvidencePackError(f"missing reconciliation file: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if not reader.fieldnames:
            raise EvidencePackError(f"{path}: missing CSV header")
        return [
            {key: (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader
        ]


def load_reconciliation_pack(root: str | Path) -> tuple[Path, dict[str, Any]]:
    base = Path(root).resolve()
    path = base / "reconcile.json"
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidencePackError(f"missing reconciliation manifest: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EvidencePackError(f"invalid reconciliation manifest: {exc}") from exc
    if manifest.get("format") != FORMAT or str(manifest.get("version")) != VERSION:
        raise EvidencePackError(f"reconcile.json must use {FORMAT}/{VERSION}")
    for field in ("reconciliation_id", "source", "target", "identity_map", "attributes"):
        if field not in manifest:
            raise EvidencePackError(f"reconcile.json missing required field: {field}")
    if not isinstance(manifest["attributes"], list) or not manifest["attributes"]:
        raise EvidencePackError("reconcile.json attributes must be a non-empty list")
    return base, manifest


def analyze_reconciliation(root: str | Path) -> dict[str, Any]:
    base, manifest = load_reconciliation_pack(root)
    source_cfg = manifest["source"]
    target_cfg = manifest["target"]
    map_cfg = manifest["identity_map"]
    source_rows = _read_csv(base / source_cfg["file"])
    target_rows = _read_csv(base / target_cfg["file"])
    map_rows = _read_csv(base / map_cfg["file"])

    source_id_col = source_cfg.get("id_column", "source_id")
    target_id_col = target_cfg.get("id_column", "target_id")
    source_time_col = source_cfg.get("observed_at_column", "observed_at")
    target_time_col = target_cfg.get("observed_at_column", "observed_at")

    target_by_id = {row.get(target_id_col, ""): row for row in target_rows if row.get(target_id_col)}
    mappings: dict[str, list[dict[str, str]]] = {}
    for row in map_rows:
        mappings.setdefault(row.get("source_id", ""), []).append(row)

    results: list[dict[str, Any]] = []
    for source in source_rows:
        source_id = source.get(source_id_col, "")
        identity_candidates = mappings.get(source_id, [])
        resolved = [row for row in identity_candidates if row.get("status", "").lower() == "resolved" and row.get("target_id")]
        if len(resolved) != 1:
            results.append(
                {
                    "source_id": source_id,
                    "target_id": None,
                    "attribute": None,
                    "source_value": None,
                    "target_value": None,
                    "classification": "identity_unresolved" if not resolved else "identity_ambiguous",
                    "safe_next_action": "resolve_identity",
                    "unsafe_action": "compare_or_merge_by_similarity",
                }
            )
            continue
        target_id = resolved[0]["target_id"]
        target = target_by_id.get(target_id)
        if target is None:
            results.append(
                {
                    "source_id": source_id,
                    "target_id": target_id,
                    "attribute": None,
                    "source_value": None,
                    "target_value": None,
                    "classification": "target_record_missing",
                    "safe_next_action": "determine_expected_target_scope_and_creation_state",
                    "unsafe_action": "create_target_without_scope_or_authority_check",
                }
            )
            continue

        source_time = _time(source.get(source_time_col))
        target_time = _time(target.get(target_time_col))
        for attr in manifest["attributes"]:
            name = str(attr.get("name", ""))
            authority = str(attr.get("authority", "unknown")).lower()
            source_value = source.get(name, "")
            target_value = target.get(name, "")
            common = {
                "source_id": source_id,
                "target_id": target_id,
                "attribute": name,
                "source_value": source_value,
                "target_value": target_value,
                "authority": authority,
                "source_observed_at": source.get(source_time_col),
                "target_observed_at": target.get(target_time_col),
                "mapping_version": resolved[0].get("mapping_version"),
            }
            if authority not in {"source", "target"}:
                results.append(
                    common
                    | {
                        "classification": "attribute_authority_unresolved",
                        "safe_next_action": "resolve_attribute_authority",
                        "unsafe_action": "copy_value_between_systems",
                    }
                )
                continue
            if source_value == target_value:
                results.append(
                    common
                    | {
                        "classification": "aligned",
                        "safe_next_action": "none",
                        "unsafe_action": "none",
                    }
                )
                continue
            if source_time is None or target_time is None:
                results.append(
                    common
                    | {
                        "classification": "mismatch_freshness_unknown",
                        "safe_next_action": "collect_snapshot_timestamps",
                        "unsafe_action": "overwrite_without_freshness_evidence",
                    }
                )
                continue

            authority_time = source_time if authority == "source" else target_time
            other_time = target_time if authority == "source" else source_time
            if other_time > authority_time:
                results.append(
                    common
                    | {
                        "classification": "non_authoritative_snapshot_is_newer",
                        "safe_next_action": "refresh_authoritative_evidence_and_reconcile_change_origin",
                        "unsafe_action": "overwrite_newer_state_from_stale_snapshot",
                    }
                )
            else:
                results.append(
                    common
                    | {
                        "classification": "authoritative_mismatch",
                        "safe_next_action": "investigate_replication_or_target_processing",
                        "unsafe_action": "blind_manual_overwrite",
                    }
                )

    counts = Counter(row["classification"] for row in results)
    return {
        "format": "sao-reconciliation-report/0.1",
        "reconciliation_id": manifest["reconciliation_id"],
        "source_system": source_cfg.get("system"),
        "target_system": target_cfg.get("system"),
        "source_records": len(source_rows),
        "target_records": len(target_rows),
        "checks": len(results),
        "aligned": counts.get("aligned", 0),
        "needs_attention": len(results) - counts.get("aligned", 0),
        "by_classification": dict(sorted(counts.items())),
        "results": results,
    }


def write_reconciliation_outputs(report: dict[str, Any], output_dir: str | Path) -> dict[str, Path]:
    root = Path(output_dir)
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / "reconciliation-report.json"
    csv_path = root / "reconciliation-report.csv"
    md_path = root / "reconciliation-report.md"
    json_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    fieldnames = [
        "source_id",
        "target_id",
        "attribute",
        "source_value",
        "target_value",
        "authority",
        "classification",
        "safe_next_action",
        "unsafe_action",
        "source_observed_at",
        "target_observed_at",
        "mapping_version",
    ]
    with csv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(report["results"])

    lines = [
        f"# SAO Reconciliation — {report['reconciliation_id']}",
        "",
        f"**{report.get('source_system')} → {report.get('target_system')}**",
        "",
        f"- Checks: **{report['checks']}**",
        f"- Aligned: **{report['aligned']}**",
        f"- Need attention: **{report['needs_attention']}**",
        "",
        "## Classification summary",
        "",
        "| Classification | Count |",
        "|---|---:|",
    ]
    for name, count in report["by_classification"].items():
        lines.append(f"| `{name}` | {count} |")
    lines += [
        "",
        "## Attention items",
        "",
        "| Source | Target | Attribute | Classification | Safe next action |",
        "|---|---|---|---|---|",
    ]
    for row in report["results"]:
        if row["classification"] == "aligned":
            continue
        lines.append(
            f"| `{row.get('source_id','')}` | `{row.get('target_id') or ''}` | "
            f"`{row.get('attribute') or ''}` | `{row['classification']}` | "
            f"`{row['safe_next_action']}` |"
        )
    lines += [
        "",
        "---",
        "This report classifies supplied snapshots using explicit identity, attribute authority and freshness evidence. It does not execute corrections.",
        "",
    ]
    md_path.write_text("\n".join(lines), encoding="utf-8")
    return {"json": json_path, "csv": csv_path, "markdown": md_path}


def create_reconciliation_demo(root: str | Path, *, force: bool = False) -> Path:
    base = Path(root).resolve()
    if base.exists() and any(base.iterdir()) and not force:
        raise EvidencePackError(f"output directory is not empty: {base}")
    if base.exists() and force:
        import shutil
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)
    manifest = {
        "format": FORMAT,
        "version": VERSION,
        "reconciliation_id": "demo-customer-master-reconciliation",
        "source": {"system": "MDG", "file": "source.csv", "id_column": "source_id", "observed_at_column": "observed_at"},
        "target": {"system": "S4", "file": "target.csv", "id_column": "target_id", "observed_at_column": "observed_at"},
        "identity_map": {"file": "identity_map.csv"},
        "attributes": [
            {"name": "tax_class", "authority": "source"},
            {"name": "delivery_control", "authority": "source"},
        ],
    }
    (base / "reconcile.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (base / "source.csv").write_text(
        "source_id,observed_at,tax_class,delivery_control\n"
        "C-100,2026-08-25T10:15:00Z,A,NEW\n"
        "C-200,2026-08-25T10:15:00Z,B,OPEN\n"
        "C-300,2026-08-25T10:00:00Z,C,OPEN\n",
        encoding="utf-8",
    )
    (base / "target.csv").write_text(
        "target_id,observed_at,tax_class,delivery_control\n"
        "BP-100,2026-08-25T10:10:00Z,A,OLD\n"
        "BP-200,2026-08-25T10:20:00Z,B,CLOSED\n"
        "BP-300,2026-08-25T10:00:00Z,C,OPEN\n",
        encoding="utf-8",
    )
    (base / "identity_map.csv").write_text(
        "source_id,target_id,status,mapping_version,effective_from\n"
        "C-100,BP-100,resolved,M1,2026-08-01T00:00:00Z\n"
        "C-200,BP-200,resolved,M1,2026-08-01T00:00:00Z\n"
        "C-300,BP-300,resolved,M1,2026-08-01T00:00:00Z\n",
        encoding="utf-8",
    )
    return base
