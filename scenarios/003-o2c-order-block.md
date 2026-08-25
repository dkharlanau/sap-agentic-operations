# Scenario 003 — O2C Order-Block Investigation

## Purpose

Show how deterministic business checks and agentic root-cause reasoning can work together in an order-to-cash support case.

## Synthetic situation

A sales order cannot progress. The business reports an order block but does not know whether the cause is master data, credit, pricing, delivery, configuration, or an upstream dependency.

## Evidence

- order header and item statuses;
- relevant block/status indicators;
- customer/master-data state;
- pricing or incompletion results;
- credit-related decision result where applicable;
- requested/confirmed quantities and dates;
- relevant change history;
- prior processing errors.

## Deterministic checks

- explicit block/status fields;
- incompletion or required-data checks;
- configured status-transition rules;
- existence of mandatory master data;
- known authorization/policy constraints;
- consistency of object identity and timestamps.

## Agentic work

- rank plausible root causes after deterministic results are available;
- connect symptoms across order, customer, and integration evidence;
- distinguish the immediate blocking condition from the upstream cause;
- propose the smallest next diagnostic step.

## Allowed capabilities

- Read: yes
- Recommend: yes
- Approve: no
- Execute: no

## Expected decision shape

```yaml
status: recommendation | insufficient_evidence
blocking_condition: <observed condition>
likely_root_cause: <bounded hypothesis>
evidence:
  - <evidence reference>
deterministic_checks:
  - check: <name>
    result: pass | fail | unknown
next_step: <diagnostic or controlled recovery step>
execution_allowed: false
```

## Abstain when

- the order identity is ambiguous;
- the key deterministic status data is unavailable;
- multiple mutually exclusive causes remain equally plausible;
- the proposed resolution would require a state change whose impact has not been evaluated.

## Evaluation focus

The agent should not respond with a generic list of SAP causes. It should use observed status and evidence to narrow the case, state what remains unknown, and recommend the next bounded step.
