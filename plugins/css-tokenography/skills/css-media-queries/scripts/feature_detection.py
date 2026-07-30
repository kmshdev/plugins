#!/usr/bin/env python3
"""Analyze browser-collected feature support without using user-agent tables."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any


PROTOCOL = "css-tokenography-feature-detection/v1"
MAX_INPUT_BYTES = 65_536
MAX_ENGINES = 16
MAX_FEATURES = 128


def read_input(path: Path | None) -> object:
    try:
        data = path.read_bytes() if path is not None else sys.stdin.buffer.read(MAX_INPUT_BYTES + 1)
    except OSError as error:
        raise ValueError(f"unable to read input: {error}") from error
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError(f"input exceeds {MAX_INPUT_BYTES} bytes")
    try:
        return json.loads(data.decode("utf-8"))
    except UnicodeDecodeError as error:
        raise ValueError(f"input must be UTF-8: {error}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"input must be valid JSON: {error}") from error


def non_empty_strings(value: object) -> list[str] | None:
    if (
        not isinstance(value, list)
        or not value
        or not all(isinstance(item, str) and item.strip() for item in value)
    ):
        return None
    return value


def analyze(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("input must be a JSON object")
    if set(value) != {"features", "engines"}:
        raise ValueError("input keys must be exactly features and engines")

    features = non_empty_strings(value["features"])
    if features is None:
        raise ValueError("features must be a non-empty array of strings")
    if len(features) > MAX_FEATURES:
        raise ValueError(f"features must contain at most {MAX_FEATURES} entries")
    if len(features) != len(set(features)):
        raise ValueError("features must not contain duplicates")

    engines = value["engines"]
    if not isinstance(engines, list) or not engines:
        raise ValueError("engines must be a non-empty array")
    if len(engines) > MAX_ENGINES:
        raise ValueError(f"engines must contain at most {MAX_ENGINES} entries")

    support_by_engine: dict[str, dict[str, bool]] = {}
    for index, engine in enumerate(engines):
        if not isinstance(engine, dict) or set(engine) != {"name", "support"}:
            raise ValueError(
                f"engines[{index}] keys must be exactly name and support"
            )
        name = engine["name"]
        support = engine["support"]
        if not isinstance(name, str) or not name.strip():
            raise ValueError(f"engines[{index}].name must be a non-empty string")
        if name in support_by_engine:
            raise ValueError(f"duplicate engine name: {name}")
        if not isinstance(support, dict) or set(support) != set(features):
            raise ValueError(
                f"engines[{index}].support must contain every declared feature exactly once"
            )
        if not all(type(result) is bool for result in support.values()):
            raise ValueError(
                f"engines[{index}].support values must be JSON booleans"
            )
        support_by_engine[name] = support

    results: list[dict[str, object]] = []
    engine_names = list(support_by_engine)
    for feature in features:
        supported = [
            name for name in engine_names if support_by_engine[name][feature]
        ]
        unsupported = [
            name for name in engine_names if not support_by_engine[name][feature]
        ]
        status = "all" if not unsupported else "none" if not supported else "partial"
        results.append(
            {
                "feature": feature,
                "status": status,
                "support": {
                    name: support_by_engine[name][feature] for name in engine_names
                },
                "supported_engines": supported,
                "unsupported_engines": unsupported,
            }
        )

    return {
        "protocol": PROTOCOL,
        "scope": "analysis-of-collected-runtime-facts",
        "engines": engine_names,
        "features": results,
        "limitations": [
            "Results describe only the supplied browser observations.",
            "The analyzer does not use user-agent strings or predict future support.",
        ],
    }


def render_human(report: dict[str, object]) -> str:
    lines = [
        f"protocol={report['protocol']}",
        f"engines={','.join(report['engines'])}",
    ]
    for feature in report["features"]:
        assert isinstance(feature, dict)
        lines.append(f"{feature['feature']}: {feature['status']}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Analyze feature support collected from real browser engines."
    )
    parser.add_argument(
        "--input",
        type=Path,
        help="JSON input file. Reads stdin when omitted.",
    )
    parser.add_argument("--format", choices=("json", "human"), default="json")
    args = parser.parse_args()

    try:
        report = analyze(read_input(args.input))
    except ValueError as error:
        print(f"feature-detection: {error}", file=sys.stderr)
        return 1

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(render_human(report))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
