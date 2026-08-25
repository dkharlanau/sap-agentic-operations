# SAP Agentic Operations (SAO)

[![SAO practical toolkit](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/product.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/product.yml)
[![SAO full suite](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml)
[![Dynamic variants](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/dynamic-variants.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/dynamic-variants.yml)

**A local-first, evidence-first toolkit for diagnosing, reconciling, validating, and safely recovering SAP-heavy enterprise operations.**

Maintained by **Dzmitryi Kharlanau** — SAP Transformation · Enterprise Operations · Agentic AI.

Status: **experimental practical toolkit v0.4-dev / SAO-Bench v0.3-dev**.

---

## Start with a real operational question

A customer is wrong in S/4. An IDoc is green. A mapping changed. A target value is stale. Somebody proposes: “just reprocess it.”

The difficult question is not whether one technical message succeeded.

It is:

> **What business change are we trying to explain, which evidence is actually related to that change, and what recovery action is justified without making the state worse?**

SAO turns fragmented operational evidence into:

- a bounded diagnosis;
- missing evidence;
- safe next actions;
- actions that are explicitly **not** justified;
- a business-level resolution condition;
- traceable evidence references.

The first practical workflow does this without SAP credentials, a database, or an LLM.

```text
SAP / MDG / IDoc / AIF / CPI / exports
                 |
                 v
           Evidence Pack
                 |
      identity + authority
      causality + freshness
      mapping + message state
      target business state
                 |
                 v
          Incident Analyzer
                 |
      diagnosis / evidence gap
      safe recovery choices
      blocked unsafe shortcuts
                 |
                 v
       business postcondition
```

---

## Try it in about a minute

Requirements: Python 3.11+.

```bash
git clone https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations
python -m pip install .

sao demo
```

The default demo models a common support trap:

- an older customer change has a successful message;
- a newer authoritative MDG change exists;
- the target still contains the old value;
- no message is causally linked to the current change.

SAO should classify it as:

```text
current_outbound_event_not_proven
```

and explicitly reject:

```text
reprocess_old_successful_message
manual_target_overwrite
```

The generated report is written to:

```text
sao-demo/sao-output/incident-report.md
sao-demo/sao-output/incident-report.json
```

### Explore different failure modes

```bash
sao demo --list

sao demo --scenario business-rejection --output /tmp/sao-business
sao demo --scenario mapping-drift --output /tmp/sao-mapping
sao demo --scenario target-mismatch --output /tmp/sao-target
sao demo --scenario resolved --output /tmp/sao-resolved
```

Bundled scenarios currently cover:

| Scenario | What it demonstrates |
|---|---|
| `missing-current-event` | old technical success does not explain a newer business change |
| `business-rejection` | transport success is not business acceptance |
| `mapping-drift` | historical replay cannot silently use a newer identity mapping |
| `target-mismatch` | accepted message but wrong business postcondition |
| `technical-failure` | retry is unsafe before commit/idempotency state is understood |
| `resolved` | complete evidence chain to verified target state |
| `identity-unresolved` | cross-system comparison is blocked without canonical identity |
| `stale-target-observation` | an old target snapshot cannot prove a new message succeeded |
| `target-identity-mismatch` | the event targets a different identity than current mapping |

---

## Analyze your own exports

An SAO **Evidence Pack** is intentionally a small folder of JSON/CSV files:

```text
incident/
  incident.json
  source_changes.csv
  messages.csv
  target_state.csv
  identity_map.csv
```

Validate:

```bash
sao incident validate ./incident
```

Analyze:

```bash
sao incident analyze ./incident
```

Read the full input contract in [`docs/EVIDENCE-PACK.md`](docs/EVIDENCE-PACK.md).

### Why this is connector-neutral

The product is built around evidence semantics, not around one SAP API.

Future collectors can all produce the same Evidence Pack:

```text
Cloud ALM       ─┐
AIF export       │
CPI export       ├──> Evidence Pack ──> same diagnostic engine
IDoc CSV         │
custom API/SQL   │
manual Excel    ─┘
```

Connectors can change. The meaning of identity, authority, causality, mapping version, acknowledgement and business postcondition should not.

---

## Example of the output model

A diagnosis is not a free-form paragraph. It is a structured operational decision:

```json
{
  "status": "insufficient_evidence",
  "classification": "current_outbound_event_not_proven",
  "execution_allowed": false,
  "findings": [
    "A successful technical message exists, but it predates the current authoritative change.",
    "Old technical success is not evidence that the current business change replicated."
  ],
  "missing_evidence": [
    "outbound event causally linked to the current source change"
  ],
  "safe_next_actions": [
    "determine_whether_current_outbound_event_was_created"
  ],
  "unsafe_actions": [
    "reprocess_old_successful_message",
    "manual_target_overwrite"
  ]
}
```

The goal is not to make the tool sound intelligent. The goal is to make the operational conclusion inspectable.

---

# What SAO is becoming

The practical toolkit is the front door. Underneath it is a larger architecture and assurance lab.

The project is designed around four connected surfaces.

## 1. SAP Operations Toolkit

Current:

- Evidence Pack v0.1;
- deterministic Incident Analyzer;
- installable zero-dependency CLI;
- nine reproducible failure scenarios;
- Markdown + JSON reports.

Next:

- Integration Operations Pack;
- Cloud ALM read-only collector;
- local Workbench;
- semantic master-data reconciliation;
- cutover integrity campaigns.

See [`ROADMAP.md`](ROADMAP.md).

## 2. Enterprise Architecture as Code

SAO can model:

```text
process
  -> business invariant
  -> business object / authority
  -> systems
  -> integrations
  -> controls
  -> evidence
  -> agent capability
  -> cutover state
```

Validate an example:

```bash
python sao.py context-check \
  examples/enterprise-context/customer-replication.json \
  --strict
```

Compare architecture snapshots:

```bash
python sao.py context-diff before.json after.json
```

The diff highlights changes such as authority drift, integration semantics, idempotency, business postconditions, removed controls and agent-capability changes.

Start with [`ARCHITECTURE.md`](ARCHITECTURE.md).

## 3. Synthetic Enterprise Lab

The stateful simulator models control failures without pretending to emulate S/4HANA.

It includes:

- canonical identity and mapping versions;
- policy drift;
- delayed/dropped/duplicate messages;
- approval expiry;
- before-state/precondition binding;
- idempotency collisions;
- business postcondition failures;
- audit evidence;
- governed compensation;
- trust-aware memory and evidence.

Run:

```bash
python sao.py tests
```

## 4. SAO-Bench and Agent Assurance

SAO-Bench contains 51 synthetic enterprise-control cases across integration operations, master data, business process, agent security and state change.

It exists to test whether an agent/runtime respects enterprise control boundaries — not to measure writing quality.

Examples include:

- unresolved identity;
- old successful message vs newer source change;
- ambiguous master-data authority;
- duplicate/replay risk;
- stale approval;
- tool-output instruction injection;
- memory poisoning;
- capability escalation;
- technical success with failed business postcondition;
- missing provenance.

The reference self-test is a harness check, not an AI score.

```bash
python sao.py audit
python sao.py self-test
```

---

# Professional views

SAO is intentionally useful from three different roles.

### SAP / Enterprise Architect

Focus on business truth, authority, integration semantics, failure/recovery, clean-core placement, observability and bounded agent capability.

Start with [`ARCHITECTURE.md`](ARCHITECTURE.md).

### SAP Consultant / AMS Lead

Focus on evidence collection, repeatable diagnostics, incident ownership, safe recovery, runbook quality and business-level resolution.

Start with [`docs/AGENTIC-AMS-OPERATING-MODEL.md`](docs/AGENTIC-AMS-OPERATING-MODEL.md) and [`docs/SAP-OPERATIONS-FAILURE-ATLAS.md`](docs/SAP-OPERATIONS-FAILURE-ATLAS.md).

### System Analyst

Focus on requirement → invariant → identity → contract → control → evidence → test → owner.

Start with [`docs/BUSINESS-TRACEABILITY.md`](docs/BUSINESS-TRACEABILITY.md).

---

# Design principles

1. **Identity before comparison.**
2. **Authority before correction.**
3. **Change causality before replay.**
4. **Deterministic rules before probabilistic reasoning.**
5. **Recommendation is not authorization.**
6. **Authorization is not execution.**
7. **A green interface is not a verified business outcome.**
8. **A tool failure never authorizes a broader tool.**
9. **Current evidence outranks stale operational memory.**
10. **Compensation is a governed state change, not an escape hatch.**
11. **A score without provenance is not a benchmark result.**
12. **The practical tool should be useful without an AI model.**

---

# What SAO deliberately does not replace

SAO is not intended to become:

- another SAP monitoring dashboard;
- another SAP MCP server;
- an S/4HANA emulator;
- a generic CSV diff tool;
- an unrestricted SAP write agent;
- a replacement for SAP Cloud ALM, Integration Suite monitoring, Migration Cockpit/DTV, Joule Studio or AI Agent Hub.

Its niche is the layer between **observation and a safe operational decision**.

---

# Current product roadmap

The roadmap is now measured by time-to-first-value and external use rather than framework size.

Priority order:

1. Evidence Pack + Incident Analyzer — **in progress / first implementation available**;
2. Integration Operations Pack;
3. simple installation and demo quality;
4. local Workbench;
5. Cloud ALM read-only connector;
6. semantic Master Data Reconciliation;
7. Cutover Integrity Pack;
8. architecture rendering/traceability;
9. cross-runtime agent assurance.

See [`ROADMAP.md`](ROADMAP.md).

---

# Safety, privacy and SAP scope

SAO examples are synthetic.

Do not publish:

- customer/client names;
- production IDs that reveal private context;
- ticket contents;
- internal URLs;
- credentials/tokens;
- proprietary payloads;
- copied SAP product code.

Local Evidence Packs stay local; the practical toolkit does not upload them.

SAO is independent work. It is not an official SAP project, SAP certification, production-safety certification, or substitute for landscape-specific authorization, security, compliance or business ownership.

---

# Repository map

- [`sao_toolkit/`](sao_toolkit/) — practical Evidence Pack / incident-analysis product code
- [`examples/evidence-packs/`](examples/evidence-packs/) — ready-to-run operational evidence examples
- [`docs/EVIDENCE-PACK.md`](docs/EVIDENCE-PACK.md) — practical input contract
- [`docs/`](docs/) — architecture, operations, benchmark and governance
- [`schemas/`](schemas/) — machine-readable contracts
- [`simulator/`](simulator/) — Synthetic Enterprise Lab
- [`evals/`](evals/) — SAO-Bench corpus
- [`adapters/`](adapters/) — runtime-neutral agent adapter protocol
- [`traces/`](traces/) — SAO-Trace examples and invariants
- [`results/`](results/) — public reproducible result ledger
- [`research/`](research/) — source-backed architecture research
- [`ROADMAP.md`](ROADMAP.md) — product roadmap

---

# Author

**Dzmitryi Kharlanau**  
SAP Transformation · Enterprise Operations · Agentic AI

- Professional site: https://dkharlanau.github.io/
- LinkedIn: https://www.linkedin.com/in/dkharlanau/
- Agent-Ready Web Profile: https://github.com/dkharlanau/agent-ready-web-profile
- Public datasets: https://github.com/dkharlanau/dkharlanau-datasets

## License

Apache License 2.0. See [`LICENSE`](LICENSE).
