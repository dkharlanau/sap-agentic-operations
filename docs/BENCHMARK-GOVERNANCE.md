# SAO-Bench Governance and Case Disputes

SAO-Bench is an independent experimental benchmark. Its expected answers are reviewable claims, not unquestionable truth.

This process exists to make disagreement inspectable before SAO is used for broader enterprise-agent assurance claims.

## What can be disputed

A case dispute should use one or more of these categories:

- **wording ambiguity** — the published input supports more than one reasonable interpretation;
- **incorrect expected decision** — the expected status/action is unsafe or unjustified;
- **missing evidence** — the case assumes information that is not actually present in the input;
- **risk-tier dispute** — business impact is under- or over-classified;
- **threat-taxonomy dispute** — mapped T1–T10 classes do not describe the failure mechanism;
- **answer leakage** — labels/field names reveal benchmark truth rather than testing reasoning/control behavior;
- **duplicate coverage** — another released case tests the same invariant without meaningful additional coverage;
- **SAP/domain realism** — the synthetic abstraction is misleading enough to distort the enterprise-control lesson.

## Required dispute evidence

A useful dispute identifies:

1. exact case ID and benchmark version/commit;
2. disputed field(s);
3. the current expected behavior;
4. proposed interpretation or correction;
5. why the current benchmark truth is unsafe, ambiguous, or redundant;
6. source/reference when the dispute depends on product/standard behavior;
7. whether the proposed change should alter old result comparability.

## Resolution states

- `confirmed` — case remains unchanged; rationale is documented;
- `clarified-nonsemantic` — wording/documentation changes without expected-answer change;
- `corrected-breaking` — benchmark truth changes and versioning impact is recorded;
- `retired` — case remains in release history but is excluded from a future corpus;
- `split` — one ambiguous case becomes two materially different immutable case IDs;
- `deferred` — evidence is insufficient to resolve the dispute.

## Frozen release rule

After a public benchmark release:

- never silently rewrite the expected answer;
- never reuse the same case ID for a materially different situation;
- preserve the old released case and result history;
- record old expectation, new expectation, rationale, and effective version in `CHANGELOG.md`;
- use a new case ID when the situation itself changes materially.

## False positives and false negatives

SAO should maintain a public limitations record as external evidence accumulates.

A **false positive** means SAO flags a control failure that is not actually unsafe under the documented experiment/enterprise semantics.

A **false negative** means an implementation passes SAO while exhibiting a materially unsafe enterprise-agent behavior not covered or detected by the benchmark.

False negatives are especially important: they define where SAO assurance claims must remain bounded.

## Maintainer conflict rule

A maintainer should not resolve a substantive benchmark-truth dispute only by restating the existing expected answer. The resolution should reference the control invariant, supporting evidence, and versioning consequence.

For controversial R3/R4 execution cases, prefer an external enterprise operations/security reviewer before freeze when practical.

## Review objective

The goal is not consensus on every SAP implementation detail. SAO cases should remain synthetic and architecture-focused.

The goal is narrower: **would a reasonable enterprise agent be permitted to make this decision or state change from the evidence, identity, policy, approval, and state conditions actually represented in the case?**

## Issue form

Use the `SAO-Bench case dispute` issue template. Keep confidential landscape details out of public issues.