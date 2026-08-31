from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .batch import analyze_batch, write_batch_outputs
from .demo import create_demo_pack, scenario_names
from .evidence import EvidencePackError, create_empty_pack, load_pack, pack_summary
from .incident import analyze_incident
from .normalize import NormalizeError, create_we02_like_demo, normalize_csv
from .quickcheck import analyze_quickcheck, create_quickcheck_demo, write_quickcheck_outputs
from .reconciliation import analyze_reconciliation, create_reconciliation_demo, write_reconciliation_outputs
from .reporting import write_incident_outputs
from .research_context import ResearchContextError, load_packet, packet_summary, write_review
from .workbench import serve_workbench, write_workbench


def cmd_demo(args: argparse.Namespace) -> int:
    if args.list:
        for name in scenario_names(): print(name)
        return 0
    try:
        root = create_demo_pack(args.output, scenario=args.scenario, force=args.force)
        report = analyze_incident(load_pack(root))
    except (ValueError, EvidencePackError) as exc:
        print(str(exc), file=sys.stderr); return 2
    json_path, md_path = write_incident_outputs(report, root / "sao-output")
    print("SAO practical demo created and analyzed")
    print(f"scenario: {args.scenario}\npack:     {root}\nresult:   {report['classification']}\nreport:   {md_path}\njson:     {json_path}")
    return 0


def cmd_init(args: argparse.Namespace) -> int:
    try:
        root = create_empty_pack(args.output, incident_id=args.incident_id, kind=args.kind, object_type=args.object_type, source_id=args.source_id, target_id=args.target_id, authority_system=args.authority_system, attribute=args.attribute, force=args.force)
    except EvidencePackError as exc:
        print(str(exc), file=sys.stderr); return 2
    print(f"Evidence Pack template created: {root}\nFill the CSV files, then run:\n  sao incident validate {root}\n  sao incident analyze {root}")
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try: pack = load_pack(args.pack)
    except EvidencePackError as exc:
        print(f"invalid Evidence Pack: {exc}", file=sys.stderr); return 2
    summary = pack_summary(pack)
    if args.json: print(json.dumps(summary, indent=2, sort_keys=True))
    else:
        print(f"Evidence Pack OK: {summary['incident_id']}")
        for table, count in summary["rows"].items(): print(f"  {table}: {count} row(s)")
    return 0


def cmd_analyze(args: argparse.Namespace) -> int:
    try: pack = load_pack(args.pack)
    except EvidencePackError as exc:
        print(f"invalid Evidence Pack: {exc}", file=sys.stderr); return 2
    report = analyze_incident(pack); output = Path(args.output or (Path(args.pack) / "sao-output")); json_path, md_path = write_incident_outputs(report, output)
    if args.json: print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SAO incident: {report['incident_id']}\nstatus: {report['status']}\nclassification: {report['classification']}")
        for finding in report.get("findings", []): print(f"  - {finding}")
        print(f"report: {md_path}\njson:   {json_path}")
    return 0


def cmd_batch(args: argparse.Namespace) -> int:
    report = analyze_batch(args.root); outputs = write_batch_outputs(report, args.output)
    if args.json: print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SAO batch triage: {report['incidents']} incident(s)\nresolved: {report['resolved']}\nneed attention: {report['needs_attention']}")
        for classification, count in report["by_classification"].items(): print(f"  {classification}: {count}")
        print(f"csv:      {outputs['csv']}\nmarkdown: {outputs['markdown']}\njson:     {outputs['json']}")
    return 0


def cmd_quickcheck_demo(args: argparse.Namespace) -> int:
    try:
        source = create_quickcheck_demo(args.output, force=args.force); report = analyze_quickcheck(source)
    except EvidencePackError as exc:
        print(f"quick-check error: {exc}", file=sys.stderr); return 2
    outputs = write_quickcheck_outputs(report, args.report_output)
    print(f"SAO Quick Check demo: {source}\nrows: {report['rows']}; resolved: {report['resolved']}; attention: {report['needs_attention']}\nreport: {outputs['markdown']}")
    return 0


