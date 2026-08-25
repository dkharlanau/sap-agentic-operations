# Roadmap

SAP Agentic Operations should grow by increasing **evidence, adversarial coverage, and reproducibility** — not by accumulating generic agent features.

## v0.2 — Executable control benchmark

Status: current baseline.

- control-plane architecture;
- R0–R4 business-risk tiers;
- T1–T10 agentic threat classes;
- decision, evidence, and write-envelope schemas;
- 15 deterministic benchmark cases;
- framework-neutral JSONL evaluator;
- GitHub Actions self-test;
- stateful synthetic order-block simulator;
- write tests for approval, stale preconditions, idempotency, and postconditions;
- current SAP/MCP/OWASP research map.

## v0.3 — Enterprise scenario packs

Target: 50–100 cases with stronger SAP-shaped operational depth.

Packs:

1. **Integration Operations** — IDoc/API/middleware causality, retries, duplicates, out-of-order delivery, target processing, replay safety.
2. **Master Data & MDG** — source-of-truth ownership, BP/customer/vendor identity, stale target state, ambiguous duplicates, governed writes.
3. **O2C / P2P** — blocks, incompletion, credit/partner/master dependencies, exception routing, approval boundaries.
4. **Agent Security** — untrusted tool output, memory poisoning, scope escalation, MCP authorization boundaries, inter-agent trust.
5. **State Change** — approvals, stale versions, idempotency, postconditions, rollback and compensation.

Every pack should include both static cases and stateful simulator sequences.

## v0.4 — Synthetic Enterprise Operations Simulator

Move from isolated fixtures to a deterministic event-driven system:

- canonical business objects plus system-specific identities;
- event/message ledger;
- source/target timestamps;
- policy registry;
- narrow read/write tools;
- mutable state with versioning;
- deterministic fault injection;
- audit trail;
- postcondition and compensation engine.

Example experiments:

- a mapping changes between diagnosis and execution;
- a message succeeds at transport level but fails business postcondition;
- two agents race to update the same object;
- an approval becomes stale;
- memory recommends an obsolete recovery;
- an MCP tool returns injected instructions inside valid evidence.

## v0.5 — Runtime adapters

Provide thin adapters rather than framework forks:

```text
Joule Studio ----\
LangGraph --------> SAO decision JSON -> SAO-Bench
Pydantic AI ------/
n8n -------------/
Custom ----------/
```

Adapters should demonstrate how an implementation emits evidence references, decision classes, and write-envelope proposals.

## v0.6 — Conformance profiles

Define explicit profiles such as:

- `SAO-Diagnostic` — read/recommend only;
- `SAO-Approval` — supports approval-bound proposals;
- `SAO-Write-Safe` — state-change envelope + postcondition + idempotency;
- `SAO-Auditable` — full evidence/provenance decision record;
- `SAO-Adversarial` — passes minimum injection/memory/tool-misuse cases.

A conformance claim must name the profile and benchmark version.

## v0.7 — External evidence

Before calling SAO a standard or publishing comparative claims:

- at least three independent implementations;
- benchmark feedback from SAP/enterprise practitioners;
- documented false positives/negatives;
- generated/hidden case variants to reduce benchmark memorization;
- versioned compatibility policy;
- public release artifacts and citation DOI if useful.

## Long-term thesis

The interesting open problem is not whether agents can call enterprise APIs. It is whether organizations can **prove which agents are safe to trust with which business capabilities under which evidence and policy conditions**.

SAO should remain focused on making that question executable.
