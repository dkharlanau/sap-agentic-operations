# SAO Result Ledger

This directory is the public index for **reproducible SAO evidence**, not a leaderboard.

A score is not a result unless its provenance can be inspected.

## Result classes

SAO keeps three classes visually and semantically separate:

1. **Harness self-test** — generated from benchmark truth to prove evaluator plumbing. It is expected to score 100% and says nothing about a model/runtime.
2. **Deterministic baseline** — deliberately simple no-model strategies used to show that the corpus discriminates among control behaviors.
3. **External runtime evaluation** — a real configured agent/runtime/model evaluated through the neutral SAO adapter contract.

Simulator experiments are recorded separately when they test dynamic/stateful behavior rather than static SAO-Bench decisions.

## Publication contract

A committed external runtime result should include or reference:

- experiment manifest;
- benchmark version and exact Git commit;
- corpus SHA-256;
- evaluator SHA-256;
- runtime/framework version;
- model/provider/version where applicable;
- agent configuration hash;
- tool/capability manifest hash;
- capability and policy profiles;
- raw prediction JSONL;
- deterministic benchmark report;
- SAO-Trace report and declared telemetry completeness when available;
- machine-readable Assurance Case;
- human-readable Assurance Review;
- latency/token/cost data only when measured under a documented protocol.

## Ledger index

`results/index.json` is generated from committed result manifests by `scripts/build_result_index.py`.

The index is intentionally descriptive. It must not invent missing provenance and must not silently rank unlike experiments.

## No leaderboard yet

Do not publish a model/runtime leaderboard until all of the following are true:

- at least two independently configured real runtimes have reproducible runs;
- the benchmark corpus is frozen and versioned;
- comparison protocol is stable enough that scores are meaningfully comparable;
- known telemetry/trace completeness differences are visible;
- failure signatures are reported alongside aggregate scores.

Even then, the primary output should remain control failures by risk/threat/pack, not a single rank.

## Directory convention

```text
results/
  README.md
  manifests/
    <experiment-id>.json
  index.json
```

Raw large artifacts may live in a release/archive store if keeping them in Git is impractical, but the ledger must retain immutable references and hashes.

## Integrity rule

Do not edit a published result to make a later runtime look better. Rerun it as a new experiment with a new ID and compare the two evidence bundles using `scripts/diff_results.py`.