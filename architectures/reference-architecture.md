# Reference Architecture

## Objective

Keep probabilistic reasoning useful without making it the uncontrolled authority over enterprise state.

## Layers

### 1. Request and intent

A user, support analyst, or scheduled process asks for an investigation or action.

The request should be normalized into:

- business intent;
- target object or process;
- requested capability level;
- known scope and time window.

### 2. Evidence layer

Read-only tools retrieve approved evidence such as:

- business object state;
- message or interface status;
- change history;
- mapping and identity information;
- deterministic rule results;
- operational logs and prior incidents.

The evidence layer should expose stable identifiers, timestamps, source system, and provenance.

### 3. Deterministic control layer

Known rules should execute outside the LLM where possible:

- schema validation;
- required-field checks;
- identity mapping;
- authorization checks;
- status-transition rules;
- duplicate detection;
- configured business constraints.

The agent consumes these results instead of re-inventing the rules in natural language.

### 4. Reasoning layer

The agent can:

- correlate evidence;
- rank hypotheses;
- identify missing information;
- explain contradictions;
- propose a next diagnostic step;
- recommend a bounded business action.

It should not silently convert uncertainty into execution.

### 5. Decision boundary

The output is classified as one of:

- `resolved_read_only`;
- `recommendation`;
- `approval_required`;
- `insufficient_evidence`;
- `policy_blocked`.

### 6. Execution boundary

Writes are performed only through narrow tools with explicit contracts.

A write tool should know:

- which object can be changed;
- which fields or operation are allowed;
- who authorized the action;
- preconditions;
- expected postcondition;
- rollback or compensating procedure;
- audit correlation ID.

## Baseline flow

```text
REQUEST
  |
  v
INTENT NORMALIZATION
  |
  v
READ-ONLY EVIDENCE TOOLS
  |
  +--> DETERMINISTIC VALIDATION
  |          |
  |          v
  +------> AGENT REASONING
             |
             v
        DECISION CLASS
             |
       +-----+------+----------------+
       |            |                |
     REPORT      RECOMMEND       ABSTAIN
                    |
                    v
              APPROVAL GATE
                    |
                    v
              NARROW WRITE TOOL
                    |
                    v
               SYSTEM OF RECORD
                    |
                    v
             VERIFY + AUDIT
```

## Failure design

The architecture should fail closed when:

- identity cannot be resolved;
- authorization cannot be established;
- evidence sources disagree materially;
- a required deterministic check did not run;
- a requested write exceeds the tool contract;
- rollback is unavailable for a high-impact operation;
- the expected postcondition cannot be verified.

## Practical rule

The model may have broad context. The execution surface should remain narrow, typed, observable, and revocable.
