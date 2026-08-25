# ADR-0005 — Keep the Decision Contract Runtime-Neutral

- Status: Accepted
- Date: 2026-08-25

## Context

SAP/Joule, MCP clients, workflow engines and pro-code agent frameworks evolve quickly. A benchmark coupled to one runtime would measure implementation details instead of enterprise control behavior.

## Decision

SAO-Bench accepts a portable structured decision contract. Any runtime can participate if an adapter emits that contract without changing benchmark cases or expected invariants.

Runtime/model/tool metadata belongs in the experiment manifest, not inside benchmark truth.

## Rejected alternatives

- make SAO a Joule-only benchmark;
- make SAO a LangGraph/n8n framework package;
- allow each adapter to reinterpret expected behavior.

## Consequences

Cross-runtime comparison becomes possible, while adapters must explicitly translate runtime-specific concepts into SAO semantics.

## Reversal criteria

Runtime-specific extensions may be added only as optional layers. The core decision contract remains portable unless a broadly adopted standard provides a strictly better neutral representation.
