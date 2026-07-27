#!/usr/bin/env python3
"""Evaluate CSS Tokenography routing through temporary Codex plugin installation."""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, Callable, Sequence


ROUTER = "css-tokenography"
MARKETPLACE = "kmshdev"
REMOTE_SOURCE = "kmshdev/plugins"
PROTOCOL = "css-tokenography-routing/v1"
Runner = Callable[[Sequence[str], Path | None], subprocess.CompletedProcess[str]]


class EvaluationError(RuntimeError):
    """Actionable routing evaluation failure."""


def default_runner(command: Sequence[str], cwd: Path | None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        list(command),
        cwd=cwd,
        text=True,
        capture_output=True,
        check=False,
    )


def run_checked(
    runner: Runner,
    command: Sequence[str],
    *,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[str]:
    result = runner(command, cwd)
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "no diagnostic output"
        raise EvaluationError(f"command failed ({' '.join(command)}): {detail}")
    return result


def load_json_output(result: subprocess.CompletedProcess[str], command: Sequence[str]) -> Any:
    try:
        return json.loads(result.stdout)
    except json.JSONDecodeError as error:
        raise EvaluationError(
            f"command emitted malformed JSON ({' '.join(command)}): {error}"
        ) from error


def snapshot_state(runner: Runner) -> dict[str, Any]:
    marketplace_command = ("codex", "plugin", "marketplace", "list", "--json")
    plugin_command = ("codex", "plugin", "list", "--json")
    marketplaces = load_json_output(
        run_checked(runner, marketplace_command), marketplace_command
    )
    plugins = load_json_output(run_checked(runner, plugin_command), plugin_command)
    marketplace_rows = marketplaces.get("marketplaces", []) if isinstance(marketplaces, dict) else []
    installed_rows = plugins.get("installed", []) if isinstance(plugins, dict) else []
    return {
        "marketplace": next(
            (
                row
                for row in marketplace_rows
                if isinstance(row, dict) and row.get("name") == MARKETPLACE
            ),
            None,
        ),
        "installed": [
            row
            for row in installed_rows
            if isinstance(row, dict) and row.get("marketplaceName") == MARKETPLACE
        ],
    }


def comparable_state(state: dict[str, Any]) -> dict[str, Any]:
    marketplace = state.get("marketplace")
    source = (
        marketplace.get("marketplaceSource")
        if isinstance(marketplace, dict)
        else None
    )
    installed = state.get("installed", [])
    return {
        "marketplace_source": source,
        "installed": sorted(
            (
                row.get("pluginId"),
                row.get("version"),
                row.get("enabled"),
                row.get("installed"),
            )
            for row in installed
            if isinstance(row, dict)
        ),
    }


def command_plan(repository: Path, cases: list[dict[str, Any]]) -> list[list[str]]:
    commands = [
        ["codex", "plugin", "marketplace", "remove", MARKETPLACE, "--json"],
        ["codex", "plugin", "marketplace", "add", str(repository), "--json"],
        ["codex", "plugin", "add", f"{ROUTER}@{MARKETPLACE}", "--json"],
    ]
    commands.extend(
        [
            [
                "codex",
                "exec",
                "--ephemeral",
                "--json",
                "--sandbox",
                "read-only",
                "<routing-eval-prompt>",
            ]
            for _case in cases
        ]
    )
    commands.extend(
        [
            ["codex", "plugin", "remove", f"{ROUTER}@{MARKETPLACE}", "--json"],
            ["codex", "plugin", "marketplace", "remove", MARKETPLACE, "--json"],
            [
                "codex",
                "plugin",
                "marketplace",
                "add",
                REMOTE_SOURCE,
                "--ref",
                "main",
                "--json",
            ],
        ]
    )
    return commands


def response_schema() -> dict[str, Any]:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "type": "object",
        "additionalProperties": False,
        "required": [
            "protocol",
            "selected_skills",
            "disclosure",
            "semantic_retry",
        ],
        "properties": {
            "protocol": {"type": "string"},
            "selected_skills": {
                "type": "array",
                "items": {"type": "string", "pattern": "^[a-z0-9-]+$"},
            },
            "disclosure": {"type": "string"},
            "semantic_retry": {"type": "boolean"},
        },
    }


