#!/usr/bin/env python3
"""Model CSS subgrid track inheritance without a browser."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, TextIO


class SubgridInputError(ValueError):
    pass


def read_json(path: str, stdin: TextIO) -> dict[str, Any]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise SubgridInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise SubgridInputError("Input must be a JSON object")
    return value


def positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise SubgridInputError(f"{field} must be a positive integer")
    return value


def track_list(parent: dict[str, Any], field: str, count: int) -> list[str]:
    raw = parent.get(field)
    if raw is None:
        return ["1fr"] * count
    if not isinstance(raw, list) or len(raw) != count:
        raise SubgridInputError(f"parent.{field} must contain exactly {count} track values")
    values = []
    for index, value in enumerate(raw):
        if not isinstance(value, str) or not value.strip() or re.search(r"[;{}<>\n\r]", value):
            raise SubgridInputError(f"parent.{field}[{index}] must be one safe CSS track value")
        values.append(value.strip())
    return values


def validate_axis(item: dict[str, Any], axis: str, tracks: int) -> tuple[int, int, int]:
    start = positive_int(item.get(f"{axis}_start"), f"{axis}_start")
    end = positive_int(item.get(f"{axis}_end"), f"{axis}_end")
    if start >= end:
        raise SubgridInputError(f"{axis} placement requires start < end")
    if end > tracks + 1:
        raise SubgridInputError(
            f"{axis} placement {start}/{end} crosses the parent boundary at grid line {tracks + 1}"
        )
    return start, end, end - start


def model_item(item: dict[str, Any], columns: int, rows: int, gap: str, depth: int = 0) -> dict[str, Any]:
    if not isinstance(item, dict):
        raise SubgridInputError("each item must be a JSON object")
    name = item.get("name")
    if not isinstance(name, str) or not name.strip():
        raise SubgridInputError("each item requires a non-empty name")
    column_start, column_end, inherited_columns = validate_axis(item, "column", columns)
    row_start, row_end, inherited_rows = validate_axis(item, "row", rows)
    subgrid_columns = bool(item.get("subgrid_columns", False))
    subgrid_rows = bool(item.get("subgrid_rows", False))
    children_raw = item.get("children", [])
    if not isinstance(children_raw, list):
        raise SubgridInputError(f"children for {name!r} must be an array")
    if children_raw and not (subgrid_columns or subgrid_rows):
        raise SubgridInputError(f"item {name!r} has nested placement but no subgrid axis")

    child_columns = inherited_columns if subgrid_columns else positive_int(item.get("child_columns", 1), "child_columns")
    child_rows = inherited_rows if subgrid_rows else positive_int(item.get("child_rows", 1), "child_rows")
    children = [model_item(child, child_columns, child_rows, gap, depth + 1) for child in children_raw]
    return {
        "name": name.strip(),
        "column_start": column_start,
        "column_end": column_end,
        "row_start": row_start,
        "row_end": row_end,
        "subgrid_columns": subgrid_columns,
        "subgrid_rows": subgrid_rows,
        "inherited_columns": inherited_columns if subgrid_columns else 0,
        "inherited_rows": inherited_rows if subgrid_rows else 0,
        "gap": gap,
        "depth": depth,
        "children": children,
    }


def css_for_item(item: dict[str, Any], index_path: str) -> str:
    selector = f".grid-item-{index_path}"
    declarations = [
        f"  grid-column: {item['column_start']} / {item['column_end']};",
        f"  grid-row: {item['row_start']} / {item['row_end']};",
    ]
    if item["subgrid_columns"] or item["subgrid_rows"]:
        declarations.append("  display: grid;")
    if item["subgrid_columns"]:
        declarations.append("  grid-template-columns: subgrid;")
    if item["subgrid_rows"]:
        declarations.append("  grid-template-rows: subgrid;")
    blocks = [f"{selector} {{\n" + "\n".join(declarations) + "\n}"]
    for child_index, child in enumerate(item["children"], start=1):
        blocks.append(css_for_item(child, f"{index_path}-{child_index}"))
    return "\n\n".join(blocks)


def build_result(data: dict[str, Any]) -> dict[str, Any]:
    parent = data.get("parent")
    if not isinstance(parent, dict):
        raise SubgridInputError("parent must be a JSON object")
    columns = positive_int(parent.get("columns"), "parent.columns")
    rows = positive_int(parent.get("rows"), "parent.rows")
    column_tracks = track_list(parent, "column_tracks", columns)
    row_tracks = track_list(parent, "row_tracks", rows)
    gap = parent.get("gap", "0")
    if not isinstance(gap, str) or not gap.strip():
        raise SubgridInputError("parent.gap must be a non-empty CSS value")
    items_raw = data.get("items")
    if not isinstance(items_raw, list) or not items_raw:
        raise SubgridInputError("items must be a non-empty array")
    items = [model_item(item, columns, rows, gap.strip()) for item in items_raw]
    parent_css = (
        ".parent-grid {\n"
        "  display: grid;\n"
        f"  grid-template-columns: {' '.join(column_tracks)};\n"
        f"  grid-template-rows: {' '.join(row_tracks)};\n"
        f"  gap: {gap.strip()};\n"
        "}"
    )
    css = "\n\n".join([parent_css, *[css_for_item(item, str(index)) for index, item in enumerate(items, start=1)]])
    return {
        "parent": {
            "columns": columns,
            "rows": rows,
            "column_tracks": column_tracks,
            "row_tracks": row_tracks,
            "gap": gap.strip(),
        },
        "items": items,
        "css": css,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Model parent tracks, item spans, and CSS subgrid inheritance.")
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin (default)")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = build_result(read_json(args.input, sys.stdin))
    except SubgridInputError as error:
        print(f"subgrid-visualizer: {error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.format == "css":
        print(result["css"])
    else:
        print(f"Modeled {len(result['items'])} item(s) on a {result['parent']['columns']}x{result['parent']['rows']} parent grid")
        print(result["css"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
