"""Typed ordered CSS transform-list validation and matrix composition."""

from __future__ import annotations

import math
import re
from typing import Any

from transform_matrix import clean, from_matrix2d, from_matrix3d, identity, multiply, perspective, rotate_axis, scale, skew, translate


class TransformInputError(ValueError):
    pass


LENGTH = re.compile(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))px$")
ANGLE = re.compile(r"^([+-]?(?:\d+(?:\.\d*)?|\.\d+))(deg|grad|rad|turn)$")
SAFE_TEXT = re.compile(r"^[^;{}<>\n\r]+$")


def numeric(value: Any, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(float(value)):
        raise TransformInputError(f"{field} must be a finite unitless number")
    return float(value)


def length(value: Any, field: str, *, positive: bool = False) -> float:
    if value == 0:
        result = 0.0
    elif isinstance(value, str) and (match := LENGTH.fullmatch(value.strip())):
        result = float(match.group(1))
    else:
        raise TransformInputError(f"{field} must be a px length (unitless zero is allowed)")
    if positive and result <= 0:
        raise TransformInputError(f"{field} must be greater than zero")
    return result


def angle(value: Any, field: str) -> float:
    if value == 0:
        return 0.0
    if not isinstance(value, str) or not (match := ANGLE.fullmatch(value.strip())):
        raise TransformInputError(f"{field} must be an angle with deg, grad, rad, or turn units")
    amount = float(match.group(1))
    return amount * {"deg": math.pi / 180, "grad": math.pi / 200, "rad": 1, "turn": 2 * math.pi}[match.group(2)]


def safe_text(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip() or not SAFE_TEXT.fullmatch(value.strip()) or ")" in value or "(" in value:
        raise TransformInputError(f"{field} must be a safe single CSS value")
    return value.strip()


def css_arg(value: Any) -> str:
    if isinstance(value, bool):
        raise TransformInputError("transform arguments cannot be booleans")
    if isinstance(value, (int, float)):
        return f"{value:g}"
    return safe_text(value, "transform argument")


def arity(name: str, args: list[Any], minimum: int, maximum: int | None = None) -> None:
    maximum = minimum if maximum is None else maximum
    if not minimum <= len(args) <= maximum:
        expected = str(minimum) if minimum == maximum else f"{minimum} or {maximum}"
        raise TransformInputError(f"{name}() requires {expected} arguments")


def function_matrix(name: str, args: list[Any]) -> list[list[float]]:
    field = lambda index: f"{name}.args[{index}]"
    if name == "translate":
        arity(name, args, 1, 2); return translate(length(args[0], field(0)), length(args[1], field(1)) if len(args) == 2 else 0, 0)
    if name in {"translateX", "translateY", "translateZ"}:
        arity(name, args, 1); value = length(args[0], field(0)); return translate(value if name == "translateX" else 0, value if name == "translateY" else 0, value if name == "translateZ" else 0)
    if name == "translate3d":
        arity(name, args, 3); return translate(*(length(value, field(index)) for index, value in enumerate(args)))
    if name == "scale":
        arity(name, args, 1, 2); x = numeric(args[0], field(0)); y = numeric(args[1], field(1)) if len(args) == 2 else x; return scale(x, y, 1)
    if name in {"scaleX", "scaleY", "scaleZ"}:
        arity(name, args, 1); value = numeric(args[0], field(0)); return scale(value if name == "scaleX" else 1, value if name == "scaleY" else 1, value if name == "scaleZ" else 1)
    if name == "scale3d":
        arity(name, args, 3); return scale(*(numeric(value, field(index)) for index, value in enumerate(args)))
    if name in {"rotate", "rotateX", "rotateY", "rotateZ"}:
        arity(name, args, 1); axes = {"rotate": (0, 0, 1), "rotateX": (1, 0, 0), "rotateY": (0, 1, 0), "rotateZ": (0, 0, 1)}; return rotate_axis(*axes[name], angle(args[0], field(0)))
    if name == "rotate3d":
        arity(name, args, 4); return rotate_axis(*(numeric(args[i], field(i)) for i in range(3)), angle(args[3], field(3)))
    if name == "skew":
        arity(name, args, 1, 2); return skew(angle(args[0], field(0)), angle(args[1], field(1)) if len(args) == 2 else 0)
    if name in {"skewX", "skewY"}:
        arity(name, args, 1); value = angle(args[0], field(0)); return skew(value if name == "skewX" else 0, value if name == "skewY" else 0)
    if name == "matrix":
        arity(name, args, 6); return from_matrix2d([numeric(value, field(index)) for index, value in enumerate(args)])
    if name == "matrix3d":
        arity(name, args, 16); return from_matrix3d([numeric(value, field(index)) for index, value in enumerate(args)])
    if name == "perspective":
        arity(name, args, 1); return perspective(length(args[0], field(0), positive=True))
    raise TransformInputError(f"Unsupported transform function {name!r}")


def build_transform_report(data: Any) -> dict[str, Any]:
    if not isinstance(data, dict):
        raise TransformInputError("Input must be a JSON object")
    transform = data.get("transform")
    if not isinstance(transform, dict) or transform.get("kind") not in {"none", "list"}:
        raise TransformInputError("transform.kind must be 'none' or 'list'")
    kind = transform["kind"]
    raw_functions = transform.get("functions", [])
    if kind == "none" and raw_functions:
        raise TransformInputError("transform.functions must be absent or empty when kind is 'none'")
    if kind == "list" and (not isinstance(raw_functions, list) or not raw_functions):
        raise TransformInputError("transform.functions must be a non-empty ordered array when kind is 'list'")
    ordered: list[dict[str, Any]] = []
    matrices = []
    serialized = []
    for index, raw in enumerate(raw_functions):
        if not isinstance(raw, dict) or not isinstance(raw.get("name"), str) or not isinstance(raw.get("args"), list):
            raise TransformInputError(f"transform.functions[{index}] must contain name and args")
        name, args = raw["name"], list(raw["args"])
        matrices.append(function_matrix(name, args))
        ordered.append({"name": name, "args": args})
        serialized.append(f"{name}({', '.join(css_arg(value) for value in args)})")
    composite = identity()
    for matrix in matrices:
        composite = multiply(composite, matrix)

    ancestor = data.get("ancestor", {})
    if not isinstance(ancestor, dict):
        raise TransformInputError("ancestor must be an object")
    ancestor_value = ancestor.get("perspective", "none")
    ancestor_css = ""
    has_property = ancestor_value != "none"
    if has_property:
        length(ancestor_value, "ancestor.perspective", positive=True)
        declarations = [f"perspective: {css_arg(ancestor_value)};"]
        if "perspective_origin" in ancestor:
            declarations.append(f"perspective-origin: {safe_text(ancestor['perspective_origin'], 'ancestor.perspective_origin')};")
        ancestor_css = "\n".join(declarations)
    origin_css = ""
    if "transform_origin" in data:
        origin_css = f"transform-origin: {safe_text(data['transform_origin'], 'transform_origin')};"
    transform_css = "transform: none;" if kind == "none" else f"transform: {' '.join(serialized)};"
    css = "\n".join(part for part in (ancestor_css, transform_css, origin_css) if part)
    has_function = any(item["name"] == "perspective" for item in ordered)
    mode = "both" if has_property and has_function else "ancestor-property" if has_property else "transform-function" if has_function else "none"
    creates = kind != "none"
    return {
        "css": css,
        "ancestor_css": ancestor_css,
        "transform_css": transform_css,
        "ordered_functions": ordered,
        "matrix": clean(composite),
        "matrix_order": "multiply-functions-left-to-right",
        "perspective": {"mode": mode, "ancestor_value": ancestor_value},
        "creates_stacking_context": creates,
        "creates_absolute_containing_block": creates,
        "creates_fixed_containing_block": creates,
        "compositor_layer": "browser-dependent",
        "gpu_acceleration": "not-guaranteed",
        "warnings": ["A transform, including translateZ(0), does not guarantee a GPU or compositor layer; measure the target browser."],
    }
