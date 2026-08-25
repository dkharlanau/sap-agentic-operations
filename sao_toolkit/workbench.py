from __future__ import annotations

import html
import json
import threading
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any

from .evidence import load_pack
from .incident import analyze_incident


def _items(values: list[str], css_class: str = "") -> str:
    if not values:
        return '<div class="empty">None</div>'
    return "".join(
        f'<div class="item {css_class}">{html.escape(str(value))}</div>' for value in values
    )


def render_workbench_html(report: dict[str, Any]) -> str:
    obj = report.get("object", {})
    authority = report.get("authority", {})
    identity = report.get("identity") or {}
    change = report.get("authoritative_change") or {}
    message = report.get("current_message") or {}
    target = report.get("target_state") or {}

    chain = [
        ("Object", f"{obj.get('type', '?')} · {obj.get('source_id', '?')}"),
        ("Authority", str(authority.get("system", "?"))),
        ("Identity", str(identity.get("target_id") or "not resolved")),
        ("Current change", str(change.get("change_id") or "not established")),
        ("Message", str(message.get("message_id") or "not established")),
        ("Target state", str(target.get("value") if target else "not verified")),
    ]
    chain_html = "".join(
        f'<div class="node"><div class="node-title">{html.escape(label)}</div>'
        f'<div class="node-value">{html.escape(value)}</div></div>'
        + ('<div class="arrow">→</div>' if index < len(chain) - 1 else '')
        for index, (label, value) in enumerate(chain)
    )

    report_json = html.escape(json.dumps(report, indent=2, sort_keys=True))
    title = html.escape(str(report.get("incident_id", "SAO incident")))
    classification = html.escape(str(report.get("classification", "unknown")))
    status = html.escape(str(report.get("status", "unknown")))
    resolution = html.escape(str(report.get("resolution_condition") or "Not defined"))

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>SAO Workbench · {title}</title>
<style>
:root {{ color-scheme: light dark; font-family: Inter, ui-sans-serif, system-ui, sans-serif; }}
body {{ margin:0; background:#f5f5f3; color:#171717; }}
main {{ max-width:1180px; margin:0 auto; padding:34px 22px 70px; }}
h1 {{ font-size:32px; margin:0 0 8px; letter-spacing:-.03em; }}
.sub {{ color:#60605b; margin-bottom:24px; }}
.badges {{ display:flex; gap:10px; flex-wrap:wrap; margin:18px 0 26px; }}
.badge {{ background:white; border:1px solid #d8d8d2; border-radius:999px; padding:8px 12px; font-family:ui-monospace,monospace; }}
.grid {{ display:grid; grid-template-columns:1fr 1fr; gap:16px; }}
.card {{ background:white; border:1px solid #deded8; border-radius:16px; padding:20px; box-shadow:0 2px 10px rgba(0,0,0,.025); }}
.card h2 {{ font-size:15px; text-transform:uppercase; letter-spacing:.08em; color:#60605b; margin:0 0 14px; }}
.item {{ padding:9px 0; border-bottom:1px solid #eeeeea; line-height:1.45; }}
.item:last-child {{ border-bottom:0; }}
.safe::before {{ content:'✓ '; font-weight:700; }}
.unsafe::before {{ content:'× '; font-weight:700; }}
.missing::before {{ content:'? '; font-weight:700; }}
.chain {{ display:flex; align-items:stretch; gap:8px; overflow:auto; padding-bottom:4px; }}
.node {{ min-width:130px; background:#fafaf7; border:1px solid #e2e2dc; border-radius:12px; padding:12px; }}
.node-title {{ font-size:11px; text-transform:uppercase; letter-spacing:.08em; color:#71716b; margin-bottom:7px; }}
.node-value {{ font-weight:650; overflow-wrap:anywhere; }}
.arrow {{ display:flex; align-items:center; font-size:20px; color:#8a8a84; }}
.resolution {{ font-size:18px; line-height:1.5; }}
details {{ margin-top:16px; }}
pre {{ white-space:pre-wrap; overflow-wrap:anywhere; font-size:12px; background:#111; color:#eee; padding:18px; border-radius:12px; }}
.empty {{ color:#8a8a84; }}
footer {{ color:#777; margin-top:24px; font-size:13px; }}
@media (max-width:760px) {{ .grid {{ grid-template-columns:1fr; }} }}
</style>
</head>
<body>
<main>
<h1>{title}</h1>
<div class="sub">SAP Agentic Operations · local evidence workbench</div>
<div class="badges">
  <div class="badge">status: {status}</div>
  <div class="badge">classification: {classification}</div>
  <div class="badge">execution: {'allowed' if report.get('execution_allowed') else 'not allowed'}</div>
</div>
<div class="card" style="margin-bottom:16px"><h2>Evidence chain</h2><div class="chain">{chain_html}</div></div>
<div class="grid">
  <section class="card"><h2>Findings</h2>{_items(report.get('findings', []))}</section>
  <section class="card"><h2>Missing evidence</h2>{_items(report.get('missing_evidence', []), 'missing')}</section>
  <section class="card"><h2>Safe next actions</h2>{_items(report.get('safe_next_actions', []), 'safe')}</section>
  <section class="card"><h2>Not justified by current evidence</h2>{_items(report.get('unsafe_actions', []), 'unsafe')}</section>
</div>
<section class="card" style="margin-top:16px"><h2>Resolution condition</h2><div class="resolution">{resolution}</div></section>
<details><summary>Raw deterministic report</summary><pre>{report_json}</pre></details>
<footer>Read-only local view. SAO does not execute SAP changes and does not upload this Evidence Pack.</footer>
</main>
</body>
</html>"""


def write_workbench(pack_path: str | Path, output: str | Path) -> Path:
    report = analyze_incident(load_pack(pack_path))
    target = Path(output)
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_workbench_html(report), encoding="utf-8")
    return target


def serve_workbench(
    pack_path: str | Path,
    *,
    host: str = "127.0.0.1",
    port: int = 8765,
    open_browser: bool = True,
) -> None:
    report = analyze_incident(load_pack(pack_path))
    page = render_workbench_html(report).encode("utf-8")
    raw_json = (json.dumps(report, indent=2, sort_keys=True) + "\n").encode("utf-8")

    class Handler(BaseHTTPRequestHandler):
        def do_GET(self) -> None:  # noqa: N802
            if self.path in {"/", "/index.html"}:
                payload, content_type = page, "text/html; charset=utf-8"
            elif self.path == "/report.json":
                payload, content_type = raw_json, "application/json; charset=utf-8"
            else:
                self.send_error(404)
                return
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = ThreadingHTTPServer((host, port), Handler)
    url = f"http://{host}:{port}/"
    print(f"SAO Workbench: {url}")
    print("Press Ctrl+C to stop.")
    if open_browser:
        threading.Timer(0.25, lambda: webbrowser.open(url)).start()
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
