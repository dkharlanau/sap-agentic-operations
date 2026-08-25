# Roadmap

SAP Agentic Operations should grow by increasing **evidence, adversarial coverage, reproducibility, and external validity** — not by accumulating generic agent features.

## Current — v0.3-dev assurance lab

Implemented:

- enterprise agent control-plane architecture;
- R0–R4 business-risk tiers;
- T1–T10 agentic threat classes;
- 51 deterministic enterprise-control benchmark cases;
- five domain packs plus core cases;
- decision, evidence, write-envelope, experiment, trace-event, and assurance-case schemas;
- deterministic full-suite evaluator with pack/risk/threat breakdown;
- benchmark structural/coverage validator;
- four deliberately different no-model baselines;
- immutable baseline evidence snapshot;
- stateful Synthetic Enterprise Lab v0.3;
- identity/mapping versions, policy drift, event ledger, message faults, approvals, concurrency/preconditions, idempotency, postconditions, audit, and compensation;
- trust-aware operational memory/evidence controls;
- runtime-neutral stdin/stdout adapter protocol;
- generic HTTPS/OpenAPI runtime bridge;
- SAO-Trace behavioral invariant evaluator with positive/negative fixtures;
- reproducible experiment manifest protocol;
- machine-readable Assurance Case generator;
- benchmark release-versioning policy and SHA-256 integrity manifest;
- public ADRs preventing architectural drift;
- GitHub Actions evidence bundle covering benchmark + trace + simulator + baselines + integrity.

The current priority is no longer “build the missing architecture.” It is **validate the architecture with external implementations and freeze a credible benchmark release.**

## v0.3 release — freeze the first public benchmark

Before tagging `SAO-Bench v0.3.0`:

1. complete a corpus review for ambiguous or duplicate cases;
2. document every case pack and expected invariant;
3. ensure decision/trace/experiment/assurance schemas are internally consistent;
4. run all deterministic baselines and preserve results;
5. generate immutable corpus/schema/evaluator hashes;
6. freeze case IDs and changelog;
7. publish release notes distinguishing benchmark self-test from runtime results;
8. create a Zenodo/DOI release only if it improves citation/research reuse;
9. keep the development branch open for future v0.4 cases after the frozen tag.

A frozen release matters more than adding another 50 unreviewed cases.

## v0.4 — first real cross-runtime evidence

Target: prove that SAO can compare implementations without changing benchmark truth.

Priority experiments:

1. one accessible pro-code or HTTP runtime;
2. one orchestration-style runtime;
3. Joule Studio/Joule Agent when an appropriate environment is available.

For every runtime preserve:

- exact runtime/model versions;
- agent/prompt/config hash;
- tool/capability manifest;
- policy profile;
- raw decisions;
- SAO-Trace where telemetry is available;
- benchmark/trace reports;
- machine-readable Assurance Case;
- latency/token/cost only when measured under a defined protocol.

The result should emphasize **different failure signatures**, not crown a “best model.”

## v0.5 — dynamic and stateful assurance

Static case memorization is an eventual benchmark risk. Expand the lab with generated and stateful experiments:

- parameterized object IDs/values/timestamps;
- hidden case variants generated from invariant templates;
- controlled evidence omissions/contradictions;
- multi-step fault campaigns;
- concurrent actors and stale approvals;
- changing identity/value mappings during an investigation;
- policy revocation between planning and execution;
- duplicate/out-of-order/replayed business events;
- postcondition observation failure;
- compensation failure and partial recovery;
- operational-memory poisoning and stale runbooks;
- inter-agent claims with missing/invalid attestations.

The generator must preserve deterministic expected invariants and never expose customer data.

## v0.6 — trace completeness and runtime instrumentation

SAO-Trace is only as good as observable runtime behavior.

Research and implement:

- adapter-side trace normalization;
- completeness declarations (which event classes a runtime can expose);
- tool-call and approval telemetry adapters;
- hidden-action limitations;
- trace-to-decision correlation;
- multi-agent span/correlation identity;
- behavior-delta analysis between runtime/model versions.

A final safe answer should never hide an unsafe intermediate action simply because telemetry was absent.

## v0.7 — governance evidence adapters

Keep SAO vendor-neutral, but make evidence easy to consume by enterprise governance processes.

Potential adapters, only through supported contracts:

- SAP AI Agent Hub / enterprise architecture governance evidence;
- internal risk/architecture review systems;
- CI release gates;
- policy-as-code systems;
- security evidence stores.

Export:

- benchmark identity/hash;
- Assurance Case;
- risk/threat failure breakdown;
- failed control IDs;
- trace completeness;
- tool/capability profile;
- immutable artifact references.

Do **not** claim official integration/certification until a real supported integration exists.

## v0.8 — external validity

Before presenting SAO as anything broader than an independent research project:

- at least three independent runtime implementations;
- review from SAP/enterprise operations practitioners;
- review from agent-security/AI-governance practitioners;
- documented false positives and false negatives;
- case disputes preserved and resolved transparently;
- benchmark contribution process with adversarial review;
- public result provenance and reproducible reruns;
- evidence that SAO catches failures not already captured by simpler generic evals.

## 1.0 criterion

Version 1.0 should mean the project has **independent evidence of usefulness**, not merely more code.

A reasonable 1.0 bar:

- stable benchmark semantics;
- multiple independent implementations;
- versioned reproducible result corpus;
- demonstrated trace/state assurance value;
- documented limitations and false-negative classes;
- external contributors or reviewers;
- evidence that the project changes real architecture/governance decisions.

## Long-term thesis

The interesting open problem is not whether agents can call enterprise APIs. It is whether organizations can **produce inspectable evidence for which agents may be trusted with which business capabilities, under which identity, evidence, policy, approval, and state conditions.**

SAO should remain focused on making that question executable.
