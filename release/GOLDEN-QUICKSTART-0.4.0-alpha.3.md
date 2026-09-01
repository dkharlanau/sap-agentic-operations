# Golden quickstart — Practical Toolkit 0.4.0-alpha.3

This walkthrough installs the released package, analyzes one checked-in synthetic incident, and verifies its deterministic report. It does not use SAP credentials, connect to live SAP, or authorize a recovery action.

Requirements: Git and Python 3.11+.

```bash
git clone --branch v0.4.0-alpha.3 --depth 1 \
  https://github.com/dkharlanau/sap-agentic-operations.git
cd sap-agentic-operations
python -m venv .venv
. .venv/bin/activate
python -m pip install .

sao incident analyze examples/evidence-packs/customer-replication-missing-event \
  --output /tmp/sao-30-second-proof
```

Verify the deterministic JSON report:

```bash
python - <<'PY'
from hashlib import sha256
from pathlib import Path
import json

path = Path('/tmp/sao-30-second-proof/incident-report.json')
report = json.loads(path.read_text(encoding='utf-8'))
assert report['status'] == 'insufficient_evidence', report
assert report['classification'] == 'current_outbound_event_not_proven', report
assert report['execution_allowed'] is False, report

actual = sha256(path.read_bytes()).hexdigest()
expected = 'b2040e8ce1613d797205ff9b2b54e668513fc399049dd4345f5ab9079ca14a8d'
assert actual == expected, (actual, expected)
print(f'verified {actual}')
PY
```

A matching result proves the released synthetic rule path and byte-stable report. It does not prove correctness for an unmodeled production incident or grant execution authority.
