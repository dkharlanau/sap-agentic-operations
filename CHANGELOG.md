# Changelog

SAO has two versioned surfaces:

- the **practical toolkit**, focused on evidence, incident analysis, reconciliation and local workflows;
- **SAO-Bench**, the experimental agent-assurance corpus and evaluator.

## 0.4.0-alpha.3 — Practical Toolkit Alpha 3

### Changed

- Added a compact, reproducible proof path using the checked-in synthetic missing-event Evidence Pack.
- Named the expected JSON artifact and deterministic control result directly in the README.
- Linked the proof to the public Evidence Pack contract and made the no-live-SAP, no-execution-authority boundary explicit.

### Compatibility and limits

- Practical CLI behavior and Evidence Pack formats are unchanged from Alpha 2.
- The proof is synthetic local evidence, not a production SAP result or authorization signal.
- SAO-Bench remains separately versioned as `0.3-dev`; no benchmark freeze is implied.

## 0.4.0-alpha.2 — Practical Toolkit Alpha 2

### Added

- Portable Signal to Insight research-evidence handoff validation.
- `sao research validate` for schema, publication-boundary and digest checks.
- `sao research review` for a bounded, Markdown-escaped human review card.
- An explicit separation between external research context and operational Evidence Packs.
- A complete synthetic Customer Governance to Order-to-Cash reference assurance set.
- Stable cross-repository artifact references with executable validation helpers.
- Business-event idempotency and postcondition checks in the reference runtime path.
- Public product and documentation Pages.

### Compatibility and limits

- Evidence Pack and practical CLI contracts remain compatible with Alpha 1.
- Research evidence is review context only; it cannot grant authority or become incident evidence.
- The customer-governance reference set is synthetic assurance evidence, not production validation.
- No live SAP connector, production write automation, or package-registry publication is claimed.

## 0.4.0-alpha.1 — Practical Toolkit Alpha 1

First usable product-oriented alpha.

### Added

- Installable zero-dependency `sao` CLI for Python 3.11+.
- SAO Evidence Pack v0.1:
  - explicit business-object identity;
  - source change evidence;
  - message/integration evidence;
  - target business-state observations;
  - versioned identity mappings.
- Deterministic Incident Analyzer with evidence-backed classifications including:
  - `current_outbound_event_not_proven`;
  - `business_processing_rejection`;
  - `mapping_version_drift`;
  - `target_state_mismatch_after_current_event`;
  - `technical_message_failure`;
  - `business_state_verified`;
  - unresolved identity;
  - stale target observation;
  - message/target identity mismatch.
- Nine ready-to-run synthetic SAP operations scenarios through `sao demo`.
- `sao incident init`, `validate`, and `analyze` workflows.
- One-CSV `sao quickcheck` path for Excel-style operational lists; it reuses the full Incident Analyzer rather than separate simplified logic.
- Batch triage over multiple Evidence Packs with CSV/JSON/Markdown summaries.
- Local read-only Workbench with evidence chain, findings, missing evidence, safe actions, blocked actions and resolution condition.
- Semantic master-data reconciliation using canonical identity, per-attribute authority and snapshot freshness.
- Configurable CSV normalizer for SAP/Excel exports with explicit column mappings, constants and value maps; includes a WE02-like demo with status mapping.
- Machine-readable schemas for Evidence Pack and reconciliation manifests.
- Privacy-safe practical field-report GitHub issue template.
- Dedicated `SAO practical toolkit` GitHub Actions workflow exercising the installed CLI end to end.

### Product principles established

- local-first core workflow;
- no SAP credentials required for file-based use;
- no LLM required for deterministic diagnosis;
- read-only by default;
- technical success is not accepted as business success without a verified postcondition;
- historical successful messages do not prove a newer change replicated;
- replay is blocked when event-time identity/mapping semantics are unresolved;
- explicit mappings are preferred to unsafe automatic guessing of export columns;
- connectors should populate stable evidence semantics rather than define product logic.

### Known limits

- File/CSV workflows are the practical alpha; no live SAP or Cloud ALM collector is claimed yet.
- Evidence Pack v0.1 currently focuses on a single bounded object/change investigation; more complex multi-object/process semantics will evolve from field reports.
- Reconciliation v0.1 does not yet model value-mapping history, pending governance state, or scoped exceptions in the practical CLI.
- Workbench is a local read-only evidence view, not an incident-management system.
- The project is independent and is not an official SAP product or certification.

## Unreleased — toward SAO-Bench 0.3

### Added

- Expanded benchmark from 15 to 51 enterprise-control cases.
- Added domain packs:
  - Integration Operations;
  - Master Data / MDG;
  - Business Process / O2C / P2P;
  - Agent Security;
  - State Change.
- Added R0–R4 risk tiers and T1–T10 agentic threat classes to the expanded corpus.
- Added structural coverage validation requiring every domain pack to contain:
  - an `insufficient_evidence` case;
  - an explicit policy/approval/execution boundary.
- Added runtime-neutral decision adapter protocol.
- Added reproducible experiment manifest contract.
- Added deterministic benchmark baselines.
- Added Synthetic Enterprise Lab v0.3 with identity/policy/version/fault/state-change controls.
- Added release integrity-manifest generator.

### Changed

- Canonical write-ready status is `approved_for_execution`.
- Full-suite reporting now includes pack, risk-tier, threat-class and decision-status breakdown.

### Fixed

- Prevented status drift between new benchmark cases and `schemas/decision.schema.json`.
- Fixed baseline profiler import path under GitHub Actions.

### Compatibility

This is still `0.3-dev`; no public benchmark version is frozen yet. Development results must reference an exact commit.

## 0.2-dev

- Introduced executable evaluator over the initial synthetic corpus.
- Added decision/evidence/write-envelope schemas.
- Added first stateful simulator and CI.

## 0.1-dev

- Established SAO control-plane concept, capability model and initial SAP-shaped scenarios.
