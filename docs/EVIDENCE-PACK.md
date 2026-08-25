# SAO Evidence Pack v0.1

An Evidence Pack is the practical input contract for SAP Agentic Operations.

It is deliberately boring.

No database is required. No SAP credential is required. No model is required. A consultant can collect a small set of exports, put them in one folder, and ask SAO to reason about **identity, authority, causality, message state, and observed business state** without pretending that one green technical status proves the incident is resolved.

## Why a folder instead of another connector-first product

SAP incidents rarely fail because one monitoring screen is missing. They fail because the evidence is fragmented:

- the governed change is visible in one system;
- the outbound event in another;
- middleware has its own status;
- the target has a different identifier;
- mapping changed over time;
- the ticket contains historical advice;
- and somebody eventually asks: "Can I just retry it?"

Connectors are useful, but they should populate a stable evidence contract rather than define the product. This keeps SAO usable with manual exports today and Cloud ALM/AIF/CPI/API collectors later.

## Minimal structure

```text
incident/
  incident.json
  source_changes.csv
  messages.csv
  target_state.csv
  identity_map.csv
```

Validate it:

```bash
sao incident validate ./incident
```

Analyze it:

```bash
sao incident analyze ./incident
```

Outputs:

```text
incident/sao-output/
  incident-report.json
  incident-report.md
```

## `incident.json`

```json
{
  "format": "sao-evidence-pack",
  "version": "0.1",
  "incident_id": "customer-2026-001",
  "kind": "master-data-replication",
  "object": {
    "type": "customer",
    "source_id": "C-100",
    "target_id": "BP-501"
  },
  "authority": {
    "system": "MDG",
    "attribute": "delivery_control"
  },
  "files": {
    "source_changes": "source_changes.csv",
    "messages": "messages.csv",
    "target_state": "target_state.csv",
    "identity_map": "identity_map.csv"
  },
  "recovery": {
    "regeneration_supported": true
  },
  "resolution_condition": "Target business state matches the current authoritative change and the evidence chain is causally traceable."
}
```

## Source changes

Required columns:

```text
change_id,object_id,attribute,value,changed_at
```

The important idea is **change identity**, not merely object identity.

If a customer was changed at 10:15, a successful IDoc from 09:40 does not explain the current discrepancy. SAO treats that as missing causality rather than as a successful replication.

## Messages

Required columns:

```text
message_id,change_id,object_id,status,created_at,target_id,business_status,mapping_version
```

The first version intentionally separates:

- technical message status;
- business acknowledgement/status;
- event/change identity;
- target identity;
- mapping version.

This allows SAO to distinguish cases such as:

- transport failed;
- transport succeeded but business processing rejected the message;
- message belongs to an older change;
- mapping changed between event creation and recovery;
- the message is technically successful but the target business state is still wrong.

## Target state

Required columns:

```text
object_id,attribute,value,observed_at
```

The observation timestamp matters. A target snapshot taken before the current message cannot prove the current message succeeded.

## Identity map

Required columns:

```text
source_id,target_id,status,mapping_version,effective_from
```

SAO does not choose a target object from fuzzy similarity. Identity must be resolved explicitly before cross-system comparison or recovery.

## What the analyzer returns

The report is intentionally structured around operational decisions:

- `status` — whether evidence is sufficient for a bounded conclusion;
- `classification` — the current failure class;
- `findings` — statements directly supported by supplied evidence;
- `missing_evidence` — what still prevents a safe conclusion;
- `safe_next_actions` — bounded next steps justified by evidence;
- `unsafe_actions` — tempting actions not justified by current evidence;
- `evidence_refs` — traceable references back to the pack;
- `resolution_condition` — what must be observed before the incident can be called resolved.

## Example: old success is not current success

The bundled demo contains:

- old change `CHG-100`;
- successful message for `CHG-100`;
- newer authoritative change `CHG-200`;
- target still holding the old value;
- no message linked to `CHG-200`.

Run:

```bash
sao demo
```

Expected classification:

```text
current_outbound_event_not_proven
```

Expected operational consequence:

- do not replay the old successful message;
- determine whether an outbound event for the current change exists;
- only consider regeneration from current authoritative state after confirming that the current event was not created;
- do not close the incident until target business state is verified.

## Privacy and client data

Evidence Packs are local files. SAO does not upload them anywhere.

For public examples and GitHub issues:

- use synthetic identifiers;
- remove customer/company names;
- remove tickets and internal URLs;
- remove credentials and tokens;
- do not publish raw production payloads;
- preserve the failure semantics, not the client's data.

## Connector principle

Future collectors should all produce the same Evidence Pack model.

Examples:

```text
Cloud ALM       -> Evidence Pack
AIF export      -> Evidence Pack
CPI export      -> Evidence Pack
IDoc CSV        -> Evidence Pack
custom SQL/API  -> Evidence Pack
manual Excel    -> Evidence Pack
```

That is how SAO stays portable: **connectors change; evidence semantics remain stable.**
