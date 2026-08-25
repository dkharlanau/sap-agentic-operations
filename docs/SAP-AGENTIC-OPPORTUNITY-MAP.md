# SAP Agentic Opportunity Map

The easiest way to waste money on enterprise AI is to start with the question:

> Where can we put an agent?

A better question is:

> Where does the enterprise have **expensive uncertainty** that cannot be solved by one deterministic rule, and where can reasoning help without becoming hidden business authority?

This map separates high-value agentic work from attractive but structurally weak use cases.

## The opportunity test

A SAP/enterprise task is a good agent candidate when several of these are true:

- evidence is spread across systems;
- the operator must correlate rather than merely validate;
- multiple hypotheses are plausible;
- the next diagnostic step depends on context;
- humans spend time collecting/structuring evidence before making a decision;
- a recommendation can be verified before action;
- the task benefits from explanation and handover;
- failure can safely result in `insufficient_evidence`.

It is a poor agent candidate when:

- an exact rule already exists;
- correctness requires atomic transaction semantics;
- identity is unresolved;
- business authority is undefined;
- the agent would need broad generic write access;
- success cannot be verified;
- the only benefit is replacing three deterministic API calls with natural language.

## 1. SAP AMS / Production Support

### Strong opportunities

**Incident evidence assembler**

Collect object state, change history, interface status, relevant config/check results, prior incidents and current runbook version into one evidence bundle.

Value:

- reduces first-hour investigation work;
- makes handover better;
- creates reusable structured evidence.

Recommended capability: **Read**.

---

**Root-cause hypothesis ranking**

Given deterministic checks and evidence, rank plausible failure classes and propose the next diagnostic step.

Value:

- this is exactly where ambiguity exists;
- agent can explain contradictions rather than hide them.

Recommended capability: **Recommend**.

---

**Recovery option analysis**

Explain whether retry, regenerate, reconcile, manual correction, compensation or escalation is appropriate for the observed failure class.

Value:

- converts tribal operational knowledge into reviewable reasoning.

Recommended capability: **Recommend**. Execution stays separate.

### Weak opportunity

**Generic SAP fixer** with GUI/RFC/admin access.

Why weak:

- broad capability;
- poor auditability;
- hidden authority decisions;
- tool failure encourages scope escalation.

## 2. Integration Operations

### Strong opportunities

**Causality reconstruction**

Trace:

```text
source change -> event/message -> middleware -> target processing -> business state
```

Recommended capability: **Read / Recommend**.

---

**Retry/replay safety advisor**

Determine whether a failure is safe to retry based on commit state, idempotency, event identity, ordering and current target state.

Recommended capability: **Recommend**.

A typed replay tool can become **Execute** only after deterministic gates establish safety.

---

**Duplicate/out-of-order detection**

Much of this should be deterministic. Agentic reasoning is useful for explaining impact and choosing the next investigation path when business sequence is incomplete.

Recommended capability: **Read / Recommend**.

### Weak opportunity

**“Auto-retry every red interface.”**

This is automation without failure semantics.

## 3. Master Data / MDG

### Strong opportunities

**Cross-system discrepancy analysis**

Compare central governance state, operational target state, mapping version and attribute authority.

Recommended capability: **Recommend**.

---

**Duplicate candidate investigation**

Use the model to structure evidence and explain candidate similarity, while deterministic/business identity controls decide whether merge is allowed.

Recommended capability: **Recommend**.

---

**Governance workflow briefing**

Summarize what is pending, who owns the next decision, which downstream systems are affected and what will change after activation.

Recommended capability: **Read / Recommend**.

---

**Mass-change impact preview**

Before a mass change, explain impacted scopes, dependent processes/integrations and risky exception groups.

Recommended capability: **Recommend**.

### Weak opportunity

**Autonomous customer/vendor/BP merge based on semantic similarity.**

Similarity is useful evidence. It is not identity or business authority.

## 4. O2C / P2P Operations

### Strong opportunities

**Blocked-process investigator**

Run deterministic checks first, then explain unresolved dependencies and route to the correct owner.

Examples:

- delivery/order block;
- missing partner function;
- supplier block;
- incomplete master data;
- conflicting configuration/process evidence.

Recommended capability: **Recommend**.

---

**Exception packet builder**

