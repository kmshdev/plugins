#!/usr/bin/env python3
"""Validate docdev MDX frontmatter, structure, and portable-safety rules."""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any


ALLOWED_TYPES = {"development", "plan", "architecture", "library"}
ALLOWED_STATUSES = {"draft", "review", "approved", "deprecated"}
REQUIRED_FIELDS = {"title", "summary", "type", "status", "slug", "created", "updated", "audience", "owners", "tags", "evidence"}
REQUIRED_HEADINGS = {
    "development": {"context", "workflow", "verification", "failure modes"},
    "plan": {"outcome", "scope", "execution plan", "acceptance evidence"},
    "architecture": {"system boundary", "decisions", "runtime model", "verification"},
    "library": {"purpose", "installation", "api", "examples", "compatibility"},
}
PLACEHOLDER_RE = re.compile(r"\{\{[^}]+\}\}|\b(?:TODO|TBD)\b|lorem ipsum", re.IGNORECASE)
UNSAFE_RE = re.compile(r"<\s*script\b|\bon(?:load|error|click)\s*=|javascript\s*:", re.IGNORECASE)
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


@dataclass
class Result:
    path: Path
    errors: list[str]
    slug: str | None = None


def scalar(value: str) -> Any:
    value = value.strip()
    if value.startswith('"') and value.endswith('"'):
        return value[1:-1].replace('\\"', '"')
    if value.startswith("["):
        return json.loads(value)
    return value


def split_document(text: str) -> tuple[dict[str, Any], str]:
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        raise ValueError("frontmatter must begin on the first line with ---")
    try:
        end = next(index for index, line in enumerate(lines[1:], start=1) if line.strip() == "---")
    except StopIteration as error:
        raise ValueError("frontmatter is missing its closing ---") from error
    data: dict[str, Any] = {}
    for number, line in enumerate(lines[1:end], start=2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if ":" not in line:
            raise ValueError(f"frontmatter line {number} must be key: value")
        key, raw = line.split(":", 1)
        key = key.strip()
        if not re.fullmatch(r"[a-z][a-z0-9_-]*", key):
            raise ValueError(f"frontmatter line {number} has invalid key {key!r}")
        if key in data:
            raise ValueError(f"frontmatter field {key!r} is duplicated")
        try:
            data[key] = scalar(raw)
        except json.JSONDecodeError as error:
            raise ValueError(f"frontmatter field {key!r} must use JSON-compatible array syntax") from error
    return data, "\n".join(lines[end + 1 :])


def headings(body: str) -> list[tuple[int, str]]:
    found: list[tuple[int, str]] = []
    in_fence = False
    marker = ""
    for line in body.splitlines():
        stripped = line.lstrip()
        if stripped.startswith(("```", "~~~")):
            current = stripped[:3]
            if not in_fence:
                in_fence, marker = True, current
            elif current == marker:
                in_fence = False
            continue
        if in_fence:
            continue
        match = re.match(r"^(#{1,6})\s+(.+?)\s*#*\s*$", stripped)
        if match:
            found.append((len(match.group(1)), match.group(2).strip()))
    return found


def validate(path: Path) -> Result:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
        data, body = split_document(text)
    except (OSError, UnicodeError, ValueError) as error:
        return Result(path, [str(error)])

    missing = sorted(REQUIRED_FIELDS - data.keys())
    if missing:
        errors.append(f"missing frontmatter fields: {', '.join(missing)}")
    doc_type = data.get("type")
    if doc_type not in ALLOWED_TYPES:
        errors.append(f"type must be one of: {', '.join(sorted(ALLOWED_TYPES))}")
    if data.get("status") not in ALLOWED_STATUSES:
        errors.append(f"status must be one of: {', '.join(sorted(ALLOWED_STATUSES))}")
    for field in ("title", "summary"):
        if not isinstance(data.get(field), str) or not data[field].strip():
            errors.append(f"{field} must be a non-empty string")
    if not isinstance(data.get("slug"), str) or not SLUG_RE.fullmatch(data.get("slug", "")):
        errors.append("slug must contain lowercase ASCII words separated by single hyphens")
    for field in ("created", "updated"):
        if not isinstance(data.get(field), str) or not DATE_RE.fullmatch(data.get(field, "")):
            errors.append(f"{field} must use YYYY-MM-DD")
    for field in ("audience", "owners", "tags", "evidence"):
        if not isinstance(data.get(field), list):
            errors.append(f"{field} must be a JSON-compatible array")
    if isinstance(data.get("audience"), list) and not data["audience"]:
        errors.append("audience must contain at least one reader group")

    found = headings(body)
    if any(level == 1 for level, _ in found):
        errors.append("body must not contain # headings; the renderer creates H1 from frontmatter title")
    levels = [level for level, _ in found]
    for previous, current in zip(levels, levels[1:]):
        if current > previous + 1:
            errors.append(f"heading level jumps from H{previous} to H{current}")
            break
    normalized = {title.casefold() for level, title in found if level == 2}
    if doc_type in REQUIRED_HEADINGS:
        absent = sorted(REQUIRED_HEADINGS[doc_type] - normalized)
        if absent:
            errors.append(f"missing required H2 sections for {doc_type}: {', '.join(absent)}")
    if PLACEHOLDER_RE.search(text):
        errors.append("unresolved template or placeholder text is present")
    if UNSAFE_RE.search(text):
        errors.append("unsafe executable HTML or URL is present")
    return Result(path, errors, data.get("slug") if isinstance(data.get("slug"), str) else None)


def collect(paths: list[Path]) -> list[Path]:
    files: set[Path] = set()
    for path in paths:
        path = path.expanduser()
        if path.is_dir():
            files.update(candidate for candidate in path.rglob("*.mdx") if candidate.is_file())
        elif path.is_file():
            files.add(path)
        else:
            raise FileNotFoundError(f"path does not exist: {path}")
    return sorted(files)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="+", type=Path)
    parser.add_argument("--json", action="store_true", dest="as_json")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        files = collect(args.paths)
    except FileNotFoundError as error:
        print(f"validate_mdx: {error}", file=sys.stderr)
        return 2
    if not files:
        print("validate_mdx: no .mdx files found", file=sys.stderr)
        return 2

    results = [validate(path) for path in files]
    slug_owners: dict[str, Path] = {}
    for result in results:
        if not result.slug:
            continue
        if result.slug in slug_owners:
            result.errors.append(f"slug duplicates {slug_owners[result.slug]}")
        else:
            slug_owners[result.slug] = result.path
    failures = [result for result in results if result.errors]
    if args.as_json:
        print(json.dumps({"files": len(files), "failures": [{"path": str(result.path), "errors": result.errors} for result in failures]}, indent=2))
    else:
        for result in failures:
            for error in result.errors:
                print(f"{result.path}: {error}", file=sys.stderr)
        if not failures:
            print(f"validated {len(files)} MDX document(s)")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
