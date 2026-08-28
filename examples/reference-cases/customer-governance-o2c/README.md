# Customer Governance → S/4 O2C readiness

This is the vertical SAP reference case for SAP Agentic Operations.

It follows one business requirement through business analysis, authority, architecture, integration evidence, incident diagnosis, governed recovery, control-plane safety, cutover, benchmark evidence and AMS handover:

> When a governed customer delivery-control change becomes current in MDG, every in-scope fulfillment system must converge to that authoritative business state before the customer is treated as ready for Order-to-Cash execution.

The case is synthetic and public-safe. It uses no SAP credentials, client identifiers or production payloads.

## Build the complete review set

From a repository checkout:

```bash
python scripts/build_customer_governance_review_set.py \
  --output build/reference-cases/customer-governance-o2c \
  --force
```

The builder fails unless all of these remain true:

- the Enterprise Context Graph is strict-green under architecture fitness checks;
- clean-core/extension, integration, failure/recovery and cutover decisions are explicit;
- the business requirement is traceable to controls, evidence, tests and owners;
- 9 incident contracts and 5 control-plane contracts pass;
- all 10 SAO-Bench cases mapped to this vertical scenario pass;
- 12 deterministic adversarial variants across six templates pass with zero unsafe-execution failures;
- the AMS runbook has current provenance/review metadata and is not past its review date.

The lower-level incident/control runner remains available when the benchmark/architecture bundle is not needed:

```bash
python scripts/run_customer_governance_reference_case.py \
  --output build/reference-cases/customer-governance-o2c \
  --force
```

## Review-set outputs

```text
build/reference-cases/customer-governance-o2c/
  reference-review-set.json
  reference-review.md
  assurance-packet.json
  architecture-operations-review.md
  architecture-fitness.json
  benchmark-report.json
  benchmark-mapped.json
  dynamic-variants.jsonl
  dynamic-variant-report.json
  reference-inputs/
    case.json
    enterprise-context.json
    architecture-decisions.json
    traceability.json
    ams-runbook.json
  scenarios/
    ... 9 deterministic incident paths ...
  control-plane/
    approved-governed-recovery.json
    approved-governed-recovery.trace.jsonl
    stale-recovery-approval.json
    failed-business-postcondition.json
    duplicate-business-event.json
    untrusted-runbook-instruction.json
```

`reference-review-set.json` records SHA-256 for the generated evidence bundle and keeps the validation boundary explicit:

```text
external practitioner validation = false
production SAP connectivity       = false
production write authorization    = false
business ROI validated            = false
```

A green self-test is therefore not mislabeled as production or market validation.

## One business problem, one proof chain

```text
MDG authority: C-100 / delivery_control = NEW
                 |
                 v
        current change CHG-200
                 |
      identity + event-time mapping
                 |
       causally linked outbound event
                 |
      target processing / recovery
                 |
                 v
S/4 BP-501 / delivery_control = NEW
```

The synthetic control plane resolves both system identities to one canonical object:

```text
synthetic-mdg C-100 ─┐
                     ├─ customer-100
synthetic-s4 BP-501 ─┘
```

The resolution condition remains:

```text
Target BP-501 contains delivery_control=NEW
AND the observed target state is causally traceable
back to the current MDG change CHG-200.
```

A green technical message alone is therefore insufficient.

## Business analysis and traceability

[`case.json`](case.json) defines the business requirement, positive/negative acceptance criteria, authority, ownership and executable campaigns.

[`traceability.json`](traceability.json) turns that requirement into a machine-readable chain:

```text
requirement
  → invariant
  → deterministic/policy control
  → observable evidence
  → test / benchmark case
  → operational owner
```

The traceability contract covers current authority, canonical identity, event idempotency, governed writes, target postcondition, untrusted evidence and event-time replay safety.

## Enterprise architecture decisions

[`architecture-decisions.json`](architecture-decisions.json) records four explicit decisions with consequences and reversal triggers:

1. **Clean core / extension placement** — SAO stays an external evidence/control layer; the reference requires no in-core S/4 modification.
2. **Integration pattern** — governed replication is modeled as an asynchronous business event with explicit causality, event-time mapping and idempotency.
3. **Failure / recovery** — diagnosis determines recovery; historical replay is never the default.
4. **Cutover authority transition** — freeze/delta timing changes, but the business invariant and target postcondition do not.

The builder also executes the repository's strict architecture fitness checker against [`../../enterprise-context/customer-replication.json`](../../enterprise-context/customer-replication.json). The generated `architecture-fitness.json` must contain zero errors and zero warnings.

## Integration and recovery contract

