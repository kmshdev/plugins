#!/usr/bin/env python3
"""Canonical ordered CSS transform playground CLI."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any, TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope
from transform_model import TransformInputError, build_transform_report


def read_json(path: str, stdin: TextIO) -> dict[str, Any]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise TransformInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise TransformInputError("Input must be a JSON object")
    return value


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Validate an ordered typed CSS transform list and compute its 4x4 matrix.")
    result.add_argument("--input", default="-", help="JSON path, or '-' for stdin")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    result.add_argument("--evidence", action="store_true", help="Emit a JSON evidence envelope")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = build_transform_report(read_json(args.input, sys.stdin))
    except TransformInputError as error:
        print(f"css-transform-playground: {error}", file=sys.stderr)
        return 1
    if args.evidence:
        print(json.dumps(EvidenceEnvelope(core=report).to_dict(), indent=2, sort_keys=True))
    elif args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    elif args.format == "css":
        print(report["css"])
    else:
        print(report["css"])
        print(report["warnings"][0])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
