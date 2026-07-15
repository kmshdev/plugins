#!/usr/bin/env python3
"""Create a docdev MDX document from a bundled template."""

from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path


DOCUMENT_TYPES = ("development", "plan", "architecture", "library")
TEMPLATE_NAMES = {"plan": "plan.mdx", **{name: f"{name}.mdx" for name in DOCUMENT_TYPES if name != "plan"}}


def slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    if not slug:
        raise ValueError("title or --slug must contain an ASCII letter or digit")
    return slug


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("document_type", choices=DOCUMENT_TYPES)
    parser.add_argument("output", type=Path)
    parser.add_argument("--title", required=True)
    parser.add_argument("--summary", required=True)
    parser.add_argument("--slug")
    parser.add_argument("--force", action="store_true")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    output = args.output.expanduser()
    if output.suffix.lower() != ".mdx":
        print(f"create_doc: output must end in .mdx: {output}", file=sys.stderr)
        return 2
    if output.exists() and not args.force:
        print(f"create_doc: refusing to overwrite {output}; pass --force to replace it", file=sys.stderr)
        return 2

    template_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    template = template_dir / TEMPLATE_NAMES[args.document_type]
    if not template.is_file():
        print(f"create_doc: bundled template is missing: {template}", file=sys.stderr)
        return 2

    try:
        slug = slugify(args.slug or args.title)
    except ValueError as error:
        print(f"create_doc: {error}", file=sys.stderr)
        return 2

    title = args.title.strip()
    summary = args.summary.strip()
    if not title or not summary:
        print("create_doc: --title and --summary must not be blank", file=sys.stderr)
        return 2
    if any(character in value for value in (title, summary) for character in ("\n", "\r")):
        print("create_doc: --title and --summary must each fit on one line", file=sys.stderr)
        return 2

    replacements = {
        "{{TITLE}}": title,
        "{{SUMMARY}}": summary,
        "{{SLUG}}": slug,
        "{{DATE}}": date.today().isoformat(),
    }
    content = template.read_text(encoding="utf-8")
    for marker, value in replacements.items():
        escaped = json.dumps(value, ensure_ascii=False)[1:-1]
        content = content.replace(marker, escaped)
    unresolved = sorted(set(re.findall(r"\{\{[^}]+\}\}", content)))
    if unresolved:
        print(f"create_doc: unresolved template markers: {', '.join(unresolved)}", file=sys.stderr)
        return 2

    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(content, encoding="utf-8")
    print(f"created {args.document_type} document: {output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
