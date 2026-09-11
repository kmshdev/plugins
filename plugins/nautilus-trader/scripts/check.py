#!/usr/bin/env python3
"""Check a relocated skill offline; optionally record or verify source hashes."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tomllib
from pathlib import Path
from urllib.parse import unquote, urlsplit

import sync_resources

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
SOURCE = re.compile(r"`((?:crates/[^`:\s]+|Cargo\.toml)):(\d[^`]*)`")
EXCLUDED = {"target", "__pycache__", "results"}
PLUGIN_VERSION = "0.63.0+codex.20260911.1"
PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


def check_skill(root: Path) -> list[str]:
    """Check an independent workflow without reading the parent package."""
    root = root.resolve(strict=True)
    errors: list[str] = []
    for path in root.rglob("*"):
        if EXCLUDED.intersection(path.relative_to(root).parts):
            continue
        if path.is_symlink():
            errors.append(f"Workflow depends on symlink: {path.relative_to(root)}")
            continue
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if "/Users/" in text or "/home/" in text or "file://" in text:
            errors.append(f"Machine-local workflow reference: {path.relative_to(root)}")
        for match in LINK.finditer(text):
            target = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme in {"https", "http", "mailto"} or not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if parsed.scheme or not resolved.is_relative_to(root):
                errors.append(f"Link escapes independent workflow: {target}")
            elif not resolved.exists():
                errors.append(f"Missing workflow link: {target}")
    entry = (root / "SKILL.md").read_text(encoding="utf-8")
    name_match = re.match(r"---\nname: ([a-z-]+)\n", entry)
    if name_match is None or name_match[1] not in sync_resources.ANCHORS:
        errors.append("Unknown workflow skill frontmatter")
        return errors
    name = name_match[1]
    if name == "building-nautilus-actors":
        for source in (root / "assets/quickstart").rglob("*.rs"):
            if EXCLUDED.intersection(source.relative_to(root).parts):
                continue
            if re.search(r"\b(?:submit_order(?:_list)?|add_strategy|nautilus_strategy)\b", source.read_text()):
                errors.append(f"Actor example contains order authority: {source.relative_to(root)}")
    if len(entry.split()) > 400:
        errors.append(f"Workflow router exceeds 400-word budget: {name}")
    if 'version: "0.63.0"' not in entry:
        errors.append(f"Wrong workflow version: {name}")
    ids: set[str] = set()
    prompts: set[str] = set()
    for filename in ("evals.json", "acceptance.json"):
        dataset = json.loads((root / "evals" / filename).read_text())
        if dataset.get("skill_name") != name or not dataset.get("evals"):
            errors.append(f"Wrong or empty workflow dataset: {name}/{filename}")
        for case in dataset.get("evals", []):
            if case.get("id") in ids or case.get("prompt") in prompts:
                errors.append(f"Working/acceptance case reused: {name}/{case.get('id')}")
            ids.add(case.get("id"))
            prompts.add(case.get("prompt"))
            required = ("id", "prompt", "expected_output")
            if any(not isinstance(case.get(key), str) or not case[key] for key in required):
                errors.append(f"Incomplete evaluator case: {name}/{case.get('id')}")
            assertions = case.get("assertions")
            if not isinstance(assertions, list) or len(assertions) < 2 or any(
                not isinstance(assertion, str) or not assertion for assertion in assertions
            ):
                errors.append(f"Incomplete assertions: {name}/{case.get('id')}")
            if "expected_skill" not in case or case["expected_skill"] not in (None, name):
                errors.append(f"Wrong case target: {name}/{case.get('id')}")
            if case.get("files") != []:
                errors.append(f"Unexpected evaluator staging: {name}/{case.get('id')}")
    evidence = json.loads((root / "references/source-manifest.json").read_text())
    if evidence.get("framework_version") != "0.63.0" or not evidence.get("files"):
        errors.append(f"Missing workflow source evidence: {name}")
    source_text = (root / "references/sources.md").read_text()
    paths = {item["path"] for item in evidence.get("files", [])}
    if len(paths) != len(evidence.get("files", [])):
        errors.append(f"Duplicate workflow source record: {name}")
    for item in evidence.get("files", []):
        if not re.fullmatch(r"[0-9a-f]{64}", item.get("sha256", "")):
            errors.append(f"Invalid workflow digest: {name}/{item['path']}")
    if paths != set(sync_resources.SOURCE.findall(source_text)):
        errors.append(f"Workflow source inventory differs: {name}")
    return errors


def source_coordinates() -> dict[str, str]:
    text = (ROOT / "references/sources.md").read_text(encoding="utf-8")
    coordinates: dict[str, str] = {}
    for name, ranges in SOURCE.findall(text):
        coordinates[name] = ",".join(filter(None, (coordinates.get(name), ranges)))
    return coordinates


def source_records(source_root: Path) -> list[dict[str, str]]:
    base = source_root.resolve(strict=True)
    workspace = tomllib.loads((base / "Cargo.toml").read_text(encoding="utf-8"))
    package = workspace["workspace"]["package"]
    if package["version"] != "0.63.0":
        raise ValueError(f"Expected source 0.63.0, found {package['version']}")
    if package["rust-version"] != "1.98.0" or package["edition"] != "2024":
        raise ValueError("Source toolchain contract differs from this bundle")
    records = []
    errors = []
    for name, ranges in sorted(source_coordinates().items()):
        path = (base / name).resolve(strict=True)
        if not path.is_relative_to(base):
            raise ValueError(f"Source escapes supplied root: {name}")
        contents = path.read_bytes()
        last_line = max(int(number) for number in re.findall(r"\d+", ranges))
        if last_line > len(contents.splitlines()):
            errors.append(f"Source citation exceeds file length: {name}:{ranges}")
        records.append({"path": name, "sha256": hashlib.sha256(contents).hexdigest()})
    if errors:
        raise ValueError("\n".join(errors))
    return records


def check_bundle() -> list[str]:
    errors: list[str] = []
    for path in ROOT.rglob("*"):
        relative = path.relative_to(ROOT)
        if EXCLUDED.intersection(relative.parts):
            continue
        if path.is_symlink():
            errors.append(f"Bundle must not depend on symlinks: {relative}")
            continue
        if path.suffix != ".md":
            continue
        text = path.read_text(encoding="utf-8")
        if "/Users/" in text or "/home/" in text or "file://" in text:
            errors.append(f"Machine-local reference: {relative}")
        for match in LINK.finditer(text):
            target = match.group(1).strip().split(maxsplit=1)[0].strip("<>")
            parsed = urlsplit(target)
            if parsed.scheme in {"https", "http", "mailto"}:
                continue
            if not parsed.path:
                continue
            resolved = (path.parent / unquote(parsed.path)).resolve()
            if parsed.scheme or not resolved.is_relative_to(ROOT):
                errors.append(f"Link escapes bundle: {relative}: {target}")
            elif not resolved.exists():
                errors.append(f"Missing local link: {relative}: {target}")
    if (ROOT / "SKILL.md").exists():
        errors.append("Legacy root SKILL.md must not be shipped")
    if (ROOT / "agents").exists():
        errors.append("Legacy root agents directory must not be shipped")
    if (ROOT / "plugin.json").exists():
        errors.append("Legacy root plugin.json must not be shipped")
    manifest = json.loads((ROOT / "source-manifest.json").read_text(encoding="utf-8"))
    if manifest["framework_version"] != "0.63.0":
        errors.append("Wrong manifest framework pin")
    records = manifest["files"]
    paths = [record["path"] for record in records]
    if len(set(paths)) != len(paths) or set(paths) != set(source_coordinates()):
        errors.append("Source ledger and hash inventory differ")
    for record in records:
        if not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
            errors.append(f"Invalid source digest: {record['path']}")
    examples = sorted((ROOT / "examples").rglob("Cargo.toml"))
    if not examples:
        errors.append("Bundle has no canonical Rust examples")
    for cargo_path in examples:
        relative = cargo_path.relative_to(ROOT)
        cargo = tomllib.loads(cargo_path.read_text(encoding="utf-8"))
        for name, dependency in cargo.get("dependencies", {}).items():
            if not name.startswith("nautilus-"):
                continue
            if not isinstance(dependency, dict) or dependency.get("version") != "=0.63.0":
                errors.append(f"Unpinned framework dependency: {relative}: {name}")
                continue
            if any(key in dependency for key in ("path", "git", "branch")):
                errors.append(f"Example has external source-layout dependency: {relative}: {name}")
            features = dependency.get("features", [])
            if not isinstance(features, list) or {"python", "extension-module"}.intersection(features):
                errors.append(f"Example requests Python: {relative}: {name}")
    dataset = json.loads((ROOT / "evals/evals.json").read_text(encoding="utf-8"))
    if dataset["skill_name"] != "nautilus-trader":
        errors.append("Wrong evaluation skill name")
    ids: set[str] = set()
    for case in dataset["evals"]:
        if case["id"] in ids:
            errors.append(f"Duplicate case: {case['id']}")
        ids.add(case["id"])
        if not case["prompt"] or len(case["assertions"]) < 2:
            errors.append(f"Missing evaluation contract: {case['id']}")
        for route in case["references"]:
            target = (ROOT / route).resolve()
            if not target.is_relative_to(ROOT) or not target.is_file():
                errors.append(f"Invalid evaluation route: {case['id']}: {route}")
    plugin_path = ROOT / ".codex-plugin/plugin.json"
    if not plugin_path.is_file():
        errors.append("Missing Codex plugin manifest")
        plugin = {}
    else:
        plugin = json.loads(plugin_path.read_text(encoding="utf-8"))
    if plugin.get("name") != "nautilus-trader" or plugin.get("version") != PLUGIN_VERSION:
        errors.append("Wrong plugin identity/version")
    interface = plugin.get("interface")
    if not isinstance(interface, dict):
        errors.append("Missing plugin interface metadata")
    else:
        expected_icons = {"composerIcon": "./assets/icon.png", "logo": "./assets/icon.png"}
        if any(interface.get(key) != value for key, value in expected_icons.items()):
            errors.append("Wrong plugin interface icons")
    for icon, signature in ((ROOT / "assets/icon.svg", b"<svg"), (ROOT / "assets/icon.png", PNG_SIGNATURE)):
        if not icon.is_file() or icon.is_symlink():
            errors.append(f"Missing plugin icon: {icon.relative_to(ROOT)}")
        elif signature not in icon.read_bytes()[:512]:
            errors.append(f"Invalid plugin icon: {icon.relative_to(ROOT)}")
    discovered = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
    if discovered != set(sync_resources.ANCHORS):
        errors.append("Plugin must discover exactly the five workflow skills")
    for name in sorted(discovered & set(sync_resources.ANCHORS)):
        skill_root = ROOT / "skills" / name
        errors.extend(check_skill(skill_root))
        errors.extend(check_skill_icons(skill_root))
    errors.extend(f"Generated resource drift: {path}" for path in sync_resources.drift(ROOT))
    return errors


def check_skill_icons(skill_root: Path) -> list[str]:
    """Check icon declarations without accepting YAML features in a portable bundle."""
    path = skill_root / "agents/openai.yaml"
    if not path.is_file() or path.is_symlink():
        return [f"Missing workflow agent metadata: {path.relative_to(ROOT)}"]
    text = path.read_text(encoding="utf-8")
    errors: list[str] = []
    expected = {"icon_small": "./assets/icon.svg", "icon_large": "./assets/icon.png"}
    for key, value in expected.items():
        raw_matches = re.findall(
            rf'''(?m)^\s*{key}:\s*(?:"([^"\r\n]*)"|'([^'\r\n]*)'|([^#\s\r\n]+))\s*$''',
            text,
        )
        matches = [next((part for part in match if part), "") for match in raw_matches]
        if matches != [value]:
            errors.append(f"Wrong workflow icon declaration: {path.relative_to(ROOT)}: {key}")
            continue
        target = (skill_root / value).resolve()
        if not target.is_relative_to(skill_root) or not target.is_file() or target.is_symlink():
            errors.append(f"Unsafe workflow icon path: {path.relative_to(ROOT)}: {key}")
            continue
        signature = b"<svg" if key == "icon_small" else PNG_SIGNATURE
        if signature not in target.read_bytes()[:512]:
            errors.append(f"Invalid workflow icon: {target.relative_to(ROOT)}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--source-root", type=Path, help="Verify source content, read-only")
    group.add_argument("--record-source", type=Path, help="Explicitly regenerate source manifest")
    group.add_argument("--skill", type=Path, help="Check one independently relocated workflow")
    args = parser.parse_args()
    if args.skill:
        errors = check_skill(args.skill)
        if errors:
            print("\n".join(errors), file=sys.stderr)
            return 1
        print("Independent workflow contract passed")
        return 0
    manifest_path = ROOT / "source-manifest.json"
    if args.record_source:
        manifest = {
            "schema_version": 1,
            "framework_version": "0.63.0",
            "rust_version": "1.98.0",
            "edition": "2024",
            "research_date": "2026-09-09",
            "source_identity": "unversioned-source-snapshot",
            "upstream_revision": None,
            "scope": "Hashes identify cited files, not an entire release or registry artifact.",
            "files": source_records(args.record_source),
        }
        manifest_path.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    errors = check_bundle()
    if args.source_root:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if source_records(args.source_root) != manifest["files"]:
            errors.append("Supplied source differs from the recorded snapshot")
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1
    print("Portable skill contract passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
