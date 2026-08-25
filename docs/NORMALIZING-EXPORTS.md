# Normalizing SAP and Excel Exports

SAO uses canonical evidence columns so diagnostic logic remains stable. Real exports do not.

A WE02 export might call the message ID `DOCNUM`. Another file may call it `IDOC_NUMBER`. Status may be `53`, `51`, `SUCCESS`, `ERROR`, or a project-specific value. Requiring users to manually rename every file would make Evidence Packs impractical.

The normalizer separates **source format** from **evidence semantics**.

## Try the synthetic WE02-style demo

```bash
sao normalize demo
```

It creates:

```text
sao-normalize-demo/
  we02_export.csv
  messages.mapping.json
  messages.csv
```

The input contains SAP-like technical statuses:

```text
53
51
```

The mapping converts them to canonical SAO states:

```text
success
failed
```

and supplies a constant mapping version for the export.

## Mapping format

```json
{
  "columns": {
    "message_id": "DOCNUM",
    "change_id": "CHANGE_REF",
    "object_id": "OBJECT_KEY",
    "status": "STATUS",
    "created_at": "CREATED_AT",
    "target_id": "RECEIVER",
    "business_status": "BUS_ACK"
  },
  "constants": {
    "mapping_version": "M1"
  },
  "value_maps": {
    "status": {
      "53": "success",
      "51": "failed"
    }
  }
}
```

Run against your own export:

```bash
sao normalize csv \
  --table messages \
  --input my-export.csv \
  --mapping messages.mapping.json \
  --output incident/messages.csv
```

Supported canonical tables in v0.1:

- `source_changes`
- `messages`
- `target_state`
- `identity_map`

## Why mapping is explicit

SAO deliberately does not guess that a column named `STATUS` means technical message status or that a field called `CUSTOMER` is a canonical identity.

Automatic guessing is convenient until it maps the wrong field and produces a plausible but false diagnosis.

The mapping file is therefore an auditable boundary:

```text
raw export
    ↓
explicit column/value mapping
    ↓
canonical Evidence Pack table
    ↓
deterministic analysis
```

Projects can version their mapping files alongside runbooks and integration documentation. If the export layout changes, the mapping change is visible and reviewable.

## Future collectors

Direct Cloud ALM/AIF/CPI collectors should emit the exact same canonical tables.

This means a team can start with manual Excel exports and later automate collection without replacing the diagnostic model.
