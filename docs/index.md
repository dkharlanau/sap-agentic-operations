---
title: SAP Agentic Operations — Architecture & Assurance Lab
description: Enterprise architecture, SAP operations, system analysis and executable assurance patterns for AI agents around systems of record.
---

# SAP Agentic Operations

## Architecture & Assurance Lab

**How do we let AI reason around SAP without letting probabilistic reasoning become invisible authority over enterprise state?**

SAP Agentic Operations (SAO) is an independent public lab by **Dzmitryi Kharlanau** exploring that question through SAP-shaped operational scenarios, architecture contracts, executable evaluations and stateful failure simulation.

The project is deliberately not another “chat with SAP” demo.

It focuses on the parts that become difficult in real enterprises:

**identity · data/process authority · integration semantics · deterministic policy · approvals · stale state · idempotency · business postconditions · cutover · recovery · auditability**

---

## Choose a professional lens

### SAP / Enterprise Architect

Start with the decisions behind the boxes.

- [The Architect's Decision Spine](./ARCHITECT-DECISION-SPINE.md)
- [Enterprise Integration Contract](./INTEGRATION-CONTRACT.md)
- [Agent Identity & Authorization](./AGENT-IDENTITY-AUTHORIZATION.md)
- [SAP Agent Tool Contract Design](./SAP-AGENT-TOOL-CONTRACTS.md)
- [Cutover & Recovery Architecture](./CUTOVER-RECOVERY.md)
- [Architecture Fitness Functions](./ARCHITECTURE-FITNESS-FUNCTIONS.md)
- [Enterprise Architecture Anti-Patterns](./ENTERPRISE-ANTI-PATTERNS.md)

Core question:

> If this component, mapping, approval, integration or agent is wrong, what is the first deterministic control that prevents incorrect business state?

### SAP Consultant / AMS Lead

Start with operations, workshops and recovery.

- [SAP Consulting Review Cards](./CONSULTING-REVIEW-CARDS.md)
- [SAP / Enterprise Operations Failure Atlas](./SAP-OPERATIONS-FAILURE-ATLAS.md)
- [Agentic SAP AMS Operating Model](./AGENTIC-AMS-OPERATING-MODEL.md)
- [SAP Agentic Opportunity Map](./SAP-AGENTIC-OPPORTUNITY-MAP.md)
- [Enterprise Agent Readiness Ladder](./ENTERPRISE-AGENT-READINESS-LADDER.md)

Core question:

> Can the solution be diagnosed, operated, recovered and handed over without relying on one experienced person remembering how it works?

### System Analyst

Start with traceability and evidence.

- [Business-to-System Traceability](./BUSINESS-TRACEABILITY.md)
- [Enterprise Integration Contract](./INTEGRATION-CONTRACT.md)
- [Architecture Fitness Functions](./ARCHITECTURE-FITNESS-FUNCTIONS.md)

Core question:

> What exactly must remain true, in which business scope, and what observable evidence proves that the systems preserved it?

---

## Architecture as code

SAO includes a small machine-readable **Enterprise Context Graph** that connects:

```text
business process
  -> invariant
  -> business object
  -> authority
  -> system
  -> integration
  -> control
  -> evidence
  -> agent boundary
  -> cutover state
```

The goal is not to replace an EA repository. The goal is to make enough architecture context inspectable by humans, CI and agent evaluations.

Example:

`examples/enterprise-context/customer-replication.json`

Validate locally:

```bash
python sao.py context-check \
  examples/enterprise-context/customer-replication.json \
  --strict
```

Compare two architecture snapshots:

```bash
python sao.py context-diff before.json after.json --json
```

High-risk drift includes changes such as:

- business/data authority moved;
- integration interaction semantics changed;
- idempotency or correlation semantics changed;
- business postcondition changed;
- protecting control removed;
- agent capability increased;
- execution gate changed;
- cutover authority/watermark changed.

---

## Executable assurance

### SAO-Bench

The current development corpus contains **51 synthetic enterprise-control cases** across:

- core control scenarios;
- integration operations;
- master data / MDG;
- O2C / P2P business processes;
- agent security;
- state-changing operations.

The benchmark evaluates control decisions, not writing style.

### Synthetic Enterprise Lab

A stateful simulator exercises:

- identity/mapping drift;
- policy changes;
- delayed/duplicated messages;
- stale approvals;
- concurrency;
- idempotency;
- failed business postconditions;
- compensation;
- untrusted operational memory.

### Dynamic adversarial variants

Seeded hidden variants reduce fixed-case memorization risk while keeping benchmark truth deterministic.

---

## A few architecture anti-patterns

**Green Interface Fallacy**  
A technically green interface is treated as proof that the business state is correct.

**Source of Truth by Habit**  
Authority is inferred from where the field has historically lived.

**Retry Button Architecture**  
Every integration failure is assumed to be recoverable by sending the message again.

**Similarity Is Identity**  
The closest-looking BP/customer/vendor is treated as the same business entity.

**Prompt as Business Rule**  
A probabilistic instruction is used where deterministic policy should exist.

**Agent as Missing Integration Layer**  
AI is used to hide weak identity, mappings, APIs and ownership rather than make those contracts explicit.

[Read the full anti-pattern catalog](./ENTERPRISE-ANTI-PATTERNS.md).

---

## The operating thesis

The interesting enterprise-AI problem is not whether a model can call an API.

It is whether the organization can produce inspectable evidence for:

- **which business truth is at risk;**
- **who owns it;**
- **which system persists it;**
- **which identity maps it across systems;**
- **which controls protect it;**
- **what evidence proves current state;**
- **what the agent may infer;**
- **what the agent must never decide;**
- **what exact gate permits state change;**
- **how the business outcome is verified;**
- **how failure is recovered without creating a second failure.**

That is the layer SAO is trying to make executable.

---

## About

Maintained by **Dzmitryi Kharlanau**  
SAP Transformation · Enterprise Operations · Agentic AI

- [GitHub repository](https://github.com/dkharlanau/sap-agentic-operations)
- [Professional site](https://dkharlanau.github.io/)
- [LinkedIn](https://www.linkedin.com/in/dkharlanau/)

SAO is independent work. It is not an official SAP project or certification and does not use client data.
