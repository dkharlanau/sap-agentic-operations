# SAO-Bench Versioning and Compatibility

SAO-Bench results are meaningful only when the benchmark identity is stable.

This policy applies to the **benchmark corpus and scoring semantics**, independently of ordinary repository/documentation changes.

## Version model

SAO-Bench uses `MAJOR.MINOR.PATCH` once a release is frozen.

### MAJOR

Increment when results are not meaningfully comparable without explicit migration, for example:

- decision status semantics change;
- risk-tier meaning changes materially;
- threat taxonomy is redefined incompatibly;
- scoring weights/required invariants change in a way that systematically changes old results;
- previously valid prediction format becomes invalid.

### MINOR

Increment for additive benchmark coverage under compatible semantics, for example:

- new cases;
- new domain packs;
- new threat coverage using existing threat definitions;
- optional output fields that do not invalidate older predictions.

Old scores remain valid for the old release but must not be presented as if they were run on the larger suite.

### PATCH

Increment for compatible fixes that do not change intended benchmark truth, such as:

- evaluator bug fix where expected semantics were already unambiguous;
- metadata/citation fixes;
- non-semantic schema clarifications.

If a patch changes a case's expected safe decision, treat it as at least MINOR and document the case explicitly.

## Immutable case IDs

Once included in a public frozen release:

- a case ID is never silently reassigned to a different situation;
- retired cases remain documented;
- a materially changed situation receives a new case ID;
- correcting benchmark truth requires a changelog entry.

## Expected-answer changes

Never edit expected behavior in a released case without recording:

- case ID;
- old expectation;
- new expectation;
- why the old expectation was wrong or incomplete;
- version in which the change takes effect.

## Result compatibility

Every published result must identify:

- benchmark version;
- exact Git commit;
- case count;
- raw prediction artifact;
- evaluator version/hash;
- experiment manifest.

An aggregate score without benchmark identity is not a valid SAO result.

## Release freeze

Before tagging a benchmark release:

1. `scripts/validate_suite_contracts.py` passes;
2. reference self-test passes 100%;
3. all simulator tests pass;
4. baseline profiles remain discriminative;
5. experiment manifests validate;
6. a release manifest is generated with SHA-256 hashes;
7. `CHANGELOG.md` describes the corpus/scoring delta;
8. release commit is immutable and tagged.

## Current status

`0.3-dev` is development state, not a frozen public benchmark release. Results created against it must be labeled `0.3-dev` and bound to an exact commit.
