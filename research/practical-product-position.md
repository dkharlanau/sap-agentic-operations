# Practical Product Boundary — 2026-08

This note records the product boundary behind Practical Toolkit 0.4.0-alpha.1.

## What the ecosystem already does well

SAP and the surrounding ecosystem already provide substantial capability for:

- integration monitoring;
- message/error visibility;
- AI-assisted error explanation in integration tooling;
- S/4 migration/data validation;
- agent development/orchestration;
- agent inventory/governance;
- SAP/MCP connectivity.

SAO should not compete by recreating those surfaces.

## The remaining operational gap

Monitoring and technical success still leave a harder cross-system question:

> **Which current business change is affected, which evidence is causally related, which identity/authority applies, what recovery action is justified, and what business state proves recovery?**

This gap is especially visible when evidence is distributed across:

- source change history;
- IDoc/AIF/message logs;
- middleware;
- identity/value mappings;
- target-system observations;
- runbooks/tickets;
- cutover state.

## SAO product boundary

SAO should own:

```text
canonical evidence
   -> identity / authority
   -> causality / freshness
   -> deterministic failure classification
   -> safe/unsafe recovery boundary
   -> business postcondition
   -> reproducible report
```

SAO should integrate with, not replace, monitoring and source systems.

## Cloud ALM implication

Cloud ALM Integration Monitoring Analytics is appropriate for discovery/aggregate views. Detailed causal incident evidence may require raw message/exception exports such as Cloud ALM raw-data outbound/OpenTelemetry-style flows where configured.

Therefore the first SAO Cloud ALM integration should not pretend that aggregate monitoring metrics are a complete Incident Pack.

## MCP implication

There are already numerous public SAP MCP servers around OData, HANA, CPI, SAP GUI, ABAP/ADT and other surfaces.

SAO's differentiation should not be another generic SAP tool gateway. Tool connectivity can later feed evidence or execute narrowly typed recovery actions, but the product value remains the decision/evidence layer.

## Migration / data-validation implication

SAP and third-party tools already perform source/target comparisons. SAO reconciliation should stay differentiated by:

- canonical identity;
- attribute-level authority;
- temporal freshness;
- mapping/version semantics;
- safe correction boundaries;
- evidence-backed explanation.

## Product rule

> **Do not build a feature because SAO can technically implement it. Build it when it closes a recurring evidence-to-decision gap that existing SAP tooling leaves open.**