def eval_prompt(case: dict[str, Any], specialists: Sequence[str]) -> str:
    mode = case["mode"]
    protocol_instruction = (
        f'Set "protocol" to "{PROTOCOL}".'
        if mode == "implicit-router"
        else 'Set "protocol" to "explicit-specialist/v1".'
    )
    disclosure_instruction = (
        'Put the one required "CSS Tokenography route:" line only in the '
        '"disclosure" field. Use canonical $skill-name tokens in that line.'
        if mode == "implicit-router"
        else 'Set "disclosure" to an empty string; use only the explicitly named specialist.'
    )
    emission_instruction = (
        "Do not emit a provisional disclosure or structured response before "
        "those reads finish. Emit the routing disclosure exactly once, in the "
        "final structured result only."
        if mode == "implicit-router"
        else "Do not emit any routing disclosure or provisional structured response."
    )
    evaluation_kind = (
        "This is a router contract probe."
        if mode == "implicit-router"
        else "This is an explicit specialist contract probe."
    )
    allowed = ", ".join(specialists)
    return (
        f"{case['prompt']}\n\n"
        f"{evaluation_kind} Complete the semantic selection once. "
        f"{protocol_instruction} {disclosure_instruction} "
        f'The only canonical specialist names are: {allowed}. '
        'In "selected_skills", list only selected canonical specialist names '
        'without "$"; never include the router, plugin name, marketplace name, '
        'display labels, aliases, or topic groups. Read each selected sibling '
        f"SKILL.md as required, but do not edit files. {emission_instruction} "
        'Set "semantic_retry" to false and return only that structured result.'
    )


def token_usage(events: list[dict[str, Any]]) -> dict[str, int]:
    totals: dict[str, int] = {}

    def visit(value: Any) -> None:
        if isinstance(value, dict):
            for key, child in value.items():
                normalized = key.casefold()
                if "token" in normalized and isinstance(child, int) and not isinstance(child, bool):
                    totals[key] = max(totals.get(key, 0), child)
                else:
                    visit(child)
        elif isinstance(value, list):
            for child in value:
                visit(child)

    visit(events)
    return dict(sorted(totals.items()))


def parse_events(raw: str) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for line_number, line in enumerate(raw.splitlines(), start=1):
        if not line.strip():
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError as error:
            raise EvaluationError(f"invalid JSONL event at line {line_number}: {error}") from error
        if not isinstance(event, dict):
            raise EvaluationError(f"JSONL event at line {line_number} is not an object")
        events.append(event)
    if not events:
        raise EvaluationError("Codex emitted no JSONL events")
    return events


def validate_result(
    case: dict[str, Any],
    payload: Any,
    events: list[dict[str, Any]],
) -> list[str]:
    errors: list[str] = []
    if not isinstance(payload, dict):
        return ["final structured output is not an object"]
    selected = payload.get("selected_skills")
    if not isinstance(selected, list) or not all(isinstance(item, str) for item in selected):
        return ["selected_skills is not a string array"]
    if len(selected) != len(set(selected)):
        errors.append("selected_skills contains duplicates")
    required = set(case["required_skills"])
    forbidden = set(case["forbidden_skills"])
    missing = sorted(required - set(selected))
    present_forbidden = sorted(forbidden & set(selected))
    if missing:
        errors.append(f"missing required skills: {missing}")
    if present_forbidden:
        errors.append(f"selected forbidden skills: {present_forbidden}")
    if ROUTER in selected:
        errors.append("router selected itself recursively")
    command_evidence: list[str] = []
    agent_messages: list[str] = []
    for event in events:
        item = event.get("item")
        if event.get("type") != "item.completed" or not isinstance(item, dict):
            continue
        if item.get("type") == "command_execution":
            command_evidence.extend(
                value
                for value in (item.get("command"), item.get("aggregated_output"))
                if isinstance(value, str)
            )
        elif item.get("type") == "agent_message" and isinstance(item.get("text"), str):
            agent_messages.append(item["text"])
    read_evidence = "\n".join(command_evidence)
    for skill in selected:
        if (
            f"/skills/{skill}/SKILL.md" not in read_evidence
            and f"name: {skill}" not in read_evidence
        ):
            errors.append(f"missing SKILL.md read evidence for {skill}")
    if payload.get("semantic_retry") is not False:
        errors.append("semantic_retry must be false")
    disclosure = payload.get("disclosure")
    disclosure_count = sum(
        message.count("CSS Tokenography route:") for message in agent_messages
    )
    if case["mode"] == "implicit-router":
        if payload.get("protocol") != PROTOCOL:
            errors.append(f"protocol must be {PROTOCOL}")
        if not isinstance(disclosure, str) or disclosure.count("CSS Tokenography route:") != 1:
            errors.append("implicit case must contain exactly one routing disclosure")
        if disclosure_count != 1:
            errors.append(
                "implicit session must emit exactly one routing disclosure; "
                f"found {disclosure_count}"
            )
    else:
        if disclosure != "":
            errors.append("explicit specialist case must not contain a routing disclosure")
        if disclosure_count != 0:
            errors.append(
                "explicit specialist session must emit no routing disclosure; "
                f"found {disclosure_count}"
            )
    return errors


