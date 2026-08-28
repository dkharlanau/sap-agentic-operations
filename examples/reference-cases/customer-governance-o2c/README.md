# Customer Governance → S/4 O2C readiness

This is the vertical SAP reference case for SAP Agentic Operations.

It follows one business requirement through authority, identity, integration evidence, failure diagnosis, recovery choice and business-state verification:

> When a governed customer delivery-control change becomes current in MDG, every in-scope fulfillment system must converge to that authoritative business state before the customer is treated as ready for Order-to-Cash execution.

The case is synthetic and public-safe. It uses no SAP credentials, client identifiers or production payloads.

## Run the complete failure campaign

From a repository checkout:

```bash
python scripts/run_customer_governance_reference_case.py \
  --output build/reference-cases/customer-governance-o2c \
  --force
```

The runner uses the same `sao_toolkit` Incident Analyzer that backs the practical CLI. It does not contain a second diagnosis implementation.

Outputs:

```text
build/reference-cases/customer-governance-o2c/
  assurance-packet.json
  architecture-operations-review.md
  scenarios/
    missing-current-event/
    technical-failure/
    business-rejection/
    mapping-drift/
    identity-unresolved/
    target-identity-mismatch/
    stale-target-observation/
    target-mismatch/
    resolved/
```

Every scenario retains its generated Evidence Pack plus JSON/Markdown incident report. The assurance packet records SHA-256 for the scenario contract/output artifacts and fails generation if the analyzer no longer meets the expected safety contract.

## One business problem, not nine disconnected demos

The failure campaign changes evidence around the same governed customer change:

```text
MDG authority: C-100 / delivery_control = NEW
                 |
                 v
        current change CHG-200
                 |
          identity + mapping
                 |
          outbound evidence
                 |
          target processing
                 |
                 v
S/4 BP-501 / delivery_control = NEW
```

The resolution condition stays stable:

```text
Target BP-501 contains delivery_control=NEW
AND the observed target state is causally traceable
back to the current MDG change CHG-200.
```

That means a technically green message is insufficient if identity, mapping, business acknowledgement, freshness or target state is wrong.

## Business analysis

The machine-readable contract in [`case.json`](case.json) defines:

- business requirement and process boundary;
- system/data authority;
- business invariants;
- positive and negative acceptance criteria;
- business, data-governance, integration, operations and security ownership;
- explicit non-goals.

The key business invariant is deliberately simple: **current authoritative business state must be proven at the target before O2C readiness is declared.**

## Enterprise architecture

The case reuses existing SAO architecture rather than copying it:

- [`../../enterprise-context/customer-replication.json`](../../enterprise-context/customer-replication.json) — enterprise context and authority boundary;
- [`../../../architectures/reference-architecture.md`](../../../architectures/reference-architecture.md) — evidence-first architecture;
- [`../../../docs/ARCHITECT-DECISION-SPINE.md`](../../../docs/ARCHITECT-DECISION-SPINE.md) — architecture decision sequence;
- [`../../../docs/AGENT-IDENTITY-AUTHORIZATION.md`](../../../docs/AGENT-IDENTITY-AUTHORIZATION.md) — identity and authorization boundary.

The case contract validates these references before execution so the walkthrough cannot silently point at removed architecture.

## Integration contract

The runtime analysis depends on the same controls described in [`../../../docs/INTEGRATION-CONTRACT.md`](../../../docs/INTEGRATION-CONTRACT.md):

- explicit business change identity;
- source/target business identity;
- event-time mapping version;
- technical and business acknowledgement separation;
- fresh target-state postcondition;
- retry/replay only after the relevant failure state is known.

## Agent / tool boundary

This reference case is diagnostic and recommend-only.

The agent/tool contract may:

- read bounded evidence;
- classify the current evidence state;
- identify missing evidence;
- recommend a recovery class;
- explicitly block unsafe shortcuts.

It may not silently overwrite S/4, reprocess an old message, bypass authorization or treat a recommendation as an approved change. See [`../../../docs/SAP-AGENT-TOOL-CONTRACTS.md`](../../../docs/SAP-AGENT-TOOL-CONTRACTS.md) and [`../../../contracts/write-safety-envelope.md`](../../../contracts/write-safety-envelope.md).

## Executable failure and recovery campaign

| Failure | Expected diagnosis | Bounded recovery direction |
|---|---|---|
| no event for current change | `current_outbound_event_not_proven` | prove absence, then regenerate current authoritative state if supported |
| current technical failure | `technical_message_failure` | inspect failure + commit/idempotency state before retry |
| target business rejection | `business_processing_rejection` | business/target-processing correction |
| mapping changed after event | `mapping_version_drift` | resolve event-time identity/mapping before replay |
| identity unresolved | `identity_ambiguous_or_unresolved` | resolve canonical identity |
| message targets wrong identity | `message_target_identity_mismatch` | resolve event-time identity/routing |
| target observation is stale | `target_observation_stale` | refresh target evidence before decision |
| transport succeeded, target wrong | `target_state_mismatch_after_current_event` | reconcile authority / investigate target processing |
| complete evidence chain | `business_state_verified` | close only if scope is complete |

The runner checks both required **safe actions** and required **blocked actions**. A regression where an unsafe shortcut disappears from the blocked set fails the reference case.

## Cutover variant

During authority transition the same invariant is retained but the evidence boundary changes:

1. record freeze/bounded-write point;
2. record final delta watermark;
3. identify in-flight messages crossing that boundary;
4. retain the event-time mapping/identity version;
5. reconcile target business state after final processing.

Cutover readiness is therefore a business-state assurance decision, not a queue-empty check. See [`../../../docs/CUTOVER-RECOVERY.md`](../../../docs/CUTOVER-RECOVERY.md).

## AMS handover

The contract defines the monitoring signals and incident lifecycle required to operate the same design after go-live:

```text
collecting_evidence
  → bounded_diagnosis
  → recovery_decision
  → recovery_in_progress
  → business_postcondition_check
  → resolved
```

The generated `architecture-operations-review.md` is the compact handover/review artifact.

## What this proves — and what it does not

It proves that the current deterministic analyzer distinguishes several materially different SAP-heavy failure states and preserves bounded recovery decisions for one coherent business scenario.

It does **not** prove:

- production SAP connectivity;
- correctness for every customer landscape;
- autonomous write safety in a live system;
- external practitioner validation;
- business ROI.

Those are separate evidence gates. In particular, three independent practitioner runs remain required before the practical alpha should expand into another major horizontal platform layer.
