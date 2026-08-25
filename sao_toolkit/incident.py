from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .evidence import EvidencePack

SAFE_NON_EXECUTION = {
    "insufficient_evidence",
    "policy_blocked",
    "recommendation",
    "resolved_read_only",
}


def _time(value: str | None) -> datetime | None:
    if not value:
        return None
    text = value.strip()
    if not text:
        return None
    try:
        parsed = datetime.fromisoformat(text.replace("Z", "+00:00"))
    except ValueError:
        return None
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _latest(rows: list[dict[str, str]], field: str) -> dict[str, str] | None:
    candidates = [(row, _time(row.get(field))) for row in rows]
    candidates = [(row, stamp) for row, stamp in candidates if stamp is not None]
    return max(candidates, key=lambda item: item[1])[0] if candidates else None


def _evidence_ref(table: str, key: str, value: str) -> str:
    return f"evidence://{table}/{key}={value}"


def _result_base(pack: EvidencePack) -> dict[str, Any]:
    manifest = pack.manifest
    return {
        "format": "sao-incident-report/0.1",
        "incident_id": pack.incident_id,
        "kind": manifest.get("kind"),
        "object": manifest.get("object", {}),
        "authority": manifest.get("authority", {}),
        "status": "insufficient_evidence",
        "classification": "unclassified",
        "execution_allowed": False,
        "findings": [],
        "missing_evidence": [],
        "safe_next_actions": [],
        "unsafe_actions": [],
        "evidence_refs": [],
        "resolution_condition": manifest.get("resolution_condition")
        or "Authoritative business state is observed at the target and causally linked to the current change.",
    }


def _append_unique(target: list[str], *values: str) -> None:
    for value in values:
        if value and value not in target:
            target.append(value)


