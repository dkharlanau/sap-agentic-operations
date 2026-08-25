# Cutover and Recovery Architecture

Cutover is not a project-management checklist. For a few hours or days, the enterprise runs under a **different architecture**: authority moves, clocks matter, mappings can change, queues accumulate, and the same business object may exist in two valid but temporally different realities.

SAO treats cutover and recovery as first-class architecture.

## 1. Define the authority transition

For every important object/process, write the transition explicitly.

```text
BEFORE CUTOVER              DURING CUTOVER              AFTER CUTOVER
Legacy authoritative   ->   frozen / delta only   ->    S/4 authoritative
Target shadow copy     ->   load + reconcile      ->    operational source
Old interface active   ->   drained / stopped     ->    retired
New interface passive  ->   controlled start      ->    active
```

For master data, authority may transition at different times by object or attribute. Avoid one global statement such as `S/4 becomes source of truth at go-live` unless that is literally true for every governed attribute.

## 2. Freeze is a business rule

A freeze defines which changes are legal, not merely when users should stop typing.

Capture:

- freeze start;
- scope;
- exempt emergency changes;
- who can approve an exception;
- where exception changes are recorded;
- whether exceptions enter the migration delta;
- how late changes are reconciled.

An agent must never infer that urgency overrides freeze policy.

## 3. Delta boundary

Every migration needs a precise answer to:

> Which source changes are included in the load, and which are expected to arrive later through normal integration?

Use an explicit watermark/version, not an approximate clock time where possible.

Examples:

- change number <= N included in migration;
- source snapshot at version V;
- events before sequence S included;
- transactions posted before business cutoff C included.

This creates a causal boundary for reconciliation.

## 4. Identity and mapping freeze

Mapping is state.

Before cutover capture:

- legacy ID;
- target ID;
- canonical business identity;
- mapping version;
- effective time;
- unresolved/ambiguous mappings;
- mapping changes allowed during the window.

If a mapping changes after an event or migration record was created, recovery must know whether to apply historical or current semantics.

## 5. In-flight integration

At stop/start time, classify every in-flight message/event:

- delivered and business-applied;
- delivered but business result unknown;
- pending in sender;
- pending in middleware;
- pending in receiver;
- failed and retryable;
- failed and requires regeneration;
- obsolete after cutover.

`Queue empty` is not enough. The important question is whether all in-scope business changes are represented exactly once in the new steady state.

## 6. Duplicate and replay policy

Migration plus live integration creates a classic double-apply risk.

Define:

- how migrated state relates to queued events;
- which messages must be suppressed because their state is already in the load;
- whether business event IDs survive cutover;
- how idempotency is preserved;
- how older messages are recognized after newer state is loaded.

Do not replay historical traffic simply because it is technically available.

## 7. Reconciliation model

A useful reconciliation has layers.

### Level 1 — counts

- expected objects;
- migrated objects;
- rejected objects;
- unresolved mappings.

Necessary, but weak.

### Level 2 — keys

- all expected canonical identities present;
- no unexpected duplicates;
- no orphan target records.

### Level 3 — critical attributes

Compare business-critical attributes according to authority and scope.

### Level 4 — process readiness

Prove that migrated objects can participate in the required process:

- customer can be ordered/shipped/billed when expected;
- supplier can be procured/paid when expected;
- partner relationships resolve;
- credit/tax/delivery controls behave correctly.

### Level 5 — integration continuity

Prove that a post-cutover delta can flow from source to target with correlation and business verification.

The last two levels are what turn migration validation into operational readiness.

## 8. Go/no-go evidence

A go-live decision should refer to evidence, not confidence language.

Example evidence set:

```yaml
identity:
  unresolved_critical: 0
migration:
  expected: 2480
  loaded: 2480
  rejected: 0
critical_attribute_reconciliation:
  mismatches_open: 0
interfaces:
  old_path_drained: true
  new_path_smoke_test: passed
business_postconditions:
  o2c_smoke: passed
  p2p_smoke: passed
recovery:
  rollback_tested: true
open_risks:
  - id: RISK-...
    owner: ...
    accepted_by: ...
```

An AI summary may explain this evidence. It should not manufacture the go/no-go authority.

## 9. Rollback is not time travel

Rollback after business activity begins is often a compensation program, not a database restore.

Ask:

- Which system has accepted new business transactions?
- Which external parties received messages?
- Which numbers/documents were allocated?
- Which master-data changes were made only in the new system?
- Can state be reversed safely?
- Which actions require financial/regulatory approval?

A rollback plan that only says `restore backup` is not a business rollback plan.

## 10. Recovery classes

Classify cutover failures before the event.

| Failure | Typical response |
|---|---|
| Missing object, source unchanged | regenerate/reload object |
| Wrong identity mapping | stop, correct mapping, re-evaluate affected events |
| Duplicate application | quarantine, determine business impact, compensate if required |
| Old message after new state | suppress or evaluate historical semantics |
| Target business validation failure | correct business data/process, not blind retry |
| Unknown commit state | inspect target before retry |
| Postcondition failed | mark unresolved, escalate/compensate |
| Authority unclear | business/data owner decision required |

## 11. Hypercare handover

The cutover team should not hand operations a spreadsheet of defects. Hand over an operating model.

Required:

- monitored business objects/processes;
- known error classes;
- evidence locations;
- replay/retry rules;
- escalation matrix;
- manual recovery procedures;
- temporary cutover exceptions and expiry;
- baseline reconciliation dataset;
- definition of `resolved`.

Hypercare ends when normal operations can distinguish new defects from migration residue and recover them safely.

## 12. Agent role during cutover

Agents can add substantial value in read/recommend mode:

- correlate migration rejects with identity/mapping evidence;
- classify interface failures;
- compare source/target state;
- detect stale or duplicate events;
- summarize reconciliation gaps;
- propose the next diagnostic step.

Execution should be especially constrained during cutover because the architecture is changing underneath the agent.

Useful additional gates:

- cutover phase;
- authority version;
- mapping version;
- freeze status;
- delta watermark;
- approved recovery operation;
- current target state.

## Cutover architecture card

```yaml
object_or_process: ""
pre_cutover_authority: ""
post_cutover_authority: ""
freeze:
  start: ""
  exceptions: ""
delta_watermark: ""
identity_mapping_version: ""
in_flight_policy: ""
duplicate_policy: ""
replay_policy: ""
reconciliation_levels: []
go_live_postconditions: []
rollback_trigger: ""
rollback_or_compensation: ""
hypercare_owner: ""
agent_max_capability: recommend
```

A cutover is ready when the team can explain not only how to move the data, but how to preserve business truth while authority is moving.
