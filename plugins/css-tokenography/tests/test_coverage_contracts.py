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
SPECIFICITY_URL = "https://design.dev/tools/specificity-calculator/"
PROCEDURAL_URL = "https://design.dev/tools/gradient-mixer/"


def load_tool_rows() -> list[dict[str, object]]:
    return json.loads(TOOL_COVERAGE.read_text(encoding="utf-8"))


def non_procedural_rows() -> list[dict[str, object]]:
    return [row for row in load_tool_rows() if row["status"] != "procedural"]


def run_validator_with_row_update(
    url: str,
    *,
    extra_files: dict[str, str] | None = None,
    extra_hardlinks: dict[str, str] | None = None,
    extra_symlinks: dict[str, str] | None = None,
    **changes: object,
) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
        for relative_path, content in (extra_files or {}).items():
            path = plugin / relative_path
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
        for relative_path, target in (extra_symlinks or {}).items():
            path = plugin / relative_path
            path.unlink(missing_ok=True)
            path.symlink_to(target)
        for relative_path, target in (extra_hardlinks or {}).items():
            path = plugin / relative_path
            path.unlink(missing_ok=True)
            path.hardlink_to(plugin / target)
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

    def test_inventory_names_all_canonical_non_procedural_clis(self) -> None:
        rows = non_procedural_rows()

        self.assertEqual(
            [row["url"] for row in rows],
            [
                "https://design.dev/tools/color-contrast-checker/",
                "https://design.dev/tools/css-filter-effects/",
                "https://design.dev/tools/backdrop-filter-playground/",
                "https://design.dev/tools/css-transform-playground/",
                "https://design.dev/tools/grid-area-mapper/",
                "https://design.dev/tools/subgrid-visualizer/",
                "https://design.dev/tools/z-index-visualizer/",
                "https://design.dev/tools/clamp-generator/",
                "https://design.dev/tools/px-to-rem-converter/",
                "https://design.dev/tools/specificity-calculator/",
                "https://design.dev/tools/aspect-ratio-calculator/",
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
                slug = str(row["url"]).rstrip("/").rsplit("/", 1)[-1]
                self.assertEqual(Path(str(artifact)).name, slug.replace("-", "_") + ".py")

    def test_contrast_coverage_discloses_apca_exclusion(self) -> None:
        row = next(item for item in load_tool_rows() if item["url"] == CONTRAST_URL)

        self.assertEqual(row["status"], "implemented-core")
        self.assertEqual(
            row["implementation_artifact"],
            "skills/css-variables/scripts/color_contrast_checker.py",
        )
        self.assertEqual(row["validation_fixture"], "tests/fixtures/contrast-threshold-fail.json")
        self.assertIn("exact contrast ratio", row["outputs"])
        self.assertIn("WCAG 2.2 threshold results", row["outputs"])
        self.assertEqual(row["coverage_gap"], None)
        unsupported = row["unsupported_behavior"]
        self.assertEqual(unsupported[0]["behavior"], "APCA")
        self.assertEqual(unsupported[0]["status"], "not-implemented")
        self.assertIn("not a WCAG 3 conformance method", unsupported[0]["reason"])
        self.assertEqual(
            unsupported[0]["references"],
            {
                "official_project": "https://git.apcacontrast.com/documentation/",
                "wcag_3": "https://www.w3.org/TR/wcag-3.0/",
            },
        )

    def test_specificity_coverage_names_level_four_executable_evidence(self) -> None:
        row = next(item for item in load_tool_rows() if item["url"] == SPECIFICITY_URL)

        self.assertEqual(row["status"], "implemented-core")
        self.assertEqual(
            row["implementation_artifact"],
            "skills/css-selectors/scripts/specificity_calculator.py",
        )
        self.assertEqual(row["validation_fixture"], "tests/fixtures/specificity-level-4.json")
        self.assertEqual(row["coverage_gap"], None)
        self.assertIn("per-member specificity tuples", row["outputs"])
        self.assertIn("half-open source spans", row["outputs"])
        self.assertIn("Selectors Level 4 standards notes", row["outputs"])

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

    def test_validator_rejects_owner_local_noncanonical_artifact(self) -> None:
        artifact = "skills/css-grid/scripts/arbitrary.py"
        fixture = "tests/fixtures/arbitrary-subgrid.json"
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={
                artifact: (ROOT / "skills/css-grid/scripts/subgrid_visualizer.py").read_text(
                    encoding="utf-8"
                ),
                fixture: (ROOT / "tests/fixtures/subgrid-valid.json").read_text(encoding="utf-8"),
            },
            implementation_artifact=artifact,
            validation_fixture=fixture,
            validation_command=[
                "python3",
                "{plugin}/" + artifact,
                "--input",
                "{fixture}",
                "--format",
                "json",
            ],
        )

        self.assert_rejected(result, "canonical tool script")

    def test_validator_rejects_canonical_symlink_to_shared_tool(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            extra_symlinks={
                "skills/css-grid/scripts/grid_area_mapper.py": "design_tool.py",
            },
        )

        self.assert_rejected(result, "must not be a symlink")

    def test_validator_rejects_canonical_hardlink_to_shared_tool(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            extra_hardlinks={
                "skills/css-grid/scripts/grid_area_mapper.py": (
                    "skills/css-grid/scripts/design_tool.py"
                ),
            },
        )

        self.assert_rejected(result, "link count must be 1")

    def test_validator_rejects_copied_shared_tool_content(self) -> None:
        canonical_artifact = "skills/css-grid/scripts/grid_area_mapper.py"
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={
                canonical_artifact: (ROOT / "skills/css-grid/scripts/design_tool.py").read_text(
                    encoding="utf-8"
                ),
            },
        )

        self.assert_rejected(result, "duplicates shared design_tool.py content")

    def test_validator_rejects_direct_shared_tool_import(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={
                "skills/css-grid/scripts/grid_area_mapper.py": (
                    "import design_tool\n"
                    "import json\n"
                    "print(json.dumps({'ok': True}))\n"
                ),
            },
        )

        self.assert_rejected(result, "must not reference shared design_tool.py")

    def test_validator_rejects_runpy_delegation_to_shared_tool(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={
                "skills/css-grid/scripts/grid_area_mapper.py": (
                    "import json\n"
                    "from pathlib import Path\n"
                    "import runpy\n"
                    "runpy.run_path(str(Path(__file__).with_name('design_tool.py')), "
                    "run_name='shared_serializer')\n"
                    "print(json.dumps({'ok': True}))\n"
                ),
            },
        )

        self.assert_rejected(result, "must not reference shared design_tool.py")

    def test_validator_rejects_subprocess_delegation_to_shared_tool(self) -> None:
        result = run_validator_with_row_update(
            GRID_URL,
            extra_files={
                "skills/css-grid/scripts/grid_area_mapper.py": (
                    "import json\n"
                    "import subprocess\n"
                    "def delegate():\n"
                    "    return subprocess.run(['python3', 'design_tool.py'], check=False)\n"
                    "print(json.dumps({'ok': True}))\n"
                ),
            },
        )

        self.assert_rejected(result, "must not reference shared design_tool.py")

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
        result = run_validator_with_row_update(PROCEDURAL_URL, coverage_gap=None)

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
                result = run_validator_with_row_update(PROCEDURAL_URL, coverage_gap=coverage_gap)

                self.assert_rejected(result, expected_error)


if __name__ == "__main__":
    unittest.main()