def analyze_incident(pack: EvidencePack) -> dict[str, Any]:
    report = _result_base(pack)
    manifest = pack.manifest
    obj = manifest["object"]
    authority = manifest["authority"]
    source_id = str(obj["source_id"])
    target_hint = str(obj.get("target_id") or "")
    attribute = str(authority.get("attribute") or manifest.get("attribute") or "")

    # 1. Resolve identity using explicit mapping evidence, never similarity.
    identity_rows = [
        row for row in pack.tables["identity_map"] if row.get("source_id") == source_id
    ]
    if not identity_rows:
        report["classification"] = "identity_unresolved"
        _append_unique(report["findings"], "No identity mapping exists for the source object.")
        _append_unique(report["missing_evidence"], "canonical source-to-target identity mapping")
        _append_unique(report["safe_next_actions"], "resolve_identity")
        _append_unique(report["unsafe_actions"], "compare_or_change_target_without_resolved_identity")
        return report

    current_identity = _latest(identity_rows, "effective_from") or identity_rows[-1]
    identity_status = current_identity.get("status", "").lower()
    target_id = current_identity.get("target_id", "")
    if identity_status != "resolved" or not target_id:
        report["classification"] = "identity_ambiguous_or_unresolved"
        _append_unique(
            report["findings"],
            f"Identity mapping status is {identity_status or 'unknown'}, so cross-system state comparison is unsafe.",
        )
        _append_unique(report["missing_evidence"], "resolved canonical identity")
        _append_unique(report["safe_next_actions"], "resolve_identity")
        _append_unique(report["unsafe_actions"], "choose_target_by_similarity", "execute")
        return report
    if target_hint and target_hint != target_id:
        report["classification"] = "identity_conflict"
        _append_unique(
            report["findings"],
            f"Manifest target {target_hint} conflicts with current identity mapping {target_id}.",
        )
        _append_unique(report["safe_next_actions"], "resolve_identity_conflict")
        _append_unique(report["unsafe_actions"], "overwrite_using_manifest_target", "execute")
        return report

    report["identity"] = {
        "status": "resolved",
        "source_id": source_id,
        "target_id": target_id,
        "mapping_version": current_identity.get("mapping_version"),
    }
    _append_unique(
        report["evidence_refs"],
        _evidence_ref("identity_map", "source_id", source_id),
    )

    # 2. Find the current authoritative change.
    source_rows = [
        row
        for row in pack.tables["source_changes"]
        if row.get("object_id") == source_id
        and (not attribute or row.get("attribute") == attribute)
    ]
    latest_change = _latest(source_rows, "changed_at")
    if latest_change is None:
        report["classification"] = "authoritative_change_missing"
        _append_unique(report["findings"], "No current authoritative source change is present in the evidence pack.")
        _append_unique(report["missing_evidence"], "authoritative source change")
        _append_unique(report["safe_next_actions"], "collect_current_source_change")
        return report

    change_id = latest_change.get("change_id", "")
    change_time = _time(latest_change.get("changed_at"))
    expected_value = latest_change.get("value", "")
    report["authoritative_change"] = {
        "change_id": change_id,
        "attribute": latest_change.get("attribute"),
        "value": expected_value,
        "changed_at": latest_change.get("changed_at"),
        "authority_system": authority.get("system"),
    }
    _append_unique(
        report["evidence_refs"],
        _evidence_ref("source_changes", "change_id", change_id or "current"),
    )

    # 3. Establish causality. Prefer explicit change_id; timestamps are only supporting evidence.
    messages = [row for row in pack.tables["messages"] if row.get("object_id") == source_id]
    explicit = [row for row in messages if change_id and row.get("change_id") == change_id]
    current_messages = explicit
    if not current_messages and change_time is not None:
        # Timestamp matching is deliberately not treated as proven causality. It only helps explain stale successes.
        after_change = [
            row for row in messages if (_time(row.get("created_at")) or datetime.min.replace(tzinfo=timezone.utc)) >= change_time
        ]
    else:
        after_change = current_messages

    if not current_messages:
        older_success = [
            row
            for row in messages
            if row.get("status", "").lower() in {"success", "processed", "completed"}
            and change_time is not None
            and _time(row.get("created_at")) is not None
            and _time(row.get("created_at")) < change_time
        ]
        report["classification"] = "current_outbound_event_not_proven"
        if older_success:
            _append_unique(
                report["findings"],
                "A successful technical message exists, but it predates the current authoritative change.",
                "Old technical success is not evidence that the current business change replicated.",
            )
        elif after_change:
            _append_unique(
                report["findings"],
                "Messages exist after the source change, but the evidence pack does not causally link them to the current change.",
            )
        else:
            _append_unique(
                report["findings"],
                "No outbound message is causally linked to the current authoritative change.",
            )
        _append_unique(report["missing_evidence"], "outbound event causally linked to the current source change")
        _append_unique(report["safe_next_actions"], "determine_whether_current_outbound_event_was_created")
        if manifest.get("recovery", {}).get("regeneration_supported") is True:
            _append_unique(report["safe_next_actions"], "consider_regenerating_current_authoritative_state_after_confirming_no_event")
        _append_unique(report["unsafe_actions"], "reprocess_old_successful_message", "manual_target_overwrite")
        return report

    message = _latest(current_messages, "created_at") or current_messages[-1]
    message_id = message.get("message_id", "")
    report["current_message"] = {
        "message_id": message_id,
        "status": message.get("status"),
        "business_status": message.get("business_status"),
        "created_at": message.get("created_at"),
        "target_id": message.get("target_id"),
        "mapping_version": message.get("mapping_version"),
        "causality": "explicit_change_id",
    }
    _append_unique(report["evidence_refs"], _evidence_ref("messages", "message_id", message_id))

    # 4. Guard event-time identity/mapping semantics before recommending replay.
    current_mapping = current_identity.get("mapping_version", "")
    event_mapping = message.get("mapping_version", "")
    if event_mapping and current_mapping and event_mapping != current_mapping:
        report["classification"] = "mapping_version_drift"
        _append_unique(
            report["findings"],
            f"The current identity mapping is {current_mapping}, but the event was created under {event_mapping}.",
            "Current mapping cannot be silently applied to historical event recovery.",
        )
        _append_unique(report["missing_evidence"], "event-time identity/mapping semantics")
        _append_unique(report["safe_next_actions"], "resolve_event_time_identity_before_replay")
        _append_unique(report["unsafe_actions"], "replay_using_current_mapping", "execute")
        return report

    if message.get("target_id") and message.get("target_id") != target_id:
        report["classification"] = "message_target_identity_mismatch"
        _append_unique(
            report["findings"],
            f"Current message targets {message.get('target_id')} while resolved current identity is {target_id}.",
        )
        _append_unique(report["safe_next_actions"], "resolve_event_time_identity")
        _append_unique(report["unsafe_actions"], "replay_message", "execute")
        return report

    status = message.get("status", "").lower()
    business_status = message.get("business_status", "").lower()
    if status in {"failed", "error", "cancelled", "rejected"}:
        report["status"] = "recommendation"
        report["classification"] = "technical_message_failure"
        _append_unique(report["findings"], f"The causally linked message has technical status {status}.")
        _append_unique(report["safe_next_actions"], "inspect_message_failure_and_commit_state")
        _append_unique(report["unsafe_actions"], "blind_retry_without_commit_or_idempotency_evidence")
        return report

    if business_status in {"rejected", "failed", "error"}:
        report["status"] = "recommendation"
        report["classification"] = "business_processing_rejection"
        _append_unique(
            report["findings"],
            "Technical transport reached the processing layer, but the business acknowledgement rejected the change.",
        )
        _append_unique(report["safe_next_actions"], "route_to_business_validation_or_target_processing")
        _append_unique(report["unsafe_actions"], "declare_resolved", "blind_retry")
        return report

    # 5. Verify current business state, not transport status.
    target_rows = [
        row
        for row in pack.tables["target_state"]
        if row.get("object_id") == target_id
        and (not attribute or row.get("attribute") == attribute)
    ]
    target_state = _latest(target_rows, "observed_at")
    if target_state is None:
        report["classification"] = "target_business_state_missing"
        _append_unique(report["findings"], "Technical evidence exists but target business state was not provided.")
        _append_unique(report["missing_evidence"], "current target business state")
        _append_unique(report["safe_next_actions"], "collect_target_business_state")
        _append_unique(report["unsafe_actions"], "declare_resolved")
        return report

    observed_at = _time(target_state.get("observed_at"))
    message_time = _time(message.get("created_at"))
    if observed_at and message_time and observed_at < message_time:
        report["classification"] = "target_observation_stale"
        _append_unique(
            report["findings"],
            "Target-state observation predates the current outbound event and cannot verify its business outcome.",
        )
        _append_unique(report["missing_evidence"], "target observation after current message processing")
        _append_unique(report["safe_next_actions"], "refresh_target_business_state")
        return report

    target_value = target_state.get("value", "")
    report["target_state"] = {
        "target_id": target_id,
        "attribute": target_state.get("attribute"),
        "value": target_value,
        "observed_at": target_state.get("observed_at"),
    }
    _append_unique(report["evidence_refs"], _evidence_ref("target_state", "object_id", target_id))

    if target_value == expected_value:
        report["status"] = "resolved_read_only"
        report["classification"] = "business_state_verified"
        _append_unique(
            report["findings"],
            "The target business state matches the current authoritative source value.",
            "The current change, message, identity, and target observation form a traceable evidence chain.",
        )
        _append_unique(report["safe_next_actions"], "close_incident_if_scope_is_complete")
        return report

    report["status"] = "recommendation"
    report["classification"] = "target_state_mismatch_after_current_event"
    _append_unique(
        report["findings"],
        f"The authoritative value is {expected_value!r}, but the observed target value is {target_value!r}.",
        "Technical message evidence does not establish the expected business postcondition.",
    )
    _append_unique(
        report["safe_next_actions"],
        "investigate_target_processing_or_business_validation",
        "reconcile_current_authoritative_state",
    )
    _append_unique(report["unsafe_actions"], "declare_resolved", "manual_target_overwrite", "blind_retry")
    return report
