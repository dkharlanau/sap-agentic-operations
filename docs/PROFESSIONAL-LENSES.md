# Professional Lenses

SAP Agentic Operations can be read as an AI-agent project. That is only one layer.

The more useful way to read it is through three professional lenses: **SAP / Enterprise Architect**, **SAP Consultant / Operations Lead**, and **System Analyst**.

The same problem looks different from each role. A strong solution survives all three views.

## Lens 1 — SAP / Enterprise Architect

The architect asks:

> Where does business truth live, which boundary protects it, how does state move, and what happens when the design fails?

Start here:

1. [`ARCHITECT-DECISION-SPINE.md`](ARCHITECT-DECISION-SPINE.md) — the main decision chain: business invariant → authority → placement → integration → failure → evidence → cutover → agent capability.
2. [`INTEGRATION-CONTRACT.md`](INTEGRATION-CONTRACT.md) — identity, causality, ordering, idempotency, acknowledgement, recovery and ownership for enterprise integrations.
3. [`CUTOVER-RECOVERY.md`](CUTOVER-RECOVERY.md) — authority transitions, delta watermarks, in-flight messages, reconciliation, rollback and hypercare.
4. [`CONTROL-PLANE.md`](CONTROL-PLANE.md) — deterministic enterprise control plane around probabilistic reasoning.
5. [`RISK-MODEL.md`](RISK-MODEL.md) — business impact R0–R4 separated from agent failure class T1–T10.
6. [`../schemas/enterprise-context.schema.json`](../schemas/enterprise-context.schema.json) — machine-readable architecture context linking process, authority, systems, integrations, controls and evidence.

Architectural signal to look for:

- decisions are expressed as trade-offs;
- `source of truth` has scope and effective time;
- integration is modeled by failure semantics, not only transport;
- clean-core placement is a decision, not dogma;
- observability proves business state, not only technical health;
- cutover is treated as a temporary architecture;
- agents never become invisible authority over enterprise state.

## Lens 2 — SAP Consultant / Operations Lead

The consultant asks:

> Can this architecture actually be discovered, explained, operated, recovered and handed over to a team?

Start here:

1. [`CONSULTING-REVIEW-CARDS.md`](CONSULTING-REVIEW-CARDS.md) — compact workshop questions for business truth, clean core, MDG, integration, AMS, cutover and agent readiness.
2. [`INTEGRATION-CONTRACT.md`](INTEGRATION-CONTRACT.md) — use it as an interface design/review template.
3. [`CUTOVER-RECOVERY.md`](CUTOVER-RECOVERY.md) — use it for migration/cutover/hypercare preparation.
4. [`../scenarios/`](../scenarios/) — synthetic operational scenarios built around failure and recovery, not demo happy paths.
5. [`../simulator/`](../simulator/) — stateful experiments for stale approvals, duplicates, policy drift, mapping drift and compensation.
6. [`../results/`](../results/) — evidence/results model rather than presentation-only claims.

Consulting signal to look for:

- every workshop question leads to a decision or unresolved risk;
- error ownership follows failure type;
- recovery is designed before go-live;
- recurring support problems are converted into contracts/checks;
- `green interface` is never confused with correct business outcome;
- hypercare ends with an operating model, not a defect spreadsheet.

## Lens 3 — System Analyst

The analyst asks:

> What exactly must be true, in which scope, how will systems preserve it, and what evidence proves that they did?

Start here:

1. [`BUSINESS-TRACEABILITY.md`](BUSINESS-TRACEABILITY.md) — requirement → invariant → contract → control → evidence → test → owner.
2. [`INTEGRATION-CONTRACT.md`](INTEGRATION-CONTRACT.md) — turns interface requirements into explicit semantic contracts.
3. [`../evals/`](../evals/) — executable acceptance/negative-acceptance criteria.
4. [`../schemas/decision.schema.json`](../schemas/decision.schema.json) — structured decision output.
5. [`../schemas/evidence.schema.json`](../schemas/evidence.schema.json) — evidence/provenance contract.
6. [`../examples/enterprise-context/customer-replication.json`](../examples/enterprise-context/customer-replication.json) — example of requirements/authority/integration/evidence represented as context rather than prose alone.

Analysis signal to look for:

- requirements describe business outcomes, not transaction codes;
- invariants can be violated/tested;
- organizational scope is explicit;
- authority is not inferred from data location;
- negative acceptance criteria are first-class;
- evidence is defined before testing;
- agentic reasoning is separated from deterministic business rules.

## One problem, three views

Take a simple statement:

> Customer master replication failed.

An analyst asks:

- Which governed change is missing?
- Which customer identity and business scope?
- What expected state is violated?

A consultant asks:

- Who owns recovery?
- Can it be retried, regenerated, or manually corrected?
- Which evidence will support need?

An architect asks:

- Is the failure transport, identity, authority, sequencing, or business-state verification?
- What prevents the wrong customer/state from being changed?
- Why did the architecture allow this failure to become operationally ambiguous?

SAO's purpose is to make these views converge on one inspectable model.

## The professional thesis

The interesting skill in enterprise AI is not knowing how to attach an LLM to SAP.

It is being able to move fluently between:

```text
business intent
    -> requirement
        -> architecture boundary
            -> data/process authority
                -> integration semantics
                    -> operational failure
                        -> evidence
                            -> recovery
                                -> controlled automation
```

Agents are one participant in that chain.

The architecture remains accountable for the whole chain.
