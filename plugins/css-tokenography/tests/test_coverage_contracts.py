import ast
import json
import shlex
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TOOL_COVERAGE = ROOT / "references" / "tool-coverage.json"


def load_tool_rows() -> list[dict[str, object]]:
    return json.loads(TOOL_COVERAGE.read_text(encoding="utf-8"))


def implemented_tool_rows() -> list[dict[str, object]]:
    return [row for row in load_tool_rows() if row["status"] != "procedural"]


def tool_name(row: dict[str, object]) -> str:
    return str(row["url"]).rstrip("/").rsplit("/", 1)[-1]


def run_artifact(row: dict[str, object], *args: str) -> subprocess.CompletedProcess[str]:
    command = shlex.split(str(row["implementation_artifact"]))
    command[0] = str(ROOT / command[0])
    return subprocess.run(
        [sys.executable, *command, *args],
        text=True,
        capture_output=True,
        check=False,
    )


def unittest_method_exists(fixture: str) -> bool:
    relative_path, separator, anchor = fixture.partition("#")
    path = ROOT / relative_path
    if not path.is_file():
        return False
    if not separator:
        return True
    class_name, dot, method_name = anchor.partition(".")
    if not dot or not method_name.startswith("test_"):
        return False
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    return any(
        isinstance(node, ast.ClassDef)
        and node.name == class_name
        and any(
            isinstance(member, (ast.FunctionDef, ast.AsyncFunctionDef))
            and member.name == method_name
            for member in node.body
        )
        for node in tree.body
    )


def run_validator_with_row_update(url: str, **changes: object) -> subprocess.CompletedProcess[str]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
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
    def test_non_procedural_tools_name_unique_evidence(self) -> None:
        evidence = [row["validation_fixture"] for row in implemented_tool_rows()]
        self.assertEqual(len(evidence), len(set(evidence)))

    def test_non_procedural_evidence_resolves_to_a_fixture_or_unittest_method(self) -> None:
        for row in implemented_tool_rows():
            with self.subTest(tool=row["url"]):
                fixture = row["validation_fixture"]
                self.assertIsInstance(fixture, str)
                self.assertTrue(unittest_method_exists(fixture), fixture)

    def test_cli_artifacts_name_existing_tools(self) -> None:
        for row in implemented_tool_rows():
            with self.subTest(tool=row["url"]):
                result = run_artifact(row, "--help")
                self.assertEqual(result.returncode, 0, row["url"])
                if " --tool " in str(row["implementation_artifact"]):
                    self.assertIn(tool_name(row), result.stdout)

    def test_validator_rejects_unanchored_evidence_outside_fixture_directory(self) -> None:
        result = run_validator_with_row_update(
            "https://design.dev/tools/oklch-color-converter/",
            validation_fixture="skills/css-variables/SKILL.md",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("tests/fixtures", result.stdout)

    def test_validator_rejects_fixture_the_artifact_cannot_consume(self) -> None:
        result = run_validator_with_row_update(
            "https://design.dev/tools/oklch-color-converter/",
            validation_fixture="tests/fixtures/subgrid-invalid.json",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("cannot consume validation fixture", result.stdout)

    def test_validator_rejects_existing_non_executable_artifact(self) -> None:
        result = run_validator_with_row_update(
            "https://design.dev/tools/grid-area-mapper/",
            implementation_artifact="tests/fixtures/grid-valid.json",
        )

        self.assertNotEqual(result.returncode, 0, result.stdout)
        self.assertIn("Python CLI", result.stdout)

    def test_validator_requires_structured_downgrade_reasons(self) -> None:
        cases = (
            ("https://design.dev/tools/color-contrast-checker/", "procedural"),
            ("https://design.dev/tools/css-transform-playground/", "serializer-only"),
        )
        for url, status in cases:
            with self.subTest(status=status):
                result = run_validator_with_row_update(url, reason="Coverage is intentionally limited.")

                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("Missing semantic contract:", result.stdout)
                self.assertIn("Restoration task:", result.stdout)


if __name__ == "__main__":
    unittest.main()
