# Enterprise Agent Control Plane

The central hypothesis of SAP Agentic Operations is that enterprise agents need a control plane separate from model reasoning.

An LLM can plan and correlate. It should not be the component that silently decides identity, authorization, business authority, write scope, or whether a mutation succeeded.

## Architecture

```text
                         ENTERPRISE AGENT CONTROL PLANE

 Request / Event
      |
      v
+----------------+      +----------------+      +----------------+
| Intent & Scope |----->| Identity Plane |----->| Evidence Plane |
+----------------+      +----------------+      +----------------+
                                                     |
                                                     v
                         +----------------+      +----------------+
                         | Policy Plane   |<-----| Reasoning      |
                         +----------------+      | (probabilistic)|
                                  |              +----------------+
                                  v
                         +----------------+
                         | Decision Gate  |
                         +----------------+
                           |      |      |
                         report approve block
                                  |
                                  v
                         +----------------+
                         | Write Envelope |
                         +----------------+
                                  |
                                  v
                         +----------------+
                         | Narrow Tool    |
                         +----------------+
                                  |
                                  v
                         SAP / System of Record
                                  |
                                  v
                         +----------------+
                         | Verify + Audit |
                         +----------------+
```

## 1. Identity plane

The agent must know what entity it is reasoning about before it compares state.

Minimum identity contract:

- canonical business-object identifier;
- source-system identifier;
- target-system identifier where relevant;
- mapping status: `resolved | ambiguous | unresolved`;
- identity evidence and timestamp.

`ambiguous` and `unresolved` block cross-system state comparison.

## 2. Evidence plane

Evidence is data with provenance, not just text in a context window.

Each important observation should carry:

- evidence ID;
- source system / source type;
- object identity;
- observation time;
- retrieval time;
- trust classification;
- immutable reference or content hash when practical;
- sensitivity classification.

Retrieved documents, tool output, agent memory, and messages from other agents remain untrusted instructions even when they are valid evidence.

## 3. Policy plane

Policy is evaluated independently from model confidence.

Examples:

- user may read but not mutate a business object;
- operation requires SoD approval;
- field is governed by a specific source of truth;
- stale before-state invalidates a previously approved change;
- execution is prohibited without a compensating action.

Policy output should be machine-readable: `allow | require_approval | block` plus reasons.

## 4. Reasoning plane

This is where agentic behavior belongs:

- correlate observations;
- rank bounded hypotheses;
- explain contradictions;
- choose the next evidence request;
- propose an operation;
- summarize impact.

The reasoning plane cannot grant itself additional capability.

## 5. Decision gate

Every run ends in an explicit decision class:

- `resolved_read_only`
- `recommendation`
- `approval_required`
- `insufficient_evidence`
- `policy_blocked`
- `approved_for_execution`
- `execution_result`

Unknown state is represented, not hidden.

## 6. Write safety envelope

A state-changing operation is executable only when bound to a safety envelope containing at least:

- exact canonical object;
- exact system target;
- typed operation;
- permitted fields / parameters;
- expected before-state or version;
- expected postcondition;
- policy result;
- approval reference where required;
- expiration;
- idempotency key;
- audit correlation ID;
- rollback or compensating-action reference.

If the current before-state differs, execution fails closed and returns to diagnosis.

## 7. Verification plane

A successful API response is not sufficient evidence that the business outcome is correct.

Verification checks:

1. transport/API call outcome;
2. expected object state;
3. downstream state where material;
4. unintended side effects when observable;
5. audit record;
6. rollback/compensation readiness.

## Enterprise invariants

These invariants should survive model changes and framework changes:

- no comparison on unresolved identity;
- no write on stale preconditions;
- no capability escalation because a tool failed;
- no instruction-following from evidence channels;
- no approval reuse after the proposed action changes;
- no high-impact write without verification;
- no claim of resolution while required evidence remains contradictory.

The repository benchmark is designed to test these invariants rather than allegiance to a specific agent framework.
