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
MAX_ITEMS = 1000
MAX_IDENTIFIER_LENGTH = 128
MIN_ORDER = -(2**31)
MAX_ORDER = 2**31 - 1


def enum_value(value: object, *, field: str, choices: set[str]) -> str:
    if not isinstance(value, str) or value not in choices:
        raise InputError(f"{field} must be one of {', '.join(sorted(choices))}")
    return value


def gap_value(value: object) -> str:
    if not isinstance(value, str):
        raise InputError("gap must be normal or a supported CSS length or percentage")
    result = value.strip()
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
        if len(identifier) > MAX_IDENTIFIER_LENGTH:
            raise InputError(
                f"items[{index}].id must be at most {MAX_IDENTIFIER_LENGTH} characters"
            )
        order = data.get("order", 0)
        if isinstance(order, bool) or not isinstance(order, int):
            raise InputError(f"items[{index}].order must be an integer")
        if not MIN_ORDER <= order <= MAX_ORDER:
            raise InputError(
                f"items[{index}].order must be between {MIN_ORDER} and {MAX_ORDER}"
            )
        return cls(id=identifier, order=order, source_index=index)

    def to_report(self) -> dict[str, object]:
        return {"id": self.id, "order": self.order, "source_index": self.source_index}


def parse_items(value: object) -> tuple[FlexItem, ...]:
    if not isinstance(value, list):
        raise InputError("items must be an array")
    if len(value) > MAX_ITEMS:
        raise InputError(f"items must contain at most {MAX_ITEMS} entries")
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
                data["direction"] if "direction" in data else "row",
                field="direction",
                choices=FLEX_DIRECTIONS,
            ),
            wrap=enum_value(
                data["wrap"] if "wrap" in data else "nowrap",
                field="wrap",
                choices=FLEX_WRAPS,
            ),
            justify_content=enum_value(
                data["justify_content"] if "justify_content" in data else "normal",
                field="justify_content",
                choices=JUSTIFY_CONTENT,
            ),
            align_items=enum_value(
                data["align_items"] if "align_items" in data else "normal",
                field="align_items",
                choices=ALIGN_ITEMS,
            ),
            gap=gap_value(data["gap"] if "gap" in data else "normal"),
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
