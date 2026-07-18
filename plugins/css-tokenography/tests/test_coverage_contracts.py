import ast
import json
import shlex
import subprocess
import sys
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


if __name__ == "__main__":
    unittest.main()
