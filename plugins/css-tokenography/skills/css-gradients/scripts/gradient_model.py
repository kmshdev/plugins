"""Typed, source-order-preserving CSS gradient validation and serialization."""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Mapping


class InputError(ValueError):
    pass


NUMBER = r"[+-]?(?:\d+(?:\.\d*)?|\.\d+)"
ANGLE = re.compile(rf"^(?:[+-]?0(?:\.0+)?|{NUMBER}(?:deg|grad|rad|turn))$")
ANGLE_PERCENTAGE = re.compile(
    rf"^(?:[+-]?0(?:\.0+)?|{NUMBER}(?:%|deg|grad|rad|turn))$"
)
LENGTH_PERCENTAGE = re.compile(
    rf"^(?:[+-]?0(?:\.0+)?|{NUMBER}(?:%|px|em|rem|ex|ch|lh|rlh|vw|vh|vmin|vmax|cm|mm|q|in|pc|pt))$"
)
FUNCTION_COLOR = re.compile(
    r"^(?:rgb|rgba|hsl|hsla|hwb|lab|lch|oklab|oklch|color)"
    r"\([A-Za-z0-9#.,%+\-/ ]+\)$",
    re.IGNORECASE,
)
HEX_COLOR = re.compile(r"^#[0-9a-fA-F]{3,8}$")
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9-]*$")
RADIAL_SHAPES = {"circle", "ellipse"}
RADIAL_SIZES = {"closest-side", "farthest-side", "closest-corner", "farthest-corner"}
POSITION_KEYWORDS = {"left", "right", "top", "bottom", "center"}

# CSS Color named colors. Keeping the vocabulary explicit prevents arbitrary
# identifiers from being presented as validated colors.
NAMED_COLORS = set(
    """
    aliceblue antiquewhite aqua aquamarine azure beige bisque black
    blanchedalmond blue blueviolet brown burlywood cadetblue chartreuse
    chocolate coral cornflowerblue cornsilk crimson cyan darkblue darkcyan
    darkgoldenrod darkgray darkgreen darkgrey darkkhaki darkmagenta
    darkolivegreen darkorange darkorchid darkred darksalmon darkseagreen
    darkslateblue darkslategray darkslategrey darkturquoise darkviolet
    deeppink deepskyblue dimgray dimgrey dodgerblue firebrick floralwhite
    forestgreen fuchsia gainsboro ghostwhite gold goldenrod gray green
    greenyellow grey honeydew hotpink indianred indigo ivory khaki lavender
    lavenderblush lawngreen lemonchiffon lightblue lightcoral lightcyan
    lightgoldenrodyellow lightgray lightgreen lightgrey lightpink lightsalmon
    lightseagreen lightskyblue lightslategray lightslategrey lightsteelblue
    lightyellow lime limegreen linen magenta maroon mediumaquamarine
    mediumblue mediumorchid mediumpurple mediumseagreen mediumslateblue
    mediumspringgreen mediumturquoise mediumvioletred midnightblue mintcream
    mistyrose moccasin navajowhite navy oldlace olive olivedrab orange
    orangered orchid palegoldenrod palegreen paleturquoise palevioletred
    papayawhip peachpuff peru pink plum powderblue purple rebeccapurple red
    rosybrown royalblue saddlebrown salmon sandybrown seagreen seashell sienna
    silver skyblue slateblue slategray slategrey snow springgreen steelblue tan
    teal thistle tomato transparent turquoise violet wheat white whitesmoke
    yellow yellowgreen currentcolor
    """.split()
)


