# SAP Cloud ALM as an Evidence Source

SAP Cloud ALM already solves important monitoring problems. SAO should not duplicate them.

The useful integration pattern is:

```text
SAP Cloud ALM
      |
      | monitoring / analytics / exported evidence
      v
SAO canonical evidence
      |
      v
identity + causality + business-state analysis
```

## Two different Cloud ALM roles

### 1. Integration Monitoring Analytics

The Generic Integration Monitoring Analytics API is useful for:

- discovery;
- aggregate visibility;
- filtering by monitored integration context;
- identifying time windows or integration areas that deserve deeper investigation.

This is valuable input for SAO, but aggregate monitoring data should not automatically be treated as a causal message-level evidence chain.

A dashboard metric such as “failed messages = 5” does not by itself answer:

- which exact business change is affected;
- whether a later successful message corresponds to that change;
- which identity/mapping version was used;
- whether the target business state is correct.

### 2. Raw Data Outbound Logs / OpenTelemetry-style evidence

Cloud ALM Integration & Exception Monitoring can expose collected messages/exceptions to other services through its raw-data outbound capabilities.

Where that feed contains sufficient identifiers/timestamps/status context, it is a more natural source for detailed SAO message evidence.

The long-term collector should normalize supported raw evidence into the existing canonical table:

```text
message_id
change_id / correlation evidence
object_id
target_id
technical status
business acknowledgement
created_at
mapping/version context when known
```

Missing causal fields must remain missing. A connector must never invent them merely to satisfy the Evidence Pack schema.

## Planned SAO integration shape

Prefer a two-stage flow:

```text
Cloud ALM analytics
       ↓
find candidate integration/time window
       ↓
raw message / exception evidence where available
       ↓
explicit normalization
       ↓
Evidence Pack
       ↓
Incident Analyzer
```

Potential commands after field validation:

```text
sao calm discover ...
sao calm import-otel ...
```

The exact commands should only be implemented against verified supported payloads.

## Security boundary

Any Cloud ALM integration should be:

- read-only;
- least-privilege;
- explicit about required scopes;
- local-output by default;
- free of backend SAP write credentials;
- unable to convert a monitoring status into an execution authorization.

## Non-goal

SAO will not claim to be a Cloud ALM replacement.

Cloud ALM answers important observability questions. SAO is interested in the additional operational question:

> **Given the observed evidence, what business change can we explain, what evidence is still missing, what recovery is safe, and what proves the business outcome?**
