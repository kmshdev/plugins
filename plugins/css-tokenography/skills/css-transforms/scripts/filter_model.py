"""Typed ordered filter and backdrop-filter semantic model."""

from __future__ import annotations

import math
import re
from typing import Any


class FilterInputError(ValueError):
    pass


NUMBER = re.compile(r"^[+]?(?:\d+(?:\.\d*)?|\.\d+)$")
PERCENT = re.compile(r"^([+]?(?:\d+(?:\.\d*)?|\.\d+))%$")
LENGTH = re.compile(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))px$")
ANGLE = re.compile(r"^[+-]?(?:\d+(?:\.\d*)?|\.\d+)(?:deg|grad|rad|turn)$")
LOCAL_URL = re.compile(r"^url\(#[A-Za-z_][\w-]*\)$")
COLOR = re.compile(r"^(?:#[0-9a-fA-F]{3,8}|[A-Za-z][\w-]*|(?:rgb|rgba|hsl|hsla|oklch|oklab)\([^;{}<>]+\))$")
SAFE = re.compile(r"^[^;{}<>\n\r]+$")
AMOUNT_NAMES = {"brightness", "contrast", "grayscale", "invert", "opacity", "saturate", "sepia"}
BOUNDED_NAMES = {"grayscale", "invert", "opacity", "sepia"}


def compact(value: float) -> str:
    return f"{value:g}"


def serialize(value: Any, field: str) -> str:
    if isinstance(value, bool):
        raise FilterInputError(f"{field} must not be boolean")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        return compact(float(value))
    if not isinstance(value, str) or not value.strip() or not SAFE.fullmatch(value.strip()):
        raise FilterInputError(f"{field} must be a safe single CSS value")
    return value.strip()


def amount(value: Any, field: str) -> float:
    if isinstance(value, bool):
        raise FilterInputError(f"{field} must be a non-negative number or percentage")
    if isinstance(value, (int, float)) and math.isfinite(float(value)):
        result = float(value)
    elif isinstance(value, str) and (match := PERCENT.fullmatch(value.strip())):
        result = float(match.group(1)) / 100
    elif isinstance(value, str) and NUMBER.fullmatch(value.strip()):
        result = float(value)
    else:
        raise FilterInputError(f"{field} must be a non-negative number or percentage")
    if result < 0:
        raise FilterInputError(f"{field} must not be negative")
    return result


def px_length(value: Any, field: str, *, nonnegative: bool = False) -> float:
    if value == 0:
        result = 0.0
    elif isinstance(value, str) and (match := LENGTH.fullmatch(value.strip())):
        result = float(match.group(1))
    else:
        raise FilterInputError(f"{field} must be a px length")
    if nonnegative and result < 0:
        raise FilterInputError(f"{field} must not be negative")
    return result


def split_tokens(value: str) -> list[str]:
    tokens: list[str] = []
    start = 0
    depth = 0
    for index, character in enumerate(value):
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if depth < 0:
                raise FilterInputError("drop-shadow has unmatched parentheses")
        elif character.isspace() and depth == 0:
            if start < index:
                tokens.append(value[start:index])
            start = index + 1
    if depth:
        raise FilterInputError("drop-shadow has unmatched parentheses")
    if start < len(value):
        tokens.append(value[start:])
    return tokens


def drop_shadow(value: Any, field: str) -> dict[str, Any]:
    text = serialize(value, field)
    tokens = split_tokens(text)
    lengths: list[str] = []
    color: str | None = None
    for token in tokens:
        if LENGTH.fullmatch(token) or token == "0":
            if color is not None:
                raise FilterInputError(f"{field} lengths must precede the optional color")
            lengths.append(token)
        elif COLOR.fullmatch(token) and color is None:
            color = token
        else:
            raise FilterInputError(f"{field} supports 2 or 3 px lengths and one optional bounded color")
    if len(lengths) not in {2, 3}:
        raise FilterInputError(f"{field} requires two offsets and an optional blur radius")
    px_length(lengths[0], field + ".offset_x")
    px_length(lengths[1], field + ".offset_y")
    if len(lengths) == 3:
        px_length(lengths[2], field + ".blur", nonnegative=True)
    return {"length_count": len(lengths), "color": color}


