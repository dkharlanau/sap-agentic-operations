from __future__ import annotations

import copy
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import urlparse

SCHEMA_URL = "https://dkharlanau.github.io/signal-to-insight/contracts/research-evidence-handoff.schema.json"
SCHEMA_VERSION = "1.0.0"
CANONICALIZATION = "UTF-8 JSON with lexicographically sorted object keys and compact separators"
FORBIDDEN_RAW_KEYS = {
    "transcript",
    "full_transcript",
    "raw_text",
    "full_text",
    "article_body",
    "pdf_text",
    "source_content",
}
TOP_LEVEL_FIELDS = {
    "schema",
    "schema_version",
    "packet_id",
    "producer",
    "exported_from",
    "source",
    "claims",
    "operational_boundary",
    "integrity",
}


class ResearchContextError(ValueError):
    pass


def load_packet(path: str | Path) -> dict:
    packet_path = Path(path)
    try:
        data = json.loads(packet_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise ResearchContextError(f"cannot read research evidence packet: {exc}") from exc
    if not isinstance(data, dict):
        raise ResearchContextError("research evidence packet must be a JSON object")
    return data


def canonical_bytes(payload: dict) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def payload_digest(payload: dict) -> str:
    return "sha256:" + hashlib.sha256(canonical_bytes(payload)).hexdigest()


def forbidden_keys(node: object) -> list[str]:
    found: list[str] = []
    stack = [node]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for key, value in current.items():
                if str(key).lower() in FORBIDDEN_RAW_KEYS:
                    found.append(str(key))
                stack.append(value)
        elif isinstance(current, list):
            stack.extend(current)
    return sorted(found)


def is_http_url(value: object) -> bool:
    if not isinstance(value, str):
        return False
    parsed = urlparse(value)
    return parsed.scheme in {"http", "https"} and bool(parsed.netloc)


def validate_packet(packet: object) -> list[str]:
    if not isinstance(packet, dict):
        return ["packet must be a JSON object"]
    errors: list[str] = []
    missing = sorted(TOP_LEVEL_FIELDS - set(packet))
    extra = sorted(set(packet) - TOP_LEVEL_FIELDS)
    if missing:
        errors.append("missing fields: " + ", ".join(missing))
    if extra:
        errors.append("unsupported fields: " + ", ".join(extra))
    if packet.get("schema") != SCHEMA_URL:
        errors.append("unsupported schema")
    if packet.get("schema_version") != SCHEMA_VERSION:
        errors.append("unsupported schema_version")

    packet_id = packet.get("packet_id")
    if not isinstance(packet_id, str) or not packet_id:
        errors.append("packet_id must be a non-empty string")

    exported = packet.get("exported_from")
    if not isinstance(exported, dict):
        errors.append("exported_from must be an object")
    else:
        if exported.get("status") != "published":
            errors.append("exported_from.status must be published")
        for field in ("insight_id", "title", "one_liner", "public_url", "reviewed_at"):
            if not isinstance(exported.get(field), str) or not exported.get(field):
                errors.append(f"exported_from.{field} must be a non-empty string")
        if not is_http_url(exported.get("public_url")):
            errors.append("exported_from.public_url must be an HTTP(S) URL")

    source = packet.get("source")
    if not isinstance(source, dict):
        errors.append("source must be an object")
    else:
        for field in ("id", "type", "title", "canonical_url"):
            if not isinstance(source.get(field), str) or not source.get(field):
                errors.append(f"source.{field} must be a non-empty string")
        if not is_http_url(source.get("canonical_url")):
            errors.append("source.canonical_url must be an HTTP(S) URL")

    claims = packet.get("claims")
    if not isinstance(claims, list) or not claims:
        errors.append("claims must be a non-empty list")
    else:
        claim_ids: list[str] = []
        for index, claim in enumerate(claims):
            where = f"claims[{index}]"
            if not isinstance(claim, dict):
                errors.append(f"{where} must be an object")
                continue
            claim_id = claim.get("id")
            if not isinstance(claim_id, str) or not claim_id:
                errors.append(f"{where}.id must be a non-empty string")
            else:
                claim_ids.append(claim_id)
            if not isinstance(claim.get("text"), str) or not claim.get("text"):
                errors.append(f"{where}.text must be a non-empty string")
            if claim.get("origin") not in {
                "source",
                "verification",
                "project_interpretation",
                "prior_knowledge",
            }:
                errors.append(f"{where}.origin is unsupported")
            if claim.get("status") not in {"supported", "uncertain", "unresolved"}:
                errors.append(f"{where}.status is unsupported")
            evidence = claim.get("evidence")
            if not isinstance(evidence, list):
                errors.append(f"{where}.evidence must be a list")
            else:
                for evidence_index, item in enumerate(evidence):
                    item_where = f"{where}.evidence[{evidence_index}]"
                    if not isinstance(item, dict):
                        errors.append(f"{item_where} must be an object")
                        continue
                    if not is_http_url(item.get("url")):
                        errors.append(f"{item_where}.url must be an HTTP(S) URL")
                    if not isinstance(item.get("locator"), str) or not item.get("locator"):
                        errors.append(f"{item_where}.locator must be a non-empty string")
        if len(claim_ids) != len(set(claim_ids)):
            errors.append("claim ids must be unique")

    boundary = packet.get("operational_boundary")
    if not isinstance(boundary, dict):
        errors.append("operational_boundary must be an object")
    else:
        if boundary.get("trust_level") != "external_research_context":
            errors.append("operational_boundary.trust_level must be external_research_context")
        if boundary.get("requires_human_review") is not True:
            errors.append("operational_boundary.requires_human_review must be true")
        prohibited = boundary.get("prohibited_uses")
        if not isinstance(prohibited, list):
            errors.append("operational_boundary.prohibited_uses must be a list")
        else:
            for required_use in (
                "authorization",
                "execution",
                "production incident evidence",
                "automatic policy change",
            ):
                if required_use not in prohibited:
                    errors.append(f"operational_boundary must prohibit {required_use}")

    raw = forbidden_keys(packet)
    if raw:
        errors.append("packet contains forbidden raw-source keys: " + ", ".join(raw))

    integrity = packet.get("integrity")
    if not isinstance(integrity, dict):
        errors.append("integrity must be an object")
    else:
        if integrity.get("algorithm") != "sha256":
            errors.append("integrity.algorithm must be sha256")
        if integrity.get("canonicalization") != CANONICALIZATION:
            errors.append("integrity.canonicalization is unsupported")
        unsigned = copy.deepcopy(packet)
        unsigned.pop("integrity", None)
        if integrity.get("digest") != payload_digest(unsigned):
            errors.append("integrity.digest does not match the canonical packet payload")
    return errors


def packet_summary(packet: dict) -> dict:
    errors = validate_packet(packet)
    boundary = packet.get("operational_boundary") if isinstance(packet.get("operational_boundary"), dict) else {}
    exported = packet.get("exported_from") if isinstance(packet.get("exported_from"), dict) else {}
    source = packet.get("source") if isinstance(packet.get("source"), dict) else {}
    claims = packet.get("claims") if isinstance(packet.get("claims"), list) else []
    return {
        "valid": not errors,
        "packet_id": packet.get("packet_id"),
        "insight_id": exported.get("insight_id"),
        "source_id": source.get("id"),
        "claims": len(claims),
        "trust_level": boundary.get("trust_level"),
        "requires_human_review": boundary.get("requires_human_review"),
        "execution_allowed": False,
        "errors": errors,
    }


def markdown_text(value: object) -> str:
    text = re.sub(r"\s+", " ", str(value or "")).strip()
    return text.replace("\\", "\\\\").replace("[", "\\[").replace("]", "\\]").replace("<", "&lt;").replace(">", "&gt;")


def markdown_url(value: object) -> str:
    text = str(value or "").replace("\r", "").replace("\n", "")
    return text.replace(" ", "%20").replace("(", "%28").replace(")", "%29")


def render_review(packet: dict) -> str:
    errors = validate_packet(packet)
    if errors:
        raise ResearchContextError("invalid research evidence packet: " + "; ".join(errors))
    exported = packet["exported_from"]
    source = packet["source"]
    boundary = packet["operational_boundary"]
    lines = [
        "# External research evidence review",
        "",
        "> This card is external research context. It requires human review and cannot authorize execution or represent production incident evidence.",
        "",
        f"- **Packet:** `{markdown_text(packet['packet_id'])}`",
        f"- **Insight:** [{markdown_text(exported['title'])}]({markdown_url(exported['public_url'])})",
        f"- **Source:** [{markdown_text(source['title'])}]({markdown_url(source['canonical_url'])})",
        f"- **Reviewed:** {markdown_text(exported['reviewed_at'])}",
        f"- **Integrity:** `{markdown_text(packet['integrity']['digest'])}`",
        "",
        "## Claims to review",
        "",
    ]
    for claim in packet["claims"]:
        lines.extend(
            [
                f"### {markdown_text(claim['id'])}",
                "",
                markdown_text(claim["text"]),
                "",
                f"- **Origin:** `{markdown_text(claim['origin'])}`",
                f"- **Support status:** `{markdown_text(claim['status'])}`",
            ]
        )
        if claim.get("note"):
            lines.append(f"- **Boundary note:** {markdown_text(claim['note'])}")
        for evidence in claim.get("evidence") or []:
            lines.append(
                f"- **Evidence:** [{markdown_text(evidence['locator'])}]({markdown_url(evidence['url'])})"
            )
        lines.append("")
    lines.extend(
        [
            "## Operational boundary",
            "",
            f"- **Trust level:** `{markdown_text(boundary['trust_level'])}`",
            "- **Human review required:** yes",
            "- **Execution allowed by this packet:** no",
            "- **Prohibited uses:** " + ", ".join(markdown_text(item) for item in boundary["prohibited_uses"]),
            "",
            "## Human review checklist",
            "",
            "- [ ] Confirm the source and claim scope are relevant to the current SAP or enterprise decision.",
            "- [ ] Independently verify any time-sensitive or high-impact claim before adopting a control.",
            "- [ ] Keep research context separate from observed incident evidence and system authority.",
            "- [ ] Translate an accepted idea into an explicit local control, owner and verification rule.",
            "- [ ] Do not grant capability, approval or execution rights from this packet.",
            "",
        ]
    )
    return "\n".join(lines)


def write_review(packet: dict, output: str | Path, force: bool = False) -> Path:
    target = Path(output)
    if target.exists() and not force:
        raise ResearchContextError(f"output already exists: {target}; use --force to replace it")
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(render_review(packet), encoding="utf-8")
    return target
