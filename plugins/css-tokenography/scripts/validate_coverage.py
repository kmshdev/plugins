#!/usr/bin/env python3
"""Validate css-tokenography guide, tool, source, and artifact coverage."""

from __future__ import annotations

import argparse
import ast
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


ALLOWED_TOOL_STATUSES = {"implemented-full", "implemented-core", "serializer-only", "procedural"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path}: {error}") from error


def artifact_path(plugin: Path, value: str) -> Path:
    return plugin / value.split(" --tool ", 1)[0]


def tool_name(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def fixture_resolves(plugin: Path, value: str) -> bool:
    relative_path, separator, anchor = value.partition("#")
    path = plugin / relative_path
    if not path.is_file():
        return False
    if not separator:
        fixture_root = (plugin / "tests" / "fixtures").resolve()
        if path.suffix != ".json" or not path.resolve().is_relative_to(fixture_root):
            return False
        try:
            return isinstance(load_json(path), dict)
        except ValueError:
            return False
    test_root = (plugin / "tests").resolve()
    if path.suffix != ".py" or not path.resolve().is_relative_to(test_root):
        return False
    class_name, dot, method_name = anchor.partition(".")
    if not dot or not method_name.startswith("test_"):
        return False
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, SyntaxError):
        return False
    return any(
        isinstance(node, ast.ClassDef)
        and node.name == class_name
        and any(
            isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            and member.name == method_name
            for member in node.body
        )
        for node in tree.body
    )


