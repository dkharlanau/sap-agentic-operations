# Semantic Master-Data Reconciliation

A normal CSV diff answers:

> Which cells are different?

That is not enough for enterprise master data.

SAO asks:

> **Which identity is this, who owns this attribute, which snapshot is newer, and what conclusion is justified by that evidence?**

The reconciliation workflow is intentionally read-only. It classifies discrepancies; it does not correct SAP data.

## Try the demo

```bash
sao reconcile demo
```

The generated example contains three synthetic customers:

1. an authoritative source snapshot newer than a stale target value;
2. a target snapshot newer than the source export;
3. an aligned record.

The second case is important. A generic diff sees a mismatch. SAO refuses to assume that the target is wrong simply because the source is labelled authoritative: the source evidence itself is older, so the safe next action is to refresh authoritative evidence and understand the newer target change origin.

## Pack structure

```text
reconciliation/
  reconcile.json
  source.csv
  target.csv
  identity_map.csv
```

Example `reconcile.json`:

```json
{
  "format": "sao-reconciliation-pack",
  "version": "0.1",
  "reconciliation_id": "customer-master-check",
  "source": {
    "system": "MDG",
    "file": "source.csv",
    "id_column": "source_id",
    "observed_at_column": "observed_at"
  },
  "target": {
    "system": "S4",
    "file": "target.csv",
    "id_column": "target_id",
    "observed_at_column": "observed_at"
  },
  "identity_map": {"file": "identity_map.csv"},
  "attributes": [
    {"name": "tax_class", "authority": "source"},
    {"name": "delivery_control", "authority": "source"}
  ]
}
```

Run:

```bash
sao reconcile analyze ./reconciliation
```

Outputs:

```text
sao-output/
  reconciliation-report.csv
  reconciliation-report.json
  reconciliation-report.md
```

## Current classifications

### `aligned`

The supplied values agree.

### `identity_unresolved` / `identity_ambiguous`

Cross-system comparison is not safe until canonical identity is established.

SAO will not merge or select a record based on name similarity.

### `target_record_missing`

A resolved source identity has no corresponding target record in the supplied target snapshot.

This does not automatically mean “create it.” Expected target scope and creation state still need to be understood.

### `attribute_authority_unresolved`

The values differ, but the pack does not establish which side owns that attribute.

A record-level “system of record” statement is not enough when different attributes have different owners.

### `mismatch_freshness_unknown`

Values differ but one or both snapshot timestamps are missing/unparseable.

Do not overwrite without freshness evidence.

### `authoritative_mismatch`

Values differ and the authoritative snapshot is at least as fresh as the compared non-authoritative snapshot.

Typical next step:

```text
investigate_replication_or_target_processing
```

### `non_authoritative_snapshot_is_newer`

The compared non-authoritative side is newer than the authoritative export.

This is deliberately **not** classified as a simple stale-target error.

Safe next step:

```text
refresh_authoritative_evidence_and_reconcile_change_origin
```

Unsafe shortcut:

```text
overwrite_newer_state_from_stale_snapshot
```

## Why this matters in SAP projects

Master-data discrepancies are often discussed as if there were one permanent truth table and one bad copy. Real landscapes are temporal:

- governance workflows may still be pending;
- mappings change;
- local attributes have different owners;
- source exports become stale;
- target systems may receive legitimate later changes;
- cutover phases temporarily change authority.

SAO therefore treats **identity + attribute authority + freshness** as minimum reconciliation context.

Future versions can add mapping/value-map semantics and change/event provenance without changing this principle.
