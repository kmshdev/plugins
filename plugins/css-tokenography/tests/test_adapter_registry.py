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


def validate_copy(
    changes: dict[str, object], *, adapter_id: str = "lightningcss"
) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
        registry = plugin / "references" / "automation-adapters.json"
        rows = json.loads(registry.read_text(encoding="utf-8"))
        row = next(value for value in rows if value["id"] == adapter_id)
        row.update(changes)
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
        self.assertEqual(
            [row["id"] for row in report["adapters"]],
            ["lightningcss", "playwright", "passmark", "stagehand"],
        )
        passmark = next(row for row in report["adapters"] if row["id"] == "passmark")
        self.assertEqual(passmark["adoption"], "approved-internal-use-only")
        self.assertEqual(passmark["kind"], "node-package")
        self.assertNotIn("command", passmark)

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

    def test_restricted_adapters_must_remain_optional(self) -> None:
        report = validate_copy({"adoption": "blocked-pending-review", "required": True})

        self.assertIn(
            "adapter lightningcss restricted adoption must remain optional",
            report["errors"],
        )

    def test_node_packages_are_pinned_in_declared_workspaces(self) -> None:
        wrong_version = validate_copy(
            {"version": "0.0.0"}, adapter_id="passmark"
        )
        command = validate_copy(
            {"command": ["passmark", "--version"]}, adapter_id="passmark"
        )

        self.assertIn(
            "adapter passmark workspace must pin passmark exactly to 0.0.0",
            wrong_version["errors"],
        )
        self.assertIn(
            "adapter passmark node-package must not declare a command",
            command["errors"],
        )

    def test_registry_requires_activation_network_and_credential_contracts(self) -> None:
        bad_activation = validate_copy({"activation": "implicit"})
        bad_network = validate_copy({"network": "unknown"})
        bad_credentials = validate_copy({"credentials": ["TOKEN", "TOKEN"]})

        self.assertIn(
            "adapter lightningcss has invalid activation 'implicit'",
            bad_activation["errors"],
        )
        self.assertIn(
            "adapter lightningcss has invalid network mode 'unknown'",
            bad_network["errors"],
        )
        self.assertIn(
            "adapter lightningcss credentials must not contain duplicates",
            bad_credentials["errors"],
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

    def test_passmark_license_record_scopes_internal_use(self) -> None:
        record = ROOT / "references" / "licenses" / "passmark.md"

        self.assertTrue(record.is_file(), record)
        text = record.read_text(encoding="utf-8")
        self.assertIn("FSL-1.1-ALv2", text)
        self.assertIn("approved-internal-use-only", text)
        self.assertIn("2028-06-08", text)

    def test_playwright_and_stagehand_license_records_are_explicit(self) -> None:
        playwright = (
            ROOT / "references" / "licenses" / "playwright.md"
        ).read_text(encoding="utf-8")
        stagehand = (
            ROOT / "references" / "licenses" / "stagehand.md"
        ).read_text(encoding="utf-8")

        self.assertIn("@playwright/test@1.62.0", playwright)
        self.assertIn("@browserbasehq/stagehand@3.7.1", stagehand)
        self.assertIn("experimental-discovery-only", stagehand)

    def test_browserytools_license_record_is_observation_only(self) -> None:
        record = ROOT / "references" / "licenses" / "browserytools.md"

        self.assertTrue(record.is_file(), record)
        text = record.read_text(encoding="utf-8")
        self.assertIn("AGPL-3.0", text)
        self.assertIn("observation-only", text)


if __name__ == "__main__":
    unittest.main()