def run_artifact(plugin: Path, artifact: str, *args: str) -> subprocess.CompletedProcess[str] | None:
    command = shlex.split(artifact)
    if not command:
        return None
    command[0] = str(plugin / command[0])
    try:
        return subprocess.run(
            [sys.executable, *command, *args],
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError:
        return None


def structured_downgrade_reason(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    missing_prefix = "Missing semantic contract:"
    restoration_prefix = "Restoration task:"
    if not value.startswith(missing_prefix) or restoration_prefix not in value:
        return False
    missing_contract, restoration_task = value[len(missing_prefix):].split(restoration_prefix, 1)
    return bool(missing_contract.strip() and restoration_task.strip())


def validate(plugin: Path) -> dict[str, Any]:
    errors: list[str] = []
    references = plugin / "references"
    guides = load_json(references / "guide-coverage.json")
    tools = load_json(references / "tool-coverage.json")
    sources = load_json(references / "source-inventory.json")
    migration = load_json(references / "source-migration.json")

    if not isinstance(guides, list) or len(guides) != 17:
        errors.append("guide-coverage.json must contain exactly 17 guide entries")
        guides = guides if isinstance(guides, list) else []
    guide_skills = [entry.get("skill") for entry in guides if isinstance(entry, dict)]
    guide_urls = [entry.get("url") for entry in guides if isinstance(entry, dict)]
    if len(set(guide_skills)) != len(guide_skills): errors.append("guide skills must be unique")
    if len(set(guide_urls)) != len(guide_urls): errors.append("guide URLs must be unique")
    for entry in guides:
        if not isinstance(entry, dict):
            errors.append("guide entries must be objects")
            continue
        skill = entry.get("skill")
        url = entry.get("url")
        skill_file = plugin / "skills" / str(skill) / "SKILL.md"
        if not isinstance(url, str) or not url.startswith("https://design.dev/guides/"):
            errors.append(f"invalid guide URL for {skill}")
        if not skill_file.is_file():
            errors.append(f"missing skill file for {skill}")
        elif "TODO" in skill_file.read_text(encoding="utf-8"):
            errors.append(f"skill {skill} contains TODO placeholders")

    if not isinstance(tools, list) or len(tools) != 33:
        errors.append("tool-coverage.json must contain exactly 33 tool entries")
        tools = tools if isinstance(tools, list) else []
    tool_urls = [entry.get("url") for entry in tools if isinstance(entry, dict)]
    if len(set(tool_urls)) != len(tool_urls): errors.append("tool URLs must be unique")
    evidence = [entry.get("validation_fixture") for entry in tools if isinstance(entry, dict) and entry.get("status") != "procedural"]
    if len(evidence) != len(set(evidence)):
        errors.append("non-procedural tools must name unique validation evidence")
    required_tool_fields = {
        "url", "title", "category", "owner", "inputs", "outputs", "classification",
        "implementation_artifact", "validation_fixture", "status", "reason",
    }
    for entry in tools:
        if not isinstance(entry, dict):
            errors.append("tool entries must be objects")
            continue
        missing_fields = sorted(required_tool_fields - set(entry))
        if missing_fields: errors.append(f"tool {entry.get('url')} missing fields: {', '.join(missing_fields)}")
        url = entry.get("url")
        owner = entry.get("owner")
        if not isinstance(url, str) or not url.startswith("https://design.dev/tools/"):
            errors.append(f"invalid tool URL {url!r}")
        if owner not in guide_skills:
            errors.append(f"tool {url} has unknown owner {owner!r}")
        artifact = entry.get("implementation_artifact")
        artifact_exists = isinstance(artifact, str) and artifact_path(plugin, artifact).is_file()
        if not artifact_exists:
            errors.append(f"tool {url} has missing artifact {artifact!r}")
        status = entry.get("status")
        if status not in ALLOWED_TOOL_STATUSES:
            errors.append(f"tool {url} has unsupported status {status!r}")
        if status != "procedural":
            fixture = entry.get("validation_fixture")
            fixture_is_valid = isinstance(fixture, str) and fixture_resolves(plugin, fixture)
            if not fixture_is_valid:
                errors.append(f"tool {url} has unresolved validation evidence {fixture!r}")
                if isinstance(fixture, str) and "#" not in fixture:
                    errors.append(f"tool {url} unanchored evidence must be a JSON object under tests/fixtures")
            if artifact_exists and isinstance(artifact, str):
                command = shlex.split(artifact)
                help_result = run_artifact(plugin, artifact, "--help")
                if help_result is None or help_result.returncode != 0:
                    errors.append(f"tool {url} artifact {artifact!r} does not support --help")
                elif "--tool" in command and isinstance(url, str) and tool_name(url) not in help_result.stdout:
                    errors.append(f"tool {url} is not an available CLI choice in {artifact!r}")
                if artifact_path(plugin, artifact).suffix != ".py":
                    errors.append(f"tool {url} implementation artifact must name a Python CLI")
                if fixture_is_valid and isinstance(fixture, str) and "#" not in fixture:
                    fixture_result = run_artifact(
                        plugin,
                        artifact,
                        "--input",
                        str(plugin / fixture),
                        "--format",
                        "json",
                    )
                    try:
                        fixture_output = json.loads(fixture_result.stdout) if fixture_result is not None else None
                    except json.JSONDecodeError:
                        fixture_output = None
                    if fixture_result is None or fixture_result.returncode != 0 or not isinstance(fixture_output, dict):
                        errors.append(f"tool {url} artifact cannot consume validation fixture {fixture!r}")
        if status in {"procedural", "serializer-only"} and not structured_downgrade_reason(entry.get("reason")):
            errors.append(
                f"tool {url} downgrade reason requires non-empty "
                "'Missing semantic contract:' and 'Restoration task:' clauses"
            )
        if not entry.get("reason"):
            errors.append(f"tool {url} requires a coverage reason")

    source_entries = sources.get("sources") if isinstance(sources, dict) else None
    if not isinstance(source_entries, list) or len(source_entries) != 7:
        errors.append("source-inventory.json must contain seven source skills")
    if not isinstance(migration, list) or len(migration) != 7:
        errors.append("source-migration.json must cover seven source skills")
    elif any(not entry.get("sections") for entry in migration if isinstance(entry, dict)):
        errors.append("every source migration entry needs section dispositions")

    return {
        "plugin": str(plugin),
        "guides": len(guides),
        "tools": len(tools),
        "sources": len(source_entries) if isinstance(source_entries, list) else 0,
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate css-tokenography coverage matrices and artifacts.")
    parser.add_argument("--plugin", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--format", choices=("json", "human"), default="human")
    args = parser.parse_args()
    try:
        report = validate(args.plugin.resolve())
    except ValueError as error:
        print(f"coverage-validator: {error}")
        return 1
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(f"guides={report['guides']} tools={report['tools']} sources={report['sources']}")
        for error in report["errors"]: print(f"ERROR {error}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
