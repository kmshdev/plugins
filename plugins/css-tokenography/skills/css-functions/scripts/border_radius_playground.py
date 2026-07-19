#!/usr/bin/env python3
"""Validate and serialize bounded CSS border-radius shorthand input."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
GRADIENT_SCRIPTS = Path(__file__).resolve().parents[2] / "css-gradients" / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))
sys.path.insert(0, str(GRADIENT_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope
from gradient_model import InputError, LENGTH_PERCENTAGE


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


def parse_length(value: object, *, field: str) -> str:
    if not isinstance(value, str) or LENGTH_PERCENTAGE.fullmatch(value.strip()) is None:
        raise InputError(f"{field} must be a supported CSS length or percentage")
    result = value.strip()
    if result.startswith("-"):
        raise InputError(f"{field} must not be negative")
    return result


def parse_radii(value: object, *, field: str) -> tuple[str, ...]:
    if not isinstance(value, list) or not 1 <= len(value) <= 4:
        raise InputError(f"{field} must contain one to four radii")
    return tuple(parse_length(item, field=f"{field}[{index}]") for index, item in enumerate(value))


def build_report(data: dict[str, object]) -> dict[str, object]:
    if set(data) - {"horizontal", "vertical"}:
        raise InputError("Input supports only horizontal and vertical")
    horizontal = parse_radii(data.get("horizontal"), field="horizontal")
    vertical = (
        None
        if "vertical" not in data
        else parse_radii(data["vertical"], field="vertical")
    )
    value = " ".join(horizontal)
    if vertical is not None:
        value += f" / {' '.join(vertical)}"
    return {
        "horizontal": list(horizontal),
        "vertical": None if vertical is None else list(vertical),
        "value": value,
        "css": f"border-radius: {value};",
        "shape": "circular" if vertical is None else "elliptical",
        "standards": {
            "grammar": "https://drafts.csswg.org/css-backgrounds-3/#propdef-border-radius",
            "percentage_basis": "corresponding dimension of the border box",
        },
        "limitations": [
            "Only explicit primitive lengths, percentages, and unitless zero are modeled.",
            "calc(), var(), global keywords, and individual corner properties are not modeled.",
            "Serialization does not establish rendered geometry or browser pixel fidelity.",
        ],
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description=(
            "Validate one to four horizontal border radii and optional one to four "
            "vertical radii."
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
        print(f"border-radius-playground: {error}", file=sys.stderr)
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
        print(
            f"{report['shape'].capitalize()} border radius "
            f"({len(report['horizontal'])} horizontal"
            + (
                ")"
                if report["vertical"] is None
                else f", {len(report['vertical'])} vertical)"
            )
        )
        print(report["css"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
