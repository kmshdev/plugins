#!/usr/bin/env python3
"""Deterministic semantic models for design.dev developer tools."""

from __future__ import annotations

import argparse
import json
import math
import re
import sys
from pathlib import Path
from typing import Any, Callable, TextIO


class ToolInputError(ValueError):
    pass


def read_json(path: str, stdin: TextIO) -> dict[str, Any]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise ToolInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise ToolInputError("Input must be a JSON object")
    return value


def number(data: dict[str, Any], key: str) -> float:
    value = data.get(key)
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise ToolInputError(f"{key} must be numeric")
    return float(value)


def css_value(value: Any, key: str) -> str:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return f"{value:g}"
    if not isinstance(value, str) or not value.strip() or re.search(r"[;{}<>\n\r]", value):
        raise ToolInputError(f"{key} must be a single safe CSS value")
    return value.strip()


def compact(value: float) -> str:
    return f"{value:.6f}".rstrip("0").rstrip(".")


def clamp_generator(data: dict[str, Any]) -> dict[str, Any]:
    minimum = number(data, "min_px")
    maximum = number(data, "max_px")
    min_viewport = number(data, "min_viewport_px")
    max_viewport = number(data, "max_viewport_px")
    root = number(data, "root_px") if "root_px" in data else 16.0
    if minimum >= maximum or min_viewport >= max_viewport or root <= 0:
        raise ToolInputError("Require min_px < max_px, min_viewport_px < max_viewport_px, and root_px > 0")
    slope = (maximum - minimum) / (max_viewport - min_viewport)
    intercept = minimum - slope * min_viewport
    css = f"clamp({compact(minimum / root)}rem, {compact(intercept / root)}rem + {compact(slope * 100)}vw, {compact(maximum / root)}rem)"
    return {"css": css, "slope_vw": slope * 100, "intercept_rem": intercept / root}


def px_to_rem(data: dict[str, Any]) -> dict[str, Any]:
    pixels = number(data, "px")
    root = number(data, "root_px") if "root_px" in data else 16.0
    if root <= 0:
        raise ToolInputError("root_px must be greater than zero")
    rem = pixels / root
    return {"px": pixels, "root_px": root, "rem": rem, "css": f"{compact(rem)}rem"}


def transform(data: dict[str, Any]) -> dict[str, Any]:
    owner_scripts = Path(__file__).resolve().parents[1] / "skills" / "css-transforms" / "scripts"
    sys.path.insert(0, str(owner_scripts))
    try:
        from transform_model import build_transform_report
        if "transform" in data:
            return build_transform_report(data)
        fields = [
            ("translate_x", "translateX"), ("translate_y", "translateY"), ("translate_z", "translateZ"),
            ("rotate", "rotate"), ("rotate_x", "rotateX"), ("rotate_y", "rotateY"), ("rotate_z", "rotateZ"),
            ("scale", "scale"), ("scale_x", "scaleX"), ("scale_y", "scaleY"),
            ("skew_x", "skewX"), ("skew_y", "skewY"),
        ]
        functions = [{"name": name, "args": [data[key]]} for key, name in fields if key in data]
        if not functions:
            raise ToolInputError("Provide transform.kind and functions, or at least one legacy component")
        typed: dict[str, Any] = {"transform": {"kind": "list", "functions": functions}}
        if "perspective" in data:
            typed["ancestor"] = {"perspective": data["perspective"]}
        if "origin" in data:
            typed["transform_origin"] = data["origin"]
        return build_transform_report(typed)
    except (ImportError, ValueError) as error:
        raise ToolInputError(str(error)) from error


def cubic_bezier(data: dict[str, Any]) -> dict[str, Any]:
    values = [number(data, key) for key in ("x1", "y1", "x2", "y2")]
    for key, value in (("x1", values[0]), ("x2", values[2])):
        if not 0 <= value <= 1:
            raise ToolInputError(f"{key} must be between 0 and 1 for a CSS cubic-bezier timing function")
    css = "cubic-bezier(" + ", ".join(compact(value) for value in values) + ")"
    return {"css": css, "control_points": values}


