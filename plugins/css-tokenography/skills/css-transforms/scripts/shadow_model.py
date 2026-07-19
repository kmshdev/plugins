"""Typed, source-order-preserving box-shadow validation and serialization."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


GRADIENT_SCRIPTS = Path(__file__).resolve().parents[2] / "css-gradients" / "scripts"
sys.path.insert(0, str(GRADIENT_SCRIPTS))

from gradient_model import InputError, NUMBER, validate_color


LENGTH = re.compile(
    rf"^(?:[+-]?0(?:\.0+)?|{NUMBER}(?:px|em|rem|ex|ch|lh|rlh|vw|vh|vmin|vmax|cm|mm|q|in|pc|pt))$"
)
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")
LAYER_FIELDS = {"id", "inset", "offset_x", "offset_y", "blur", "spread", "color"}
REQUIRED_LAYER_FIELDS = ("id", "inset", "offset_x", "offset_y", "blur", "spread", "color")


def parse_length(value: object, *, field: str, allow_negative: bool) -> str:
    if not isinstance(value, str) or LENGTH.fullmatch(value.strip()) is None:
        raise InputError(f"{field} must be a supported CSS length")
    result = value.strip()
    if not allow_negative and result.startswith("-"):
        raise InputError(f"{field} must not be negative")
    return result


def parse_identifier(value: object, *, field: str) -> str:
    if not isinstance(value, str) or IDENTIFIER.fullmatch(value.strip()) is None:
        raise InputError(f"{field} must be a simple identifier")
    return value.strip()


@dataclass(frozen=True)
class ShadowLayer:
    id: str
    inset: bool
    offset_x: str
    offset_y: str
    blur: str
    spread: str
    color: str

    @classmethod
    def from_data(cls, data: object, *, index: int) -> ShadowLayer:
        field = f"layers[{index}]"
        if not isinstance(data, dict):
            raise InputError(f"{field} must be an object")
        if set(data) - LAYER_FIELDS:
            raise InputError(
                f"{field} supports only id, inset, offset_x, offset_y, blur, spread, and color"
            )
        for key in REQUIRED_LAYER_FIELDS:
            if key not in data:
                raise InputError(f"{field}.{key} is required")
        inset = data["inset"]
        if not isinstance(inset, bool):
            raise InputError(f"{field}.inset must be boolean")
        return cls(
            id=parse_identifier(data["id"], field=f"{field}.id"),
            inset=inset,
            offset_x=parse_length(data["offset_x"], field=f"{field}.offset_x", allow_negative=True),
            offset_y=parse_length(data["offset_y"], field=f"{field}.offset_y", allow_negative=True),
            blur=parse_length(data["blur"], field=f"{field}.blur", allow_negative=False),
            spread=parse_length(data["spread"], field=f"{field}.spread", allow_negative=True),
            color=validate_color(data["color"], f"{field}.color"),
        )

    def value(self) -> str:
        parts = [self.offset_x, self.offset_y, self.blur, self.spread, self.color]
        if self.inset:
            parts.insert(0, "inset")
        return " ".join(parts)

    def to_report(self) -> dict[str, object]:
        return {
            "id": self.id,
            "inset": self.inset,
            "offset_x": self.offset_x,
            "offset_y": self.offset_y,
            "blur": self.blur,
            "spread": self.spread,
            "color": self.color,
            "value": self.value(),
        }


@dataclass(frozen=True)
class BoxShadow:
    layers: tuple[ShadowLayer, ...]

    @classmethod
    def from_data(cls, data: object) -> BoxShadow:
        if not isinstance(data, dict):
            raise InputError("Input must be a JSON object")
        if set(data) - {"layers"}:
            raise InputError("Input supports only layers")
        layers = data.get("layers")
        if not isinstance(layers, list) or not layers:
            raise InputError("layers must contain at least one shadow layer")
        parsed = tuple(
            ShadowLayer.from_data(layer, index=index) for index, layer in enumerate(layers)
        )
        ids = [layer.id for layer in parsed]
        if len(ids) != len(set(ids)):
            raise InputError("layer ids must be unique")
        return cls(layers=parsed)

    def value(self) -> str:
        return ", ".join(layer.value() for layer in self.layers)

    def to_report(self) -> dict[str, object]:
        value = self.value()
        return {
            "layers": [layer.to_report() for layer in self.layers],
            "value": value,
            "css": f"box-shadow: {value};",
            "layer_order": "preserved-front-to-back",
            "semantics": {
                "negative_offsets": "allowed",
                "negative_spread": "allowed",
                "negative_blur": "invalid",
                "inset": "required explicit boolean",
                "omitted_color": "not modeled; color is explicit",
            },
            "standards": {
                "grammar": "https://drafts.csswg.org/css-backgrounds-3/#typedef-shadow",
                "painting_order": "first layer is closest to the user",
            },
            "limitations": [
                "Colors are limited to the shared bounded CSS hex and named-color grammar.",
                "All four lengths and a color are explicit; omitted CSS defaults are not modeled.",
                "calc(), var(), global keywords, and percentages are not modeled.",
                "Serialization does not establish rendered blur pixels or browser fidelity.",
            ],
        }
