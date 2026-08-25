# Enterprise Agent Readiness Ladder

The wrong way to discuss agent maturity is:

> How autonomous should we make it?

Autonomy is an outcome of architecture readiness, not a starting target.

This ladder asks a different question:

> What controls must exist before the next level of agent capability becomes credible?

## Level 0 — Opaque Operations

Characteristics:

- knowledge lives in people and tickets;
- system ownership is ambiguous;
- integration errors are interpreted manually;
- business postconditions are not observable;
- recovery depends on experienced individuals;
- mappings and exceptions are partly tribal knowledge.

Agent opportunity:

- search and summarization only.

Maximum sensible capability:

**Read**, and even read results must be treated carefully because context is incomplete.

Do not automate state changes here. AI will amplify ambiguity.

## Level 1 — Observable

Characteristics:

- important systems and interfaces are identified;
- correlation exists across major technical hops;
- current object state is retrievable;
- failure statuses are visible;
- basic ownership is known.

Still missing:

- explicit business authority;
- reliable failure taxonomy;
- recovery contracts;
- requirement/invariant traceability.

Agent opportunity:

- evidence assembly;
- incident summarization;
- search across operational knowledge.

Maximum sensible capability:

**Read**.

## Level 2 — Contracted

Characteristics:

- canonical identity is defined;
- source/data authority is explicit;
- integration semantics are documented;
- retry/replay/idempotency rules exist;
- business postconditions are observable;
- deterministic business validations are exposed;
- recovery ownership exists;
- cutover/migration authority rules are explicit when relevant.

Agent opportunity:

- root-cause hypothesis ranking;
- discrepancy analysis;
- recovery option recommendation;
- requirement/test generation;
- architecture drift explanation.

Maximum sensible capability:

**Recommend**.

This is the first level where an enterprise agent becomes genuinely useful rather than merely conversational.

## Level 3 — Governed Decision Support

Characteristics:

- policy decisions are machine-evaluable;
- approvals are scoped artifacts rather than booleans;
- evidence provenance/freshness is preserved;
- operational memory is versioned;
- negative acceptance criteria exist;
- agent decisions are auditable;
- runtime/tool scope is explicit;
- benchmark/eval cases cover material failure modes.

Agent opportunity:

- prepare approval packets;
- propose bounded recovery;
- recommend changes with evidence;
- produce assurance reports;
- orchestrate read-only diagnostics.

Maximum sensible capability:

**Recommend**, with controlled transition to **Approve** only where the organization intentionally delegates approval authority to deterministic policy or a human workflow.

The model itself does not become an approver because it is confident.

## Level 4 — Governed Execution

Characteristics:

Every executable action has:

- exact business object identity;
- exact operation/field scope;
- deterministic policy decision;
- required approval reference;
- fresh before-state/precondition;
- idempotency semantics where relevant;
- narrow typed execution tool;
- observable business postcondition;
- audit correlation;
- compensation/rollback rule;
- explicit failure handling.

Agent opportunity:

- invoke approved typed actions;
- perform bounded low-risk recovery;
- trigger deterministic reconciliation;
- execute pre-approved operational corrections.

Maximum sensible capability:

**Execute**, but only inside the state-change envelope.

The agent chooses among allowed operations. It does not invent new authority.

## Level 5 — Bounded Autonomous Operations

This level should be rare and domain-specific.

Characteristics:

- action set is small and reversible/low-risk;
- policy and authorization are deterministic;
- agent cannot broaden its own tools;
- hidden-case/adversarial evaluations exist;
- behavioral traces are observable;
- runtime/version regressions are evaluated;
- automatic circuit breakers exist;
- error budget / impact threshold is explicit;
- human escalation is immediate when invariants break;
- business outcome verification is reliable.

Examples that might eventually qualify:

- suppressing proven duplicate events;
- retrying a confirmed-not-applied idempotent operation;
- routing incidents based on deterministic classification plus agent explanation;
- triggering read-only or reversible reconciliation workflows.

Examples that generally should not be Level 5 merely because the model is good:

- arbitrary master-data changes;
- credit decisions;
- unrestricted order/delivery release;
- autonomous BP/customer/vendor merge;
- generic SAP GUI/RFC mutation.

## Capability gate matrix

| Readiness capability | L0 | L1 | L2 | L3 | L4 | L5 |
|---|:---:|:---:|:---:|:---:|:---:|:---:|
| Observable state | △ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Canonical identity | — | △ | ✓ | ✓ | ✓ | ✓ |
| Explicit authority | — | △ | ✓ | ✓ | ✓ | ✓ |
| Integration failure semantics | — | △ | ✓ | ✓ | ✓ | ✓ |
| Provenance / freshness | — | △ | △ | ✓ | ✓ | ✓ |
| Deterministic policy | — | — | △ | ✓ | ✓ | ✓ |
| Scoped approval | — | — | — | ✓ | ✓ | ✓ |
| Typed write surface | — | — | — | — | ✓ | ✓ |
| Postcondition verification | — | △ | ✓ | ✓ | ✓ | ✓ |
| Idempotency / stale-state protection | — | — | △ | ✓ | ✓ | ✓ |
| Adversarial/runtime evals | — | — | — | △ | ✓ | ✓ |
| Behavioral trace assurance | — | — | — | △ | △ | ✓ |
| Circuit breaker / autonomous limit | — | — | — | — | △ | ✓ |

`✓` expected, `△` partial/emerging, `—` not sufficient.

## Readiness assessment questions

Before moving one level higher, ask:

### Identity

- Can the system prove which business object the action refers to?
- Can mapping change over time?
- Is event-time identity recoverable?

### Authority

- Who owns the value/action?
- Is authority object-, attribute-, organization-, or time-specific?
- Can the architecture distinguish data location from authority?

### Evidence

- What proves current state?
- How fresh must evidence be?
- What happens when sources disagree?

### Policy

- Which rules are deterministic?
- Which exceptions require human authority?
- Can policy change after planning?

### Execution

- Is the tool typed and narrow?
- Can it affect only the approved object/operation?
- Is retry safe?

### Outcome

- What business postcondition defines success?
- Can success be observed independently of the write call?

### Recovery

- What happens if execution succeeds technically but fails the business postcondition?
- Is compensation separately governed?

### Assurance

- Are negative/adversarial cases evaluated?
- Can a runtime upgrade be compared by failure signature?
- Can unsafe intermediate behavior be observed?

## Organizational interpretation

The ladder is intentionally not a vendor maturity score.

One enterprise may be Level 4 for a narrow integration retry operation and Level 1 for customer master-data governance.

Readiness belongs to a **business capability + operation + scope**, not to “the company” or “the AI platform.”

A useful statement is:

> We are ready for governed execution of operation X on object scope Y under policy Z.

A weak statement is:

> We are Level 4 in agentic AI.

## The practical rule

Do not ask the agent to compensate for missing enterprise architecture.

If identity, authority, evidence, policy or recovery is unclear, improving the model is usually the wrong next step.

Improve the system around the model first.
