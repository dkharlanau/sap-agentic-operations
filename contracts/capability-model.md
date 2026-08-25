# Capability Model

Enterprise agents should not receive a single undifferentiated permission called "access".

This model separates four capability classes.

## Read

Purpose: retrieve approved evidence.

Examples:

- read business object state;
- inspect interface or IDoc status;
- retrieve change history;
- retrieve mapping or identity references;
- read an approved operational runbook.

Controls:

- authorization remains source-system enforced;
- retrieved data should include provenance;
- sensitive fields should be minimized;
- arbitrary query or URL access should not be exposed by default.

## Recommend

Purpose: reason over evidence and propose an action.

Expected output:

```yaml
status: recommendation
hypothesis: <bounded explanation>
evidence:
  - <evidence reference>
missing_evidence: []
proposed_action: <action or next diagnostic step>
confidence: low | medium | high
execution_allowed: false
```

A recommendation is not permission to execute.

## Approve

Purpose: authorize a specific proposed state change.

Approval should bind to:

- exact object identity;
- exact proposed operation;
- relevant before-state;
- expected after-state;
- approver identity;
- expiration or one-time-use semantics where appropriate.

Changing the proposed operation invalidates the approval.

## Execute

Purpose: perform a narrow state-changing operation.

Execution tools should be more constrained than read tools. Prefer typed business operations over generic database, RFC, HTTP, scripting, or GUI access.

A useful execution response includes:

```yaml
status: executed | rejected | failed
correlation_id: <id>
object: <stable object identity>
operation: <operation name>
precondition_check: passed | failed
result: <bounded result>
postcondition_check: passed | failed | not_available
rollback_reference: <reference or null>
```

## Capability escalation

An agent should begin at the lowest capability sufficient for the request.

```text
READ -> RECOMMEND -> APPROVE -> EXECUTE
```

Escalation requires an explicit reason. A failure at one level must not silently trigger a broader capability.

## Default policy

For public reference scenarios in this repository:

- `Read`: allowed within the synthetic scenario;
- `Recommend`: allowed;
- `Approve`: represented as an explicit human/policy boundary;
- `Execute`: simulated only unless a deliberately safe test harness exists.
