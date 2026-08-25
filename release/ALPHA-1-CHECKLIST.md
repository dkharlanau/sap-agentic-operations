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

## Verification before publishing GitHub prerelease

- [ ] latest `SAO practical toolkit` run is green on the release commit
- [ ] latest `SAO full suite` remains green
- [ ] GitHub tag `v0.4.0-alpha.1` points to the intended release commit
- [ ] GitHub Release is marked **pre-release**
- [ ] release body uses `release/PRODUCT-0.4.0-alpha.1.md`

## After publishing

Do not start another major framework layer immediately.

Collect:

- [ ] first external install
- [ ] three practitioner field reports
- [ ] one incorrect/incomplete SAO conclusion
- [ ] one real export-layout mapping
- [ ] one diagnostic rule improved from field evidence

The alpha is successful if it reveals where the product model is wrong, not only if users agree with it.
