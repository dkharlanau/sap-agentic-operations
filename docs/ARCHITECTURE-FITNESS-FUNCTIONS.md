# Architecture Fitness Functions

Architecture principles become useful when they can fail a build, block a review, or force an explicit exception.

SAO therefore treats selected enterprise-architecture expectations as **fitness functions**: small deterministic checks that continuously test whether an architecture context still contains the controls it claims to rely on.

The goal is not to automate architecture judgment. The goal is to automate the boring part of noticing when important context disappeared.

## Why this matters

A slide can still look correct after:

- an integration loses its recovery owner;
- a mapping authority changes;
- an async interface has no idempotency rule;
- a business invariant is no longer linked to a control;
- an agent is given execute capability without an explicit gate;
- a cutover plan changes phase but keeps no delta watermark.

Machine-readable context lets us detect those structural regressions.

## Current fitness checks

Run:

```bash
python scripts/check_enterprise_context.py \
  examples/enterprise-context/customer-replication.json \
  --strict
```

The checker validates architectural semantics such as:

### Identity and authority

- object authority references a known system;
- system-specific identities reference known systems;
- missing authority is surfaced as a warning.

### Integration completeness

- producer and consumer are real systems in the context;
- a business postcondition exists;
- recovery ownership exists;
- async/message flows state correlation semantics;
- async/message flows state ordering semantics;
- async/message flows state idempotency semantics.

### Business invariant protection

- each invariant should be linked to at least one explicit control;
- dangling relations fail validation.

### Agent boundary

- execute capability requires an explicit execution gate;
- elevated capability should name what the agent may not decide;
- agent evidence references must exist.

### Cutover readiness

For non-steady-state phases, missing items are surfaced:

- authority transition;
- delta watermark;
- mapping version;
- reconciliation definition.

## Error vs warning

An **error** means the context is internally inconsistent — for example, authority references a system that does not exist.

A **warning** means the architecture may be intentionally incomplete, but someone should make that decision consciously — for example, an integration with no stated business postcondition.

Use `--strict` when a context is expected to be review/release ready.

## Fitness functions are not architecture scoring

SAO deliberately does not produce an opaque `architecture quality = 87%` score.

Architecture quality is contextual. A batch interface can be excellent. A side-by-side extension can be wrong. An event-driven design can be unnecessary. A human approval can be either critical control or pointless friction.

Fitness functions should therefore answer specific questions:

- Is the claimed authority resolvable?
- Is recovery ownership explicit?
- Is a state-changing path verifiable?
- Is the agent boundary explicit?
- Is cutover causality defined?

They should not pretend to replace an architect.

## Future fitness functions

High-value additions include:

- extension placement policy against a declared clean-core strategy;
- synchronous coupling / availability-chain analysis;
- critical integration without reconciliation evidence;
- authority conflicts across overlapping scopes;
- undocumented manual recovery dependency;
- exception without expiry;
- business invariant with no acceptance/eval case;
- state-changing agent tool with no write-envelope contract;
- event flow with no replay/deduplication strategy;
- architecture decision with no reversal trigger.

## Architectural principle

> Automate structural discipline. Keep judgment explicit.

That combination is more useful than either extreme: architecture by slide deck or architecture by static linter.
