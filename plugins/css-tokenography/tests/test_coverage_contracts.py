import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL_COVERAGE = ROOT / "references" / "tool-coverage.json"
GRID_URL = "https://design.dev/tools/grid-area-mapper/"
CONTRAST_URL = "https://design.dev/tools/color-contrast-checker/"


def load_tool_rows() -> list[dict[str, object]]:
    return json.loads(TOOL_COVERAGE.read_text(encoding="utf-8"))


def non_procedural_rows() -> list[dict[str, object]]:
    return [row for row in load_tool_rows() if row["status"] != "procedural"]


def run_validator_with_row_update(
    url: str,
    *,
    extra_files: dict[str, str] | None = None,
    **changes: object,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
        for relative_path, content in (extra_files or {}).items():
            path = plugin / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        coverage = plugin / "references" / "tool-coverage.json"
        rows = json.loads(coverage.read_text(encoding="utf-8"))
        row = next(item for item in rows if item["url"] == url)
        row.update(changes)
        coverage.write_text(json.dumps(rows), encoding="utf-8")
        return subprocess.run(
            [
                sys.executable,
                str(ROOT / "scripts" / "validate_coverage.py"),
                "--plugin",
                str(plugin),
                "--format",
                "json",
            ],
            text=True,
            capture_output=True,
            check=False,
        )


class CoverageContractTests(unittest.TestCase):
    def assert_rejected(self, result: subprocess.CompletedProcess[str], message: str) -> None:
        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn(message, result.stdout)

    def test_inventory_keeps_only_grid_clis_non_procedural(self) -> None:
        rows = non_procedural_rows()

        self.assertEqual(
            [row["url"] for row in rows],
            [
                "https://design.dev/tools/grid-area-mapper/",
                "https://design.dev/tools/subgrid-visualizer/",
            ],
        )
        for row in rows:
            with self.subTest(tool=row["url"]):
                owner = row["owner"]
                artifact = row["implementation_artifact"]
                self.assertIsInstance(artifact, str)
                self.assertTrue(str(artifact).startswith(f"skills/{owner}/scripts/"))
                self.assertTrue(str(artifact).endswith(".py"))
                self.assertNotEqual(Path(str(artifact)).name, "design_tool.py")

    def test_non_procedural_rows_name_object_fixtures_and_explicit_commands(self) -> None:
        for row in non_procedural_rows():
            with self.subTest(tool=row["url"]):
                fixture = ROOT / str(row["validation_fixture"])
                self.assertTrue(fixture.is_relative_to(ROOT / "tests" / "fixtures"))
                self.assertTrue(fixture.is_file(), fixture)
                self.assertIsInstance(json.loads(fixture.read_text(encoding="utf-8")), dict)
                command = row.get("validation_command")
                self.assertIsInstance(command, list)
                assert isinstance(command, list)
                self.assertIn("{fixture}", command)
                self.assertIn(
                    "{plugin}/" + str(row["implementation_artifact"]),
                    command,
                )

    def test_validator_rejects_arbitrary_python_artifact(self) -> None:
        artifact = "tests/arbitrary.py"
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={artifact: "import json\nprint(json.dumps({'ok': True}))\n"},
            implementation_artifact=artifact,
            validation_command=["python3", "{plugin}/" + artifact, "{fixture}"],
        )

        self.assert_rejected(result, "owner-bound Python CLI")

    def test_validator_rejects_arbitrary_json_artifact(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            implementation_artifact="tests/fixtures/grid-valid.json",
            validation_command=[
                "python3",
                "{plugin}/tests/fixtures/grid-valid.json",
                "{fixture}",
            ],
        )

        self.assert_rejected(result, "owner-bound Python CLI")

    def test_validator_rejects_shared_design_tool(self) -> None:
        artifact = "skills/css-grid/scripts/design_tool.py"
        result = run_validator_with_row_update(
            GRID_URL,
            implementation_artifact=artifact,
            validation_command=["python3", "{plugin}/" + artifact, "{fixture}"],
        )

        self.assert_rejected(result, "standalone owner CLI")

    def test_validator_rejects_wrong_owner(self) -> None:
        artifact = "skills/css-functions/scripts/grid_area_mapper.py"
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={artifact: "import json\nprint(json.dumps({'ok': True}))\n"},
            implementation_artifact=artifact,
            validation_command=["python3", "{plugin}/" + artifact, "{fixture}"],
        )

        self.assert_rejected(result, "owner-bound Python CLI")

    def test_validator_rejects_mismatched_artifact_command(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            validation_command=[
                "python3",
                "{plugin}/skills/css-grid/scripts/subgrid_visualizer.py",
                "--input",
                "{fixture}",
                "--format",
                "json",
            ],
        )

        self.assert_rejected(result, "must invoke declared implementation artifact")

    def test_validator_rejects_mismatched_fixture_command(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            validation_command=[
                "python3",
                "{plugin}/skills/css-grid/scripts/grid_area_mapper.py",
                "--input",
                "{plugin}/tests/fixtures/subgrid-valid.json",
                "--format",
                "json",
            ],
        )

        self.assert_rejected(result, "must invoke declared validation fixture")

    def test_validator_rejects_failing_validation_command(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            validation_fixture="tests/fixtures/grid-disconnected.json",
        )

        self.assert_rejected(result, "validation command failed")

    def test_validator_rejects_non_json_command_output(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            validation_command=[
                "python3",
                "{plugin}/skills/css-grid/scripts/grid_area_mapper.py",
                "--input",
                "{fixture}",
                "--format",
                "css",
            ],
        )

        self.assert_rejected(result, "must emit a JSON object")

    def test_validator_rejects_non_object_fixture(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={"tests/fixtures/arbitrary.json": "[]\n"},
            validation_fixture="tests/fixtures/arbitrary.json",
        )

        self.assert_rejected(result, "JSON object under tests/fixtures")

    def test_validator_requires_coverage_gap_object(self) -> None:
        result = run_validator_with_row_update(CONTRAST_URL, coverage_gap=None)

        self.assert_rejected(result, "requires a coverage_gap object")

    def test_validator_rejects_malformed_coverage_gap_fields(self) -> None:
        cases = (
            (
                "missing contract",
                {
                    "missing_contract": "APCA vectors",
                    "restoration_artifact": "skills/css-variables/scripts/color_contrast_checker.py",
                    "restoration_tests": ["tests/test_color_contrast.py"],
                    "acceptance": ["Reports APCA contrast from independent vectors"],
                },
                "missing_contract must be a non-empty array",
            ),
            (
                "wrong restoration owner",
                {
                    "missing_contract": ["APCA vectors"],
                    "restoration_artifact": "skills/css-grid/scripts/color_contrast_checker.py",
                    "restoration_tests": ["tests/test_color_contrast.py"],
                    "acceptance": ["Reports APCA contrast from independent vectors"],
                },
                "restoration_artifact must be owner-bound",
            ),
            (
                "missing restoration tests",
                {
                    "missing_contract": ["APCA vectors"],
                    "restoration_artifact": "skills/css-variables/scripts/color_contrast_checker.py",
                    "restoration_tests": [],
                    "acceptance": ["Reports APCA contrast from independent vectors"],
                },
                "restoration_tests must be a non-empty array",
            ),
            (
                "restoration test outside tests",
                {
                    "missing_contract": ["APCA vectors"],
                    "restoration_artifact": "skills/css-variables/scripts/color_contrast_checker.py",
                    "restoration_tests": ["skills/css-variables/SKILL.md"],
                    "acceptance": ["Reports APCA contrast from independent vectors"],
                },
                "restoration_tests entries must be paths under tests/",
            ),
            (
                "missing acceptance",
                {
                    "missing_contract": ["APCA vectors"],
                    "restoration_artifact": "skills/css-variables/scripts/color_contrast_checker.py",
                    "restoration_tests": ["tests/test_color_contrast.py"],
                    "acceptance": [],
                },
                "acceptance must be a non-empty array",
            ),
        )
        for name, coverage_gap, expected_error in cases:
            with self.subTest(case=name):
                result = run_validator_with_row_update(CONTRAST_URL, coverage_gap=coverage_gap)

                self.assert_rejected(result, expected_error)


if __name__ == "__main__":
    unittest.main()
