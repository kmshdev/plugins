"""Typed Flexbox container controls and logical-axis reporting."""

from __future__ import annotations

import re
import sys
from dataclasses import dataclass
from pathlib import Path


GRADIENT_SCRIPTS = Path(__file__).resolve().parents[2] / "css-gradients" / "scripts"
sys.path.insert(0, str(GRADIENT_SCRIPTS))

from gradient_model import InputError, LENGTH_PERCENTAGE


FLEX_DIRECTIONS = {"row", "row-reverse", "column", "column-reverse"}
FLEX_WRAPS = {"nowrap", "wrap", "wrap-reverse"}
JUSTIFY_CONTENT = {
    "normal",
    "start",
    "end",
    "center",
    "space-between",
    "space-around",
    "space-evenly",
}
ALIGN_ITEMS = {"normal", "stretch", "start", "end", "center", "baseline"}
CONTAINER_FIELDS = {
    "direction",
    "wrap",
    "justify_content",
    "align_items",
    "gap",
    "items",
}
ITEM_FIELDS = {"id", "order"}
IDENTIFIER = re.compile(r"^[A-Za-z][A-Za-z0-9_-]*$")


def enum_value(value: object, *, field: str, choices: set[str], default: str) -> str:
    result = default if value is None else value
    if not isinstance(result, str) or result not in choices:
        raise InputError(f"{field} must be one of {', '.join(sorted(choices))}")
    return result


def gap_value(value: object) -> str:
    result = "normal" if value is None else value
    if not isinstance(result, str):
        raise InputError("gap must be normal or a supported CSS length or percentage")
    result = result.strip()
    if result == "normal":
        return result
    if LENGTH_PERCENTAGE.fullmatch(result) is None:
        raise InputError("gap must be normal or a supported CSS length or percentage")
    if result.startswith("-"):
        raise InputError("gap must not be negative")
    return result


@dataclass(frozen=True)
class FlexItem:
    id: str
    order: int
    source_index: int

    @classmethod
    def from_data(cls, data: object, *, index: int) -> FlexItem:
        if not isinstance(data, dict):
            raise InputError(f"items[{index}] must be an object")
        if set(data) - ITEM_FIELDS:
            raise InputError(f"items[{index}] supports only id and order")
        identifier = data.get("id")
        if not isinstance(identifier, str) or IDENTIFIER.fullmatch(identifier) is None:
            raise InputError(f"items[{index}].id must be a simple identifier")
        order = data.get("order", 0)
        if isinstance(order, bool) or not isinstance(order, int):
            raise InputError(f"items[{index}].order must be an integer")
        return cls(id=identifier, order=order, source_index=index)

    def to_report(self) -> dict[str, object]:
        return {"id": self.id, "order": self.order, "source_index": self.source_index}


def parse_items(value: object) -> tuple[FlexItem, ...]:
    if not isinstance(value, list):
        raise InputError("items must be an array")
    items = tuple(FlexItem.from_data(item, index=index) for index, item in enumerate(value))
    ids = [item.id for item in items]
    if len(set(ids)) != len(ids):
        raise InputError("item ids must be unique")
    return items


def axes(direction: str, wrap: str) -> tuple[str, str]:
    if direction == "row":
        main_axis = "inline-start-to-inline-end"
        cross_axis = "block-start-to-block-end"
    elif direction == "row-reverse":
        main_axis = "inline-end-to-inline-start"
        cross_axis = "block-start-to-block-end"
    elif direction == "column":
        main_axis = "block-start-to-block-end"
        cross_axis = "inline-start-to-inline-end"
    else:
        main_axis = "block-end-to-block-start"
        cross_axis = "inline-start-to-inline-end"
    if wrap == "wrap-reverse":
        start, _, end = cross_axis.partition("-to-")
        cross_axis = f"{end}-to-{start}"
    return main_axis, cross_axis


@dataclass(frozen=True)
class Flexbox:
    direction: str
    wrap: str
    justify_content: str
    align_items: str
    gap: str
    items: tuple[FlexItem, ...]

    @classmethod
    def from_data(cls, data: object) -> Flexbox:
        if not isinstance(data, dict):
            raise InputError("Input must be a JSON object")
        if set(data) - CONTAINER_FIELDS:
            raise InputError(
                "Input supports only direction, wrap, justify_content, align_items, gap, and items"
            )
        return cls(
            direction=enum_value(
                data.get("direction"),
                field="direction",
                choices=FLEX_DIRECTIONS,
                default="row",
            ),
            wrap=enum_value(
                data.get("wrap"), field="wrap", choices=FLEX_WRAPS, default="nowrap"
            ),
            justify_content=enum_value(
                data.get("justify_content"),
                field="justify_content",
                choices=JUSTIFY_CONTENT,
                default="normal",
            ),
            align_items=enum_value(
                data.get("align_items"),
                field="align_items",
                choices=ALIGN_ITEMS,
                default="normal",
            ),
            gap=gap_value(data.get("gap")),
            items=parse_items(data.get("items", [])),
        )

    def to_report(self) -> dict[str, object]:
        declarations = {
            "display": "flex",
            "flex-direction": self.direction,
            "flex-wrap": self.wrap,
            "justify-content": self.justify_content,
            "align-items": self.align_items,
            "gap": self.gap,
        }
        main_axis, cross_axis = axes(self.direction, self.wrap)
        source_order = [item.id for item in self.items]
        order_modified = [
            item.id for item in sorted(self.items, key=lambda item: (item.order, item.source_index))
        ]
        css = "\n".join(f"{property_name}: {value};" for property_name, value in declarations.items())
        return {
            "declarations": declarations,
            "css": css,
            "main_axis": main_axis,
            "cross_axis": cross_axis,
            "items": [item.to_report() for item in self.items],
            "source_order": source_order,
            "order_modified_source_order": order_modified,
            "item_order": order_modified,
            "accessibility": [
                "Flex direction and order change visual traversal, not DOM, reading, or focus order."
            ],
            "standards": {
                "flex_direction": "https://drafts.csswg.org/css-flexbox-1/#flex-direction-property",
                "ordering": "https://drafts.csswg.org/css-flexbox-1/#order-accessibility",
                "alignment": "https://drafts.csswg.org/css-align-3/",
            },
            "limitations": [
                "The report normalizes logical axes; physical directions depend on writing mode and direction.",
                "The model does not predict wrapping, line breaks, free-space distribution, or browser sizes without item and container dimensions.",
                "Only normal or primitive nonnegative length-percentage gaps are modeled; calc(), var(), and global keywords are unsupported.",
                "Order-modified source order is reported, but rendered positions and keyboard or reading order are not inferred.",
            ],
        }


def build_report(data: dict[str, object]) -> dict[str, object]:
    return Flexbox.from_data(data).to_report()
