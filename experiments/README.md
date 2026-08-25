# SAO Experiments

This directory defines how public SAO benchmark results should be recorded.

A screenshot, a chat transcript, or an aggregate score is not a reproducible experiment.

## Required provenance

A runtime evaluation should bind the result to:

1. exact SAO-Bench commit and suite version;
2. runtime/framework name and version;
3. model/provider/version when a model is used;
4. agent configuration hash;
5. tool/capability manifest hash;
6. policy/conformance profile;
7. raw prediction JSONL;
8. deterministic SAO report;
9. simulator/fault profile when stateful execution is tested.

The manifest contract is [`schemas/experiment.schema.json`](../schemas/experiment.schema.json).

## Result kinds

### `reference_self_test`

Generated directly from expected benchmark invariants. This proves only that the corpus and evaluator agree. It is **not** an agent/model result and must never appear in a leaderboard as one.

### `runtime_evaluation`

A real agent/runtime/model configuration emits the portable SAO decision format and is scored without modifying the benchmark.

### `simulator_experiment`

An implementation interacts with the stateful Synthetic Enterprise Lab under a named fault profile. The experiment should preserve the simulator fixture and audit export in addition to prediction/report artifacts.

## Immutability rules

Published result directories are append-only.

- Do not overwrite a previously shared result.
- If the runtime configuration changes, create a new experiment ID.
- If benchmark expected behavior changes, use a new benchmark version.
- Keep failed and unsafe cases visible.
- Preserve raw predictions, not only summaries.

## Comparison rules

Never compare two aggregate scores without also showing:

- benchmark version;
- case count;
- risk-tier breakdown;
- threat-class breakdown;
- domain-pack breakdown;
- unsafe-execution count.

Latency, token and cost comparisons require a separately documented measurement protocol.

## Naming

Recommended experiment ID:

```text
YYYYMMDD-runtime-model-profile-shortid
```

Example:

```text
20260825-reference-selftest-v03
```

## Public claims

SAO results measure performance on this synthetic enterprise-control corpus. They do not prove production safety, SAP certification, official compatibility, or suitability for a specific customer landscape.
