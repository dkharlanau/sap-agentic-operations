# SAO-Bench Release Discipline

This directory records what must be true before a development corpus becomes a frozen public benchmark release.

A green CI run is necessary but not sufficient.

## Release gates

### Gate A — Structural validity

Must be automated and reproducible:

- corpus parses;
- case IDs are unique;
- schemas parse and internal contracts validate;
- risk/threat values are from the published taxonomy;
- reference self-test is 100%;
- simulator tests pass;
- deterministic baselines remain intentionally discriminative;
- experiment and assurance artifacts validate;
- release manifest hashes can be regenerated.

### Gate B — Corpus review

Requires deliberate human review:

- no exact semantic duplicates that add no coverage;
- no ambiguous expected decision;
- no accidental answer leakage in case wording;
- each case has a defensible business-risk tier;
- each threat mapping describes a failure mechanism;
- each pack contains useful abstention/policy-boundary coverage;
- positive-path cases exist where safe execution is part of the pack's purpose;
- disputed cases are recorded transparently.

### Gate C — Reproducibility

A public result must preserve:

- benchmark version and Git commit;
- release manifest / corpus hashes;
- evaluator identity;
- runtime/model/config identity;
- raw decisions;
- experiment manifest;
- trace evidence and declared trace completeness when available;
- Assurance Case.

### Gate D — External validity

Not required to publish an experimental corpus, but required before broad claims of usefulness:

- at least one non-reference runtime has completed a reproducible run;
- limitations and untested behaviors are stated;
- benchmark self-test results are not presented as runtime performance;
- external reviewers can dispute case truth.

## v0.3.0 release-candidate checklist

- [ ] `python scripts/validate_project_state.py`
- [ ] `python scripts/validate_suite_contracts.py`
- [ ] `python scripts/audit_corpus.py --require-cases 50`
- [ ] corpus audit contains no structural errors
- [ ] all corpus warnings reviewed and disposition recorded
- [ ] `python scripts/evaluate_suite.py --predictions reference --require-cases 50`
- [ ] deterministic baseline profiles regenerated and reviewed
- [ ] simulator/adapter/trace tests green
- [ ] case pack review completed using `docs/CASE-PACKS.md`
- [ ] case IDs frozen for the release
- [ ] `CHANGELOG.md` contains the v0.3.0 corpus/scoring delta
- [ ] release manifest generated from the exact release commit
- [ ] release notes explicitly state that SAO is an independent experimental project
- [ ] any external runtime result is clearly separated from reference/self-test evidence
- [ ] unresolved benchmark-truth disputes are either resolved or explicitly block release

## Freeze rule

After the v0.3.0 release commit is tagged, do not change expected behavior for a released case in place. Follow `BENCHMARK_VERSIONING.md`.

New development continues under the next development version. The frozen release remains reproducible.