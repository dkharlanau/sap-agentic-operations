#!/usr/bin/env python3
"""Build, parse, and validate Enterprise-as-Code artifact references."""

from __future__ import annotations

import argparse
import json
import re
from dataclasses import asdict, dataclass
from urllib.parse import parse_qs, quote, unquote, urlencode, urlsplit


TOKEN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


@dataclass(frozen=True)
class ArtifactRef:
    owner: str
    repository: str
    kind: str
    local_id: str
    version: str | None = None

    @property
    def uri(self) -> str:
        path = "/".join(
            [
                quote(self.repository, safe="._-"),
                quote(self.kind, safe="._-"),
                *[quote(part, safe="._-:@") for part in self.local_id.split("/")],
            ]
        )
        query = urlencode({"version": self.version}) if self.version else ""
        return f"eac://{quote(self.owner, safe='._-')}/{path}" + (f"?{query}" if query else "")


def _check_token(name: str, value: str) -> None:
    if not value or not TOKEN.fullmatch(value):
        raise ValueError(f"{name} must match {TOKEN.pattern}: {value!r}")


def build(owner: str, repository: str, kind: str, local_id: str, version: str | None = None) -> ArtifactRef:
    _check_token("owner", owner)
    _check_token("repository", repository)
    _check_token("kind", kind)
    local_id = local_id.strip("/")
    if not local_id:
        raise ValueError("local_id must not be empty")
    if any(not segment for segment in local_id.split("/")):
        raise ValueError("local_id must not contain empty path segments")
    if version is not None and not str(version).strip():
        raise ValueError("version must not be blank")
    return ArtifactRef(owner, repository, kind, local_id, str(version) if version is not None else None)


def parse(uri: str) -> ArtifactRef:
    parts = urlsplit(uri)
    if parts.scheme != "eac":
        raise ValueError(f"scheme must be 'eac', got {parts.scheme!r}")
    if not parts.netloc:
        raise ValueError("artifact reference must include an owner")
    owner = unquote(parts.netloc)
    segments = [unquote(segment) for segment in parts.path.split("/") if segment]
    if len(segments) < 3:
        raise ValueError("artifact reference path must include repository/kind/local-id")
    repository, kind = segments[0], segments[1]
    local_id = "/".join(segments[2:])
    query = parse_qs(parts.query, keep_blank_values=True)
    unsupported = sorted(set(query) - {"version"})
    if unsupported:
        raise ValueError(f"unsupported query parameter(s): {unsupported}")
    versions = query.get("version", [])
    if len(versions) > 1:
        raise ValueError("version may be provided at most once")
    version = versions[0] if versions else None
    return build(owner, repository, kind, local_id, version)


def normalize(uri: str) -> str:
    return parse(uri).uri


def validate(uri: str) -> dict[str, object]:
    try:
        ref = parse(uri)
    except ValueError as exc:
        return {"valid": False, "input": uri, "error": str(exc)}
    return {"valid": True, "input": uri, "canonical": ref.uri, "reference": asdict(ref)}


def main() -> int:
    parser = argparse.ArgumentParser(description="Enterprise-as-Code artifact reference helper")
    sub = parser.add_subparsers(dest="command", required=True)

    build_cmd = sub.add_parser("build")
    build_cmd.add_argument("owner")
    build_cmd.add_argument("repository")
    build_cmd.add_argument("kind")
    build_cmd.add_argument("local_id")
    build_cmd.add_argument("--version")

    parse_cmd = sub.add_parser("parse")
    parse_cmd.add_argument("uri")

    validate_cmd = sub.add_parser("validate")
    validate_cmd.add_argument("uri")

    args = parser.parse_args()
    if args.command == "build":
        ref = build(args.owner, args.repository, args.kind, args.local_id, args.version)
        print(ref.uri)
        return 0
    if args.command == "parse":
        ref = parse(args.uri)
        print(json.dumps({"uri": ref.uri, **asdict(ref)}, indent=2))
        return 0
    result = validate(args.uri)
    print(json.dumps(result, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
