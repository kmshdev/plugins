#!/usr/bin/env python3
"""Validate css-tokenography coverage using fixture-driven CLI evidence."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path
from typing import Any


ALLOWED_TOOL_STATUSES = {"implemented-full", "implemented-core", "serializer-only", "procedural"}


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path}: {error}") from error


def is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and bool(value.strip())


def is_path_under(plugin: Path, value: Any, directory: Path) -> bool:
    if not is_non_empty_string(value):
        return False
    relative = Path(value)
    if relative.is_absolute():
        return False
    path = (plugin / relative).resolve()
    root = directory.resolve()
    return path != root and path.is_relative_to(root)


def owner_cli_path(plugin: Path, owner: Any, value: Any, *, must_exist: bool) -> Path | None:
    if not is_non_empty_string(owner) or not is_non_empty_string(value):
        return None
    if not is_path_under(plugin, value, plugin / "skills" / owner / "scripts"):
        return None
    path = plugin / value
    if path.suffix != ".py" or (must_exist and not path.is_file()):
        return None
    return path


def non_empty_string_array(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(is_non_empty_string(item) for item in value)
    )


def coverage_gap_errors(plugin: Path, owner: Any, value: Any) -> list[str]:
    if not isinstance(value, dict):
        return ["requires a coverage_gap object"]

    errors: list[str] = []
    if not non_empty_string_array(value.get("missing_contract")):
        errors.append("coverage_gap missing_contract must be a non-empty array of strings")

    restoration_artifact = value.get("restoration_artifact")
    if owner_cli_path(plugin, owner, restoration_artifact, must_exist=False) is None:
        errors.append(
            f"coverage_gap restoration_artifact must be owner-bound under skills/{owner}/scripts/ and name a Python file"
        )

    restoration_tests = value.get("restoration_tests")
    if not non_empty_string_array(restoration_tests):
        errors.append("coverage_gap restoration_tests must be a non-empty array of paths")
    elif any(not is_path_under(plugin, path, plugin / "tests") for path in restoration_tests):
        errors.append("coverage_gap restoration_tests entries must be paths under tests/")

    if not non_empty_string_array(value.get("acceptance")):
        errors.append("coverage_gap acceptance must be a non-empty array of strings")
    return errors


def validation_fixture_error(plugin: Path, value: Any) -> str | None:
    if not is_path_under(plugin, value, plugin / "tests" / "fixtures"):
        return "must name a JSON object under tests/fixtures"
    path = plugin / value
    if path.suffix != ".json" or not path.is_file():
        return "must name a JSON object under tests/fixtures"
    try:
        fixture = load_json(path)
    except ValueError:
        return "must name a JSON object under tests/fixtures"
    return None if isinstance(fixture, dict) else "must name a JSON object under tests/fixtures"


def execute_validation_command(
    plugin: Path,
    artifact: str,
    fixture: str,
    value: Any,
) -> list[str]:
    if not isinstance(value, list) or not value or not all(is_non_empty_string(item) for item in value):
        return ["requires an explicit validation_command array of strings"]

    declared_artifact = "{plugin}/" + artifact
    if len(value) < 2 or value[1] != declared_artifact:
        return ["validation_command must invoke declared implementation artifact"]
    if value.count("{fixture}") != 1:
        return ["validation_command must invoke declared validation fixture"]

    command = [
        part.replace("{plugin}", str(plugin)).replace("{fixture}", str(plugin / fixture))
        for part in value
    ]
    try:
        result = subprocess.run(
            command,
            cwd=plugin,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        return [f"validation command failed to start: {error}"]
    if result.returncode != 0:
        return [f"validation command failed with exit {result.returncode}"]
    try:
        output = json.loads(result.stdout)
    except json.JSONDecodeError:
        output = None
    if not isinstance(output, dict):
        return ["validation command must emit a JSON object"]
    return []


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
    if len(set(guide_skills)) != len(guide_skills):
        errors.append("guide skills must be unique")
    if len(set(guide_urls)) != len(guide_urls):
        errors.append("guide URLs must be unique")
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

    skill_directories = sorted(path.parent for path in (plugin / "skills").glob("*/SKILL.md"))
    agent_files = sorted((plugin / "skills").glob("*/agents/openai.yaml"))
    if len(skill_directories) != 17:
        errors.append("plugin must contain exactly 17 skill directories")
    if len(agent_files) != 17:
        errors.append("plugin must contain exactly 17 agents/openai.yaml files")

    if not isinstance(tools, list) or len(tools) != 33:
        errors.append("tool-coverage.json must contain exactly 33 tool entries")
        tools = tools if isinstance(tools, list) else []
    tool_urls = [entry.get("url") for entry in tools if isinstance(entry, dict)]
    if len(set(tool_urls)) != len(tool_urls):
        errors.append("tool URLs must be unique")
    evidence = [
        entry.get("validation_fixture")
        for entry in tools
        if isinstance(entry, dict) and entry.get("status") != "procedural"
    ]
    if len(evidence) != len(set(evidence)):
        errors.append("non-procedural tools must name unique validation fixtures")

    required_tool_fields = {
        "url",
        "title",
        "category",
        "owner",
        "inputs",
        "outputs",
        "classification",
        "implementation_artifact",
        "validation_fixture",
        "validation_command",
        "status",
        "reason",
        "coverage_gap",
    }
    for entry in tools:
        if not isinstance(entry, dict):
            errors.append("tool entries must be objects")
            continue
        url = entry.get("url")
        missing_fields = sorted(required_tool_fields - set(entry))
        if missing_fields:
            errors.append(f"tool {url} missing fields: {', '.join(missing_fields)}")
        owner = entry.get("owner")
        if not isinstance(url, str) or not url.startswith("https://design.dev/tools/"):
            errors.append(f"invalid tool URL {url!r}")
        if owner not in guide_skills:
            errors.append(f"tool {url} has unknown owner {owner!r}")
        status = entry.get("status")
        if status not in ALLOWED_TOOL_STATUSES:
            errors.append(f"tool {url} has unsupported status {status!r}")
        if not is_non_empty_string(entry.get("reason")):
            errors.append(f"tool {url} requires a coverage reason")

        if status != "procedural":
            artifact = entry.get("implementation_artifact")
            artifact_path = owner_cli_path(plugin, owner, artifact, must_exist=True)
            if artifact_path is None:
                errors.append(f"tool {url} requires an owner-bound Python CLI")
            elif artifact_path.name == "design_tool.py":
                errors.append(f"tool {url} requires a standalone owner CLI, not shared design_tool.py")

            fixture = entry.get("validation_fixture")
            fixture_error = validation_fixture_error(plugin, fixture)
            if fixture_error:
                errors.append(f"tool {url} {fixture_error}")
            if (
                artifact_path is not None
                and artifact_path.name != "design_tool.py"
                and fixture_error is None
                and isinstance(artifact, str)
                and isinstance(fixture, str)
            ):
                for command_error in execute_validation_command(
                    plugin,
                    artifact,
                    fixture,
                    entry.get("validation_command"),
                ):
                    errors.append(f"tool {url} {command_error}")

        if status in {"procedural", "serializer-only"}:
            for gap_error in coverage_gap_errors(plugin, owner, entry.get("coverage_gap")):
                errors.append(f"tool {url} {gap_error}")

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
        "skills": len(skill_directories),
        "agents": len(agent_files),
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
        print(
            f"guides={report['guides']} tools={report['tools']} sources={report['sources']} "
            f"skills={report['skills']} agents={report['agents']}"
        )
        for error in report["errors"]:
            print(f"ERROR {error}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
