#!/usr/bin/env python3
"""Validate a named CSS Grid matrix and emit grid-template-areas."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, TextIO


NAME_RE = re.compile(r"^-?[_a-zA-Z][_a-zA-Z0-9-]*$")
EMPTY = {"", ".", None}


class GridInputError(ValueError):
    pass


def read_json(path: str, stdin: TextIO) -> dict[str, Any]:
    try:
        raw = stdin.read() if path == "-" else Path(path).read_text(encoding="utf-8")
        value = json.loads(raw)
    except (OSError, json.JSONDecodeError) as error:
        raise GridInputError(f"Unable to read JSON input: {error}") from error
    if not isinstance(value, dict):
        raise GridInputError("Input must be a JSON object")
    return value


def positive_int(value: Any, field: str) -> int:
    if isinstance(value, bool) or not isinstance(value, int) or value < 1:
        raise GridInputError(f"{field} must be a positive integer")
    return value


def normalize_matrix(data: dict[str, Any]) -> tuple[int, int, list[list[str]], str]:
    rows = positive_int(data.get("rows"), "rows")
    columns = positive_int(data.get("columns"), "columns")
    raw_cells = data.get("cells")
    if not isinstance(raw_cells, list) or len(raw_cells) != rows:
        raise GridInputError(f"cells must contain exactly {rows} rows")

    cells: list[list[str]] = []
    for row_index, raw_row in enumerate(raw_cells, start=1):
        if not isinstance(raw_row, list) or len(raw_row) != columns:
            raise GridInputError(f"row {row_index} must contain exactly {columns} cells")
        row: list[str] = []
        for column_index, raw_name in enumerate(raw_row, start=1):
            name = "." if raw_name in EMPTY else raw_name
            if not isinstance(name, str) or (name != "." and not NAME_RE.fullmatch(name)):
                raise GridInputError(
                    f"cell {row_index},{column_index} has invalid area name {raw_name!r}; use a CSS identifier or '.'"
                )
            if name in {"auto", "span"}:
                raise GridInputError(f"area name {name!r} is reserved by CSS Grid")
            row.append(name)
        cells.append(row)

    gap = data.get("gap", "1rem")
    if not isinstance(gap, str) or not gap.strip():
        raise GridInputError("gap must be a non-empty CSS length string")
    return rows, columns, cells, gap.strip()


def validate_rectangles(cells: list[list[str]]) -> list[str]:
    names = list(dict.fromkeys(name for row in cells for name in row if name != "."))
    for name in names:
        coordinates = [(r, c) for r, row in enumerate(cells) for c, cell in enumerate(row) if cell == name]
        min_row = min(r for r, _ in coordinates)
        max_row = max(r for r, _ in coordinates)
        min_column = min(c for _, c in coordinates)
        max_column = max(c for _, c in coordinates)
        expected = {
            (r, c)
            for r in range(min_row, max_row + 1)
            for c in range(min_column, max_column + 1)
        }
        if set(coordinates) != expected:
            raise GridInputError(
                f"area {name!r} must form one filled rectangular region; disconnected and L-shaped areas are invalid"
            )
    return names


def build_result(data: dict[str, Any]) -> dict[str, Any]:
    rows, columns, cells, gap = normalize_matrix(data)
    names = validate_rectangles(cells)
    area_rows = [f'"{" ".join(row)}"' for row in cells]
    template = "\n    ".join(area_rows)
    container_css = (
        ".grid-container {\n"
        "  display: grid;\n"
        f"  grid-template-columns: repeat({columns}, 1fr);\n"
        f"  grid-template-rows: repeat({rows}, 1fr);\n"
        f"  grid-template-areas:\n    {template};\n"
        f"  gap: {gap};\n"
        "}"
    )
    item_css = "\n\n".join(f".{name} {{\n  grid-area: {name};\n}}" for name in names)
    css = container_css + ("\n\n" + item_css if item_css else "")
    return {
        "rows": rows,
        "columns": columns,
        "cells": cells,
        "areas": names,
        "grid_template_areas": area_rows,
        "css": css,
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(description="Validate a named grid and generate CSS grid-template-areas.")
    result.add_argument("--input", default="-", help="JSON file path, or '-' for stdin (default)")
    result.add_argument("--format", choices=("json", "css", "human"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    try:
        result = build_result(read_json(args.input, sys.stdin))
    except GridInputError as error:
        print(f"grid-area-mapper: {error}", file=sys.stderr)
        return 1
    if args.format == "json":
        print(json.dumps(result, indent=2, sort_keys=True))
    elif args.format == "css":
        print(result["css"])
    else:
        print(f"Valid {result['rows']}x{result['columns']} grid with {len(result['areas'])} named areas")
        print(result["css"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
