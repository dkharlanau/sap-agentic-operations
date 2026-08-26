# Enterprise as Code Ecosystem

This repository is the operational diagnosis and safe-recovery layer of a broader set of small, composable enterprise engineering tools maintained under the same GitHub profile.

The repositories are intentionally separated by problem boundary rather than by SAP module. Each one owns a compact machine-readable model and deterministic checks that can be used alone, in CI, or as context for an AI agent.

## The system at a glance

```text
business intent / requirement
          |
          v
   Process as Code ------ Decision Tables as Code
          |                         |
          v                         v
   Mapping as Code -------- Transformation Graph
          |                         |
          +----------+--------------+
                     |
                     v
              Interface as Code
                     |
          +----------+-----------+
          |                      |
          v                      v
Data Relationship Map    Reconciliation as Code
          |                      |
          +----------+-----------+
                     |
                     v
          SAP Agentic Operations
           diagnosis / recovery
                     |
          +----------+-----------+
          |                      |
          v                      v
       Cutover Graph      Enterprise Change Graph
          |                      |
          +----------+-----------+
                     |
                     v
            Project Evidence Graph
      requirement -> change -> test -> evidence
```

This is not intended to become one monolithic framework. The useful unit is the smallest model that can answer a real project question deterministically.

## Repository map

| Repository | Primary question | Current useful capability |
|---|---|---|
| [`process-as-code`](https://github.com/dkharlanau/process-as-code) | What business/process path should happen? | Versionable process/control model |
| [`decision-tables-as-code`](https://github.com/dkharlanau/decision-tables-as-code) | Which rule should apply for this case? | Executable decision-table semantics |
| [`mapping-as-code`](https://github.com/dkharlanau/mapping-as-code) | How should source values/structures map to target? | Versioned mappings, validation, testable examples |
| [`transformation-graph`](https://github.com/dkharlanau/transformation-graph) | Through which transformations did a value travel? | Transformation dependency/lineage model |
| [`interface-as-code`](https://github.com/dkharlanau/interface-as-code) | What contract should an integration satisfy? | Machine-readable interface contracts and checks |
| [`data-relationship-map`](https://github.com/dkharlanau/data-relationship-map) | How are business objects/IDs related across systems? | CSV/XLSX ingestion, composite IDs, provenance, 1:1 ambiguity policy, path and drift analysis |
| [`reconciliation-as-code`](https://github.com/dkharlanau/reconciliation-as-code) | Does observed state match expected state? | Versioned reconciliation definitions and deterministic checks |
| [`sap-agentic-operations`](https://github.com/dkharlanau/sap-agentic-operations) | What actually failed and what recovery is justified? | Evidence-first diagnosis, missing-evidence detection, safe/unsafe action boundaries |
| [`cutover-graph`](https://github.com/dkharlanau/cutover-graph) | What can run now and are we ready to continue? | Dependency planning, checkpoints, approvals/evidence gates, timing forecast, delay propagation, snapshot diff |
| [`enterprise-change-graph`](https://github.com/dkharlanau/enterprise-change-graph) | What can this change affect? | Enterprise change/impact graph |
| [`project-evidence-graph`](https://github.com/dkharlanau/project-evidence-graph) | Why does this exist and what proves it works now? | CSV/GitHub import, traceability, impact, coverage, freshness policy, reusable graph explorer |

## Three concrete end-to-end workflows

### 1. Cross-system master-data incident

Input:

- AFS/ERP customer extract
- MDG BP extract
- S/4 BP/customer extract
- message/AIF evidence

Flow:

1. `data-relationship-map` resolves and validates the AFS -> MDG -> S/4 identity chain.
2. `interface-as-code` describes the expected integration contract.
3. `reconciliation-as-code` compares expected vs observed target state.
4. `sap-agentic-operations` correlates authoritative change, messages, freshness, and target observation.
5. `project-evidence-graph` links the incident, fix, regression test, and final evidence.

Result: not just “IDoc failed/succeeded”, but a traceable explanation of the business state and justified recovery.

### 2. Migration/cutover control

Input:

- load tasks
- dependencies
- reconciliation output
- approvals
- evidence references
- live timestamps/statuses

Flow:

1. `cutover-graph` calculates executable work, blockers, checkpoint state, critical path, and forecast completion.
2. Reconciliation evidence becomes a checkpoint requirement before interfaces/business activity can open.
3. Missing business/data approval keeps the dependency closed even if the technical task is marked `done`.
4. Snapshot diff explains which delay or gate changed since the previous control-room state.
5. `project-evidence-graph` receives the final cutover evidence chain.

Result: a machine-readable go/no-go argument instead of a spreadsheet status color.

### 3. Controlled enterprise change

Input:

- requirement
- decision/rule
- mapping/interface change
- implementation/test evidence

Flow:

1. `process-as-code` and `decision-tables-as-code` capture intended behavior.
2. `mapping-as-code`, `transformation-graph`, and `interface-as-code` describe implementation boundaries.
3. `enterprise-change-graph` evaluates likely impact.
4. `project-evidence-graph` links requirement -> decision -> implementation -> test -> evidence.
5. Quality and freshness policies can fail CI when the evidence chain is incomplete or stale.

Result: a change can be reviewed as an evidence-backed system, not only as files and tickets.

## Shared design contract

Across the repository family, new capabilities should prefer:

- deterministic rules before probabilistic interpretation;
- machine-readable canonical models;
- source provenance rather than copied facts with no origin;
- explicit relationships rather than inferred links when correctness matters;
- small CLI tools that also work in CI;
- synthetic public examples instead of customer data;
- AI/agent use as a consumer of structured context, not as the only execution engine;
- separate read/diagnose/recommend layers from state-changing automation.

## What should *not* become another repository yet

Several ideas are currently better implemented as modules inside an existing product boundary:

- **Quality Gate as Code** -> policy gates in `project-evidence-graph`, `cutover-graph`, and other domain repos.
- **Traceability Matrix** -> generated view of `project-evidence-graph`.
- **GitHub Pages Explorer** -> reusable zero-build graph explorer in `project-evidence-graph/docs/index.html`.
- **Cutover Orchestrator** -> the executable core belongs in `cutover-graph` until state-changing orchestration becomes a separate security/operational boundary.
- **Adapter Conformance** -> already part of SAP Agentic Operations conformance tooling.
- **Enterprise Integration Failure Atlas** -> already part of SAP Agentic Operations documentation/research assets.
- **Synthetic Enterprise Data Lab** -> synthetic simulation belongs close to the products/benchmarks that consume it until a reusable data product emerges.

The criterion for a new repository should be a distinct user problem, canonical model, and lifecycle — not simply a new name.

## Next integration contract

The highest-leverage next step is stable cross-repository references. A future project pack should be able to refer to artifacts such as:

```text
process://order-to-cash/customer-create
mapping://customer/country/v3
interface://mdg-s4/customer/v2
relationship://AFS:4711->MDG:7200311
reconciliation://customer-country/post-load
cutover://wave-3/reconcile-customers
evidence://release-2026-08/regression-42
```

Those identifiers can become the common spine that allows tools and agents to traverse the ecosystem without merging all repositories into one framework.
