# ADR-0002 — Separate Probabilistic Reasoning from Deterministic Policy and Execution

- Status: Accepted
- Date: 2026-08-25

## Context

LLMs are useful for correlating ambiguous evidence, but identity resolution, authorization, policy enforcement and state mutation require stronger guarantees.

## Decision

SAO architectures separate:

1. evidence retrieval;
2. deterministic identity/policy validation;
3. probabilistic reasoning/recommendation;
4. approval;
5. typed execution;
6. deterministic verification/audit.

A model recommendation never becomes authorization implicitly.

## Rejected alternatives

- one agent prompt owns policy + reasoning + execution;
- generic admin/RFC/HTTP tools exposed as fallback;
- model confidence used as an approval signal.

## Consequences

This introduces more components and contracts, but makes failures observable, testable and revocable.

## Reversal criteria

Supersede only if another architecture provides equivalent or stronger deterministic enforcement and auditability without collapsing model output into authority.
