# Research and Evidence Policy

This repository may include research notes about enterprise agents, SAP operations, interoperability, evaluation, security, and governance.

Research notes should be useful as evidence, not as decoration.

## Source hierarchy

Prefer, in order:

1. primary standards, protocol specifications, official product documentation, and original papers;
2. implementation repositories and release notes;
3. strong technical or industry analysis with identifiable authorship;
4. community discussion for operational experience, clearly labeled as anecdotal.

## Rules

- Date time-sensitive claims.
- Link claims to the source that supports them.
- Separate documented behavior from interpretation.
- Do not generalize one product implementation into an enterprise-wide rule.
- Do not present experimental protocols or previews as stable standards.
- Do not publish client architecture, incidents, screenshots, IDs, or confidential configuration.
- Prefer small reproducible examples over broad claims.
- When evidence conflicts, preserve the disagreement rather than forcing a single conclusion.

## SAP-related content

Public SAP scenarios in this repository are synthetic abstractions. They are intended to demonstrate operational reasoning patterns, not reproduce a client landscape or replace official SAP documentation.

Any configuration, API, transaction, table, authorization, or product-specific behavior introduced later should be verified against the relevant supported release and documented source before publication.

## Agent claims

Claims about agent capability should distinguish:

- what a model can generate;
- what a tool contract allows;
- what authorization permits;
- what has been evaluated;
- what is safe to execute.

A working demo is not automatically evidence of production suitability.
