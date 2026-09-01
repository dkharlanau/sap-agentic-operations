---
title: SAP Agentic Operations — Practical Toolkit & Architecture Lab
description: Local-first SAP operations evidence, incident analysis, reconciliation, enterprise architecture and agent assurance.
---

# SAP Agentic Operations

## Practical Toolkit & Architecture Lab

**From fragmented SAP evidence to a reproducible diagnosis, a safe next action, and a verified business outcome.**

SAP Agentic Operations (SAO) is an independent public project by **Dzmitryi Kharlanau**.

The practical toolkit is now the front door. The architecture and agent-assurance lab sits underneath it.

---

## Try the practical alpha

```bash
git clone https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations
python -m pip install .
sao demo
```

Current practical version: **0.4.0-alpha.3**.

The default demo deliberately models a dangerous support shortcut: a successful old message exists, but it does not prove that a newer authoritative business change replicated.

The output separates:

- observed evidence;
- deterministic findings;
- missing evidence;
- safe next actions;
- actions not justified by current evidence;
- the business postcondition required before resolution.

---

## Four ways to use SAO today

### 1. Incident analysis

```bash
sao incident init ./incident --incident-id INC-001
sao incident validate ./incident
sao incident analyze ./incident
```

Use a small local Evidence Pack containing source changes, messages, target state and identity mappings.

[Evidence Pack v0.1](./EVIDENCE-PACK.md)

### 2. One-CSV Quick Check

```bash
sao quickcheck demo
sao quickcheck analyze my-incidents.csv
```

Useful when a consultant already works from one Excel-style list. Quick Check uses the same diagnostic engine as the full Evidence Pack.

[Quick Check](./QUICKCHECK.md)

### 3. Semantic master-data reconciliation

```bash
sao reconcile demo
sao reconcile analyze ./reconciliation
```

SAO does not stop at “source != target.” It considers canonical identity, attribute authority and snapshot freshness before deciding whether a difference is actually an error.

[Semantic reconciliation](./RECONCILIATION.md)

### 4. Local Workbench

```bash
sao workbench ./incident
```

A read-only local view of the evidence chain, diagnosis, evidence gaps, safe actions and resolution condition.

No cloud account is required for the core workflow.

---

## Bring normal SAP/Excel exports

Real exports do not use canonical column names.

```bash
sao normalize demo

sao normalize csv \
  --table messages \
  --input we02-export.csv \
  --mapping messages.mapping.json \
  --output incident/messages.csv
```

Explicit mappings can translate source column names, constants and technical values such as IDoc-style statuses.

[Normalizing exports](./NORMALIZING-EXPORTS.md)

## Review external research without turning it into operational truth

```bash
sao research validate examples/research-evidence/sti-enterprise-agents.json
sao research review examples/research-evidence/sti-enterprise-agents.json \
  --output /tmp/enterprise-agent-review.md
```

The portable handoff preserves claim provenance and an explicit non-operational boundary. It cannot authorize execution or stand in for incident evidence.

[External research evidence handoff](./RESEARCH-EVIDENCE-HANDOFF.md)

The design rule is simple:

> **Connectors may change; evidence semantics should remain stable.**

---

## The practical evidence chain

```text
MDG / S4 / IDoc / AIF / CPI / Excel / OTel
                    |
                    v
              canonical evidence
                    |
         identity + authority
         causality + freshness
         mapping + message state
         business postcondition
                    |
                    v
          diagnosis / reconciliation
                    |
         safe recovery boundaries
                    |
                    v
            verified outcome
```

SAO deliberately does not equate:

```text
HTTP 200
IDoc 53
middleware green
API success
```

with:

```text
business problem resolved
```

---

## Choose a professional lens

### SAP / Enterprise Architect

Focus on the decisions behind the boxes:

