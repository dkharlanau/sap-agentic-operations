# Experimental Conformance Profiles

These profiles are **project conventions**, not an industry standard or SAP certification. They make implementation claims precise while SAO gathers external evidence.

A claim should name both profile and benchmark version, for example:

```text
SAO-Diagnostic / SAO-Bench v0.2
```

## SAO-Diagnostic

For read/recommend agents.

Required:

- emit the SAO decision contract;
- preserve evidence references for recommendations/resolutions;
- block cross-system comparison when identity is unresolved/ambiguous;
- represent missing evidence explicitly;
- separate deterministic findings from hypotheses;
- `execution_allowed=false` for all outputs;
- pass the applicable R1 diagnostic benchmark cases.

## SAO-Approval

Adds approval-bound proposals.

Required in addition to `SAO-Diagnostic`:

- identify requested business-risk tier;
- produce `approval_required` where policy demands it;
- bind approval proposal to exact object, operation, parameters, and before-state;
- invalidate approval when material proposal/current state changes;
- pass applicable approval/stale-state cases.

## SAO-Write-Safe

For implementations capable of mutating enterprise state.

Required in addition to `SAO-Approval`:

- state changes only through typed allow-listed operations;
- write-envelope equivalent to `schemas/write-envelope.schema.json`;
- authorization/policy evaluated outside model confidence;
- immediate precondition re-check before execution;
- idempotency protection;
- business-level postcondition verification;
- audit correlation ID;
- rollback or documented compensating path for supported R2/R3 operations;
- no fallback to broader tools after typed-tool failure;
- pass applicable R2/R3 state-change cases.

R4 execution is outside the default SAO conformance scope.

## SAO-Auditable

For implementations that preserve a reconstructable decision trail.

Required:

- evidence IDs and provenance;
- object identity/mapping state;
- decision class;
- deterministic policy result;
- selected actions and rejected/blocked reason;
- model/runtime identity where model reasoning was used;
- correlation across proposal, approval, execution, and verification;
- timestamped audit record.

## SAO-Adversarial

For implementations tested against agentic trust-boundary failures.

Required:

- untrusted retrieved/tool content cannot become instructions;
- historical memory cannot override current contradictory evidence;
- tool failure cannot trigger privilege/capability escalation;
- inter-agent/tool inputs have explicit trust handling;
- pass the current T1/T2/T4/T6 adversarial subset.

## Conformance is capability-scoped

An implementation can conform to `SAO-Diagnostic` without supporting writes. This is deliberate: a strong diagnostic agent with explicit abstention is preferable to an unnecessarily autonomous agent.

## What conformance does not mean

A passing profile does not prove:

- SAP product certification;
- regulatory compliance;
- security of the underlying model/provider/runtime;
- correctness for a specific customer's processes;
- production readiness without environment-specific testing.

Profiles become stronger only when benchmark coverage and independent implementation evidence grow.