def specificity(data: dict[str, Any]) -> dict[str, Any]:
    selector = data.get("selector")
    if not isinstance(selector, str) or not selector.strip():
        raise ToolInputError("selector must be a non-empty string")
    try:
        selector_scripts = Path(__file__).resolve().parents[1] / "skills" / "css-selectors" / "scripts"
        if str(selector_scripts) not in sys.path:
            sys.path.insert(0, str(selector_scripts))
        from specificity_calculator import calculate_selector_list
    except ImportError as error:
        raise ToolInputError(
            "Run the canonical css-selectors/scripts/specificity_calculator.py CLI"
        ) from error
    results = calculate_selector_list(selector)
    members = [
        {
            "selector": result.selector,
            "specificity": result.specificity.as_list(),
            "span": {"start": result.start, "end": result.end},
            "notes": list(result.notes),
        }
        for result in results
    ]
    score = members[0]["specificity"]
    return {
        "selector": selector,
        "specificity": score,
        "display": "-".join(str(part) for part in score),
        "selectors": members,
    }


def nth_child(data: dict[str, Any]) -> dict[str, Any]:
    expression = data.get("expression")
    if not isinstance(expression, str) or not re.fullmatch(r"\s*(?:odd|even|[+-]?\d+|[+-]?\d*n(?:\s*[+-]\s*\d+)?)\s*", expression, re.I):
        raise ToolInputError("expression must be odd, even, an integer, or an An+B expression")
    element = data.get("element", "li")
    element = css_value(element, "element")
    return {"selector": f"{element}:nth-child({expression.strip()})", "css": f"{element}:nth-child({expression.strip()}) {{\n  /* styles */\n}}"}


def parse_hex(value: Any, key: str) -> tuple[float, float, float]:
    if not isinstance(value, str) or not re.fullmatch(r"#[0-9a-fA-F]{6}", value):
        raise ToolInputError(f"{key} must be a six-digit hex color")
    return tuple(int(value[index:index + 2], 16) / 255 for index in (1, 3, 5))


def luminance(rgb: tuple[float, float, float]) -> float:
    linear = [channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4 for channel in rgb]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def contrast(data: dict[str, Any]) -> dict[str, Any]:
    foreground = parse_hex(data.get("foreground"), "foreground")
    background = parse_hex(data.get("background"), "background")
    light, dark = sorted((luminance(foreground), luminance(background)), reverse=True)
    ratio = (light + 0.05) / (dark + 0.05)
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


def oklch_converter(data: dict[str, Any]) -> dict[str, Any]:
    rgb = parse_hex(data.get("hex"), "hex")
    red, green, blue = [
        channel / 12.92 if channel <= 0.04045 else ((channel + 0.055) / 1.055) ** 2.4
        for channel in rgb
    ]
    l_value = 0.4122214708 * red + 0.5363325363 * green + 0.0514459929 * blue
    m_value = 0.2119034982 * red + 0.6806995451 * green + 0.1073969566 * blue
    s_value = 0.0883024619 * red + 0.2817188376 * green + 0.6299787005 * blue
    l_root, m_root, s_root = (math.copysign(abs(value) ** (1 / 3), value) for value in (l_value, m_value, s_value))
    lightness = 0.2104542553 * l_root + 0.7936177850 * m_root - 0.0040720468 * s_root
    a_value = 1.9779984951 * l_root - 2.4285922050 * m_root + 0.4505937099 * s_root
    b_value = 0.0259040371 * l_root + 0.7827717662 * m_root - 0.8086757660 * s_root
    chroma = math.hypot(a_value, b_value)
    hue = math.degrees(math.atan2(b_value, a_value)) % 360 if chroma > 1e-12 else 0.0
    return {
        "input": data["hex"].lower(),
        "oklch": {"l": lightness, "c": chroma, "h": hue},
        "css": f"oklch({compact(lightness * 100)}% {compact(chroma)} {compact(hue)})",
    }


def aspect_ratio(data: dict[str, Any]) -> dict[str, Any]:
    width, height = number(data, "width"), number(data, "height")
    if width <= 0 or height <= 0:
        raise ToolInputError("width and height must be greater than zero")
    divisor = math.gcd(round(width), round(height)) if width.is_integer() and height.is_integer() else 1
    return {"ratio": width / height, "ratio_pair": [width / divisor, height / divisor], "css": f"aspect-ratio: {compact(width / divisor)} / {compact(height / divisor)};"}


def gradient(data: dict[str, Any]) -> dict[str, Any]:
    kind = data.get("type", "linear")
    if kind not in {"linear", "radial", "conic"}:
        raise ToolInputError("type must be linear, radial, or conic")
    stops = data.get("stops")
    if not isinstance(stops, list) or len(stops) < 2:
        raise ToolInputError("stops must contain at least two CSS color stops")
    stop_values = [css_value(stop, f"stops[{index}]") for index, stop in enumerate(stops)]
    prefix = css_value(data.get("direction", "180deg"), "direction") if kind == "linear" else css_value(data.get("shape", "circle"), "shape") if kind == "radial" else css_value(data.get("from", "from 0deg"), "from")
    value = f"{kind}-gradient({prefix}, {', '.join(stop_values)})"
    return {"value": value, "css": f"background-image: {value};"}


