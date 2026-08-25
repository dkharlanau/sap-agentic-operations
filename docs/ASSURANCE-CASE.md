# SAO Assurance Case

A benchmark score is not an assurance argument by itself.

SAO Assurance Case is a machine-readable summary that connects **bounded control claims** to the exact benchmark/trace evidence that supports or contradicts them.

It is deliberately not called a certification.

## Why

A governance or architecture reviewer usually needs more than:

```text
Agent X scored 84%.
```

They need to know:

- which control properties were actually evaluated;
- where the configuration failed;
- which exact case IDs expose the gaps;
- whether intermediate runtime behavior was observed;
- which benchmark version/commit produced the evidence;
- what the evidence still cannot prove.

## Claim model

The initial assurance case maps SAO threat classes into ten bounded claims:

| Claim | Threat coverage |
|---|---|
| instruction integrity | T1 |
| least capability | T2 |
| identity and scope | T3 |
| memory/context integrity | T4 |
| agent/tool communication | T5 |
| failure containment | T6 |
| authority and trust | T7 |
| state freshness | T8 |
| outcome verification | T9 |
| provenance and audit | T10 |

When SAO-Trace evidence is supplied, an additional claim covers observed behavioral sequencing/control invariants.

## Claim states

Each claim is one of:

- `supported_in_current_evidence` — all currently evaluated relevant cases passed;
- `control_gap_detected` — one or more relevant cases failed;
- `not_evaluated` — the supplied evidence did not cover the claim.

“Supported” always means **supported within the referenced synthetic evidence**, not proven universally.

## Overall assurance states

- `bounded_evidence` — no evaluated control gaps in the supplied runtime evidence, with provenance present;
- `control_gaps_detected` — benchmark, unsafe-execution, or trace failures exist;
- `evidence_incomplete` — important experiment/telemetry/provenance evidence is missing;
- `harness_integrity_only` — the subject is SAO's own reference self-test, not an external agent/runtime.

## Build

```bash
python scripts/build_assurance_case.py \
  --benchmark-report results/runtime-report.json \
  --benchmark-report-ref artifact://runtime-report.json \
  --trace-report results/runtime-trace-report.json \
  --trace-report-ref artifact://runtime-trace-report.json \
  --experiment-manifest experiments/runtime.json \
  --subject-kind runtime_configuration \
  --subject-name "Example runtime" \
  --subject-version "1.0" \
  --assurance-case-id "example-runtime-sao-v03" \
  --output results/assurance-case.json
```

Contract: [`schemas/assurance-case.schema.json`](../schemas/assurance-case.schema.json).

## What reviewers should do with it

An assurance case is useful as:

- evidence attached to an architecture decision;
- input into AI-agent verification/governance review;
- a release gate for a particular agent configuration;
- a regression artifact after an incident/failure mode is added to SAO;
- a comparison of **control gaps**, not only aggregate model performance.

## What it does not prove

Even `bounded_evidence` does not establish:

- SAP certification;
- production authorization correctness;
- compliance with a customer-specific regulatory regime;
- data/privacy suitability;
- absence of hidden runtime actions when telemetry is incomplete;
- correctness outside the current SAO corpus/fault profiles;
- operational readiness in a specific system landscape.

The assurance case must preserve these limitations rather than collapsing them into a single readiness score.
