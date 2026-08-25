#!/usr/bin/env python3
"""Build a bounded human-readable SAO assurance review report.

The report is intentionally conservative. It summarizes evidence but never turns
an experimental benchmark result into certification or production approval.
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


def load(path: Path | None) -> dict[str, Any] | None:
    if path is None:
        return None
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return data


def pct(value: object) -> str:
    if isinstance(value, (int, float)):
        return f"{float(value):.1%}"
    return "n/a"


def failed_dimension_rows(report: dict[str, Any], field: str) -> list[tuple[str, dict[str, Any]]]:
    raw = report.get(field, {})
    if not isinstance(raw, dict):
        return []
    rows = []
    for key, value in sorted(raw.items()):
        if isinstance(value, dict) and int(value.get("failed", 0)) > 0:
            rows.append((str(key), value))
    return rows


def build_markdown(
    benchmark: dict[str, Any],
    corpus: dict[str, Any] | None,
    adapter: dict[str, Any] | None,
    trace: dict[str, Any] | None,
    experiment: dict[str, Any] | None,
) -> str:
    lines = [
        "# SAO Enterprise Assurance Review",
        "",
        "> Experimental evidence summary. This is not certification, SAP approval, security accreditation, or permission to operate a production agent.",
        "",
        "## Executive view",
        "",
        f"- Benchmark: **{benchmark.get('benchmark', 'SAO-Bench')} {benchmark.get('suite_version', 'unknown')}**",
        f"- Cases: **{benchmark.get('cases', 'unknown')}**",
        f"- Score: **{pct(benchmark.get('score'))}**",
        f"- Failed cases: **{benchmark.get('failed', 'unknown')}**",
        f"- Unsafe execution failures: **{benchmark.get('unsafe_execution_failures', 'unknown')}**",
    ]

    if experiment:
        runtime = experiment.get("runtime", {}) if isinstance(experiment.get("runtime"), dict) else {}
        model = experiment.get("model") if isinstance(experiment.get("model"), dict) else None
        lines += [
            f"- Result kind: **{experiment.get('result_kind', 'unknown')}**",
            f"- Runtime: **{runtime.get('name', 'unknown')} {runtime.get('version', '')}**".rstrip(),
        ]
        if model:
            lines.append(
                f"- Model: **{model.get('provider', 'unknown')} / {model.get('name', 'unknown')} / {model.get('version') or 'unspecified'}**"
            )
        benchmark_identity = experiment.get("benchmark", {}) if isinstance(experiment.get("benchmark"), dict) else {}
        lines.append(f"- Benchmark commit: `{benchmark_identity.get('commit', 'unknown')}`")

    lines += ["", "## What this evidence supports", ""]
    if int(benchmark.get("failed", 0)) == 0 and int(benchmark.get("unsafe_execution_failures", 0)) == 0:
        lines.append(
            "The tested implementation satisfied the deterministic SAO case expectations in this result artifact and produced no benchmark-detected unsafe execution failures."
        )
    else:
        lines.append(
            "The tested implementation has benchmark-detected control failures. These should be treated as architecture/test findings, not hidden by the aggregate score."
        )

    lines += ["", "## Failure signature", ""]
    failed_results = [item for item in benchmark.get("results", []) if isinstance(item, dict) and not item.get("passed")]
    if not failed_results:
        lines.append("No failed SAO cases are present in the benchmark report.")
    else:
        for item in failed_results:
            lines.append(
                f"- `{item.get('id')}` — pack `{item.get('pack')}`, risk `{item.get('risk_tier')}`: "
                + "; ".join(str(x) for x in item.get("failures", []))
            )

    for title, field in (
        ("Risk-tier failures", "by_risk_tier"),
        ("Threat-class failures", "by_threat"),
        ("Pack failures", "by_pack"),
    ):
        rows = failed_dimension_rows(benchmark, field)
        lines += ["", f"### {title}", ""]
        if not rows:
            lines.append("None in this report.")
        else:
            for key, values in rows:
                lines.append(
                    f"- `{key}`: {values.get('failed')} failed / {values.get('total')} total ({pct(values.get('rate'))} pass)"
                )

    lines += ["", "## Evidence completeness", ""]
    if corpus:
        gate = corpus.get("release_gate", {}) if isinstance(corpus.get("release_gate"), dict) else {}
        lines += [
            f"- Corpus structural validity: **{gate.get('structural_validity', 'unknown')}**",
            f"- Corpus case count: **{corpus.get('case_count', 'unknown')}**",
            f"- Corpus audit warnings: **{len(corpus.get('warnings', [])) if isinstance(corpus.get('warnings'), list) else 'unknown'}**",
            "- Human corpus review: **required**",
        ]
    else:
        lines.append("- Corpus audit: **not supplied**")

    if adapter:
        lines.append(
            f"- Adapter conformance: **{'pass' if adapter.get('conformant') else 'fail'}** ({adapter.get('passed', '?')}/{adapter.get('cases_checked', '?')} sampled cases)"
        )
        lines.append("- Adapter conformance scope: transport and decision structure only; not a safety result")
    else:
        lines.append("- Adapter conformance: **not supplied**")

    if trace:
        trace_failed = trace.get("failed")
        trace_passed = trace.get("passed")
        if trace_failed is not None or trace_passed is not None:
            lines.append(f"- SAO-Trace: passed={trace_passed}, failed={trace_failed}")
        else:
            lines.append("- SAO-Trace report supplied, but completeness semantics must be reviewed in the source artifact")
    else:
        lines.append("- SAO-Trace: **not supplied**; hidden unsafe intermediate actions may be unobserved")

    lines += [
        "",
        "## What this evidence does not prove",
        "",
        "- that the runtime is safe for a specific SAP production landscape;",
        "- that source-system authorization and segregation-of-duties are correctly configured;",
        "- that all model/tool actions are observable if runtime telemetry is incomplete;",
        "- that synthetic SAO cases cover every customer-specific business rule or failure mode;",
        "- that a model/runtime update preserves the same behavior without rerunning the evidence pipeline;",
        "- that a high aggregate score compensates for a high-risk failed control.",
        "",
        "## Recommended review decision",
        "",
    ]

    unsafe = int(benchmark.get("unsafe_execution_failures", 0))
    failed = int(benchmark.get("failed", 0))
    if unsafe:
        lines.append(
            "**Do not increase state-changing capability.** Resolve unsafe execution failures, rerun the exact benchmark, and review trace evidence before considering a broader capability profile."
        )
    elif failed:
        lines.append(
            "**Keep the runtime at a bounded diagnostic/recommendation capability.** Resolve failed control classes and rerun before considering additional authority."
        )
    else:
        lines.append(
            "**Benchmark evidence is clean for the tested corpus, but production authority is still not implied.** The next useful step is independent runtime evidence, trace completeness review, and landscape-specific authorization/tool validation."
        )

    lines += [
        "",
        "## Evidence references",
        "",
        "This report must be distributed together with, or point back to, the raw benchmark report and experiment manifest. A detached prose summary is not sufficient evidence.",
    ]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a human-readable SAO assurance review")
    parser.add_argument("--benchmark-report", type=Path, required=True)
    parser.add_argument("--corpus-audit", type=Path)
    parser.add_argument("--adapter-conformance", type=Path)
    parser.add_argument("--trace-report", type=Path)
    parser.add_argument("--experiment-manifest", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    try:
        benchmark = load(args.benchmark_report)
        if benchmark is None:
            raise ValueError("benchmark report is required")
        content = build_markdown(
            benchmark,
            load(args.corpus_audit),
            load(args.adapter_conformance),
            load(args.trace_report),
            load(args.experiment_manifest),
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        parser.error(str(exc))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(content, encoding="utf-8")
    print(f"wrote SAO assurance review: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
