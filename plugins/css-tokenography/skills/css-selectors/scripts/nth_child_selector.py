#!/usr/bin/env python3
"""Generate a safe :nth-child() selector from CSS An+B input."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TextIO

from selector_tokens import SelectorSyntaxError, tokenize_selector


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope


class InputError(ValueError):
    pass


CSS_WS = r"[ \t\r\n\f]"
ANB_RE = re.compile(
    rf"^{CSS_WS}*(?:(?P<keyword>odd|even)|(?P<integer>[+-]?[0-9]+)|"
    rf"(?P<a>[+-]?(?:[0-9]+)?)n(?:{CSS_WS}*(?P<b_sign>[+-])"
    rf"{CSS_WS}*(?P<b_digits>[0-9]+))?){CSS_WS}*$",
    re.IGNORECASE,
)


def read_json(path: str, stdin: TextIO) -> dict[str, object]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise InputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise InputError("Input must be a JSON object")
    return value


def _canonical_expression(a_value: int, b_value: int) -> str:
    if a_value == 0:
        return str(b_value)
    if a_value == 1:
        expression = "n"
    elif a_value == -1:
        expression = "-n"
    else:
        expression = f"{a_value}n"
    if b_value > 0:
        return f"{expression}+{b_value}"
    if b_value < 0:
        return f"{expression}{b_value}"
    return expression


def parse_an_plus_b(value: str) -> dict[str, object]:
    """Parse CSS Syntax Level 3 An+B without collapsing token boundaries."""

    if not isinstance(value, str):
        raise InputError("expression must be a string")
    match = ANB_RE.fullmatch(value)
    if match is None:
        raise InputError("expression must be odd, even, an integer, or An+B")

    keyword = match.group("keyword")
    try:
        if keyword is not None:
            a_value, b_value = (2, 1) if keyword.lower() == "odd" else (2, 0)
        elif match.group("integer") is not None:
            a_value, b_value = 0, int(match.group("integer"))
        else:
            coefficient = match.group("a")
            if coefficient in (None, "", "+"):
                a_value = 1
            elif coefficient == "-":
                a_value = -1
            else:
                a_value = int(coefficient)
            digits = match.group("b_digits")
            b_value = 0 if digits is None else int(digits)
            if match.group("b_sign") == "-":
                b_value = -b_value
    except ValueError as error:
        raise InputError("expression contains an integer that is too large") from error

    return {
        "a": a_value,
        "b": b_value,
        "expression": _canonical_expression(a_value, b_value),
    }


def _element_token(value: object) -> str:
    if not isinstance(value, str):
        raise InputError("element must be a single CSS type or universal selector token")
    element = value.strip(" \t\r\n\f")
    if not element:
        raise InputError("element must be a single CSS type or universal selector token")
    try:
        tokens = tokenize_selector(element)
    except SelectorSyntaxError as error:
        raise InputError(f"element must be a valid selector token: {error}") from error
    if len(tokens) != 1 or tokens[0].kind not in {"IDENT", "STAR"}:
        raise InputError("element must be a single CSS type or universal selector token")
    return element


def build_report(data: dict[str, object]) -> dict[str, object]:
    expression_input = data.get("expression")
    if not isinstance(expression_input, str):
        raise InputError("expression must be a string")
    parsed = parse_an_plus_b(expression_input)
    element = _element_token(data.get("element", "li"))
    expression = str(parsed["expression"])
    selector = f"{element}:nth-child({expression})"
    return {
        "coefficients": {"a": parsed["a"], "b": parsed["b"]},
        "expression": expression,
        "selector": selector,
        "css": f"{selector} {{\n  /* styles */\n}}",
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Generate a safe :nth-child() selector from a CSS An+B expression."
    )
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin (default)")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    result.add_argument("--evidence", action="store_true", help="Emit a JSON evidence envelope")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        data = read_json(args.input, sys.stdin)
        report = build_report(data)
    except InputError as error:
        print(f"nth-child-selector: {error}", file=sys.stderr)
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
        coefficients = report["coefficients"]
        print(
            f"{report['selector']} (a={coefficients['a']}, b={coefficients['b']})\n"
            f"{report['css']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
