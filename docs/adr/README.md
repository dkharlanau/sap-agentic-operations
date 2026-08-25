# SAO Architecture Decision Records

Architecture Decision Records preserve the decisions that make SAP Agentic Operations distinct from a generic agent framework or SAP connector.

Each ADR records context, decision, rejected alternatives, consequences, and explicit reversal criteria.

## Accepted decisions

- [ADR-0001 — Benchmark enterprise control decisions, not prose quality](0001-control-decisions-not-prose.md)
- [ADR-0002 — Separate probabilistic reasoning from deterministic policy and execution](0002-separate-reasoning-policy-execution.md)
- [ADR-0003 — Use synthetic SAP-shaped scenarios, not proprietary system emulation](0003-synthetic-enterprise-not-sap-emulator.md)
- [ADR-0004 — Require evidence and provenance for concrete decisions](0004-evidence-and-provenance.md)
- [ADR-0005 — Keep the decision contract runtime-neutral](0005-runtime-neutral-contract.md)
- [ADR-0006 — Treat state change as a separate governed risk class](0006-governed-state-change.md)

## Rule

A future change that contradicts an accepted ADR should either:

1. revise/supersede that ADR with explicit evidence; or
2. be rejected as architectural drift.
