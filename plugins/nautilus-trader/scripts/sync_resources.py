#!/usr/bin/env python3
"""Materialize portable workflow resources from reviewed package-owned sources."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
ANCHORS = {
    "building-nautilus-actors": ("V", "A", "D", "M2", "B1", "Q", "CF", "CP", "T", "RP", "AX"),
    "building-nautilus-strategies": ("V", "A", "D1", "S", "E", "R", "Q", "CF", "CP", "T", "RP", "AX"),
    "integrating-nautilus-data": ("V", "A", "D", "M", "B1", "B2", "AD", "Q", "CF", "CP", "T", "RP", "AX"),
    "backtesting-nautilus-strategies": ("V", "A", "D", "S", "E", "R", "B", "M", "L1", "L2", "Q", "CF", "CP", "T", "RP", "AX"),
    "running-nautilus-live": ("V", "A", "S3", "E", "R", "L", "B1", "B2", "M3", "AD", "AR", "SB", "CF", "CP", "T", "RP", "AX"),
    "deploying-nautilus-runs": ("V", "DP", "RP"),
}
CONNECTIONS = {
    "building-nautilus-actors": ("C1", "C3"),
    "building-nautilus-strategies": ("C1", "C2", "C4"),
    "integrating-nautilus-data": ("C1", "C3", "C7", "C8"),
    "backtesting-nautilus-strategies": ("C1", "C2", "C3", "C4", "C6", "C8"),
    "running-nautilus-live": ("C2", "C4", "C5", "C6", "C7"),
}
SOURCE = re.compile(r"`((?:crates/[^`:\s]+|schema/sql/[^`:\s]+|Cargo\.toml)):\d[^`]*`")
EXAMPLE_FILES = ("Cargo.toml", "Cargo.lock", "src/lib.rs", "src/main.rs", "src/observer.rs")


def json_bytes(value: object) -> bytes:
    return (json.dumps(value, indent=2) + "\n").encode()


def generated_files(root: Path) -> dict[Path, bytes]:
    manifest = json.loads((root / "source-manifest.json").read_text())
    rows = (root / "references/sources.md").read_text().splitlines()
    cases = json.loads((root / "evals/workflows.json").read_text())
    connections = (root / "references/connections.md").read_text()
    matches = list(re.finditer(r"^## (C\d+): [^\n]+\n.*?(?=^## |\Z)", connections, re.M | re.S))
    sections = {match[1]: match[0] for match in matches}
    if len(matches) != 8 or set(sections) != {f"C{i}" for i in range(1, 9)}:
        raise ValueError("Connection recipes must contain exactly C1 through C8")
    introduction = connections[:matches[0].start()]
    generated: dict[Path, bytes] = {}
    shared_guides = ("configuration.md", "composition.md", "rust-testing.md", "event-replay.md", "adapter-development.md", "version-and-integration.md")
    for name, prefixes in ANCHORS.items():
        skill = root / "skills" / name
        guides = ("event-replay.md", "version-and-integration.md") if name == "deploying-nautilus-runs" else shared_guides
        for guide in guides:
            generated[skill / "references" / guide] = (root / "references" / guide).read_bytes()
        if name != "deploying-nautilus-runs":
            generated[skill / "references/foundation.md"] = (root / "references/foundation.md").read_bytes()
            generated[skill / "references/connections.md"] = (
                (introduction + "".join(sections[case] for case in CONNECTIONS[name])).rstrip() + "\n"
            ).encode()
        selected = [
            row for row in rows
            if re.match(r"\| [A-Z]+\d+ \|", row)
            and (
                row.split("|")[1].strip() in prefixes
                or row.split("|")[1].strip().rstrip("0123456789") in prefixes
            )
        ]
        source_paths = set(SOURCE.findall("\n".join(selected)))
        local_manifest = {
            **manifest,
            "files": [item for item in manifest["files"] if item["path"] in source_paths],
        }
        generated[skill / "references/source-manifest.json"] = json_bytes(local_manifest)
        sources = f"""# Source-qualified Rust {manifest['framework_version']} evidence

