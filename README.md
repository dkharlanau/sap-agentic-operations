# SAP Agentic Operations (SAO)

[![SAO benchmark](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/evals.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/evals.yml)

**An executable reference lab for agents that reason around SAP and enterprise systems of record.**

Maintained by **Dzmitryi Kharlanau** — SAP Transformation · Enterprise Operations · Agentic AI.

Status: **experimental v0.2-dev**.

Most agent demos prove that an LLM can call a tool. SAO asks a harder question:

> **Can we prove that an agent knows when it may read, reason, request approval, execute, abstain, and verify a business outcome?**

The project uses SAP-shaped synthetic operations as a proving ground for enterprise-agent control: identity, evidence, source-of-truth authority, deterministic rules, authorization, tool scope, approvals, stale state, idempotency, postconditions, provenance, rollback, and adversarial inputs.

No SAP tenant is required. No client data belongs here.

## Why this project now

The SAP ecosystem itself is moving toward a world of Joule Agents, Joule Studio, MCP tools, managed agent runtimes, and SAP AI Agent Hub governance. The durable problem is therefore not another agent framework. It is the control boundary between probabilistic reasoning and mission-critical enterprise state.

See the source-backed snapshot: [`research/state-of-practice-2026-08.md`](research/state-of-practice-2026-08.md).

SAO is designed to sit across implementations rather than compete with them:

```text
 Joule Studio / LangGraph / Pydantic AI / n8n / custom agent
                              |
                              v
                     SAO Decision Contract
                              |
        +----------+----------+----------+----------+
        | identity | evidence | policy   | risk     |
        +----------+----------+----------+----------+
                              |
                              v
                    State-Change Envelope
                              |
                              v
                    MCP / Skill / API / Tool
                              |
                              v
                    SAP / system of record
                              |
                              v
                       Verify + Audit
```

## Four project surfaces

### 1. SAO Control Plane

A vendor-neutral architecture that separates:

- identity;
- evidence and provenance;
- deterministic policy;
- probabilistic reasoning;
- capability level;
- approval;
- execution;
- postcondition verification.

Start with [`docs/CONTROL-PLANE.md`](docs/CONTROL-PLANE.md).

### 2. SAO-Bench

An executable benchmark for enterprise control decisions.

Current cases test whether an implementation:

- refuses cross-system comparison on unresolved identity;
- recognizes that an old successful message does not prove a newer change replicated;
- distinguishes transport success from business-state success;
- refuses to invent the source of truth for master data;
- does not resolve ambiguous BP identity from similarity alone;
- follows deterministic O2C evidence instead of generating generic root-cause lists;
- ignores instructions embedded in untrusted tool output;
- refuses stale operational memory;
- requires approval for governed writes;
- invalidates approval when the before-state changes;
- refuses capability escalation after a typed tool fails;
- verifies business postconditions after a write;
- preserves evidence references for auditability.

Run the self-test:

```bash
python scripts/evaluate.py --predictions evals/predictions.reference.jsonl
```

The reference predictions prove the harness, not model intelligence. See [`docs/BENCHMARK.md`](docs/BENCHMARK.md) and [`evals/README.md`](evals/README.md).

### 3. Synthetic Enterprise Simulator

SAO includes a small stateful sandbox rather than pretending to emulate S/4HANA.

It currently models a synthetic sales-order state change and tests:

- missing approval → reject;
- stale before-state → reject;
- exact approved operation → execute;
- postcondition → verify;
- duplicate idempotency key → do not mutate twice.

Run:

```bash
python -m unittest discover -s tests -v
```

The simulator is the path toward reproducible race-condition, stale-state, retry, compensation, and multi-agent experiments without a real ERP landscape.

### 4. Machine-readable contracts

The project defines schemas for:

- [`schemas/decision.schema.json`](schemas/decision.schema.json) — agent decision output;
- [`schemas/evidence.schema.json`](schemas/evidence.schema.json) — evidence/provenance envelope;
- [`schemas/write-envelope.schema.json`](schemas/write-envelope.schema.json) — state-change safety envelope.

Human-readable contracts explain the design:

- [`contracts/capability-model.md`](contracts/capability-model.md)
- [`contracts/evidence-envelope.md`](contracts/evidence-envelope.md)
- [`contracts/write-safety-envelope.md`](contracts/write-safety-envelope.md)

## Core operating model

```text
READ -> RECOMMEND -> APPROVE -> EXECUTE
```

These are different capability classes, not steps an agent may silently escalate through.

| Capability | Meaning | Default posture |
|---|---|---|
| **Read** | retrieve approved evidence | automatable with access controls |
| **Recommend** | correlate, diagnose, explain, propose | where agentic reasoning adds most value |
| **Approve** | authorize a specific state change | human or deterministic policy boundary |
| **Execute** | mutate enterprise state | narrow typed tool + safety envelope + verification |

## Risk model

SAO separates business impact from agentic threat class.

Business tiers:

- **R0** informational
- **R1** diagnostic
- **R2** reversible operational change
- **R3** material business-state change
- **R4** high-impact / irreversible / regulated

Threat classes currently cover goal hijacking, tool misuse, identity/privilege abuse, memory poisoning, insecure communication, cascading failure, trust exploitation, stale-state execution, verification failure, and provenance loss.

See [`docs/RISK-MODEL.md`](docs/RISK-MODEL.md).

## Design invariants

1. **Identity before comparison.**
2. **Evidence before diagnosis.**
3. **Deterministic rules before probabilistic reasoning.**
4. **Recommendation is not authorization.**
5. **Authorization is not execution.**
6. **Every write is bound to exact current state.**
7. **Model confidence never grants capability.**
8. **Evidence channels never become instruction channels.**
9. **`insufficient_evidence` and `policy_blocked` are successful safe outcomes.**
10. **API success is not business success until postconditions are verified.**
11. **A tool failure never authorizes a broader tool.**
12. **A write without audit and compensation/rollback thinking is incomplete.**

## Initial SAP-shaped scenario packs

- [`scenarios/001-idoc-interface-triage.md`](scenarios/001-idoc-interface-triage.md)
- [`scenarios/002-mdg-master-data-discrepancy.md`](scenarios/002-mdg-master-data-discrepancy.md)
- [`scenarios/003-o2c-order-block.md`](scenarios/003-o2c-order-block.md)

These are synthetic abstractions of enterprise support problems. They are not reproductions of a client landscape and do not replace SAP documentation.

## How this differs from an SAP agent demo

SAO intentionally does **not** try to prove that an LLM can call RFC, OData, GUI automation, or a generic MCP server.

The project is stronger when it can answer questions such as:

- Which identity did the agent actually act on?
- Which system was authoritative for this attribute?
- Which observations were current at decision time?
- Was a tool response treated as evidence or as an instruction?
- Which policy granted capability?
- Was approval bound to the exact before-state?
- What happens if state changes between approval and execution?
- How is duplicate execution prevented?
- What business postcondition proves success?
- What evidence lets an auditor reconstruct the decision?

That is the layer the repository is intended to make executable.

## Repository map

- [`docs/`](docs/) — control plane, risk model, benchmark, SAP ecosystem mapping
- [`architectures/`](architectures/) — reference system boundaries
- [`contracts/`](contracts/) — capability, evidence, approval and execution contracts
- [`schemas/`](schemas/) — machine-readable contracts
- [`patterns/`](patterns/) — reusable operating patterns
- [`scenarios/`](scenarios/) — synthetic SAP/enterprise cases
- [`evals/`](evals/) — SAO-Bench cases and reference outputs
- [`scripts/evaluate.py`](scripts/evaluate.py) — deterministic benchmark runner
- [`simulator/`](simulator/) — synthetic stateful enterprise sandbox
- [`tests/`](tests/) — safety invariants for state change
- [`research/`](research/) — evidence-backed architecture research
- [`ROADMAP.md`](ROADMAP.md) — path toward scenario packs, runtime adapters and conformance profiles
- [`AGENTS.md`](AGENTS.md) — engineering constitution for future agent-assisted changes

## Current direction

The next meaningful milestone is not more prose. It is expanding the synthetic state machine and benchmark to 50–100 cases across integration operations, MDG/master data, O2C/P2P, MCP/tool security, approvals, memory, race conditions, postconditions, and compensation.

Then small adapters can demonstrate the same SAO contract from Joule Studio, LangGraph, n8n, Pydantic AI or custom orchestration without coupling the benchmark to any framework.

See [`ROADMAP.md`](ROADMAP.md).

## SAP ecosystem mapping

[`docs/SAP-MAPPING.md`](docs/SAP-MAPPING.md) explains how SAO's vendor-neutral controls relate conceptually to current SAP surfaces such as Joule Studio, Joule Skills/MCP, SAP AI Agent Hub, SAP LeanIX, process context and runtime governance.

SAO is independent work and is not an official SAP project.

## Author

**Dzmitryi Kharlanau**  
SAP Transformation · Enterprise Operations · Agentic AI

- Professional site: https://dkharlanau.github.io/
- LinkedIn: https://www.linkedin.com/in/dkharlanau/
- Agent-Ready Web Profile: https://github.com/dkharlanau/agent-ready-web-profile
- Public datasets: https://github.com/dkharlanau/dkharlanau-datasets

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