Assemble evidence needed for a business owner to approve an exception: object, reason, scope, before-state, impact, expiry and proposed operation.

Recommended capability: **Recommend**.

### Weak opportunity

**“Urgent order? Let the agent release the block.”**

Business urgency is evidence of impact, not authorization.

## 5. Data Migration / Cutover

### Strong opportunities

**Reconciliation gap analyst**

Compare counts, identities, critical attributes, process readiness and post-cutover integration continuity.

Recommended capability: **Read / Recommend**.

---

**Delta-gap detector**

Identify source changes that fall between migration snapshot/freeze/delta boundaries.

Recommended capability: **Read / Recommend**.

---

**In-flight message classifier**

Classify pending/failed/obsolete/replay-risk messages against cutover watermarks and target state.

Recommended capability: **Recommend**.

---

**Go/no-go evidence summarizer**

Summarize objective readiness evidence and open risks for decision makers.

Recommended capability: **Recommend**.

The human governance body still owns go/no-go.

### Weak opportunity

**Autonomous mass correction during cutover.**

The architecture itself is changing. This is precisely when state-changing autonomy should become narrower, not broader.

## 6. Testing and Quality

### Strong opportunities

**Requirement-to-negative-test generation**

From a business invariant, generate candidate failure/negative cases:

- stale state;
- missing identity;
- duplicate event;
- missing approval;
- business rejection after technical success.

Recommended capability: **Recommend**.

---

**Cross-version regression explanation**

Compare test/eval results and explain which control classes regressed, not only which scripts failed.

Recommended capability: **Read / Recommend**.

---

**Evidence completeness check**

Detect requirements/tests that have no observable evidence or no negative criteria.

Much of this can be deterministic; agent can explain gaps.

## 7. Enterprise Architecture

### Strong opportunities

**Architecture context assembler**

Build a draft relationship map from existing repositories/documents:

```text
process -> invariant -> object -> authority -> system -> integration -> control -> evidence -> owner
```

Recommended capability: **Recommend**; architect confirms.

---

**ADR research assistant**

Collect current platform guidance and compare architecture alternatives against declared constraints.

Recommended capability: **Recommend**.

---

**Architecture drift detector**

Compare current machine-readable context with declared architecture policy and flag changes:

- new integration without recovery owner;
- authority moved;
- new generic tool scope;
- exception without expiry;
- cutover phase mismatch.

Deterministic fitness functions should do the detection; agent explains impact.

## 8. Documentation and Knowledge

### Strong opportunities

**Operational memory with expiry/provenance**

Convert resolved incidents into reusable patterns while preserving:

- environment;
- config/policy version;
- evidence;
- applicability conditions;
- expiry/review trigger.

Recommended capability: **Recommend**.

---

**Runbook gap detection**

Compare real incident evidence to runbook assumptions and flag stale procedures.

Recommended capability: **Recommend**.

### Weak opportunity

**Store every agent conclusion as durable memory.**

A conclusion without provenance and freshness becomes future misinformation.

## 9. Governed Execution: where it can make sense

Agentic execution is not always wrong.

It becomes plausible when the operation is:

- narrow and typed;
- reversible or low-impact;
- object/operation scope is exact;
- current before-state is verified;
- policy result is deterministic;
- required approval is present;
- idempotency exists;
- business postcondition is observable;
- audit correlation is preserved;
- compensation is defined and separately governed when necessary.

Examples worth exploring:

- replay a confirmed-not-applied idempotent business event;
- execute a pre-approved low-risk correction through a typed tool;
- close a diagnostic task after deterministic postconditions are met;
- trigger a bounded reconciliation job.

The key is that the agent is not receiving generic ERP mutation authority. It is invoking a **small business operation inside a stronger deterministic envelope**.

## Portfolio view

A mature enterprise agent portfolio should contain more **diagnostic and evidence agents** than autonomous mutation agents.

A healthy distribution might look conceptually like:

```text
Knowledge / discovery       ██████████
Evidence assembly           ██████████
Diagnosis / recommendation  ████████
Decision support            ██████
Approval preparation        ████
Governed execution          ██
Broad autonomy              ▏
```

The exact ratio is not the point.

The principle is:

> Put intelligence where uncertainty is expensive. Put deterministic control where incorrect state is expensive.
