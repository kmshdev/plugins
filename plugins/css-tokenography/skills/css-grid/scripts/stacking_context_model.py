#!/usr/bin/env python3
"""Deterministic stacking-context model over pre-collected element facts."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable


GLOBAL_KEYWORDS = {"inherit", "initial", "revert", "revert-layer", "unset"}
CONTEXT_ANIMATION_PROPERTIES = {
    "opacity", "transform", "scale", "rotate", "translate", "filter",
    "backdrop-filter", "backdrop_filter", "clip-path", "clip_path", "mask",
}


class StackingInputError(ValueError):
    pass


@dataclass(frozen=True)
class Trigger:
    name: str
    predicate: Callable[[dict[str, Any]], bool]


def style(fact: dict[str, Any], key: str, default: Any = None) -> Any:
    return fact["style"].get(key, default)


def not_none(value: Any) -> bool:
    return value is not None and str(value).strip().lower() != "none"


def z_index(value: Any, element_id: str) -> int | str:
    if value is None:
        return "auto"
    if isinstance(value, bool) or not (
        isinstance(value, int) or isinstance(value, str) and value in {"auto", *GLOBAL_KEYWORDS}
    ):
        raise StackingInputError(
            f"elements[{element_id}].style.z_index must be auto, an integer, or a CSS-wide keyword"
        )
    return value


def non_auto_z(fact: dict[str, Any]) -> bool:
    return isinstance(fact["z_index"], int)


def contains_token(value: Any, tokens: set[str]) -> bool:
    if not isinstance(value, str):
        return False
    return bool(set(value.lower().replace(",", " ").split()) & tokens)


def retained_animation(fact: dict[str, Any]) -> bool:
    value = fact.get("retained_animation_properties", [])
    return isinstance(value, list) and any(item in CONTEXT_ANIMATION_PROPERTIES for item in value)


STACKING_TRIGGERS: tuple[Trigger, ...] = (
    Trigger("root", lambda fact: fact.get("is_root") is True),
    Trigger("positioned-z-index", lambda fact: style(fact, "position", "static") in {"absolute", "relative"} and non_auto_z(fact)),
    Trigger("fixed-or-sticky", lambda fact: style(fact, "position", "static") in {"fixed", "sticky"}),
    Trigger("flex-or-grid-item-z-index", lambda fact: (fact.get("is_flex_item") is True or fact.get("is_grid_item") is True) and non_auto_z(fact)),
    Trigger("opacity", lambda fact: isinstance(style(fact, "opacity", 1), (int, float)) and not isinstance(style(fact, "opacity", 1), bool) and style(fact, "opacity", 1) < 1),
    Trigger("mix-blend-mode", lambda fact: style(fact, "mix_blend_mode", "normal") != "normal"),
    Trigger("transform", lambda fact: not_none(style(fact, "transform"))),
    Trigger("scale", lambda fact: not_none(style(fact, "scale"))),
    Trigger("rotate", lambda fact: not_none(style(fact, "rotate"))),
    Trigger("translate", lambda fact: not_none(style(fact, "translate"))),
    Trigger("filter", lambda fact: not_none(style(fact, "filter"))),
    Trigger("backdrop-filter", lambda fact: not_none(style(fact, "backdrop_filter"))),
    Trigger("perspective", lambda fact: not_none(style(fact, "perspective"))),
    Trigger("clip-path", lambda fact: not_none(style(fact, "clip_path"))),
    Trigger("mask", lambda fact: any(not_none(style(fact, name)) for name in ("mask", "mask_image", "mask_border"))),
    Trigger("isolation", lambda fact: style(fact, "isolation") == "isolate"),
    Trigger("contain", lambda fact: contains_token(style(fact, "contain"), {"layout", "paint", "strict", "content"})),
    Trigger("container-type", lambda fact: style(fact, "container_type", "normal") in {"size", "inline-size"}),
    Trigger("will-change", lambda fact: contains_token(style(fact, "will_change"), CONTEXT_ANIMATION_PROPERTIES)),
    Trigger("top-layer", lambda fact: fact.get("top_layer") is True),
    Trigger("retained-animation", retained_animation),
)


_TRANSFORM_CB = lambda fact: any(
    not_none(style(fact, name))
    for name in ("transform", "scale", "rotate", "translate", "filter", "backdrop_filter", "perspective")
)
_CONTAINING_CONTAIN = lambda fact: contains_token(style(fact, "contain"), {"layout", "paint", "strict", "content"})
_CB_WILL_CHANGE = lambda fact: contains_token(
    style(fact, "will_change"),
    {"transform", "filter", "backdrop-filter", "backdrop_filter", "perspective", "contain"},
)

ABSOLUTE_CB_TRIGGERS: tuple[Trigger, ...] = (
    Trigger("positioned", lambda fact: style(fact, "position", "static") != "static"),
    Trigger("transform-like", _TRANSFORM_CB),
    Trigger("contain", _CONTAINING_CONTAIN),
    Trigger("container-type", lambda fact: style(fact, "container_type", "normal") in {"size", "inline-size"}),
    Trigger("content-visibility", lambda fact: style(fact, "content_visibility") == "auto"),
    Trigger("will-change", _CB_WILL_CHANGE),
)

FIXED_CB_TRIGGERS: tuple[Trigger, ...] = (
    Trigger("transform-like", _TRANSFORM_CB),
    Trigger("contain", _CONTAINING_CONTAIN),
    Trigger("content-visibility", lambda fact: style(fact, "content_visibility") == "auto"),
    Trigger("will-change", _CB_WILL_CHANGE),
)


def trigger_names(fact: dict[str, Any], registry: tuple[Trigger, ...]) -> list[str]:
    return [trigger.name for trigger in registry if trigger.predicate(fact)]


def validate_tree(elements: Any) -> list[dict[str, Any]]:
    if not isinstance(elements, list) or not elements:
        raise StackingInputError("elements must be a non-empty array of pre-collected element facts")
    normalized: list[dict[str, Any]] = []
    ids: set[str] = set()
    orders: set[int] = set()
    for index, raw in enumerate(elements):
        if not isinstance(raw, dict):
            raise StackingInputError(f"elements[{index}] must be an object")
        identifier = raw.get("id")
        order = raw.get("order")
        computed = raw.get("style", {})
        if not isinstance(identifier, str) or not identifier or identifier in ids:
            raise StackingInputError(f"elements[{index}].id must be a unique non-empty string")
        if isinstance(order, bool) or not isinstance(order, int) or order in orders:
            raise StackingInputError(f"elements[{identifier}].order must be a unique integer")
        if not isinstance(computed, dict):
            raise StackingInputError(f"elements[{identifier}].style must be an object")
        item = {**raw, "style": dict(computed)}
        item["z_index"] = z_index(computed.get("z_index"), identifier)
        normalized.append(item)
        ids.add(identifier)
        orders.add(order)
    roots = [item for item in normalized if item.get("is_root") is True]
    if len(roots) != 1 or roots[0].get("parent") is not None:
        raise StackingInputError("exactly one root with parent null and is_root true is required")
    by_id = {item["id"]: item for item in normalized}
    for item in normalized:
        parent = item.get("parent")
        if not item.get("is_root") and parent not in by_id:
            raise StackingInputError(f"elements[{item['id']}].parent must reference another element")
        seen = {item["id"]}
        while parent is not None:
            if parent in seen:
                raise StackingInputError(f"elements[{item['id']}] creates a parent cycle")
            seen.add(parent)
            parent = by_id[parent].get("parent")
    return sorted(normalized, key=lambda item: item["order"])


def analyze_tree(elements: Any) -> dict[str, Any]:
    facts = validate_tree(elements)
    by_id = {fact["id"]: fact for fact in facts}
    root_id = next(fact["id"] for fact in facts if fact.get("is_root"))
    contexts: dict[str, dict[str, Any]] = {}
    results: dict[str, dict[str, Any]] = {}

    def ancestor_with(identifier: str, registry: tuple[Trigger, ...], fallback: str) -> str:
        parent = by_id[identifier].get("parent")
        while parent is not None:
            candidate = by_id[parent]
            if trigger_names(candidate, registry):
                return parent
            parent = candidate.get("parent")
        return fallback

    for fact in facts:
        reasons = trigger_names(fact, STACKING_TRIGGERS)
        absolute_reasons = trigger_names(fact, ABSOLUTE_CB_TRIGGERS)
        fixed_reasons = trigger_names(fact, FIXED_CB_TRIGGERS)
        results[fact["id"]] = {
            "creates_context": bool(reasons),
            "context_reasons": reasons,
            "creates_absolute_containing_block": bool(absolute_reasons) or fact.get("is_root") is True,
            "absolute_containing_block_reasons": absolute_reasons,
            "creates_fixed_containing_block": bool(fixed_reasons),
            "fixed_containing_block_reasons": fixed_reasons,
            "absolute_containing_block": ancestor_with(fact["id"], ABSOLUTE_CB_TRIGGERS, root_id),
            "fixed_containing_block": ancestor_with(fact["id"], FIXED_CB_TRIGGERS, "viewport"),
        }
        if reasons:
            parent = fact.get("parent")
            parent_context = None
            if not fact.get("is_root"):
                while parent is not None and not results.get(parent, {}).get("creates_context"):
                    parent = by_id[parent].get("parent")
                parent_context = parent or root_id
            value = fact["z_index"]
            phase = (
                "top-layer" if fact.get("top_layer") else
                "negative-z-index" if isinstance(value, int) and value < 0 else
                "positive-z-index" if isinstance(value, int) and value > 0 else
                "auto-or-zero-z-index"
            )
            contexts[fact["id"]] = {
                "parent_context": parent_context,
                "trigger_reasons": reasons,
                "z_index": value,
                "paint_phase": phase,
                "document_order": fact["order"],
                "children_in_paint_order": [],
            }

    phase_rank = {"negative-z-index": 0, "auto-or-zero-z-index": 1, "positive-z-index": 2, "top-layer": 3}
    for context_id, context in contexts.items():
        parent = context["parent_context"]
        if parent is not None:
            contexts[parent]["children_in_paint_order"].append(context_id)
    for context in contexts.values():
        context["children_in_paint_order"].sort(key=lambda identifier: (
            phase_rank[contexts[identifier]["paint_phase"]],
            contexts[identifier]["z_index"] if isinstance(contexts[identifier]["z_index"], int) else 0,
            contexts[identifier]["document_order"],
        ))
    return {
        "schema": "pre-collected-computed-element-facts-v1",
        "elements": results,
        "contexts": contexts,
        "root_context": root_id,
        "warnings": [
            "This deterministic analyzer consumes pre-collected computed facts; it does not parse raw HTML/CSS or claim browser visual fidelity."
        ],
    }
