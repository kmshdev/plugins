#!/usr/bin/env python3
"""Generate deployment files and isolated run plans without external actions."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import json
from pathlib import Path
import re
from urllib.parse import unquote, urlsplit
from uuid import uuid4

ASSETS = Path(__file__).resolve().parent.parent / "assets/deployment"
IDENTIFIER = re.compile(r"[A-Za-z][A-Za-z0-9_-]*\Z")
IMAGE = re.compile(r"[A-Za-z0-9][A-Za-z0-9._:/-]*@sha256:[0-9a-f]{64}\Z")


def storage_uri(value: str, *, writable: bool) -> str:
    """Validate and normalize a storage URI for catalog input or artifact output."""
    parsed = urlsplit(value)
    if not parsed.scheme:
        return str(Path(value).resolve())
    allowed = {"file", "s3", "az", "abfs", "gs", "gcs", "http", "https"}
    if parsed.scheme not in allowed or parsed.query or parsed.fragment:
        raise ValueError("Use a supported storage URI without query strings or fragments")
    if parsed.password or (parsed.username and parsed.scheme != "abfs"):
        raise ValueError("Credentials must not be embedded in storage URIs")
    if parsed.scheme == "abfs" and not parsed.username:
        raise ValueError("ABFS requires container@account addressing")
    if parsed.scheme == "file":
        if parsed.netloc not in {"", "localhost"} or not parsed.path.startswith("/"):
            raise ValueError("Use an absolute local file URI")
        return str(Path(unquote(parsed.path)).resolve())
    elif not parsed.hostname:
        raise ValueError("Remote storage URIs require a bucket, container, or host")
    if writable and parsed.scheme in {"http", "https"}:
        raise ValueError("HTTP input support does not establish a writable artifact backend")
    return value.rstrip("/")


def initialize(output: Path, package: str, binary: str) -> None:
    """Create deployment overlay files from templates without starting execution."""
    if not IDENTIFIER.fullmatch(package) or not IDENTIFIER.fullmatch(binary):
        raise ValueError("Package and binary must be Cargo-style identifiers")
    templates = {
        source.relative_to(ASSETS): source.read_text()
        for source in sorted(ASSETS.rglob("*")) if source.is_file()
    }
    output.mkdir(parents=True, exist_ok=False)
    for relative, text in templates.items():
        target = output / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text.replace("@@PACKAGE@@", package).replace("@@BINARY@@", binary))


def plan(output: Path, image: str, mode: str, catalog_uri: str, artifact_root: str, *, config_digest: str) -> dict:
    """Generate an isolated run plan with unique identifiers without executing the run."""
    if not IMAGE.fullmatch(image):
        raise ValueError("Use the actual OCI image reference with an immutable sha256 digest")
    if mode not in {"backtest", "sandbox", "live"}:
        raise ValueError("Use one of: backtest, sandbox, live")
    if not re.fullmatch(r"[0-9a-f]{64}", config_digest):
        raise ValueError("Use the effective application configuration SHA-256 digest (64 lowercase hex characters)")
    source = storage_uri(catalog_uri, writable=False)
    destination = storage_uri(artifact_root, writable=True)
    if mode == "backtest" and urlsplit(destination).scheme == "az":
        raise ValueError("0.64 kernel streaming cannot supply az account_name; use qualified ABFS addressing or local capture and explicit Azure publication")
    run_id = str(uuid4())
    separator = "" if destination.endswith("/") else "/"
    prefix = f"{destination}{separator}runs/{run_id}"
    record = {
        "schema": "nautilus-application-run-plan/v1",
        "created_at": datetime.now(UTC).isoformat(),
        "state": "planned",
        "run_id": run_id,
        "attempt_id": str(uuid4()),
        "instance_id": run_id,
        "mode": mode,
        "image_digest": image,
        "config_digest": config_digest,
        "framework_version": "0.64.0",
        "node_processes": 1,
        "automatic_retries": 0,
        "capture_integration": "kernel-streaming-config" if mode == "backtest" else "explicit-native-writer",
        "input_catalog_uri": source,
        "artifact_prefix": prefix,
        "streaming": {
            "catalog_path": f"{prefix}/catalog",
            "fs_protocol": urlsplit(destination).scheme or "file",
            "flush_interval_ms": 1000,
            "replace_existing": False,
            "rotation_config": "no_rotation",
        },
        "cache": {"use_trader_prefix": True, "use_instance_id": True, "flush_on_start": False},
        "postgres_role": "application-run-registry",
        "native_cache_backend": "redis",
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("x") as handle:
        json.dump(record, handle, indent=2)
        handle.write("\n")
    return record


def main() -> int:
    """Process command-line arguments and execute the requested scaffold operation."""
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    initialize_parser = commands.add_parser("init", help="Create a reviewable overlay in a new directory")
    initialize_parser.add_argument("--output", type=Path, required=True)
    initialize_parser.add_argument("--package", required=True)
    initialize_parser.add_argument("--binary", required=True)
    plan_parser = commands.add_parser("plan", help="Write a new run plan without executing it")
    plan_parser.add_argument("--output", type=Path, required=True)
    plan_parser.add_argument("--image", required=True)
    plan_parser.add_argument("--config-digest", required=True, help="SHA-256 of the effective application configuration")
    plan_parser.add_argument("--mode", choices=("backtest", "sandbox", "live"), required=True)
    plan_parser.add_argument("--catalog-uri", required=True)
    plan_parser.add_argument("--artifact-root", required=True)
    args = parser.parse_args()
    try:
        if args.command == "init":
            initialize(args.output, args.package, args.binary)
            print(f"Generated deployment overlay: {args.output}; nothing started or deployed")
        else:
            record = plan(args.output, args.image, args.mode, args.catalog_uri, args.artifact_root, config_digest=args.config_digest)
            print(f"Planned run {record['run_id']}: {args.output}; nothing executed")
    except (ValueError, OSError) as error:
        parser.exit(2, f"{error}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