SIMPLE_TOOLS: dict[str, tuple[str, list[str]]] = {
    "backdrop-filter-playground": ("backdrop-filter", ["blur", "brightness", "contrast", "saturate"]),
    "border-radius-playground": ("border-radius", ["value"]),
    "box-shadow-generator": ("box-shadow", ["value"]),
    "clip-path-shapes": ("clip-path", ["value"]),
    "css-background-generator": ("background", ["value"]),
    "css-filter-effects": ("filter", ["value"]),
    "css-loaders": ("animation", ["value"]),
    "css-tooltips": ("content", ["value"]),
    "custom-cursor-generator": ("cursor", ["value"]),
    "flexbox-playground": ("display", ["direction", "wrap", "justify", "align", "gap"]),
    "hover-effect-generator": ("transform", ["value"]),
    "liquid-glass-generator": ("backdrop-filter", ["value"]),
    "metallic-effect-generator": ("background", ["value"]),
    "neumorphism": ("box-shadow", ["value"]),
    "text-shadow-generator": ("text-shadow", ["value"]),
}


def simple_tool(tool: str, data: dict[str, Any]) -> dict[str, Any]:
    primary, keys = SIMPLE_TOOLS[tool]
    if tool == "flexbox-playground":
        mapping = {"direction": "flex-direction", "wrap": "flex-wrap", "justify": "justify-content", "align": "align-items", "gap": "gap"}
        declarations = ["display: flex;"] + [f"{mapping[key]}: {css_value(data[key], key)};" for key in keys if key in data]
    elif tool == "backdrop-filter-playground":
        values = [f"{key}({css_value(data[key], key)})" for key in keys if key in data]
        if not values: raise ToolInputError(f"{tool} requires at least one filter control")
        declarations = [f"{primary}: {' '.join(values)};"]
    else:
        value = data.get("value")
        declarations = [f"{primary}: {css_value(value, 'value')};"]
    return {"css": "\n".join(declarations), "declarations": declarations}


def stacking_contexts(data: dict[str, Any]) -> dict[str, Any]:
    owner_scripts = Path(__file__).resolve().parents[1] / "skills" / "css-grid" / "scripts"
    sys.path.insert(0, str(owner_scripts))
    try:
        from z_index_visualizer import build_report
        return build_report(data)
    except (ImportError, ValueError) as error:
        raise ToolInputError(str(error)) from error


HANDLERS: dict[str, Callable[[dict[str, Any]], dict[str, Any]]] = {
    "clamp-generator": clamp_generator,
    "px-to-rem-converter": px_to_rem,
    "css-transform-playground": transform,
    "cubic-bezier-studio": cubic_bezier,
    "specificity-calculator": specificity,
    "nth-child-selector": nth_child,
    "color-contrast-checker": contrast,
    "oklch-color-converter": oklch_converter,
    "aspect-ratio-calculator": aspect_ratio,
    "gradient-mixer": gradient,
    "z-index-visualizer": stacking_contexts,
}


def run_tool(tool: str, data: dict[str, Any]) -> dict[str, Any]:
    if tool in HANDLERS:
        result = HANDLERS[tool](data)
    elif tool in SIMPLE_TOOLS:
        result = simple_tool(tool, data)
    else:
        raise ToolInputError(f"Unsupported deterministic tool {tool!r}")
    return {"tool": tool, "model": "deterministic-core", **result}


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Run a deterministic semantic model for a design.dev CSS developer tool.")
    result.add_argument("--tool", required=True, choices=sorted([*HANDLERS, *SIMPLE_TOOLS]))
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin (default)")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = run_tool(args.tool, read_json(args.input, sys.stdin))
    except ToolInputError as error:
        print(f"design-tool: {error}", file=sys.stderr)
        return 1
    if args.format == "json": print(json.dumps(result, indent=2, sort_keys=True))
    elif args.format == "css": print(result.get("css", json.dumps(result, sort_keys=True)))
    else:
        print(f"{args.tool}: deterministic core model")
        print(result.get("css", json.dumps(result, indent=2, sort_keys=True)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
