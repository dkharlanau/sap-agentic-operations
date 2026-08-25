# SAP Agentic Operations (SAO)

[![SAO full suite](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml)
[![SAO benchmark](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/evals.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/evals.yml)
[![Dynamic variants](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/dynamic-variants.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/dynamic-variants.yml)

**An executable assurance lab for AI agents that reason around SAP and other enterprise systems of record.**

Maintained by **Dzmitryi Kharlanau** — SAP Transformation · Enterprise Operations · Agentic AI.

Status: **experimental SAO-Bench v0.3-dev**.

Most agent demos answer:

> Can an LLM call a tool?

SAO asks the harder enterprise question:

> **Can we produce evidence that an agent knows when it may read, reason, request approval, execute, abstain, and verify a business outcome?**

SAO uses SAP-shaped synthetic operations to test identity, evidence, source-of-truth authority, policy, authorization, capability scope, approval, stale state, idempotency, postconditions, provenance, compensation, memory trust, and adversarial tool/context inputs.

No SAP tenant is required. No client data belongs here. The simulator does **not** emulate S/4HANA.

---

## Try the lab in 60 seconds

Requirements: Python 3.11+; the core tooling uses the standard library.

```bash
git clone https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations

python sao.py doctor
python sao.py audit
python sao.py self-test
python sao.py tests
```

Expected distinction:

- `doctor` checks the assurance harness itself;
- `self-test` should score 100% because it generates predictions from benchmark truth;
- **neither is a model/runtime result**.

Profile the intentionally different deterministic baselines:

```bash
python sao.py baselines
```

Check that a runtime adapter obeys the neutral protocol:

```bash
python sao.py adapter-check -- python adapters/guarded_rules.py
```

Generate adversarial variants:

```bash
python sao.py variants \
  --seed local-demo \
  --per-template 4 \
  --output /tmp/sao-variants.jsonl

python sao.py score-cases \
  --cases /tmp/sao-variants.jsonl \
  --predictions reference
```

---

## The project in one diagram

```text
Agent runtime / Joule / LangGraph / n8n / custom orchestrator
                              |
                              v
                    Runtime Adapter Contract
                              |
                              v
                     SAO Decision Contract
                              |
              +---------------+---------------+
              | identity | evidence | policy  |
              | risk     | approval | trust   |
              +---------------+---------------+
                              |
                              v
                      Decision / Abstain
                              |
                       approval if needed
                              |
                              v
                    State-Change Envelope
                              |
                              v
                     Narrow typed tool
                              |
                              v
                    SAP / system of record
                              |
                              v
                    Verify + Audit + Recover

                     ^                    ^
                     |                    |
               SAO-Bench             SAO-Trace
                     \____________________/
                              |
                    Assurance Case / Review
```

The model may reason broadly. The state-changing surface should remain narrow, typed, policy-bound, observable, and revocable.

Start with [`docs/CONTROL-PLANE.md`](docs/CONTROL-PLANE.md).

---

## What exists today

### SAO-Bench: 51 reviewed enterprise-control cases

The static development corpus contains **51 synthetic cases** across a core set and five packs.

| Pack | Cases | Main control problem |
|---|---:|---|
| Core | 15 | causality, authority, evidence, approvals, abstention |
| Integration Operations | 7 | replay, ordering, mapping drift, retry ambiguity, business acknowledgement |
| Master Data / MDG | 7 | canonical identity, source of truth, governance/mapping versions |
| Business Process | 7 | O2C/P2P blocks, deterministic checks, business authority |
| Agent Security | 7 | tool-output injection, poisoned memory, scope escalation, inter-agent trust |
| State Change | 8 | stale approval, races, idempotency, postconditions, compensation |

Every case carries:

- an **R0–R4 business-impact tier**;
- one or more **T1–T10 failure/threat classes**;
- explicit expected control findings/actions;
- forbidden actions;
- an execution gate;
- safe abstention/policy outcomes where appropriate.

The evaluator reports failure signatures by case, pack, risk tier, threat class, and expected status.

```bash
python sao.py audit --json
python sao.py self-test --json
```

See [`evals/README.md`](evals/README.md), [`docs/BENCHMARK.md`](docs/BENCHMARK.md), and [`docs/CASE-PACKS.md`](docs/CASE-PACKS.md).

### Deterministic control baselines

SAO contains deliberately simple no-model strategies so a benchmark cannot look useful merely because its reference answers score 100%.

A reproducible 51-case snapshot demonstrates sharply different behavior:

| Baseline | Decision-class accuracy | Execution-gate accuracy | Unsafe executions |
|---|---:|---:|---:|
| `guarded-rules` | 37.3% | 94.1% | 0 |
| `always-abstain` | 31.4% | 94.1% | 0 |
| `memory-biased` | 17.7% | 94.1% | 0 |
| `naive-auto-execute` | 5.9% | 5.9% | **48 / 51** |

This is a control group, not a model leaderboard.

The point is that blanket refusal can be safe but weak, generic guardrails cannot replace enterprise evidence, and naive autonomy is catastrophically unsafe on the corpus.

See [`baselines/`](baselines/).

### Synthetic Enterprise Lab v0.3

The stateful simulator tests dynamic failure conditions that a static prompt benchmark cannot represent well.

It models:

- canonical identity and mapping versions;
- deterministic time;
- policy drift;
- event/message ledger;
- delay/drop/duplicate faults;
- scoped approvals and expiry;
- object version/precondition binding;
- typed writes;
- idempotency/collision detection;
- business postconditions;
- audit evidence;
- governed compensation;
- trust-aware memory/evidence.

Examples enforced by tests:

- missing approval → reject;
- changed identity mapping → quarantine/reject stale action;
- changed object version → invalidate stale approval;
- same idempotency key + same operation → no second mutation;
- same key + different operation → reject;
- technical success + failed business postcondition → failure, not success;
- available rollback + missing rollback authorization → do not compensate;
- untrusted ticket/tool text → never becomes control authority.

```bash
python sao.py tests
```

See [`simulator/`](simulator/).

### SAO-Trace

A safe final sentence does not prove the runtime behaved safely internally.

SAO-Trace evaluates observable action sequences and can detect patterns such as:

- capability escalation after a narrow tool failure;
- using untrusted memory as policy;
- unsafe intermediate writes followed by a safe-looking final answer;
- obeying control-like instructions embedded in tool output.

The Assurance Case explicitly states when trace/telemetry evidence is absent or incomplete.

See [`traces/`](traces/) and `scripts/evaluate_trace.py`.

---

## Runtime-neutral integration

SAO does not require a particular agent framework.

An adapter receives one case without benchmark truth:

```json
{
  "protocol_version": "0.1",
  "case": {
    "id": "...",
    "pack": "...",
    "scenario": "...",
    "risk_tier": "R3",
    "threats": ["T8"],
    "input": {}
  }
}
```

It returns one [`SAO Decision`](schemas/decision.schema.json).

### Local adapter

```bash
python sao.py adapter-check -- python your_adapter.py

python sao.py run-adapter \
  --output /tmp/predictions.jsonl \
  -- python your_adapter.py

python sao.py score /tmp/predictions.jsonl --json
```

### Generic HTTPS runtime bridge

```bash
export SAO_ADAPTER_URL=https://agent.example.com/sao-decision
export SAO_ADAPTER_TOKEN=...

python sao.py adapter-check -- python adapters/http_endpoint.py
python sao.py run-adapter --output /tmp/predictions.jsonl -- python adapters/http_endpoint.py
```

The bridge rejects remote plain HTTP, embedded URL credentials, mismatched case IDs, and oversized responses. Benchmark `expected` truth is never sent to the runtime.

See [`adapters/README.md`](adapters/README.md) and [`adapters/http/openapi.json`](adapters/http/openapi.json).

---

## Bring your own runtime: one GitHub workflow

The manual workflow [`SAO external runtime evaluation`](.github/workflows/external-runtime.yml) turns an HTTPS agent endpoint into a reproducible evidence bundle.

Configure repository secrets:

```text
SAO_ADAPTER_URL=https://your-agent.example/sao-decision
SAO_ADAPTER_TOKEN=<optional bearer token>
```

Run the workflow and provide runtime/model/capability metadata.

It executes:

```text
project validation
    -> corpus audit
    -> adapter conformance
    -> 51-case external run
    -> deterministic score
    -> agent/tool configuration fingerprints
    -> experiment manifest with corpus/evaluator hashes
    -> Assurance Case
    -> human-readable Assurance Review
    -> release integrity manifest
    -> evidence artifact bundle
```

Benchmark control failures are preserved as experiment results rather than disguised as infrastructure failures.

The next critical milestone is a **real external-runtime result** through this path.

---

## Dynamic / hidden adversarial variants

Static cases are reviewable but can be memorized. SAO also generates deterministic variants from control invariants:

- stale approvals;
- ambiguous identity;
- duplicate replay;
- tool-output injection;
- missing business postcondition;
- stale runbook/policy memory.

The runtime never receives the raw generation seed or benchmark truth.

For hidden experiments, the report exposes only a SHA-256 seed commitment. The raw hidden corpus is not uploaded automatically. The seed can be disclosed after predictions are frozen when independent reproduction is desired.

See [`docs/DYNAMIC-VARIANTS.md`](docs/DYNAMIC-VARIANTS.md) and [`SAO dynamic variants`](.github/workflows/dynamic-variants.yml).

---

## Evidence, not screenshots

SAO treats provenance as part of the benchmark result.

A real runtime experiment can bind:

- exact SAO commit and benchmark version;
- corpus SHA-256;
- evaluator SHA-256;
- runtime/framework identity;
- model identity/version when known;
- agent-config SHA-256;
- tool/capability-manifest SHA-256;
- capability/policy profiles;
- raw predictions;
- benchmark report;
- trace evidence where observable;
- machine-readable Assurance Case;
- human-readable Assurance Review.

Build/compare evidence locally:

```bash
python sao.py manifest --version 0.3-dev --output /tmp/release.json
python sao.py diff before-report.json after-report.json
```

`diff` reports fixed/regressed cases plus pack/risk/threat deltas; aggregate score movement alone is not enough for enterprise change control.

### Public result ledger

[`results/index.json`](results/index.json) is the machine-readable result ledger.

It currently contains only the harness self-test and explicitly keeps:

```json
"leaderboard_enabled": false
```

SAO will not publish a runtime leaderboard until at least two independently configured, reproducible external runtime results exist and the comparison protocol is credible.

See [`results/README.md`](results/README.md).

---

## Benchmark governance and release discipline

SAO-Bench expected answers are reviewable claims, not unquestionable truth.

The repository now has:

- deterministic corpus audit;
- pack-level human review checklist;
- immutable released case-ID policy;
- explicit semantic-change versioning;
- a structured `SAO-Bench case dispute` GitHub issue form;
- public false-positive/false-negative terminology;
- four release gates: structural validity, corpus review, reproducibility, external validity.

A green CI run is necessary but not sufficient to freeze v0.3.

See:

- [`release/README.md`](release/README.md)
- [`BENCHMARK_VERSIONING.md`](BENCHMARK_VERSIONING.md)
- [`docs/BENCHMARK-GOVERNANCE.md`](docs/BENCHMARK-GOVERNANCE.md)
- [`CHANGELOG.md`](CHANGELOG.md)

---

## Machine-readable contracts

Important schemas include:

- [`decision.schema.json`](schemas/decision.schema.json) — portable decision output;
- [`evidence.schema.json`](schemas/evidence.schema.json) — evidence/provenance envelope;
- [`write-envelope.schema.json`](schemas/write-envelope.schema.json) — governed state change;
- [`trace-event.schema.json`](schemas/trace-event.schema.json) — observable runtime events;
- [`experiment.schema.json`](schemas/experiment.schema.json) — reproducible experiment identity;
- [`assurance-case.schema.json`](schemas/assurance-case.schema.json) — bounded evidence claims;
- [`result-index.schema.json`](schemas/result-index.schema.json) — public result ledger.

The core capability model remains:

```text
READ -> RECOMMEND -> APPROVE -> EXECUTE
```

These are different capability classes. A failure at one level never grants the next level.

---

## Risk model

Business impact and agent failure mechanism are deliberately separate.

### Business impact

- **R0** — informational;
- **R1** — diagnostic;
- **R2** — reversible operational change;
- **R3** — material business-state change;
- **R4** — high-impact / irreversible / regulated.

### Threat / control-failure classes

- **T1** goal / instruction hijacking;
- **T2** excessive tool capability;
- **T3** identity / privilege abuse;
- **T4** memory / context poisoning;
- **T5** insecure agent/tool communication;
- **T6** cascading / retry failure;
- **T7** trust / authority exploitation;
- **T8** stale-state execution;
- **T9** verification failure;
- **T10** provenance loss.

See [`docs/RISK-MODEL.md`](docs/RISK-MODEL.md).

---

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
15. **A score without provenance is not a benchmark result.**
16. **A safe final answer does not erase an unsafe intermediate action.**

Accepted architectural decisions and reversal criteria live in [`docs/adr/`](docs/adr/).

---

## SAP-shaped, framework-neutral

The initial narrative scenarios are:

- [`IDoc / interface failure triage`](scenarios/001-idoc-interface-triage.md)
- [`MDG / master-data discrepancy`](scenarios/002-mdg-master-data-discrepancy.md)
- [`O2C order-block investigation`](scenarios/003-o2c-order-block.md)

They are synthetic abstractions of enterprise support problems, not client reproductions and not replacements for official SAP documentation.

SAO is independent work. It is not an official SAP project, SAP certification, production-safety certification, or substitute for landscape-specific authorization/security review.

---

## Repository map

- [`docs/`](docs/) — control plane, benchmark, risk/governance, conformance, ADRs
- [`contracts/`](contracts/) — capability/evidence/write contracts
- [`schemas/`](schemas/) — machine-readable evidence contracts
- [`evals/`](evals/) — core benchmark + domain packs
- [`baselines/`](baselines/) — deterministic controls and immutable snapshots
- [`simulator/`](simulator/) — Synthetic Enterprise Lab
- [`traces/`](traces/) — observable-behavior invariants and fixtures
- [`adapters/`](adapters/) — framework-neutral runtime bridges
- [`experiments/`](experiments/) — experiment provenance protocol
- [`results/`](results/) — public evidence ledger
- [`release/`](release/) — benchmark freeze/release gates
- [`research/`](research/) — source-backed architecture research
- [`scripts/`](scripts/) — evaluators, validators, generators, assurance tooling
- [`ROADMAP.md`](ROADMAP.md) — evidence-first path to stronger external validity
- [`AGENTS.md`](AGENTS.md) — engineering constitution for future agent loops

---

## What matters next

The project does **not** need another generic agent framework.

Highest-value next milestones:

1. run the first real external runtime through the BYO workflow;
2. perform human corpus review and freeze **SAO-Bench v0.3.0**;
3. publish the first reproducible external result in the result ledger;
4. compare runtime/model versions through failure-signature regression diffs;
5. disclose and reproduce selected hidden-variant seeds after predictions freeze;
6. seek external review of R3/R4 benchmark truth and enterprise relevance;
7. grow the corpus only when a genuinely new control failure is identified.

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
