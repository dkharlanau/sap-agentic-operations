# SAO Benchmark

The benchmark tests **enterprise control decisions**, not writing style.

Any model, agent framework, Joule agent, MCP-based client, or custom orchestrator can participate if it can produce the decision JSONL format.

## Run

```bash
python scripts/evaluate.py --predictions evals/predictions.reference.jsonl
```

Machine-readable report:

```bash
python scripts/evaluate.py \
  --predictions evals/predictions.reference.jsonl \
  --json
```

The bundled reference predictions are a harness self-test and should score 100%. They are not a model benchmark result.

## Prediction format

One JSON object per line:

```json
{
  "id": "case-id",
  "status": "recommendation",
  "risk_tier": "R1",
  "findings": ["bounded finding backed by evidence"],
  "actions": ["request_next_evidence"],
  "execution_allowed": false,
  "evidence_refs": ["synthetic://case-id/e1"]
}
```

See `schemas/decision.schema.json`.

## What is scored

- correct decision class;
- required deterministic or control findings;
- required safe next actions;
- absence of forbidden actions;
- execution gating;
- evidence references for resolved/recommendation/execution outcomes;
- threat-class and risk-tier breakdown.

## Current threat classes

- T1 goal / instruction hijacking
- T2 tool misuse / excessive capability
- T3 identity and privilege abuse
- T4 memory and context poisoning
- T5 insecure agent/tool communication
- T6 cascading failure
- T7 trust exploitation
- T8 stale-state execution
- T9 verification failure
- T10 provenance loss

See `docs/RISK-MODEL.md`.

## Why exact findings are used in v0.2

The first executable version intentionally uses structured exact markers instead of an LLM-as-judge. This keeps the benchmark deterministic and auditable while the case taxonomy is still evolving.

Later versions can add semantic grading for hypotheses while preserving deterministic grading for policy, capability, identity, and execution invariants.

## Adding a case

Each case in `cases.jsonl` should include:

- `id`
- `scenario`
- `risk_tier`
- `threats`
- synthetic `input`
- expected `status`
- `required_actions`
- `must_identify`
- optional `must_not`

Cases should be difficult because the enterprise control decision is difficult, not because the prompt is intentionally obscure.
