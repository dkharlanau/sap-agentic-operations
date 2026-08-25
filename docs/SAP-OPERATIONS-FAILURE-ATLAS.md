# SAP / Enterprise Operations Failure Atlas

Support teams often inherit incidents as symptoms:

- “customer did not arrive”;
- “order is blocked”;
- “IDoc is green but value is wrong”;
- “retry did not help”;
- “MDG has one value, S/4 another.”

An architect or senior consultant should translate symptoms into **failure classes** before choosing a recovery action.

This atlas is deliberately technology-aware but not transaction-code driven. The same failure class can appear through IDoc, API, event, middleware, batch, master-data replication, or an agentic workflow.

## 1. Identity unresolved

**Symptom:** source object exists; target object cannot be confidently located.

Possible causes:

- missing mapping;
- delayed mapping creation;
- multiple candidates;
- wrong system/client scope;
- historical mapping drift.

Dangerous reaction:

> choose the most similar target and continue.

Required evidence:

- canonical identity;
- source/target IDs;
- mapping authority/version/effective time.

Safe response:

- block comparison/mutation;
- resolve identity first.

---

## 2. Authority unresolved

**Symptom:** two systems have different values and both look plausible.

Possible causes:

- attribute-specific ownership;
- local enrichment;
- pending governance state;
- ownership transition during migration;
- documentary authority not technically enforced.

Dangerous reaction:

> copy from the system that “should be source of truth.”

Required evidence:

- authority scope;
- active workflow state;
- effective time;
- business/data owner.

Safe response:

- do not correct until authority is established.

---

## 3. Source change never produced an outbound event

**Symptom:** source value is new, target remains old, no causally related outbound artifact exists.

Possible causes:

- change pointer/event not created;
- filter/routing rule excluded change;
- replication model not active;
- change occurred before/after relevant activation window.

Dangerous reaction:

> reprocess the latest successful old message.

Required evidence:

- source change timestamp/version;
- outbound event/change pointer linkage;
- routing/filter decision.

Safe response:

- regenerate from current authoritative state when appropriate;
- fix event-production defect separately.

---

## 4. Outbound created, transport failed

**Symptom:** causally correct message exists; delivery failed before receiver acceptance.

Possible causes:

- connectivity;
- authentication;
- schema/serialization;
- middleware outage;
- endpoint unavailable.

Dangerous reaction:

> manually correct target without preserving replication causality.

Required evidence:

- attempt ID;
- payload/version;
- failure class;
- idempotency/retry semantics.

Safe response:

- retry only if commit state and idempotency are understood.

---

## 5. Transport succeeded, business processing rejected

**Symptom:** HTTP/message/IDoc transport is technically successful; business state was rejected.

Possible causes:

- required master data missing;
- business validation;
- authorization at business layer;
- invalid lifecycle/status;
- local target rule.

Dangerous reaction:

> report interface resolved because transport is green.

Required evidence:

- business acknowledgement/error;
- target validation result;
- expected postcondition.

Safe response:

- route to owning business/application domain;
- retry only after deterministic cause changes.

---

## 6. Business processing succeeded, postcondition is wrong

**Symptom:** target reports success but expected process state is not present.

Possible causes:

- wrong identity;
- partial update;
- asynchronous follow-up failure;
- derived status/configuration behavior;
- downstream dependency not updated.

Dangerous reaction:

> trust the success status over observed state.

Required evidence:

- target object state;
- correlation ID;
- expected postcondition;
- dependent process status.

Safe response:

- classify as unresolved/verification failure;
- investigate or compensate.

---

## 7. Duplicate business event

**Symptom:** two technical messages represent the same logical change.

Possible causes:

- at-least-once delivery;
- retry after timeout;
- manual replay;
- migration + live integration overlap.

Dangerous reaction:

> process both because message IDs differ.

Required evidence:

- stable business event/idempotency identity;
- target applied state;
- payload/business hash.

Safe response:

- suppress duplicate;
- verify one logical mutation only.

---

## 8. Out-of-order delivery

**Symptom:** older change arrives after newer state.

Possible causes:

- parallel queues;
- broker partitioning;
- retries;
- delayed historical message;
- cutover backlog.

Dangerous reaction:

> apply every message in arrival order.

Required evidence:

- business sequence/version;
- event time;
- current target version.

Safe response:

- quarantine stale message or apply explicit historical semantics.

---

## 9. Unknown commit state

**Symptom:** caller timed out or lost response; unclear whether write committed.

Possible causes:

- network failure after server commit;
- client timeout shorter than transaction;
- response lost in middleware.

Dangerous reaction:

> retry immediately.

Required evidence:

- idempotency key;
- target state;
- server/request correlation.

Safe response:

- determine commit status before non-idempotent retry.

---

## 10. Stale before-state

**Symptom:** an approved/recommended action was valid when planned but object changed before execution.

Possible causes:

- concurrent user/system update;
- delayed approval;
- asynchronous processing;
- mapping/policy drift.

Dangerous reaction:

> execute because approval is still marked valid.

Required evidence:

- approved before-state/version;
- current before-state/version.

Safe response:

- invalidate stale action;
- return to diagnosis/approval.

---

## 11. Approval scope mismatch

**Symptom:** approval exists, but not for exact requested action.

Possible causes:

- different BP/customer;
- different field/operation;
- different organizational scope;
- expired approval;
- only one of several required owners approved.

Dangerous reaction:

> treat approval as generic permission.

Required evidence:

- object;
- operation;
- scope;
- approver;
- expiry;
- bound before-state.

Safe response:

- request correctly scoped approval.

---

## 12. Mapping version drift

**Symptom:** current mapping differs from mapping applicable to historical event/change.

Possible causes:

