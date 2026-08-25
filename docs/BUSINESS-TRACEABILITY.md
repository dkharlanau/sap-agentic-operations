# Business-to-System Traceability

A system analyst's job is not finished when a requirement has been written. It is finished when the requirement can be traced to a **business invariant, system behavior, observable evidence, test, and operational owner**.

SAO uses this chain:

```text
BUSINESS NEED
    |
    v
REQUIREMENT
    |
    v
BUSINESS INVARIANT
    |
    v
SYSTEM / DATA / INTEGRATION CONTRACT
    |
    v
CONTROL OR DECISION RULE
    |
    v
OBSERVABLE EVIDENCE
    |
    v
TEST / EVAL
    |
    v
OPERATIONAL RESPONSE
```

The purpose is not paperwork. The purpose is to stop requirements from disappearing inside configuration, interfaces, prompts, and assumptions.

## 1. Requirement

Write the business outcome without prematurely choosing implementation.

Example:

> Approved changes to customer delivery controls must reach every in-scope fulfillment system before the customer can be processed under the new state.

Avoid:

> Send field X in segment Y.

The second sentence may become a solution detail. It does not explain what must remain true if the integration mechanism changes.

## 2. Business invariant

Turn the requirement into something that can be violated.

Example:

> No fulfillment system may act on a customer state that is older than the latest activated governed delivery-control state for that system's scope.

This is the anchor for architecture, testing, incident handling, and agent evaluation.

## 3. Scope

Define the dimensions that change the rule:

- company code;
- sales organization / distribution channel / division;
- plant / purchasing organization;
- country / region;
- business partner role;
- customer/vendor account group;
- process variant;
- system/client;
- effective date;
- migration/cutover phase.

Many SAP defects are not failures of the rule itself. They are failures to model scope explicitly.

## 4. Authority

State who decides the business truth.

For a master-data requirement, this may be:

- governance system for one field;
- local operational system for another;
- business workflow for activation;
- regulatory source for a third.

Do not infer authority from where a field happens to be populated.

## 5. System behavior

Describe what systems must do to preserve the invariant.

Example:

1. governance activates a value;
2. change receives canonical object identity and version;
3. integration publishes the active change;
4. receiver resolves the target identity using the correct mapping version;
5. receiver validates scope;
6. receiver persists the value;
7. target postcondition proves the new active state;
8. unresolved targets remain visible for recovery.

Now the requirement is operationally meaningful.

## 6. Control classification

Classify each rule as:

- **deterministic validation** — exact rule, schema, status, authorization;
- **policy decision** — explicit allow/deny/approval requirement;
- **human business decision** — exception, risk acceptance, ownership;
- **agentic reasoning** — correlation, hypothesis, explanation, next diagnostic step.

This prevents an LLM from becoming the accidental implementation of a business rule.

## 7. Evidence

Ask what proves each step actually happened.

Typical evidence:

- source change timestamp/version;
- approval/workflow state;
- change pointer/event/message ID;
- interface processing state;
- mapping version;
- target object state;
- business acknowledgement;
- audit correlation;
- postcondition observation.

A requirement that cannot name its evidence is difficult to test and almost impossible to support well.

## 8. Acceptance criteria

Write acceptance criteria as observable invariants, not UI instructions.

Good:

- Given an activated governed value at version 12, every in-scope target either reports version 12 or exposes a traceable unresolved replication state.
- A duplicate delivery of business event `E` does not apply the business mutation twice.
- A target identity that cannot be resolved blocks comparison and mutation.
- A successful transport status without the expected target state is reported as unresolved, not successful.

These criteria can become tests, benchmark cases, or operational monitors.

## 9. Negative acceptance criteria

Enterprise systems need explicit `must not` behavior.

Examples:

- must not overwrite a newer target state from an older source snapshot;
- must not reprocess a historical message as recovery without proving causal relevance;
- must not select a BP match only because one similarity score is highest;
- must not execute a governed change because a business deadline is urgent;
- must not treat tool/retrieval text as policy authority.

Negative criteria are particularly valuable for agentic systems because fluent output can hide unsafe behavior.

## 10. Operational ownership

Every requirement should identify who acts when the invariant is violated.

Possible owners:

- business process owner;
- master-data governance team;
- integration operations;
- SAP AMS/application support;
- platform/SRE team;
- security/governance;
- data steward.

`The interface team` is often too vague. Ownership should follow the failure class.

## 11. Traceability matrix

A compact example:

| ID | Requirement | Invariant | Control | Evidence | Test | Owner |
|---|---|---|---|---|---|---|
| R-01 | Active customer control reaches targets | No target acts on stale active state | identity + version + postcondition | source version, event ID, target version | stale target case | MDG + integration ops |
| R-02 | Retry must not duplicate business change | One event produces at most one logical mutation | idempotency | event ID, idempotency record | duplicate/replay case | integration ops |
| R-03 | Governed write needs authority | Mutation requires scoped approval | policy + approval | approval ref, before-state | missing/stale approval cases | business owner |

## 12. Agent-ready requirement

For an agentic workflow add three more questions:

1. What evidence is the agent allowed to read?
2. What decision class may it produce?
3. What exact fact/policy/human action is required before capability can increase?

Example:

```yaml
agent:
  allowed_capability: recommend
  evidence:
    - source_change
    - interface_status
    - target_state
    - identity_mapping
  may_not_decide:
    - business_authority
    - approval_validity_without_reference
    - write_authorization
  escalation_gate:
    execute: scoped_approval + fresh_precondition + typed_tool
```

## 13. Definition of done for analysis

A requirement is analysis-ready when another competent person can answer all of these without asking what the analyst “meant”:

- What business outcome matters?
- What must never become false?
- What is the exact scope?
- Who owns the truth?
- Which systems enforce or distribute it?
- Which checks are deterministic?
- Where is judgment required?
- What evidence proves success?
- What evidence proves failure?
- What are the negative criteria?
- Who owns recovery?
- What changes during cutover?

That is the difference between documenting a request and engineering a requirement.
