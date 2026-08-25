# External field-validation gate

Practical Toolkit 0.4.0-alpha.1 is feature-complete enough for the first practitioner loop.

Before starting another large horizontal framework layer, collect:

1. **Three independent practitioner runs**
   - at least two different SAP roles/domains if possible;
   - Quick Check or full Evidence Pack both count.

2. **One incorrect or incomplete SAO conclusion**
   - classification wrong;
   - missing evidence rule wrong;
   - recovery boundary too strict/too permissive;
   - field model unable to represent the real situation.

3. **One real export normalization**
   - sanitized column names/layout are enough;
   - preserve the mapping file, not production data.

4. **One product change grounded in field evidence**
   - diagnostic rule;
   - Evidence Pack field;
   - reconciliation classification;
   - import mapping;
   - Workbench usability change.

## Why this gate exists

SAO has already demonstrated that it can accumulate architecture, scenarios and code quickly.

The remaining risk is product-model error: building a coherent system around assumptions that practitioners do not actually need.

A field report that disproves one SAO assumption is therefore a successful alpha result.

## Exceptions

Work may continue without field validation only for:

- security fixes;
- correctness/regression fixes;
- packaging/install fixes;
- documentation required to complete an existing workflow;
- benchmark semantic review already tracked in #17;
- release mechanics.

New domain packs, agent frameworks, connectors, write capabilities and plugin systems should wait for field evidence or a clearly documented external demand.
