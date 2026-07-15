#!/usr/bin/env python3
"""Validate current Windsurf/Devin Desktop workspace rule frontmatter."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


VALID_TRIGGERS = {"always_on", "model_decision", "glob", "manual"}


class RuleError(ValueError):
    pass


def parse_rule(path: Path) -> dict[str, object]:
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as error:
        raise RuleError(f"Unable to read rule: {error}") from error
    if len(text) > 12_000:
        raise RuleError("workspace rule exceeds the 12,000-character limit")
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise RuleError("workspace rule must begin with YAML frontmatter")
    try:
        closing = lines.index("---", 1)
    except ValueError as error:
        raise RuleError("workspace rule frontmatter is not closed") from error
    frontmatter: dict[str, str] = {}
    for line_number, line in enumerate(lines[1:closing], start=2):
        if not line.strip():
            continue
        if ":" not in line:
            raise RuleError(f"invalid frontmatter at line {line_number}")
        key, value = line.split(":", 1)
        key, value = key.strip(), value.strip().strip('"\'')
        if key in frontmatter:
            raise RuleError(f"duplicate frontmatter key {key!r}")
        frontmatter[key] = value
    allowed = {"trigger", "globs", "description"}
    unknown = sorted(set(frontmatter) - allowed)
    if unknown:
        raise RuleError(f"unsupported frontmatter keys: {', '.join(unknown)}")
    trigger = frontmatter.get("trigger")
    if trigger not in VALID_TRIGGERS:
        raise RuleError(f"trigger must be one of {', '.join(sorted(VALID_TRIGGERS))}")
    if trigger == "glob" and not frontmatter.get("globs"):
        raise RuleError("glob rules require a non-empty globs pattern")
    if trigger == "model_decision" and not frontmatter.get("description"):
        raise RuleError("model_decision rules require a concrete description")
    body = "\n".join(lines[closing + 1:]).strip()
    if not body:
        raise RuleError("rule body must not be empty")
    return {
        "path": str(path),
        "scope": "workspace",
        "trigger": trigger,
        "globs": frontmatter.get("globs"),
        "description": frontmatter.get("description"),
        "characters": len(text),
        "body_characters": len(body),
        "preferred_directory": ".devin/rules",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate Windsurf/Devin Desktop workspace-rule syntax and activation metadata.")
    parser.add_argument("--input", type=Path, required=True, help="Workspace rule Markdown file")
    parser.add_argument("--format", choices=("json", "human"), default="human")
    args = parser.parse_args()
    try:
        report = parse_rule(args.input)
    except RuleError as error:
        print(f"windsurf-rule: {error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"Valid workspace rule: trigger={report['trigger']} characters={report['characters']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
