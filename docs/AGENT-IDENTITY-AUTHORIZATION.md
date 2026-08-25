# Agent Identity and Authorization in SAP / Enterprise Systems

An enterprise agent should never be represented by one vague statement:

> “The bot has access to SAP.”

That sentence hides the most important security questions: **who is acting, on whose behalf, under which business authority, against which object, for which operation, and with which evidence?**

## 1. Separate the identities

A governed agent interaction can contain several different identities:

### Human initiator

The person who asked for the task.

Examples:

- support analyst;
- sales operations user;
- data steward;
- integration operator.

### Agent/runtime identity

The software identity running the reasoning/orchestration.

This identity should not automatically inherit the human's full access or carry broad permanent SAP credentials.

### Tool/service identity

The identity used by the API/MCP/tool when it communicates with the target system.

### Business approver

The person or deterministic policy authority allowed to approve a material state change.

These identities can overlap, but they should never be confused.

## 2. Authentication is not authorization

Authentication answers:

> Who/what is calling?

Authorization answers:

> Is this caller allowed to perform this operation on this object in this context?

Business authority answers a third question:

> Even if technically allowed, who is entitled to decide that this business change should happen?

An integration technical user may be authorized to write customer data technically while having no business authority to decide a credit or governance exception.

## 3. Delegation chain

For delegated agent actions preserve a chain such as:

```text
human U1
  -> requests business intent
     -> agent A1 reasons
        -> policy P7 evaluates
           -> approver U2 authorizes operation O
              -> tool T3 executes on object X
```

The audit record should make clear which identity contributed which authority.

A service account should not erase the human/business context.

## 4. Object-level scope

Authorization should bind to business object scope whenever possible.

Examples:

- customer/BP X;
- sales order Y;
- supplier Z;
- business event E;
- company code / sales organization scope;
- one attribute group.

Dangerous pattern:

> User is authorized for one order, delegated agent calls a tool on another order because the tool credential is broader.

This is a classic confused-deputy shape.

## 5. Operation-level scope

`write customer` is too broad.

Prefer operations such as:

- `request_customer_replication`;
- `replay_business_event`;
- `release_delivery_block`;
- `apply_approved_master_data_change`;
- `run_reconciliation`.

Each operation should have its own authorization and preconditions.

## 6. Field / attribute scope

For master data, write permission may need to be narrower than object permission.

An agent/tool allowed to correct a delivery-control attribute should not automatically be able to change:

- bank data;
- tax identifiers;
- credit attributes;
- addresses;
- partner functions.

Attribute authority and authorization should align.

## 7. Temporal scope

Authorization can become stale.

Bind governed actions to:

- approval time;
- expiry;
- policy version;
- before-state version/hash;
- mapping version where identity can drift.

A valid approval from ten minutes ago may be invalid after the object changes.

## 8. Policy version

The policy that authorized the plan must still be valid when execution occurs.

Possible drift:

- tool is revoked;
- role changed;
- business rule changed;
- emergency freeze activated;
- cutover phase changed.

Execution should re-evaluate policy at the point of action, not only during planning.

## 9. Segregation of duties

Agentic orchestration can accidentally collapse roles that were intentionally separated.

Examples:

- requestor + approver;
- data preparer + data activator;
- business decision + technical execution;
- exception creator + exception approver.

Do not remove SoD by routing all steps through one service principal.

The agent may coordinate the workflow while separate principals/policies preserve the business separation.

## 10. Emergency access

Emergency/break-glass access should remain exceptional even when an agent is available.

Requirements should include:

- explicit activation;
- reason;
- time-bound scope;
- stronger audit;
- post-use review;
- no silent reuse by future agent tasks.

An agent should never infer emergency authority from urgency.

## 11. Tool authorization must be enforced at the tool/system

Do not rely on the model remembering that a tool is restricted.

The tool/runtime should deterministically reject:

- wrong object;
- wrong operation;
- missing approval;
- stale precondition;
- revoked policy;
- expired delegation;
- excessive scope.

Prompt instructions are defense-in-depth, not authorization enforcement.

## 12. Read access is also sensitive

Read-only agents can still create enterprise risk.

Examples:

- cross-user data exposure;
- HR/customer/supplier sensitive fields;
- excessive retrieval;
- data exfiltration through external tools;
- operational logs containing secrets or personal data.

Apply least privilege to read evidence too.

## 13. Recommended authorization envelope

```yaml
subject:
  human_initiator: U1
  agent_runtime: A1
  tool_principal: T3
business_object:
  type: sales_order
  id: SO-100
scope:
  operation: release_delivery_block
  fields: [delivery_block]
policy:
  id: POL-17
  version: 4
approval:
  required: true
  reference: AP-900
  approver: U2
  expires_at: 2026-08-25T18:00:00Z
precondition:
  object_version: 12
  state_hash: sha256:...
idempotency_key: OP-...
postcondition:
  delivery_block: false
correlation_id: CORR-...
```

## 14. Agent authorization anti-patterns

Avoid:

- shared permanent SAP credentials embedded in agent config;
- generic service user with broad mutation scope;
- agent deciding its own authorization based on prompt/context;
- technical access treated as business approval;
- approval boolean without object/operation/state scope;
- delegation without preserving human identity;
- silently widening tool scope after failure;
- using emergency access because the task is urgent.

## Architecture review question

> If the agent attempts the wrong action on the wrong object with a convincing explanation, which deterministic component says “no”?

If the answer is “the model should know better,” authorization is not yet designed.
