"""Offline regression cases for bundle portability, using only the standard library."""

from __future__ import annotations

import json
import re
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import check
import sync_resources


class BundleContractTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="nautilus-skill-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve() / "relocated-skill"
        shutil.copytree(
            check.ROOT,
            self.root,
            ignore=shutil.ignore_patterns("target", "__pycache__", "results"),
        )
        root_patch = patch.object(check, "ROOT", self.root)
        root_patch.start()
        self.addCleanup(root_patch.stop)

    def append_link(self, target: str) -> None:
        path = self.root / "README.md"
        path.write_text(
            path.read_text(encoding="utf-8") + f"\n[fixture]({target})\n",
            encoding="utf-8",
        )

    def test_relocated_bundle_without_source_checkout(self) -> None:
        self.assertEqual(check.check_bundle(), [])
        result = subprocess.run(
            [sys.executable, str(self.root / "scripts/check.py")],
            cwd=self.temporary.name,
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("Portable skill contract passed", result.stdout)

    def test_missing_local_link(self) -> None:
        self.append_link("not-present.md")
        self.assertTrue(any("Missing local link" in error for error in check.check_bundle()))

    def test_encoded_parent_escape(self) -> None:
        self.append_link("%2e%2e/outside.md")
        self.assertTrue(any("Link escapes bundle" in error for error in check.check_bundle()))

    def test_absolute_local_path(self) -> None:
        self.append_link("/Users/example/private.md")
        self.assertTrue(any("Machine-local reference" in error for error in check.check_bundle()))

    def test_symlink_dependency(self) -> None:
        (self.root / "alias.md").symlink_to(self.root / "README.md")
        self.assertTrue(any("symlinks" in error for error in check.check_bundle()))

    def test_unpinned_nautilus_dependency(self) -> None:
        path = self.root / "examples/quickstart/Cargo.toml"
        path.write_text(
            path.read_text(encoding="utf-8").replace('version = "=0.64.0"', 'version = "0.63"'),
            encoding="utf-8",
        )
        self.assertTrue(any("Unpinned framework" in error for error in check.check_bundle()))

    def test_every_canonical_example_is_checked(self) -> None:
        path = self.root / "examples/live-composition/Cargo.toml"
        path.write_text(
            path.read_text(encoding="utf-8").replace('version = "=0.64.0"', 'version = "0.63"'),
            encoding="utf-8",
        )
        self.assertTrue(any("live-composition/Cargo.toml" in error for error in check.check_bundle()))

    def test_python_feature(self) -> None:
        path = self.root / "examples/quickstart/Cargo.toml"
        path.write_text(
            path.read_text(encoding="utf-8").replace(
                "default-features = false }",
                'default-features = false, features = ["python"] }',
            ),
            encoding="utf-8",
        )
        self.assertTrue(any("requests Python" in error for error in check.check_bundle()))

    def test_missing_source_inventory(self) -> None:
        path = self.root / "source-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"].pop()
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("inventory differ" in error for error in check.check_bundle()))

    def test_invalid_digest(self) -> None:
        path = self.root / "source-manifest.json"
        manifest = json.loads(path.read_text(encoding="utf-8"))
        manifest["files"][0]["sha256"] = "unverified"
        path.write_text(json.dumps(manifest), encoding="utf-8")
        self.assertTrue(any("Invalid source digest" in error for error in check.check_bundle()))

    def test_evaluation_route_escape(self) -> None:
        path = self.root / "evals/evals.json"
        dataset = json.loads(path.read_text(encoding="utf-8"))
        dataset["evals"][0]["references"] = ["../outside.md"]
        path.write_text(json.dumps(dataset), encoding="utf-8")
        self.assertTrue(any("Invalid evaluation route" in error for error in check.check_bundle()))

    def test_each_workflow_alone_outside_bundle(self) -> None:
        for name in sync_resources.ANCHORS:
            with self.subTest(skill=name):
                isolated = Path(self.temporary.name).resolve() / name
                shutil.copytree(self.root / "skills" / name, isolated)
                self.assertEqual(check.check_skill(isolated), [])
                result = subprocess.run(
                    [sys.executable, str(self.root / "scripts/check.py"), "--skill", str(isolated)],
                    cwd=isolated,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)

    def test_sibling_link_is_not_independent(self) -> None:
        actor = self.root / "skills/building-nautilus-actors/SKILL.md"
        actor.write_text(actor.read_text() + "\n[other](../building-nautilus-strategies/SKILL.md)\n")
        self.assertTrue(any("escapes independent" in error for error in check.check_bundle()))

    def test_generated_resource_drift(self) -> None:
        foundation = self.root / "skills/building-nautilus-actors/references/foundation.md"
        foundation.write_text(foundation.read_text() + "\nChanged fixture.\n")
        self.assertTrue(any("resource drift" in error for error in check.check_bundle()))

    def test_working_case_cannot_be_held_out(self) -> None:
        directory = self.root / "skills/building-nautilus-actors/evals"
        data = json.loads((directory / "evals.json").read_text())
        (directory / "acceptance.json").write_text(json.dumps(data))
        self.assertTrue(any("case reused" in error for error in check.check_bundle()))

    def test_implicit_task_input_staging_rejected(self) -> None:
        path = self.root / "skills/building-nautilus-actors/evals/evals.json"
        data = json.loads(path.read_text())
        del data["evals"][0]["files"]
        path.write_text(json.dumps(data))
        self.assertTrue(any("Unexpected evaluator staging" in error for error in check.check_bundle()))

    def test_missing_expected_output(self) -> None:
        path = self.root / "skills/building-nautilus-actors/evals/evals.json"
        data = json.loads(path.read_text())
        del data["evals"][0]["expected_output"]
        path.write_text(json.dumps(data))
        self.assertTrue(any("Incomplete evaluator case" in error for error in check.check_bundle()))

    def test_sixth_workflow_rejected(self) -> None:
        (self.root / "skills/extra").mkdir()
        self.assertTrue(any("exactly the five" in error for error in check.check_bundle()))

    def test_plugin_version_is_exact_release_identity(self) -> None:
        path = self.root / ".codex-plugin/plugin.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["version"] = "0.64.0"
        path.write_text(json.dumps(data), encoding="utf-8")
        self.assertTrue(any("plugin identity/version" in error for error in check.check_bundle()))

    def test_workflow_icon_cannot_escape_or_use_yaml_indirection(self) -> None:
        path = self.root / "skills/building-nautilus-actors/agents/openai.yaml"
        path.write_text(
            path.read_text(encoding="utf-8").replace("./assets/icon.svg", "../../outside.svg"),
            encoding="utf-8",
        )
        self.assertTrue(any("icon declaration" in error for error in check.check_bundle()))

    def test_duplicate_source_ranges_preserved(self) -> None:
        (self.root / "references/sources.md").write_text(
            "`crates/common/src/actor/data_actor.rs:1-2`\n"
            "`crates/common/src/actor/data_actor.rs:5-6`\n"
        )
        coordinates = check.source_coordinates()
        self.assertEqual(coordinates["crates/common/src/actor/data_actor.rs"], "1-2,5-6")

    def test_cachebuster_does_not_require_checker_changes(self) -> None:
        path = self.root / ".codex-plugin/plugin.json"
        data = json.loads(path.read_text())
        data["version"] = "0.64.0+codex.another-build"
        path.write_text(json.dumps(data))
        self.assertEqual(check.check_bundle(), [])

    def test_independent_source_revision_is_qualified(self) -> None:
        skill = self.root / "skills/building-nautilus-actors"
        path = skill / "references/source-manifest.json"
        data = json.loads(path.read_text())
        data["upstream_revision"] = None
        path.write_text(json.dumps(data))
        self.assertTrue(any("source toolchain or revision" in error for error in check.check_skill(skill)))

    def test_actor_asset_has_no_order_authority(self) -> None:
        source = self.root / "skills/building-nautilus-actors/assets/quickstart/src/main.rs"
        source.write_text(source.read_text() + "\nfn fixture() { submit_order(); }\n")
        self.assertTrue(any("order authority" in error for error in check.check_bundle()))

    def test_actor_nested_test_has_no_order_authority(self) -> None:
        source = self.root / "skills/building-nautilus-actors/assets/quickstart/tests/fixture.rs"
        source.parent.mkdir()
        source.write_text("fn fixture() { add_strategy(); }\n")
        self.assertTrue(any("order authority" in error for error in check.check_bundle()))

    def test_actor_build_output_is_not_authored_code(self) -> None:
        skill = self.root / "skills/building-nautilus-actors"
        source = skill / "assets/quickstart/target/generated.rs"
        source.parent.mkdir()
        source.write_text("fn fixture() { add_strategy(); }\n")
        self.assertEqual(check.check_skill(skill), [])

    def test_connection_recipes_and_evidence_are_local(self) -> None:
        for name, expected in sync_resources.CONNECTIONS.items():
            with self.subTest(skill=name):
                skill = self.root / "skills" / name
                text = (skill / "references/connections.md").read_text()
                self.assertEqual(tuple(re.findall(r"^## (C\d+):", text, re.M)), expected)
                evidence = (skill / "references/sources.md").read_text()
                anchors = set(re.findall(r"^\| ([A-Z]+\d+) \|", evidence, re.M))
                for line in re.findall(r"^Source anchors: ([A-Z0-9, ]+)\.", text, re.M):
                    self.assertTrue(set(line.split(", ")).issubset(anchors), line)

    def test_connection_recipe_cannot_be_omitted(self) -> None:
        source = self.root / "references/connections.md"
        source.write_text(source.read_text().replace("## C5:", "## Missing:"))
        with self.assertRaisesRegex(ValueError, "exactly C1 through C8"):
            sync_resources.generated_files(self.root)

    def test_independent_workflow_rejects_invalid_digest(self) -> None:
        skill = self.root / "skills/building-nautilus-actors"
        path = skill / "references/source-manifest.json"
        data = json.loads(path.read_text())
        data["files"][0]["sha256"] = "unverified"
        path.write_text(json.dumps(data))
        self.assertTrue(any("Invalid workflow digest" in error for error in check.check_skill(skill)))

    def test_independent_workflow_rejects_duplicate_source(self) -> None:
        skill = self.root / "skills/building-nautilus-actors"
        path = skill / "references/source-manifest.json"
        data = json.loads(path.read_text())
        data["files"].append(data["files"][0])
        path.write_text(json.dumps(data))
        self.assertTrue(any("Duplicate workflow source" in error for error in check.check_skill(skill)))


if __name__ == "__main__":
    unittest.main()
