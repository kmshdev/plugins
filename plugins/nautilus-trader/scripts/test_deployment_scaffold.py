from __future__ import annotations

import importlib.util
from pathlib import Path
import tempfile
import unittest
from uuid import UUID

SCRIPT = Path(__file__).resolve().parent.parent / "skills/deploying-nautilus-runs/scripts/scaffold.py"
SPEC = importlib.util.spec_from_file_location("deployment_scaffold", SCRIPT)
scaffold = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(scaffold)
IMAGE = "registry.example/runner@sha256:" + "a" * 64


class DeploymentScaffoldTests(unittest.TestCase):
    def test_independent_run_plans_are_isolated_without_execution(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            first = scaffold.plan(root / "first.json", IMAGE, "backtest", "s3://input/catalog", "s3://output/artifacts")
            second = scaffold.plan(root / "second.json", IMAGE, "backtest", "s3://input/catalog", "s3://output/artifacts")
            self.assertNotEqual(first["run_id"], second["run_id"])
            self.assertNotEqual(first["artifact_prefix"], second["artifact_prefix"])
            self.assertEqual(str(UUID(first["instance_id"])), first["run_id"])
            self.assertEqual(first["node_processes"], 1)
            self.assertEqual(first["automatic_retries"], 0)
            self.assertFalse(first["cache"]["flush_on_start"])
            self.assertFalse(first["streaming"]["replace_existing"])
            self.assertEqual({item.name for item in root.iterdir()}, {"first.json", "second.json"})

    def test_existing_plan_and_overlay_are_not_overwritten(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            destination = root / "plan.json"
            destination.write_text("preserve")
            with self.assertRaises(FileExistsError):
                scaffold.plan(destination, IMAGE, "live", "file:///input", "file:///output")
            self.assertEqual(destination.read_text(), "preserve")
            with self.assertRaises(FileExistsError):
                scaffold.initialize(root, "strategy", "runner")
            self.assertEqual(list(root.iterdir()), [destination])

    def test_secret_uris_and_unqualified_output_are_rejected(self) -> None:
        for uri in ("s3://user:secret@bucket/path", "az://container/data?sig=secret", "https://host/path"):
            with self.subTest(uri=uri), self.assertRaises(ValueError):
                scaffold.storage_uri(uri, writable=True)
        self.assertEqual(scaffold.storage_uri("https://host/input", writable=False), "https://host/input")
        self.assertEqual(scaffold.storage_uri("abfs://container@account.dfs.core.windows.net/data", writable=True), "abfs://container@account.dfs.core.windows.net/data")

    def test_scaffold_identifiers_cannot_inject_build_commands(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "overlay"
            with self.assertRaises(ValueError):
                scaffold.initialize(destination, "strategy; touch outside", "runner")
            self.assertFalse(destination.exists())
            scaffold.initialize(destination, "my-strategy", "my-runner")
            self.assertIn("--package my-strategy --bin my-runner", (destination / "Dockerfile").read_text())
            self.assertFalse(any("@@" in item.read_text() for item in destination.rglob("*") if item.is_file()))

    def test_local_root_and_mode_specific_capture(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for mode in ("backtest", "sandbox", "live"):
                with self.subTest(mode=mode):
                    record = scaffold.plan(root / f"{mode}.json", IMAGE, mode, "file:///", "file:///")
                    self.assertEqual(record["input_catalog_uri"], "/")
                    self.assertEqual(record["artifact_prefix"], f"/runs/{record['run_id']}")
                    self.assertEqual(record["streaming"]["fs_protocol"], "file")
                    expected = "kernel-streaming-config" if mode == "backtest" else "explicit-native-writer"
                    self.assertEqual(record["capture_integration"], expected)
            with self.assertRaises(ValueError):
                scaffold.plan(root / "mutable.json", "runner:latest", "backtest", "/input", "/output")
            self.assertFalse((root / "mutable.json").exists())

    def test_native_local_paths_preserve_special_characters(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            location = Path(directory).resolve() / "my catalog 100% café"
            self.assertEqual(scaffold.storage_uri(str(location), writable=True), str(location))
            self.assertEqual(scaffold.storage_uri(location.as_uri(), writable=False), str(location))
            self.assertEqual(scaffold.storage_uri("file://localhost/data/catalog", writable=False), "/data/catalog")

    def test_azure_kernel_streaming_requires_account_addressing(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "plan.json"
            with self.assertRaisesRegex(ValueError, "account_name"):
                scaffold.plan(destination, IMAGE, "backtest", "https://host/input", "az://container/output")
            self.assertFalse(destination.exists())
            record = scaffold.plan(destination, IMAGE, "backtest", "https://host/input", "abfs://container@account.dfs.core.windows.net/output")
            self.assertEqual(record["streaming"]["fs_protocol"], "abfs")
            with self.assertRaises(ValueError):
                scaffold.storage_uri("abfs://container@/output", writable=True)


if __name__ == "__main__":
    unittest.main()
