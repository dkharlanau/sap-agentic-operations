# Golden quickstart — Practical Toolkit 0.4.0-alpha.2

This walkthrough runs one synthetic incident and verifies its deterministic report. It does not use SAP credentials or authorize a recovery action.

Requirements: Git and Python 3.11+.

```bash
git clone --branch v0.4.0-alpha.2 --depth 1 \
  https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations
python -m venv .venv
. .venv/bin/activate
python -m pip install .

golden_dir="$(mktemp -d)"
cd "$golden_dir"
sao demo
```

Verify the deterministic JSON report:

```bash
python - <<'PY'
from hashlib import sha256
from pathlib import Path

path = Path('sao-demo/sao-output/incident-report.json')
actual = sha256(path.read_bytes()).hexdigest()
expected = '321aeab74a315ef3ffec4a7a6cdadee0ffd07efc83902f8b6c4d9ccabf0f82a0'
assert actual == expected, (actual, expected)
print(f'verified {actual}')
PY
```

The report must classify the incident as `current_outbound_event_not_proven`, return `insufficient_evidence`, and keep `execution_allowed` false. A matching result proves the released synthetic rule path, not correctness for an unmodeled production incident.
