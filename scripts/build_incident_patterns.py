from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from sao_toolkit.demo import create_demo_pack, scenario_names
from sao_toolkit.evidence import load_pack
from sao_toolkit.incident import analyze_incident

REGISTRY_PATH = ROOT / "data" / "incident-patterns.json"
_REQUIRED = {
    "id",
    "slug",
    "scenario",
    "title",
    "symptom",
    "search_phrases",
    "signal_establishes",
    "not_established",
    "related",
}
_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


class PatternRegistryError(ValueError):
    pass


def load_registry(path: Path = REGISTRY_PATH) -> dict[str, Any]:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise PatternRegistryError(f"cannot read incident-pattern registry {path}: {exc}") from exc
    if data.get("schema_version") != "1.0":
        raise PatternRegistryError("incident-pattern registry schema_version must be 1.0")
    patterns = data.get("patterns")
    if not isinstance(patterns, list) or not patterns:
        raise PatternRegistryError("incident-pattern registry must contain a non-empty patterns list")
    if len(patterns) > 25:
        raise PatternRegistryError("incident-pattern registry is intentionally bounded to 25 patterns")

    runnable = set(scenario_names())
    seen_ids: set[str] = set()
    seen_slugs: set[str] = set()
    seen_scenarios: set[str] = set()
    for index, pattern in enumerate(patterns):
        if not isinstance(pattern, dict):
            raise PatternRegistryError(f"pattern {index} must be an object")
        missing = _REQUIRED - set(pattern)
        if missing:
            raise PatternRegistryError(f"pattern {index} missing required fields: {sorted(missing)}")
        pattern_id = str(pattern["id"])
        slug = str(pattern["slug"])
        scenario = str(pattern["scenario"])
        if pattern_id in seen_ids:
            raise PatternRegistryError(f"duplicate pattern id: {pattern_id}")
        if slug in seen_slugs:
            raise PatternRegistryError(f"duplicate pattern slug: {slug}")
        if scenario in seen_scenarios:
            raise PatternRegistryError(f"duplicate scenario projection: {scenario}")
        if not _SLUG_RE.fullmatch(slug):
            raise PatternRegistryError(f"invalid pattern slug: {slug}")
        if scenario not in runnable:
            raise PatternRegistryError(f"pattern {pattern_id} references unknown scenario: {scenario}")
        if scenario == "resolved":
            raise PatternRegistryError("resolved is a control scenario, not an incident-pattern acquisition page")
        phrases = pattern["search_phrases"]
        if not isinstance(phrases, list) or not 1 <= len(phrases) <= 4:
            raise PatternRegistryError(f"pattern {pattern_id} must have 1-4 search_phrases")
        if not all(isinstance(value, str) and value.strip() for value in phrases):
            raise PatternRegistryError(f"pattern {pattern_id} has an invalid search phrase")
        if not isinstance(pattern["related"], list):
            raise PatternRegistryError(f"pattern {pattern_id} related must be a list")
        seen_ids.add(pattern_id)
        seen_slugs.add(slug)
        seen_scenarios.add(scenario)

    unknown_related = sorted(
        {
            str(related)
            for pattern in patterns
            for related in pattern["related"]
            if str(related) not in seen_ids
        }
    )
    if unknown_related:
        raise PatternRegistryError(f"unknown related pattern ids: {unknown_related}")
    return data


def _analyze_scenario(scenario: str) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="sao-pattern-") as tmp:
        pack_root = Path(tmp) / scenario
        create_demo_pack(pack_root, scenario=scenario)
        return analyze_incident(load_pack(pack_root))


