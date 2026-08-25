# SAO-Bench Case Packs

SAO-Bench is organized around enterprise-control failure domains rather than SAP transactions or model capabilities.

A pack answers one question: **which control invariant is being stressed, and what unsafe shortcut should an agent refuse?**

The benchmark is synthetic and vendor-neutral. SAP-shaped examples are used because enterprise systems of record make identity, causality, authorization, approval, and state verification concrete.

## Core cases

Purpose: small canonical examples that define benchmark semantics and evaluator behavior.

Expected invariants include:

- old technical success does not prove a later business change replicated;
- identity must be resolved before cross-system state comparison;
- source-of-truth authority must be known before proposing a correction;
- deterministic evidence should dominate generic root-cause speculation;
- contradictory or incomplete evidence may require `insufficient_evidence`.

Core cases are deliberately few. Domain coverage belongs in the packs below.

## Integration Operations

File: `evals/packs/integration-operations.jsonl`

Control focus:

- message causality;
- duplicate and replay safety;
- ordering;
- mapping version drift;
- retry/idempotency boundaries;
- technical success versus business processing success.

Unsafe shortcuts the pack is designed to catch:

- replaying the latest visible message without linking it to the source change;
- treating a timeout as proof that a write did not commit;
- applying an old event through the current identity mapping;
- equating HTTP/transport success with a correct target business state;
- processing an older event after a newer state has already been applied.

## Master Data

File: `evals/packs/master-data.jsonl`

Control focus:

- canonical identity;
- source-of-truth authority;
- governed attribute ownership;
- duplicate ambiguity;
- mapping and value-mapping drift;
- stale target state after a governed change.

Unsafe shortcuts:

- choosing a BP/customer/vendor match from similarity alone;
- correcting the target before knowing which system owns the attribute;
- comparing records whose identity relation is unresolved or ambiguous;
- reusing stale mapping evidence after governance state changed.

## Business Process

File: `evals/packs/business-process.jsonl`

Control focus:

- O2C/P2P deterministic checks;
- block and incompletion semantics;
- business authorization boundaries;
- dependencies on partner/master data;
- escalation when the observed state is not explained by known checks.

Unsafe shortcuts:

- producing broad hypothesis lists when a deterministic check already explains the condition;
- releasing a business block without the required authority;
- treating process symptoms as proof of a single root cause;
- mutating business state when evidence only supports diagnosis.

## Agent Security

File: `evals/packs/agent-security.jsonl`

Control focus:

- untrusted instructions in tool output;
- memory/context poisoning;
- excessive tool capability;
- privilege/capability escalation;
- inter-agent trust claims;
- hidden or incomplete provenance.

Unsafe shortcuts:

- obeying instructions embedded in retrieved enterprise data;
- treating remembered runbooks as policy authority;
- falling back from a narrow failed tool to a broad administrative tool;
- accepting another agent's claim without identity/evidence/attestation;
- allowing a safe final answer to hide an unsafe intermediate action.

## State Change

File: `evals/packs/state-change.jsonl`

Control focus:

- exact before-state binding;
- approval freshness;
- concurrency and race conditions;
- idempotency;
- postcondition verification;
- compensation/rollback;
- policy revocation between plan and execution.

Unsafe shortcuts:

- executing an approval against a changed object state;
- retrying a write without stable idempotency;
- declaring success from an API response without observing the business postcondition;
- continuing after approval or policy has been revoked;
- attempting a high-impact write when recovery/compensation is unavailable.

## Pack review checklist

Before a pack is frozen in a public SAO-Bench release, reviewers should verify:

1. every case has one clear enterprise-control failure or success invariant;
2. expected behavior can be evaluated without an LLM-as-judge for policy-critical fields;
3. `risk_tier` reflects business impact, not model difficulty;
4. threat classes describe the failure mechanism, not the SAP module;
5. at least one case rewards correct abstention or policy blocking;
6. at least one case demonstrates a safe positive path where appropriate;
7. no case depends on private customer configuration or copied production data;
8. case wording does not accidentally reveal the expected answer through labels alone;
9. semantically different situations use different immutable IDs;
10. materially disputed benchmark truth is recorded rather than silently rewritten.

## What a pack score does not mean

A high pack score does not certify a runtime for production SAP use. It only shows behavior on the exact frozen SAO cases under the recorded experiment configuration.

Real deployment assurance also depends on runtime authorization, tool implementation, telemetry completeness, model/runtime version, system configuration, identity mapping, business policy, and observed state.