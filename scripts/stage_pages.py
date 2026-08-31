#!/usr/bin/env python3
"""Stage the product page and Markdown documentation for GitHub Pages."""

from __future__ import annotations

import argparse
import re
import shutil
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
ROOT_DOCUMENTS = (
    "README.md",
    "ARCHITECTURE.md",
    "ROADMAP.md",
    "BENCHMARK_VERSIONING.md",
    "CHANGELOG.md",
    "CONTRIBUTING.md",
    "SECURITY.md",
)
RELATIVE_MARKDOWN_LINK = re.compile(
    r"(\]\((?!https?://|mailto:|#|/)[^)#?]+)\.md([#?][^)]*)?\)"
)


def title_for(path: Path, text: str) -> str:
    for line in text.splitlines():
        if line.startswith("# "):
            return line[2:].strip()
    return path.stem.replace("-", " ").replace("_", " ").title()


def add_layout(path: Path, text: str) -> str:
    if text.startswith("---\n"):
        closing = text.find("\n---\n", 4)
        if closing != -1:
            frontmatter = text[4:closing]
            if not re.search(r"^layout\s*:", frontmatter, flags=re.MULTILINE):
                text = text[:4] + "layout: default\n" + text[4:]
            return text
    title = title_for(path, text).replace('"', "'")
    return f'---\nlayout: default\ntitle: "{title}"\n---\n\n{text}'


def renderable_markdown(path: Path) -> str:
    text = path.read_text(encoding="utf-8")
    text = RELATIVE_MARKDOWN_LINK.sub(r"\1.html\2)", text)
    return add_layout(path, text)


def stage_markdown(source: Path, destination: Path) -> None:
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(renderable_markdown(source), encoding="utf-8")


def stage(output: Path) -> None:
    if output.exists():
        raise SystemExit(f"Output already exists: {output}")
    output.mkdir(parents=True)

    shutil.copyfile(REPOSITORY_ROOT / "docs" / "product.html", output / "index.html")
    shutil.copyfile(
        REPOSITORY_ROOT / "docs" / "agent-manifest.json",
        output / "agent-manifest.json",
    )

    assets = output / "assets"
    assets.mkdir()
    shutil.copyfile(
        REPOSITORY_ROOT / "docs" / "assets" / "toolkit-pages.css",
        assets / "toolkit-pages.css",
    )

    for name in ROOT_DOCUMENTS:
        source = REPOSITORY_ROOT / name
        if source.exists():
            stage_markdown(source, output / name)

    docs_root = REPOSITORY_ROOT / "docs"
    for source in sorted(docs_root.rglob("*.md")):
        stage_markdown(source, output / "docs" / source.relative_to(docs_root))

    (output / "_config.yml").write_text(
        "\n".join(
            (
                'title: "SAP Agentic Operations"',
                'description: "Evidence-first operational diagnosis and bounded agent assurance."',
                "theme: minima",
                "markdown: kramdown",
                "",
            )
        ),
        encoding="utf-8",
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    stage(args.output.resolve())
    print(f"Staged Pages source at {args.output.resolve()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
