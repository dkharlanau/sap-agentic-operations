# SAP Consulting Review Cards

Good consulting questions are compact, uncomfortable, and expensive to answer incorrectly.

These cards are designed for architecture reviews, discovery workshops, solution assessments, cutover preparation, AMS stabilization, and agent-readiness discussions. They are not checklists to complete mechanically. Each card is meant to expose an assumption before that assumption becomes an incident.

## Card 1 — Business Truth

Ask:

- What must remain true for the business even if the technology changes?
- What is the cost of this invariant being wrong for one hour, one day, one month?
- Is failure visible immediately, or can incorrect state accumulate silently?
- Which process can legally continue with stale data, and which cannot?

Red flag:

> “The interface is green, so the process is fine.”

## Card 2 — System of Record vs Authority

Ask:

- Where is the value stored?
- Who is allowed to decide the value?
- Who is allowed to distribute it?
- Is ownership object-wide, attribute-specific, or scope-specific?
- Can another system enrich the value without becoming authoritative?
- What happens when two authoritative-looking systems disagree?

Red flag:

> “S/4 is the source of truth for everything.”

That sentence is often too broad to operate safely.

## Card 3 — Clean Core Boundary

Ask:

- Is this logic transactional core integrity or cross-system orchestration?
- Does it need to run atomically inside ERP?
- Can it live side-by-side without weakening the business invariant?
- What is the upgrade burden of keeping it in core?
- What is the latency/availability burden of moving it out?
- Is the extension using a supported contract or reaching into internals?

Red flag:

> A side-by-side design chosen only because “BTP is strategic,” or an in-core design chosen only because “ABAP is easier.”

## Card 4 — Integration Semantics

Ask:

- Is this a command, request, notification, or business fact?
- Does the producer need a response now?
- What is the business event identity?
- Can messages arrive twice or out of order?
- How is retry made safe?
- How do we distinguish technical acceptance from business acceptance?
- What is the postcondition?

Red flag:

> “We can always resend the message.”

## Card 5 — Identity

Ask:

- What is the canonical business identity?
- Which IDs exist in each system?
- Who owns the mapping?
- Can mappings change over time?
- What identity version applied when the event was created?
- What happens when there are two plausible matches?

Red flag:

> “Just take the closest BP/customer match.”

## Card 6 — Master Data Governance

Ask:

- Which fields are governed centrally?
- Which are locally owned?
- Is the proposed value active or still pending approval?
- What is the activation event?
- Who may override a default rule?
- How is a valid exception scoped and expired?
- How is target drift detected?

Red flag:

> A comparison of whole records when authority is actually field-specific.

## Card 7 — Error and Recovery

Ask:

- Which failures are transient?
- Which failures are deterministic business errors?
- Which failures require regeneration from current source state?
- When is historical replay safe?
- What proves the first attempt did or did not commit?
- Who owns manual recovery?
- Can recovery create a second business error?

Red flag:

> One generic “Retry” button for every failure type.

## Card 8 — Observability

Ask:

- Can we trace source change → event/message → middleware → target processing → business postcondition?
- Is correlation preserved across systems?
- Can support see the mapping version used?
- Can we distinguish not-sent, not-delivered, rejected, stale, duplicate, and unverified?
- Is the final business state observable?

Red flag:

> Monitoring only the middleware layer.

## Card 9 — Requirement Quality

Ask:

- What business invariant does this requirement protect?
- What is the exact organizational/process scope?
- What are the negative acceptance criteria?
- What evidence proves success?
- What evidence proves failure?
- Which rule is deterministic and which requires judgment?
- Who owns the requirement after go-live?

Red flag:

> A requirement written as a transaction code, table, field, or screen behavior with no business invariant.

## Card 10 — Cutover

Ask:

- When exactly does authority move?
- What is the freeze boundary?
- What delta is inside the load vs normal integration?
- What happens to in-flight messages?
- Which mapping version applies?
- How do we prevent migration + integration double-apply?
- What are the go/no-go business postconditions?
- What does rollback mean after new transactions exist?

Red flag:

> “We will reconcile counts after migration.”

Counts are necessary. They are not process readiness.

## Card 11 — Agent Readiness

Ask:

- What evidence may the agent read?
- Which facts must come from deterministic tools?
- What capability does the agent actually need: read, recommend, approve, execute?
- Which business decisions must never be inferred?
- What happens when evidence conflicts?
- What happens when tool/retrieval content contains instructions?
- What exact gate allows capability escalation?

Red flag:

> “The agent has SAP access.”

Access is not a capability model.

## Card 12 — State Change

Ask:

- What exact object and operation are authorized?
- Is approval bound to the current before-state?
- Can the state change between approval and execution?
- Is the operation idempotent?
- What business postcondition defines success?
- Is compensation separately governed?
- What audit evidence survives the action?

Red flag:

> Treating successful API execution as resolved business outcome.

## Card 13 — AMS / Operations

Ask:

- What does operations monitor proactively?
- Which failure classes have automated recovery?
- Which require business decision?
- Which evidence can support access without developer help?
- Are recurring incidents converted into deterministic checks/runbooks?
- Is operational memory versioned against current policy and configuration?

Red flag:

> A support model where the user is still the monitoring system.

## Card 14 — Architecture Debt

Ask:

- Which integrations depend on undocumented behavior?
- Which mappings exist only in people's memory?
- Which manual recovery procedures are not tested?
- Which customizations block upgrades?
- Which systems appear authoritative only because nobody has challenged them?
- Which exceptions have no expiry?

Red flag:

> “It has worked for years.”

Long-lived behavior can be long-lived debt.

## Card 15 — Decision Reversal

Ask:

- What evidence would make us change this architecture decision?
- At what volume does sync become event-driven?
- At what complexity does on-stack become side-by-side?
- At what failure rate does manual recovery become automation?
- At what business impact does recommend-only become mandatory?
- Which assumption has an expiry date?

Red flag:

> An architecture decision with no reversal trigger.

## 30-minute review format

A compact workshop can use five passes:

1. **Truth** — business invariant, authority, scope.
2. **Flow** — identity, integration, causality, state transitions.
3. **Failure** — retry, replay, recovery, compensation.
4. **Evidence** — observability, acceptance criteria, audit.
5. **Change** — cutover, future scale, reversal trigger, agent capability.

The deliverable should be a short list of explicit architecture decisions and unresolved risks — not another meeting summary.
