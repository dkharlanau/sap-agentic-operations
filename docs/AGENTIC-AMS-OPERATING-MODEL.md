# Agentic SAP AMS Operating Model

The strongest near-term use of agents around SAP is not autonomous configuration or transaction processing.

It is making **support operations more observable, evidence-driven and repeatable**.

A modern AMS model can treat the agent as a structured investigator inside an operating system of controls.

## The old support loop

A common production-support pattern is:

```text
user notices problem
-> opens ticket
-> support asks for examples
-> someone checks SAP
-> someone checks middleware
-> someone remembers a similar incident
-> several teams exchange screenshots
-> cause is eventually found
-> fix is applied
-> knowledge stays in ticket/chat
```

The user is effectively part of monitoring. Evidence collection is manual. Ownership is discovered during the incident.

## The target loop

```text
signal / ticket / monitor
        |
        v
scope + canonical identity
        |
        v
read-only evidence collection
        |
        v
deterministic checks
        |
        v
failure-class classification
        |
        v
agent hypothesis + missing evidence
        |
        +------> insufficient evidence -> collect / escalate
        |
        v
recovery recommendation
        |
        v
policy / business approval if needed
        |
        v
typed recovery operation
        |
        v
business postcondition
        |
        v
incident evidence + reusable memory
```

The agent improves the expensive ambiguous middle. Deterministic systems protect the boundaries.

## 1. Detect

Signals can come from:

- AIF/interface monitoring;
- IDoc/message failures;
- API/business acknowledgements;
- data-quality checks;
- reconciliation gaps;
- process KPIs;
- user tickets;
- scheduled comparison jobs.

The goal is to reduce dependence on user discovery.

## 2. Scope

Before diagnosis establish:

- business process;
- canonical object identity;
- system/client scope;
- organizational scope;
- relevant time window;
- business impact.

A ticket saying “customer not updated” is not yet a diagnostic object.

## 3. Evidence assembly

The evidence layer should retrieve approved data such as:

- source active state and change history;
- business event/change pointer/message IDs;
- middleware state;
- target processing state;
- target business state;
- identity/value mapping versions;
- relevant deterministic configuration checks;
- current runbook/policy version;
- related prior incident patterns.

Output should be structured and citable.

## 4. Deterministic triage

Run known checks before model reasoning.

Examples:

- identity resolved?;
- source change newer than last successful outbound?;
- message exists?;
- target processed?;
- business acknowledgement rejected?;
- target postcondition matches?;
- explicit business block exists?;
- required partner/master data exists?;
- mapping/config version matches?;

This removes many cases from the LLM entirely.

## 5. Agent reasoning

Now the agent can do useful work:

- correlate cross-system evidence;
- identify contradictions;
- rank remaining failure classes;
- explain likely causality;
- request specific missing evidence;
- recommend next diagnostic step;
- produce a concise support narrative.

Output should distinguish:

```yaml
facts: []
hypotheses: []
missing_evidence: []
recommended_next_step: ""
execution_allowed: false
```

## 6. Recovery decision

Recovery depends on failure class.

Examples:

- transient transport → idempotent retry;
- no outbound event → regenerate current authoritative state;
- business validation → correct owning data/config/process;
- identity ambiguity → resolve mapping;
- stale message → suppress/quarantine;
- unknown commit → inspect target before retry;
- failed postcondition → compensation review/escalation.

The agent can recommend. Policy and business authority decide whether recovery may execute.

## 7. Execute narrowly

A recovery tool should be business-specific and typed.

Good:

- `replay_confirmed_not_applied_event`;
- `run_customer_reconciliation`;
- `request_current_state_replication`.

Bad:

- generic RFC/GUI/admin execution.

See [`SAP-AGENT-TOOL-CONTRACTS.md`](SAP-AGENT-TOOL-CONTRACTS.md).

## 8. Verify

Resolution requires the business postcondition.

For example:

> target customer delivery-control version = current activated governance version.

Not:

> replay returned success.

The incident remains unresolved while postcondition is unavailable or wrong.

## 9. Learn without poisoning memory

After resolution, capture:

- failure class;
- environment/scope;
- evidence pattern;
- deterministic cause;
- recovery;
- applicable policy/config versions;
- conditions where this pattern is valid;
- expiry/review trigger.

Do not store a natural-language conclusion as timeless policy.

## Human / agent / automation split

| Step | Deterministic automation | Agent | Human/business |
|---|---|---|---|
| Detect | strong | optional summary | oversight |
| Scope | partial | assist | confirm ambiguous business scope |
| Evidence | strong | orchestrate/request | authorize sensitive access |
| Known checks | primary | explain | — |
| Hypothesis | inputs | primary | review high-impact cases |
| Recovery choice | enforce allowed set | recommend | approve material action |
| Execute | typed tool | invoke if authorized | approve where required |
| Verify | primary | explain gaps | accept business exception |
| Memory | validate metadata | draft pattern | approve durable operational guidance |

## AMS control metrics

Technical MTTR alone is not enough.

Track metrics such as:

### Detection gap

Time between business failure and first reliable signal.

### Evidence assembly time

Time until the incident has enough structured evidence for diagnosis.

### Identity-resolution debt

Open incidents where canonical/source/target identity is unresolved.

### Unverified resolution rate

Incidents closed without observed business postcondition.

### Blind retry rate

Recovery attempts executed without known commit/idempotency semantics.

### Repeat-without-learning rate

Recurring failure class with no improved deterministic check/runbook/monitor.

### User-reported detection share

Percentage of incidents first discovered by business users instead of monitoring.

A mature support model should drive this down for monitorable failure classes.

## Incident state machine

```text
DETECTED
  -> SCOPED
  -> EVIDENCE_READY
  -> DIAGNOSED | NEEDS_EVIDENCE
  -> RECOVERY_PROPOSED
  -> APPROVAL_REQUIRED | READY_TO_EXECUTE
  -> EXECUTED
  -> VERIFIED | VERIFICATION_FAILED
  -> RESOLVED
```

`EXECUTED` is intentionally not `RESOLVED`.

## Operating principle

> The goal of AI in AMS is not to make support look autonomous. It is to make operational truth easier to discover, decisions easier to review, and recovery safer to repeat.

That is a much more valuable transformation than adding a chatbot to incident management.
