# State-Change Safety Envelope

A recommendation becomes executable only after it is converted into a state-change safety envelope.

Canonical schema: [`../schemas/write-envelope.schema.json`](../schemas/write-envelope.schema.json).

## The rule

> Approval is valid for an exact action against an exact object in an expected current state — not for a vague intent.

## Required bindings

The envelope binds:

- decision ID;
- business-risk tier;
- canonical object identity;
- target system and target-system ID;
- typed operation and parameters;
- allowed fields;
- current before-state hash/version/expected state;
- expected postcondition;
- deterministic policy result;
- approval record when required;
- expiration;
- idempotency key;
- correlation ID;
- rollback or compensating action.

## Example

```json
{
  "envelope_version": "0.1",
  "decision_id": "decision-123",
  "risk_tier": "R3",
  "object": {
    "canonical_type": "sales_order",
    "canonical_id": "order-100",
    "target_system": "synthetic-s4",
    "target_system_id": "SO-100"
  },
  "operation": {
    "name": "release_business_block",
    "parameters": {"reason": "verified_condition_cleared"},
    "allowed_fields": ["business_block"]
  },
  "precondition": {"state_hash": "sha256:before"},
  "postcondition": {
    "expected_state": {"business_block": false},
    "verification_method": "read_after_write"
  },
  "policy": {
    "result": "require_approval",
    "policy_ref": "policy://release-block/r3"
  },
  "approval": {
    "approval_id": "approval-9",
    "approver": "human:operations-owner",
    "approved_at": "2026-08-25T10:00:00Z",
    "bound_state_hash": "sha256:before"
  },
  "expires_at": "2026-08-25T10:15:00Z",
  "idempotency_key": "release-order-100-v4",
  "correlation_id": "corr-42",
  "compensation": {
    "available": true,
    "reference": "procedure://restore-business-block"
  }
}
```

## Execution algorithm

A write adapter should check, in this order:

1. envelope parses and operation is allow-listed;
2. object identity is still resolved;
3. current authorization is valid;
4. policy result is not `block`;
5. required approval exists, is unexpired, and is bound to this operation;
6. current before-state still matches the envelope;
7. idempotency key has not already completed the action;
8. execute the narrow operation;
9. read back and verify the business postcondition;
10. write the audit event;
11. if verification fails, stop downstream actions and enter compensation/escalation.

## What invalidates approval

- target object changes;
- operation name changes;
- parameters materially change;
- allowed fields broaden;
- before-state changes;
- approval expires;
- policy changes to block;
- target identity becomes ambiguous.

An invalid approval returns the flow to diagnosis. The agent must not silently request a broader tool.
