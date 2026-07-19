#!/usr/bin/env python3
"""Generate a deterministic fluid CSS clamp expression."""

from __future__ import annotations

from numeric_model import build_clamp, compact, finite_number, run_cli


def build_report(data: dict[str, object]) -> dict[str, object]:
    return build_clamp(
        finite_number(data, "min_px"),
        finite_number(data, "max_px"),
        finite_number(data, "min_viewport_px"),
        finite_number(data, "max_viewport_px"),
        finite_number(data, "root_px"),
    )


def human_report(report: dict[str, object], data: dict[str, object]) -> str:
    minimum = compact(finite_number(data, "min_px"))
    maximum = compact(finite_number(data, "max_px"))
    min_viewport = compact(finite_number(data, "min_viewport_px"))
    max_viewport = compact(finite_number(data, "max_viewport_px"))
    return (
        f"Fluid size from {minimum}px to {maximum}px between "
        f"{min_viewport}px and {max_viewport}px:\n{report['css']}"
    )


def main(argv: list[str] | None = None) -> int:
    return run_cli(
        "clamp-generator",
        "Generate a fluid CSS clamp expression from pixel endpoints.",
        build_report,
        human_report,
        argv,
    )


if __name__ == "__main__":
    raise SystemExit(main())
