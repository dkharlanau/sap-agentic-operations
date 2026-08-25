# Enterprise Architecture Anti-Patterns

Some architecture failures are difficult to see because every individual component appears reasonable.

A middleware flow is green. The SAP document exists. The agent answered confidently. The migration count matches. The approval field says `valid=true`.

And the business state is still wrong.

This catalog gives those recurring failures names.

## 1. Green Interface Fallacy

**Belief:** If the interface is technically successful, the business change succeeded.

Typical evidence:

- HTTP 200;
- IDoc success status;
- message consumed;
- middleware flow green.

What is missing:

- target business acceptance;
- correct target identity;
- expected business postcondition.

Better rule:

> Transport success is evidence of transport success. Nothing more.

---

## 2. Source of Truth by Habit

**Belief:** The system that has historically contained the field is authoritative.

Failure:

- governance moved elsewhere;
- authority is attribute-specific;
- local enrichment is mistaken for ownership;
- pending proposed state is mistaken for active state.

Better rule:

> Authority needs scope, owner, effective time, and enforcement semantics.

---

## 3. Retry Button Architecture

**Belief:** Recovery means sending the message again.

Failure:

- first write may already have committed;
- business event may be duplicated;
- mapping may have changed;
- historical payload may no longer represent current source state;
- deterministic business validation will fail again.

Better rule:

> Retry is one recovery strategy for one class of failure. It is not an operating model.

---

## 4. Latest Message Wins

**Belief:** The newest technical message must represent the business change we are investigating.

Failure:

- correlation is missing;
- several changes were made;
- message sequence differs from business causality;
- latest success predates the reported change.

Better rule:

> Recover causality before selecting a technical artifact.

---

## 5. Similarity Is Identity

**Belief:** The closest-looking customer/BP/vendor is probably the right one.

Failure:

- same legal name across company contexts;
- duplicate candidates;
- historical mappings;
- reused external identifiers.

Better rule:

> Similarity can propose candidates. It does not grant business identity.

---

## 6. Clean Core Cargo Cult

**Belief:** Side-by-side is automatically cleaner; in-core is automatically legacy.

Failure:

- transactional invariant moved outside atomic boundary;
- unnecessary network/availability dependency;
- duplicated business rules;
- external extension becomes harder to operate than a supported on-stack option.

The opposite cargo cult also exists: keeping orchestration in core because ABAP is familiar.

Better rule:

> Choose placement from invariant, lifecycle, coupling, latency, upgrade and operational consequences.

---

## 7. Event-Driven Because Modern

**Belief:** An event is better than an API/message because it is more modern and decoupled.

Failure:

- consumer actually requires immediate business response;
- event ordering is undefined;
- duplicates are not handled;
- replay semantics are unknown;
- event identity is missing.

Better rule:

> Choose interaction semantics before technology style.

---

## 8. Prompt as Business Rule

**Belief:** If the prompt says “never release a blocked customer without approval,” the control exists.

Failure:

- prompt changes;
- retrieved text conflicts;
- tool metadata asks for broader scope;
- model interprets policy inconsistently.

Better rule:

> Deterministic policy belongs outside probabilistic reasoning.

---

## 9. Agent as Missing Integration Layer

**Belief:** An agent can compensate for undocumented mappings, weak APIs, inconsistent identity and manual operations.

Failure:

The agent becomes an intelligent wrapper around architectural debt and inherits all ambiguity underneath it.

Better rule:

> Agents should consume explicit enterprise contracts, not manufacture the contracts from symptoms.

---

## 10. Access Means Authority

**Belief:** If the agent/tool can technically call the API, the action is allowed.

Failure:

- technical credentials are broader than business authority;
- delegated user scope differs from tool scope;
- object-level authorization is lost;
- policy changed after planning.

Better rule:

> Capability is the intersection of identity, policy, object scope, operation scope, current state and approval.

---

## 11. Model Confidence as Control

**Belief:** High-confidence reasoning can justify action.

Failure:

The model may be confidently wrong about identity, current state, business authority or causal history.

Better rule:

> Confidence can rank hypotheses. It cannot create permission.

---

## 12. Memory as Policy

**Belief:** The last successful incident resolution is a safe shortcut for the next incident.

Failure:

- mapping changed;
- runbook changed;
- policy changed;
- the historical incident only looked similar.

Better rule:

> Operational memory is evidence with age and provenance, not durable control authority.

---

## 13. Observability Without Causality

**Belief:** More dashboards mean better supportability.

Failure:

There are many statuses but no chain linking:

```text
business change -> event -> message -> target processing -> business state
```

Better rule:

> Useful observability answers “what happened to this business change?” not “which systems are green?”

---

## 14. One Owner for the Interface

**Belief:** The integration team owns everything between systems.

Failure:

- business validation needs a business owner;
- master-data authority needs a data owner;
- transport needs integration ownership;
- recovery needs operations ownership.

Better rule:

> Ownership follows the failure class.

---

## 15. Counts Equal Migration Quality

**Belief:** Source count = target count means migration is correct.

Failure:

- wrong identities;
- wrong critical attributes;
- duplicates replace missing objects numerically;
- process dependencies are broken.

Better rule:

> Reconcile counts, keys, critical attributes, process readiness and post-cutover integration continuity.

---

## 16. Cutover as Project Plan

**Belief:** Cutover is mostly tasks, timestamps and owners.

Failure:

Authority moves, mappings freeze/change, messages remain in flight, and the recovery meaning of a historical payload changes.

Better rule:

> Cutover is a temporary architecture with its own authority and causality model.

---

## 17. Rollback by Hope

**Belief:** If go-live fails, restore the old system/database.

Failure:

- new business documents already exist;
- messages reached partners;
- numbers were allocated;
- state changed in external systems.

Better rule:

> After business activity begins, rollback often means governed compensation, not time travel.

---

## 18. Approval as Boolean

**Belief:** `approval_valid=true` is sufficient.

Failure:

Approval may be for:

- another object;
- another operation;
- an older before-state;
- an expired time window;
- one of several required business owners.

Better rule:

> Approval is a scoped, versioned business artifact.

---

## 19. API Success Ends the Story

**Belief:** Once the write call succeeds, the automation is complete.

Failure:

- business postcondition failed;
- audit correlation missing;
- asynchronous follow-up failed;
- compensation is required.

Better rule:

> Execution is an intermediate state. Verified business outcome is the end state.

---

## 20. The Invisible Manual Step

**Belief:** The process is automated.

Reality:

A specific person checks a spreadsheet, remembers a mapping, opens a transaction, interprets an error, and fixes the state manually.

Failure:

The real control exists in someone's head and disappears during absence, handover, or scale.

Better rule:

> Treat recurring manual judgment as architecture: document evidence, decision rule, owner, and safe automation boundary.

---

## 21. Exception Without Expiry

**Belief:** A one-time business exception can stay in configuration “until we clean it up.”

Failure:

Temporary authority becomes permanent architecture.

Better rule:

> Every exception should have scope, owner, rationale, effective period and removal/review trigger.

---

## 22. Architecture by Screenshot

**Belief:** A landscape diagram proves the design is documented.

Failure:

The diagram cannot answer:

- who owns the value;
- what happens on timeout;
- which mapping version applies;
- how replay works;
- what proves business success;
- which agent capability is allowed.

Better rule:

> A diagram is navigation. Contracts and decisions are architecture.

---

## How to use the catalog

During a design review, do not ask “is the architecture good?”

Ask:

> Which of these anti-patterns could this design accidentally become six months after go-live?

That question usually produces a more useful conversation.
