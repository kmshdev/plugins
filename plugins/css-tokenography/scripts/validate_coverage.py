#!/usr/bin/env python3
"""Validate css-tokenography coverage using fixture-driven CLI evidence."""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


ALLOWED_TOOL_STATUSES = {"implemented-full", "implemented-core", "serializer-only", "procedural"}
REQUIRED_BROWSER_ENGINES = {"chromium", "firefox", "webkit"}


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


def file_digest(path: Path) -> bytes:
    return hashlib.sha256(path.read_bytes()).digest()


def shared_wrapper_reference_error(path: Path) -> str | None:
    try:
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    except (OSError, UnicodeError, SyntaxError) as error:
        return f"cannot be parsed for shared-wrapper isolation: {error}"

    for node in ast.walk(tree):
        if isinstance(node, ast.Import) and any(
            alias.name.rsplit(".", 1)[-1] == "design_tool" for alias in node.names
        ):
            return "must not reference shared design_tool.py"
        if isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module.rsplit(".", 1)[-1] == "design_tool" or any(
                alias.name == "design_tool" for alias in node.names
            ):
                return "must not reference shared design_tool.py"
        if (
            isinstance(node, ast.Constant)
            and isinstance(node.value, str)
            and "design_tool.py" in node.value
        ):
            return "must not reference shared design_tool.py"
    return None


def shared_wrapper_isolation_error(plugin: Path, path: Path) -> str | None:
    try:
        if path.stat().st_nlink != 1:
            return "canonical tool script link count must be 1"
        artifact_digest = file_digest(path)
        shared_digests = {
            file_digest(shared_path)
            for shared_path in plugin.glob("skills/*/scripts/design_tool.py")
            if shared_path.is_file()
        }
    except OSError as error:
        return f"cannot inspect canonical tool script: {error}"
    if artifact_digest in shared_digests:
        return "canonical tool script duplicates shared design_tool.py content"
    return shared_wrapper_reference_error(path)


def non_empty_string_array(value: Any) -> bool:
    return (
        isinstance(value, list)
        and bool(value)
        and all(is_non_empty_string(item) for item in value)
    )


