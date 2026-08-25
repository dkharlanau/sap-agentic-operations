# Five-minute walkthrough — Practical Toolkit 0.4.0-alpha.1

This walkthrough is designed for a SAP consultant, support analyst, system analyst, integration lead or architect who wants to understand the practical SAO workflow before preparing any real evidence.

## 1. Install

```bash
git clone https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations
python -m pip install .
```

## 2. Run the default incident

```bash
sao demo
```

The synthetic situation contains:

- source customer `C-100`;
- target BP `BP-501`;
- older source change `CHG-100`;
- a successful message for `CHG-100`;
- newer authoritative change `CHG-200`;
- target still holding the old value;
- no message linked to `CHG-200`.

The interesting fact is not that a successful message exists.

The interesting fact is that it explains the **wrong change**.

Expected result:

```text
current_outbound_event_not_proven
```

## 3. Open the local report

```bash
sao workbench ./sao-demo
```

Look at four sections:

### Findings

What SAO can establish from supplied evidence.

### Missing evidence

What prevents a stronger conclusion.

### Safe next actions

The next evidence/recovery step justified by the current state.

### Not justified by current evidence

Actions that may be tempting but are not currently safe.

For the default scenario, the important blocked shortcut is reprocessing the old successful message.

## 4. Change the failure mode

```bash
sao demo --scenario business-rejection --output sao-rejected
sao workbench ./sao-rejected
```

This time the current message is technically successful but business processing rejects it.

The classification changes to:

```text
business_processing_rejection
```

This demonstrates a core SAO principle:

> **Transport success is not business success.**

## 5. Try semantic reconciliation

```bash
sao reconcile demo
```

The demo includes one counterintuitive case: the target snapshot is newer than the source export.

A basic CSV diff says the records differ.

SAO says:

```text
non_authoritative_snapshot_is_newer
```

and blocks:

```text
overwrite_newer_state_from_stale_snapshot
```

This demonstrates the second core practical idea:

> **Authority without freshness is not enough to justify correction.**

## 6. Move to your own data

For one Excel-style list:

```bash
sao quickcheck analyze my-incidents.csv
```

For a richer incident:

```bash
sao incident init ./incident --incident-id TEST-001
```

For unfamiliar SAP/Excel column names:

```bash
sao normalize csv \
  --table messages \
  --input my-export.csv \
  --mapping my-mapping.json \
  --output incident/messages.csv
```

## What to tell us after trying it

A useful field report is not “nice project.”

It is:

```text
I was investigating X.
I had evidence A/B/C.
SAO classified it as Y.
That was useful/wrong because Z.
The missing evidence or recovery class was Q.
```

Use the repository's **SAO practical field report** issue form and sanitize all client data.
