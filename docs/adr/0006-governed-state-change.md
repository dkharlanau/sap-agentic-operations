# ADR-0006 — Treat State Change as a Separate Governed Risk Class

- Status: Accepted
- Date: 2026-08-25

## Context

Reading and diagnosing enterprise state is materially different from changing it. A correct recommendation can still become an unsafe write because state, identity, policy or approval changed between reasoning and execution.

## Decision

State-changing operations require a separate envelope with:

- exact canonical object and typed operation;
- capability/risk classification;
- current policy decision;
- scoped approval where required;
- before-state/precondition binding;
- idempotency key;
- expected business postcondition;
- correlation/audit identity;
- compensation/rollback reference where relevant.

Execution must re-check current controls. Planning-time authorization is not sufficient.

## Rejected alternatives

- generic write-capable tool available throughout reasoning;
- approval that binds only to a natural-language request;
- treating HTTP/API success as business success;
- automatic rollback without its own policy/authorization.

## Consequences

Write paths are narrower and more complex, but stale approvals, races, retries and business-state failures become testable.

## Reversal criteria

Supersede only if a different state-change protocol provides equivalent guarantees for scope, freshness, idempotency, postconditions, audit and compensation.
