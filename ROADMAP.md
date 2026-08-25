# Product Roadmap

## From assurance lab to a useful SAP operations toolkit

SAP Agentic Operations has already proved that it can model enterprise-agent controls, benchmark decisions, simulate state-changing failures, and represent architecture as code.

The next problem is different:

> **Can a SAP consultant, support analyst, system analyst, integration lead, or architect use SAO to solve a real task within minutes?**

From this point forward, product progress is measured primarily by **time-to-first-value, useful outputs, real input formats, external use, and repeatability** — not by the number of framework documents or benchmark cases.

---

## Product thesis

SAO should become a **local-first, evidence-first toolkit for diagnosing, reconciling, validating, and safely recovering SAP-heavy enterprise operations**.

The assurance lab remains the engine underneath it.

SAO should not try to replace:

- SAP Cloud ALM as central monitoring;
- SAP Integration Suite monitoring or its AI-assisted error resolution;
- SAP Data Transition Validation or Migration Cockpit;
- SAP AI Agent Hub as an enterprise agent inventory/governance product;
- Joule Studio or other agent-development runtimes;
- generic SAP MCP servers.

Those products already cover monitoring, migration, governance, or agent construction.

SAO's practical niche is the layer **between observation and a safe operational decision**:

```text
monitor / export / event / snapshot
             |
             v
       SAO Evidence Pack
             |
      identity + authority
      causality + freshness
      deterministic checks
      cross-system state
             |
             v
    diagnosis / reconciliation
             |
      missing evidence
      safe recovery choices
      blocked unsafe choices
             |
             v
 business postcondition + report
             |
             v
      optional agent assurance
```

The core promise should be:

> **Turn fragmented SAP operational evidence into an inspectable diagnosis, a safe next action, and a verifiable business outcome.**

---

# Primary users

## 1. SAP AMS / support consultant

Typical task:

> "A customer, order, IDoc, replication, or integration is wrong. I have several logs and screenshots. What actually failed, what evidence is missing, and what can safely be retried or corrected?"

The product must help with:

- incident triage;
- evidence collection;
- cross-system causality;
- retry/replay safety;
- recovery choice;
- verification that the business problem is actually resolved.

## 2. SAP integration / solution architect

Typical task:

> "Does this interface design define identity, authority, ordering, duplicate semantics, recovery, and business acknowledgement well enough to operate safely?"

The product must help with:

- integration-contract validation;
- architecture fitness checks;
- failure campaigns;
- architecture change/diff review;
- recovery ownership.

## 3. SAP MDG / master-data / migration consultant

Typical task:

> "Source and target differ. Which difference is actually wrong, which system is authoritative, which identity/mapping was used, and what should be repaired?"

The product must help with:

- authority-aware reconciliation;
- identity resolution;
- mapping-version drift;
- stale snapshots;
- pending-vs-active governance state;
- post-migration / post-replication validation.

## 4. Enterprise-agent / AI governance engineer

Typical task:

> "Can this agent configuration safely reason or act around a system of record?"

This remains the existing SAO-Bench / SAO-Trace / simulator use case.

It is important, but it should no longer be the only obvious reason to use the repository.

---

# Product surface

SAO should converge on six user-facing surfaces.

## A. SAO CLI

One install, one entry point:

```bash
sao demo
sao incident analyze ./incident
sao reconcile ./reconciliation
sao context-check architecture.json
sao cutover verify ./cutover
sao agent-eval ./runtime-result
```

The user should not need to know which internal Python script implements a feature.

## B. Evidence Packs

A portable folder format representing one operational problem.

Example:

```text
incident-2026-001/
  manifest.yaml
  source-change.csv
  messages.csv
  target-state.csv
  identity-map.csv
  mapping-version.json
  runbook.md
```

The pack is local, inspectable, shareable, redactable, and reproducible.

## C. Domain Packs

A domain pack defines useful checks and reports for a real SAP problem.

Initial packs:

1. Integration / replication incident
2. Master-data reconciliation
3. Cutover delta integrity
4. Agent assurance
5. Architecture review

Do **not** build a generic plugin framework before the first two practical packs have external users.

## D. Read-only connectors

Connectors should bring evidence into SAO without turning SAO into another SAP integration platform.

