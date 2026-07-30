import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "skills" / "css-media-queries" / "scripts" / "feature_detection.py"
FIXTURE = ROOT / "tests" / "fixtures" / "feature-detection-runtime.json"


def run_cli(
    payload: object | None = None, *arguments: str
) -> subprocess.CompletedProcess[str]:
    command = [sys.executable, str(SCRIPT), *arguments]
    return subprocess.run(
        command,
        input=None if payload is None else json.dumps(payload),
        text=True,
        capture_output=True,
        check=False,
    )


class FeatureDetectionTests(unittest.TestCase):
    def test_fixture_reports_cross_engine_support_without_user_agent_claims(self) -> None:
        result = run_cli(None, "--input", str(FIXTURE), "--format", "json")

        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["protocol"], "css-tokenography-feature-detection/v1")
        self.assertEqual(report["scope"], "analysis-of-collected-runtime-facts")
        by_feature = {item["feature"]: item for item in report["features"]}
        self.assertEqual(by_feature["subgrid"]["status"], "all")
        self.assertEqual(by_feature["backdrop-filter"]["status"], "partial")
        self.assertEqual(
            by_feature["backdrop-filter"]["unsupported_engines"], ["firefox"]
        )

    def test_stdin_and_human_output_are_supported(self) -> None:
        payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
        result = run_cli(payload, "--format", "human")

        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("engines=chromium,firefox,webkit", result.stdout)
        self.assertIn("backdrop-filter: partial", result.stdout)

    def test_invalid_shapes_and_non_boolean_support_fail_actionably(self) -> None:
        cases = [
            {},
            {"features": ["subgrid"], "engines": []},
            {
                "features": ["subgrid"],
                "engines": [
                    {"name": "chromium", "support": {"subgrid": "yes"}}
                ],
            },
            {
                "features": ["subgrid", "subgrid"],
                "engines": [
                    {"name": "chromium", "support": {"subgrid": True}}
                ],
            },
        ]
        for payload in cases:
            with self.subTest(payload=payload):
                result = run_cli(payload)
                self.assertNotEqual(result.returncode, 0)
                self.assertTrue(result.stderr.startswith("feature-detection: "))
                self.assertNotIn("Traceback", result.stderr)

    def test_help_is_available_without_browser_dependencies(self) -> None:
        result = run_cli(None, "--help")

        self.assertEqual(result.returncode, 0)
        self.assertIn("Analyze feature support", result.stdout)


if __name__ == "__main__":
    unittest.main()
