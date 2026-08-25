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

Output: exactly one SAO Decision JSON object on standard output, compatible with [`schemas/decision.schema.json`](../schemas/decision.schema.json).

No Markdown wrapper or additional stdout logging is allowed. Diagnostics belong on stderr.

## Run a local adapter

```bash
python sao.py run-adapter \
  --output /tmp/predictions.jsonl \
  -- python adapters/guarded_rules.py

python sao.py score /tmp/predictions.jsonl --json
```

Equivalent low-level commands remain available through `scripts/run_adapter.py` and `scripts/evaluate_suite.py`.

## Generic HTTPS bridge

`http_endpoint.py` lets an external runtime participate without adding its SDK to SAO.

```bash
export SAO_ADAPTER_URL=https://agent.example.com/sao-decision
export SAO_ADAPTER_TOKEN=...

python sao.py run-adapter \
  --output /tmp/predictions.jsonl \
  -- python adapters/http_endpoint.py
```

Transport rules:

- remote endpoints must use HTTPS;
- plain HTTP is accepted only for localhost experiments;
- credentials embedded in URLs are rejected;
- bearer token is optional and supplied only from the environment;
- response size is bounded;
- returned case ID must match the request;
- the benchmark `expected` answer is never sent to the endpoint.

A formal OpenAPI 3.1 contract is published at [`http/openapi.json`](http/openapi.json).

This bridge is suitable for testing a custom service, webhook/orchestration endpoint, or a runtime that can expose a small JSON HTTP boundary. It does **not** imply compatibility with any specific product until that product has been integrated and tested.

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

## Experiment discipline

A real runtime evaluation should preserve:

- runtime/framework version;
- model/provider/version when applicable;
- agent/prompt/config hash;
- tool/capability manifest hash;
- policy profile;
- raw prediction JSONL;
- SAO benchmark commit/version;
- deterministic result report.

See [`../experiments/README.md`](../experiments/README.md).

## Rules

1. Never expose benchmark `expected` fields to the runtime.
2. Do not customize benchmark truth per runtime.
3. Preserve model/runtime/tool configuration in an experiment manifest.
4. Keep credentials outside the repository.
5. Capture raw predictions before scoring.
6. A runtime failure is a result; do not silently replace it with a reference answer.
7. Adapters may use deterministic guards around a model, but the configuration must be documented.
8. Do not call a protocol/transport smoke test a model or runtime benchmark result.

## Reference adapter

[`guarded_rules.py`](guarded_rules.py) is a deterministic no-model adapter used to test protocol plumbing. CI verifies that its protocol output exactly matches the same baseline generated directly, proving that the adapter transport itself does not alter benchmark decisions.
