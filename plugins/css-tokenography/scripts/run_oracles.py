#!/usr/bin/env python3
"""Run declared optional CSS oracles without making them dependencies."""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Any

from css_tokenography_core import EvidenceEnvelope, OracleObservation


PLUGIN = Path(__file__).resolve().parents[1]
REGISTRY = PLUGIN / "references" / "automation-adapters.json"
ADAPTERS = PLUGIN / "scripts" / "adapters"


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise ValueError(f"unable to read {path}: {error}") from error


def validate_payload(value: object) -> dict[str, object]:
    if not isinstance(value, dict):
        raise ValueError("input must contain a JSON object")
    if value.get("subject") != "transform":
        raise ValueError("subject must be transform")

    core = value.get("input")
    if not isinstance(core, dict):
        raise ValueError("input.input must be an object")

    adapters = value.get("adapters")
    if (
        not isinstance(adapters, list)
        or not adapters
        or not all(isinstance(adapter, str) and adapter for adapter in adapters)
    ):
        raise ValueError("adapters must be a non-empty array of adapter ids")
    if len(adapters) != len(set(adapters)):
        raise ValueError("adapters must not contain duplicate ids")
    return value


def load_registry() -> dict[str, dict[str, object]]:
    rows = load_json(REGISTRY)
    if not isinstance(rows, list):
        raise ValueError("automation-adapters.json must contain an array")

    registry: dict[str, dict[str, object]] = {}
    for row in rows:
        if not isinstance(row, dict):
            raise ValueError("automation adapter rows must be objects")
        adapter_id = row.get("id")
        command = row.get("command")
        if not isinstance(adapter_id, str) or not adapter_id:
            raise ValueError("automation adapter id must be a non-empty string")
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(item, str) and item for item in command)
        ):
            raise ValueError(f"adapter {adapter_id} command must be an argv array")
        registry[adapter_id] = row
    return registry


def parse_overrides(values: list[str]) -> dict[str, list[str]]:
    overrides: dict[str, list[str]] = {}
    for value in values:
        adapter_id, separator, encoded = value.partition("=")
        if not separator or not adapter_id:
            raise ValueError("adapter commands must use ID=JSON_ARGV")
        try:
            command = json.loads(encoded)
        except json.JSONDecodeError as error:
            raise ValueError(f"invalid command for adapter {adapter_id}: {error}") from error
        if (
            not isinstance(command, list)
            or not command
            or not all(isinstance(item, str) and item for item in command)
        ):
            raise ValueError(f"adapter {adapter_id} override must be an argv array")
        if adapter_id in overrides:
            raise ValueError(f"adapter {adapter_id} has more than one override")
        overrides[adapter_id] = command
    return overrides


def json_exact(left: object, right: object) -> bool:
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            json_exact(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            json_exact(left_item, right_item)
            for left_item, right_item in zip(left, right)
        )
    return left == right


def execute_adapter(
    argv: list[str], payload: dict[str, object], *, oracle: str | None = None
) -> OracleObservation:
    oracle_name = oracle or argv[0]
    executable = shutil.which(argv[0])
    if executable is None:
        return OracleObservation(oracle_name, "unavailable", None)

    result = subprocess.run(
        [executable, *argv[1:]],
        input=json.dumps(payload, sort_keys=True),
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        note = result.stderr.strip() or f"adapter exited {result.returncode}"
        return OracleObservation(oracle_name, "error", None, notes=(note,))
    try:
        value = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        return OracleObservation(
            oracle_name,
            "error",
            None,
            notes=(f"adapter returned invalid JSON: {error}",),
        )

    relation = "exact" if json_exact(value, payload) else "different"
    return OracleObservation(
        oracle_name,
        "ok",
        value,
        relation_to_core=relation,
    )


def run(payload: dict[str, object], overrides: dict[str, list[str]]) -> EvidenceEnvelope:
    registry = load_registry()
    requested = payload["adapters"]
    core = payload["input"]
    assert isinstance(requested, list)
    assert isinstance(core, dict)
    envelope = EvidenceEnvelope(core=core)

    unknown_overrides = sorted(set(overrides) - set(requested))
    if unknown_overrides:
        raise ValueError(
            "adapter command overrides were not requested: " + ", ".join(unknown_overrides)
        )

    for adapter_id in requested:
        assert isinstance(adapter_id, str)
        row = registry.get(adapter_id)
        if row is None:
            raise ValueError(f"adapter {adapter_id} is not registered")

        if adapter_id in overrides:
            envelope.add(execute_adapter(overrides[adapter_id], core, oracle=adapter_id))
            continue

        declared_command = row["command"]
        assert isinstance(declared_command, list)
        if shutil.which(declared_command[0]) is None:
            envelope.add(OracleObservation(adapter_id, "unavailable", None))
            continue

        bridge = ADAPTERS / f"{adapter_id}_adapter.py"
        if not bridge.is_file():
            envelope.add(
                OracleObservation(
                    adapter_id,
                    "error",
                    None,
                    notes=(f"missing local adapter bridge: {bridge}",),
                )
            )
            continue
        command = [
            sys.executable,
            str(bridge),
            "--executable",
            shutil.which(declared_command[0]) or declared_command[0],
        ]
        envelope.add(execute_adapter(command, core, oracle=adapter_id))
    return envelope


def main() -> int:
    parser = argparse.ArgumentParser(description="Run optional CSS oracle adapters.")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument(
        "--adapter-command",
        action="append",
        default=[],
        metavar="ID=JSON_ARGV",
        help="Override a requested adapter command with an explicit JSON argv array.",
    )
    args = parser.parse_args()

    try:
        payload = validate_payload(load_json(args.input))
        overrides = parse_overrides(args.adapter_command)
        envelope = run(payload, overrides)
    except ValueError as error:
        print(
            json.dumps(
                {
                    "classification": "error",
                    "errors": [str(error)],
                    "observations": [],
                },
                indent=2,
                sort_keys=True,
            )
        )
        return 1

    report = envelope.to_dict()
    print(json.dumps(report, indent=2, sort_keys=True))
    return 1 if report["classification"] == "error" else 0


if __name__ == "__main__":
    raise SystemExit(main())
