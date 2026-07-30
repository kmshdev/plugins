#!/usr/bin/env python3
"""Validate optional automation adapter metadata without invoking adapters."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any


STRING_FIELDS = (
    "id",
    "role",
    "kind",
    "license",
    "license_record",
    "source",
    "adoption",
    "activation",
    "network",
)
ALLOWED_KINDS = {"executable", "node-package"}
ALLOWED_ACTIVATION = {"explicit-only", "manual-only"}
ALLOWED_NETWORK = {"none", "optional", "required-live"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path}: {error}") from error


def error_report(message: str) -> dict[str, object]:
    return {"adapters": [], "errors": [message], "warnings": []}


def relative_file(plugin: Path, value: object, *, root: Path) -> Path | None:
    if not isinstance(value, str) or not value:
        return None
    relative = Path(value)
    if relative.is_absolute():
        return None
    candidate = (plugin / relative).resolve()
    resolved_root = root.resolve()
    if candidate == resolved_root or not candidate.is_relative_to(resolved_root):
        return None
    return candidate if candidate.is_file() else None


def validate_node_package(
    plugin: Path, adapter_id: object, row: dict[str, object]
) -> list[str]:
    errors: list[str] = []
    package = row.get("package")
    version = row.get("version")
    workspace = row.get("workspace")
    if not isinstance(package, str) or not package:
        errors.append(f"adapter {adapter_id} package must be a non-empty string")
    if not isinstance(version, str) or not version:
        errors.append(f"adapter {adapter_id} version must be a non-empty string")
    if not isinstance(workspace, str) or not workspace:
        errors.append(f"adapter {adapter_id} workspace must be a non-empty string")
        return errors

    package_json = relative_file(
        plugin, f"{workspace}/package.json", root=plugin / "laboratory"
    )
    if package_json is None:
        errors.append(
            f"adapter {adapter_id} workspace must contain a package.json under laboratory/"
        )
        return errors
    try:
        manifest = load_json(package_json)
    except ValueError as error:
        errors.append(f"adapter {adapter_id} package manifest is unreadable: {error}")
        return errors
    if not isinstance(manifest, dict):
        errors.append(f"adapter {adapter_id} package manifest must be an object")
        return errors

    dependencies: dict[str, object] = {}
    for field in ("dependencies", "devDependencies", "optionalDependencies"):
        values = manifest.get(field)
        if isinstance(values, dict):
            dependencies.update(values)
    if isinstance(package, str) and dependencies.get(package) != version:
        errors.append(
            f"adapter {adapter_id} workspace must pin {package} exactly to {version}"
        )
    if row.get("command") is not None:
        errors.append(f"adapter {adapter_id} node-package must not declare a command")
    return errors


def validate(plugin: Path) -> dict[str, object]:
    try:
        loaded = load_json(plugin / "references" / "automation-adapters.json")
    except ValueError as error:
        return error_report(str(error))
    errors: list[str] = []
    if not isinstance(loaded, list):
        return error_report("automation-adapters.json must contain an array")

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

        required = row.get("required")
        if not isinstance(required, bool):
            errors.append(f"adapter {adapter_id} required must be a boolean")
        elif required:
            errors.append(f"adapter {adapter_id} required must be false")

        kind = row.get("kind")
        if kind not in ALLOWED_KINDS:
            errors.append(f"adapter {adapter_id} kind must be executable or node-package")
        elif kind == "executable":
            command = row.get("command")
            if (
                not isinstance(command, list)
                or not command
                or not all(
                    isinstance(argument, str) and bool(argument) for argument in command
                )
            ):
                errors.append(f"adapter {adapter_id} command must be an argv array")
        else:
            errors.extend(validate_node_package(plugin, adapter_id, row))

        activation = row.get("activation")
        if activation not in ALLOWED_ACTIVATION:
            errors.append(f"adapter {adapter_id} has invalid activation {activation!r}")
        network = row.get("network")
        if network not in ALLOWED_NETWORK:
            errors.append(f"adapter {adapter_id} has invalid network mode {network!r}")

        credentials = row.get("credentials")
        if not isinstance(credentials, list) or not all(
            isinstance(item, str) and item for item in credentials
        ):
            errors.append(f"adapter {adapter_id} credentials must be an array of names")
        elif len(credentials) != len(set(credentials)):
            errors.append(f"adapter {adapter_id} credentials must not contain duplicates")

        license_record = relative_file(
            plugin, row.get("license_record"), root=plugin / "references" / "licenses"
        )
        if license_record is None:
            errors.append(
                f"adapter {adapter_id} license_record must name a file under references/licenses/"
            )

        adoption = row.get("adoption")
        if (
            isinstance(adoption, str)
            and (
                adoption.startswith("blocked")
                or adoption.endswith("only")
            )
            and row.get("required") is not False
        ):
            errors.append(f"adapter {adapter_id} restricted adoption must remain optional")

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
    parser.add_argument(
        "--plugin", type=Path, default=Path(__file__).resolve().parents[1]
    )
    parser.add_argument("--format", choices=("json", "human"), default="human")
    args = parser.parse_args()

    try:
        report = validate(args.plugin.resolve())
    except ValueError as error:
        report = error_report(str(error))

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
