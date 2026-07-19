#!/usr/bin/env python3
"""Convert six/eight-digit sRGB hex colors to unclamped OKLCH channels."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope
from color_contrast_checker import parse_hex


HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}(?:[0-9a-fA-F]{2})?")
POWERLESS_HUE_EPSILON = 0.000004


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


def parse_srgb_hex(value: object) -> tuple[str, tuple[float, float, float], float, bool]:
    if not isinstance(value, str) or HEX_COLOR.fullmatch(value) is None:
        raise InputError("hex must be a six- or eight-digit sRGB hex color")
    normalized = value.lower()
    rgb = parse_hex(normalized[:7], "hex")
    has_alpha = len(normalized) == 9
    alpha = int(normalized[7:9], 16) / 255 if has_alpha else 1.0
    return normalized, rgb, alpha, has_alpha


def srgb_to_linear(rgb: tuple[float, float, float]) -> tuple[float, float, float]:
    return tuple(
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in rgb
    )


def linear_srgb_to_oklab(
    rgb: tuple[float, float, float],
) -> tuple[float, float, float]:
    red, green, blue = rgb
    l_value = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    m_value = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    s_value = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue
    l_root, m_root, s_root = (
        math.copysign(abs(value) ** (1 / 3), value)
        for value in (l_value, m_value, s_value)
    )
    return (
        0.2104542553 * l_root + 0.7936177850 * m_root - 0.0040720468 * s_root,
        1.9779984951 * l_root - 2.4285922050 * m_root + 0.4505937099 * s_root,
        0.0259040371 * l_root + 0.7827717662 * m_root - 0.8086757660 * s_root,
    )


def oklab_to_oklch(lab: tuple[float, float, float]) -> tuple[float, float, float]:
    lightness, a_value, b_value = lab
    chroma = math.hypot(a_value, b_value)
    hue = math.degrees(math.atan2(b_value, a_value)) % 360 if chroma else 0.0
    return lightness, chroma, hue


def compact(value: float) -> str:
    return "0" if value == 0 else repr(value)


def convert(value: object) -> dict[str, object]:
    normalized, rgb, alpha, has_alpha = parse_srgb_hex(value)
    lightness, chroma, hue = oklab_to_oklch(
        linear_srgb_to_oklab(srgb_to_linear(rgb))
    )
    powerless_hue = chroma <= POWERLESS_HUE_EPSILON
    serialized_hue = "none" if powerless_hue else compact(hue)
    css = (
        f"oklch({compact(lightness * 100)}% {compact(chroma)} {serialized_hue}"
        + (f" / {compact(alpha)}" if has_alpha else "")
        + ")"
    )
    return {
        "input": normalized,
        "input_space": "srgb",
        "oklch": {"l": lightness, "c": chroma, "h": hue},
        "alpha": alpha,
        "powerless_hue": powerless_hue,
        "css": css,
        "css_semantics": {
            "powerless_hue_epsilon": POWERLESS_HUE_EPSILON,
            "powerless_hue_serialization": "none",
        },
        "scope": "color-space-conversion-only",
        "gamut": {
            "input": "in-gamut-srgb-hex",
            "output_space": "oklch-unbounded",
            "mapping": "none",
            "clamping": "none",
        },
        "rounding": {
            "numeric_channels": "unrounded-binary64",
            "css_serialization": "python-repr-round-trip-binary64",
        },
        "contrast": {
            "status": "not-evaluated",
            "reason": "Color-space conversion does not establish contrast for any rendered color pair.",
        },
        "apca": {
            "status": "not-implemented",
            "reason": "This converter makes no APCA or WCAG 3 claim.",
        },
        "standard": "https://drafts.csswg.org/css-color-4/#ok-lab",
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Convert a six- or eight-digit sRGB hex color to OKLCH."
    )
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    result.add_argument("--evidence", action="store_true", help="Emit a JSON evidence envelope")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        data = read_json(args.input, sys.stdin)
        if set(data) != {"hex"}:
            raise InputError("Input must contain exactly hex")
        report = convert(data.get("hex"))
    except InputError as error:
        print(f"oklch-color-converter: {error}", file=sys.stderr)
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
        print(f"{report['input']} -> {report['css']}")
        print("Scope: color-space conversion only; contrast and APCA are not evaluated.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
