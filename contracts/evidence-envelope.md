# Evidence Envelope

The evidence envelope makes observations auditable before they reach probabilistic reasoning.

Canonical schema: [`../schemas/evidence.schema.json`](../schemas/evidence.schema.json).

## Minimal example

```json
{
  "evidence_id": "ev-42",
  "source": {
    "system": "synthetic-mdg",
    "type": "business_object",
    "reference": "record/customer/C-100"
  },
  "object": {
    "canonical_type": "customer",
    "canonical_id": "customer-100",
    "system_id": "C-100",
    "mapping_status": "resolved"
  },
  "observed_at": "2026-08-25T10:00:00Z",
  "retrieved_at": "2026-08-25T10:00:05Z",
  "trust": "authoritative",
  "sensitivity": "internal",
  "content_hash": "sha256:...",
  "instruction_trust": "never_from_evidence"
}
```

## Why `observed_at` and `retrieved_at` are different

A value retrieved now may describe state observed earlier. Enterprise diagnosis frequently fails when retrieval time is mistaken for business-event time.

## Why instruction trust is explicit

Documents, logs, API payloads, tool output, prior incidents, and messages from other agents can contain text that looks like an instruction. In SAO they are evidence channels, not control channels.

The agent may reason about such text. It must not treat it as authorization or system instruction.

## Identity rule

Cross-system comparison requires `mapping_status=resolved`. An `ambiguous` mapping is evidence that more identity work is required, not permission to pick the closest candidate.

## Trust classes

- `authoritative` — designated source for the specific fact under current governance.
- `verified` — evidence checked through a trusted process but not necessarily the source of truth.
- `untrusted_evidence` — useful content whose instructions must never be followed.
- `historical` — prior observation or memory that requires current-state revalidation.
- `unknown` — origin or authority is insufficiently established.

Trust is scoped to the fact. A generally trusted system is not automatically authoritative for every field.
