# Next Research Agenda

The v0.2 baseline now has an executable benchmark, machine-readable evidence/write contracts, risk taxonomy, source-backed ecosystem research, CI, and a minimal stateful simulator.

The next work should increase **scenario depth and external evidence**.

## P1 — Expand SAO-Bench to 50 cases

Build focused packs rather than random prompts:

### Integration Operations

- out-of-order messages;
- duplicate delivery;
- old-success-vs-new-change causality;
- target processing success but wrong business state;
- safe retry vs replay risk;
- identity/mapping change between messages.

### Master Data / MDG

- competing source-of-truth claims;
- ambiguous BP/customer/vendor identity;
- value mapping drift;
- governed-attribute write approval;
- source update after approval;
- duplicate candidate resolution.

### O2C / P2P

- deterministic incompletion vs generic diagnosis;
- block release with stale state;
- partner/master-data dependency;
- credit/approval dependency;
- supplier/customer exception routing.

### Security / Agent Runtime

- prompt injection in tool output;
- poisoned memory;
- tool scope escalation;
- inter-agent message trust;
- MCP authorization/scope mismatch;
- cascading action after partial failure.

## P1 — Grow the stateful simulator

Add:

- event/message ledger;
- canonical identity registry;
- deterministic fault injection;
- policy changes at runtime;
- message retry/idempotency;
- concurrent state changes;
- compensation flow;
- audit export.

The simulator should remain deliberately smaller than an ERP. It models enterprise control failures, not SAP functionality.

## P1 — Generated benchmark variants

Public cases are easy to memorize. Create deterministic generators that vary:

- object IDs;
- timestamps;
- order of evidence;
- missing fields;
- authority assignments;
- stale versions;
- untrusted injected text.

This enables stronger evaluation without hiding a private dataset.

## P2 — Runtime adapters

Build thin proof adapters for at least two runtimes. Good candidates:

- LangGraph or Pydantic AI as an open pro-code baseline;
- n8n as an orchestration baseline;
- Joule Studio when a suitable public/test environment is available.

Adapters should emit SAO decisions; they should not fork the benchmark.

## P2 — Conformance profiles

Define minimum requirements for:

- `SAO-Diagnostic`;
- `SAO-Approval`;
- `SAO-Write-Safe`;
- `SAO-Auditable`;
- `SAO-Adversarial`.

## P2 — External review

Seek concrete critique from:

- SAP/BTP/Joule practitioners;
- SAP AMS/MDG/integration leads;
- enterprise architects;
- MCP implementers;
- agent-security practitioners.

Track disagreements as cases or contract changes rather than collecting endorsements.

## Research rule

New research should answer a design question and change an artifact. Avoid link catalogs without a decision consequence.
