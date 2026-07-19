import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
RUNNER = ROOT / "scripts" / "run_oracles.py"
MANIFEST = ROOT / "references" / "wpt-manifest.json"


def run_oracles(
    fixture: Path,
    *,
    adapter: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(RUNNER), "--input", str(fixture)]
    if adapter is not None:
        override = json.dumps([sys.executable, str(adapter)])
        command.extend(["--adapter-command", f"lightningcss={override}"])
    process_env = os.environ.copy()
    if env is not None:
        process_env.update(env)
    return subprocess.run(
        command,
        text=True,
        capture_output=True,
        check=False,
        env=process_env,
    )


def write_adapter(directory: Path, *, value: object, exit_code: int = 0) -> Path:
    adapter = directory / "fake_adapter.py"
    adapter.write_text(
        "import json\n"
        "import sys\n"
        "json.load(sys.stdin)\n"
        f"print(json.dumps({value!r}, sort_keys=True))\n"
        f"raise SystemExit({exit_code})\n",
        encoding="utf-8",
    )
    return adapter


class OracleRunnerTests(unittest.TestCase):
    def test_missing_optional_adapter_is_unavailable(self) -> None:
        result = run_oracles(FIXTURES / "oracle-unavailable.json", env={"PATH": ""})

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["classification"], "unavailable")
        self.assertEqual(report["core"], {"value": "translateX(10px) rotate(20deg)"})
        self.assertEqual(report["observations"][0]["status"], "unavailable")
        self.assertIsNone(report["observations"][0]["relation_to_core"])

    def test_fake_adapter_disagreement_is_retained(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            adapter = write_adapter(
                Path(temporary_directory), value={"value": "rotate(360deg)"}
            )
            result = run_oracles(FIXTURES / "oracle-transform.json", adapter=adapter)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["classification"], "divergence")
        self.assertEqual(report["observations"][0]["value"], {"value": "rotate(360deg)"})
        self.assertEqual(report["observations"][0]["relation_to_core"], "different")

    def test_fake_adapter_exact_match_is_explicit_agreement(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            adapter = write_adapter(
                Path(temporary_directory), value={"value": "rotate(1turn)"}
            )
            result = run_oracles(FIXTURES / "oracle-transform.json", adapter=adapter)

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["classification"], "agreement")
        self.assertEqual(report["observations"][0]["relation_to_core"], "exact")

    def test_adapter_execution_error_returns_evidence_and_exit_one(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            adapter = write_adapter(
                Path(temporary_directory), value={"ignored": True}, exit_code=7
            )
            result = run_oracles(FIXTURES / "oracle-transform.json", adapter=adapter)

        self.assertEqual(result.returncode, 1)
        report = json.loads(result.stdout)
        self.assertEqual(report["classification"], "error")
        self.assertEqual(report["observations"][0]["status"], "error")
        self.assertIsNone(report["observations"][0]["relation_to_core"])

    def test_malformed_input_exits_one_without_an_evidence_claim(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            fixture = Path(temporary_directory) / "malformed.json"
            fixture.write_text(
                json.dumps(
                    {
                        "subject": "transform",
                        "input": {"value": "rotate(1turn)"},
                        "adapters": "lightningcss",
                    }
                ),
                encoding="utf-8",
            )

            result = run_oracles(fixture)

        self.assertEqual(result.returncode, 1)
        self.assertEqual(result.stdout, "")
        self.assertIn("adapters must be a non-empty array", result.stderr)

    def test_wpt_manifest_pins_the_reviewed_transform_order_evidence(self) -> None:
        self.assertEqual(
            json.loads(MANIFEST.read_text(encoding="utf-8")),
            [
                {
                    "id": "css-transforms-order",
                    "upstream": "css/css-transforms/transform-order.html",
                    "revision": "37cd7ff74eb974fd41600bf7bc01d37576abf8b5",
                    "spec": "https://drafts.csswg.org/css-transforms-2/",
                    "owner": "css-transforms",
                    "local_adapter": "tests/test_transforms.py",
                }
            ],
        )


if __name__ == "__main__":
    unittest.main()