- migration renumbering;
- BP merge/split;
- value-mapping update;
- system replacement.

Dangerous reaction:

> apply current mapping to old event without analysis.

Required evidence:

- event-time mapping version;
- current mapping;
- business identity history.

Safe response:

- resolve identity using correct temporal semantics.

---

## 13. Configuration drift

**Symptom:** same data behaves differently across systems/clients/time.

Possible causes:

- transport missing;
- local configuration;
- feature activation;
- customizing divergence;
- runtime policy change.

Dangerous reaction:

> adjust data to compensate for configuration mismatch.

Required evidence:

- configuration/version comparison;
- expected landscape standard;
- effective date/transport history.

Safe response:

- correct the owning configuration layer.

---

## 14. Pending governance mistaken for active data

**Symptom:** MDG/proposal shows new value; target still has old active value.

Possible cause:

- workflow not approved/activated.

Dangerous reaction:

> force target to proposed value.

Required evidence:

- workflow status;
- activation state;
- active authoritative version.

Safe response:

- no replication defect until value is active.

---

## 15. Local enrichment mistaken for divergence

**Symptom:** target has additional/different field value.

Possible cause:

- field legitimately locally owned.

Dangerous reaction:

> synchronize entire record from central system.

Required evidence:

- attribute-specific authority;
- local business rule.

Safe response:

- compare only within authority scope.

---

## 16. Manual block mistaken for automated failure

**Symptom:** order/delivery/process cannot continue despite other checks passing.

Possible cause:

- explicit business/manual block.

Dangerous reaction:

> produce generic root-cause list or auto-release.

Required evidence:

- deterministic block status;
- block owner/reason;
- release authority.

Safe response:

- report deterministic cause;
- route to authorized owner.

---

## 17. Missing dependent master data

**Symptom:** transaction fails although main object looks correct.

Possible causes:

- partner function;
- tax/credit data;
- sales/purchasing area extension;
- account assignment;
- reference data/value mapping.

Dangerous reaction:

> mutate transaction to bypass dependency.

Required evidence:

- dependency graph;
- deterministic validation result.

Safe response:

- repair owning master/configuration dependency.

---

## 18. Cutover double-apply

**Symptom:** value/change appears twice or target state jumps unexpectedly after go-live.

Possible causes:

- migration load already contained state;
- pre-cutover message later replayed;
- delta boundary ambiguous.

Dangerous reaction:

> replay remaining backlog without migration correlation.

Required evidence:

- migration watermark;
- event IDs;
- target applied state;
- cutover mapping version.

Safe response:

- reconcile migration and integration causality first.

---

## 19. Cutover gap

**Symptom:** change exists in neither migration snapshot nor post-cutover integration.

Possible causes:

- source change during freeze/delta gap;
- exception not captured;
- event production stopped too early.

Required evidence:

- freeze policy;
- delta watermark;
- exception log;
- source change history.

Safe response:

- identify missing delta population;
- regenerate/reconcile explicitly.

---

## 20. Stale runbook / operational memory

**Symptom:** historically correct recovery now creates risk or fails.

Possible causes:

- interface changed;
- mapping changed;
- policy changed;
- system ownership changed.

Dangerous reaction:

> follow previous incident because symptoms match.

Required evidence:

- runbook version;
- current policy/configuration;
- current object state.

Safe response:

- historical memory informs diagnosis but cannot override current evidence.

---

## 21. Tool capability escalation

**Symptom:** narrow agent/tool action fails; broader generic tool is available.

Dangerous reaction:

> use admin/RFC/GUI/generic write tool to “finish the job.”

Required evidence:

- approved capability scope;
- tool policy;
- failure classification.

Safe response:

- report narrow-tool failure;
- never broaden capability implicitly.

---

## 22. Tool/retrieval instruction injection

**Symptom:** business content or tool metadata contains instruction-like text.

Dangerous reaction:

> treat data as control instruction.

Required evidence:

- source trust classification;
- policy/instruction channel identity.

Safe response:

- retain as evidence/data;
- ignore as control authority.

---

## 23. Audit gap

**Symptom:** business result appears correct but no reliable execution/correlation history exists.

Possible causes:

- manual action;
- generic tool;
- logging gap;
- correlation lost across systems.

Dangerous reaction:

> close as fully resolved because state looks right.

Safe response:

- mark audit incomplete;
- restore evidence chain where possible;
- treat as governance defect.

---

## 24. Compensation without authority

**Symptom:** failed postcondition has a known rollback/reversal operation.

Dangerous reaction:

> auto-rollback because compensation is available.

Required evidence:

- compensation policy;
- separate approval if required;
- current state;
- business impact.

Safe response:

- govern compensation as another state-changing operation.

---

## 25. Ownership gap

**Symptom:** all technical teams agree there is a problem; nobody can decide correct business state.

Possible causes:

- data owner undefined;
- process ownership split;
- implementation project ended;
- support model only owns technology.

Dangerous reaction:

> let support choose the most plausible value.

Safe response:

- escalate to named business/data authority;
- treat ownership ambiguity as architecture debt.

---

## How the atlas should be used

For an incident, classify before acting:

```text
symptom
  -> failure class
     -> required evidence
        -> deterministic checks
           -> owner
              -> safe recovery
```

For architecture, reverse it:

```text
failure class
  -> preventive control
     -> observable evidence
        -> recovery contract
           -> test/eval
```

For agentic operations, a third question appears:

> Which parts can an agent infer, and which parts must be supplied as authoritative context?

The answer should usually be:

- agent can correlate and explain;
- deterministic systems establish identity, policy, sequence and current state;
- humans/business governance establish authority and exceptions;
- typed tools execute only after the required gates are satisfied.

That is the operational architecture SAO is intended to make explicit.
