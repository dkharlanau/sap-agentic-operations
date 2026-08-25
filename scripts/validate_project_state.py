#!/usr/bin/env python3
"""Validate that public SAO metadata matches executable repository state."""

from __future__ import annotations

import json
import re
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from scripts.evaluate_suite import load_suite


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    cases = load_suite(ROOT)
    pack_counts = Counter(case.get("pack", "core") for case in cases)

    try:
        manifest = json.loads((ROOT / "sao-manifest.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"invalid sao-manifest.json: {exc}", file=sys.stderr)
        return 1

    benchmark = manifest.get("benchmark") or {}
    if benchmark.get("caseCount") != len(cases):
        fail(errors, f"sao-manifest benchmark.caseCount={benchmark.get('caseCount')} but executable suite has {len(cases)}")
    declared_packs = benchmark.get("packs") or {}
    if dict(sorted(declared_packs.items())) != dict(sorted(pack_counts.items())):
        fail(errors, f"sao-manifest pack counts {declared_packs!r} do not match executable suite {dict(pack_counts)!r}")
    if benchmark.get("version") != manifest.get("version"):
        fail(errors, "sao-manifest project version and benchmark version must match during the current dev line")

    simulator = manifest.get("simulator") or {}
    if simulator.get("stateful") is not True or simulator.get("faultInjection") is not True:
        fail(errors, "sao-manifest must accurately expose stateful fault-injection simulator capability")
    if not (ROOT / "simulator" / "v03.py").exists():
        fail(errors, "manifest declares simulator but simulator/v03.py is missing")

    try:
        openapi = json.loads((ROOT / "adapters" / "http" / "openapi.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(errors, f"invalid HTTP adapter OpenAPI: {exc}")
        openapi = {}
    if openapi.get("openapi") != "3.1.0":
        fail(errors, "HTTP adapter OpenAPI must declare 3.1.0")
    try:
        protocol_const = openapi["components"]["schemas"]["AdapterEnvelope"]["properties"]["protocol_version"]["const"]
    except (KeyError, TypeError):
        protocol_const = None
    if protocol_const != "0.1":
        fail(errors, "HTTP OpenAPI protocol version must match SAO adapter protocol 0.1")
    if "/sao-decision" not in (openapi.get("paths") or {}):
        fail(errors, "HTTP OpenAPI must expose /sao-decision")

    for schema in (
        "decision.schema.json",
        "evidence.schema.json",
        "write-envelope.schema.json",
        "experiment.schema.json",
        "trace-event.schema.json",
        "assurance-case.schema.json",
    ):
        path = ROOT / "schemas" / schema
        try:
            json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as exc:
            fail(errors, f"invalid schema {schema}: {exc}")

    required_surfaces = [
        ROOT / "docs" / "CONTROL-PLANE.md",
        ROOT / "docs" / "ASSURANCE-CASE.md",
        ROOT / "traces" / "README.md",
        ROOT / "adapters" / "README.md",
        ROOT / "experiments" / "README.md",
    ]
    for path in required_surfaces:
        if not path.exists():
            fail(errors, f"required public surface missing: {path.relative_to(ROOT)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if f"SAO-Bench v{benchmark.get('version')}" not in readme:
        fail(errors, "README status does not match manifest benchmark version")
    if f"**{len(cases)} synthetic cases**" not in readme:
        fail(errors, "README case-count statement does not match executable suite")

    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cff, flags=re.MULTILINE)
    if not match or not match.group(1).startswith("0.3"):
        fail(errors, "CITATION.cff must describe the current 0.3 development line")

    if errors:
        print("SAO project-state validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(f"SAO project-state validation passed: version={benchmark.get('version')}, cases={len(cases)}, packs={dict(sorted(pack_counts.items()))}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