Priority:

1. CSV / JSON / SAP GUI exports
2. OpenTelemetry logs
3. SAP Cloud ALM Generic Integration Monitoring Analytics API
4. SAP Cloud ALM Raw Data Outbound Logs
5. other supported read-only APIs only when demanded by users

Direct production mutation is not a roadmap priority.

## E. Local Workbench

A lightweight local UI for consultants who do not want to operate through Python commands.

Functions:

- drag/drop evidence;
- map columns;
- view timeline and identity chain;
- see missing evidence;
- inspect diagnosis and recovery options;
- export Markdown / JSON evidence packet.

No cloud account should be required for the core workflow.

## F. Reports / evidence artifacts

Every useful command should produce both:

- human-readable Markdown/HTML;
- machine-readable JSON.

A report should clearly separate:

- observed facts;
- deterministic checks;
- hypotheses;
- missing evidence;
- permitted recovery;
- blocked unsafe actions;
- verification/postcondition;
- limitations.

---

# Phase 0 — freeze the research foundation

**Target: late August–early September 2026**

Goal: stop changing benchmark truth while the user-facing product is built.

Complete:

- semantic review of the 51 SAO-Bench cases;
- benchmark versioning and release manifest;
- first tagged research release;
- explicit distinction between benchmark release and product release;
- keep SAO-Bench stable enough that practical packs can reuse its invariants.

Existing issues: #7, #17.

Exit criterion:

- `SAO-Bench v0.3.0` can be cited and reproduced;
- no new benchmark case is added merely because an idea is interesting.

---

# Phase 1 — SAO Evidence Pack + Incident Analyzer

**Target: September 2026**

This is the highest-priority product milestone.

Build a useful workflow that requires **no SAP tenant and no AI API**.

## User story

A support consultant exports several pieces of evidence, places them into an incident folder, and runs:

```bash
sao incident analyze ./incident
```

SAO produces:

```text
incident-report.md
incident-report.json
```

## Minimum evidence model

- business object / canonical identity;
- system-specific identities;
- relevant time window;
- observed source state/change;
- integration/message evidence;
- target state;
- mapping / configuration evidence when supplied;
- operational memory/runbook provenance.

## Minimum analysis

- identity resolved / ambiguous / unresolved;
- source of truth known / unknown;
- causal chain complete / broken;
- technical success vs business success;
- duplicate/replay risk;
- stale evidence risk;
- missing evidence;
- recovery class;
- verification/postcondition.

## Recovery classes

SAO should distinguish at least:

- retry;
- replay;
- regenerate from current authoritative state;
- resolve identity/mapping first;
- correct configuration;
- business/master-data correction;
- reconcile only;
- compensate;
- escalate / insufficient evidence.

Exit criterion:

> A new user can clone/install SAO, run one bundled SAP-shaped incident, and understand the result in under five minutes.

---

# Phase 2 — Integration Operations Pack

**Target: September–October 2026**

This is the first domain pack and the best adoption wedge.

## Why first

Integration operations generate exactly the fragmented evidence SAO is designed to correlate:

- IDoc/AIF status;
- middleware processing;
- change/event timestamps;
- identity/value mapping;
- source state;
- target processing;
- target business state.

Monitoring tools tell users that something failed. SAO should help answer:

> **What failed, which business change is affected, what is safe to do next, and what will prove recovery?**

## Input adapters

Start with files:

- generic CSV;
- generic JSON/JSONL;
- configurable SAP GUI-export column maps;
- OpenTelemetry log JSON.

Then add a read-only SAP Cloud ALM connector:

```bash
sao calm pull integration \
  --message-type IDOC \
  --from ... \
  --to ... \
  --output ./incident
```

The connector should use supported Cloud ALM read APIs and never require broad SAP backend write access.

## First useful incident templates

1. successful old message does not explain current missing change;
2. duplicate business event / replay risk;
3. out-of-order message;
4. message transport success but target business rejection;
5. mapping changed between event and recovery;
6. missing causal correlation;
7. unknown commit after timeout;
8. source change exists but no outbound event was created.

Exit criteria:

- at least 8 bundled incidents;
- one real supported external evidence source (Cloud ALM or OTel);
- reports produce concrete next checks rather than generic root-cause lists.

