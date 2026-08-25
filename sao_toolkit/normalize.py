from __future__ import annotations

import csv
import json
from pathlib import Path
from typing import Any

from .evidence import EvidencePackError, REQUIRED_TABLES


class NormalizeError(EvidencePackError):
    pass


def _load_mapping(path: str | Path) -> dict[str, Any]:
    source = Path(path)
    try:
        value = json.loads(source.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise NormalizeError(f"mapping file not found: {source}") from exc
    except json.JSONDecodeError as exc:
        raise NormalizeError(f"invalid mapping JSON {source}: {exc}") from exc
    if not isinstance(value, dict):
        raise NormalizeError("mapping JSON must be an object")
    if not isinstance(value.get("columns", {}), dict):
        raise NormalizeError("mapping.columns must be an object")
    if not isinstance(value.get("constants", {}), dict):
        raise NormalizeError("mapping.constants must be an object")
    if not isinstance(value.get("value_maps", {}), dict):
        raise NormalizeError("mapping.value_maps must be an object")
    return value


def normalize_csv(
    *,
    table: str,
    input_path: str | Path,
    mapping_path: str | Path,
    output_path: str | Path,
    delimiter: str = ",",
) -> dict[str, Any]:
    if table not in REQUIRED_TABLES:
        raise NormalizeError(
            f"unsupported canonical table {table!r}; choose one of: {', '.join(sorted(REQUIRED_TABLES))}"
        )
    mapping = _load_mapping(mapping_path)
    columns: dict[str, str] = {str(k): str(v) for k, v in mapping.get("columns", {}).items()}
    constants: dict[str, Any] = mapping.get("constants", {})
    value_maps: dict[str, Any] = mapping.get("value_maps", {})
    required = REQUIRED_TABLES[table]

    missing_mapping = [
        field for field in required if field not in columns and field not in constants
    ]
    if missing_mapping:
        raise NormalizeError(
            "mapping does not define required canonical fields: " + ", ".join(missing_mapping)
        )

    source_path = Path(input_path)
    if not source_path.exists():
        raise NormalizeError(f"input CSV not found: {source_path}")

    with source_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle, delimiter=delimiter)
        source_headers = list(reader.fieldnames or [])
        missing_source = sorted(
            {
                source_name
                for canonical, source_name in columns.items()
                if canonical in required and source_name not in source_headers
            }
        )
        if missing_source:
            raise NormalizeError(
                "input CSV is missing mapped source columns: " + ", ".join(missing_source)
            )
        input_rows = list(reader)

    normalized: list[dict[str, str]] = []
    for source_row in input_rows:
        row: dict[str, str] = {}
        for canonical in required:
            if canonical in constants:
                raw = constants[canonical]
            else:
                raw = source_row.get(columns[canonical], "")
            text = "" if raw is None else str(raw).strip()
            field_map = value_maps.get(canonical, {})
            if isinstance(field_map, dict):
                text = str(field_map.get(text, text))
            row[canonical] = text
        normalized.append(row)

    output = Path(output_path)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=required)
        writer.writeheader()
        writer.writerows(normalized)

    return {
        "format": "sao-normalization-report/0.1",
        "table": table,
        "input": str(source_path.resolve()),
        "mapping": str(Path(mapping_path).resolve()),
        "output": str(output.resolve()),
        "rows": len(normalized),
        "canonical_columns": required,
    }


def create_we02_like_demo(root: str | Path, *, force: bool = False) -> Path:
    base = Path(root).resolve()
    if base.exists() and any(base.iterdir()) and not force:
        raise NormalizeError(f"output directory is not empty: {base}")
    if base.exists() and force:
        import shutil
        shutil.rmtree(base)
    base.mkdir(parents=True, exist_ok=True)
    (base / "we02_export.csv").write_text(
        "DOCNUM,CHANGE_REF,OBJECT_KEY,STATUS,CREATED_AT,RECEIVER,BUS_ACK\n"
        "000000001,CHG-200,C-100,53,2026-08-25T10:16:00Z,BP-501,accepted\n"
        "000000002,CHG-201,C-200,51,2026-08-25T10:17:00Z,BP-502,\n",
        encoding="utf-8",
    )
    mapping = {
        "columns": {
            "message_id": "DOCNUM",
            "change_id": "CHANGE_REF",
            "object_id": "OBJECT_KEY",
            "status": "STATUS",
            "created_at": "CREATED_AT",
            "target_id": "RECEIVER",
            "business_status": "BUS_ACK"
        },
        "constants": {"mapping_version": "M1"},
        "value_maps": {
            "status": {"53": "success", "51": "failed"}
        }
    }
    (base / "messages.mapping.json").write_text(
        json.dumps(mapping, indent=2) + "\n", encoding="utf-8"
    )
    return base
