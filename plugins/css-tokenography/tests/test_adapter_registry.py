import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_adapters import validate


def validate_copy(changes: dict[str, object]) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
        registry = plugin / "references" / "automation-adapters.json"
        rows = json.loads(registry.read_text(encoding="utf-8"))
        rows[0].update(changes)
        registry.write_text(json.dumps(rows), encoding="utf-8")
        return validate(plugin)


def validate_registry_content(
    content: str | None, *, registry_is_directory: bool = False
) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
        registry = plugin / "references" / "automation-adapters.json"
        registry.unlink()
        if registry_is_directory:
            registry.mkdir()
        elif content is not None:
            registry.write_text(content, encoding="utf-8")
        return validate(plugin)


def run_validator_with_registry(content: str | None) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
        registry = plugin / "references" / "automation-adapters.json"
        registry.unlink()
        if content is not None:
            registry.write_text(content, encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_adapters.py"),
                "--plugin",
                str(plugin),
                "--format",
                "json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )


class AdapterRegistryTests(unittest.TestCase):
    def test_optional_adapters_do_not_require_installed_commands(self) -> None:
        report = validate(ROOT)

        self.assertEqual(report["errors"], [])
        self.assertIn("lightningcss", [row["id"] for row in report["adapters"]])
        passmark = next(row for row in report["adapters"] if row["id"] == "passmark")
        self.assertEqual(passmark["adoption"], "blocked-pending-license-review")

    def test_every_adapter_must_remain_optional(self) -> None:
        report = validate_copy({"required": True})

        self.assertIn("adapter lightningcss required must be false", report["errors"])

    def test_registry_rejects_shell_commands_and_missing_license_records(self) -> None:
        shell_report = validate_copy({"command": "npx lightningcss"})
        missing_license_report = validate_copy({"license": ""})

        self.assertIn("command must be an argv array", shell_report["errors"][0])
        self.assertIn(
            "adapter lightningcss license must be a non-empty string",
            missing_license_report["errors"],
        )

    def test_blocked_adapters_must_remain_optional(self) -> None:
        report = validate_copy({"adoption": "blocked-pending-review", "required": True})

        self.assertIn(
            "adapter lightningcss blocked adoption must remain optional",
            report["errors"],
        )

    def test_invalid_adapter_ids_are_reported_without_crashing(self) -> None:
        report = validate_copy({"id": []})

        self.assertIn("adapter [] id must be a non-empty string", report["errors"])

    def test_registry_read_failures_return_structured_reports(self) -> None:
        cases = {
            "missing": (None, False),
            "malformed": ("{not-json", False),
            "unreadable": (None, True),
            "wrong-shaped": ("{}", False),
        }
        for name, (content, registry_is_directory) in cases.items():
            with self.subTest(case=name):
                try:
                    report = validate_registry_content(
                        content, registry_is_directory=registry_is_directory
                    )
                except (OSError, ValueError) as error:
                    self.fail(f"validate raised instead of returning a report: {error}")
                self.assertEqual(set(report), {"adapters", "errors", "warnings"})
                self.assertEqual(report["adapters"], [])
                self.assertNotEqual(report["errors"], [])
                self.assertEqual(report["warnings"], [])

    def test_json_cli_keeps_registry_read_errors_machine_readable(self) -> None:
        for name, content in {"missing": None, "malformed": "{not-json"}.items():
            with self.subTest(case=name):
                result = run_validator_with_registry(content)
                self.assertNotEqual(result.returncode, 0)
                try:
                    report = json.loads(result.stdout)
                except json.JSONDecodeError as error:
                    self.fail(f"validator did not emit JSON: {error}: {result.stdout!r}")
                self.assertEqual(set(report), {"adapters", "errors", "warnings"})
                self.assertEqual(report["adapters"], [])
                self.assertNotEqual(report["errors"], [])
                self.assertEqual(report["warnings"], [])

    def test_passmark_license_record_keeps_adoption_blocked(self) -> None:
        record = ROOT / "references" / "licenses" / "passmark.md"

        self.assertTrue(record.is_file(), record)
        text = record.read_text(encoding="utf-8")
        self.assertIn("FSL-1.1-ALv2", text)
        self.assertIn("blocked-pending-license-review", text)

    def test_browserytools_license_record_is_observation_only(self) -> None:
        record = ROOT / "references" / "licenses" / "browserytools.md"

        self.assertTrue(record.is_file(), record)
        text = record.read_text(encoding="utf-8")
        self.assertIn("AGPL-3.0", text)
        self.assertIn("observation-only", text)


if __name__ == "__main__":
    unittest.main()
