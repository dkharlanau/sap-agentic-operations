# Next Research Agenda

The v0.1 baseline is intentionally small. The next work should increase evidence and evaluability rather than add generic agent features.

## P1 — Executable eval harness

Build a tiny local evaluator that reads `evals/cases.jsonl` and checks structured agent decisions against required and forbidden behaviors.

Success means the repository can measure whether an implementation:

- abstains when evidence is missing;
- refuses unauthorized execution;
- resolves identity before comparison;
- distinguishes deterministic failures from hypotheses;
- preserves required evidence in its output.

## P1 — Evidence contracts

Define a machine-readable evidence envelope with fields such as:

- source system / source type;
- canonical object identity;
- system-specific identity;
- observed timestamp;
- retrieved timestamp;
- evidence type;
- content hash or stable reference;
- sensitivity classification;
- provenance chain.

## P1 — Approval contract

Add an approval token/record model that binds authorization to an exact object, operation, before-state, expected after-state, approver, and expiry.

## P2 — Additional synthetic scenarios

Candidates:

- P2P supplier/master-data inconsistency;
- credit or delivery hold with conflicting evidence;
- duplicate business-partner candidate resolution;
- cross-system mapping drift;
- recurring incident memory and recommendation reuse;
- post-execution verification and rollback failure.

## P2 — Source-backed research

Track current work on:

- enterprise-agent authorization and policy enforcement;
- MCP/tool security and least-capability patterns;
- agent evaluation for state-changing workflows;
- provenance and auditability;
- human approval patterns;
- enterprise observability for agent decisions.

Research should change an architecture, contract, scenario, or eval. Avoid collecting links without a decision consequence.