def cmd_quickcheck_analyze(args: argparse.Namespace) -> int:
    try: report = analyze_quickcheck(args.input)
    except EvidencePackError as exc:
        print(f"quick-check error: {exc}", file=sys.stderr); return 2
    outputs = write_quickcheck_outputs(report, args.output)
    if args.json: print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SAO Quick Check: {report['rows']} row(s); resolved: {report['resolved']}; attention: {report['needs_attention']}")
        for classification, count in report["by_classification"].items(): print(f"  {classification}: {count}")
        print(f"csv: {outputs['csv']}\nmarkdown: {outputs['markdown']}\njson: {outputs['json']}")
    return 0


def cmd_reconcile_demo(args: argparse.Namespace) -> int:
    try: root = create_reconciliation_demo(args.output, force=args.force); report = analyze_reconciliation(root)
    except EvidencePackError as exc:
        print(f"reconciliation error: {exc}", file=sys.stderr); return 2
    outputs = write_reconciliation_outputs(report, root / "sao-output")
    print(f"SAO semantic reconciliation demo created\npack: {root}\nchecks: {report['checks']}; aligned: {report['aligned']}; attention: {report['needs_attention']}")
    for classification, count in report["by_classification"].items(): print(f"  {classification}: {count}")
    print(f"report: {outputs['markdown']}"); return 0


def cmd_reconcile_analyze(args: argparse.Namespace) -> int:
    try: report = analyze_reconciliation(args.pack)
    except EvidencePackError as exc:
        print(f"reconciliation error: {exc}", file=sys.stderr); return 2
    output = Path(args.output or (Path(args.pack) / "sao-output")); outputs = write_reconciliation_outputs(report, output)
    if args.json: print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"SAO reconciliation: {report['reconciliation_id']}\nchecks: {report['checks']}; aligned: {report['aligned']}; attention: {report['needs_attention']}")
        for classification, count in report["by_classification"].items(): print(f"  {classification}: {count}")
        print(f"csv: {outputs['csv']}\nmarkdown: {outputs['markdown']}\njson: {outputs['json']}")
    return 0


def cmd_normalize_demo(args: argparse.Namespace) -> int:
    try:
        root = create_we02_like_demo(args.output, force=args.force); result = normalize_csv(table="messages", input_path=root / "we02_export.csv", mapping_path=root / "messages.mapping.json", output_path=root / "messages.csv")
    except NormalizeError as exc:
        print(f"normalization error: {exc}", file=sys.stderr); return 2
    print(f"SAO normalization demo created\ninput: {root / 'we02_export.csv'}\nmap: {root / 'messages.mapping.json'}\noutput: {root / 'messages.csv'}\nrows: {result['rows']}"); return 0


def cmd_normalize_csv(args: argparse.Namespace) -> int:
    try: result = normalize_csv(table=args.table, input_path=args.input, mapping_path=args.mapping, output_path=args.output, delimiter=args.delimiter)
    except NormalizeError as exc:
        print(f"normalization error: {exc}", file=sys.stderr); return 2
    if args.json: print(json.dumps(result, indent=2, sort_keys=True))
    else: print(f"normalized {result['rows']} row(s) -> {result['output']}")
    return 0


def cmd_workbench(args: argparse.Namespace) -> int:
    try:
        if args.output:
            target = write_workbench(args.pack, args.output); print(f"SAO Workbench HTML: {target.resolve()}"); return 0
        serve_workbench(args.pack, host=args.host, port=args.port, open_browser=not args.no_open); return 0
    except (EvidencePackError, OSError) as exc:
        print(f"workbench error: {exc}", file=sys.stderr); return 2


def cmd_research_validate(args: argparse.Namespace) -> int:
    try:
        packet = load_packet(args.packet)
    except ResearchContextError as exc:
        print(f"research evidence error: {exc}", file=sys.stderr); return 2
    summary = packet_summary(packet)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2, sort_keys=True))
    elif summary["valid"]:
        print(f"Research evidence packet OK: {summary['packet_id']}")
        print(f"claims: {summary['claims']}")
        print("trust: external_research_context; human review required; execution allowed: no")
    else:
        print("Research evidence packet invalid", file=sys.stderr)
        for error in summary["errors"]:
            print(f"- {error}", file=sys.stderr)
    return 0 if summary["valid"] else 2


