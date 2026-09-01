# Contributing

Contributions should improve the repository's ability to reason about real enterprise control problems.

## Good contributions

- a synthetic SAP or enterprise scenario with a clear failure condition;
- a deterministic-vs-agentic boundary that can be tested;
- an evaluation case with an expected safe decision;
- a narrow tool or approval contract;
- an architecture pattern that improves authorization, observability, evidence, rollback, or abstention;
- source-backed research that changes an architectural decision.

## Avoid

- generic chatbot examples;
- large framework scaffolding without an enterprise use case;
- copied client data or screenshots;
- undocumented product claims;
- examples where an LLM receives broad write access;
- benchmarks that only score prose style rather than operational decisions.

## Scenario template

A scenario should normally define:

1. purpose;
2. synthetic situation;
3. available evidence;
4. deterministic checks;
5. agentic reasoning task;
6. allowed capability level;
7. expected decision shape;
8. abstention criteria;
9. failure modes the scenario is intended to catch.

## Evaluation rule

Whenever possible, add at least one machine-readable eval case for a new scenario.

The safest expected answer may be `insufficient_evidence`, `approval_required`, or `policy_blocked`. Evaluations should reward correct restraint, not only successful automation.

## Privacy

Do not contribute confidential enterprise information, credentials, internal hostnames, client-specific identifiers, production exports, or proprietary configuration.

## Reproducible checks and feedback

Before a code or contract contribution:

```bash
python scripts/validate_project_state.py
python scripts/validate_suite_contracts.py
python scripts/evaluate_suite.py --predictions reference --require-cases 50
python -m unittest discover -s tests -p 'test_*.py'
```

For adoption feedback, use the [15-minute external usability test](release/USABILITY-TEST-15-MIN.md) and the existing **SAO practical field report** issue form. A planned or blank session is not a tester result. Preserve only the failure semantics; never submit real customer data or private SAP artifacts.
