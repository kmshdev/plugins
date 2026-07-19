#!/usr/bin/env python3
"""Reduce dimensions to a deterministic CSS aspect ratio."""

from __future__ import annotations

from numeric_model import compact, finite_number, reduce_ratio, run_cli


def build_report(data: dict[str, object]) -> dict[str, object]:
    return reduce_ratio(
        finite_number(data, "width"),
        finite_number(data, "height"),
    )


def human_report(report: dict[str, object], data: dict[str, object]) -> str:
    width = compact(finite_number(data, "width"))
    height = compact(finite_number(data, "height"))
    pair = report["pair"]
    assert isinstance(pair, list)
    return (
        f"{width} × {height} reduces to "
        f"{compact(pair[0])}:{compact(pair[1])}\n{report['css']}"
    )


def main(argv: list[str] | None = None) -> int:
    return run_cli(
        "aspect-ratio-calculator",
        "Reduce dimensions and generate a CSS aspect-ratio declaration.",
        build_report,
        human_report,
        argv,
    )


if __name__ == "__main__":
    raise SystemExit(main())
