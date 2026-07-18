#!/usr/bin/env python3
"""Calculate per-member CSS selector specificity using a bounded parser."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import TextIO

from selector_ast import SelectorResult, fold_specificity, parse_selector_list
from selector_tokens import SelectorSyntaxError, tokenize_selector


class SpecificityInputError(ValueError):
    pass


def read_json(path: str, stdin: TextIO) -> dict[str, object]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise SpecificityInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise SpecificityInputError("Input must be a JSON object")
    return value


def calculate_selector_list(source: str) -> list[SelectorResult]:
    if not isinstance(source, str) or not source.strip():
        raise SpecificityInputError("selector must be a non-empty string")
    tokens = tokenize_selector(source)
    selectors = parse_selector_list(tokens)
    return [fold_specificity(selector) for selector in selectors]


def build_report(data: dict[str, object]) -> dict[str, object]:
    selector = data.get("selector")
    if not isinstance(selector, str) or not selector.strip():
        raise SpecificityInputError("selector must be a non-empty string")
    results = calculate_selector_list(selector)
    return {
        "selector": selector,
        "selectors": [
            {
                "selector": result.selector,
                "specificity": result.specificity.as_list(),
                "span": {"start": result.start, "end": result.end},
                "notes": list(result.notes),
            }
            for result in results
        ],
        "standard": "Selectors Level 4",
        "inline_style": "outside-selector-specificity",
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Calculate Selectors Level 4 specificity for each selector-list member."
    )
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin (default)")
    result.add_argument("--format", choices=("json", "human"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        report = build_report(read_json(args.input, sys.stdin))
    except (SpecificityInputError, SelectorSyntaxError) as error:
        print(f"specificity-calculator: {error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        for member in report["selectors"]:
            specificity = "-".join(str(value) for value in member["specificity"])
            print(f"{member['selector']}: {specificity}")
        print("Inline styles are outside selector specificity.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