def _text(value: object, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{field} must be a non-empty string")
    text = value.strip()
    if any(character in text for character in ";{}<>\n\r"):
        raise InputError(f"{field} contains unsupported CSS syntax")
    return text


def validate_color(value: object, field: str) -> str:
    color = _text(value, field)
    if HEX_COLOR.fullmatch(color):
        if len(color) not in {4, 5, 7, 9}:
            raise InputError(f"{field} must be a valid CSS hex color")
        return color
    if IDENTIFIER.fullmatch(color) and color.lower() in NAMED_COLORS:
        return color
    if FUNCTION_COLOR.fullmatch(color):
        return color
    raise InputError(
        f"{field} must be a bounded CSS hex, named, or functional color"
    )


def validate_angle(value: object, field: str) -> str:
    angle = _text(value, field)
    if ANGLE.fullmatch(angle) is None:
        raise InputError(f"{field} must be an angle")
    return angle


def validate_direction(value: object, field: str) -> str:
    direction = _text(value, field)
    if ANGLE.fullmatch(direction):
        return direction
    tokens = direction.lower().split()
    if not tokens or tokens[0] != "to" or len(tokens) not in {2, 3}:
        raise InputError(f"{field} must be an angle or a 'to <side-or-corner>' direction")
    sides = tokens[1:]
    if any(side not in {"left", "right", "top", "bottom"} for side in sides):
        raise InputError(f"{field} must be an angle or a 'to <side-or-corner>' direction")
    if len(sides) == 2 and (
        set(sides) <= {"left", "right"} or set(sides) <= {"top", "bottom"}
    ):
        raise InputError(f"{field} corner must combine one horizontal and one vertical side")
    return direction


def validate_position(value: object, field: str) -> str:
    position = _text(value, field)
    tokens = position.lower().split()
    if not 1 <= len(tokens) <= 2 or any(token not in POSITION_KEYWORDS for token in tokens):
        raise InputError(f"{field} must use one or two position keywords")
    if len(tokens) == 2 and (
        set(tokens) <= {"left", "right", "center"}
        or set(tokens) <= {"top", "bottom", "center"}
    ):
        if "center" not in tokens:
            raise InputError(f"{field} must combine compatible position keywords")
    return position


def validate_stop_position(kind: str, value: object, field: str) -> str:
    position = _text(value, field)
    pattern = ANGLE_PERCENTAGE if kind == "conic" else LENGTH_PERCENTAGE
    if pattern.fullmatch(position) is None:
        expected = "an angle or percentage" if kind == "conic" else "a length or percentage"
        raise InputError(f"{kind} {field} must be {expected}")
    return position


@dataclass(frozen=True)
class ColorStop:
    color: str
    position: str | None

    def serialize(self) -> str:
        return self.color if self.position is None else f"{self.color} {self.position}"


def validate_stops(kind: str, stops: object) -> tuple[ColorStop, ...]:
    if not isinstance(stops, list) or len(stops) < 2:
        raise InputError("stops must contain at least two color stops")
    parsed: list[ColorStop] = []
    for index, item in enumerate(stops):
        field = f"stops[{index}]"
        if not isinstance(item, dict):
            raise InputError(f"{field} must be an object")
        if set(item) - {"color", "position"}:
            raise InputError(f"{field} supports only color and position")
        color = validate_color(item.get("color"), f"{field}.color")
        raw_position = item.get("position")
        position = (
            None
            if raw_position is None
            else validate_stop_position(kind, raw_position, f"{field}.position")
        )
        parsed.append(ColorStop(color=color, position=position))
    return tuple(parsed)


def validate_geometry(kind: str, geometry: object) -> dict[str, str]:
    if not isinstance(geometry, dict):
        raise InputError("geometry must be an object")
    if kind == "linear":
        allowed = {"direction"}
        if set(geometry) - allowed:
            raise InputError("linear geometry supports only direction")
        return (
            {"direction": validate_direction(geometry["direction"], "geometry.direction")}
            if "direction" in geometry
            else {}
        )
    if kind == "radial":
        allowed = {"shape", "size", "position"}
        if set(geometry) - allowed:
            raise InputError("radial geometry supports only shape, size, and position")
        result: dict[str, str] = {}
        if "shape" in geometry:
            shape = _text(geometry["shape"], "geometry.shape")
            if shape not in RADIAL_SHAPES:
                raise InputError("geometry.shape must be circle or ellipse")
            result["shape"] = shape
        if "size" in geometry:
            size = _text(geometry["size"], "geometry.size")
            if size not in RADIAL_SIZES:
                raise InputError("geometry.size must be a radial extent keyword")
            result["size"] = size
        if "position" in geometry:
            result["position"] = validate_position(
                geometry["position"], "geometry.position"
            )
        return result
    allowed = {"from", "position"}
    if set(geometry) - allowed:
        raise InputError("conic geometry supports only from and position")
    result = {}
    if "from" in geometry:
        result["from"] = validate_angle(geometry["from"], "geometry.from")
    if "position" in geometry:
        result["position"] = validate_position(geometry["position"], "geometry.position")
    return result


@dataclass(frozen=True, init=False)
class Gradient:
    kind: str
    geometry: Mapping[str, str]
    stops: tuple[ColorStop, ...]

    def __init__(self, kind: object, geometry: object, stops: object) -> None:
        if kind not in {"linear", "radial", "conic"}:
            raise InputError("kind must be linear, radial, or conic")
        assert isinstance(kind, str)
        object.__setattr__(self, "kind", kind)
        object.__setattr__(self, "geometry", validate_geometry(kind, geometry))
        object.__setattr__(self, "stops", validate_stops(kind, stops))

    @classmethod
    def from_data(cls, data: object) -> Gradient:
        if not isinstance(data, dict):
            raise InputError("Input must be a JSON object")
        if set(data) - {"kind", "geometry", "stops"}:
            raise InputError("Input supports only kind, geometry, and stops")
        return cls(data.get("kind"), data.get("geometry"), data.get("stops"))

    def prelude(self) -> str | None:
        if self.kind == "linear":
            return self.geometry.get("direction")
        if self.kind == "radial":
            shape_and_size = " ".join(
                self.geometry[key] for key in ("shape", "size") if key in self.geometry
            )
            position = self.geometry.get("position")
            if shape_and_size and position:
                return f"{shape_and_size} at {position}"
            if position:
                return f"at {position}"
            return shape_and_size or None
        start = self.geometry.get("from")
        position = self.geometry.get("position")
        parts = [f"from {start}" for _ in (0,) if start]
        if position:
            parts.append(f"at {position}")
        return " ".join(parts) or None

    def value(self) -> str:
        items = [stop.serialize() for stop in self.stops]
        prelude = self.prelude()
        if prelude:
            items.insert(0, prelude)
        return f"{self.kind}-gradient({', '.join(items)})"

    def to_report(self) -> dict[str, object]:
        value = self.value()
        return {
            "kind": self.kind,
            "geometry": dict(self.geometry),
            "stops": [
                {"color": stop.color, "position": stop.position} for stop in self.stops
            ],
            "value": value,
            "css": f"background-image: {value};",
            "source_order": "preserved",
            "interpolation": {
                "specification_default": "Oklab",
                "serialized_explicitly": False,
                "target_browser_verification_required": True,
            },
            "standards": {
                "gradient_syntax": "https://drafts.csswg.org/css-images-4/#gradients",
                "color_syntax": "https://drafts.csswg.org/css-color-4/",
            },
            "limitations": [
                "One position per color stop; two-position stops and transition hints are not modeled.",
                "This model requires at least two stops although CSS Images Level 4 also defines single-stop gradients.",
                "Geometry positions use keywords; calc(), explicit radial radii, and interpolation-method controls are not modeled.",
                "Functional colors are injection-bounded but require browser parsing for full grammar conformance.",
                "Serialization does not establish rendered contrast, gamut mapping, or browser pixel fidelity.",
            ],
        }
