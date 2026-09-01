# Product Roadmap

## From assurance lab to a useful SAP operations toolkit

SAP Agentic Operations now has two layers:

1. a **practical local toolkit** for evidence, incident analysis, reconciliation and triage;
2. an **architecture and agent-assurance lab** underneath it.

The practical layer is now usable enough to test with external SAP practitioners.

From this point forward, roadmap priority is driven by:

- time-to-first-value;
- real input formats;
- external field reports;
- repeated SAP operating problems;
- evidence that the tool changes or accelerates a real investigation.

It is **not** driven by the number of framework documents, benchmark cases, agent integrations or architectural concepts.

---

# Product thesis

SAO should become a **local-first, evidence-first toolkit for diagnosing, reconciling, validating and safely recovering SAP-heavy enterprise operations**.

The assurance lab remains the engine underneath it.

Core promise:

> **Turn fragmented SAP operational evidence into an inspectable diagnosis, a safe recovery decision, and a verified business outcome.**

SAO should not try to replace:

- SAP Cloud ALM monitoring;
- SAP Integration Suite monitoring / AI error assistance;
- Migration Cockpit / Data Transition Validation;
- SAP AI Agent Hub;
- Joule Studio;
- generic SAP MCP servers;
- cutover scheduling/project-management products.

The practical niche is the layer between **observation and a safe operational decision**.

```text
monitor / export / event / snapshot
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
 diagnosis / reconciliation / triage
             |
 missing evidence + safe recovery class
             |
             v
 verified business outcome
```

---

# Current state — Practical Toolkit 0.4.0-alpha.3

## Shipped through Alpha 2

### Installable CLI

```bash
python -m pip install .
sao demo
```

Zero runtime dependencies; Python 3.11+.

### Evidence Pack v0.1

```text
incident/
  incident.json
  source_changes.csv
  messages.csv
  target_state.csv
  identity_map.csv
```

Commands:

```bash
sao incident init ./incident --incident-id INC-001
sao incident validate ./incident
sao incident analyze ./incident
```

### Deterministic Incident Analyzer

Current failure semantics include:

- old successful message does not prove a newer change replicated;
- current outbound event not proven;
- unresolved/ambiguous identity;
- event/current mapping drift;
- message target identity mismatch;
- technical message failure;
- technical success + business rejection;
- stale target observation;
- current event + wrong target business state;
- complete evidence chain to verified business state.

### Nine bundled operational scenarios

```bash
sao demo --list
```

All nine are exercised through the installed CLI in product CI.

### One-CSV Quick Check

```bash
sao quickcheck demo
sao quickcheck analyze incidents.csv
```

Each row reuses the same Incident Analyzer; there is no separate simplified root-cause engine.

### Batch triage

```bash
sao batch ./incident-packs --output ./triage
```

CSV + JSON + Markdown aggregation by failure class.

### Local Workbench

```bash
sao workbench ./incident
```

Read-only local evidence chain, findings, missing evidence, safe/unsafe actions and resolution condition.

### Semantic master-data reconciliation

```bash
sao reconcile demo
sao reconcile analyze ./reconciliation
```

Current minimum semantics:

- explicit identity;
- per-attribute authority;
- source/target snapshot freshness;
- refusal to overwrite newer non-authoritative state from a stale authority snapshot.

### Explicit export normalization

```bash
sao normalize demo
sao normalize csv --table messages --input export.csv --mapping map.json --output messages.csv
```

Supports explicit column mappings, constants and value maps such as `53 -> success`, `51 -> failed`.

### Adoption loop

GitHub includes a privacy-safe **SAO practical field report** template so practitioners can report usefulness or incorrect classifications without exposing client data.

---

# The immediate roadmap changed

Before Alpha 1, the next problem was missing functionality.

After Alpha 1, the next problem is **external validity**.

The highest-value next input is not another feature. It is a practitioner saying:

> “I had this SAP operational problem, these were the evidence types I had, SAO classified it this way, and this part was useful/wrong/missing.”

The first release-quality loop therefore becomes:

```text
external field case
       ↓
privacy-safe failure semantics
       ↓
Evidence Pack / Quick Check
       ↓
SAO conclusion
       ↓
practitioner challenge / confirmation
       ↓
new deterministic invariant or corrected rule
       ↓
regression test / benchmark case
```

---

# P0 — Field validation

## Goal

Get **3 independent SAP practitioners** to complete one practical workflow.

Good target roles:

- SAP AMS/support consultant;
- integration consultant;
- MDG/master-data consultant;
- system analyst;
- migration/cutover lead.

## Success evidence

For each user capture only sanitized information:

- job to be done;
- evidence types available;
- workflow used;
- SAO classification;
- whether it accelerated or changed the investigation;
- missing/wrong rule;
- input friction.

## Exit criteria

Before another major framework layer:

- 3 external completed practical runs;
- at least 1 report where SAO was wrong or incomplete;
- at least 1 real export format normalized;
- at least 1 failure fixture or rule improved from field feedback.

A false positive discovered by a practitioner is more valuable now than another ten synthetic benchmark cases.

---

# P1 — Integration Operations Pack

This remains the strongest adoption wedge.

## Why

Integration incidents naturally produce fragmented evidence:

- source change;
- IDoc/AIF/message state;
- middleware processing;
- mapping/version;
- target identity;
- business acknowledgement;
- target business state.

Monitoring can show an error. SAO should answer:

> **Which business change is affected, which evidence is causally related, what recovery is safe, and what proves recovery?**

## Already available

- nine synthetic failure scenarios;
- canonical message evidence format;
- explicit export normalization;
- one-row Quick Check;
- multi-file Evidence Pack;
- batch triage.

## Next additions — only when grounded by field use

