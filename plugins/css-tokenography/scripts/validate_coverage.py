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
        return True
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


def cli_names_tool(plugin: Path, artifact: str, name: str) -> bool:
    command = shlex.split(artifact)
    if "--tool" not in command:
        return True
    command[0] = str(plugin / command[0])
    result = subprocess.run(
        [sys.executable, *command, "--help"],
        text=True,
        capture_output=True,
        check=False,
    )
    return result.returncode == 0 and name in result.stdout


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
        if not isinstance(artifact, str) or not artifact_path(plugin, artifact).is_file():
            errors.append(f"tool {url} has missing artifact {artifact!r}")
        status = entry.get("status")
        if status not in ALLOWED_TOOL_STATUSES:
            errors.append(f"tool {url} has unsupported status {status!r}")
        if status != "procedural":
            fixture = entry.get("validation_fixture")
            if not isinstance(fixture, str) or not fixture_resolves(plugin, fixture):
                errors.append(f"tool {url} has unresolved validation evidence {fixture!r}")
            if isinstance(artifact, str) and isinstance(url, str) and not cli_names_tool(plugin, artifact, tool_name(url)):
                errors.append(f"tool {url} is not an available CLI choice in {artifact!r}")
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
