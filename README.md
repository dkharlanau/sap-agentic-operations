# SAP Agentic Operations (SAO)

[![SAO practical toolkit](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/product.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/product.yml)
[![SAO full suite](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml/badge.svg)](https://github.com/dkharlanau/sap-agentic-operations/actions/workflows/suite.yml)

[Documentation](https://dkharlanau.github.io/sap-agentic-operations/docs/) · [Product page](https://dkharlanau.github.io/sap-agentic-operations/)

**A local-first, evidence-first toolkit for diagnosing, reconciling, validating, and safely recovering SAP-heavy enterprise operations.**

Maintained by **Dzmitryi Kharlanau** — SAP Transformation · Enterprise Operations · Agentic AI.

Status: **Practical Toolkit `0.4.0-alpha.2` · SAO-Bench `0.3-dev`**.

---

## The problem SAO is trying to solve

A customer is wrong in S/4. An IDoc is green. A mapping changed. A target value is stale. A ticket says that last time somebody reprocessed the message and it worked.

The difficult question is not:

> Did one technical step return success?

It is:

> **Which business change are we trying to explain, which evidence is actually related to that change, and what recovery action is justified without making the state worse?**

SAO turns fragmented evidence into:

- a bounded diagnosis;
- missing evidence;
- safe next actions;
- actions explicitly **not** justified by current evidence;
- a business-level resolution condition;
- traceable evidence references.

The practical alpha does this **without SAP credentials, a database, or an LLM**.

```text
SAP / MDG / IDoc / AIF / CPI / Excel / exports
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

# Try it in a minute

Requirements: Python 3.11+.

```bash
git clone https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations
python -m pip install .

sao demo
```

The default demo models a common support trap:

- an older source change has a successful message;
- a newer authoritative change exists;
- the target still contains the old value;
- no message is causally linked to the current change.

SAO classifies this as:

```text
current_outbound_event_not_proven
```

and explicitly blocks shortcuts such as:

```text
reprocess_old_successful_message
manual_target_overwrite
```

The report is generated locally:

```text
sao-demo/sao-output/incident-report.md
sao-demo/sao-output/incident-report.json
```

---

# Practical workflows available in Alpha 2

## 1. Incident Analyzer — full Evidence Pack

Create a blank pack:

```bash
sao incident init ./incident \
  --incident-id INC-001 \
  --object-type customer \
  --source-id C-100 \
  --target-id BP-501 \
  --authority-system MDG \
  --attribute delivery_control
```

Fill the exported evidence and run:

```bash
sao incident validate ./incident
sao incident analyze ./incident
```

Minimal pack:

```text
incident/
  incident.json
  source_changes.csv
  messages.csv
  target_state.csv
  identity_map.csv
```

Read [`docs/EVIDENCE-PACK.md`](docs/EVIDENCE-PACK.md).

### What the analyzer checks

- canonical identity resolved / ambiguous / unresolved;
- current authoritative change;
- explicit change-to-message causality;
- mapping version drift;
- technical message failure;
- transport success vs business rejection;
- target observation freshness;
- target business-state postcondition;
- safe and unsafe recovery choices.

It does not silently infer that the latest message belongs to the latest change.

---

## 2. Quick Check — one CSV for Excel-style triage

If you already maintain one row per customer/order/incident in Excel, use the shorter path:

```bash
sao quickcheck demo
sao quickcheck analyze my-incidents.csv
```

Quick Check is not a weaker second engine. Every row is converted into an in-memory Evidence Pack and evaluated by the same incident semantics.

Useful for:

- AMS incident lists;
- customer replication backlogs;
- cutover validation spreadsheets;
- IDoc triage lists;
- deciding which cases deserve a richer Evidence Pack.

Read [`docs/QUICKCHECK.md`](docs/QUICKCHECK.md).

---

## 3. Batch triage — many Evidence Packs

```bash
sao batch ./incident-packs --output ./triage
```

Outputs:

```text
triage/
  batch-report.csv
  batch-report.json
  batch-report.md
```

The report aggregates incidents by failure class and gives the first evidence-backed next action for each case.

---

## 4. Local Workbench

View an incident without reading JSON:

```bash
sao workbench ./incident
```

or export a static local HTML report:

```bash
sao workbench ./incident --output incident.html
```

The Workbench shows:

- evidence chain;
- current classification;
- findings;
- missing evidence;
- safe actions;
- actions not justified by current evidence;
- resolution condition.

It is read-only and local. The alpha does not upload the Evidence Pack.

---

## 5. Semantic Master-Data Reconciliation

A normal CSV diff answers:

> Which cells differ?

SAO asks:

> **Which identity is this, who owns this attribute, which snapshot is newer, and is a correction actually justified?**

Try it:

```bash
sao reconcile demo
sao reconcile analyze ./reconciliation
```

Current discrepancy classes include:

- unresolved / ambiguous identity;
- target record missing;
- attribute authority unresolved;
- aligned;
- mismatch with unknown freshness;
- authoritative mismatch;
- non-authoritative snapshot newer than the authoritative export.

That last case is deliberately important: SAO refuses to overwrite a newer target from a stale source snapshot just because the source is usually authoritative.

Read [`docs/RECONCILIATION.md`](docs/RECONCILIATION.md).

---

## 6. Normalize SAP / Excel exports

Real exports rarely use SAO's canonical column names.

Use an explicit mapping rather than manually renaming every file:

```bash
sao normalize demo

sao normalize csv \
  --table messages \
  --input we02-export.csv \
  --mapping messages.mapping.json \
  --output incident/messages.csv
```

Mappings can define:

- source-column names;
- constants;
- value maps such as `53 -> success`, `51 -> failed`.

SAO deliberately does not auto-guess that an arbitrary field is a canonical identity or business status.

Read [`docs/NORMALIZING-EXPORTS.md`](docs/NORMALIZING-EXPORTS.md).

---

# Nine reproducible incident scenarios

```bash
sao demo --list
```

| Scenario | What it demonstrates |
|---|---|
| `missing-current-event` | old success does not explain a newer change |
| `business-rejection` | transport success is not business acceptance |
| `mapping-drift` | historical replay cannot silently use a newer mapping |
| `target-mismatch` | accepted message but wrong target business state |
| `technical-failure` | retry is unsafe until commit/idempotency state is understood |
| `resolved` | complete causal chain to verified target state |
| `identity-unresolved` | cross-system comparison blocked without canonical identity |
| `stale-target-observation` | an old target snapshot cannot prove a new message succeeded |
| `target-identity-mismatch` | event target conflicts with resolved business identity |

These are synthetic operating scenarios, not copied client incidents.

---

# Why SAO is connector-neutral

SAO is built around **evidence semantics**, not around one SAP API.

```text
manual Excel    ─┐
WE02 / AIF CSV   │
CPI export       │
OpenTelemetry    ├──> canonical evidence ──> same diagnostic engine
Cloud ALM        │
custom API/SQL  ─┘
```

This is intentional.

A connector may change. The meaning of identity, authority, causality, mapping version, acknowledgement and business postcondition should not.

Cloud ALM / AIF / CPI collectors are roadmap items; Alpha 2 does **not** claim a live SAP connector yet.

---

# Bring research into control design without treating it as operational truth

Signal to Insight can export a published insight as a digest-protected research-evidence packet. SAO validates the packet locally and renders a bounded human review card:

```bash
sao research validate \
  examples/research-evidence/sti-enterprise-agents.json

sao research review \
  examples/research-evidence/sti-enterprise-agents.json \
  --output /tmp/enterprise-agent-review.md
```

The packet remains `external_research_context`. It requires human review, cannot authorize execution and cannot represent observations from a production incident.

See [External research evidence handoff](docs/RESEARCH-EVIDENCE-HANDOFF.md) for the contract, threat boundary and Signal to Insight exporter.

---

# Example output

A diagnosis is structured, not free-form AI prose:

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

# Under the practical toolkit: the assurance lab

The user-facing toolkit is now the front door. The repository also contains the deeper architecture and agent-assurance machinery that protects its semantics.

## Enterprise Architecture as Code

SAO models:

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

Validate a context:

```bash
python sao.py context-check \
  examples/enterprise-context/customer-replication.json \
  --strict
```

Compare architectural drift:

```bash
python sao.py context-diff before.json after.json
```

Start with [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Synthetic Enterprise Lab

The simulator exercises:

- identity and mapping drift;
- policy drift;
- delayed / duplicated messages;
- approval expiry;
- before-state binding;
- idempotency collisions;
- failed business postconditions;
- audit gaps;
- governed compensation;
- untrusted operational memory.

```bash
python sao.py tests
```

## SAO-Bench / SAO-Trace

SAO-Bench currently contains 51 synthetic enterprise-control cases across integration operations, master data, business process, agent security and state change.

The benchmark evaluates control decisions, not writing style.

```bash
python sao.py audit
python sao.py self-test
```

The reference self-test checks the harness. It is not a model score.

---

# Professional views

### SAP / Enterprise Architect

Use SAO for business authority, integration semantics, recovery boundaries, architecture drift and bounded agent capability.

Start with [`ARCHITECTURE.md`](ARCHITECTURE.md).

### SAP Consultant / AMS Lead

Use SAO for evidence collection, repeatable diagnostics, recovery decisions and business-level resolution.

Start with [`docs/EVIDENCE-PACK.md`](docs/EVIDENCE-PACK.md) and [`docs/AGENTIC-AMS-OPERATING-MODEL.md`](docs/AGENTIC-AMS-OPERATING-MODEL.md).

### System Analyst

Use SAO for requirement → invariant → identity → contract → control → evidence → test → owner.

Start with [`docs/BUSINESS-TRACEABILITY.md`](docs/BUSINESS-TRACEABILITY.md).

---

# Design principles

1. **Identity before comparison.**
2. **Authority before correction.**
3. **Change causality before replay.**
4. **Deterministic rules before probabilistic reasoning.**
5. **Recommendation is not authorization.**
6. **A green interface is not a verified business outcome.**
7. **A tool failure never authorizes a broader tool.**
8. **Current evidence outranks stale operational memory.**
9. **Compensation is a governed state change, not an escape hatch.**
10. **A score without provenance is not a benchmark result.**
11. **The practical tool should be useful without an AI model.**
12. **Connectors may change; evidence semantics should remain stable.**

---

# What SAO does not try to replace

SAO is not:

- another SAP monitoring dashboard;
- another SAP MCP server;
- an S/4HANA emulator;
- a generic CSV diff tool;
- an unrestricted SAP write agent;
- a replacement for SAP Cloud ALM, Integration Suite monitoring, Migration Cockpit/DTV, Joule Studio or AI Agent Hub.

Its intended niche is the layer between **observation and a safe operational decision**.

---

# Alpha 2 stopping rule

The practical alpha is now broad enough to test with people.

The next major feature should not be added merely because it is interesting.

Before another large framework layer, SAO should collect field evidence from SAP practitioners:

- Did the classification help?
- What evidence was hard to prepare?
- Which recovery class was missing?
- Which conclusion was wrong?
- Which export format should be normalized next?

Use the **SAO practical field report** issue template and keep client data out of public issues.

See [`ROADMAP.md`](ROADMAP.md).

---

# Safety and privacy

Local Evidence Packs stay local; the practical toolkit does not upload them.

Do not publish:

- customer/client names;
- production identifiers that reveal private context;
- ticket contents;
- internal URLs;
- credentials/tokens;
- proprietary payloads;
- copied SAP product code.

SAO is independent work. It is not an official SAP project, SAP certification, production-safety certification, or substitute for landscape-specific authorization, security, compliance or business ownership.

---

# Repository map

- [`sao_toolkit/`](sao_toolkit/) — practical toolkit code
- [`examples/evidence-packs/`](examples/evidence-packs/) — ready-to-run operational examples
- [`docs/EVIDENCE-PACK.md`](docs/EVIDENCE-PACK.md) — full incident input contract
- [`docs/QUICKCHECK.md`](docs/QUICKCHECK.md) — one-CSV path
- [`docs/RECONCILIATION.md`](docs/RECONCILIATION.md) — semantic master-data reconciliation
- [`docs/NORMALIZING-EXPORTS.md`](docs/NORMALIZING-EXPORTS.md) — explicit export mappings
- [`ARCHITECTURE.md`](ARCHITECTURE.md) — architecture entry point
- [`simulator/`](simulator/) — Synthetic Enterprise Lab
- [`evals/`](evals/) — SAO-Bench corpus
- [`adapters/`](adapters/) — runtime-neutral agent adapter protocol
- [`traces/`](traces/) — SAO-Trace
- [`ROADMAP.md`](ROADMAP.md) — product roadmap
- [`CHANGELOG.md`](CHANGELOG.md) — product + benchmark changes
- [`release/GOLDEN-QUICKSTART-0.4.0-alpha.2.md`](release/GOLDEN-QUICKSTART-0.4.0-alpha.2.md) — pinned release verification
- [`release/USABILITY-TEST-15-MIN.md`](release/USABILITY-TEST-15-MIN.md) — blank external first-use protocol
- [`CONTRIBUTING.md`](CONTRIBUTING.md) — contribution and privacy-safe feedback paths

---

## Related projects

- [Signal to Insight](https://github.com/dkharlanau/signal-to-insight) produces the v1 public research-evidence packet supported by `sao research`; the handoff is intentionally non-operational.
- [Reconciliation as Code](https://github.com/dkharlanau/reconciliation-as-code) is the broader declarative reconciliation engine; SAO keeps a smaller SAP-operations-oriented reconciliation path for local evidence packs.
- [Interface as Code](https://github.com/dkharlanau/interface-as-code) defines versionable interface contracts; SAO focuses on runtime observations, diagnosis and verified business outcomes.
- [dkharlanau-datasets](https://github.com/dkharlanau/dkharlanau-datasets) publishes citable public learning records, not client data or production incident evidence.

## License

Apache License 2.0. See [`LICENSE`](LICENSE).

## About the author

Created and maintained by **Dzmitryi Kharlanau**, an SAP consultant and system analyst working across enterprise architecture, data, integration, operations, and practical AI.

- [Website and knowledge base](https://dkharlanau.github.io/)
- [LinkedIn](https://www.linkedin.com/in/dkharlanau/)
