# The Architect's Decision Spine

A serious enterprise architecture is not a diagram of boxes. It is a chain of decisions that remains defensible when the landscape changes, an interface fails, a business owner asks for an exception, or an agent proposes a shortcut.

SAO uses the following decision spine to keep architecture work grounded in business responsibility rather than technology fashion.

## 1. What business truth are we protecting?

Start with the business invariant, not the product.

Examples:

- a customer must not be shipped to while a governed block is active;
- the same business event must not be applied twice;
- a payment-term change requires the correct business authority;
- a target record must not be overwritten from a stale source snapshot;
- a delivery block is not considered released until the business postcondition is observed.

An architecture decision is weak if it cannot say which business truth would be violated when the design fails.

## 2. Which system owns that truth?

Separate three concepts that are often collapsed into one:

- **system of record** — where the operational state is persisted;
- **business authority** — who is allowed to decide the value or action;
- **distribution authority** — which system is allowed to publish the authoritative state to others.

They may be the same. They often are not.

For master data, ownership may be object-specific or attribute-specific. A customer name, tax classification, credit decision, partner assignment, and sales-area attribute can have different authorities even when they are displayed in one record.

The architecture must therefore answer:

- Who may create?
- Who may change?
- Who may delete or block?
- Who may approve?
- Who may distribute?
- What happens when two systems disagree?

`source of truth` is not a useful answer unless its scope is explicit.

## 3. Where should the logic live?

Use the narrowest place that can enforce the invariant without creating unnecessary coupling.

### Keep logic in the ERP/core when

- it is transactional and must be evaluated atomically with the business operation;
- latency cannot tolerate an external round trip;
- the rule belongs to the semantic integrity of the core object;
- the supported on-stack extension model is the cleanest option.

### Move logic side-by-side when

- it orchestrates across systems;
- it needs independent lifecycle/scaling;
- it is experimental or AI-heavy;
- it aggregates context from multiple systems;
- keeping it outside the core improves upgradeability and isolation.

### Keep logic deterministic when

- the rule can be expressed exactly;
- authorization or policy has a definitive result;
- sequence, schema, state-transition, or idempotency rules are known.

### Use agentic reasoning when

- evidence is incomplete or distributed;
- competing hypotheses need to be ranked;
- context must be interpreted rather than validated;
- a human-readable recommendation is useful.

The agent should sit between controls, not replace them.

## 4. What integration contract are we choosing?

Do not start with `API vs event vs IDoc`. Start with the business interaction.

Ask:

- Is the caller waiting for a business answer now?
- Is the event a fact that already happened?
- Must consumers be decoupled?
- Is ordering material?
- Can delivery be duplicated?
- Can the operation be retried safely?
- What proves business completion?
- Who owns recovery?

A synchronous API, asynchronous event, message, and batch file have different failure semantics. Treating them as interchangeable transport choices produces operational debt.

See [`INTEGRATION-CONTRACT.md`](INTEGRATION-CONTRACT.md).

## 5. What happens when the happy path stops?

Every material design should contain its failure design before go-live.

At minimum define:

- timeout semantics;
- retry/idempotency behavior;
- duplicate handling;
- ordering assumptions;
- poison-message handling;
- stale-state detection;
- reconciliation;
- manual recovery;
- compensation/rollback;
- escalation ownership.

If the architecture only describes how a transaction succeeds, operations will discover the real architecture after the first incident.

## 6. How do we know the business outcome happened?

Transport success is not business success.

Examples:

- HTTP `200` can contain a business rejection;
- an IDoc can be technically processed while downstream business state is still wrong;
- middleware can deliver a payload to the wrong identity mapping;
- a write API can succeed while the expected business postcondition remains false.

Every important state-changing path therefore needs:

1. execution evidence;
2. business postcondition;
3. correlation identity;
4. audit record;
5. recovery path when verification fails.

This is where observability becomes architecture rather than monitoring.

## 7. What changes at cutover?

A migration or cutover is a temporary architecture with different authority, timing, and recovery rules.

For the cutover window define:

- old and new systems of record;
- freeze points;
- last accepted delta;
- identity/mapping version;
- in-flight messages;
- duplicate/replay policy;
- reconciliation set;
- rollback threshold;
- who can authorize an exception.

A design that is safe in steady state may be unsafe during cutover because authority and causality are moving targets.

See [`CUTOVER-RECOVERY.md`](CUTOVER-RECOVERY.md).

## 8. Which evidence makes the decision reviewable?

Architecture decisions should be inspectable later.

For every material decision preserve:

- business invariant;
- scope;
- alternatives considered;
- chosen boundary;
- operational consequence;
- failure mode;
- security/authorization consequence;
- migration consequence;
- evidence/source;
- reversal trigger.

A good ADR does not merely explain why option A won. It explains what future evidence would justify replacing option A.

## 9. What capability may an agent actually receive?

Never describe an agent as simply having `SAP access`.

Use capability classes:

```text
READ -> RECOMMEND -> APPROVE -> EXECUTE
```

Then bind capability to:

- object scope;
- field/operation scope;
- identity context;
- policy version;
- approval scope;
- current before-state;
- idempotency semantics;
- postcondition;
- audit/rollback requirements.

The more material the business impact, the narrower the execution surface should become.

## 10. The architecture review question

The final question is deliberately uncomfortable:

> If this component, mapping, message, policy, human approval, or agent is wrong, what is the first control that prevents incorrect enterprise state?

If the answer is “someone will notice,” the architecture is relying on hope.

## Compact decision record

For a design review, SAO recommends this one-page skeleton:

```yaml
business_invariant: ""
business_owner: ""
system_of_record: ""
data_or_action_authority: ""
integration_style: sync_api | async_event | message | batch | none
identity_contract: ""
policy_boundary: ""
agent_capability: read | recommend | approve | execute | none
failure_semantics: ""
recovery_owner: ""
postcondition: ""
cutover_impact: ""
observability_evidence: []
reversal_trigger: ""
```

The technology stack comes after these decisions, not before them.
