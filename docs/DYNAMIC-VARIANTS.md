# SAO Dynamic Adversarial Variants

Static benchmark cases are necessary for reviewability, but a runtime can overfit to fixed IDs, field values, timestamps, or familiar examples.

SAO therefore supports deterministic generated variants derived from reviewed enterprise-control invariants.

Dynamic variants are **supplemental evidence**. They do not silently change the frozen SAO-Bench corpus or score.

## Current invariant templates

`scripts/generate_variants.py` currently generates:

- stale approval after object state changed;
- ambiguous cross-system identity;
- duplicate/replay risk after a business event was already applied;
- instructions embedded in untrusted tool output;
- technical write success with unavailable business postcondition;
- stale runbook/memory guidance after policy changed.

Each variant changes surface values while preserving the expected control decision.

## Determinism

Generation is seed-based:

```bash
python sao.py variants \
  --seed my-experiment-seed \
  --per-template 5 \
  --output /tmp/sao-variants.jsonl
```

The same generator version + seed + `per-template` value produces the same variants.

Variant IDs are derived from the template, seed, and index. They are stable for that generation configuration.

## Evaluate generated cases

Reference/harness self-test:

```bash
python sao.py score-cases \
  --cases /tmp/sao-variants.jsonl \
  --predictions reference \
  --json
```

Run a real adapter:

```bash
python sao.py run-adapter \
  --cases /tmp/sao-variants.jsonl \
  --output /tmp/variant-predictions.jsonl \
  -- python your_adapter.py

python sao.py score-cases \
  --cases /tmp/sao-variants.jsonl \
  --predictions /tmp/variant-predictions.jsonl \
  --json
```

## Hidden-case protocol

For an external runtime experiment, the seed may remain private while decisions are being generated.

Important boundaries:

1. the adapter input never contains benchmark `expected` truth;
2. the adapter input strips the raw generation seed;
3. generated-case reports strip the raw seed and expose only `seed_sha256`;
4. a hidden workflow should not upload the raw generated case file because it contains generation truth and the raw seed;
5. after predictions are frozen, the seed can be disclosed later if independent reproduction is desired.

This gives a simple commitment protocol:

```text
private seed
    |
    +--> generated corpus --> runtime decisions --> freeze predictions
    |
    +--> SHA-256 commitment -----------------------> public report

optional later disclosure of seed --> regenerate exact corpus --> reproduce score
```

## GitHub workflow

`.github/workflows/dynamic-variants.yml` has two modes:

- push/PR: deterministic public self-test using the commit SHA as part of the seed;
- manual external run: uses repository secrets `SAO_ADAPTER_URL`, optional `SAO_ADAPTER_TOKEN`, and `SAO_VARIANT_SEED`.

The manual workflow uploads predictions, a seed-hash metadata record, and the scored report. It intentionally does **not** upload the raw generated hidden corpus.

## What variants should test

A useful variant changes surface details without changing the enterprise-control invariant.

Good mutations:

- object IDs;
- mapping candidates;
- message IDs/order;
- timestamps/version numbers;
- contradictory vs missing evidence;
- stale policy/approval state;
- injected untrusted instruction text.

Weak mutations:

- paraphrasing the same sentence without changing evidence structure;
- random noise unrelated to enterprise control;
- changing expected behavior through uncontrolled randomness;
- using an LLM to invent benchmark truth dynamically.

## No hidden leaderboard

Hidden variants are useful for robustness checks, but a private seed/corpus makes independent comparison weaker until disclosed.

Do not mix hidden-variant scores with frozen SAO-Bench leaderboard-style results. Report them as a separate experiment dimension with generator version, seed commitment, and variant count.