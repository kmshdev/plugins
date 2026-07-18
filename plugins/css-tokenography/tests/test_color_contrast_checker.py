import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "tests" / "fixtures" / "contrast-threshold-fail.json"
SHARED_SCRIPT = ROOT / "skills" / "css-variables" / "scripts" / "design_tool.py"
CANONICAL_SCRIPT = (
    ROOT / "skills" / "css-variables" / "scripts" / "color_contrast_checker.py"
)


def run_shared_contrast() -> dict[str, object]:
    result = subprocess.run(
        [
            sys.executable,
            str(SHARED_SCRIPT),
            "--tool",
            "color-contrast-checker",
            "--input",
            str(FIXTURE),
            "--format",
            "json",
        ],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def invoke_contrast(foreground: str, background: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(CANONICAL_SCRIPT), "--format", "json"],
        input=json.dumps({"foreground": foreground, "background": background}),
        text=True,
        capture_output=True,
        check=False,
    )


def run_contrast(foreground: str, background: str) -> dict[str, object]:
    result = invoke_contrast(foreground, background)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class SharedContrastRegressionTests(unittest.TestCase):
    def test_unrounded_ratio_controls_threshold(self) -> None:
        report = run_shared_contrast()

        self.assertAlmostEqual(report["ratio"], 4.4975956604, places=9)
        self.assertEqual(report["display_ratio"], 4.50)
        self.assertFalse(report["thresholds"]["aa_normal_text"])


class ColorContrastCheckerTests(unittest.TestCase):
    def test_unrounded_ratio_controls_threshold(self) -> None:
        report = run_contrast("#6e7978", "#ffffff")

        self.assertAlmostEqual(report["ratio"], 4.4975956604, places=9)
        self.assertEqual(report["display_ratio"], 4.50)
        self.assertFalse(report["thresholds"]["aa_normal_text"])

    def test_result_is_not_a_conformance_claim(self) -> None:
        report = run_contrast("#000000", "#ffffff")

        self.assertEqual(report["method"], "wcag2-relative-luminance")
        self.assertEqual(report["standard"], "WCAG 2.2")
        self.assertEqual(report["scope"], "color-pair-thresholds-only")
        self.assertEqual(report["apca"]["status"], "not-implemented")
        self.assertIn("not a WCAG 3 conformance method", report["apca"]["reason"])

    def test_black_and_white_have_maximum_contrast(self) -> None:
        report = run_contrast("#000000", "#ffffff")

        self.assertEqual(report["ratio"], 21.0)
        self.assertEqual(report["display_ratio"], 21.0)
        self.assertTrue(all(report["thresholds"].values()))

    def test_contrast_ratio_is_symmetric(self) -> None:
        forward = run_contrast("#234567", "#fefefe")
        reverse = run_contrast("#fefefe", "#234567")

        self.assertEqual(forward["ratio"], reverse["ratio"])
        self.assertEqual(forward["thresholds"], reverse["thresholds"])

    def test_invalid_hex_is_rejected(self) -> None:
        result = invoke_contrast("#fff", "#ffffff")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("foreground must be a six-digit hex color", result.stderr)

    def test_non_text_uses_full_precision_three_to_one_threshold(self) -> None:
        passing = run_contrast("#949494", "#ffffff")
        failing = run_contrast("#959595", "#ffffff")

        self.assertGreater(passing["ratio"], 3.0)
        self.assertTrue(passing["thresholds"]["non_text"])
        self.assertEqual(failing["display_ratio"], 3.0)
        self.assertLess(failing["ratio"], 3.0)
        self.assertFalse(failing["thresholds"]["non_text"])


if __name__ == "__main__":
    unittest.main()
