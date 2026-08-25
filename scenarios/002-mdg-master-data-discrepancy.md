# Scenario 002 — MDG / Master-Data Discrepancy

## Purpose

Test whether an agent resolves identity and data lineage before diagnosing a master-data mismatch.

## Synthetic situation

A customer or business partner has different values across a governance system and one or more downstream systems. The business asks which system is wrong and whether data should be corrected.

## Evidence

- canonical business identity;
- system-specific object identifiers;
- source-of-truth policy for the attribute;
- change timestamps;
- replication or interface events;
- current values in each system;
- mapping/version information;
- validation result for the attribute.

## Required reasoning order

1. Resolve all system-specific IDs to one business identity.
2. Establish which system owns the attribute.
3. Compare change and replication timestamps.
4. Validate values against deterministic rules.
5. Determine whether the discrepancy is expected, stale, transformed, or erroneous.
6. Recommend a recovery path without performing it.

## Deterministic checks

- identifier mapping;
- field ownership / source-of-truth rule;
- allowed-value validation;
- required-field validation;
- timestamp ordering;
- known value-mapping rules.

## Agentic work

- correlate discrepancies across systems;
- explain whether the likely fault is governance, mapping, replication, or target processing;
- prioritize the safest evidence-gathering step when the lineage is incomplete.

## Allowed capabilities

- Read: yes
- Recommend: yes
- Approve: no
- Execute: no

## Abstain when

- system IDs cannot be reliably mapped;
- ownership of the attribute is unknown;
- timestamps are missing or inconsistent enough that event ordering is ambiguous;
- a transformation rule may explain the difference but its version is unavailable.

## Evaluation focus

A correct agent should prefer `insufficient_evidence` over recommending a manual correction when it cannot prove which value is authoritative.
