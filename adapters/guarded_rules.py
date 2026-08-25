#!/usr/bin/env python3
"""Protocol-compliant deterministic adapter used to test SAO plumbing."""

from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from baselines.generate import guarded_rules


def main() -> int:
    try:
        envelope = json.load(sys.stdin)
    except json.JSONDecodeError as exc:
        print(f"invalid protocol JSON: {exc}", file=sys.stderr)
        return 2

    if envelope.get("protocol_version") != "0.1":
        print("unsupported protocol_version", file=sys.stderr)
        return 2
    case = envelope.get("case")
    if not isinstance(case, dict) or not case.get("id"):
        print("missing case", file=sys.stderr)
        return 2
    if "expected" in case:
        print("benchmark expected answer leaked into adapter input", file=sys.stderr)
        return 2

    decision = guarded_rules(case)
    sys.stdout.write(json.dumps(decision, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
