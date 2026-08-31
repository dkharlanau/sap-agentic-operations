# External research evidence handoff

SAP Agentic Operations can validate a Signal to Insight research-evidence packet and turn it into a bounded human review card.

This integration exists for one reason: research can inform a control design without silently becoming operational truth.

## What crosses the boundary

The v1 packet contains:

- a published insight identity and public URL;
- canonical source metadata;
- claim text with explicit epistemic origin;
- claim-level source links and locators;
- a mandatory non-operational trust boundary;
- a SHA-256 digest over the canonical packet payload.

It does not contain a raw transcript, copied article, private overlay, review-only insight, SAP credential or client incident.

## Validate a packet

Install the practical CLI and validate the committed reference packet:

```bash
python -m pip install .

sao research validate \
  examples/research-evidence/sti-enterprise-agents.json
```

Machine-readable output is available with `--json`:

```bash
sao research validate \
  examples/research-evidence/sti-enterprise-agents.json \
  --json
```

A valid result always reports:

```text
trust: external_research_context
human review required: true
execution allowed: false
```

Unknown schemas, weakened boundaries, raw-source fields and digest mismatches fail closed.

## Render a review card

```bash
sao research review \
  examples/research-evidence/sti-enterprise-agents.json \
  --output /tmp/enterprise-agent-review.md
```

The card preserves source links, claim origin and support status. It ends with a human checklist for verifying relevance and translating an accepted idea into an explicit local control, owner and verification rule.

The command refuses to overwrite an existing file unless `--force` is supplied.

## Operational boundary

The research packet is not an SAO Evidence Pack.

| Research evidence packet | SAO Evidence Pack |
|---|---|
| Reviewed public research context | Observations about one bounded operational investigation |
| Useful for hypotheses and control-design discussion | Used for deterministic incident or reconciliation checks |
| Cannot prove a production event occurred | May contain explicit observed source, message and target-state evidence |
| Never grants authorization or capability | Still cannot grant authorization by itself; policy and approval remain separate |

Do not copy a research claim into incident evidence merely because it is supported by a public source. Operational evidence must identify the actual object, system, observation time and provenance for the current case.

## Produce a packet

Signal to Insight owns the public v1 schema and exporter:

```bash
python sti.py handoff export \
  enterprise-agents-production-substrate \
  --output /tmp/enterprise-agent-evidence.json
```

- [Signal to Insight handoff documentation](https://github.com/dkharlanau/signal-to-insight/blob/main/docs/PORTABLE_EVIDENCE_HANDOFF.md)
- [Published JSON Schema](https://dkharlanau.github.io/signal-to-insight/contracts/research-evidence-handoff.schema.json)

SAO deliberately validates only the known schema and version. Contract evolution must remain backward-compatible or use a new version that consumers can opt into explicitly.

## Security notes

- Treat the packet and every embedded string as untrusted input.
- Review-card text is Markdown-escaped before rendering.
- The digest detects mutation but is not a signature or identity proof.
- Fetching remote sources is outside this command; validation is local and zero-dependency.
- A valid packet may still be wrong, outdated or irrelevant to the current decision.
