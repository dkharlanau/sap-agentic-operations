# SAP Agentic Operations — Practical Toolkit 0.4.0-alpha.3

Alpha 3 is a proof-oriented documentation release of the local-first practical toolkit. It makes the shortest safe product path explicit without changing Evidence Pack or CLI behavior.

## Highlights

- Run one exact installed-CLI command against the checked-in synthetic missing-event Evidence Pack.
- Inspect a named deterministic JSON artifact with `insufficient_evidence`, `current_outbound_event_not_proven`, and `execution_allowed: false`.
- Continue from the proof to the public Evidence Pack documentation.
- Keep the boundary explicit: no live SAP connection, SAP credentials, production evidence, or execution authority is involved.

## Verify

Run the [golden quickstart](GOLDEN-QUICKSTART-0.4.0-alpha.3.md). Release assets include a reproducible wheel, a deterministic `git archive` source snapshot, and `SHA256SUMS` built from the proven tag.

## Compatibility and non-goals

- Practical Evidence Pack and CLI contracts remain Alpha-2 compatible; this is still a prerelease.
- The proof fixture and expected output are synthetic and do not establish production suitability or SAP certification.
- SAO-Bench remains separately versioned as `0.3-dev`; the reference self-test is not external-runtime performance.
- No live SAP connector, production write automation, execution authority, or package-registry publication is included.
