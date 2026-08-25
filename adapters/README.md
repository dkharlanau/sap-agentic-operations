# SAO Runtime Adapter Protocol

SAO adapters let any agent/runtime participate in the same benchmark without changing benchmark truth.

## Protocol v0.1

The runner starts the adapter once per case.

Input: one JSON object on standard input.

```json
{
  "protocol_version": "0.1",
  "case": {
    "id": "...",
    "pack": "...",
    "scenario": "...",
    "risk_tier": "R2",
    "threats": ["T8"],
    "input": {}
  }
}
```

The runner deliberately removes `expected` and internal source metadata before invoking the adapter.

Output: exactly one SAO Decision JSON object on standard output, compatible with `schemas/decision.schema.json`.

No Markdown wrapper or additional stdout logging is allowed. Diagnostics belong on stderr.

## Run an adapter

```bash
python scripts/run_adapter.py \
  --output /tmp/predictions.jsonl \
  -- python adapters/guarded_rules.py

python scripts/evaluate_suite.py \
  --predictions /tmp/predictions.jsonl \
  --json
```

## Runtime-specific adapters

An adapter may call:

- Joule Studio / a Joule Agent;
- LangGraph;
- Pydantic AI;
- n8n;
- another MCP client/orchestrator;
- a proprietary enterprise agent runtime;
- a plain model API.

The adapter is responsible for translating the runtime's result into the neutral SAO decision contract.

## Rules

1. Never expose benchmark `expected` fields to the runtime.
2. Do not customize benchmark truth per runtime.
3. Preserve model/runtime/tool configuration in an experiment manifest.
4. Keep credentials outside the repository.
5. Capture raw predictions before scoring.
6. A runtime failure is a result; do not silently replace it with a reference answer.
7. Adapters may use deterministic guards around a model, but the configuration must be documented.

## Reference adapter

`guarded_rules.py` is a deterministic no-model adapter used to test the protocol plumbing. It is not an AI benchmark result.
