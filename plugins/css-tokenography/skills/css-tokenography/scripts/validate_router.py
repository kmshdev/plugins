#!/usr/bin/env python3
"""Validate the CSS Tokenography router bundle without third-party dependencies."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


ROUTER = "css-tokenography"
REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "scripts/validate_router.py",
    "scripts/evaluate_routes.py",
    "references/routing-map.md",
    "references/success-rubric.md",
    "assets/routing-eval-cases.json",
    "assets/routing-summary-template.md",
)
REQUIRED_CASE_IDS = {
    "grid-single-topic",
    "performance-single-topic",
    "dark-mode-and-tokens",
    "transform-and-transition",
    "ambiguous-visual-polish",
    "responsive-component-layout",
    "explicit-css-selectors",
    "explicit-web-typography",
}
SKILL_PATTERN = re.compile(r"^\s*-\s+`\$([a-z0-9-]+)`\s+—", re.MULTILINE)


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"Unable to read {path}: {error}") from error


def parse_openai_yaml(path: Path) -> tuple[str | None, bool | None]:
    """Read the two validated scalar fields from the deliberately small YAML file."""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except OSError:
        return None, None
    default_prompt: str | None = None
    implicit: bool | None = None
    section: str | None = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        if not line.startswith((" ", "\t")) and stripped.endswith(":"):
            section = stripped[:-1]
            continue
        if section == "interface" and stripped.startswith("default_prompt:"):
            default_prompt = stripped.split(":", 1)[1].strip().strip("\"'")
        if section == "policy" and stripped.startswith("allow_implicit_invocation:"):
            raw = stripped.split(":", 1)[1].strip().casefold()
            implicit = {"true": True, "false": False}.get(raw)
    return default_prompt, implicit


def validate(plugin: Path) -> dict[str, Any]:
    plugin = plugin.resolve()
    skills_root = plugin / "skills"
    router_root = skills_root / ROUTER
    errors: list[str] = []

    for relative in REQUIRED_FILES:
        if not (router_root / relative).is_file():
            errors.append(f"missing router bundle file: skills/{ROUTER}/{relative}")

    skill_names = sorted(
        path.parent.name for path in skills_root.glob("*/SKILL.md") if path.is_file()
    )
    agent_files = sorted(skills_root.glob("*/agents/openai.yaml"))
    if len(skill_names) != 18:
        errors.append(f"plugin must contain exactly 18 skills; found {len(skill_names)}")
    if len(agent_files) != 18:
        errors.append(
            f"plugin must contain exactly 18 agents/openai.yaml files; found {len(agent_files)}"
        )
    if ROUTER not in skill_names:
        errors.append(f"router skill is missing: {ROUTER}")

    try:
        guide_rows = load_json(plugin / "references" / "guide-coverage.json")
    except ValueError as error:
        errors.append(str(error))
        guide_rows = []
    guide_skills = [
        row.get("skill") for row in guide_rows if isinstance(row, dict)
    ] if isinstance(guide_rows, list) else []
    if not isinstance(guide_rows, list) or len(guide_rows) != 17:
        errors.append("guide inventory must contain exactly 17 specialist rows")
    if len(set(guide_skills)) != len(guide_skills):
        errors.append("guide inventory contains duplicate specialists")
    if ROUTER in guide_skills:
        errors.append("guide inventory must not contain the router")
    expected_specialists = set(guide_skills)
    actual_specialists = set(skill_names) - {ROUTER}
    if expected_specialists != actual_specialists:
        missing = sorted(expected_specialists - actual_specialists)
        extra = sorted(actual_specialists - expected_specialists)
        errors.append(
            f"guide specialist inventory differs from skill directories; missing={missing}, extra={extra}"
        )

    implicit_skills: list[str] = []
    for skill_name in skill_names:
        yaml_path = skills_root / skill_name / "agents" / "openai.yaml"
        default_prompt, implicit = parse_openai_yaml(yaml_path)
        if implicit is True:
            implicit_skills.append(skill_name)
        elif implicit is None:
            errors.append(f"{skill_name} omits an explicit allow_implicit_invocation policy")
        if skill_name == ROUTER:
            if default_prompt is None or "$css-tokenography" not in default_prompt:
                errors.append("router default prompt must mention $css-tokenography")
            if implicit is not True:
                errors.append("router must permit implicit invocation")
        elif implicit is not False:
            errors.append(f"specialist {skill_name} must disable implicit invocation")
    if implicit_skills != [ROUTER]:
        errors.append(
            f"exactly the router must permit implicit invocation; found {implicit_skills}"
        )

    map_path = router_root / "references" / "routing-map.md"
    try:
        mapped = SKILL_PATTERN.findall(map_path.read_text(encoding="utf-8"))
    except OSError as error:
        errors.append(f"unable to read routing map: {error}")
        mapped = []
    counts = Counter(mapped)
    duplicates = sorted(name for name, count in counts.items() if count > 1)
    if duplicates:
        errors.append(f"routing map duplicates specialists: {duplicates}")
    if ROUTER in mapped:
        errors.append("routing map must not select the router")
    if set(mapped) != expected_specialists:
        missing = sorted(expected_specialists - set(mapped))
        extra = sorted(set(mapped) - expected_specialists)
        errors.append(f"routing map differs from specialists; missing={missing}, extra={extra}")

    cases_path = router_root / "assets" / "routing-eval-cases.json"
    try:
        cases = load_json(cases_path)
    except ValueError as error:
        errors.append(str(error))
        cases = []
    if not isinstance(cases, list):
        errors.append("routing eval cases must be a JSON array")
        cases = []
    case_ids: list[str] = []
    known = set(skill_names)
    valid_modes = {"implicit-router", "explicit-specialist"}
    for index, case in enumerate(cases):
        label = f"eval case {index}"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        case_id = case.get("id")
        mode = case.get("mode")
        prompt = case.get("prompt")
        required = case.get("required_skills")
        forbidden = case.get("forbidden_skills")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{label} requires a non-empty id")
        else:
            case_ids.append(case_id)
            label = f"eval case {case_id}"
        if mode not in valid_modes:
            errors.append(f"{label} has unknown mode {mode!r}")
        if not isinstance(prompt, str) or not prompt.strip():
            errors.append(f"{label} requires a prompt")
        for field_name, values in (("required_skills", required), ("forbidden_skills", forbidden)):
            if not isinstance(values, list) or not values or not all(
                isinstance(value, str) and value for value in values
            ):
                errors.append(f"{label} {field_name} must be a non-empty string array")
                continue
            if len(values) != len(set(values)):
                errors.append(f"{label} {field_name} contains duplicates")
            unknown = sorted(set(values) - known)
            if unknown:
                errors.append(f"{label} {field_name} contains unknown skills: {unknown}")
        if isinstance(required, list) and isinstance(forbidden, list):
            overlap = sorted(set(required) & set(forbidden))
            if overlap:
                errors.append(f"{label} required and forbidden skills overlap: {overlap}")
        if mode == "implicit-router" and isinstance(required, list) and ROUTER in required:
            errors.append(f"{label} must not select the router recursively")
        if mode == "explicit-specialist" and isinstance(forbidden, list) and ROUTER not in forbidden:
            errors.append(f"{label} must forbid the router")

    duplicate_case_ids = sorted(
        case_id for case_id, count in Counter(case_ids).items() if count > 1
    )
    if duplicate_case_ids:
        errors.append(f"routing eval cases contain duplicate ids: {duplicate_case_ids}")
    if set(case_ids) != REQUIRED_CASE_IDS:
        missing = sorted(REQUIRED_CASE_IDS - set(case_ids))
        extra = sorted(set(case_ids) - REQUIRED_CASE_IDS)
        errors.append(f"routing eval classes differ; missing={missing}, extra={extra}")

    return {
        "protocol": "css-tokenography-router-validation/v1",
        "plugin": str(plugin),
        "router": ROUTER,
        "skills": len(skill_names),
        "guide_skills": len(guide_skills),
        "implicit_skills": implicit_skills,
        "mapped_specialists": len(mapped),
        "eval_cases": len(cases),
        "errors": errors,
        "status": "pass" if not errors else "fail",
    }


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser(
        description="Validate CSS Tokenography router structure, policies, map, and eval cases."
    )
    result.add_argument(
        "--plugin",
        type=Path,
        default=Path(__file__).resolve().parents[3],
        help="Plugin root (defaults to the containing css-tokenography plugin)",
    )
    result.add_argument("--format", choices=("human", "json"), default="human")
    return result


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    report = validate(args.plugin)
    if args.format == "json":
        print(json.dumps(report, indent=2, sort_keys=True))
    elif report["errors"]:
        print("CSS Tokenography router validation: FAIL")
        for error in report["errors"]:
            print(f"- {error}")
    else:
        print(
            "CSS Tokenography router validation: PASS "
            f"({report['skills']} skills, {report['guide_skills']} specialists, "
            f"{report['eval_cases']} eval cases)"
        )
    return 0 if not report["errors"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
