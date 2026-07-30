import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
RUNNER = SCRIPTS / "run_browser_lab.py"
sys.path.insert(0, str(SCRIPTS))

from css_tokenography_core.laboratory import (  # noqa: E402
    PROTOCOL,
    LaboratoryContractError,
    build_report,
    validate_report,
)


def sections(name: str) -> dict[str, object]:
    return json.loads((FIXTURES / name).read_text(encoding="utf-8"))


def report_from_fixture(name: str) -> dict[str, object]:
    fixture = sections(name)
    return build_report(
        fixture["deterministic"], fixture["browser"], fixture["agentic"]
    )


def write_fake_runner(
    directory: Path,
    report: dict[str, object],
    exit_code: int = 0,
    expected_arguments: list[str] | None = None,
) -> Path:
    runner = directory / "fake_browser_lab.py"
    expectation = (
        "\n"
        f"if sys.argv[1:] != {expected_arguments!r}:\n"
        "    print('unexpected argv: ' + repr(sys.argv[1:]), file=sys.stderr)\n"
        "    raise SystemExit(9)\n"
        if expected_arguments is not None
        else ""
    )
    runner.write_text(
        (
            "import json\n"
            "import sys\n"
            + expectation
            + f"print(json.dumps({report!r}, sort_keys=True))\n"
            + f"raise SystemExit({exit_code})\n"
        ),
        encoding="utf-8",
    )
    return runner


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(RUNNER), *args],
        text=True,
        capture_output=True,
        check=False,
    )


class LaboratoryEvidenceContractTests(unittest.TestCase):
    def test_protocol_and_sections_are_explicit(self) -> None:
        report = report_from_fixture("laboratory-pass.json")

        self.assertEqual(report["protocol"], PROTOCOL)
        self.assertEqual(report["deterministic"]["status"], "pass")
        self.assertEqual(report["browser"]["status"], "pass")
        self.assertEqual(report["agentic"]["status"], "skipped")
        self.assertEqual(report["release"], {"status": "pass", "reasons": []})

    def test_agentic_success_cannot_override_deterministic_failure(self) -> None:
        report = report_from_fixture("laboratory-deterministic-fail-agentic-pass.json")

        self.assertEqual(report["release"], {"status": "fail", "reasons": ["deterministic"]})

    def test_agentic_success_cannot_override_browser_failure(self) -> None:
        report = report_from_fixture("laboratory-browser-fail-agentic-pass.json")

        self.assertEqual(report["release"], {"status": "fail", "reasons": ["browser"]})

    def test_agentic_disagreement_is_visible_and_makes_release_stricter(self) -> None:
        report = report_from_fixture("laboratory-agentic-disagreement.json")

        self.assertEqual(report["agentic"]["status"], "disagreement")
        self.assertEqual(
            report["release"], {"status": "fail", "reasons": ["agentic:disagreement"]}
        )

    def test_lower_layer_unavailability_is_not_reported_as_success(self) -> None:
        report = report_from_fixture("laboratory-browser-unavailable.json")

        self.assertEqual(report["release"], {"status": "unavailable", "reasons": ["browser"]})

    def test_report_rejects_adapter_supplied_release_override(self) -> None:
        report = report_from_fixture("laboratory-browser-fail-agentic-pass.json")
        report["release"] = {"status": "pass", "reasons": []}

        with self.assertRaisesRegex(LaboratoryContractError, "precedence decision"):
            validate_report(report)

    def test_report_normalizes_non_authoritative_release_explanations(self) -> None:
        report = report_from_fixture("laboratory-pass.json")
        report["release"] = {"status": "pass", "reasons": ["runner explanation"]}

        self.assertEqual(
            validate_report(report)["release"], {"status": "pass", "reasons": []}
        )

    def test_required_agentic_evaluation_cannot_be_skipped(self) -> None:
        fixture = sections("laboratory-pass.json")
        fixture["agentic"]["required"] = True

        with self.assertRaisesRegex(LaboratoryContractError, "cannot be skipped"):
            build_report(fixture["deterministic"], fixture["browser"], fixture["agentic"])


class BrowserLaboratoryCliTests(unittest.TestCase):
    def test_help_requires_no_node_or_browser_packages(self) -> None:
        result = run_cli("--help")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("without installing", result.stdout)
        self.assertIn("dependencies.", result.stdout)
        self.assertIn("--update-snapshots", result.stdout)

    def test_missing_runner_override_returns_unavailable_report(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            missing = Path(temporary_directory) / "browser-lab"
            result = run_cli(
                "--format", "json", "--runner-command", json.dumps([str(missing)])
            )

        self.assertEqual(result.returncode, 2, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["release"]["status"], "unavailable")
        self.assertIn("missing runner executable", report["deterministic"]["blockers"][0])

    def test_fake_runner_receives_stable_flags_and_returns_protocol_report(self) -> None:
        report = report_from_fixture("laboratory-pass.json")
        with tempfile.TemporaryDirectory() as temporary_directory:
            fake = write_fake_runner(
                Path(temporary_directory),
                report,
                expected_arguments=[
                    "--engines",
                    "firefox,webkit",
                    "--format",
                    "json",
                    "--update-snapshots",
                ],
            )
            command = json.dumps([sys.executable, str(fake)])
            result = run_cli(
                "--format",
                "json",
                "--engines",
                "firefox,webkit",
                "--update-snapshots",
                "--runner-command",
                command,
            )

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout), report)

    def test_fake_semantic_failure_returns_exit_one(self) -> None:
        report = report_from_fixture("laboratory-browser-fail-agentic-pass.json")
        with tempfile.TemporaryDirectory() as temporary_directory:
            fake = write_fake_runner(Path(temporary_directory), report, exit_code=1)
            result = run_cli(
                "--format", "json", "--runner-command", json.dumps([sys.executable, str(fake)])
            )

        self.assertEqual(result.returncode, 1, result.stderr)
        self.assertEqual(json.loads(result.stdout)["release"]["status"], "fail")

    def test_runner_cannot_claim_pass_when_process_failed(self) -> None:
        report = report_from_fixture("laboratory-pass.json")
        with tempfile.TemporaryDirectory() as temporary_directory:
            fake = write_fake_runner(Path(temporary_directory), report, exit_code=1)
            result = run_cli(
                "--format", "json", "--runner-command", json.dumps([sys.executable, str(fake)])
            )

        self.assertEqual(result.returncode, 1, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["release"]["status"], "fail")
        self.assertIn("exited 1", report["deterministic"]["errors"][0])

    def test_invalid_engine_is_rejected_before_any_runner_invocation(self) -> None:
        result = run_cli("--engines", "chrome")

        self.assertEqual(result.returncode, 2)
        self.assertIn("unsupported browser engine", result.stderr)


if __name__ == "__main__":
    unittest.main()
