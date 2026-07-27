#!/usr/bin/env python3
"""Validate and serialize bounded CSS Flexbox container controls."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope
from flexbox_model import Flexbox, InputError


MAX_INPUT_BYTES = 65_536
MAX_JSON_NESTING_DEPTH = 256


def validate_json_depth(raw: str) -> None:
    """Reject excessive JSON container depth without interpreting JSON syntax."""
    depth = 0
    in_string = False
    escaped = False
    for character in raw:
        if in_string:
            if escaped:
                escaped = False
            elif character == "\\":
                escaped = True
            elif character == '"':
                in_string = False
            continue
        if character == '"':
            in_string = True
        elif character in "[{":
            depth += 1
            if depth > MAX_JSON_NESTING_DEPTH:
                raise InputError(
                    "Unable to read JSON input: "
                    "JSON nesting exceeds the supported parser depth"
                )
        elif character in "]}":
            depth -= 1


def read_json(path: str, stdin: TextIO) -> dict[str, object]:
    try:
        if path == "-":
            raw = stdin.read(MAX_INPUT_BYTES + 1)
            if len(raw.encode("utf-8")) > MAX_INPUT_BYTES:
                raise InputError(
                    f"JSON input must not exceed {MAX_INPUT_BYTES} UTF-8 bytes"
                )
        else:
            with Path(path).open("rb") as input_file:
                encoded = input_file.read(MAX_INPUT_BYTES + 1)
            if len(encoded) > MAX_INPUT_BYTES:
                raise InputError(
                    f"JSON input must not exceed {MAX_INPUT_BYTES} UTF-8 bytes"
                )
            raw = encoded.decode("utf-8")
        validate_json_depth(raw)
        value = json.loads(raw)
    except RecursionError as error:
        raise InputError(
            "Unable to read JSON input: JSON nesting exceeds the supported parser depth"
        ) from error
    except UnicodeError as error:
        raise InputError("Unable to read JSON input: input is not valid UTF-8") from error
    except (OSError, ValueError) as error:
        raise InputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise InputError("Input must be a JSON object")
    return value


def build_report(data: dict[str, object]) -> dict[str, object]:
    return Flexbox.from_data(data).to_report()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Validate Flexbox direction, wrapping, alignment, gap, and optional ordered items."
        )
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
        print(f"flexbox-playground: {error}", file=sys.stderr)
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
        print(f"Main axis: {report['main_axis']}")
        print(f"Cross axis: {report['cross_axis']}")
        print(report["css"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
