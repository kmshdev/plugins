"""Finite-number models and CLI support for deterministic CSS numeric tools."""

from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path
from typing import Callable, TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope


class InputError(ValueError):
    pass


def read_json(path: str, stdin: TextIO) -> dict[str, object]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise InputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise InputError("Input must be a JSON object")
    return value


Number = int | float


def finite_number(data: dict[str, object], key: str) -> Number:
    value = data.get(key)
    if (
        isinstance(value, bool)
        or not isinstance(value, (int, float))
        or (isinstance(value, float) and not math.isfinite(value))
    ):
        raise InputError(f"{key} must be a finite number")
    return value


def _finite_value(value: object, key: str) -> Number:
    return finite_number({key: value}, key)


def compact(value: int | float) -> str:
    if value == 0:
        return "0"
    if isinstance(value, int) or value.is_integer():
        return str(int(value))
    return repr(value)


def build_clamp(
    min_px: Number,
    max_px: Number,
    min_viewport_px: Number,
    max_viewport_px: Number,
    root_px: Number,
) -> dict[str, object]:
    minimum = _finite_value(min_px, "min_px")
    maximum = _finite_value(max_px, "max_px")
    min_viewport = _finite_value(min_viewport_px, "min_viewport_px")
    max_viewport = _finite_value(max_viewport_px, "max_viewport_px")
    root = _finite_value(root_px, "root_px")
    if minimum >= maximum:
        raise InputError("min_px < max_px is required")
    if min_viewport >= max_viewport:
        raise InputError("min_viewport_px < max_viewport_px is required")
    if root <= 0:
        raise InputError("root_px must be greater than zero")

    slope = (maximum - minimum) / (max_viewport - min_viewport)
    intercept = minimum - slope * min_viewport
    minimum_rem = minimum / root
    maximum_rem = maximum / root
    slope_vw = slope * 100
    intercept_rem = intercept / root
    if not all(
        math.isfinite(value)
        for value in (minimum_rem, maximum_rem, slope_vw, intercept_rem)
    ):
        raise InputError("clamp calculation must produce finite values")
    css = (
        f"clamp({compact(minimum_rem)}rem, "
        f"{compact(intercept_rem)}rem + {compact(slope_vw)}vw, "
        f"{compact(maximum_rem)}rem)"
    )
    return {
        "css": css,
        "slope_vw": slope_vw,
        "intercept_rem": intercept_rem,
    }


def reduce_ratio(width: Number, height: Number) -> dict[str, object]:
    normalized_width = _finite_value(width, "width")
    normalized_height = _finite_value(height, "height")
    if normalized_width <= 0 or normalized_height <= 0:
        raise InputError("width and height must be greater than zero")

    if isinstance(normalized_width, int) and isinstance(normalized_height, int):
        divisor = math.gcd(normalized_width, normalized_height)
        pair: list[int | float] | None = [
            normalized_width // divisor,
            normalized_height // divisor,
        ]
    else:
        pair = None

    if pair is not None and pair[1] == 1:
        ratio: int | float = pair[0]
    else:
        try:
            ratio = normalized_width / normalized_height
        except OverflowError as error:
            raise InputError("aspect-ratio calculation must produce finite values") from error
        if not math.isfinite(ratio):
            raise InputError("aspect-ratio calculation must produce finite values")
    if pair is None:
        pair = [ratio, 1]

    return {
        "ratio": ratio,
        "pair": pair,
        "css": f"aspect-ratio: {compact(pair[0])} / {compact(pair[1])};",
    }


def px_to_rem(px: Number, root_px: Number) -> dict[str, object]:
    pixels = _finite_value(px, "px")
    root = _finite_value(root_px, "root_px")
    if root <= 0:
        raise InputError("root_px must be greater than zero")
    rem = pixels / root
    if not math.isfinite(rem):
        raise InputError("px-to-rem conversion must produce a finite value")
    return {
        "px": pixels,
        "root_px": root,
        "rem": rem,
        "css": f"{compact(rem)}rem",
    }


Builder = Callable[[dict[str, object]], dict[str, object]]
HumanFormatter = Callable[[dict[str, object], dict[str, object]], str]


def run_cli(
    tool_name: str,
    description: str,
    builder: Builder,
    human_formatter: HumanFormatter,
    argv: list[str] | None = None,
) -> int:
    parser = argparse.ArgumentParser(description=description)
    parser.add_argument("--input", default="-", help="JSON file path, or '-' for stdin (default)")
    parser.add_argument("--format", choices=("json", "css", "human"), default="human")
    parser.add_argument("--evidence", action="store_true", help="Emit a JSON evidence envelope")
    args = parser.parse_args(argv)

    try:
        data = read_json(args.input, sys.stdin)
        report = builder(data)
    except InputError as error:
        print(f"{tool_name}: {error}", file=sys.stderr)
        return 1

    if args.evidence:
        output: object = EvidenceEnvelope(core=report).to_dict()
        print(json.dumps(output, indent=2, sort_keys=True, allow_nan=False))
    elif args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True, allow_nan=False))
    elif args.format == "css":
        print(report["css"])
    else:
        print(human_formatter(report, data))
    return 0
