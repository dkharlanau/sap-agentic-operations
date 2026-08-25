# SAP Architecture Lens — August 2026

This note records a small set of current SAP architectural directions that materially affect SAO. It is not a product catalog. Each source is included only where it changes an architectural decision.

Reviewed: 2026-08-25.

## 1. Extensibility is a placement decision, not a slogan

SAP's current BTP Guidance Framework explicitly supports a combination of **on-stack** and **side-by-side** extensibility depending on the use case. On-stack options cover adaptations, custom UI/full-stack applications and custom APIs; side-by-side on BTP covers full-stack applications, automation and digital workspaces.

Source:

- SAP Help Portal — Getting Started with Extensibility: https://help.sap.com/docs/sap-btp-guidance-framework/extension-architecture-guide/getting-started-with-extensibility
- SAP Help Portal — Clean Core Extensibility for SAP Cloud ERP: https://help.sap.com/docs/erp-transformation-with-itc/buildable-map/clean-core-extensibility-for-sap-cloud-erp

### SAO consequence

`clean core` should not become the mechanical rule “everything outside S/4.”

The architecture question remains:

- does the invariant need atomic transactional behavior in core?;
- can side-by-side execution preserve the same business guarantee?;
- what lifecycle, availability, latency and authorization boundary is created by moving the logic?;
- is the extension using supported contracts rather than internal coupling?

SAO therefore treats extension placement as an explicit ADR/trade-off rather than a quality label.

## 2. Event-driven architecture is part of a holistic integration strategy

SAP's Integration Architecture Guide describes event-driven architecture as a way to create decoupled, responsive systems and explicitly connects EDA with clean-core side-by-side extension patterns. It also warns against treating EDA as an isolated discipline: event mediation, API management, mapping/transformation and other integration styles remain part of the broader integration platform.

Sources:

- SAP Help Portal — Event-driven Architecture: https://help.sap.com/docs/sap-btp-guidance-framework/integration-architecture-guide/event-driven-architecture
- SAP Help Portal — Event Mediation: https://help.sap.com/docs/sap-btp-guidance-framework/integration-architecture-guide/event-mediation
- SAP Help Portal — Use SAP Integration Suite to Explore EDA in the Enterprise: https://help.sap.com/docs/sap-btp-guidance-framework/integration-architecture-guide/use-sap-integration-suite-to-explore-eda-in-enterprise

### SAO consequence

SAO does not treat `event` as automatically superior to API/message/batch.

The integration contract must first establish:

- command vs immutable fact;
- need for synchronous business result;
- causal identity;
- ordering requirements;
- duplicate/replay semantics;
- idempotency;
- business acknowledgement;
- operational recovery.

Only then should the transport/pattern be selected.

## 3. Event infrastructure needs operational evidence, not only decoupling

SAP Integration Suite, advanced event mesh documentation includes event streaming, event management, monitoring and insights as platform capabilities.

Source:

- SAP Help Portal — What Is SAP Integration Suite, Advanced Event Mesh?: https://help.sap.com/docs/sap-integration-suite/advanced-event-mesh

### SAO consequence

Event-driven integration increases the need for strong causality and observability. A support analyst must be able to distinguish:

```text
business event created
-> event published
-> broker delivery
-> consumer processing
-> business postcondition
```

Broker delivery alone is not the business outcome.

## 4. Data ownership is becoming a first-class architecture concept

SAP Business Data Orchestration documentation describes explicit data ownership configuration: a designated system can be the authoritative source for a business object type, with scope and create/change/delete implications for connected systems. SAP also cautions that documentary ownership only becomes enforceable when connected systems implement the corresponding behavior.

Source:

- SAP Help Portal — Manage Data Ownership: https://help.sap.com/docs/master-data-integration/sap-business-data-orchestration-8ce78b673ef04cc1bcfeb01c93ef7885/manage-data-ownership

### SAO consequence

This reinforces three distinctions used throughout SAO:

1. documented authority is not necessarily technically enforced authority;
2. ownership scope must be explicit;
3. source-of-truth claims must be tied to object/attribute/business scope and effective time.

For agentic operations, an LLM should never infer authority from data location alone.

## 5. Enterprise architecture itself is becoming an operational system of record

SAP's clean-core architecture guidance positions SAP LeanIX as an architectural system of record for BTP landscapes, linking extensions/integrations to business capabilities/processes and making compliance/deviations visible.

Source:

- SAP Help Portal — Clean Core Extensibility for SAP Cloud ERP: https://help.sap.com/docs/erp-transformation-with-itc/buildable-map/clean-core-extensibility-for-sap-cloud-erp

### SAO consequence

Architecture metadata should become machine-readable evidence rather than stay only in slide decks.

This is one motivation for SAO's experimental [`enterprise-context.schema.json`](../schemas/enterprise-context.schema.json):

```text
business process
  -> invariant
  -> business object / authority
  -> system
  -> integration
  -> deterministic control
  -> evidence
  -> operational owner
  -> agent capability
```

SAO is not attempting to replace LeanIX or an EA repository. The goal is narrower: make enough context portable for an assurance/evaluation scenario to reason about enterprise boundaries without inventing them from prose.

## Architectural thesis

The strongest enterprise-agent architecture is not the one with the most autonomous capability.

It is the one where we can inspect, for every important decision:

- **what business truth is at risk;**
- **who owns it;**
- **which system persists it;**
- **which integration distributes it;**
- **which deterministic controls protect it;**
- **what evidence proves the current state;**
- **what the agent is allowed to infer;**
- **what the agent is not allowed to decide;**
- **how failure is recovered without creating a second failure.**

That is the SAP/enterprise architecture layer SAO should continue to deepen.
