# SAP Agentic Operations

**Reference architectures, safety patterns and evaluation scenarios for AI agents around SAP enterprise operations.**

Maintained by **Dzmitryi Kharlanau** — SAP Transformation · Enterprise Operations · Agentic AI.

This repository explores how AI agents can support SAP-heavy enterprise operations without treating an ERP system like a chatbot backend.

The focus is not on autonomous demos. It is on the difficult enterprise boundaries: identity, authorization, evidence, deterministic controls, human approval, observability, data quality, rollback, and knowing when an agent should abstain.

## Why this repository exists

Enterprise AI around SAP is not mainly a prompt-engineering problem.

A useful agent must operate inside a system of controls:

- business identity must be resolved before records are compared;
- evidence must be traceable across systems and messages;
- read, recommend, approve, and execute capabilities must remain distinct;
- deterministic validation should win when rules are known;
- uncertain reasoning should produce recommendations, not silent mutations;
- write operations need authorization, approval, auditability, and rollback;
- incomplete or contradictory evidence must lead to abstention or escalation.

This repository turns those constraints into reusable architectures, scenarios, contracts, and eval cases.

## Scope

- SAP AMS and incident diagnostics
- SAP SD/MM operational support patterns
- customer, vendor, business partner, master data, and MDG scenarios
- IDoc, API, middleware, and interface failures
- O2C and P2P investigation patterns
- cross-system identity resolution
- agent-to-tool and MCP-style boundaries
- deterministic vs agentic decision rules
- human approval and escalation
- evaluation, evidence, and abstention
- observability, auditability, and rollback
- operational memory for recurring enterprise incidents

## Non-goals

- no client data or production exports
- no credentials, internal URLs, ticket IDs, or proprietary configuration
- no instructions for bypassing SAP authorization
- no assumption that an LLM should directly mutate ERP state
- no generic multi-agent demo without an enterprise control problem
- no claim that AI should replace deterministic business rules

## Core principle

> Use agents where uncertainty requires reasoning; use deterministic controls where enterprise state requires guarantees.

## Capability model

The default operating model separates four levels:

| Level | Meaning | Default posture |
|---|---|---|
| **Read** | Retrieve approved evidence | Can be automated with access controls |
| **Recommend** | Diagnose, compare, propose next action | Agentic reasoning is useful here |
| **Approve** | Validate business impact and authorize change | Human or deterministic policy gate |
| **Execute** | Change enterprise state | Narrow tools, explicit authorization, audit and rollback |

See [`contracts/capability-model.md`](contracts/capability-model.md).

## Reference architecture

The baseline architecture keeps the LLM outside the system-of-record boundary:

```text
User / Operations
       |
       v
Agent / Orchestrator
       |
       +---- Evidence layer ----> logs / IDocs / APIs / master data views
       |
       +---- Deterministic controls ----> schemas / rules / policies / identity mapping
       |
       +---- Recommendation ----> diagnosis + evidence + confidence + proposed action
       |
       v
Approval boundary
       |
       v
Narrow execution tool
       |
       v
SAP / enterprise system of record
       |
       +---- audit event / result / rollback reference
```

The agent can reason broadly; its tools should remain narrow.

See [`architectures/reference-architecture.md`](architectures/reference-architecture.md).

## Initial scenarios

1. [`IDoc / interface failure triage`](scenarios/001-idoc-interface-triage.md) — diagnose without autonomous mutation.
2. [`MDG / master-data discrepancy`](scenarios/002-mdg-master-data-discrepancy.md) — resolve identity before comparing source and target state.
3. [`O2C order-block investigation`](scenarios/003-o2c-order-block.md) — separate deterministic checks from uncertain root-cause reasoning.

Each scenario defines evidence, allowed capabilities, failure modes, abstention criteria, and an expected decision path.

## Evaluation

`evals/cases.jsonl` contains small synthetic cases designed to test decisions rather than prose quality.

An implementation should be evaluated on questions such as:

- Did it retrieve enough evidence before diagnosing?
- Did it distinguish source identity from target identity?
- Did it avoid execution when authorization or evidence was missing?
- Did it route deterministic checks to deterministic logic?
- Did it cite contradictory evidence instead of hiding it?
- Did it abstain when the safe action was unclear?

## Repository map

- [`architectures/`](architectures/) — system boundaries and reference architectures
- [`contracts/`](contracts/) — capability, approval, evidence, and tool contracts
- [`patterns/`](patterns/) — reusable enterprise-agent operating patterns
- [`scenarios/`](scenarios/) — synthetic SAP / enterprise operational cases
- [`evals/`](evals/) — machine-readable evaluation cases
- [`research/`](research/) — source-backed research notes and evidence policy
- [`docs/`](docs/) — principles and terminology

## Design principles

1. **Evidence before action.** A diagnosis without evidence is a hypothesis.
2. **Identity before comparison.** Cross-system records must be resolved before state is compared.
3. **Deterministic before agentic.** Known rules belong in code, schemas, or policy engines.
4. **Least capability.** Give an agent the smallest tool surface needed for the task.
5. **Separate recommendation from execution.** Reasoning and mutation are different risk classes.
6. **Make abstention explicit.** `insufficient_evidence` is a valid result.
7. **Preserve provenance.** Every important conclusion should point back to observable evidence.
8. **Design for rollback.** A write path without a recovery path is incomplete.
9. **Audit the decision, not only the API call.** Preserve what evidence led to the action.
10. **Synthetic public examples only.** Enterprise learning must not leak enterprise data.

## Status

Early public reference project. The initial target is a small, high-quality set of patterns and evals rather than a broad framework.

## Author

**Dzmitryi Kharlanau**  
SAP Transformation · Enterprise Operations · Agentic AI

- Professional site: https://dkharlanau.github.io/
- LinkedIn: https://www.linkedin.com/in/dkharlanau/
- Agent-Ready Web Profile: https://github.com/dkharlanau/agent-ready-web-profile
- Public datasets: https://github.com/dkharlanau/dkharlanau-datasets

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