Research date: {manifest['research_date']}. These original summaries connect
official documentation with declarations, callers, reducers and tests at upstream
revision `{manifest['upstream_revision']}`. Source coordinates are audit evidence, not paths the
skill must open. No source checkout is required to use this skill.

The release declares Rust {manifest['rust_version']}, edition 2024;
the [local hash manifest](source-manifest.json) identifies cited files, not a
whole release or proof of byte identity with published crates.

Read [Rust concepts](https://nautilustrader.io/docs/latest/concepts/rust/),
[actor how-to](https://nautilustrader.io/docs/latest/how_to/write_rust_actor/),
[strategy how-to](https://nautilustrader.io/docs/latest/how_to/write_rust_strategy/),
[message bus](https://nautilustrader.io/docs/latest/concepts/message_bus/),
[data](https://nautilustrader.io/docs/latest/concepts/data/),
[backtesting](https://nautilustrader.io/docs/latest/concepts/backtesting/), and
[Rust live](https://nautilustrader.io/docs/latest/how_to/run_rust_live_trading/)
only as relevant. Moving docs can differ from the application: its locked
compiler-visible declarations govern APIs. The published model fixture feature
is `test-support`; enable it only when fixtures require it.

| ID | Snapshot coordinates and connected symbols |
| --- | --- |
"""
        if name == "deploying-nautilus-runs":
            sources = f"""# Deployment source evidence

Qualified against Rust {manifest['framework_version']} at
`{manifest['upstream_revision']}`, with Rust {manifest['rust_version']}.
[Hashes](source-manifest.json) identify reviewed source files, not a requirement
to open a hidden checkout or a proof of cloud execution.

Official entry points: [Parquet/DataFusion backend](https://nautechsystems.github.io/nautilus_docs/rust-api-latest/nautilus_persistence/backend/index.html),
[live node](https://nautechsystems.github.io/nautilus_docs/rust-api-latest/nautilus_live/index.html),
[infrastructure](https://nautechsystems.github.io/nautilus_docs/rust-api-latest/nautilus_infrastructure/index.html).
Moving documentation is qualified by these pinned declarations and callers.

| ID | Snapshot coordinates and connected symbols |
| --- | --- |
"""
        generated[skill / "references/sources.md"] = (
            sources + "\n".join(selected) + """

Source tests were inspected, not all executed. An offline quickstart demonstrates
local composition only; it cannot prove provider entitlement, broker state,
profitability, production recovery or live protective-order behavior.
"""
        ).encode()
        adapter = {
            "integrating-nautilus-data": "adapter-data.md",
            "running-nautilus-live": "adapter-runtime.md",
        }.get(name)
        if adapter:
            generated[skill / "references/adapters.md"] = (
                root / "references" / adapter
            ).read_bytes()
        if name not in {"running-nautilus-live", "deploying-nautilus-runs"}:
            for filename in EXAMPLE_FILES:
                if name == "building-nautilus-actors" and filename == "src/observer.rs":
                    continue
                generated[skill / "assets/quickstart" / filename] = (
                    root / "examples/quickstart" / filename
                ).read_bytes()
            readme = """# Offline native quickstart

Independent Rust 2024 package pinned to Nautilus 0.64.0; requires Rust 1.98.1.
From this directory run `cargo test --locked`, then `cargo run --locked`.
With cached dependencies use `--offline`. First resolution/build may download
crates, but the application uses only synthetic input and makes no provider calls.

Read [the observer and payload](src/observer.rs), [the Strategy](src/lib.rs),
[native replay wiring](src/main.rs),
and [exact dependency features](Cargo.toml). Expected application output:
`inputs=5 quotes=4 signals=1 orders=1 positions=1`.

The actor observes synthetic quotes and a separately injected custom signal;
the Strategy alone submits the demo order. Native backtest engines own clock,
Cache, risk and execution. The observer is a local verification fixture, not a
provider adapter, ingestion implementation or second trading authority.
The example is intentionally a minimal market-order path, not a bracket recipe,
catalog round trip, realistic fill model or trading-performance demonstration.
Its JSON test does not qualify Arrow persistence. No broker is contacted.

Run `cargo test --locked --test observation_chain` for the separate C1 boundary.
That test feeds only four quotes; an order-free actor publishes four immutable
observations and a Strategy receives their exact values and causal timestamps.
It submits no orders and asserts zero positions. Read
[the integration test](tests/observation_chain.rs); unlike the default binary,
it does not inject a prebuilt custom input.
"""
            if name != "building-nautilus-actors":
                generated[skill / "assets/quickstart/tests/observation_chain.rs"] = (
                    root / "examples/quickstart/tests/observation_chain.rs"
                ).read_bytes()
            if name == "building-nautilus-actors":
                generated[skill / "assets/quickstart/src/lib.rs"] = (
                    root / "examples/quickstart/src/observer.rs"
                ).read_bytes()
                generated[skill / "assets/quickstart/src/main.rs"] = (
                    root / "examples/actor-main.rs"
                ).read_bytes()
                readme = """# Order-free actor quickstart

Independent Rust 2024 package pinned to Nautilus 0.64.0; requires Rust 1.98.1.
From this directory run `cargo test --locked`, then `cargo run --locked`.
With cached dependencies use `--offline`; an initial build may download crates.
The program is entirely synthetic and makes no provider calls.

Read [the actor and JSON test](src/lib.rs), [native replay wiring](src/main.rs),
and [dependency features](Cargo.toml). The shared manifest includes the native
backtest dependency graph; this program registers no Strategy, has no order
submission code and creates no exposure.

Expected output: `inputs=5 quotes=4 signals=1 orders=0 positions=0`.
QuoteCounter receives four native quotes and one separately injected immutable
custom signal. Native BacktestEngine owns registration, clock, Cache and dispatch.
The JSON test is not an Arrow/catalog round trip or live-provider qualification.
"""
            generated[skill / "assets/quickstart/README.md"] = readme.encode()
        if name not in {"building-nautilus-actors", "running-nautilus-live", "deploying-nautilus-runs"}:
            example = root / "examples/quickstart"
            for source in example.rglob("*"):
                if source.is_file() and not {"target", "__pycache__"}.intersection(source.relative_to(example).parts):
                    content = source.read_bytes()
                    if source.name == "README.md":
                        content = content.replace(b"../../evals/qualification.md", b"../../references/rust-testing.md").replace(b"../../references/execution.md", b"../../references/guide.md").replace(b"../../references/market-data.md", b"../../references/guide.md")
                    generated[skill / "assets/quickstart" / source.relative_to(example)] = content
        if name == "running-nautilus-live":
            example = root / "examples/live-composition"
            for source in example.rglob("*"):
                if source.is_file() and "target" not in source.relative_to(example).parts:
                    generated[skill / "assets/live-composition" / source.relative_to(example)] = source.read_bytes()
        if name == "deploying-nautilus-runs":
            for filename in ("icon.svg", "icon.png"):
                generated[skill / "assets" / filename] = (root / "assets" / filename).read_bytes()
            example = root / "examples/run-storage"
            for source in example.rglob("*"):
                if source.is_file() and "target" not in source.relative_to(example).parts:
                    generated[skill / "assets/storage-smoke" / source.relative_to(example)] = source.read_bytes()
        for group, filename in (("working", "evals.json"), ("acceptance", "acceptance.json")):
            dataset = {"skill_name": name, "evals": []}
            for case in cases[name][group]:
                entry = {key: value for key, value in case.items() if key != "kind"}
                entry["expected_skill"] = None if case.get("kind") == "negative" else name
                entry["files"] = []
                dataset["evals"].append(entry)
            generated[skill / "evals" / filename] = json_bytes(dataset)
    return generated


def drift(root: Path) -> list[str]:
    return [
        str(path.relative_to(root))
        for path, expected in generated_files(root).items()
        if not path.is_file() or path.read_bytes() != expected
    ]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="Report drift without writing")
    args = parser.parse_args()
    if args.check:
        mismatches = drift(ROOT)
        if mismatches:
            print("Generated resource drift:\n" + "\n".join(mismatches))
            return 1
        print("Portable workflow resources are current")
        return 0
    for path, content in generated_files(ROOT).items():
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(content)
    print("Portable workflow resources synchronized")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
