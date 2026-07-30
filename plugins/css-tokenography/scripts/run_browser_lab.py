#!/usr/bin/env python3
"""Run the optional CSS browser laboratory without installing anything.

The dependency-free wrapper is the public entry point.  It preflights the
private Playwright project, invokes its stable ``npm run lab`` script only when
the requested dependencies are already present, and validates the versioned
evidence report before exposing it to callers.
"""

from __future__ import annotations

import argparse
import json
import shlex
import shutil
import subprocess
from pathlib import Path
from typing import Sequence

from css_tokenography_core.laboratory import (
    LaboratoryContractError,
    failure_report,
    unavailable_report,
    validate_report,
)


PLUGIN = Path(__file__).resolve().parents[1]
LABORATORY = PLUGIN / "laboratory" / "browser"
DEFAULT_ENGINES = ("chromium", "firefox", "webkit")
KNOWN_ENGINES = frozenset(DEFAULT_ENGINES)


def parse_engines(value: str) -> tuple[str, ...]:
    engines = tuple(engine.strip().lower() for engine in value.split(",") if engine.strip())
    if not engines:
        raise ValueError("--engines must name at least one browser engine")
    unknown = sorted(set(engines) - KNOWN_ENGINES)
    if unknown:
        raise ValueError("unsupported browser engine(s): " + ", ".join(unknown))
    if len(engines) != len(set(engines)):
        raise ValueError("--engines must not contain duplicates")
    return engines


def parse_runner_command(value: str) -> list[str]:
    """Parse a test-only command override without running a shell."""

    try:
        parsed = json.loads(value)
    except json.JSONDecodeError:
        parsed = shlex.split(value)
    if (
        not isinstance(parsed, list)
        or not parsed
        or not all(isinstance(argument, str) and argument for argument in parsed)
    ):
        raise ValueError("--runner-command must be a non-empty shell-style command or JSON argv")
    return parsed


def _executable_present(command: str) -> bool:
    path = Path(command)
    if "/" in command or "\\" in command:
        return path.is_file()
    return shutil.which(command) is not None


