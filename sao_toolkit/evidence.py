from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any

PACK_VERSION = "0.1"
REQUIRED_TABLES = {
    "source_changes": ["change_id", "object_id", "attribute", "value", "changed_at"],
    "messages": [
        "message_id",
        "change_id",
        "object_id",
        "status",
        "created_at",
        "target_id",
        "business_status",
        "mapping_version",
    ],
    "target_state": ["object_id", "attribute", "value", "observed_at"],
    "identity_map": [
        "source_id",
        "target_id",
        "status",
        "mapping_version",
        "effective_from",
    ],
}


class EvidencePackError(ValueError):
    pass


@dataclass(frozen=True)
class EvidencePack:
    root: Path
    manifest: dict[str, Any]
    tables: dict[str, list[dict[str, str]]]

    @property
    def incident_id(self) -> str:
        return str(self.manifest.get("incident_id", "unknown"))


def _read_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:
        raise EvidencePackError(f"missing evidence manifest: {path}") from exc
    except json.JSONDecodeError as exc:
        raise EvidencePackError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(value, dict):
        raise EvidencePackError(f"{path}: expected a JSON object")
    return value


def _read_csv(path: Path, required: list[str]) -> list[dict[str, str]]:
    if not path.exists():
        raise EvidencePackError(f"missing evidence table: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        headers = list(reader.fieldnames or [])
        missing = [name for name in required if name not in headers]
        if missing:
            raise EvidencePackError(
                f"{path}: missing required columns: {', '.join(missing)}"
            )
        return [
            {key: (value or "").strip() for key, value in row.items() if key is not None}
            for row in reader
        ]


def validate_manifest(manifest: dict[str, Any]) -> None:
    if manifest.get("format") != "sao-evidence-pack":
        raise EvidencePackError("manifest.format must be 'sao-evidence-pack'")
    if str(manifest.get("version")) != PACK_VERSION:
        raise EvidencePackError(
            f"unsupported evidence-pack version {manifest.get('version')!r}; expected {PACK_VERSION}"
        )
    for field in ("incident_id", "kind", "object", "authority", "files"):
        if field not in manifest:
            raise EvidencePackError(f"manifest missing required field: {field}")
    obj = manifest["object"]
    if not isinstance(obj, dict) or not obj.get("source_id"):
        raise EvidencePackError("manifest.object.source_id is required")
    if not obj.get("type"):
        raise EvidencePackError("manifest.object.type is required")
    authority = manifest["authority"]
    if not isinstance(authority, dict) or not authority.get("system"):
        raise EvidencePackError("manifest.authority.system is required")
    files = manifest["files"]
    if not isinstance(files, dict):
        raise EvidencePackError("manifest.files must be an object")
    for logical_name in REQUIRED_TABLES:
        if not files.get(logical_name):
            raise EvidencePackError(f"manifest.files.{logical_name} is required")


def load_pack(root: str | Path) -> EvidencePack:
    root_path = Path(root).resolve()
    manifest = _read_json(root_path / "incident.json")
    validate_manifest(manifest)
    tables: dict[str, list[dict[str, str]]] = {}
    for logical_name, required_columns in REQUIRED_TABLES.items():
        relative = str(manifest["files"][logical_name])
        tables[logical_name] = _read_csv(root_path / relative, required_columns)
    return EvidencePack(root=root_path, manifest=manifest, tables=tables)


def pack_summary(pack: EvidencePack) -> dict[str, Any]:
    return {
        "format": "sao-evidence-pack-summary/0.1",
        "incident_id": pack.incident_id,
        "kind": pack.manifest.get("kind"),
        "object_type": pack.manifest.get("object", {}).get("type"),
        "authority_system": pack.manifest.get("authority", {}).get("system"),
        "rows": {name: len(rows) for name, rows in pack.tables.items()},
    }


def create_empty_pack(
    root: str | Path,
    *,
    incident_id: str,
    kind: str = "integration-incident",
    object_type: str = "business-object",
    source_id: str = "SOURCE-ID",
    target_id: str = "TARGET-ID",
    authority_system: str = "AUTHORITATIVE-SYSTEM",
    attribute: str = "attribute",
    force: bool = False,
) -> Path:
    root_path = Path(root).resolve()
    if root_path.exists() and any(root_path.iterdir()) and not force:
        raise EvidencePackError(
            f"output directory is not empty: {root_path}; use --force to replace it"
        )
    if root_path.exists() and force:
        import shutil

        shutil.rmtree(root_path)
    root_path.mkdir(parents=True, exist_ok=True)

    files = {
        "source_changes": "source_changes.csv",
        "messages": "messages.csv",
        "target_state": "target_state.csv",
        "identity_map": "identity_map.csv",
    }
    manifest = {
        "format": "sao-evidence-pack",
        "version": PACK_VERSION,
        "incident_id": incident_id,
        "kind": kind,
        "object": {
            "type": object_type,
            "source_id": source_id,
            "target_id": target_id,
        },
        "authority": {
            "system": authority_system,
            "attribute": attribute,
        },
        "files": files,
        "resolution_condition": "Define the business state that must be observed before this incident can be called resolved.",
    }
    (root_path / "incident.json").write_text(
        json.dumps(manifest, indent=2) + "\n", encoding="utf-8"
    )
    for logical_name, columns in REQUIRED_TABLES.items():
        with (root_path / files[logical_name]).open(
            "w", encoding="utf-8", newline=""
        ) as handle:
            writer = csv.writer(handle)
            writer.writerow(columns)
    (root_path / "README.txt").write_text(
        "Fill the CSV files with exported evidence, then run:\n"
        "  sao incident validate .\n"
        "  sao incident analyze .\n",
        encoding="utf-8",
    )
    return root_path
