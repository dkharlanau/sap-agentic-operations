from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .demo import create_demo_pack
from .evidence import EvidencePackError, load_pack, pack_summary
from .incident import analyze_incident
from .reporting import write_incident_outputs


def cmd_demo(args: argparse.Namespace) -> int:
    try:
        root = create_demo_pack(args.output, force=args.force)
        report = analyze_incident(load_pack(root))
    except (ValueError, EvidencePackError) as exc:
        print(str(exc), file=sys.stderr)
        return 2
    json_path, md_path = write_incident_outputs(report, root / "sao-output")
    print("SAO practical demo created and analyzed")
    print(f"pack:   {root}")
    print(f"result: {report['classification']}")
    print(f"report: {md_path}")
    print(f"json:   {json_path}")
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


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="sao",
        description="Evidence-first toolkit for SAP-heavy enterprise operations",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("demo", help="create and analyze a ready-to-run SAP replication example")
    p.add_argument("--output", default="sao-demo")
    p.add_argument("--force", action="store_true")
    p.set_defaults(func=cmd_demo)

    incident = sub.add_parser("incident", help="validate or analyze an Evidence Pack")
    incident_sub = incident.add_subparsers(dest="incident_command", required=True)

    p = incident_sub.add_parser("validate", help="validate Evidence Pack v0.1")
    p.add_argument("pack")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_validate)

    p = incident_sub.add_parser("analyze", help="analyze identity, causality, message and business state")
    p.add_argument("pack")
    p.add_argument("--output")
    p.add_argument("--json", action="store_true")
    p.set_defaults(func=cmd_analyze)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    return int(args.func(args))


if __name__ == "__main__":
    raise SystemExit(main())