@dataclass
class EvaluationRun:
    case: dict[str, Any]
    command: list[str]
    output_path: Path
    events_path: Path
    duration_seconds: float
    infrastructure_attempts: int
    payload: dict[str, Any] | None
    tokens: dict[str, int]
    errors: list[str]

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.case["id"],
            "mode": self.case["mode"],
            "command": self.command,
            "duration_seconds": round(self.duration_seconds, 3),
            "infrastructure_attempts": self.infrastructure_attempts,
            "output_path": str(self.output_path),
            "events_path": str(self.events_path),
            "tokens": self.tokens,
            "result": self.payload,
            "errors": self.errors,
            "status": "pass" if not self.errors else "fail",
        }


def run_case(
    runner: Runner,
    repository: Path,
    case: dict[str, Any],
    output_dir: Path,
    schema_path: Path,
    specialists: Sequence[str],
) -> EvaluationRun:
    final_path = output_dir / f"{case['id']}.final.json"
    events_path = output_dir / f"{case['id']}.events.jsonl"
    command = [
        "codex",
        "exec",
        "--ephemeral",
        "--json",
        "--sandbox",
        "read-only",
        "--skip-git-repo-check",
        "-C",
        str(repository),
        "--output-schema",
        str(schema_path),
        "--output-last-message",
        str(final_path),
        eval_prompt(case, specialists),
    ]
    started = time.monotonic()
    last_error: EvaluationError | None = None
    for attempt in (1, 2):
        result = runner(command, repository)
        try:
            if result.returncode != 0:
                raise EvaluationError(
                    result.stderr.strip() or result.stdout.strip() or "Codex execution failed"
                )
            events = parse_events(result.stdout)
            try:
                payload = json.loads(final_path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as error:
                raise EvaluationError(f"unable to read final structured output: {error}") from error
        except EvaluationError as error:
            last_error = error
            if attempt == 1:
                continue
            return EvaluationRun(
                case, command, final_path, events_path,
                time.monotonic() - started, attempt, None, {},
                [f"infrastructure failure after one retry: {error}"],
            )
        events_path.write_text(result.stdout, encoding="utf-8")
        errors = validate_result(case, payload, events)
        return EvaluationRun(
            case, command, final_path, events_path,
            time.monotonic() - started, attempt, payload, token_usage(events), errors,
        )
    raise AssertionError(last_error)


def load_cases(path: Path) -> list[dict[str, Any]]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise EvaluationError(f"unable to load routing cases: {error}") from error
    if not isinstance(value, list):
        raise EvaluationError("routing cases must be a JSON array")
    return value


def evaluate(
    repository: Path,
    plugin: Path,
    output_dir: Path,
    runner: Runner = default_runner,
) -> dict[str, Any]:
    cases = load_cases(
        plugin / "skills" / ROUTER / "assets" / "routing-eval-cases.json"
    )
    output_dir.mkdir(parents=True, exist_ok=False)
    schema_path = output_dir / "routing-result.schema.json"
    schema_path.write_text(json.dumps(response_schema(), indent=2) + "\n", encoding="utf-8")
    specialists = sorted(
        path.parent.name
        for path in (plugin / "skills").glob("*/SKILL.md")
        if path.parent.name != ROUTER
    )
    before = snapshot_state(runner)
    unrelated = [
        row.get("pluginId")
        for row in before["installed"]
        if row.get("pluginId") != f"{ROUTER}@{MARKETPLACE}"
    ]
    if unrelated:
        raise EvaluationError(
            f"refusing to remove marketplace with unrelated installed plugins: {unrelated}"
        )
    candidate_was_installed = any(
        row.get("pluginId") == f"{ROUTER}@{MARKETPLACE}"
        for row in before["installed"]
    )
    runs: list[EvaluationRun] = []
    primary_error: Exception | None = None
    restoration_errors: list[str] = []
    mutated = False
    try:
        if candidate_was_installed:
            run_checked(
                runner,
                ("codex", "plugin", "remove", f"{ROUTER}@{MARKETPLACE}", "--json"),
            )
        if before["marketplace"] is not None:
            run_checked(
                runner,
                ("codex", "plugin", "marketplace", "remove", MARKETPLACE, "--json"),
            )
        mutated = True
        run_checked(
            runner,
            ("codex", "plugin", "marketplace", "add", str(repository), "--json"),
        )
        run_checked(
            runner,
            ("codex", "plugin", "add", f"{ROUTER}@{MARKETPLACE}", "--json"),
        )
        for case in cases:
            runs.append(
                run_case(
                    runner,
                    repository,
                    case,
                    output_dir,
                    schema_path,
                    specialists,
                )
            )
    except Exception as error:
        primary_error = error
    finally:
        if mutated:
            cleanup_commands = (
                ("codex", "plugin", "remove", f"{ROUTER}@{MARKETPLACE}", "--json"),
                ("codex", "plugin", "marketplace", "remove", MARKETPLACE, "--json"),
            )
            for command in cleanup_commands:
                result = runner(command, None)
                if result.returncode != 0:
                    restoration_errors.append(
                        f"cleanup failed ({' '.join(command)}): "
                        f"{result.stderr.strip() or result.stdout.strip()}"
                    )
            if before["marketplace"] is not None:
                restore = (
                    "codex", "plugin", "marketplace", "add",
                    REMOTE_SOURCE, "--ref", "main", "--json",
                )
                result = runner(restore, None)
                if result.returncode != 0:
                    restoration_errors.append(
                        f"marketplace restoration failed: "
                        f"{result.stderr.strip() or result.stdout.strip()}"
                    )
                elif candidate_was_installed:
                    reinstall = (
                        "codex", "plugin", "add", f"{ROUTER}@{MARKETPLACE}", "--json",
                    )
                    result = runner(reinstall, None)
                    if result.returncode != 0:
                        restoration_errors.append(
                            f"plugin restoration failed: "
                            f"{result.stderr.strip() or result.stdout.strip()}"
                        )
            try:
                after = snapshot_state(runner)
            except EvaluationError as error:
                restoration_errors.append(f"unable to verify restored state: {error}")
            else:
                if comparable_state(after) != comparable_state(before):
                    restoration_errors.append(
                        "restored marketplace/plugin state differs from the snapshot"
                    )

    if primary_error is not None:
        restoration_errors.insert(0, str(primary_error))
    case_reports = [run.to_dict() for run in runs]
    passed = len(case_reports) == len(cases) and all(
        report["status"] == "pass" for report in case_reports
    )
    report = {
        "protocol": "css-tokenography-routing-evaluation/v1",
        "cases": case_reports,
        "case_count": len(cases),
        "passed": sum(report["status"] == "pass" for report in case_reports),
        "pass_rate": 1.0 if passed else (
            sum(report["status"] == "pass" for report in case_reports) / len(cases)
            if cases else 0.0
        ),
        "state_restored": not restoration_errors,
        "errors": restoration_errors,
        "status": "pass" if passed and not restoration_errors else "fail",
    }
    (output_dir / "summary.json").write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return report


def parser() -> argparse.ArgumentParser:
    script = Path(__file__).resolve()
    plugin = script.parents[3]
    repository = plugin.parents[1]
    codex_home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
    stamp = datetime.now(UTC).strftime("%Y%m%dT%H%M%SZ")
    result = argparse.ArgumentParser(
        description=(
            "Dry-run or execute fresh-session CSS Tokenography routing evaluations. "
            "Marketplace state changes require --apply and are restored in finally."
        )
    )
    result.add_argument("--apply", action="store_true", help="Run temporary installation and live evals")
    result.add_argument("--plugin", type=Path, default=plugin)
    result.add_argument("--repository", type=Path, default=repository)
    result.add_argument(
        "--output-dir",
        type=Path,
        default=codex_home / "work-notes" / "css-tokenography" / "router-evals" / stamp,
    )
    result.add_argument("--format", choices=("human", "json"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    cases = load_cases(
        args.plugin / "skills" / ROUTER / "assets" / "routing-eval-cases.json"
    )
    if not args.apply:
        report = {
            "mode": "dry-run",
            "repository": str(args.repository.resolve()),
            "plugin": str(args.plugin.resolve()),
            "case_count": len(cases),
            "commands": command_plan(args.repository.resolve(), cases),
            "marketplace_mutated": False,
        }
    else:
        try:
            report = evaluate(
                args.repository.resolve(),
                args.plugin.resolve(),
                args.output_dir.resolve(),
            )
        except EvaluationError as error:
            report = {"mode": "apply", "status": "fail", "errors": [str(error)]}
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    elif not args.apply:
        print(f"Dry run: {len(cases)} cases; marketplace state unchanged.")
        for command in report["commands"]:
            print(" ".join(command))
    else:
        print(
            f"Routing evaluation: {report.get('status', 'fail').upper()} "
            f"({report.get('passed', 0)}/{report.get('case_count', len(cases))})"
        )
        for error in report.get("errors", []):
            print(f"- {error}")
    return 0 if report.get("status", "pass") == "pass" else 1


if __name__ == "__main__":
    raise SystemExit(main())
