#!/usr/bin/env python3
"""Translate the transform oracle protocol to the optional Lightning CSS CLI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


TRANSFORM = re.compile(r"\.oracle\{transform:([^}]+)\}")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Lightning CSS transform oracle.")
    parser.add_argument("--executable", required=True)
    args = parser.parse_args()

    try:
        payload = json.load(sys.stdin)
        value = payload["value"]
        if not isinstance(value, str) or not value:
            raise ValueError("value must be a non-empty string")
    except (json.JSONDecodeError, KeyError, TypeError, ValueError) as error:
        print(f"lightningcss-adapter: invalid input: {error}", file=sys.stderr)
        return 1

    with tempfile.TemporaryDirectory() as temporary_directory:
        directory = Path(temporary_directory)
        source = directory / "oracle.css"
        output = directory / "oracle.min.css"
        source.write_text(f".oracle {{ transform: {value}; }}\n", encoding="utf-8")
        result = subprocess.run(
            [
                args.executable,
                "--minify",
                "--output-file",
                str(output),
                str(source),
            ],
            text=True,
            capture_output=True,
            check=False,
        )
        if result.returncode != 0:
            print(result.stderr.strip() or "lightningcss execution failed", file=sys.stderr)
            return 1
        try:
            css = output.read_text(encoding="utf-8")
        except (OSError, UnicodeError) as error:
            print(f"lightningcss-adapter: unable to read output: {error}", file=sys.stderr)
            return 1

    match = TRANSFORM.fullmatch(css.strip())
    if match is None:
        print("lightningcss-adapter: unexpected CSS output", file=sys.stderr)
        return 1
    print(json.dumps({"value": match.group(1).removesuffix(";")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
