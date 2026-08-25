# SAP Agentic Operations — Practical Toolkit 0.4.0-alpha.1

## First usable product alpha

This is the first SAO version intended to be **used by SAP practitioners**, not only read as an architecture/research repository.

The practical question is:

> **Given fragmented evidence around a SAP-heavy operational problem, what can we conclude, what evidence is missing, what is safe to do next, and what would prove the business problem is actually resolved?**

## Install from the repository

```bash
git clone https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations
python -m pip install .
```

Then:

```bash
sao demo
```

The practical CLI has **zero runtime dependencies** and requires Python 3.11+.

## Included workflows

### Incident Analyzer

```bash
sao incident init ./incident --incident-id INC-001
sao incident validate ./incident
sao incident analyze ./incident
```

Evidence Pack v0.1 uses explicit source changes, message evidence, target-state observations and identity mappings.

### Quick Check

```bash
sao quickcheck demo
sao quickcheck analyze incidents.csv
```

One CSV / Excel-style list; same underlying incident semantics as the full Evidence Pack.

### Batch triage

```bash
sao batch ./incident-packs --output ./triage
```

Aggregates failure classes and next actions across many incident packs.

### Local Workbench

```bash
sao workbench ./incident
```

Read-only local browser view. No evidence upload.

### Semantic master-data reconciliation

```bash
sao reconcile demo
sao reconcile analyze ./reconciliation
```

Uses identity, per-attribute authority and snapshot freshness rather than plain source/target equality.

### Export normalization

```bash
sao normalize demo
```

Includes explicit column/value mapping and a synthetic WE02-like status mapping example (`53 -> success`, `51 -> failed`).

## Bundled incident semantics

Alpha 1 contains nine practical scenarios covering:

- old successful message vs newer authoritative change;
- business rejection after technical success;
- mapping-version drift;
- target business-state mismatch;
- technical message failure;
- complete verified business state;
- unresolved identity;
- stale target observation;
- target identity mismatch.

## Important behavior

Alpha 1 deliberately refuses several common shortcuts:

- a green old IDoc is not evidence for a newer change;
- timestamp proximity alone is not causal correlation;
- fuzzy similarity is not canonical identity;
- a historical message cannot silently use a newer identity mapping during replay;
- technical success is not business success;
- a target snapshot taken before the current event cannot verify that event;
- a newer target state must not be overwritten from a stale source export merely because the source is normally authoritative.

## Validation

The dedicated `SAO practical toolkit` GitHub Actions workflow installs the package and exercises:

- all nine incident scenarios;
- Evidence Pack init/validate/analyze;
- Quick Check;
- batch triage;
- Workbench HTML rendering;
- semantic reconciliation;
- WE02-like export normalization;
- all practical toolkit unit tests.

The alpha should not be considered ready if this workflow is not green.

## What this alpha is not

- no live SAP backend connector yet;
- no Cloud ALM collector is claimed yet;
- no production write automation;
- no AI model is required for the practical workflows;
- no claim of SAP certification or production-safety certification.

## What we need from field testing

The most valuable contribution now is not another feature request in the abstract.

It is a privacy-safe field report:

- what SAP job you tried to do;
- what evidence types you had;
- what SAO concluded;
- whether the conclusion changed/accelerated the investigation;
- what rule or evidence requirement was wrong/incomplete.

Do not publish client names, production identifiers, ticket text, internal URLs, credentials or proprietary payloads.

## Separate benchmark status

Practical Toolkit `0.4.0-alpha.1` is **not** the same thing as SAO-Bench.

SAO-Bench remains `0.3-dev` until its 51-case semantic review and benchmark freeze are complete.
