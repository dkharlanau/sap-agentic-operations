# Enterprise-as-Code Artifact References

Cross-repository traceability uses a logical reference that is independent from where the source file happens to live in GitHub.

## Canonical URI

```text
eac://<owner>/<repository>/<kind>/<local-id>[?version=<logical-version>]
```

Examples:

```text
eac://dkharlanau/process-as-code/process/order-to-cash/customer-create
eac://dkharlanau/mapping-as-code/mapping/customer/country?version=v3
eac://dkharlanau/interface-as-code/interface/mdg-s4/customer?version=v2
eac://dkharlanau/data-relationship-map/relationship/AFS:4711
eac://dkharlanau/reconciliation-as-code/reconciliation/customer-country/post-load
eac://dkharlanau/cutover-graph/task/wave-3/reconcile-customers
eac://dkharlanau/project-evidence-graph/evidence/release-2026-08/regression-42
```

The URI identifies a logical artifact. A GitHub URL, file path, branch, or commit is source provenance, not identity.

## Structured record

```json
{
  "ref": "eac://dkharlanau/mapping-as-code/mapping/customer/country?version=v3",
  "source": {
    "repository": "dkharlanau/mapping-as-code",
    "path": "examples/customer-country.yaml",
    "revision": "abc123",
    "url": "https://github.com/dkharlanau/mapping-as-code/blob/abc123/examples/customer-country.yaml"
  }
}
```

`ref` should remain stable while `source.revision` changes as the implementation evolves.

## Rules

1. `owner`, `repository`, and `kind` use ASCII letters, digits, `.`, `_`, and `-`.
2. `local-id` may contain several path segments and is percent-encoded canonically.
3. `version` is optional and represents a logical artifact version, not a Git branch or commit.
4. Git commit SHA, source URL, file/sheet/row provenance, and external ticket IDs belong in provenance/metadata.
5. A consumer must not rewrite a logical reference merely because a source file moved.
6. Cross-repository links should be explicit; agents may propose missing links but must not silently persist inferred traceability.

## CLI

```bash
python scripts/artifact_ref.py build dkharlanau mapping-as-code mapping customer/country --version v3
python scripts/artifact_ref.py parse 'eac://dkharlanau/mapping-as-code/mapping/customer/country?version=v3'
python scripts/artifact_ref.py validate 'eac://dkharlanau/cutover-graph/task/wave-3/reconcile-customers'
```

The structured record schema is [`../schemas/artifact-ref.schema.json`](../schemas/artifact-ref.schema.json).

## Integration pattern

Domain repositories remain responsible for their own canonical models. They only need an optional field such as `artifact_ref` or `external_refs` whose values follow this contract. `project-evidence-graph` can then connect artifacts across repositories without importing or duplicating their full domain models.