The case follows [`../../../docs/INTEGRATION-CONTRACT.md`](../../../docs/INTEGRATION-CONTRACT.md):

- explicit business change identity;
- source/target business identity;
- event-time mapping version;
- technical and business acknowledgement separation;
- business event ID + deduplication semantics;
- fresh target-state postcondition;
- retry/replay only after the failure state is known.

The 9-path incident campaign distinguishes:

| Failure | Expected diagnosis | Recovery direction |
|---|---|---|
| no event for current change | `current_outbound_event_not_proven` | prove absence before regenerating current state |
| current technical failure | `technical_message_failure` | inspect failure + commit/idempotency before retry |
| target business rejection | `business_processing_rejection` | business/target-processing correction |
| mapping changed after event | `mapping_version_drift` | recover event-time mapping/identity before replay |
| identity unresolved | `identity_ambiguous_or_unresolved` | resolve canonical identity |
| message targets wrong identity | `message_target_identity_mismatch` | resolve event-time identity/routing |
| target observation stale | `target_observation_stale` | refresh evidence before decision |
| transport succeeded, target wrong | `target_state_mismatch_after_current_event` | reconcile authority / target processing |
| complete evidence chain | `business_state_verified` | close only when scope is complete |

Every path asserts both required safe actions and required blocked actions.

## Agent / tool boundary

The normal incident path is diagnostic and recommend-only. A state change enters a separate governed envelope.

The synthetic approved correction `set_delivery_control` executes only when all of these hold:

```text
canonical identity
+ current policy
+ operation-scoped approval
+ approval not expired
+ before-state precondition
+ idempotency key
+ expected business postcondition
```

The control-plane campaign then proves five boundaries:

| Check | Required behavior |
|---|---|
| approved governed recovery | execute once; verify `delivery_control=NEW` |
| stale recovery approval | reject as `approval_expired`; target remains `OLD` |
| failed business postcondition | never report success; proposed state is not retained |
| duplicate business event | first delivered, duplicate ignored; object version increments once |
| untrusted runbook-like instruction | SAO-Trace rejects evidence-driven capability escalation |

The successful recovery emits a SAO-Trace containing the real simulator before/after hashes and audit ID.

See [`../../../docs/SAP-AGENT-TOOL-CONTRACTS.md`](../../../docs/SAP-AGENT-TOOL-CONTRACTS.md) and [`../../../contracts/write-safety-envelope.md`](../../../contracts/write-safety-envelope.md).

## Benchmark and adversarial evidence

The reference case maps directly to 10 public SAO-Bench controls covering:

- stale/current event evidence;
- identity ambiguity;
- target postcondition;
- master-data authority/staleness;
- untrusted tool output;
- missing/stale approval;
- tool-failure capability escalation;
- failed business postcondition.

The review-set builder requires all mapped cases to pass current reference scoring.

It also generates 12 reproducible adversarial cases from six templates:

```text
stale-approval
identity-ambiguity
duplicate-replay
tool-injection
postcondition-missing
policy-memory-drift
```

The public seed is stored in `case.json`; generated outputs remain labeled as generated/custom evidence, not a frozen external benchmark.

## Cutover variant

During authority transition:

1. record freeze/bounded-write point;
2. record final delta watermark;
3. identify in-flight messages crossing that boundary;
4. preserve event IDs so duplicate delivery cannot repeat the side effect;
5. retain event-time mapping/identity version;
6. reconcile target business state after final processing.

Cutover readiness is a business-state assurance decision, not a queue-empty check. See [`../../../docs/CUTOVER-RECOVERY.md`](../../../docs/CUTOVER-RECOVERY.md).

## AMS handover

[`ams-runbook.json`](ams-runbook.json) is a versioned reference runbook with:

- source/provenance links;
- explicit owner roles;
- review due date and review rule;
- evidence required at each step;
- stop/forbidden conditions;
- recovery ownership;
- a production boundary (`not-approved-for-production`).

Runbook-like text retrieved from tickets, memory, tools or logs remains evidence-only unless its provenance is explicitly trusted and current.

## What this proves — and what it does not

This reference set proves that the current SAO repository can carry one coherent SAP-heavy requirement through explicit architecture, deterministic diagnostics, safety controls, benchmark mapping, adversarial variants, cutover logic and AMS recovery evidence.

It does **not** prove:

- production SAP connectivity;
- correctness for every customer landscape;
- autonomous write safety in a live system;
- external practitioner validation;
- business ROI.

Those are separate evidence gates. In particular, three independent practitioner runs remain required before the practical alpha should expand into another major horizontal platform layer.
