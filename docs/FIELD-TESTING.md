# Field-test SAO without exposing client data

Practical Toolkit `0.4.0-alpha.3` is at the point where **field feedback is more valuable than another framework feature**.

The purpose of a field test is simple:

> Take one real SAP operational job, preserve its failure semantics without exposing client data, and check whether SAO produces a useful and correct operational conclusion.

## Good first jobs

- newer master-data change not visible in target;
- green IDoc but wrong business state;
- repeated failed messages where replay safety is unclear;
- mapping changed between original event and recovery;
- list of customer replication discrepancies;
- source/target master-data snapshots that differ;
- cutover reconciliation spreadsheet.

## Fastest path: Quick Check

If you already have one row per problem in Excel:

```bash
sao quickcheck analyze incidents.csv
```

Start with one or two sanitized rows rather than hundreds.

## Deeper path: Evidence Pack

Use when one incident has multiple pieces of evidence:

```bash
sao incident init ./incident --incident-id TEST-001
```

Fill:

```text
source_changes.csv
messages.csv
target_state.csv
identity_map.csv
```

Then:

```bash
sao incident validate ./incident
sao incident analyze ./incident
sao workbench ./incident
```

## What to judge

Do not judge whether the wording sounds sophisticated.

Judge these questions:

1. Did SAO select the **current business change**, not an old technical success?
2. Did it require a real identity mapping before cross-system comparison?
3. Did it distinguish message/transport success from target business state?
4. Did it notice stale snapshots or mapping-version drift?
5. Did it identify evidence that was genuinely missing?
6. Was the proposed next action safe and useful?
7. Did it block a recovery action that actually should have been allowed?
8. Did it allow a conclusion that should have remained uncertain?
9. Did the result reduce manual investigation effort?

## Privacy-safe sanitization

Before sharing any field report publicly:

- replace customer/vendor/order IDs with synthetic IDs;
- replace company/system names with roles such as `MDG`, `LEGACY`, `S4_TARGET`;
- remove ticket numbers and ticket text;
- remove internal URLs, hostnames and credentials;
- do not attach original SAP payloads;
- keep timestamps relative or synthetic if exact timing is sensitive;
- preserve the causal/failure structure.

The useful information is:

```text
change happened
message X did/did not correspond
mapping changed
business state differed
replay was safe/unsafe
```

—not the client's identity.

## How to report a result

Use the GitHub issue form **SAO practical field report**.

The best report can be very short:

```text
Job:
Customer replication discrepancy after a new governed change.

Evidence available:
Source change timestamp, two IDocs, mapping table, S/4 snapshot.

SAO result:
current_outbound_event_not_proven

Useful?
Yes. It stopped us from treating an older successful IDoc as evidence for the new change.

Missing/wrong:
Our landscape has a second acknowledgement layer that SAO does not model yet.
```

That is enough to create a useful next product iteration without publishing client data.

## Alpha success criterion

Before a new major framework layer, target:

- 3 independent practitioner runs;
- 1 case where SAO is wrong/incomplete;
- 1 real export layout normalized;
- 1 diagnostic rule improved from field evidence.

A discovered false assumption is a successful alpha result.
