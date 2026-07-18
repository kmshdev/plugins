#!/usr/bin/env python3
"""Validate css-tokenography guide, tool, source, and artifact coverage."""

from __future__ import annotations

import argparse
import json
import re
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any


ALLOWED_TOOL_STATUSES = {"implemented-full", "implemented-core", "serializer-only", "procedural"}
MIN_REASON_CLAUSE_LENGTH = 32
PLACEHOLDER_REASON_RE = re.compile(r"\b(?:stuff|todo|later)\b|\bdo\s+it\b", re.IGNORECASE)
CONCRETE_RESTORATION_RE = re.compile(
    r"\bTask\s+[1-9]\d*\b|(?:tests|skills|scripts|references)/[A-Za-z0-9_.\-/]+"
)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path}: {error}") from error


def artifact_path(plugin: Path, value: str) -> Path:
    return plugin / value.split(" --tool ", 1)[0]


def tool_name(url: str) -> str:
    return url.rstrip("/").rsplit("/", 1)[-1]


def evidence_kind(plugin: Path, value: str) -> str | None:
    relative_path, separator, anchor = value.partition("#")
    path = plugin / relative_path
    if not path.is_file():
        return None
    if not separator:
        fixture_root = (plugin / "tests" / "fixtures").resolve()
        if path.suffix != ".json" or not path.resolve().is_relative_to(fixture_root):
            return None
        try:
            return "fixture" if isinstance(load_json(path), dict) else None
        except ValueError:
            return None
    test_root = (plugin / "tests").resolve()
    if path.suffix != ".py" or not path.resolve().is_relative_to(test_root):
        return None
    class_name, dot, method_name = anchor.partition(".")
    if not dot or not method_name.startswith("test_"):
        return None
    return "unittest"


def run_artifact(plugin: Path, artifact: str, *args: str) -> subprocess.CompletedProcess[str] | None:
    try:
        command = shlex.split(artifact)
    except ValueError:
        return None
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


def run_unittest_evidence(plugin: Path, evidence: str) -> subprocess.CompletedProcess[str]:
    relative_path, _, anchor = evidence.partition("#")
    module = Path(relative_path).with_suffix("").as_posix().replace("/", ".")
    return subprocess.run(
        [sys.executable, "-m", "unittest", f"{module}.{anchor}"],
        cwd=plugin,
        text=True,
        capture_output=True,
        check=False,
    )


def downgrade_reason_errors(value: Any) -> list[str]:
    errors: list[str] = []
    if not isinstance(value, str):
        return ["requires non-empty 'Missing semantic contract:' and 'Restoration task:' clauses"]
    missing_prefix = "Missing semantic contract:"
    restoration_prefix = "Restoration task:"
    if not value.startswith(missing_prefix) or restoration_prefix not in value:
        return ["requires non-empty 'Missing semantic contract:' and 'Restoration task:' clauses"]
    missing_contract, restoration_task = value[len(missing_prefix):].split(restoration_prefix, 1)
    missing_contract = missing_contract.strip()
    restoration_task = restoration_task.strip()
    if not missing_contract or not restoration_task:
        return ["requires non-empty 'Missing semantic contract:' and 'Restoration task:' clauses"]
    if PLACEHOLDER_REASON_RE.search(missing_contract) or PLACEHOLDER_REASON_RE.search(restoration_task):
        errors.append("contains placeholder vocabulary such as stuff/TODO/later/do it")
    if len(missing_contract) < MIN_REASON_CLAUSE_LENGTH or len(restoration_task) < MIN_REASON_CLAUSE_LENGTH:
        errors.append(f"requires minimum detail of {MIN_REASON_CLAUSE_LENGTH} characters per clause")
    if not CONCRETE_RESTORATION_RE.search(restoration_task):
        errors.append("restoration clause must name a concrete Task N or artifact/test path")
    return errors


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
            evidence_type = evidence_kind(plugin, fixture) if isinstance(fixture, str) else None
            if evidence_type is None:
                errors.append(f"tool {url} has unresolved validation evidence {fixture!r}")
                if isinstance(fixture, str) and "#" not in fixture:
                    errors.append(f"tool {url} unanchored evidence must be a JSON object under tests/fixtures")
            if artifact_exists and isinstance(artifact, str):
                try:
                    command = shlex.split(artifact)
                except ValueError:
                    command = []
                help_result = run_artifact(plugin, artifact, "--help")
                if help_result is None or help_result.returncode != 0:
                    errors.append(f"tool {url} artifact {artifact!r} does not support --help")
                slug = tool_name(url) if isinstance(url, str) else ""
                tool_positions = [index for index, part in enumerate(command) if part == "--tool"]
                if tool_positions:
                    exact_tool_binding = (
                        len(tool_positions) == 1
                        and tool_positions[0] + 1 < len(command)
                        and command[tool_positions[0] + 1] == slug
                    )
                    if not exact_tool_binding:
                        errors.append(f"tool {url} artifact requires exact --tool {slug} binding")
                elif evidence_type == "unittest":
                    errors.append(f"tool {url} anchored evidence requires exact --tool {slug} binding")
                if evidence_type == "fixture" and isinstance(fixture, str):
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
                elif evidence_type == "unittest" and isinstance(fixture, str):
                    unittest_result = run_unittest_evidence(plugin, fixture)
                    if unittest_result.returncode != 0:
                        errors.append(f"tool {url} exact unittest evidence failed: {fixture!r}")
        if status in {"procedural", "serializer-only"}:
            for reason_error in downgrade_reason_errors(entry.get("reason")):
                errors.append(f"tool {url} downgrade reason {reason_error}")
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