def function_semantics(name: str, value: Any, field: str) -> dict[str, Any]:
    if name == "blur":
        return {"length_px": px_length(value, field, nonnegative=True)}
    if name in AMOUNT_NAMES:
        parsed = amount(value, field)
        return {"specified_amount": parsed, "effective_amount": min(parsed, 1.0) if name in BOUNDED_NAMES else parsed}
    if name == "hue-rotate":
        text = serialize(value, field)
        if value != 0 and not ANGLE.fullmatch(text):
            raise FilterInputError(f"{field} must be an angle with deg, grad, rad, or turn units")
        return {"angle": text}
    if name == "drop-shadow":
        return drop_shadow(value, field)
    if name == "url":
        text = serialize(value, field)
        if not LOCAL_URL.fullmatch(text):
            raise FilterInputError(f"{field} supports only network-free local-fragment url(#id); external URLs are unsupported")
        return {"url_scope": "local-fragment-only"}
    raise FilterInputError(f"Unsupported filter function {name!r}")


def safe_surface_value(value: Any, field: str) -> str:
    text = serialize(value, field)
    depth = 0
    for character in text:
        depth += character == "("
        depth -= character == ")"
        if depth < 0:
            raise FilterInputError(f"{field} has unmatched parentheses")
    if depth:
        raise FilterInputError(f"{field} has unmatched parentheses")
    return text


def build_filter_report(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise FilterInputError("Input must be a JSON object")
    property_name = data.get("property")
    if property_name not in {"filter", "backdrop-filter"}:
        raise FilterInputError("property must be 'filter' or 'backdrop-filter'")
    kind = data.get("kind")
    if kind not in {"none", "list"}:
        raise FilterInputError("kind must be 'none' or 'list'")
    raw_functions = data.get("functions", [])
    if kind == "none" and raw_functions:
        raise FilterInputError("functions must be absent or empty when kind is 'none'")
    if kind == "list" and (not isinstance(raw_functions, list) or not raw_functions):
        raise FilterInputError("functions must be a non-empty ordered array when kind is 'list'")
    operations: list[dict[str, Any]] = []
    semantics: list[dict[str, Any]] = []
    serialized: list[str] = []
    for index, raw in enumerate(raw_functions):
        if not isinstance(raw, dict) or set(raw) != {"name", "value"} or not isinstance(raw.get("name"), str):
            raise FilterInputError(f"functions[{index}] must contain exactly name and value")
        name, value = raw["name"], raw["value"]
        semantics.append({"name": name, **function_semantics(name, value, f"functions[{index}].value")})
        operations.append({"name": name, "value": value})
        serialized.append(serialize(value, f"functions[{index}].value") if name == "url" else f"{name}({serialize(value, f'functions[{index}].value')})")
    declaration = f"{property_name}: none;" if kind == "none" else f"{property_name}: {' '.join(serialized)};"

    surface = data.get("surface", {})
    if not isinstance(surface, dict):
        raise FilterInputError("surface must be an object")
    declarations = [declaration]
    mapping = {"background": "background", "border": "border", "border_radius": "border-radius"}
    for key, css_name in mapping.items():
        if key in surface:
            declarations.append(f"{css_name}: {safe_surface_value(surface[key], 'surface.' + key)};")
    alpha = surface.get("background_alpha")
    if alpha is not None and (isinstance(alpha, bool) or not isinstance(alpha, (int, float)) or not 0 <= float(alpha) <= 1):
        raise FilterInputError("surface.background_alpha must be between 0 and 1")
    if property_name == "backdrop-filter":
        visibility = "browser-dependent-background-facts-missing" if alpha is None else "visible" if alpha < 1 else "not-observable-from-declared-background"
        specification = "Filter Effects Level 2 Editor's Draft"
        maturity = "exploring-no-wg-consensus-on-backdrop-root"
    else:
        visibility = "element-filter-output-browser-dependent"
        specification = "Filter Effects Module Level 1"
        maturity = "standards-track-target-browser-verification-required"
    creates = kind != "none"
    return {
        "property": property_name,
        "kind": kind,
        "css": "\n".join(declarations),
        "ordered_operations": operations,
        "semantics": semantics,
        "surface": surface,
        "specification": specification,
        "maturity": maturity,
        "creates_stacking_context": creates,
        "creates_absolute_containing_block": creates,
        "creates_fixed_containing_block": creates,
        "color_space": "sRGB",
        "visibility": visibility,
        "warnings": ["Serialization and grouping metadata do not claim browser pixel fidelity or backdrop-root consensus."],
    }
