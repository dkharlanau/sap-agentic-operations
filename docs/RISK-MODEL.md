# Risk Model

SAP Agentic Operations uses two complementary views: **business-impact tiers** and **agentic threat classes**.

The business-impact tier determines how much control is required. The threat class determines what can go wrong.

## Business-impact tiers

| Tier | Example | Default capability | Required controls |
|---|---|---|---|
| R0 — Informational | explain a status or runbook | Read | provenance, access control |
| R1 — Diagnostic | correlate logs, IDocs, master-data state | Read + Recommend | identity resolution, evidence completeness, abstention |
| R2 — Reversible operational change | retry a bounded operation with known compensation | Recommend; Execute only after gate | approval policy, exact preconditions, idempotency, postcondition |
| R3 — Material business-state change | change governed master data, release a business block | Recommend; human approval normally required | SoD, impact analysis, typed write, audit, rollback/compensation |
| R4 — High-impact / irreversible / regulated | destructive, financial, security-sensitive, mass change | Agent execution disabled by default | specialized policy, multi-party approval or deterministic workflow |

Risk is about the operation and context, not the sophistication of the model.

## Threat classes

The repository tracks threat classes that map naturally to current OWASP agentic-security concerns without binding the project to a single taxonomy version.

### T1 — Goal or instruction hijacking

Untrusted retrieved content attempts to alter the agent's goal or policy.

Control: separate evidence from instructions; validate tool outputs; system policy outranks retrieved content.

### T2 — Tool misuse / excessive capability

The agent can call a tool broader than the business operation requires.

Control: typed narrow tools, allow-listed operations, parameter schemas, capability gates.

### T3 — Identity and privilege abuse

The wrong business object or user authority is used.

Control: canonical identity resolution, delegated authorization, scoped credentials, SoD.

### T4 — Memory and context poisoning

Prior agent memory introduces stale or malicious state.

Control: memory provenance, expiry, trust labels, current-state revalidation before decisions.

### T5 — Insecure agent / tool communication

Messages or tool endpoints are accepted without sufficient identity, authorization, or integrity.

Control: authenticated endpoints, explicit scopes, server identity validation, credential isolation.

### T6 — Cascading failure

One uncertain diagnosis triggers multiple downstream actions.

Control: bounded blast radius, no silent capability escalation, transaction boundaries, circuit breakers.

### T7 — Trust exploitation

Model confidence, fluent prose, or prior success is treated as business authorization.

Control: machine-readable policy decisions and approval records independent from model confidence.

### T8 — Stale-state execution

The proposed action was correct when approved but the enterprise object changed before execution.

Control: compare expected before-state/version immediately before write; invalidate stale approvals.

### T9 — Verification failure

The tool call returns success but the intended business outcome is absent or wrong.

Control: business-level postconditions, downstream verification, compensating action.

### T10 — Provenance loss

The result cannot be reconstructed from evidence and policy inputs.

Control: stable evidence references, correlation IDs, decision record, immutable audit where appropriate.

## Evaluation principle

A benchmark case should identify both an R-tier and one or more T-classes. This makes failures interpretable: the score should reveal whether an implementation struggles with identity, stale state, policy, prompt injection, authorization, or verification rather than returning one opaque quality number.
