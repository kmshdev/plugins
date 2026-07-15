import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


def run_cli(relative_path: str, *args: str, stdin: str | None = None) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(ROOT / relative_path), *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


class GridAreaMapperTests(unittest.TestCase):
    script = "skills/css-grid/scripts/grid_area_mapper.py"

    def test_valid_matrix_emits_css_and_json(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "grid-valid.json"), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["areas"], ["header", "nav", "main", "footer"])
        self.assertIn('"nav main main"', payload["css"])
        self.assertIn(".header {\n  grid-area: header;\n}", payload["css"])

    def test_disconnected_area_is_rejected(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "grid-disconnected.json"), "--format", "json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("rectangular", result.stderr.lower())

    def test_help_is_available(self) -> None:
        result = run_cli(self.script, "--help")
        self.assertEqual(result.returncode, 0)
        self.assertIn("grid-template-areas", result.stdout)


class SubgridVisualizerTests(unittest.TestCase):
    script = "skills/css-grid/scripts/subgrid_visualizer.py"

    def test_valid_subgrid_exposes_inherited_tracks(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "subgrid-valid.json"), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["items"][0]["inherited_columns"], 3)
        self.assertEqual(payload["items"][0]["gap"], "16px")
        self.assertIn("grid-template-columns: subgrid", payload["css"])

    def test_out_of_bounds_span_is_rejected(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "subgrid-invalid.json"), "--format", "json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("boundary", result.stderr.lower())

    def test_custom_parent_tracks_are_preserved(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "subgrid-tracks.json"), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["parent"]["column_tracks"], ["1fr", "2fr", "1fr"])
        self.assertIn("grid-template-columns: 1fr 2fr 1fr;", payload["css"])


class PerformanceBudgetTests(unittest.TestCase):
    script = "skills/web-performance-optimization/scripts/performance_budget.py"

    def test_passing_fixture_exits_zero(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "performance-pass.json"), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "pass")
        self.assertEqual(payload["missing"], [])

    def test_failing_fixture_exits_nonzero(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "performance-fail.json"), "--format", "json")
        self.assertEqual(result.returncode, 2)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "fail")
        self.assertIn("lcp_ms", [failure["metric"] for failure in payload["failures"]])

    def test_partial_fixture_distinguishes_missing_data(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "performance-partial.json"), "--format", "json")
        self.assertEqual(result.returncode, 3)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["status"], "incomplete")
        self.assertIn("inp_ms", payload["missing"])

    def test_malformed_fixture_is_actionable(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "performance-malformed.json"), "--format", "json")
        self.assertEqual(result.returncode, 1)
        self.assertIn("numeric", result.stderr.lower())


class CoverageValidationTests(unittest.TestCase):
    script = "scripts/validate_coverage.py"

    def test_current_inventory_is_complete(self) -> None:
        result = run_cli(self.script, "--plugin", str(ROOT), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["guides"], 18)
        self.assertEqual(payload["tools"], 33)
        self.assertEqual(payload["errors"], [])


class ToolModelTests(unittest.TestCase):
    def test_clamp_generator_computes_fluid_expression(self) -> None:
        payload = json.dumps({"min_px": 16, "max_px": 32, "min_viewport_px": 320, "max_viewport_px": 1280})
        result = run_cli("skills/css-functions/scripts/design_tool.py", "--tool", "clamp-generator", "--format", "json", stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["css"], "clamp(1rem, 0.666667rem + 1.666667vw, 2rem)")

    def test_transform_model_preserves_declared_order(self) -> None:
        payload = json.dumps({"translate_x": "10px", "rotate": "20deg", "scale": 1.2})
        result = run_cli("skills/css-transforms/scripts/design_tool.py", "--tool", "css-transform-playground", "--format", "json", stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["css"], "transform: translateX(10px) rotate(20deg) scale(1.2);")

    def test_specificity_calculator_handles_where_and_is(self) -> None:
        payload = json.dumps({"selector": "article:where(.card) #hero:is(.featured, div)"})
        result = run_cli("skills/css-selectors/scripts/design_tool.py", "--tool", "specificity-calculator", "--format", "json", stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(json.loads(result.stdout)["specificity"], [1, 1, 1])

    def test_contrast_checker_reports_wcag_thresholds(self) -> None:
        payload = json.dumps({"foreground": "#000000", "background": "#ffffff"})
        result = run_cli("skills/css-variables/scripts/design_tool.py", "--tool", "color-contrast-checker", "--format", "json", stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertEqual(report["ratio"], 21.0)
        self.assertTrue(report["wcag_aa_normal"])

    def test_oklch_converter_computes_from_srgb_hex(self) -> None:
        payload = json.dumps({"hex": "#ff0000"})
        result = run_cli("skills/css-variables/scripts/design_tool.py", "--tool", "oklch-color-converter", "--format", "json", stdin=payload)
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertAlmostEqual(report["oklch"]["l"], 0.627955, places=5)
        self.assertAlmostEqual(report["oklch"]["c"], 0.257683, places=5)
        self.assertAlmostEqual(report["oklch"]["h"], 29.234, places=3)

    def test_invalid_bezier_control_point_is_rejected(self) -> None:
        payload = json.dumps({"x1": -0.2, "y1": 0, "x2": 0.8, "y2": 1})
        result = run_cli("skills/css-transitions/scripts/design_tool.py", "--tool", "cubic-bezier-studio", "--format", "json", stdin=payload)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("x1", result.stderr)


class WindsurfRuleTests(unittest.TestCase):
    script = "skills/windsurf-rules/scripts/validate_rule.py"

    def test_valid_glob_rule_reports_scope_and_trigger(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "windsurf-glob.md"), "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(payload["trigger"], "glob")
        self.assertEqual(payload["globs"], "**/*.test.ts")

    def test_glob_rule_requires_globs(self) -> None:
        result = run_cli(self.script, "--input", str(FIXTURES / "windsurf-invalid.md"), "--format", "json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("globs", result.stderr)


if __name__ == "__main__":
    unittest.main()
