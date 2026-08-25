#!/usr/bin/env python3
"""Bridge the SAO stdin/stdout protocol to a remote HTTP JSON endpoint.

Environment:
  SAO_ADAPTER_URL      Required. HTTPS endpoint; HTTP allowed only for localhost.
  SAO_ADAPTER_TOKEN    Optional bearer token.
  SAO_ADAPTER_TIMEOUT  Optional seconds, default 45.

The endpoint receives the complete SAO protocol envelope and must return one
SAO Decision JSON object.
"""

from __future__ import annotations

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request

MAX_RESPONSE_BYTES = 1_048_576


def validate_url(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    if parsed.scheme not in {"http", "https"} or not parsed.hostname:
        raise ValueError("SAO_ADAPTER_URL must be an absolute http(s) URL")
    localhost = parsed.hostname in {"localhost", "127.0.0.1", "::1"}
    if parsed.scheme != "https" and not localhost:
        raise ValueError("remote adapter URLs must use HTTPS; HTTP is allowed only for localhost")
    if parsed.username or parsed.password:
        raise ValueError("credentials must not be embedded in SAO_ADAPTER_URL")
    return value


def main() -> int:
    raw_url = os.environ.get("SAO_ADAPTER_URL")
    if not raw_url:
        print("SAO_ADAPTER_URL is required", file=sys.stderr)
        return 2
    try:
        url = validate_url(raw_url)
        timeout = float(os.environ.get("SAO_ADAPTER_TIMEOUT", "45"))
        envelope = json.load(sys.stdin)
    except (ValueError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 2

    if envelope.get("protocol_version") != "0.1":
        print("unsupported SAO protocol_version", file=sys.stderr)
        return 2
    case = envelope.get("case")
    if not isinstance(case, dict) or not case.get("id"):
        print("missing case", file=sys.stderr)
        return 2
    if "expected" in case:
        print("benchmark truth leak detected", file=sys.stderr)
        return 2

    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "SAO-Bench-Adapter/0.1",
    }
    token = os.environ.get("SAO_ADAPTER_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    request = urllib.request.Request(
        url,
        data=json.dumps(envelope).encode("utf-8"),
        headers=headers,
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            if response.status < 200 or response.status >= 300:
                print(f"adapter HTTP status {response.status}", file=sys.stderr)
                return 1
            body = response.read(MAX_RESPONSE_BYTES + 1)
            if len(body) > MAX_RESPONSE_BYTES:
                print("adapter response exceeds size limit", file=sys.stderr)
                return 1
    except (urllib.error.URLError, TimeoutError) as exc:
        print(f"adapter request failed: {exc}", file=sys.stderr)
        return 1

    try:
        decision = json.loads(body.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        print(f"adapter returned invalid JSON: {exc}", file=sys.stderr)
        return 1

    if not isinstance(decision, dict):
        print("adapter response must be a JSON object", file=sys.stderr)
        return 1
    if decision.get("id") != case["id"]:
        print("adapter response id does not match request case id", file=sys.stderr)
        return 1

    sys.stdout.write(json.dumps(decision, separators=(",", ":")))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
