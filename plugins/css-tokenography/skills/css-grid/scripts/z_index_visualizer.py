#!/usr/bin/env python3
"""Analyze stacking contexts and containing blocks from explicit JSON facts."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO

from stacking_context_model import StackingInputError, analyze_tree


def read_json(path: str, stdin: TextIO) -> dict[str, Any]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise StackingInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise StackingInputError("Input must be a JSON object")
    if "elements" not in value:
        raise StackingInputError(
            "Provide pre-collected element facts in elements; raw HTML/CSS parsing is not supported"
        )
    return value


def build_report(data: dict[str, Any]) -> dict[str, Any]:
    return analyze_tree(data.get("elements"))


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Model stacking contexts from pre-collected computed facts.")
    result.add_argument("--input", default="-", help="JSON path, or '-' for stdin")
    result.add_argument("--format", choices=("json", "human"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = build_report(read_json(args.input, sys.stdin))
    except StackingInputError as error:
        print(f"z-index-visualizer: {error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"{len(report['contexts'])} stacking contexts; root={report['root_context']}")
        print(report["warnings"][0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
