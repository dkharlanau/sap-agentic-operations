# Practical Toolkit 0.4.0-alpha.1 — release checklist

## Product integrity

- [x] package version is `0.4.0a1`
- [x] installed `sao` command exists
- [x] zero runtime dependencies
- [x] nine demo incident scenarios
- [x] Evidence Pack init / validate / analyze
- [x] one-CSV Quick Check
- [x] batch triage
- [x] local Workbench HTML
- [x] semantic reconciliation
- [x] configurable CSV normalization
- [x] machine-readable Evidence Pack/reconciliation schemas
- [x] privacy-safe field report template
- [x] dedicated practical-toolkit CI
- [x] release notes in `release/PRODUCT-0.4.0-alpha.1.md`

## GitHub prerelease verification

- [x] `SAO practical toolkit` is green on the release commit
- [x] full assurance/release gates were green before publication
- [x] GitHub tag `v0.4.0-alpha.1` was created by the release workflow
- [x] GitHub Release `SAO Practical Toolkit 0.4.0-alpha.1` is published as **pre-release**
- [x] release body uses `release/PRODUCT-0.4.0-alpha.1.md`

Release URL:

`https://github.com/dkharlanau/sap-agentic-operations/releases/tag/v0.4.0-alpha.1`

## After publishing — active field-validation gate

Do not start another major framework layer immediately.

Collect:

- [ ] first external install
- [ ] three practitioner field reports
- [ ] one incorrect/incomplete SAO conclusion
- [ ] one real export-layout mapping
- [ ] one diagnostic rule improved from field evidence

Tracked in issue #21: **Alpha 1 field validation: three external SAP practitioner runs**.

The alpha is successful if it reveals where the product model is wrong, not only if users agree with it.
