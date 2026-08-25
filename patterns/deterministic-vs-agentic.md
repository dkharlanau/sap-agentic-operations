# Deterministic vs Agentic Decision Pattern

Use this pattern before adding an LLM or agent to an enterprise operation.

## Decision matrix

| Problem characteristic | Prefer deterministic | Prefer agentic reasoning |
|---|---|---|
| Exact schema / format validation | Yes | No |
| Required field / status rule | Yes | No |
| Authorization decision with explicit policy | Yes | No |
| Stable identity mapping | Yes | Only to explain unresolved cases |
| Duplicate detection with exact keys | Yes | Possibly for ambiguous candidates |
| Cross-system evidence correlation | Partly | Yes |
| Root-cause hypothesis ranking | No | Yes |
| Interpreting incomplete operational context | No | Yes |
| Selecting next diagnostic step | Partly | Yes |
| Direct high-impact ERP mutation | Guardrails required | Never by reasoning alone |

## Four questions

Before assigning a task to an agent, ask:

1. **Can the decision be stated as an explicit rule?** If yes, implement or validate the rule deterministically.
2. **Does the task require interpreting ambiguous evidence?** If yes, agentic reasoning may add value.
3. **Can a wrong answer change enterprise state?** If yes, separate reasoning from execution and add an approval boundary.
4. **Can the output be verified?** If not, the task needs stronger abstention or human review.

## Hybrid pattern

Many SAP operations are best implemented as a hybrid:

```text
Deterministic extraction
        |
Deterministic validation
        |
Agentic correlation / explanation
        |
Deterministic policy check
        |
Human approval if needed
        |
Narrow deterministic execution
        |
Deterministic verification
```

The agent sits between controls; it does not replace them.

## Anti-patterns

- Asking an LLM to remember configuration rules that can be encoded.
- Giving a model a generic write-capable tool because it is convenient.
- Treating model confidence as authorization.
- Using an agent to compensate for missing object identity.
- Executing a recommendation before verifying the current state.
- Hiding deterministic validation failures inside a natural-language summary.

## Success criterion

An architecture is stronger when removing the LLM from a deterministic step does not reduce correctness. Agentic reasoning should be reserved for the parts that genuinely need interpretation, correlation, planning, or explanation.
