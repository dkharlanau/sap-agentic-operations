# Changelog

This changelog tracks benchmark/corpus/scoring changes that affect interpretation of SAO results.

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
