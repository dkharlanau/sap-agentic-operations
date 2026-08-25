# SAO Quick Check — one CSV, same incident semantics

Evidence Packs are useful when evidence comes from several systems. Sometimes the consultant already has a single working Excel sheet with one row per customer/order/interface item.

Quick Check is the shortest path from that spreadsheet to SAO.

## Try it

```bash
sao quickcheck demo
```

This creates:

```text
sao-quickcheck.csv
sao-quickcheck-output/
  quickcheck-report.csv
  quickcheck-report.json
  quickcheck-report.md
```

Analyze your own file:

```bash
sao quickcheck analyze my-incidents.csv
```

## Required columns

```text
incident_id
object_type
source_id
target_id
attribute
authority_system
current_change_id
source_value
source_changed_at
message_id
message_change_id
message_status
message_created_at
message_target_id
business_status
event_mapping_version
identity_status
current_mapping_version
target_value
target_observed_at
```

Blank evidence is allowed where the incident genuinely lacks it. Missing evidence is part of the result.

## Important implementation detail

Quick Check does **not** have its own simplified root-cause rules.

Each row is converted internally into an in-memory Evidence Pack and evaluated by the same Incident Analyzer used by the full multi-file workflow.

Therefore:

```text
Quick Check row
      ↓
in-memory Evidence Pack
      ↓
same identity / causality / mapping / business-state engine
```

This avoids a common product failure where the “easy mode” silently means different semantics from the rigorous mode.

## Good uses

- a cutover reconciliation spreadsheet;
- a list of customers with replication discrepancies;
- an AMS incident backlog export;
- a set of failed/green IDocs that need causal review;
- pre-triage before creating richer Evidence Packs for complex cases.

## When to move to a full Evidence Pack

Use the multi-file Evidence Pack when:

- one object has multiple changes/messages;
- identity mappings change over time;
- several target observations are relevant;
- one incident needs richer evidence/provenance;
- you want to preserve the incident as a reusable evidence artifact.

Quick Check optimizes time-to-first-value. Evidence Packs optimize depth and traceability.
