# Enterprise Integration Contract

An integration is not a line between two boxes. It is a promise about **identity, causality, ordering, authority, failure, and recovery**.

Most painful SAP incidents happen when teams document the payload but leave the promise implicit.

This playbook defines the questions that should exist before an interface is considered architecturally complete.

## 1. Business intent

State the business interaction in one sentence.

Good:

> When an approved customer master change becomes active, distribute the authoritative attributes to subscribed operational systems and prove which targets accepted the new business state.

Weak:

> Send DEBMAS from A to B.

The technical artifact can change. The business intent should survive the redesign.

## 2. Object identity

Define the identity model before the field mapping.

Capture:

- canonical business identity;
- sender-system identity;
- receiver-system identity;
- mapping authority;
- mapping version;
- effective time;
- ambiguity behavior.

A message is not safe to process simply because it contains a syntactically valid customer or BP number. The receiver must know **which business object that identifier meant for this event**.

## 3. Authority

For every distributed attribute or action, answer:

- Which system is authoritative?
- Is authority object-wide or attribute-specific?
- Is the proposed value already active or still pending governance?
- May the receiver reject the value for local business rules?
- Can the receiver enrich without becoming authoritative?

Authority should be explicit enough that a support analyst can explain whether a discrepancy is a replication defect, a legitimate local state, or an unresolved governance question.

## 4. Interaction pattern

### Synchronous request/response

Use when the caller genuinely needs a result before it can proceed.

Architectural questions:

- What is the business timeout, not only HTTP timeout?
- Is retry safe after an unknown commit state?
- Does technical success contain business-level rejection?
- Is the operation idempotent?
- What happens if the response is lost after the receiver committed?

### Asynchronous event/message

Use when a business fact should be distributed without coupling producer availability to consumers.

Architectural questions:

- Is the message an immutable fact or a command?
- What is the business event ID?
- Is ordering significant per object?
- Can duplicates occur?
- What is the replay policy?
- How are late consumers handled?
- Can a newer state arrive before an older message?

### Batch/file

Use deliberately, not apologetically. Batch can be correct where real-time coupling adds no business value.

Architectural questions:

- What is the extraction snapshot time?
- Full vs delta semantics?
- How are deletes represented?
- How is partial processing reconciled?
- What happens when the source changes during extraction?
- Is a rerun additive, replace-all, or idempotent?

## 5. Causality

The integration must be able to answer:

> Which source business change caused this outbound event or message?

Useful correlation chain:

```text
source change
   -> business event
      -> technical message(s)
         -> middleware processing
            -> target processing
               -> observed target state
```

Without that chain, “the latest successful message” is often mistaken for evidence of the reported change.

## 6. Delivery semantics

Document what the platform can actually guarantee.

Do not use vague phrases such as `exactly once` unless the complete business operation is truly protected end-to-end.

Prefer explicit statements:

- delivery may be duplicated;
- consumer is idempotent by business event ID;
- ordering is guaranteed only within partition/object key X;
- delivery is at-least-once, business application is deduplicated;
- retry after timeout requires commit-status check;
- replay of historical events requires historical mapping semantics.

## 7. Acknowledgement semantics

Define each level separately:

1. producer accepted the change;
2. transport accepted the message;
3. middleware processed it;
4. receiver API/message layer accepted it;
5. receiver business logic accepted it;
6. expected business state is observable.

A green technical status at level 3 must never be reported as business success at level 6.

## 8. Error taxonomy

Every interface should distinguish at least:

- identity/mapping error;
- schema/format error;
- authorization error;
- deterministic business validation error;
- transient infrastructure error;
- ordering/duplicate error;
- stale-state/precondition error;
- target business rejection;
- unknown commit state;
- postcondition verification failure.

Different errors require different recovery. Treating all failures as `retry` creates data corruption.

## 9. Recovery contract

Define recovery before production.

For each error class:

- automatic retry allowed?;
- max retry / backoff?;
- idempotency key?;
- manual action?;
- original payload reusable?;
- must current source state be regenerated?;
- historical mapping required?;
- business approval required?;
- reconciliation step?;
- compensation path?;
- recovery owner?

A particularly important rule for SAP master-data replication:

> Reprocessing an old successful technical message is not equivalent to redistributing a newer business change.

Always establish the causal relationship between the recovery artifact and the missing business state.

## 10. Observability contract

A production-ready interface should expose evidence for:

- source object/change identity;
- correlation/business event ID;
- current mapping version;
- message/API attempt IDs;
- timestamps across hops;
- business acknowledgement;
- target postcondition;
- retry/replay history;
- manual intervention;
- final resolution.

This is not “extra monitoring.” It is the evidence model required to operate the architecture.

## 11. Ownership model

Define at least four owners:

- **business owner** — decides whether the business outcome is correct;
- **data/process owner** — decides authority and governance semantics;
- **integration owner** — owns transport/contract behavior;
- **operations owner** — monitors failures and executes recovery.

One team can hold multiple roles. The roles should still be named separately.

## 12. Agent boundary

An agent may help with:

- evidence correlation;
- classification of known error patterns;
- finding missing evidence;
- selecting the next diagnostic check;
- explaining recovery options.

An agent should not decide by inference alone:

- canonical object identity;
- authorization;
- source-of-truth ownership;
- replay safety;
- whether stale state is acceptable;
- whether a high-impact mutation is approved.

Those belong to deterministic contracts or explicit business authority.

## Integration review card

```yaml
name: ""
business_intent: ""
producer: ""
consumer: ""
canonical_object: ""
identity_mapping_authority: ""
authoritative_attributes: []
interaction: sync | event | message | batch
correlation_id: ""
ordering: ""
duplicate_semantics: ""
idempotency: ""
acknowledgement_levels: []
postcondition: ""
error_classes: []
retry_policy: ""
replay_policy: ""
reconciliation: ""
compensation: ""
business_owner: ""
integration_owner: ""
operations_owner: ""
agent_capability: read | recommend | none
```

If these fields cannot be answered, the interface is not yet an architecture contract; it is only a transport configuration.
