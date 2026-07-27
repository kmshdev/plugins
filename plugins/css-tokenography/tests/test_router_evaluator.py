import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
REPOSITORY = PLUGIN.parents[1]
EVALUATOR_PATH = (
    PLUGIN / "skills" / "css-tokenography" / "scripts" / "evaluate_routes.py"
)


def load_evaluator():
    spec = importlib.util.spec_from_file_location("evaluate_routes", EVALUATOR_PATH)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load evaluator")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FakeCodex:
    def __init__(
        self,
        *,
        fail_install: bool = False,
        semantic_miss: bool = False,
        fail_first_exec: bool = False,
        fail_restore: bool = False,
        duplicate_disclosure: bool = False,
    ) -> None:
        self.fail_install = fail_install
        self.semantic_miss = semantic_miss
        self.fail_first_exec = fail_first_exec
        self.fail_restore = fail_restore
        self.duplicate_disclosure = duplicate_disclosure
        self.marketplace = {
            "name": "kmshdev",
            "root": "/tmp/kmshdev",
            "marketplaceSource": {
                "sourceType": "git",
                "source": "https://github.com/kmshdev/plugins.git",
            },
        }
        self.installed: list[dict[str, object]] = []
        self.commands: list[tuple[str, ...]] = []
        self.exec_attempts = 0

    def completed(
        self,
        command: tuple[str, ...],
        returncode: int = 0,
        stdout: str = "",
        stderr: str = "",
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.CompletedProcess(command, returncode, stdout, stderr)

    def __call__(
        self, command: tuple[str, ...] | list[str], _cwd: Path | None
    ) -> subprocess.CompletedProcess[str]:
        command = tuple(command)
        self.commands.append(command)
        if command[:4] == ("codex", "plugin", "marketplace", "list"):
            rows = [] if self.marketplace is None else [self.marketplace]
            return self.completed(command, stdout=json.dumps({"marketplaces": rows}))
        if command[:3] == ("codex", "plugin", "list"):
            return self.completed(
                command,
                stdout=json.dumps({"installed": self.installed, "available": []}),
            )
        if command[:4] == ("codex", "plugin", "marketplace", "remove"):
            self.marketplace = None
            return self.completed(command, stdout="{}")
        if command[:4] == ("codex", "plugin", "marketplace", "add"):
            source = command[4]
            if source == "kmshdev/plugins" and self.fail_restore:
                return self.completed(command, 1, stderr="restore failed")
            if source == "kmshdev/plugins":
                source = "https://github.com/kmshdev/plugins.git"
                source_type = "git"
            else:
                source_type = "local"
            self.marketplace = {
                "name": "kmshdev",
                "root": "/tmp/kmshdev",
                "marketplaceSource": {"sourceType": source_type, "source": source},
            }
            return self.completed(command, stdout="{}")
        if command[:3] == ("codex", "plugin", "add"):
            if self.fail_install and not self.installed:
                return self.completed(command, 1, stderr="install failed")
            self.installed = [
                {
                    "pluginId": "css-tokenography@kmshdev",
                    "marketplaceName": "kmshdev",
                    "version": "0.1.0",
                    "enabled": True,
                    "installed": True,
                }
            ]
            return self.completed(command, stdout="{}")
        if command[:3] == ("codex", "plugin", "remove"):
            self.installed = []
            return self.completed(command, stdout="{}")
        if command[:2] == ("codex", "exec"):
            self.exec_attempts += 1
            if self.fail_first_exec and self.exec_attempts == 1:
                return self.completed(command, 1, stderr="temporary transport failure")
            final_path = Path(command[command.index("--output-last-message") + 1])
            prompt = command[-1]
            selected = self.skills_for_prompt(prompt)
            if self.semantic_miss:
                selected = []
            implicit = "$css-selectors" not in prompt and "$web-typography" not in prompt
            payload = {
                "protocol": (
                    "css-tokenography-routing/v1"
                    if implicit
                    else "explicit-specialist/v1"
                ),
                "selected_skills": selected,
                "disclosure": (
                    "CSS Tokenography route: "
                    + ", ".join(f"${skill}" for skill in selected)
                    + " — evaluation route."
                    if implicit
                    else ""
                ),
                "semantic_retry": False,
            }
            final_path.write_text(json.dumps(payload), encoding="utf-8")
            events = [
                {
                    "type": "item.completed",
                    "item": {
                        "type": "command_execution",
                        "command": " ".join(
                            f"/cache/skills/{skill}/SKILL.md" for skill in selected
                        ),
                    },
                }
            ]
            if self.duplicate_disclosure and implicit:
                events.append(
                    {
                        "type": "item.completed",
                        "item": {
                            "type": "agent_message",
                            "text": "CSS Tokenography route: provisional route.",
                        },
                    }
                )
            events.extend(
                [
                    {
                        "type": "item.completed",
                        "item": {
                            "type": "agent_message",
                            "text": json.dumps(payload),
                        },
                    },
                    {
                        "type": "turn.completed",
                        "usage": {"input_tokens": 10, "output_tokens": 5},
                    },
                ]
            )
            return self.completed(
                command,
                stdout="".join(json.dumps(event) + "\n" for event in events),
            )
        return self.completed(command, 1, stderr="unexpected command")

    @staticmethod
    def skills_for_prompt(prompt: str) -> list[str]:
        if "named CSS Grid" in prompt:
            return ["css-grid"]
        if "Lighthouse JSON" in prompt:
            return ["web-performance-optimization"]
        if "semantic color tokens" in prompt:
            return ["css-dark-mode", "css-variables"]
        if "card hover effect" in prompt:
            return ["css-transforms", "css-transitions"]
        if "visual system feels coherent" in prompt:
            return ["css-grid", "css-variables", "web-typography"]
        if "responsive card collection" in prompt:
            return [
                "css-grid",
                "css-flexbox",
                "css-media-queries",
                "css-container-queries",
            ]
        if "$css-selectors" in prompt:
            return ["css-selectors"]
        if "$web-typography" in prompt:
            return ["web-typography"]
        return []


class RouterEvaluatorTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.evaluator = load_evaluator()

    def evaluate(self, fake: FakeCodex) -> dict[str, object]:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "evaluation"
            return self.evaluator.evaluate(
                REPOSITORY, PLUGIN, output, runner=fake
            )

    def test_dry_run_plan_has_no_side_effects(self) -> None:
        cases = self.evaluator.load_cases(
            PLUGIN
            / "skills"
            / "css-tokenography"
            / "assets"
            / "routing-eval-cases.json"
        )
        plan = self.evaluator.command_plan(REPOSITORY, cases)

        self.assertEqual(len(plan), 14)
        self.assertEqual(plan[0][:5], ["codex", "plugin", "marketplace", "remove", "kmshdev"])
        self.assertEqual(plan[-1][-3:], ["--ref", "main", "--json"])

    def test_all_cases_pass_and_state_is_restored(self) -> None:
        fake = FakeCodex()

        report = self.evaluate(fake)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(report["passed"], 8)
        self.assertEqual(report["pass_rate"], 1.0)
        self.assertTrue(report["state_restored"])
        self.assertEqual(fake.installed, [])
        self.assertEqual(
            fake.marketplace["marketplaceSource"]["source"],
            "https://github.com/kmshdev/plugins.git",
        )

    def test_install_failure_still_cleans_up_and_restores(self) -> None:
        fake = FakeCodex(fail_install=True)

        report = self.evaluate(fake)

        self.assertEqual(report["status"], "fail")
        self.assertTrue(any("install failed" in error for error in report["errors"]))
        self.assertEqual(fake.installed, [])
        self.assertIsNotNone(fake.marketplace)

    def test_semantic_miss_is_not_retried(self) -> None:
        fake = FakeCodex(semantic_miss=True)

        report = self.evaluate(fake)

        self.assertEqual(report["status"], "fail")
        self.assertEqual(fake.exec_attempts, 8)
        self.assertTrue(
            any(case["errors"] for case in report["cases"])
        )

    def test_infrastructure_failure_gets_exactly_one_retry(self) -> None:
        fake = FakeCodex(fail_first_exec=True)

        report = self.evaluate(fake)

        self.assertEqual(report["status"], "pass")
        self.assertEqual(fake.exec_attempts, 9)
        self.assertEqual(report["cases"][0]["infrastructure_attempts"], 2)

    def test_restoration_failure_is_reported(self) -> None:
        fake = FakeCodex(fail_restore=True)

        report = self.evaluate(fake)

        self.assertEqual(report["status"], "fail")
        self.assertFalse(report["state_restored"])
        self.assertTrue(
            any("marketplace restoration failed" in error for error in report["errors"])
        )

    def test_duplicate_session_disclosure_is_rejected(self) -> None:
        fake = FakeCodex(duplicate_disclosure=True)

        report = self.evaluate(fake)

        self.assertEqual(report["status"], "fail")
        self.assertTrue(
            any(
                "session must emit exactly one routing disclosure" in error
                for case in report["cases"]
                for error in case["errors"]
            )
        )


if __name__ == "__main__":
    unittest.main()
