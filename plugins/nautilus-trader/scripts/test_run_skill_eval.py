"""Offline runner regressions; use the existing SkillEvaluator interpreter for YAML."""

from __future__ import annotations

import argparse
import copy
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import run_skill_eval as runner


class RunnerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="skill-runner-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)

    def skill(self, name: str = "arbitrary-python-skill") -> Path:
        root = self.root / "skills" / name
        root.mkdir(parents=True)
        (root / "SKILL.md").write_text(f"---\nname: {name}\ndescription: A test skill.\n---\nDo the task.\n")
        (root / "evals").mkdir()
        for filename in ("evals.json", "acceptance.json", "fresh-v2.json"):
            (root / "evals" / filename).write_text(json.dumps({
                "skill_name": name, "evals": [{"id": filename, "prompt": "Synthetic test"}],
            }))
        return root

    def result(self) -> dict:
        scores = {dimension: 0.0 for dimension in runner.DIMENSIONS}
        return {
            "execution_status": "succeeded", "report_status": "complete",
            "expected_attempts": 2, "scored_attempts": 2,
            "agents": {"opencode": {
                "execution_status": "succeeded", "num_trials_with": 1, "num_trials_without": 1,
                "with_skill": scores.copy(), "without_skill": scores.copy(), "execution_errors": 0,
            }},
        }

    def test_discovers_unrelated_new_skills_without_name_list(self) -> None:
        first, second = self.skill(), self.skill("writing-sql")
        self.assertEqual(runner.discover([self.root / "skills"]), sorted([first.resolve(), second.resolve()]))
        self.assertEqual(runner.skill_name(first), "arbitrary-python-skill")

    def test_discovery_stops_at_skill_boundary(self) -> None:
        skill = self.skill()
        nested = skill / "assets" / "template"
        nested.mkdir(parents=True)
        (nested / "SKILL.md").write_text("A template, not an installed skill")
        self.assertEqual(runner.discover([self.root / "skills"]), [skill.resolve()])

    def test_ambiguous_plugin_root_requires_explicit_choice(self) -> None:
        self.skill()
        (self.root / "SKILL.md").write_text("legacy")
        with self.assertRaisesRegex(ValueError, "Choose"):
            runner.discover([self.root])

    def test_rejects_symlink_and_credentials_before_copy(self) -> None:
        skill = self.skill()
        (skill / "escape").symlink_to(self.root)
        with self.assertRaisesRegex(ValueError, "Symlinks"):
            runner.files(skill)
        (skill / "escape").unlink()
        (skill / ".env.private").write_text("DO_NOT_COPY=synthetic")
        with self.assertRaisesRegex(ValueError, "Credential-like"):
            runner.files(skill)

    def test_content_fingerprint_not_mtime(self) -> None:
        skill = self.skill()
        before = runner.tree_digest(skill)
        os.utime(skill / "SKILL.md", None)
        self.assertEqual(before, runner.tree_digest(skill))
        (skill / "SKILL.md").write_text("Different")
        self.assertNotEqual(before, runner.tree_digest(skill))

    def test_transient_build_output_excluded(self) -> None:
        skill = self.skill()
        before = runner.tree_digest(skill)
        (skill / "target").mkdir()
        (skill / "target" / "compiled").write_text("not an input")
        self.assertEqual(before, runner.tree_digest(skill))

    def test_patch_is_idempotent_and_rejects_unknown_source(self) -> None:
        for old, new in runner.PATCHES.values():
            self.assertEqual(runner.patch_source(old, old, new), new)
            self.assertEqual(runner.patch_source(new, old, new), new)
            with self.assertRaises(ValueError):
                runner.patch_source("changed upstream", old, new)

    def test_neon_and_native_routes(self) -> None:
        self.assertEqual(runner.agent_base("https://unit.neon.tech/v1", "auto", None),
                         "https://unit.neon.tech/openai/v1")
        self.assertEqual(runner.agent_base("https://unit.example/v1", "neon", None),
                         "https://unit.example/openai/v1")
        self.assertIsNone(runner.agent_base("https://api.openai.com/v1", "auto", None))
        self.assertIsNone(runner.agent_base("https://unit.neon.tech/v1", "none", None))

    def test_override_rejects_cross_origin_and_embedded_credentials(self) -> None:
        for destination in ("https://other.example/v1", "https://secret@unit.example/v1",
                            "https://unit.example/v1?key=secret"):
            with self.subTest(destination=destination), self.assertRaises(ValueError):
                runner.agent_base("https://unit.example/v1", "none", destination)

    def test_custom_dataset_staging_preserves_source_and_runtime_config(self) -> None:
        skill = self.skill()
        config = {"schema_version": 1, "harbor": {"runtime_env": {
            "OTHER_INPUT": "retained", "OPENCODE_CONFIG_CONTENT": json.dumps({
                "provider": {"openai": {"options": {"timeout": 123}}}, "theme": "test",
            }),
        }}}
        (skill / "evals/config.yml").write_text(json.dumps(config))
        before = runner.tree_digest(skill)
        target = self.root / "copy"
        runner.stage_skill(skill, target, "evals/fresh-v2.json", True, "https://unit.example/openai/v1")
        self.assertEqual(before, runner.tree_digest(skill))
        self.assertFalse((target / "evals/acceptance.json").exists())
        self.assertFalse((target / "evals/fresh-v2.json").exists())
        self.assertEqual(json.loads((target / "evals/evals.json").read_text())["evals"][0]["id"], "fresh-v2.json")
        import yaml
        runtime = yaml.safe_load((target / "evals/config.yml").read_text())["harbor"]["runtime_env"]
        self.assertEqual(runtime["OTHER_INPUT"], "retained")
        options = json.loads(runtime["OPENCODE_CONFIG_CONTENT"])["provider"]["openai"]["options"]
        self.assertEqual(options["timeout"], 123)
        self.assertEqual(options["apiKey"], "{env:OPENAI_API_KEY}")

    def test_missing_requested_dataset_cannot_fall_back_to_working(self) -> None:
        target = self.root / "copy"
        runner.stage_skill(self.skill(), target, "evals/missing.json", True, None)
        self.assertFalse((target / "evals/evals.json").exists())

    def test_dataset_escape_rejected(self) -> None:
        with self.assertRaisesRegex(ValueError, "inside"):
            runner.stage_skill(self.skill(), self.root / "copy", "../outside.json", True, None)

    def test_non_tier3_skill_does_not_need_evaluations(self) -> None:
        skill = self.skill()
        for path in (skill / "evals").iterdir():
            path.unlink()
        (skill / "evals").rmdir()
        runner.stage_skill(skill, self.root / "copy", "working", False, None)
        self.assertTrue((self.root / "copy/SKILL.md").exists())

    def test_conflicting_sdk_rejected(self) -> None:
        skill = self.skill()
        (skill / "evals/config.yml").write_text(json.dumps({"harbor": {"runtime_env": {
            "OPENCODE_CONFIG_CONTENT": json.dumps({"provider": {"openai": {"npm": "@ai-sdk/openai-compatible"}}}),
        }}}))
        with self.assertRaisesRegex(ValueError, "native OpenAI SDK"):
            runner.stage_skill(skill, self.root / "copy", "working", True, "https://unit.example/openai/v1")

    def test_low_scores_are_completed_results_not_infrastructure_failures(self) -> None:
        self.assertTrue(runner.complete_tier3(self.result(), 1))

    def test_partial_unpaired_missing_scores_and_errors_rejected(self) -> None:
        for mutate in (
            lambda r: r.update(scored_attempts=1),
            lambda r: r.update(report_status="partial"),
            lambda r: r["agents"]["opencode"].update(num_trials_without=0),
            lambda r: r["agents"]["opencode"]["with_skill"].pop("accuracy"),
            lambda r: r["agents"]["opencode"]["with_skill"].update(accuracy=float("nan")),
            lambda r: r["agents"]["opencode"].update(execution_errors=1),
        ):
            result = copy.deepcopy(self.result())
            mutate(result)
            self.assertFalse(runner.complete_tier3(result, 1))

    def test_trial_json_is_not_a_second_canonical_report(self) -> None:
        canonical = self.root / "skill/run/result.json"
        canonical.parent.mkdir(parents=True)
        canonical.write_text(json.dumps(self.result()))
        trial = canonical.parent / "opencode/with-skill/trials/test/result.json"
        trial.parent.mkdir(parents=True)
        trial.write_text("{}")
        self.assertTrue(runner.behavior_report_complete(self.root, 1))
        canonical.write_text("{broken")
        self.assertFalse(runner.behavior_report_complete(self.root, 1))

    def test_two_canonical_runs_cannot_be_combined(self) -> None:
        for run in ("run-one", "run-two"):
            path = self.root / "skill" / run / "result.json"
            path.parent.mkdir(parents=True)
            path.write_text(json.dumps(self.result()))
        self.assertFalse(runner.behavior_report_complete(self.root, 1))

    def test_commands_preserve_baseline_preflight_and_scoring(self) -> None:
        args = argparse.Namespace(n_concurrent=1, timeout_multiplier=2.0)
        command = runner.evaluator_args("behavior", self.root, self.root / "out", "test-model",
                                        "openai/test-model", args)
        self.assertIn("skillevaluator.cli", command)
        self.assertIn("--agent-runtime-preflight", command)
        self.assertIn("--no-stop-on-pass", command)
        self.assertNotIn("--skip-baseline", command)
        self.assertNotIn("--copy-repo", command)
        self.assertNotIn("--autopilot", command)
        self.assertIn("isolated", command)

    def test_redacts_file_loaded_credentials_and_urls(self) -> None:
        value = runner.redact("key=synthetic-secret https://unit.example/v1 model=private-model",
                              {"SKILL_EVAL_LLM_API_KEY": "synthetic-secret", "SKILL_EVAL_LLM_MODEL": "private-model"})
        self.assertNotIn("synthetic-secret", value)
        self.assertNotIn("unit.example", value)
        self.assertNotIn("private-model", value)

    def test_real_subprocess_exit_and_redacted_log(self) -> None:
        output = self.root / "command"
        result = runner.command([sys.executable, "-c", "print('synthetic-secret'); raise SystemExit(7)"],
                                {**os.environ, "TEST_API_KEY": "synthetic-secret"}, output, 5)
        self.assertEqual(result["returncode"], 7)
        self.assertEqual(result["status"], "finished")
        self.assertNotIn("synthetic-secret", (output / "command.log").read_text())
        self.assertFalse((output / "stdout.private").exists())

    def test_real_subprocess_timeout_is_not_success(self) -> None:
        result = runner.command([sys.executable, "-c", "import time; time.sleep(60)"],
                                os.environ.copy(), self.root / "timeout", 0.1)
        self.assertEqual(result["status"], "timed_out")
        self.assertEqual(result["returncode"], 124)

    def test_docker_missing_is_explicit_unavailable(self) -> None:
        with patch.object(runner.subprocess, "run", side_effect=FileNotFoundError):
            self.assertFalse(runner.docker_ready())

    def test_stages_do_not_depend_on_five_workflow_names(self) -> None:
        skills = {"writing-sql": self.root / "skills/writing-sql"}
        kinds = [kind for _, kind, _ in runner.stages(skills, {"1", "2", "3"})]
        self.assertEqual(kinds, ["static", "rubric", "context", "strict", "behavior"])
        skills["making-pdfs"] = self.root / "skills/making-pdfs"
        kinds = [kind for _, kind, _ in runner.stages(skills, {"2"})]
        self.assertEqual(kinds, ["context", "context", "descriptions", "full-body"])


if __name__ == "__main__":
    unittest.main()