def _browser_probe(laboratory: Path, engines: Sequence[str]) -> list[str]:
    """Ask already-installed Playwright where its browser executables are.

    The tiny ``node -e`` probe imports local packages only.  Unlike ``npx`` it
    has no package resolution/download path and does not install browsers.
    """

    script = (
        "const requested = JSON.parse(process.argv[1]);"
        "const pw = require('@playwright/test');"
        "const missing = requested.filter((name) => !pw[name].executablePath() || "
        "!require('fs').existsSync(pw[name].executablePath()));"
        "process.stdout.write(JSON.stringify({missing}));"
    )
    result = subprocess.run(
        ["node", "-e", script, json.dumps(list(engines))],
        cwd=laboratory,
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or "Playwright package could not be loaded"
        return [f"Playwright preflight failed: {detail}"]
    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError:
        return ["Playwright preflight returned invalid JSON"]
    missing = payload.get("missing") if isinstance(payload, dict) else None
    if not isinstance(missing, list) or not all(isinstance(item, str) for item in missing):
        return ["Playwright preflight returned an invalid browser list"]
    return [f"missing Playwright browser executable: {engine}" for engine in missing]


def preflight(
    laboratory: Path,
    engines: Sequence[str],
    *,
    runner_command: Sequence[str] | None = None,
) -> list[str]:
    """Return missing components; this function never mutates the environment."""

    if runner_command is not None:
        executable = runner_command[0]
        return [] if _executable_present(executable) else [f"missing runner executable: {executable}"]

    missing: list[str] = []
    if not laboratory.is_dir():
        missing.append(f"missing browser laboratory directory: {laboratory}")
    elif not (laboratory / "package.json").is_file():
        missing.append(f"missing browser laboratory package.json: {laboratory / 'package.json'}")
    if shutil.which("node") is None:
        missing.append("missing Node.js executable: node")
    if shutil.which("npm") is None:
        missing.append("missing npm executable: npm")
    if missing:
        return missing
    return _browser_probe(laboratory, engines)


def default_command(laboratory: Path, engines: Sequence[str], update_snapshots: bool) -> list[str]:
    command = [
        "npm",
        "--prefix",
        str(laboratory),
        "run",
        "lab",
        "--",
        "--engines",
        ",".join(engines),
        "--format",
        "json",
    ]
    if update_snapshots:
        command.append("--update-snapshots")
    return command


def override_command(
    command: Sequence[str], engines: Sequence[str], update_snapshots: bool
) -> list[str]:
    """Supply the same stable runner flags to an explicit fake/test runner."""

    result = [*command, "--engines", ",".join(engines), "--format", "json"]
    if update_snapshots:
        result.append("--update-snapshots")
    return result


def exit_code(report: dict[str, object]) -> int:
    release = report["release"]
    assert isinstance(release, dict)
    status = release["status"]
    assert isinstance(status, str)
    return {"pass": 0, "fail": 1, "unavailable": 2}[status]


def run(
    laboratory: Path,
    engines: Sequence[str],
    *,
    update_snapshots: bool = False,
    runner_command: Sequence[str] | None = None,
) -> dict[str, object]:
    missing = preflight(laboratory, engines, runner_command=runner_command)
    if missing:
        return unavailable_report("; ".join(missing))

    command = (
        override_command(runner_command, engines, update_snapshots)
        if runner_command is not None
        else default_command(laboratory, engines, update_snapshots)
    )
    try:
        result = subprocess.run(
            command,
            cwd=PLUGIN,
            text=True,
            capture_output=True,
            check=False,
        )
    except OSError as error:
        return unavailable_report(f"unable to execute browser laboratory: {error}")

    try:
        parsed = json.loads(result.stdout)
    except json.JSONDecodeError as error:
        detail = result.stderr.strip() or str(error)
        return failure_report(f"browser laboratory did not emit valid JSON: {detail}")
    try:
        report = validate_report(parsed)
    except LaboratoryContractError as error:
        return failure_report(f"browser laboratory protocol violation: {error}")

    # A non-zero runner with a passing payload is internally contradictory.  Do
    # not let an adapter manufacture a green release through its JSON alone.
    if result.returncode != 0 and exit_code(report) == 0:
        return failure_report(
            f"browser laboratory exited {result.returncode} despite a passing report"
        )
    return report


def human_report(report: dict[str, object]) -> str:
    release = report["release"]
    assert isinstance(release, dict)
    lines = [
        f"protocol={report['protocol']}",
        f"deterministic={report['deterministic']['status']}",  # type: ignore[index]
        f"browser={report['browser']['status']}",  # type: ignore[index]
        f"agentic={report['agentic']['status']}",  # type: ignore[index]
        f"release={release['status']}",
    ]
    reasons = release["reasons"]
    assert isinstance(reasons, list)
    lines.extend(f"reason={reason}" for reason in reasons)
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run the optional CSS Tokenography browser laboratory without installing dependencies."
    )
    parser.add_argument(
        "--engines",
        default=",".join(DEFAULT_ENGINES),
        help="Comma-separated browser engines (chromium, firefox, webkit).",
    )
    parser.add_argument("--format", choices=("json", "human"), default="human")
    parser.add_argument(
        "--update-snapshots",
        action="store_true",
        help="Request explicit screenshot baseline updates from the browser runner.",
    )
    parser.add_argument(
        "--runner-command",
        metavar="COMMAND",
        help="Test override as shell-style command text or a JSON argv array; never run through a shell.",
    )
    args = parser.parse_args()

    try:
        engines = parse_engines(args.engines)
        command = parse_runner_command(args.runner_command) if args.runner_command else None
    except ValueError as error:
        parser.error(str(error))

    report = run(
        LABORATORY,
        engines,
        update_snapshots=args.update_snapshots,
        runner_command=command,
    )
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    else:
        print(human_report(report))
    return exit_code(report)


if __name__ == "__main__":
    raise SystemExit(main())
