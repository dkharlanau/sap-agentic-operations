from __future__ import annotations

import json
from pathlib import Path

SOURCE_HEADER = "change_id,object_id,attribute,value,changed_at\n"
MESSAGE_HEADER = "message_id,change_id,object_id,status,created_at,target_id,business_status,mapping_version\n"
TARGET_HEADER = "object_id,attribute,value,observed_at\n"
IDENTITY_HEADER = "source_id,target_id,status,mapping_version,effective_from\n"

SOURCE_CHANGES = SOURCE_HEADER + (
    "CHG-100,C-100,delivery_control,OLD,2026-08-25T09:40:00Z\n"
    "CHG-200,C-100,delivery_control,NEW,2026-08-25T10:15:00Z\n"
)

SCENARIOS: dict[str, dict[str, str]] = {
    "missing-current-event": {
        "description": "An older message succeeded, but no message is linked to the current authoritative change.",
        "messages": MESSAGE_HEADER + "MSG-100,CHG-100,C-100,success,2026-08-25T09:45:00Z,BP-501,accepted,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
    },
    "business-rejection": {
        "description": "Transport succeeds but target business processing rejects the current change.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,success,2026-08-25T10:16:00Z,BP-501,rejected,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
    },
    "mapping-drift": {
        "description": "The current identity mapping changed after the event was created; historical replay needs event-time identity semantics.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,success,2026-08-25T10:16:00Z,BP-501,accepted,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\nC-100,BP-501,resolved,M2,2026-08-25T10:30:00Z\n",
    },
    "target-mismatch": {
        "description": "The current message is technically accepted, but the target business value remains stale.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,success,2026-08-25T10:16:00Z,BP-501,accepted,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
    },
    "technical-failure": {
        "description": "The causally linked message failed technically; retry is unsafe until commit/idempotency state is understood.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,failed,2026-08-25T10:16:00Z,BP-501,,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
    },
    "resolved": {
        "description": "Identity, current message and target observation form a complete evidence chain and the target matches authority.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,success,2026-08-25T10:16:00Z,BP-501,accepted,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,NEW,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
    },
    "identity-unresolved": {
        "description": "A target object must not be selected or changed while canonical identity remains unresolved.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,success,2026-08-25T10:16:00Z,BP-501,accepted,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,,unresolved,M1,2026-08-01T00:00:00Z\n",
    },
    "stale-target-observation": {
        "description": "The target snapshot predates the current event and therefore cannot prove the event's business outcome.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,success,2026-08-25T10:16:00Z,BP-501,accepted,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:10:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
    },
    "target-identity-mismatch": {
        "description": "The current event targets a different business identity than the resolved mapping.",
        "messages": MESSAGE_HEADER + "MSG-200,CHG-200,C-100,success,2026-08-25T10:16:00Z,BP-999,accepted,M1\n",
        "target": TARGET_HEADER + "BP-501,delivery_control,OLD,2026-08-25T10:20:00Z\n",
        "identity": IDENTITY_HEADER + "C-100,BP-501,resolved,M1,2026-08-01T00:00:00Z\n",
    },
}


def scenario_names() -> list[str]:
    return sorted(SCENARIOS)


def create_demo_pack(
    output: str | Path,
    *,
    scenario: str = "missing-current-event",
    force: bool = False,
) -> Path:
    if scenario not in SCENARIOS:
        raise ValueError(
            f"unknown demo scenario {scenario!r}; choose one of: {', '.join(scenario_names())}"
        )
    root = Path(output).resolve()
    if root.exists() and any(root.iterdir()) and not force:
        raise ValueError(f"demo output directory is not empty: {root}")
    if root.exists() and force:
        import shutil

        shutil.rmtree(root)
    root.mkdir(parents=True, exist_ok=True)

    manifest = {
        "format": "sao-evidence-pack",
        "version": "0.1",
        "incident_id": f"demo-{scenario}",
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
        "demo": {
            "scenario": scenario,
            "description": SCENARIOS[scenario]["description"],
        },
        "resolution_condition": "Target BP-501 contains delivery_control=NEW and the observed target state is causally traceable to the current MDG change CHG-200.",
    }
    (root / "incident.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    (root / "source_changes.csv").write_text(SOURCE_CHANGES, encoding="utf-8")
    (root / "messages.csv").write_text(SCENARIOS[scenario]["messages"], encoding="utf-8")
    (root / "target_state.csv").write_text(SCENARIOS[scenario]["target"], encoding="utf-8")
    (root / "identity_map.csv").write_text(SCENARIOS[scenario]["identity"], encoding="utf-8")
    return root
