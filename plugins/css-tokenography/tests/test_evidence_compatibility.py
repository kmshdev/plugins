import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
CONTRAST = (
    ROOT / "skills" / "css-variables" / "scripts" / "color_contrast_checker.py"
)
TRANSFORM = (
    ROOT / "skills" / "css-transforms" / "scripts" / "css_transform_playground.py"
)


def run_cli(
    script: Path,
    *args: str,
    stdin: bytes | None = None,
    cwd: Path | None = None,
) -> subprocess.CompletedProcess[bytes]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=stdin,
        capture_output=True,
        check=False,
        cwd=cwd,
    )


def sha256(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


class DefaultOutputCompatibilityTests(unittest.TestCase):
    def test_success_output_remains_byte_compatible_with_d67760e(self) -> None:
        cases = (
            (
                CONTRAST,
                ("--input", str(FIXTURES / "contrast-threshold-fail.json"), "--format", "json"),
                "449417c2af1899dbece3f4f75bb32a887e395dd55d6a9a9b41a3b74f348d08cd",
            ),
            (
                CONTRAST,
                ("--input", str(FIXTURES / "contrast-threshold-fail.json")),
                "72fde4be51b747900f7b3dc001c74c5349b4233e43cfe51cf0c6b7c5686a64b4",
            ),
            (
                TRANSFORM,
                ("--input", str(FIXTURES / "transform-valid.json"), "--format", "json"),
                "9b669de4df791e060bbe6254af93573334f23e4a47e068d2e8e9923517c72694",
            ),
            (
                TRANSFORM,
                ("--input", str(FIXTURES / "transform-valid.json"), "--format", "css"),
                "ff357ebafea4aa0d975c8cef92afc6a2ec13e8d53bcea9680972868cd7ea81ba",
            ),
            (
                TRANSFORM,
                ("--input", str(FIXTURES / "transform-valid.json")),
                "bcd230419987269ae934a4368267c20e05fa34330ff12928269f5bbbc86f3587",
            ),
        )

        for script, args, expected_stdout_hash in cases:
            with self.subTest(script=script.name, args=args):
                result = run_cli(script, *args)
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertEqual(result.stderr, b"")
                self.assertEqual(sha256(result.stdout), expected_stdout_hash)

    def test_failure_output_and_exit_behavior_remain_unchanged(self) -> None:
        cases = (
            (
                CONTRAST,
                b'{"foreground":"#fff","background":"#ffffff"}',
                b"color-contrast-checker: foreground must be a six-digit hex color\n",
            ),
            (
                TRANSFORM,
                b'{"transform":{"kind":"list","functions":[{"name":"unknown","args":[1]}]}}',
                b"css-transform-playground: Unsupported transform function 'unknown'\n",
            ),
        )

        for script, stdin, expected_stderr in cases:
            with self.subTest(script=script.name):
                result = run_cli(script, "--format", "json", stdin=stdin)
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stdout, b"")
                self.assertEqual(result.stderr, expected_stderr)


class EvidenceFlagTests(unittest.TestCase):
    def test_default_json_remains_an_unwrapped_report(self) -> None:
        cases = (
            (CONTRAST, FIXTURES / "contrast-threshold-fail.json"),
            (TRANSFORM, FIXTURES / "transform-valid.json"),
        )

        for script, fixture in cases:
            with self.subTest(script=script.name):
                result = run_cli(script, "--input", str(fixture), "--format", "json")
                self.assertEqual(result.returncode, 0, result.stderr)
                report = json.loads(result.stdout)
                self.assertNotIn("classification", report)
                self.assertNotIn("core", report)
                self.assertNotIn("observations", report)

    def test_evidence_flag_wraps_core_without_mutation_from_any_cwd(self) -> None:
        cases = (
            (CONTRAST, FIXTURES / "contrast-threshold-fail.json"),
            (TRANSFORM, FIXTURES / "transform-valid.json"),
        )

        with tempfile.TemporaryDirectory() as directory:
            cwd = Path(directory)
            for script, fixture in cases:
                with self.subTest(script=script.name):
                    plain = run_cli(
                        script,
                        "--input",
                        str(fixture),
                        "--format",
                        "json",
                        cwd=cwd,
                    )
                    wrapped = run_cli(
                        script,
                        "--input",
                        str(fixture),
                        "--format",
                        "json",
                        "--evidence",
                        cwd=cwd,
                    )
                    self.assertEqual(plain.returncode, 0, plain.stderr)
                    self.assertEqual(wrapped.returncode, 0, wrapped.stderr)
                    envelope = json.loads(wrapped.stdout)
                    self.assertEqual(envelope["core"], json.loads(plain.stdout))
                    self.assertEqual(envelope["classification"], "unavailable")
                    self.assertEqual(envelope["observations"], [])


if __name__ == "__main__":
    unittest.main()
