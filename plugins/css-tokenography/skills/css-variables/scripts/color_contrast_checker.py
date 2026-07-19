#!/usr/bin/env python3
"""Calculate WCAG 2.2 relative-luminance contrast for one sRGB color pair."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import TextIO


PLUGIN_SCRIPTS = Path(__file__).resolve().parents[3] / "scripts"
sys.path.insert(0, str(PLUGIN_SCRIPTS))

from css_tokenography_core import EvidenceEnvelope


HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}")


class ContrastInputError(ValueError):
    pass


def read_json(path: str, stdin: TextIO) -> dict[str, object]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise ContrastInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise ContrastInputError("Input must be a JSON object")
    return value


def parse_hex(value: object, field: str) -> tuple[float, float, float]:
    if not isinstance(value, str) or HEX_COLOR.fullmatch(value) is None:
        raise ContrastInputError(f"{field} must be a six-digit hex color")
    return tuple(int(value[index : index + 2], 16) / 255 for index in (1, 3, 5))


def relative_luminance(rgb: tuple[float, float, float]) -> float:
    linear = tuple(
        channel / 12.92
        if channel <= 0.04045
        else ((channel + 0.055) / 1.055) ** 2.4
        for channel in rgb
    )
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast_ratio(
    foreground: tuple[float, float, float],
    background: tuple[float, float, float],
) -> float:
    lighter, darker = sorted(
        (relative_luminance(foreground), relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def contrast_report(foreground: object, background: object) -> dict[str, object]:
    ratio = contrast_ratio(
        parse_hex(foreground, "foreground"),
        parse_hex(background, "background"),
    )
    return {
        "method": "wcag2-relative-luminance",
        "standard": "WCAG 2.2",
        "ratio": ratio,
        "display_ratio": round(ratio, 2),
        "scope": "color-pair-thresholds-only",
        "thresholds": {
            "aa_normal_text": ratio >= 4.5,
            "aa_large_text": ratio >= 3.0,
            "aaa_normal_text": ratio >= 7.0,
            "aaa_large_text": ratio >= 4.5,
            "non_text": ratio >= 3.0,
        },
        "apca": {
            "status": "not-implemented",
            "reason": (
                "APCA is beta and polarity-sensitive; it is not implemented here "
                "and is not a WCAG 3 conformance method."
            ),
        },
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Calculate WCAG 2.2 contrast thresholds for two six-digit sRGB colors."
    )
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin (default)")
    result.add_argument("--format", choices=("json", "human"), default="human")
    result.add_argument("--evidence", action="store_true", help="Emit a JSON evidence envelope")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        data = read_json(args.input, sys.stdin)
        report = contrast_report(data.get("foreground"), data.get("background"))
    except ContrastInputError as error:
        print(f"color-contrast-checker: {error}", file=sys.stderr)
        return 1

    if args.evidence:
        print(json.dumps(EvidenceEnvelope(core=report).to_dict(), indent=2, sort_keys=True))
    elif args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"WCAG 2.2 contrast: {report['display_ratio']}:1")
        print(json.dumps(report["thresholds"], indent=2, sort_keys=True))
        print("APCA: not implemented; this is not a WCAG 3 conformance result.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
