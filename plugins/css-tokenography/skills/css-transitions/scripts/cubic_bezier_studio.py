#!/usr/bin/env python3
"""Generate a valid CSS cubic-bezier() timing function."""

from __future__ import annotations

import sys
from pathlib import Path


NUMERIC_SCRIPTS = Path(__file__).resolve().parents[2] / "css-functions" / "scripts"
sys.path.insert(0, str(NUMERIC_SCRIPTS))

from numeric_model import InputError, compact, finite_number, run_cli


def build_bezier(x1: object, y1: object, x2: object, y2: object) -> dict[str, object]:
    values = [
        finite_number({"x1": x1}, "x1"),
        finite_number({"y1": y1}, "y1"),
        finite_number({"x2": x2}, "x2"),
        finite_number({"y2": y2}, "y2"),
    ]
    for key, value in (("x1", values[0]), ("x2", values[2])):
        if not 0 <= value <= 1:
            raise InputError(f"{key} must be between 0 and 1 inclusive")
    css = "cubic-bezier(" + ", ".join(compact(value) for value in values) + ")"
    return {
        "status": "valid",
        "css": css,
        "control_points": values,
    }


def build_report(data: dict[str, object]) -> dict[str, object]:
    return build_bezier(
        data.get("x1"),
        data.get("y1"),
        data.get("x2"),
        data.get("y2"),
    )


def human_report(report: dict[str, object], data: dict[str, object]) -> str:
    points = report["control_points"]
    return (
        f"{report['css']}\n"
        f"P1=({compact(points[0])}, {compact(points[1])}); "
        f"P2=({compact(points[2])}, {compact(points[3])})"
    )


def main(argv: list[str] | None = None) -> int:
    return run_cli(
        "cubic-bezier-studio",
        "Generate a CSS cubic-bezier() with constrained x control points.",
        build_report,
        human_report,
        argv,
    )


if __name__ == "__main__":
    raise SystemExit(main())
