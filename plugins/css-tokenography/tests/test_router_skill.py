import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
VALIDATOR = (
    PLUGIN
    / "skills"
    / "css-tokenography"
    / "scripts"
    / "validate_router.py"
)


class RouterSkillTests(unittest.TestCase):
    def run_validator(self, plugin: Path) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(VALIDATOR), "--plugin", str(plugin), "--format", "json"],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_router_surface_is_complete_and_has_the_only_implicit_policy(self) -> None:
        result = self.run_validator(PLUGIN)

        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["router"], "css-tokenography")
        self.assertEqual(report["skills"], 18)
        self.assertEqual(report["guide_skills"], 17)
        self.assertEqual(report["implicit_skills"], ["css-tokenography"])
        self.assertEqual(report["eval_cases"], 8)
        self.assertEqual(report["errors"], [])

    def test_validator_rejects_duplicate_mapping_and_recursive_eval_selection(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "plugin"
            shutil.copytree(PLUGIN, candidate)
            routing_map = (
                candidate
                / "skills"
                / "css-tokenography"
                / "references"
                / "routing-map.md"
            )
            routing_map.write_text(
                routing_map.read_text(encoding="utf-8")
                + "\n- `$css-grid` — duplicate test row.\n",
                encoding="utf-8",
            )
            cases_path = (
                candidate
                / "skills"
                / "css-tokenography"
                / "assets"
                / "routing-eval-cases.json"
            )
            cases = json.loads(cases_path.read_text(encoding="utf-8"))
            cases[0]["required_skills"].append("css-tokenography")
            cases_path.write_text(json.dumps(cases), encoding="utf-8")

            result = self.run_validator(candidate)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertTrue(
            any("duplicates specialists" in error for error in report["errors"])
        )
        self.assertTrue(
            any("must not select the router recursively" in error for error in report["errors"])
        )

    def test_validator_rejects_implicit_specialist_and_eval_overlap(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "plugin"
            shutil.copytree(PLUGIN, candidate)
            specialist_yaml = (
                candidate / "skills" / "css-grid" / "agents" / "openai.yaml"
            )
            specialist_yaml.write_text(
                specialist_yaml.read_text(encoding="utf-8").replace(
                    "allow_implicit_invocation: false",
                    "allow_implicit_invocation: true",
                ),
                encoding="utf-8",
            )
            cases_path = (
                candidate
                / "skills"
                / "css-tokenography"
                / "assets"
                / "routing-eval-cases.json"
            )
            cases = json.loads(cases_path.read_text(encoding="utf-8"))
            cases[0]["forbidden_skills"].append("css-grid")
            cases_path.write_text(json.dumps(cases), encoding="utf-8")

            result = self.run_validator(candidate)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertTrue(
            any("exactly the router" in error for error in report["errors"])
        )
        self.assertTrue(
            any("required and forbidden skills overlap" in error for error in report["errors"])
        )

    def test_validator_distinguishes_eighteen_skills_from_seventeen_guides(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            candidate = Path(directory) / "plugin"
            shutil.copytree(PLUGIN, candidate)
            shutil.rmtree(candidate / "skills" / "web-typography")

            result = self.run_validator(candidate)

        self.assertNotEqual(result.returncode, 0)
        report = json.loads(result.stdout)
        self.assertEqual(report["skills"], 17)
        self.assertEqual(report["guide_skills"], 17)
        self.assertTrue(
            any("exactly 18 skills" in error for error in report["errors"])
        )


if __name__ == "__main__":
    unittest.main()
