#!/usr/bin/env python3
"""Validate and serialize a typed linear, radial, or conic gradient."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope
from gradient_model import Gradient, InputError


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
    fixture_keys = {"subject", "input", "adapters"}
    if fixture_keys <= set(data) and set(data) <= fixture_keys | {"core"}:
        if data.get("subject") != "gradient" or not isinstance(data.get("input"), dict):
            raise InputError("Gradient evidence fixtures require subject 'gradient' and object input")
        fixture = data
        data = fixture["input"]
        assert isinstance(data, dict)
        report = Gradient.from_data(data).to_report()
        if "core" in fixture and fixture["core"] != {"value": report["value"]}:
            raise InputError("Gradient evidence fixture core must match the canonical serialized value")
        return report
    return Gradient.from_data(data).to_report()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Validate and serialize a typed linear, radial, or conic CSS gradient."
    )
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    result.add_argument("--evidence", action="store_true", help="Emit a JSON evidence envelope")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        data = read_json(args.input, sys.stdin)
        report = build_report(data)
    except InputError as error:
        print(f"gradient-mixer: {error}", file=sys.stderr)
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
        print(f"{report['kind']} gradient ({report['source_order']} stop order)")
        print(report["css"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
