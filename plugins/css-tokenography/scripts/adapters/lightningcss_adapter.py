#!/usr/bin/env python3
"""Translate typed transform/gradient oracle input to the optional Lightning CSS CLI."""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
import tempfile
from pathlib import Path


DECLARATION = re.compile(r"\.oracle\{(?:transform|background-image):([^}]+)\}")


GRADIENT_SCRIPTS = (
    Path(__file__).resolve().parents[2]
    / "skills"
    / "css-gradients"
    / "scripts"
)
sys.path.insert(0, str(GRADIENT_SCRIPTS))

from gradient_model import Gradient


def main() -> int:
    parser = argparse.ArgumentParser(description="Run a Lightning CSS transform oracle.")
    parser.add_argument("--executable", required=True)
    args = parser.parse_args()

    try:
        payload = json.load(sys.stdin)
        if not isinstance(payload, dict):
            raise ValueError("input must be an object")
        if "kind" in payload:
            property_name = "background-image"
            value = Gradient.from_data(payload).value()
        else:
            property_name = "transform"
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
        source.write_text(
            f".oracle {{ {property_name}: {value}; }}\n", encoding="utf-8"
        )
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

    match = DECLARATION.fullmatch(css.strip())
    if match is None:
        print("lightningcss-adapter: unexpected CSS output", file=sys.stderr)
        return 1
    print(json.dumps({"value": match.group(1).removesuffix(";")}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
