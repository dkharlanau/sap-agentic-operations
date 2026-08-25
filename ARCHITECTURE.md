# SAP Agentic Operations — Architecture

SAO is built around one premise:

> **An enterprise agent is only as trustworthy as the architecture that defines identity, authority, evidence, integration semantics, state-change controls, and recovery around it.**

The model is not the architecture.

The architecture is the chain that connects business intent to observable business state.

## Decision spine

```text
Business intent
   -> business invariant
      -> scope / owner
         -> canonical identity
            -> system & data authority
               -> extension / integration boundary
                  -> deterministic controls
                     -> evidence / observability
                        -> agent capability
                           -> approval / execution
                              -> business postcondition
                                 -> recovery / compensation
```

Every important SAO artifact exists somewhere on this chain.

## Read SAO as an architect

Start with:

- [`docs/ARCHITECT-DECISION-SPINE.md`](docs/ARCHITECT-DECISION-SPINE.md) — architecture decisions before technology choices.
- [`docs/INTEGRATION-CONTRACT.md`](docs/INTEGRATION-CONTRACT.md) — identity, causality, ordering, retry, replay, acknowledgement and recovery.
- [`docs/AGENT-IDENTITY-AUTHORIZATION.md`](docs/AGENT-IDENTITY-AUTHORIZATION.md) — human/delegated/tool/business authority boundaries.
- [`docs/SAP-AGENT-TOOL-CONTRACTS.md`](docs/SAP-AGENT-TOOL-CONTRACTS.md) — why typed business tools are safer than generic SAP execution surfaces.
- [`docs/CUTOVER-RECOVERY.md`](docs/CUTOVER-RECOVERY.md) — migration/cutover as a temporary architecture.
- [`docs/ARCHITECTURE-FITNESS-FUNCTIONS.md`](docs/ARCHITECTURE-FITNESS-FUNCTIONS.md) — architecture-as-code checks.

## Read SAO as a consultant / AMS lead

Start with:

- [`docs/CONSULTING-REVIEW-CARDS.md`](docs/CONSULTING-REVIEW-CARDS.md) — architecture/discovery workshop prompts.
- [`docs/SAP-OPERATIONS-FAILURE-ATLAS.md`](docs/SAP-OPERATIONS-FAILURE-ATLAS.md) — 25 recurring enterprise failure classes with evidence and safe recovery logic.
- [`docs/AGENTIC-AMS-OPERATING-MODEL.md`](docs/AGENTIC-AMS-OPERATING-MODEL.md) — detect → evidence → deterministic triage → agent reasoning → governed recovery → verification → learning.
- [`docs/SAP-AGENTIC-OPPORTUNITY-MAP.md`](docs/SAP-AGENTIC-OPPORTUNITY-MAP.md) — where agents create SAP value and where they create architectural risk.

## Read SAO as a system analyst

Start with:

- [`docs/BUSINESS-TRACEABILITY.md`](docs/BUSINESS-TRACEABILITY.md) — requirement → invariant → contract → control → evidence → test → owner.
- [`schemas/enterprise-context.schema.json`](schemas/enterprise-context.schema.json) — machine-readable enterprise context.
- [`examples/enterprise-context/customer-replication.json`](examples/enterprise-context/customer-replication.json) — synthetic example linking process, authority, systems, integration, evidence and agent boundary.
- [`docs/ENTERPRISE-AGENT-READINESS-LADDER.md`](docs/ENTERPRISE-AGENT-READINESS-LADDER.md) — capability is earned through architecture readiness, not declared as an AI maturity score.

## Architecture-as-code

The Enterprise Context Graph is intentionally small enough to be reviewable and machine-readable:

```text
process
  -> invariant
  -> business object
  -> authority
  -> systems
  -> integration
  -> controls
  -> evidence
  -> agent boundary
  -> cutover state
```

Validate the example:

```bash
python sao.py context-check \
  examples/enterprise-context/customer-replication.json \
  --strict
```

The full CI suite treats this as an architecture fitness function.

## Anti-patterns

SAO gives recurring design failures memorable names:

- **Green Interface Fallacy** — transport success mistaken for business success.
- **Source of Truth by Habit** — authority inferred from historic data location.
- **Retry Button Architecture** — all failures treated as retryable.
- **Similarity Is Identity** — fuzzy match mistaken for canonical business identity.
- **Clean Core Cargo Cult** — placement chosen by slogan rather than invariant/trade-off.
- **Prompt as Business Rule** — probabilistic instruction used as deterministic policy.
- **Agent as Missing Integration Layer** — AI used to hide undocumented enterprise contracts.
- **Approval as Boolean** — approval detached from object, operation, state and expiry.
- **Architecture by Screenshot** — landscape documented without semantics, failure or recovery.

See [`docs/ENTERPRISE-ANTI-PATTERNS.md`](docs/ENTERPRISE-ANTI-PATTERNS.md).

## Current SAP architecture alignment

SAO's current architecture lens is intentionally aligned with current SAP guidance without claiming official endorsement:

- choose on-stack vs side-by-side extensibility by use case and required capability;
- treat EDA as one integration style inside a holistic integration architecture;
- make data ownership/authority explicit;
- make architecture metadata machine-readable enough to support governance and evidence.

Source-backed snapshot: [`research/sap-architecture-lens-2026-08.md`](research/sap-architecture-lens-2026-08.md).

## Architectural quality bar

A SAO design is incomplete if it cannot answer:

1. What business truth is at risk?
2. Who owns that truth?
3. Which system persists it?
4. Which identity refers to it across systems?
5. How does state move?
6. What are the failure semantics?
7. What evidence proves success?
8. Who owns recovery?
9. What may the agent infer?
10. What may the agent never decide?
11. What exact gate permits state change?
12. What happens when the postcondition fails?
13. What changes during cutover?
14. What evidence would make us reverse the architecture decision?

If those questions have good answers, the choice of model becomes much less mysterious.
