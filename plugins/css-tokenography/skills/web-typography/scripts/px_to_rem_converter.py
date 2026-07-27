#!/usr/bin/env python3
"""Convert a pixel value to rem using an explicit root size."""

from __future__ import annotations

import sys
from pathlib import Path


NUMERIC_SCRIPTS = Path(__file__).resolve().parents[2] / "css-functions" / "scripts"
sys.path.insert(0, str(NUMERIC_SCRIPTS))

from numeric_model import compact, finite_number, px_to_rem, run_cli


def build_report(data: dict[str, object]) -> dict[str, object]:
    return px_to_rem(
        finite_number(data, "px"),
        finite_number(data, "root_px"),
    )


def human_report(report: dict[str, object], data: dict[str, object]) -> str:
    pixels = compact(finite_number(data, "px"))
    root = compact(finite_number(data, "root_px"))
    return f"{pixels}px at a {root}px root = {report['css']}"


def main(argv: list[str] | None = None) -> int:
    return run_cli(
        "px-to-rem-converter",
        "Convert pixels to rem using an explicit positive root size.",
        build_report,
        human_report,
        argv,
    )


if __name__ == "__main__":
    raise SystemExit(main())
