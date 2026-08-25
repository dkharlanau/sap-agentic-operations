# SAO-Bench Baselines

These strategies are deliberately simple and use **no model**. They exist to test benchmark discriminative power before external runtime/model experiments are published.

They never read the `expected` section of benchmark cases.

## Strategies

### `always-abstain`

Never executes and always returns `insufficient_evidence`.

Expected signature:

- zero unsafe executions;
- high safety by refusal;
- low usefulness/actionability;
- fails cases where evidence is sufficient for a deterministic conclusion or governed execution.

### `naive-auto-execute`

Treats every case as ready for execution.

Expected signature:

- many unsafe-execution failures;
- poor approval, identity and stale-state behavior;
- demonstrates why “tool calling works” is not an enterprise safety criterion.

### `memory-biased`

Assumes prior operating patterns should usually be reused.

Expected signature:

- no direct writes;
- poor handling of policy drift, stale context and novel evidence;
- useful control group for operational-memory experiments.

### `guarded-rules`

Uses a very small set of generic hard guards: unresolved identity, missing approval, stale state/version, revoked tool verification, obvious postcondition problems and untrusted embedded instructions.

Expected signature:

- zero unsafe executions;
- better control classification than purely naive strategies on some cases;
- still far below full benchmark success because generic guards cannot replace domain evidence and reasoning.

## Run

```bash
python baselines/generate.py guarded-rules --output /tmp/guarded.jsonl
python scripts/evaluate_suite.py --predictions /tmp/guarded.jsonl --json
```

Profile all built-in baselines:

```bash
python scripts/check_baselines.py
```

## Interpretation

A baseline score is not a target score for production agents. Baselines show whether the corpus can distinguish known operating behaviors.

In particular:

- `always-abstain` tests whether the benchmark rewards useful safe action instead of refusal alone;
- `naive-auto-execute` tests whether unsafe autonomy is strongly penalized;
- `memory-biased` tests whether current evidence/policy beats historical convenience;
- `guarded-rules` tests the value and limits of deterministic control gates.