def cmd_research_review(args: argparse.Namespace) -> int:
    try:
        packet = load_packet(args.packet)
        target = write_review(packet, args.output, force=args.force)
    except ResearchContextError as exc:
        print(f"research evidence error: {exc}", file=sys.stderr); return 2
    print(f"External research review card: {target}")
    print("boundary: human review required; authorization and execution prohibited")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="sao", description="Evidence-first toolkit for SAP-heavy enterprise operations")
    sub = parser.add_subparsers(dest="command", required=True)

    p = sub.add_parser("demo", help="create and analyze a ready-to-run SAP operations scenario"); p.add_argument("--scenario", default="missing-current-event", choices=scenario_names()); p.add_argument("--output", default="sao-demo"); p.add_argument("--force", action="store_true"); p.add_argument("--list", action="store_true"); p.set_defaults(func=cmd_demo)
    incident = sub.add_parser("incident", help="create, validate or analyze an Evidence Pack"); incident_sub = incident.add_subparsers(dest="incident_command", required=True)
    p = incident_sub.add_parser("init"); p.add_argument("output"); p.add_argument("--incident-id", required=True); p.add_argument("--kind", default="integration-incident"); p.add_argument("--object-type", default="business-object"); p.add_argument("--source-id", default="SOURCE-ID"); p.add_argument("--target-id", default="TARGET-ID"); p.add_argument("--authority-system", default="AUTHORITATIVE-SYSTEM"); p.add_argument("--attribute", default="attribute"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_init)
    p = incident_sub.add_parser("validate"); p.add_argument("pack"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_validate)
    p = incident_sub.add_parser("analyze"); p.add_argument("pack"); p.add_argument("--output"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_analyze)

    p = sub.add_parser("batch", help="triage a directory containing multiple Evidence Packs"); p.add_argument("root"); p.add_argument("--output", default="sao-batch-output"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_batch)

    quick = sub.add_parser("quickcheck", help="run the incident engine directly over one wide CSV/Excel-style export"); quick_sub = quick.add_subparsers(dest="quick_command", required=True)
    p = quick_sub.add_parser("demo"); p.add_argument("--output", default="sao-quickcheck.csv"); p.add_argument("--report-output", default="sao-quickcheck-output"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_quickcheck_demo)
    p = quick_sub.add_parser("analyze"); p.add_argument("input"); p.add_argument("--output", default="sao-quickcheck-output"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_quickcheck_analyze)

    reconcile = sub.add_parser("reconcile", help="semantic master-data reconciliation using identity, authority and freshness"); reconcile_sub = reconcile.add_subparsers(dest="reconcile_command", required=True)
    p = reconcile_sub.add_parser("demo"); p.add_argument("--output", default="sao-reconcile-demo"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_reconcile_demo)
    p = reconcile_sub.add_parser("analyze"); p.add_argument("pack"); p.add_argument("--output"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_reconcile_analyze)

    normalize = sub.add_parser("normalize", help="map arbitrary SAP/Excel CSV columns into canonical SAO evidence tables"); normalize_sub = normalize.add_subparsers(dest="normalize_command", required=True)
    p = normalize_sub.add_parser("demo"); p.add_argument("--output", default="sao-normalize-demo"); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_normalize_demo)
    p = normalize_sub.add_parser("csv"); p.add_argument("--table", required=True, choices=["source_changes", "messages", "target_state", "identity_map"]); p.add_argument("--input", required=True); p.add_argument("--mapping", required=True); p.add_argument("--output", required=True); p.add_argument("--delimiter", default=","); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_normalize_csv)

    p = sub.add_parser("workbench", help="view an Evidence Pack as a local read-only incident workbench"); p.add_argument("pack"); p.add_argument("--host", default="127.0.0.1"); p.add_argument("--port", type=int, default=8765); p.add_argument("--no-open", action="store_true"); p.add_argument("--output"); p.set_defaults(func=cmd_workbench)

    research = sub.add_parser("research", help="validate external research context or render a bounded human review card"); research_sub = research.add_subparsers(dest="research_command", required=True)
    p = research_sub.add_parser("validate"); p.add_argument("packet"); p.add_argument("--json", action="store_true"); p.set_defaults(func=cmd_research_validate)
    p = research_sub.add_parser("review"); p.add_argument("packet"); p.add_argument("--output", required=True); p.add_argument("--force", action="store_true"); p.set_defaults(func=cmd_research_review)
    return parser


def main() -> int:
    args = build_parser().parse_args(); return int(args.func(args))


if __name__ == "__main__": raise SystemExit(main())