- out-of-order events;
- duplicate/replay semantics;
- unknown commit after timeout;
- value-mapping drift;
- source change with no outbound event;
- multi-message causal chains;
- OpenTelemetry import.

## Cloud ALM integration direction

Use Cloud ALM honestly:

- Generic Integration Monitoring Analytics for discovery / filtering / aggregate visibility;
- Raw Data Outbound Logs / OpenTelemetry-style evidence for detailed message/exception ingestion where configured;
- transform data into canonical SAO evidence instead of coupling diagnosis to Cloud ALM payloads.

Do not claim a universal Cloud ALM incident collector until the required data is proven available for the target scenario.

---

# P1 — Master Data Reconciliation v0.2

Alpha 1 proves the minimum semantic model.

Next high-value classifications:

- attribute-specific authority by business scope;
- value-mapping version drift;
- pending governance change vs active value;
- duplicate candidate ambiguity;
- event-time identity mapping;
- scoped business exceptions;
- local vs central ownership;
- target change origin.

The core rule remains:

> A mismatch is not automatically an error, and authority without freshness is not enough to justify overwrite.

---

# P2 — Workbench from report viewer to import workflow

Current Workbench is deliberately small: a local read-only incident report.

Only expand it if CLI/Quick Check users confirm UI friction.

Potential v0.2:

- drag/drop CSV;
- choose mapping file;
- Evidence Pack validation errors;
- timeline view;
- multi-incident batch table;
- reconciliation table;
- export sanitized report.

Do not turn it into another incident-management platform.

---

# P2 — Cutover Integrity Pack

Issue #19 remains the most differentiated architecture workflow.

Question:

> **Did the authority transition preserve business state and event causality?**

Use the Synthetic Enterprise Lab for:

- migration snapshot + queued-event double apply;
- missing freeze/delta change;
- old interface draining after authority transition;
- mapping version changes between extraction and recovery;
- target state newer than migration snapshot;
- stale pre-cutover runbook;
- rollback after external business effects exist.

This is not a scheduling tool. It is a state-continuity and recovery-assurance pack.

---

# P2 — Architecture outputs and traceability

The Enterprise Context Graph already supports fitness checks and architecture diff.

Issue #18 should connect:

```text
business invariant
  -> architecture control
  -> negative/positive requirement
  -> practical failure class
  -> benchmark/simulator test
  -> evidence artifact
  -> operational owner
```

Before adding more architecture theory, generate useful outputs:

- authority matrix;
- integration catalog;
- recovery ownership matrix;
- control/evidence coverage;
- Mermaid/context diagram;
- change-impact report.

---

# P3 — Agent assurance as a downstream practical pack

Do not lead product development with another agent benchmark integration.

The better loop is:

```text
field failure semantics
   -> deterministic safe decision
   -> synthetic regression case
   -> external agent runtime
   -> SAO-Bench / SAO-Trace
```

This ties AI evaluation to real SAP operating semantics instead of a disconnected benchmark.

Issue #3 remains useful after practical packs have field evidence.

---

# Benchmark foundation

SAO-Bench 0.3 is still development state.

Open release work:

- #17 semantic review of all 51 cases;
- #7 benchmark freeze/version discipline.

Do not conflate:

- Practical Toolkit `0.4.0-alpha.3`;
- SAO-Bench `0.3-dev`.

The product alpha can be tested while benchmark truth receives a more deliberate human review.

---

# Distribution roadmap

## Alpha 2

Current:

- package metadata;
- console command `sao`;
- product CI through installed package;
- reproducible demos;
- versioned practical formats;
- changelog;
- field-report template.

Remaining distribution work:

- GitHub prerelease/tag `v0.4.0-alpha.3`;
- optional PyPI publication only after the package namespace/distribution policy is intentionally chosen;
- short screen recording / terminal walkthrough;
- first external install on a clean machine.

Do not publish to package registries merely for vanity. First confirm that the command/package name should remain stable.

---

# What not to build without evidence

Avoid these unless users demand them:

- generic SAP MCP server;
- full monitoring platform;
- generic RAG/chat UI;
- production write automation;
- AI root-cause summaries without deterministic evidence;
- generic field-by-field CSV validator;
- cutover scheduling product;
- plugin SDK before multiple practical packs are used;
- more framework documentation without executable/user-facing output.

---

# Adoption metrics

## Time to first value

Target:

> A new user gets a useful bundled report in under **5 minutes**.

## Practical completion

Track:

- demo completed;
- own Quick Check completed;
- own Evidence Pack completed;
- Workbench opened;
- reconciliation completed;
- mapping file reused.

## Utility

A report should answer at least one question the source tool did not answer directly:

- Which current business change is affected?
- Is identity resolved?
- Is the message causally related to that change?
- Is replay/retry justified?
- Is the target business state actually correct?
- What evidence is missing?
- Which recovery class is justified?
- What proves resolution?

## Trust

- no client data in repository examples;
- deterministic rules are inspectable;
- evidence gaps are explicit;
- no production write is required for core workflows;
- technical success is not silently upgraded to business success.

---

# Product 1.0 criterion

SAO 1.0 should mean that the tool is **used**, not merely large.

A reasonable 1.0 bar:

- straightforward installation;
- at least three practical SAP workflows;
- at least one supported external evidence source;
- useful local Workbench;
- reports remain useful without an LLM;
- architecture/evidence contracts are stable;
- real external practitioners completed tasks with it;
- external field feedback changed at least one diagnostic rule;
- external contributors/reviewers challenged the failure semantics;
- agent assurance is demonstrably connected to practical enterprise failure patterns.

The one-sentence test remains:

> **SAO helps SAP teams turn fragmented operational evidence into a reproducible diagnosis, a safe recovery decision, and a verified business outcome.**
