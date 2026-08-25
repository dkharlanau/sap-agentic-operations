from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .batch import analyze_batch, write_batch_outputs
from .demo import create_demo_pack, scenario_names
from .evidence import EvidencePackError, create_empty_pack, load_pack, pack_summary
from .incident import analyze_incident
from .reconciliation import (
    analyze_reconciliation,
    create_reconciliation_demo,
    write_reconciliation_outputs,
)
from .reporting import write_incident_outputs
from .workbench import serve_workbench, write_workbench


def cmd_demo(args: argparse.Namespace) -> int:
    if args.list:
        for name in scenario_names():
            print(name)
        return 0
    try:
        root = create_demo_pack(args.output, scenario=args.scenario, force=args.force)
        report = analyze_incident(load_pack(root))
    except (ValueError, EvidencePackError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json_path, md_path = write_incident_outputs(report, root / "sao-output")
    print("SAO practical demo created and analyzed")
    print(f"scenario: {args.scenario}")
    print(f"pack:     {root}")
    print(f"result:   {report['classification']}")
    print(f"report:   {md_path}")
    print(f"json:     {json_path}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    try:
        root = create_empty_pack(
            args.output,
            incident_id=args.incident_id,
            kind=args.kind,
            object_type=args.object_type,
            source_id=args.source_id,
            target_id=args.target_id,
            authority_system=args.authority_system,
            attribute=args.attribute,
            force=args.force,
        )
    except EvidencePackError as exc:
        print(str(exc), file=sys.stderr)
        return 2
    print(f"Evidence Pack template created: {root}")
    print("Fill the CSV files, then run:")
    print(f"  sao incident validate {root}")
    print(f"  sao incident analyze {root}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        pack = load_pack(args.pack)
    except EvidencePackError as exc:
        print(f"invalid Evidence Pack: {exc}", file=sys.stderr)
        return 2
    summary = pack_summary(pack)
    if args.json:
        print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"Evidence Pack OK: {summary['incident_id']}")
        for table, count in summary["rows"].items():
            print(f"  {table}: {count} row(s)")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    try:
        pack = load_pack(args.pack)
    except EvidencePackError as exc:
        print(f"invalid Evidence Pack: {exc}", file=sys.stderr)
        return 2
    report = analyze_incident(pack)
    output = Path(args.output or (Path(args.pack) / "sao-output"))
    json_path, md_path = write_incident_outputs(report, output)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SAO incident: {report['incident_id']}")
        print(f"status: {report['status']}")
        print(f"classification: {report['classification']}")
        for finding in report.get("findings", []):
            print(f"  - {finding}")
        print(f"report: {md_path}")
        print(f"json:   {json_path}")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    report = analyze_batch(args.root)
    outputs = write_batch_outputs(report, args.output)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SAO batch triage: {report['incidents']} incident(s)")
        print(f"resolved: {report['resolved']}")
        print(f"need attention: {report['needs_attention']}")
        for classification, count in report["by_classification"].items():
            print(f"  {classification}: {count}")
        print(f"csv:      {outputs['csv']}")
        print(f"markdown: {outputs['markdown']}")
        print(f"json:     {outputs['json']}")
    return 0


def cmd_reconcile_demo(args: argparse.Namespace) -> int:
    try:
        root = create_reconciliation_demo(args.output, force=args.force)
        report = analyze_reconciliation(root)
    except EvidencePackError as exc:
        print(f"reconciliation error: {exc}", file=sys.stderr)
        return 2
    outputs = write_reconciliation_outputs(report, root / "sao-output")
    print("SAO semantic reconciliation demo created")
    print(f"pack: {root}")
    print(f"checks: {report['checks']}; aligned: {report['aligned']}; attention: {report['needs_attention']}")
    for classification, count in report["by_classification"].items():
        print(f"  {classification}: {count}")
    print(f"report: {outputs['markdown']}")
    return 0


def cmd_reconcile_analyze(args: argparse.Namespace) -> int:
    try:
        report = analyze_reconciliation(args.pack)
    except EvidencePackError as exc:
        print(f"reconciliation error: {exc}", file=sys.stderr)
        return 2
    output = Path(args.output or (Path(args.pack) / "sao-output"))
    outputs = write_reconciliation_outputs(report, output)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SAO reconciliation: {report['reconciliation_id']}")
        print(f"checks: {report['checks']}; aligned: {report['aligned']}; attention: {report['needs_attention']}")
        for classification, count in report["by_classification"].items():
            print(f"  {classification}: {count}")
        print(f"csv:      {outputs['csv']}")
        print(f"markdown: {outputs['markdown']}")
        print(f"json:     {outputs['json']}")
    return 0


def cmd_workbench(args: argparse.Namespace) -> int:
    try:
        if args.output:
            target = write_workbench(args.pack, args.output)
            print(f"SAO Workbench HTML: {target.resolve()}")
            return 0
        serve_workbench(
            args.pack,
            host=args.host,
            port=args.port,
            open_browser=not args.no_open,
        )
        return 0
    except (EvidencePackError, OSError) as exc:
        print(f"workbench error: {exc}", file=sys.stderr)
        return 2


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sao",
        description="Evidence-first toolkit for SAP-heavy enterprise operations",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("demo", help="create and analyze a ready-to-run SAP operations scenario")
    p.add_argument("--scenario", default="missing-current-event", choices=scenario_names())
    p.add_argument("--output", default="sao-demo")
    p.add_argument("--force", action="store_true")
    p.add_argument("--list", action="store_true", help="list available scenarios")
    p.set_defaults(func=cmd_demo)

    incident = sub.add_parser("incident", help="create, validate or analyze an Evidence Pack")
    incident_sub = incident.add_subparsers(dest="incident_command", required=True)

    p = incident_sub.add_parser("init", help="create an empty Evidence Pack template")
    p.add_argument("output")
    p.add_argument("--incident-id", required=True)
    p.add_argument("--kind", default="integration-incident")
    p.add_argument("--object-type", default="business-object")
    p.add_argument("--source-id", default="SOURCE-ID")
    p.add_argument("--target-id", default="TARGET-ID")
    p.add_argument("--authority-system", default="AUTHORITATIVE-SYSTEM")
    p.add_argument("--attribute", default="attribute")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_init)

    p = incident_sub.add_parser("validate", help="validate Evidence Pack v0.1")
    p.add_argument("pack")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = incident_sub.add_parser("analyze", help="analyze identity, causality, message and business state")
    p.add_argument("pack")
    p.add_argument("--output")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("batch", help="triage a directory containing multiple Evidence Packs")
    p.add_argument("root")
    p.add_argument("--output", default="sao-batch-output")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_batch)

    reconcile = sub.add_parser("reconcile", help="semantic master-data reconciliation using identity, authority and freshness")
    reconcile_sub = reconcile.add_subparsers(dest="reconcile_command", required=True)
    p = reconcile_sub.add_parser("demo", help="create and run a ready-to-use semantic reconciliation example")
    p.add_argument("--output", default="sao-reconcile-demo")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_reconcile_demo)
    p = reconcile_sub.add_parser("analyze", help="analyze a reconciliation pack")
    p.add_argument("pack")
    p.add_argument("--output")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_reconcile_analyze)

    p = sub.add_parser("workbench", help="view an Evidence Pack as a local read-only incident workbench")
    p.add_argument("pack")
    p.add_argument("--host", default="127.0.0.1")
    p.add_argument("--port", type=int, default=8765)
    p.add_argument("--no-open", action="store_true")
    p.add_argument("--output", help="write a static HTML report instead of starting a local server")
    p.set_defaults(func=cmd_workbench)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