---

# Phase 3 — Local SAO Workbench

**Target: October 2026**

CLI proves the model; the Workbench makes it usable by SAP practitioners.

## v0.1 screens

### Incident

- upload/import evidence;
- timeline;
- source → message → target causal chain;
- missing evidence;
- diagnosis;
- safe recovery choices;
- postcondition.

### Reconciliation

- source/target mapping;
- authority rules;
- discrepancy categories;
- drill-down to records/attributes.

### Architecture

- upload/edit Enterprise Context;
- render Mermaid diagram;
- authority matrix;
- integration catalog;
- fitness warnings.

Everything should run locally by default.

Exit criterion:

> A functional SAP consultant can use the main incident workflow without reading Python code or JSON schemas.

---

# Phase 4 — Master Data Reconciliation Pack

**Target: October–November 2026**

Do not build another generic CSV comparison tool.

The value is **semantic reconciliation**.

## Inputs

```text
source.csv
target.csv
identity-map.csv
authority.yaml
value-mapping.yaml
manifest.yaml
```

## Discrepancy classes

SAO should distinguish:

- identity unresolved;
- identity ambiguous;
- authoritative source differs from target;
- target newer than source snapshot;
- attribute authority differs by field;
- event-time mapping differs from current mapping;
- value-mapping drift;
- pending governance change mistaken for active state;
- duplicate candidates;
- scoped business exception;
- technically equal but semantically out-of-scope data.

## Output

For each discrepancy:

- what is observed;
- which authority applies;
- whether correction is justified;
- which evidence is missing;
- safe remediation class;
- whether execution must remain blocked.

Exit criterion:

> SAO can explain why two SAP master-data exports differ, not merely highlight that they differ.

---

# Phase 5 — Cutover Integrity Pack

**Target: November 2026**

This is the most differentiated SAP architecture use case.

SAO should not compete with cutover scheduling tools.

It should answer a different question:

> **Did the authority transition preserve the correct business state and event causality?**

Reuse issue #19 and the Synthetic Enterprise Lab.

## Inputs

- pre-cutover snapshot;
- migration snapshot/load result;
- delta watermark;
- event/message ledger;
- before/during/after identity and mapping versions;
- post-cutover target state;
- cutover authority phases.

## Detect

- snapshot + queued-event double apply;
- missing delta;
- stale legacy message after target activation;
- mapping drift between extract and replay;
- target newer than migration snapshot;
- reconciliation gap;
- invalid rollback assumption after business activity began;
- stale runbook using retired recovery path.

Exit criterion:

> A migration/cutover lead can use SAO to validate state continuity, not to manage the schedule.

---

# Phase 6 — Architecture outputs, not only architecture lint

**Target: November–December 2026**

The Enterprise Context Graph becomes useful only when it saves documentation effort.

Add:

```bash
sao context render context.json --format markdown
sao context render context.json --format mermaid
sao context matrix context.json --authority
sao context matrix context.json --integrations
sao context matrix context.json --controls
```

Generate:

- system/context diagram;
- business/data authority matrix;
- integration catalog;
- recovery ownership matrix;
- control/evidence traceability;
- cutover readiness view.

Then implement issue #18: business invariant → control → requirement → benchmark/test → evidence → owner.

Exit criterion:

> Maintaining one machine-readable architecture context produces several artifacts an architect or analyst would otherwise maintain manually.

---

# Phase 7 — Agent Assurance becomes a practical pack

**Target: after practical packs have users**

Continue #3 only after the core SAP operations workflows are useful.

Use the same operational packs to test agent runtimes.

A useful loop is:

```text
operational failure pattern
        -> synthetic evidence pack
        -> deterministic safe decision
        -> agent runtime evaluation
        -> SAO-Trace
        -> regression result
```

This is more valuable than a disconnected AI benchmark because the cases come from real enterprise-operating semantics.

Priority runtime evidence:

1. one generic HTTPS runtime;
2. one orchestration runtime;
3. Joule Studio when accessible through a supported interface.

Do not build another MCP server merely for distribution.

---

# Packaging and distribution — must happen early

Before asking anyone to use SAO, reduce setup friction.

Target commands:

