#!/usr/bin/env python3
"""Validate optional automation adapter metadata without invoking adapters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STRING_FIELDS = ("id", "role", "license", "source", "adoption")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path}: {error}") from error


def validate(plugin: Path) -> dict[str, object]:
    loaded = load_json(plugin / "references" / "automation-adapters.json")
    errors: list[str] = []
    if not isinstance(loaded, list):
        return {
            "adapters": [],
            "errors": ["automation-adapters.json must contain an array"],
            "warnings": [],
        }

    rows: list[dict[str, object]] = []
    for index, value in enumerate(loaded):
        if not isinstance(value, dict):
            errors.append(f"adapter row {index} must be an object")
            continue
        row: dict[str, object] = value
        rows.append(row)
        adapter_id = row.get("id")

        for field in STRING_FIELDS:
            field_value = row.get(field)
            if not isinstance(field_value, str) or not field_value.strip():
                errors.append(f"adapter {adapter_id} {field} must be a non-empty string")

        if not isinstance(row.get("required"), bool):
            errors.append(f"adapter {adapter_id} required must be a boolean")

        command = row.get("command")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(argument, str) and bool(argument) for argument in command)
        ):
            errors.append(f"adapter {adapter_id} command must be an argv array")

        adoption = row.get("adoption")
        if (
            isinstance(adoption, str)
            and adoption.startswith("blocked")
            and row.get("required") is not False
        ):
            errors.append(f"adapter {adapter_id} blocked adoption must remain optional")

    adapter_ids = [
        adapter_id
        for row in rows
        if isinstance((adapter_id := row.get("id")), str) and adapter_id.strip()
    ]
    if len(adapter_ids) != len(set(adapter_ids)):
        errors.append("adapter ids must be unique")

    return {"adapters": rows, "errors": errors, "warnings": []}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Validate optional css-tokenography automation adapter metadata."
    )
    parser.add_argument("--plugin", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--format", choices=("json", "human"), default="human")
    args = parser.parse_args()

    try:
        report = validate(args.plugin.resolve())
    except ValueError as error:
        print(f"adapter-validator: {error}")
        return 1

    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"adapters={len(report['adapters'])}")
        for error in report["errors"]:
            print(f"ERROR {error}")
        for warning in report["warnings"]:
            print(f"WARNING {warning}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
