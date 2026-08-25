# SAO-Bench

**SAO-Bench** is a small framework-agnostic benchmark for enterprise-agent control decisions.

It is intentionally different from benchmarks that ask whether a model can answer SAP questions. The benchmark asks whether an agent can stay inside safe operational boundaries when evidence, identity, authority, memory, tools, and enterprise state are imperfect.

## Unit of evaluation

One case contains:

```text
synthetic enterprise state
        +
control problem
        +
expected safe decision
        +
forbidden actions
```

An implementation emits a structured decision. The deterministic evaluator checks the control invariants.

## Current dimensions

| Dimension | Example failure |
|---|---|
| Identity | compares a customer with the wrong target BP |
| Authority | invents which system owns an attribute |
| Temporal reasoning | treats an old successful IDoc as evidence for a newer change |
| Deterministic rules | produces generic hypotheses despite a known incompletion failure |
| Evidence integrity | follows an instruction embedded in tool output |
| Memory safety | reuses a historical fix despite contradictory current state |
| Approval | executes a governed change without approval |
| State freshness | uses an approval after the object changed |
| Least capability | falls back to a generic admin tool after a typed tool fails |
| Verification | treats HTTP/API success as business success |
| Provenance | reports a diagnosis with no traceable evidence refs |

## Metrics

The evaluator reports:

- overall pass rate;
- pass rate by R0–R4 business-risk tier;
- pass rate by T1–T10 threat class;
- case-level failed invariants.

A future leaderboard should never collapse these dimensions into a single marketing number without exposing the breakdown.

## Benchmark philosophy

### Restraint is a capability

A correct `insufficient_evidence`, `approval_required`, or `policy_blocked` result can be more valuable than a confident automated action.

### Control decisions are deterministic where possible

The v0.2 evaluator does not use an LLM judge for policy or security invariants. Exact structured markers make the safety contract reproducible.

### SAP-shaped, not SAP-dependent

Cases use enterprise patterns familiar from SAP operations—IDoc flow, governed master data, business partner identity, order blocking—but remain synthetic and runnable without SAP software.

### Framework-neutral

The producer of prediction JSONL can be:

- Joule Studio / Joule Agent;
- LangGraph;
- Pydantic AI;
- LlamaIndex;
- n8n;
- a custom orchestrator;
- a plain LLM call with deterministic surrounding code.

## Road to a serious benchmark

### v0.2 — deterministic control benchmark

- 15+ cases
- executable evaluator
- R-tier and T-class breakdown
- CI self-test

### v0.3 — scenario packs

Grow to 50–100 cases grouped by:

- integration / IDoc / API operations;
- master data / MDG / BP identity;
- O2C / P2P operational decisions;
- authorization and approval;
- memory and retrieval safety;
- multi-agent / MCP trust boundaries;
- write verification and compensation.

### v0.4 — stateful simulator

Agents operate against a synthetic state machine instead of a static prompt. This enables tests for stale state, retries, idempotency, race conditions, policy transitions, and postconditions.

### v0.5 — runtime adapters

Provide small adapters that let common agent runtimes emit the same decision contract, so differences in control behavior can be compared without changing the benchmark.

## Anti-gaming rule

The benchmark should evolve with hidden or generated variants before it is used for comparative claims. The public reference predictions exist to prove the evaluator works, not to demonstrate agent intelligence.
