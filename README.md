# SAP Agentic Operations (SAO)

[![SAO benchmark](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/evals.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/evals.yml)
[![SAO full suite](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml)

**An executable assurance lab for AI agents that reason around SAP and other enterprise systems of record.**

Maintained by **Dzmitryi Kharlanau** — SAP Transformation · Enterprise Operations · Agentic AI.

Status: **experimental SAO-Bench v0.3-dev**.

Most agent demos prove that an LLM can call a tool. SAO asks a harder question:

> **Can we prove that an agent knows when it may read, reason, request approval, execute, abstain, and verify a business outcome?**

SAO uses SAP-shaped synthetic operations to test enterprise-agent controls: identity, evidence, source-of-truth authority, deterministic policy, authorization, tool scope, approval, stale state, idempotency, postconditions, provenance, compensation, memory trust, and adversarial inputs.

No SAP tenant is required. No client data belongs here. The simulator does **not** emulate S/4HANA.

## Why this project exists

Enterprise agent platforms are rapidly adding orchestration, tools, MCP connectivity, managed runtimes, governance, observability, and agent inventories. Those capabilities do not by themselves prove that an agent behaves safely around mission-critical business state.

SAO therefore focuses on a narrower layer:

**pre-production assurance for enterprise-agent decisions and state changes.**

The project is designed to sit across implementations rather than compete with them:

```text
 Joule Studio / LangGraph / Pydantic AI / n8n / custom agent
                              |
                              v
                    Runtime Adapter Protocol
                              |
                              v
                     SAO Decision Contract
                              |
             +----------------+----------------+
             | identity | evidence | policy    |
             | risk     | approval | provenance|
             +----------------+----------------+
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

See the source-backed ecosystem snapshot in [`research/state-of-practice-2026-08.md`](research/state-of-practice-2026-08.md) and the conceptual SAP governance bridge in [`research/sap-agent-hub-bridge.md`](research/sap-agent-hub-bridge.md).

## What exists today

### 1. SAO Control Plane

A vendor-neutral control architecture separating:

- intent and scope;
- identity resolution;
- evidence and provenance;
- deterministic policy;
- probabilistic reasoning;
- decision/capability class;
- approval;
- typed execution;
- postcondition verification;
- audit and compensation.

Start with [`docs/CONTROL-PLANE.md`](docs/CONTROL-PLANE.md).

### 2. SAO-Bench — 51 enterprise-control cases

The current corpus contains **51 synthetic cases** across a core set and five domain packs:

| Pack | Cases | Examples |
|---|---:|---|
| Core | 15 | IDoc causality, MDG authority, O2C evidence, tool injection, stale memory, approvals |
| Integration Operations | 7 | duplicate/replay, out-of-order delivery, mapping drift, retry ambiguity, business acknowledgement |
| Master Data / MDG | 7 | attribute authority, duplicate ambiguity, governance workflow, mapping versions, scoped exceptions |
| Business Process | 7 | O2C/P2P blocks, partner dependencies, policy drift, urgency, multi-owner approval |
| Agent Security | 7 | memory poisoning, MCP scope escalation, inter-agent trust, confused deputy, retrieval injection |
| State Change | 8 | approval expiry, races, idempotency collision, postconditions, audit gaps, compensation |

Every case carries an R0–R4 impact tier and one or more T1–T10 agentic threat classes.

The benchmark tests **control decisions, not prose style**. It scores:

- decision class;
- execution gating;
- required findings and next actions;
- forbidden actions;
- evidence references;
- state-change envelope requirements;
- risk/threat/domain failure signatures.

Run the full self-test:

```bash
python scripts/validate_suite_contracts.py
python scripts/evaluate_suite.py --predictions reference --require-cases 50
```

The reference self-test should be 100%. It proves only that the corpus and evaluator agree; it is **not** an AI/model score.

See [`evals/README.md`](evals/README.md) and [`docs/BENCHMARK.md`](docs/BENCHMARK.md).

### 3. Deterministic control baselines

SAO includes deliberately simple no-model strategies to prove that the corpus distinguishes different operating behaviors.

A reproducible CI snapshot over 51 cases produced:

| Baseline | Decision-class accuracy | Execution-gate accuracy | Unsafe executions |
|---|---:|---:|---:|
| `guarded-rules` | 37.3% | 94.1% | 0 |
| `always-abstain` | 31.4% | 94.1% | 0 |
| `memory-biased` | 17.7% | 94.1% | 0 |
| `naive-auto-execute` | 5.9% | 5.9% | **48 / 51** |

This is a control-group result, not a leaderboard. It demonstrates three useful facts:

1. blanket refusal can be safe but operationally weak;
2. generic guardrails improve some decisions but cannot replace domain evidence/reasoning;
3. naive autonomy is catastrophically unsafe on this corpus.

The immutable snapshot is in [`baselines/results/20260825-0339db4.json`](baselines/results/20260825-0339db4.json). Baseline definitions are in [`baselines/`](baselines/).

### 4. Synthetic Enterprise Lab v0.3

The stateful simulator models enterprise control properties without reproducing SAP product internals.

It now supports:

- canonical identity registry and mapping versions;
- deterministic clock;
- policy registry and runtime policy changes;
- event/message ledger;
- delayed, dropped, and duplicated messages;
- identity drift between planning and delivery;
- scoped approvals and expiry;
- before-state/version binding;
- typed writes;
- idempotency and collision detection;
- business postcondition verification;
- failed-postcondition injection;
- audit export;
- governed compensation;
- trust-aware evidence and operational memory.

Examples of enforced behavior:

- missing approval → reject;
- changed identity mapping → quarantine or reject stale action;
- changed object version → reject stale approval;
- repeated idempotent request → no second mutation;
- same idempotency key + different operation → reject;
- technical write + failed business postcondition → failure, not success;
- rollback path exists + no rollback approval → do not compensate;
- untrusted ticket/tool content → never becomes control authority.

Run:

```bash
python -m unittest discover -s tests -p 'test_*.py'
```

See [`simulator/v03.py`](simulator/v03.py).

### 5. Machine-readable control contracts

Schemas:

- [`schemas/decision.schema.json`](schemas/decision.schema.json) — portable agent decision output;
- [`schemas/evidence.schema.json`](schemas/evidence.schema.json) — evidence/provenance envelope;
- [`schemas/write-envelope.schema.json`](schemas/write-envelope.schema.json) — governed state-change envelope;
- [`schemas/experiment.schema.json`](schemas/experiment.schema.json) — reproducible experiment metadata.

Human-readable contracts:

- [`contracts/capability-model.md`](contracts/capability-model.md)
- [`contracts/evidence-envelope.md`](contracts/evidence-envelope.md)
- [`contracts/write-safety-envelope.md`](contracts/write-safety-envelope.md)

The core capability model remains:

```text
READ -> RECOMMEND -> APPROVE -> EXECUTE
```

These are different capability classes, not permissions an agent may silently escalate through.

### 6. Runtime-neutral adapter protocol

Any runtime can participate if it receives a benchmark case **without its expected answer** and emits the neutral SAO Decision JSON contract.

Protocol runner:

```bash
python scripts/run_adapter.py \
  --output /tmp/predictions.jsonl \
  -- python adapters/guarded_rules.py

python scripts/evaluate_suite.py \
  --predictions /tmp/predictions.jsonl \
  --json
```

A generic HTTPS bridge is included for external services/webhooks:

```bash
export SAO_ADAPTER_URL=https://agent.example.com/sao
export SAO_ADAPTER_TOKEN=...

python scripts/run_adapter.py \
  --output /tmp/predictions.jsonl \
  -- python adapters/http_endpoint.py
```

This creates a path to Joule/custom services, n8n, LangGraph, Pydantic AI, MCP-based orchestrators, or another runtime without forking benchmark truth.

See [`adapters/README.md`](adapters/README.md).

### 7. Reproducible experiment and release evidence

Public SAO results are intended to be reproducible, not screenshots.

A runtime experiment can bind:

- exact SAO-Bench version and Git commit;
- corpus/evaluator hashes;
- runtime/framework version;
- model/provider version when known;
- agent configuration hash;
- tool/capability manifest hash;
- policy/conformance profile;
- raw predictions;
- deterministic report;
- simulator/fault profile when stateful.

See [`experiments/README.md`](experiments/README.md).

Benchmark releases also have an integrity-manifest generator:

```bash
python scripts/build_release_manifest.py \
  --version 0.3-dev \
  --output sao-release-manifest.json
```

The manifest SHA-256 hashes the corpus, schemas, and evaluator and binds them to the exact Git commit.

Versioning rules are defined in [`BENCHMARK_VERSIONING.md`](BENCHMARK_VERSIONING.md) and changes are tracked in [`CHANGELOG.md`](CHANGELOG.md).

## Risk model

SAO separates business impact from agentic failure class.

Business tiers:

- **R0** — informational;
- **R1** — diagnostic;
- **R2** — reversible operational change;
- **R3** — material business-state change;
- **R4** — high-impact / irreversible / regulated.

Threat classes T1–T10 cover:

- goal/instruction hijacking;
- excessive tool capability;
- identity and privilege abuse;
- memory/context poisoning;
- insecure agent/tool communication;
- cascading failure;
- trust exploitation;
- stale-state execution;
- verification failure;
- provenance loss.

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
12. **Compensation is a governed state change, not an automatic escape hatch.**
13. **Published experiment failures remain visible.**
14. **Benchmark truth cannot be customized per runtime.**

The accepted architectural decisions and reversal criteria are in [`docs/adr/`](docs/adr/).

## Continuous assurance

Two GitHub Actions workflows continuously test the repository:

- **SAO benchmark** — schema/artifact validation, reference evaluator and simulator safety checks;
- **SAO full suite** — 51-case structural validation, experiment validation, reference self-test, deterministic baseline profiles, adapter-protocol smoke test, simulator tests, suite report, and release integrity manifest.

A change is not considered complete merely because documentation looks correct; the control invariants must remain green.

## SAP-shaped scenarios, not SAP emulation

Current scenario documentation starts with:

- [`scenarios/001-idoc-interface-triage.md`](scenarios/001-idoc-interface-triage.md)
- [`scenarios/002-mdg-master-data-discrepancy.md`](scenarios/002-mdg-master-data-discrepancy.md)
- [`scenarios/003-o2c-order-block.md`](scenarios/003-o2c-order-block.md)

These are synthetic abstractions of enterprise support problems. They are not client reproductions and do not replace official SAP documentation.

SAO is independent work and is not an official SAP project, SAP certification, production-safety certification, or substitute for landscape-specific authorization/security review.

## Repository map

- [`docs/`](docs/) — control plane, risk model, benchmark, conformance, ADRs
- [`architectures/`](architectures/) — system boundaries and reference architectures
- [`contracts/`](contracts/) — capability/evidence/approval/execution contracts
- [`schemas/`](schemas/) — machine-readable contracts
- [`patterns/`](patterns/) — reusable enterprise-agent patterns
- [`scenarios/`](scenarios/) — synthetic SAP/enterprise cases
- [`evals/`](evals/) — SAO-Bench core corpus and domain packs
- [`baselines/`](baselines/) — deterministic control groups and reproducible result snapshots
- [`adapters/`](adapters/) — runtime-neutral adapter protocol and bridges
- [`simulator/`](simulator/) — Synthetic Enterprise Lab
- [`tests/`](tests/) — safety and trust invariants
- [`experiments/`](experiments/) — reproducible experiment protocol/manifests
- [`research/`](research/) — source-backed architecture research
- [`scripts/`](scripts/) — evaluators, validators, adapter runner, release-manifest tooling
- [`ROADMAP.md`](ROADMAP.md) — remaining experiments and release path
- [`AGENTS.md`](AGENTS.md) — engineering constitution for future agent-assisted changes

## Next high-value milestones

The project no longer needs generic feature expansion. The highest-value next work is evidence:

1. run the first real external-runtime comparison through the neutral adapter protocol;
2. freeze a reproducible **SAO-Bench v0.3** release with immutable corpus hashes;
3. add stateful multi-step experiments where agent decisions interact with injected failures;
4. grow the corpus only when a new enterprise failure mode or control gap is identified;
5. publish cross-runtime failure signatures, not a simplistic “best model” leaderboard;
6. explore governance-evidence adapters only through supported platform contracts.

See [`ROADMAP.md`](ROADMAP.md).

## Author

**Dzmitryi Kharlanau**  
SAP Transformation · Enterprise Operations · Agentic AI

- Professional site: https://dkharlanau.github.io/
- LinkedIn: https://www.linkedin.com/in/dkharlanau/
- Agent-Ready Web Profile: https://github.com/dkharlanau/agent-ready-web-profile
- Public datasets: https://github.com/dkharlanau/dkharlanau-datasets

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
