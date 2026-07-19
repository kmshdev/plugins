import json
import shutil
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


class AdapterRegistryTests(unittest.TestCase):
    def test_optional_adapters_do_not_require_installed_commands(self) -> None:
        report = validate(ROOT)

        self.assertEqual(report["errors"], [])
        self.assertIn("lightningcss", [row["id"] for row in report["adapters"]])

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