```bash
pipx install sap-agentic-operations
sao demo
```

or an equivalent zero-friction Python installer.

Required:

- package metadata;
- semantic product version;
- tagged GitHub release;
- release notes;
- supported Python versions;
- reproducible demo data;
- `sao doctor`;
- clear privacy/local-processing statement.

The first public product release should be small and useful rather than feature-complete.

---

# Community strategy

The easiest useful contribution should not be "modify the framework".

It should be:

> **Contribute a failure pattern or an anonymized/synthetic Evidence Pack.**

Good contribution types:

- integration failure fixture;
- master-data discrepancy fixture;
- cutover failure invariant;
- column mapping for a common export;
- deterministic recovery rule;
- missing-evidence rule;
- external runtime result.

Only after two or more domain packs have real external usage should SAO formalize a general pack/plugin SDK.

---

# What not to build

Avoid these unless real users demand them:

- another generic SAP MCP server;
- a full SAP monitoring platform;
- another generic RAG/chatbot UI;
- automatic write access to production SAP;
- generic AI root-cause summaries without deterministic evidence;
- a generic CSV validator competing on field rules alone;
- a cutover scheduling/project-management product;
- a large plugin architecture before useful packs exist;
- dozens of architecture documents without executable/user-facing output.

---

# 90-day execution sequence

## 25 Aug – 7 Sep 2026

**Stabilize and package**

- finish #17 semantic benchmark review;
- finish #7 and tag the benchmark foundation;
- add installable package metadata;
- build `sao demo`;
- define Evidence Pack v0.1.

## 8 Sep – 30 Sep 2026

**Ship the first useful product**

- Incident Analyzer;
- Integration Operations Pack;
- 8+ bundled incidents;
- Markdown + JSON report;
- CSV/JSON/OTel imports.

## 1 Oct – 20 Oct 2026

**Connect to real operational evidence**

- SAP Cloud ALM read-only connector;
- Generic Integration Monitoring support;
- local Workbench incident view;
- first external user walkthroughs.

## 21 Oct – 10 Nov 2026

**Expand to data governance**

- Master Data Reconciliation Pack;
- authority-aware discrepancy classes;
- local Workbench reconciliation view.

## 11 Nov – 30 Nov 2026

**Differentiate around cutover and architecture**

- Cutover Integrity Pack / issue #19;
- context rendering and generated matrices;
- control traceability / issue #18;
- complete vertical SAP reference case / issue #20.

## December 2026

**External evidence and adoption**

- first independent runtime results;
- first community-contributed failure packs;
- first stable product release candidate;
- publish reproducible examples and short technical walkthroughs.

---

# Adoption metrics

Do not optimize for stars alone.

Track:

## Time-to-first-value

A new user should reach a useful report from the bundled demo in **under 5 minutes**.

## External completion

Before building another major framework layer, get at least:

- 3 external practitioners who successfully run a practical pack;
- 1 external issue describing a real missing workflow;
- 1 external fixture/PR/review;
- 1 real supported data-source integration used outside the maintainer environment.

## Utility

A practical report should answer at least one question the source monitoring tool did not answer directly:

- Which business change is affected?
- Is identity resolved?
- Is the observed message causally related to that change?
- Is retry/replay safe?
- Is the target state actually correct?
- What evidence is missing?
- Which recovery class is justified?
- What proves the incident is resolved?

## Trust

- no client data in repository examples;
- deterministic checks visible;
- hypotheses separated from facts;
- no production write required for core workflows;
- source/runtime/version provenance preserved.

---

# Product 1.0 criterion

SAO 1.0 should not mean "the framework is large."

It should mean:

- installation is straightforward;
- at least three practical SAP domain workflows exist;
- at least one supported external evidence connector exists;
- local Workbench handles the main workflows;
- reports are useful without an LLM;
- AI/runtime adapters are optional and measurable;
- architecture/evidence contracts are stable;
- real external users have completed tasks with it;
- external practitioners have contributed or reviewed failure semantics;
- a practitioner can explain in one sentence why SAO is useful.

That sentence should be close to:

> **SAO helps SAP teams turn fragmented operational evidence into a reproducible diagnosis, a safe recovery decision, and a verified business outcome.**