def validate_browser_fixtures(
    plugin: Path,
    value: Any,
    *,
    guide_skills: list[Any],
    tool_urls: list[Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    errors: list[str] = []
    if not isinstance(value, list) or len(value) != 10:
        return [], ["browser-fixtures.json must contain exactly 10 fixture entries"]

    rows: list[dict[str, Any]] = []
    fixture_ids: list[str] = []
    for index, fixture in enumerate(value):
        if not isinstance(fixture, dict):
            errors.append(f"browser fixture {index} must be an object")
            continue
        rows.append(fixture)
        fixture_id = fixture.get("id")
        if not is_non_empty_string(fixture_id):
            errors.append(f"browser fixture {index} id must be a non-empty string")
            continue
        assert isinstance(fixture_id, str)
        fixture_ids.append(fixture_id)

        owner = fixture.get("owner")
        if owner not in guide_skills:
            errors.append(f"browser fixture {fixture_id} has unknown owner {owner!r}")
        urls = fixture.get("tool_urls")
        if not non_empty_string_array(urls):
            errors.append(f"browser fixture {fixture_id} tool_urls must be non-empty")
        elif any(url not in tool_urls for url in urls):
            errors.append(f"browser fixture {fixture_id} names an unknown tool URL")
        if not non_empty_string_array(fixture.get("claim_ids")):
            errors.append(f"browser fixture {fixture_id} claim_ids must be non-empty")
        if not non_empty_string_array(fixture.get("collectors")):
            errors.append(f"browser fixture {fixture_id} collectors must be non-empty")

        engines = fixture.get("required_engines")
        if (
            not non_empty_string_array(engines)
            or set(engines) != REQUIRED_BROWSER_ENGINES
            or len(engines) != len(REQUIRED_BROWSER_ENGINES)
        ):
            errors.append(
                f"browser fixture {fixture_id} must require chromium, firefox, and webkit exactly once"
            )
        if fixture.get("visual_baseline") is not True:
            errors.append(
                f"browser fixture {fixture_id} visual_baseline must be true"
            )
        standards = fixture.get("standards")
        if not non_empty_string_array(standards) or any(
            not url.startswith("https://") for url in standards
        ):
            errors.append(
                f"browser fixture {fixture_id} standards must be HTTPS URLs"
            )

        fixture_path = fixture.get("fixture")
        if not is_path_under(
            plugin, fixture_path, plugin / "laboratory" / "browser" / "fixtures"
        ):
            errors.append(
                f"browser fixture {fixture_id} path must be under laboratory/browser/fixtures"
            )
        elif not (plugin / fixture_path).is_file():
            errors.append(f"browser fixture {fixture_id} file is missing")

    if len(fixture_ids) != len(set(fixture_ids)):
        errors.append("browser fixture ids must be unique")
    return rows, errors


def browser_evidence_errors(
    value: Any, *, fixture_ids: set[str]
) -> list[str]:
    if not isinstance(value, dict):
        return ["browser_evidence must be an object"]
    if set(value) != {"protocol", "fixtures"}:
        return ["browser_evidence keys must be exactly protocol and fixtures"]
    if value.get("protocol") != "css-tokenography-browser-lab/v1":
        return ["browser_evidence protocol must be css-tokenography-browser-lab/v1"]
    fixtures = value.get("fixtures")
    if not non_empty_string_array(fixtures):
        return ["browser_evidence fixtures must be a non-empty array"]
    if len(fixtures) != len(set(fixtures)):
        return ["browser_evidence fixtures must not contain duplicates"]
    unknown = sorted(set(fixtures) - fixture_ids)
    if unknown:
        return [f"browser_evidence names unknown fixtures: {', '.join(unknown)}"]
    return []


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
    browser_fixtures_value = load_json(references / "browser-fixtures.json")
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
    if len(skill_directories) != 18:
        errors.append("plugin must contain exactly 18 skill directories: one router and 17 guide specialists")
    if len(agent_files) != 18:
        errors.append("plugin must contain exactly 18 agents/openai.yaml files")

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
        "browser_evidence",
    }

    browser_fixtures, browser_fixture_errors = validate_browser_fixtures(
        plugin,
        browser_fixtures_value,
        guide_skills=guide_skills,
        tool_urls=tool_urls,
    )
    errors.extend(browser_fixture_errors)
    browser_fixture_ids = {
        fixture_id
        for fixture in browser_fixtures
        if isinstance((fixture_id := fixture.get("id")), str)
    }
    fixture_ids_by_tool: dict[str, set[str]] = {}
    for fixture in browser_fixtures:
        fixture_id = fixture.get("id")
        urls = fixture.get("tool_urls")
        if not isinstance(fixture_id, str) or not isinstance(urls, list):
            continue
        for url in urls:
            if isinstance(url, str):
                fixture_ids_by_tool.setdefault(url, set()).add(fixture_id)

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

        browser_evidence = entry.get("browser_evidence")
        expected_browser_fixtures = fixture_ids_by_tool.get(str(url), set())
        if browser_evidence is None:
            if expected_browser_fixtures:
                errors.append(f"tool {url} must declare browser_evidence")
            if (
                status != "procedural"
                and entry.get("classification") == "browser-dependent"
            ):
                errors.append(
                    f"implemented browser-dependent tool {url} requires browser_evidence"
                )
        else:
            for browser_error in browser_evidence_errors(
                browser_evidence, fixture_ids=browser_fixture_ids
            ):
                errors.append(f"tool {url} {browser_error}")
            if isinstance(browser_evidence, dict):
                declared_fixtures = browser_evidence.get("fixtures")
                if (
                    isinstance(declared_fixtures, list)
                    and set(declared_fixtures) != expected_browser_fixtures
                ):
                    errors.append(
                        f"tool {url} browser_evidence fixtures must match browser-fixtures.json ownership"
                    )

        if status != "procedural":
            artifact = entry.get("implementation_artifact")
            artifact_candidate = plugin / artifact if isinstance(artifact, str) else None
            artifact_path = owner_cli_path(plugin, owner, artifact, must_exist=True)
            slug = url.rstrip("/").rsplit("/", 1)[-1] if isinstance(url, str) else ""
            canonical_name = slug.replace("-", "_") + ".py"
            if artifact_candidate is not None and artifact_candidate.is_symlink():
                errors.append(f"tool {url} canonical tool script must not be a symlink")
                artifact_path = None
            elif artifact_path is None:
                errors.append(f"tool {url} requires an owner-bound Python CLI")
            elif artifact_path.name == "design_tool.py":
                errors.append(f"tool {url} requires a standalone owner CLI, not shared design_tool.py")
                artifact_path = None
            elif artifact_path.name != canonical_name:
                errors.append(
                    f"tool {url} must use canonical tool script skills/{owner}/scripts/{canonical_name}"
                )
                artifact_path = None
            else:
                isolation_error = shared_wrapper_isolation_error(plugin, artifact_path)
                if isolation_error:
                    errors.append(f"tool {url} {isolation_error}")
                    artifact_path = None

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
        "browser_fixtures": len(browser_fixtures),
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
            f"skills={report['skills']} agents={report['agents']} "
            f"browser_fixtures={report['browser_fixtures']}"
        )
        for error in report["errors"]:
            print(f"ERROR {error}")
    return 1 if report["errors"] else 0


if __name__ == "__main__":
    raise SystemExit(main())
