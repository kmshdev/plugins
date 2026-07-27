#!/usr/bin/env python3
"""Validate and serialize ordered typed CSS box-shadow layers."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope
from shadow_model import BoxShadow, InputError


def read_json(path: str, stdin: TextIO) -> dict[str, object]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except UnicodeError as error:
        raise InputError("Unable to read JSON input: input is not valid UTF-8") from error
    except (OSError, json.JSONDecodeError) as error:
        raise InputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise InputError("Input must be a JSON object")
    return value


def build_report(data: dict[str, object]) -> dict[str, object]:
    return BoxShadow.from_data(data).to_report()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Validate and serialize an ordered front-to-back array of typed box-shadow layers."
    )
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    result.add_argument("--evidence", action="store_true", help="Emit a JSON evidence envelope")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = build_report(read_json(args.input, sys.stdin))
    except InputError as error:
        print(f"box-shadow-generator: {error}", file=sys.stderr)
        return 1

    if args.evidence:
        print(
            json.dumps(
                EvidenceEnvelope(core=report).to_dict(),
                indent=2,
                sort_keys=True,
                allow_nan=False,
            )
        )
    elif args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    elif args.format == "css":
        print(report["css"])
    else:
        print(f"{len(report['layers'])} shadow layers (front-to-back order preserved)")
        print(report["css"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
