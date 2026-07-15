#!/usr/bin/env python3
"""Scaffold the bundled docdev Astro site without deleting target files."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from pathlib import Path


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--content-dir", type=Path)
    parser.add_argument("--force", action="store_true", help="overwrite template-owned files but preserve unrelated files")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    target = args.target.expanduser().resolve()
    template = Path(__file__).resolve().parent.parent / "assets" / "astro-template"
    if not template.is_dir():
        print(f"scaffold_site: bundled Astro template is missing: {template}", file=sys.stderr)
        return 2
    if target.exists() and any(target.iterdir()) and not args.force:
        print(f"scaffold_site: target is not empty: {target}; pass --force to overwrite template-owned files", file=sys.stderr)
        return 2

    content_dir: Path | None = None
    if args.content_dir:
        content_dir = args.content_dir.expanduser().resolve()
        if not content_dir.is_dir():
            print(f"scaffold_site: content directory does not exist: {content_dir}", file=sys.stderr)
            return 2
        if not any(content_dir.rglob("*.mdx")):
            print(f"scaffold_site: content directory has no .mdx files: {content_dir}", file=sys.stderr)
            return 2

    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copytree(template, target, dirs_exist_ok=target.exists())

    if content_dir:
        relative = Path(os.path.relpath(content_dir, target)).as_posix()
        config = "export default Object.freeze({\n  contentDir: " + json.dumps(relative) + "\n});\n"
        (target / "docdev.config.mjs").write_text(config, encoding="utf-8")

    print(f"scaffolded docdev Astro site: {target}")
    print(f"content directory: {content_dir or target / 'src/content/docs'}")
    print("next: npm install && npm run check && npm run build")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
