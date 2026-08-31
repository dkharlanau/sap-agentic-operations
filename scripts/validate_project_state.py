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


def normalized_pep440(version: str) -> str:
    """Map the human alpha spelling used in docs to the compact PEP 440 package spelling."""
    return version.replace("-alpha.", "a")


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
    practical = manifest.get("practicalToolkit") or {}

    if benchmark.get("caseCount") != len(cases):
        fail(errors, f"sao-manifest benchmark.caseCount={benchmark.get('caseCount')} but executable suite has {len(cases)}")
    declared_packs = benchmark.get("packs") or {}
    if dict(sorted(declared_packs.items())) != dict(sorted(pack_counts.items())):
        fail(errors, f"sao-manifest pack counts {declared_packs!r} do not match executable suite {dict(pack_counts)!r}")

    # The practical toolkit and benchmark are independently versioned surfaces.
    if not practical.get("version"):
        fail(errors, "sao-manifest practicalToolkit.version is required")
    if benchmark.get("version") != manifest.get("version"):
        fail(errors, "top-level sao-manifest version must continue to identify the current assurance/benchmark development line")

    try:
        pyproject = (ROOT / "pyproject.toml").read_text(encoding="utf-8")
        package_version_match = re.search(r'^version\s*=\s*"([^"]+)"\s*$', pyproject, flags=re.MULTILINE)
        package_version = package_version_match.group(1) if package_version_match else None
    except OSError as exc:
        package_version = None
        fail(errors, f"cannot read pyproject.toml: {exc}")
    expected_package_version = normalized_pep440(str(practical.get("version", "")))
    if package_version != expected_package_version:
        fail(errors, f"pyproject version {package_version!r} does not match practical toolkit {expected_package_version!r}")

    try:
        init_text = (ROOT / "sao_toolkit" / "__init__.py").read_text(encoding="utf-8")
        init_match = re.search(r'^__version__\s*=\s*"([^"]+)"\s*$', init_text, flags=re.MULTILINE)
        init_version = init_match.group(1) if init_match else None
    except OSError as exc:
        init_version = None
        fail(errors, f"cannot read practical toolkit package version: {exc}")
    if init_version != expected_package_version:
        fail(errors, f"sao_toolkit.__version__ {init_version!r} does not match practical toolkit {expected_package_version!r}")

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
        "evidence-pack.schema.json",
        "reconciliation-pack.schema.json",
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
        ROOT / "docs" / "EVIDENCE-PACK.md",
        ROOT / "docs" / "QUICKCHECK.md",
        ROOT / "docs" / "RECONCILIATION.md",
        ROOT / "docs" / "RESEARCH-EVIDENCE-HANDOFF.md",
        ROOT / "docs" / "CONTROL-PLANE.md",
        ROOT / "docs" / "ASSURANCE-CASE.md",
        ROOT / "traces" / "README.md",
        ROOT / "adapters" / "README.md",
        ROOT / "experiments" / "README.md",
        ROOT / "sao_toolkit" / "cli.py",
        ROOT / "sao_toolkit" / "research_context.py",
        ROOT / "examples" / "research-evidence" / "sti-enterprise-agents.json",
        ROOT / ".github" / "workflows" / "product.yml",
    ]
    for path in required_surfaces:
        if not path.exists():
            fail(errors, f"required public surface missing: {path.relative_to(ROOT)}")

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    practical_version = str(practical.get("version", ""))
    benchmark_version = str(benchmark.get("version", ""))
    if practical_version not in readme:
        fail(errors, "README practical-toolkit version does not match manifest")
    if benchmark_version not in readme:
        fail(errors, "README benchmark version does not match manifest")
    if "SAO-Bench" not in readme or not re.search(rf'\b{len(cases)}\b', readme):
        fail(errors, "README must expose the executable SAO-Bench case count")

    cff = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    match = re.search(r'^version:\s*"?([^"\n]+)"?\s*$', cff, flags=re.MULTILINE)
    if not match or not match.group(1).startswith("0.3"):
        fail(errors, "CITATION.cff must describe the current 0.3 assurance/benchmark development line")

    if errors:
        print("SAO project-state validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
        return 1

    print(
        "SAO project-state validation passed: "
        f"practical={practical_version}, benchmark={benchmark_version}, "
        f"cases={len(cases)}, packs={dict(sorted(pack_counts.items()))}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
