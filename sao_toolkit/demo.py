from __future__ import annotations

import json
from pathlib import Path


DEMO_MANIFEST = {
    "format": "sao-evidence-pack",
    "version": "0.1",
    "incident_id": "demo-customer-replication-missing-event",
    "kind": "master-data-replication",
    "object": {"type": "customer", "source_id": "C-100", "target_id": "BP-501"},
    "authority": {"system": "MDG", "attribute": "delivery_control"},
    "files": {
        "source_changes": "source_changes.csv",
        "messages": "messages.csv",
        "target_state": "target_state.csv",
        "identity_map": "identity_map.csv",
    },
    "recovery": {"regeneration_supported": True},
    "resolution_condition": "Target BP-501 contains delivery_control=NEW and the observed target state is causally traceable to the current MDG change CHG-200.",
}

DEMO_FILES = {
    "source_changes.csv": "change_id,object_id,attribute,value,changed_at\nCHG-100,C-100,delivery_control,OLD,2026-08-25T09:40:00Z\nCHG-200,C-100,delivery_control,NEW,2026-08-25T10:15:00Z\n",
    "messages.csv": "message_id,change_id,object_id,status,created_at,target_id,business_status,mapping_version\nMSG-100,CHG-100,C-100,success,2026-08-25T09:45:00Z,BP-501,accepted,M1\n",
    "target_state.csv": "object_id,attribute,value,observed_at\nBP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
    "identity_map.csv": "source_id,target_id,status,mapping_version,effective_from\nC-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
}


def create_demo_pack(output: str | Path, *, force: bool = False) -> Path:
    root = Path(output).resolve()
    if root.exists() and any(root.iterdir()) and not force:
        raise ValueError(f"demo output directory is not empty: {root}")
    if root.exists() and force:
        import shutil

        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)
    (root / "incident.json").write_text(
        json.dumps(DEMO_MANIFEST, indent=2) + "\n", encoding="utf-8"
    )
    for name, content in DEMO_FILES.items():
        (root / name).write_text(content, encoding="utf-8")
    return root
