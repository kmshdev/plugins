#!/usr/bin/env python3
"""Canonical typed CSS backdrop-filter CLI."""

from __future__ import annotations
import argparse, json, sys
from pathlib import Path
from typing import Any, TextIO
from filter_model import FilterInputError, build_filter_report

def read_json(path: str, stdin: TextIO) -> dict[str, Any]:
    try: value = json.loads(stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error: raise FilterInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict): raise FilterInputError("Input must be a JSON object")
    return value

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Validate a typed ordered CSS backdrop-filter list and surface facts.")
    parser.add_argument("--input", default="-"); parser.add_argument("--format", choices=("json", "css", "human"), default="human")
    args = parser.parse_args(argv)
    try:
        data = read_json(args.input, sys.stdin)
        if data.get("property") != "backdrop-filter": raise FilterInputError("property must be 'backdrop-filter' for this CLI")
        report = build_filter_report(data)
    except FilterInputError as error:
        print(f"backdrop-filter-playground: {error}", file=sys.stderr); return 1
    print(json.dumps(report, indent=2, sort_keys=True) if args.format == "json" else report["css"]); return 0

if __name__ == "__main__": raise SystemExit(main())
