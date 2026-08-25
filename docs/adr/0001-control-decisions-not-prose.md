# ADR-0001 — Benchmark Enterprise Control Decisions, Not Prose Quality

- Status: Accepted
- Date: 2026-08-25

## Context

Enterprise agents can produce fluent explanations while still making unsafe operational decisions. A benchmark dominated by style, semantic similarity, or generic answer quality can therefore reward the wrong behavior.

## Decision

SAO-Bench scores structured control outcomes first:

- decision class;
- execution gating;
- required/forbidden actions;
- identity/evidence/policy invariants;
- postcondition and audit behavior;
- risk/threat failure signature.

Natural-language explanation quality may be added later as a secondary metric, never as the authority for deterministic safety controls.

## Rejected alternatives

- LLM-as-judge as the primary evaluator.
- Generic helpfulness/correctness scoring.
- A single opaque safety score without failure classes.

## Consequences

Positive:

- deterministic and auditable evaluation;
- portable comparison across runtimes;
- unsafe autonomy can be penalized explicitly.

Cost:

- exact structured cases require careful authoring;
- some valid semantic reasoning may not receive credit until semantic grading is added.

## Reversal criteria

Revisit only if a replacement preserves deterministic scoring for policy, identity, capability, approval and state-change invariants while measurably improving evaluation validity.