def materialize_patterns(registry: dict[str, Any]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for pattern in registry["patterns"]:
        report = _analyze_scenario(str(pattern["scenario"]))
        records.append(
            {
                **pattern,
                "reviewed_at": registry.get("reviewed_at"),
                "evidence_scope": registry.get("scope"),
                "engine": {
                    "report_format": report.get("format"),
                    "status": report["status"],
                    "classification": report["classification"],
                    "execution_allowed": bool(report["execution_allowed"]),
                    "findings": list(report.get("findings", [])),
                    "missing_evidence": list(report.get("missing_evidence", [])),
                    "safe_next_actions": list(report.get("safe_next_actions", [])),
                    "unsafe_actions": list(report.get("unsafe_actions", [])),
                    "resolution_condition": report.get("resolution_condition"),
                },
            }
        )
    return records


def _frontmatter(*, title: str, description: str, permalink: str) -> str:
    return "\n".join(
        [
            "---",
            "layout: default",
            f"title: {json.dumps(title, ensure_ascii=False)}",
            f"description: {json.dumps(description, ensure_ascii=False)}",
            f"permalink: {permalink}",
            "---",
            "",
        ]
    )


def _list(values: list[str], *, empty: str = "None in this synthetic scenario.") -> str:
    if not values:
        return empty + "\n"
    return "".join(
        f"- `{value}`\n" if "_" in value and " " not in value else f"- {value}\n"
        for value in values
    )


def render_pattern_page(record: dict[str, Any], by_id: dict[str, dict[str, Any]]) -> str:
    engine = record["engine"]
    lines = [
        _frontmatter(
            title=record["title"],
            description=record["symptom"],
            permalink=f"/docs/incident-patterns/{record['slug']}/",
        ),
        f"# {record['title']}\n\n",
        "> **Synthetic verified pattern.** This page is generated from a checked-in SAO demo scenario and the current deterministic Incident Analyzer. It is not production evidence, an SAP Note, or official SAP guidance.\n\n",
        f"**Typical symptom:** {record['symptom']}\n\n",
        "## What this evidence establishes\n\n",
        f"{record['signal_establishes']}\n\n",
        "## What it does not establish\n\n",
        f"{record['not_established']}\n\n",
        "## Current deterministic SAO result\n\n",
        f"- Scenario: `{record['scenario']}`\n",
        f"- Status: `{engine['status']}`\n",
        f"- Classification: `{engine['classification']}`\n",
        f"- Execution allowed: `{'yes' if engine['execution_allowed'] else 'no'}`\n",
        f"- Incident report contract: `{engine['report_format']}`\n\n",
        "### Findings\n\n",
        _list(engine["findings"]),
        "\n### Evidence still missing\n\n",
        _list(engine["missing_evidence"]),
        "\n### Safe next actions\n\n",
        _list(engine["safe_next_actions"]),
        "\n### Actions not justified by current evidence\n\n",
        _list(engine["unsafe_actions"]),
        "\n## Reproduce the scenario locally\n\n",
        "```bash\n",
        f"sao demo --scenario {record['scenario']} --output /tmp/sao-{record['slug']} --force\n",
        f"sao incident analyze /tmp/sao-{record['slug']} --output /tmp/sao-{record['slug']}/reanalysis\n",
        "```\n\n",
        "The first command creates synthetic evidence and runs the same analyzer that supplies this page. The second command re-analyzes the Evidence Pack explicitly.\n\n",
        "## How practitioners may phrase this problem\n\n",
        _list(record["search_phrases"]),
        "\n## Related verified patterns\n\n",
    ]
    if record["related"]:
        for related_id in record["related"]:
            related = by_id[related_id]
            lines.append(f"- [{related['title']}](../{related['slug']}/)\n")
    else:
        lines.append("No related pattern in the current bounded cohort.\n")
    lines.extend(
        [
            "\n## Boundary and next step\n\n",
            f"Resolution condition in the current scenario: **{engine['resolution_condition']}**\n\n",
            "Use the [Evidence Pack](../../EVIDENCE-PACK.html) when you have incident-specific evidence, or [Quick Check](../../QUICKCHECK.html) for an Excel-style triage list. The broader [SAP Operations Failure Atlas](../../SAP-OPERATIONS-FAILURE-ATLAS.html) contains additional failure classes; they are not automatically promoted into searchable incident pages.\n\n",
            f"Registry review date: `{record.get('reviewed_at') or 'unknown'}`. Public cohort scope: `{record.get('evidence_scope')}`.\n",
        ]
    )
    return "".join(lines)


def render_index(records: list[dict[str, Any]]) -> str:
    lines = [
        _frontmatter(
            title="SAP Incident Pattern Library",
            description="Verified synthetic SAP incident patterns generated from SAO's deterministic demo scenarios.",
            permalink="/docs/incident-patterns/",
        ),
        "# SAP Incident Pattern Library\n\n",
        "This is a deliberately small problem-first layer over the SAO Incident Analyzer. Every listed page is generated from an existing runnable synthetic scenario; the classification, findings, missing evidence, safe actions and unsafe actions come from the current deterministic engine rather than separate troubleshooting prose.\n\n",
        "> The library is evidence-gated. It is not an SAP error-code encyclopedia and will not expand into unsupported scenarios merely for page count or search coverage.\n\n",
        "## Current verified cohort\n\n",
    ]
    for record in records:
        lines.extend(
            [
                f"### [{record['title']}](./{record['slug']}/)\n\n",
                f"{record['symptom']}\n\n",
                f"Current classification: `{record['engine']['classification']}`.\n\n",
            ]
        )
    lines.extend(
        [
            "## Product path\n\n",
            "`search symptom -> verified synthetic pattern -> evidence checklist -> SAO Quick Check / Evidence Pack -> deterministic report`\n\n",
            "Start with [Quick Check](../QUICKCHECK.html) when you already have an Excel-style incident list. Use the [Evidence Pack](../EVIDENCE-PACK.html) when causality, identity, target state and recovery boundaries need a richer incident record.\n\n",
            "## Publication rule\n\n",
            "New pages require an existing runnable SAO scenario. Broader failure classes remain in the [SAP Operations Failure Atlas](../SAP-OPERATIONS-FAILURE-ATLAS.html) until product evidence justifies a tested scenario. Practitioner field evidence is tracked separately and is not manufactured by this library.\n",
        ]
    )
    return "".join(lines)


def build_incident_pattern_pages(output_dir: Path, registry_path: Path = REGISTRY_PATH) -> list[dict[str, Any]]:
    registry = load_registry(registry_path)
    records = materialize_patterns(registry)
    output_dir.mkdir(parents=True, exist_ok=True)
    by_id = {record["id"]: record for record in records}
    (output_dir / "index.md").write_text(render_index(records), encoding="utf-8")
    for record in records:
        (output_dir / f"{record['slug']}.md").write_text(
            render_pattern_page(record, by_id), encoding="utf-8"
        )
    machine = {
        "schema_version": "1.0",
        "reviewed_at": registry.get("reviewed_at"),
        "scope": registry.get("scope"),
        "patterns": records,
    }
    (output_dir / "patterns.json").write_text(
        json.dumps(machine, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return records


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build evidence-backed public SAO incident-pattern pages.")
    parser.add_argument("--output", default="build/incident-patterns")
    parser.add_argument("--registry", default=str(REGISTRY_PATH))
    args = parser.parse_args(argv)
    output = Path(args.output).resolve()
    if output.exists():
        shutil.rmtree(output)
    try:
        records = build_incident_pattern_pages(output, Path(args.registry).resolve())
    except PatternRegistryError as exc:
        print(f"incident-pattern registry error: {exc}", file=sys.stderr)
        return 2
    print(f"built {len(records)} verified incident pattern page(s) in {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
