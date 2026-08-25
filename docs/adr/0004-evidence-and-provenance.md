# ADR-0004 — Require Evidence and Provenance for Concrete Decisions

- Status: Accepted
- Date: 2026-08-25

## Context

Agent context can mix authoritative state, stale memory, retrieved documents, tool output, user text and model hypotheses. Without provenance, a fluent conclusion cannot be audited or safely reused.

## Decision

Concrete SAO decisions carry evidence references. Evidence should preserve, where relevant:

- source/system/type;
- canonical object identity;
- observation and retrieval time;
- trust class;
- content hash or stable reference;
- provenance chain.

`resolved_read_only`, `recommendation`, `approved_for_execution` and `execution_result` are incomplete without evidence references.

## Rejected alternatives

- treat everything in the prompt/context window as equal evidence;
- store only final natural-language rationale;
- use model confidence as evidence strength.

## Consequences

Auditability and root-cause analysis improve, but adapters must preserve metadata instead of flattening all inputs into text.

## Reversal criteria

Only supersede if an alternative offers equal or stronger traceability from decision back to observable source facts.
