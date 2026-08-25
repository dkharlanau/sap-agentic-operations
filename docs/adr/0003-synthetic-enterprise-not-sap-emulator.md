# ADR-0003 — Use Synthetic SAP-Shaped Scenarios, Not Proprietary System Emulation

- Status: Accepted
- Date: 2026-08-25

## Context

A public assurance project needs enterprise-realistic failure modes without copying customer data, proprietary SAP behavior, or requiring an SAP tenant for every test.

## Decision

SAO models control properties rather than product internals:

- object identity;
- message ordering and causality;
- source-of-truth authority;
- approvals and policy drift;
- optimistic concurrency;
- idempotency;
- postconditions;
- compensation;
- memory/tool trust.

SAP-shaped scenarios provide domain realism, but the Synthetic Enterprise Lab is explicitly not an S/4HANA emulator.

## Rejected alternatives

- copied production payloads or screenshots;
- reverse-engineered proprietary behavior;
- full SAP-system emulation;
- requiring live SAP access for baseline CI.

## Consequences

Tests are portable, public and safe, but product-specific claims must be separately verified against supported SAP documentation/environments.

## Reversal criteria

Add real-system adapters only when legal, supported, reproducible test environments exist. Keep the synthetic core even then.