- [Architecture entry point](../ARCHITECTURE.md)
- [Architect's Decision Spine](./ARCHITECT-DECISION-SPINE.md)
- [Enterprise Integration Contract](./INTEGRATION-CONTRACT.md)
- [Agent Identity & Authorization](./AGENT-IDENTITY-AUTHORIZATION.md)
- [SAP Agent Tool Contract Design](./SAP-AGENT-TOOL-CONTRACTS.md)
- [Cutover & Recovery Architecture](./CUTOVER-RECOVERY.md)
- [Architecture Fitness Functions](./ARCHITECTURE-FITNESS-FUNCTIONS.md)

Core question:

> If this component, mapping, integration or agent is wrong, what deterministic boundary prevents incorrect business state?

### SAP Consultant / AMS Lead

Focus on repeatable diagnosis and recovery:

- [Evidence Pack](./EVIDENCE-PACK.md)
- [SAP Operations Failure Atlas](./SAP-OPERATIONS-FAILURE-ATLAS.md)
- [Agentic SAP AMS Operating Model](./AGENTIC-AMS-OPERATING-MODEL.md)
- [SAP Consulting Review Cards](./CONSULTING-REVIEW-CARDS.md)

Core question:

> Can the incident be diagnosed, recovered and handed over without one experienced person remembering the hidden process?

### System Analyst

Focus on traceability:

- [Business-to-System Traceability](./BUSINESS-TRACEABILITY.md)
- [Enterprise Integration Contract](./INTEGRATION-CONTRACT.md)
- [Architecture Fitness Functions](./ARCHITECTURE-FITNESS-FUNCTIONS.md)

Core question:

> What exactly must remain true, in which scope, and what evidence proves that the systems preserved it?

---

## Architecture as code

SAO includes a small machine-readable Enterprise Context Graph:

```text
process
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

Validate:

```bash
python sao.py context-check \
  examples/enterprise-context/customer-replication.json \
  --strict
```

Compare two architecture snapshots:

```bash
python sao.py context-diff before.json after.json --json
```

---

## Under the toolkit: executable assurance

SAO also contains:

### SAO-Bench

51 synthetic enterprise-control cases across integration operations, master data, business process, agent security and state-changing operations.

### Synthetic Enterprise Lab

Stateful failure simulation for identity/mapping drift, policy changes, delayed/duplicate messages, stale approvals, idempotency, postconditions and compensation.

### SAO-Trace

Deterministic checks over observable runtime action sequences.

These layers are no longer the product front door. Their role is to preserve and test the enterprise-control semantics used by the practical workflows.

---

## A few useful anti-patterns

**Green Interface Fallacy**  
Technical success is treated as proof that business state is correct.

**Source of Truth by Habit**  
Authority is inferred from where data historically lived.

**Retry Button Architecture**  
Every integration failure is assumed to be fixed by replay.

**Similarity Is Identity**  
The closest-looking BP/customer/vendor is treated as the same entity.

**Prompt as Business Rule**  
Probabilistic model instructions are used where deterministic policy belongs.

[Full anti-pattern catalog](./ENTERPRISE-ANTI-PATTERNS.md)

---

## What happens next

Alpha 2 is intentionally a stopping point for feature accumulation.

The next high-value evidence is **field use**:

- Did a real SAP practitioner complete a Quick Check or Evidence Pack?
- Was the diagnosis useful?
- Which evidence was hard to prepare?
- Which classification was wrong or incomplete?
- Which export format should SAO normalize next?

Use the repository's **SAO practical field report** issue form with sanitized information only.

[Product roadmap](../ROADMAP.md)

---

## About

Maintained by **Dzmitryi Kharlanau**  
SAP Transformation · Enterprise Operations · Agentic AI

- [GitHub repository](https://github.com/dkharlanau/sap-agentic-operations)
- [Professional site](https://dkharlanau.github.io/)
- [LinkedIn](https://www.linkedin.com/in/dkharlanau/)

SAO is independent work. It is not an official SAP project or certification and does not use client data in public examples.
