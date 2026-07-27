import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
CLAMP = ROOT / "skills" / "css-functions" / "scripts" / "clamp_generator.py"
RATIO = ROOT / "skills" / "css-functions" / "scripts" / "aspect_ratio_calculator.py"
PX_REM = ROOT / "skills" / "web-typography" / "scripts" / "px_to_rem_converter.py"


def run_raw(
    script: Path,
    data: dict[str, object] | None = None,
    *args: str,
) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(script), *args],
        input=None if data is None else json.dumps(data),
        text=True,
        capture_output=True,
        check=False,
    )


def run_json(script: Path, data: dict[str, object], *args: str) -> dict[str, object]:
    result = run_raw(script, data, "--format", "json", *args)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


class ClampGeneratorTests(unittest.TestCase):
    def test_clamp_preserves_endpoints(self) -> None:
        report = run_json(
            CLAMP,
            {
                "min_px": 16,
                "max_px": 24,
                "min_viewport_px": 320,
                "max_viewport_px": 1280,
                "root_px": 16,
            },
        )

        self.assertEqual(
            report["css"],
            "clamp(1rem, 0.8333333333333334rem + 0.8333333333333334vw, 1.5rem)",
        )
        self.assertAlmostEqual(report["slope_vw"], 0.8333333333333334)
        self.assertAlmostEqual(report["intercept_rem"], 0.8333333333333334)

    def test_clamp_rejects_invalid_order_and_non_finite_values(self) -> None:
        invalid_cases = (
            ({"min_px": 24, "max_px": 16, "min_viewport_px": 320, "max_viewport_px": 1280, "root_px": 16}, "min_px < max_px"),
            ({"min_px": 16, "max_px": 24, "min_viewport_px": 1280, "max_viewport_px": 320, "root_px": 16}, "min_viewport_px < max_viewport_px"),
            ({"min_px": 16, "max_px": 24, "min_viewport_px": 320, "max_viewport_px": 1280, "root_px": float("inf")}, "root_px must be a finite number"),
        )

        for data, message in invalid_cases:
            with self.subTest(message=message):
                result = run_raw(CLAMP, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_clamp_rejects_finite_inputs_that_overflow_the_model(self) -> None:
        result = run_raw(
            CLAMP,
            {
                "min_px": -1e308,
                "max_px": 1e308,
                "min_viewport_px": 320,
                "max_viewport_px": 1280,
                "root_px": 16,
            },
            "--format",
            "json",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("calculation must produce finite values", result.stderr)

    def test_clamp_preserves_small_nonzero_values_in_css(self) -> None:
        report = run_json(
            CLAMP,
            {
                "min_px": 1e-8,
                "max_px": 2e-8,
                "min_viewport_px": 320,
                "max_viewport_px": 1280,
                "root_px": 16,
            },
        )

        self.assertEqual(
            report["css"],
            "clamp(6.25e-10rem, 4.166666666666667e-10rem + "
            "1.0416666666666667e-09vw, 1.25e-09rem)",
        )
        self.assertNotEqual(report["intercept_rem"], 0)
        self.assertNotEqual(report["slope_vw"], 0)

    def test_css_and_human_formats_are_useful(self) -> None:
        data = {"min_px": 16, "max_px": 24, "min_viewport_px": 320, "max_viewport_px": 1280, "root_px": 16}

        css = run_raw(CLAMP, data, "--format", "css")
        human = run_raw(CLAMP, data)

        self.assertEqual(
            css.stdout.strip(),
            "clamp(1rem, 0.8333333333333334rem + 0.8333333333333334vw, 1.5rem)",
        )
        self.assertIn("320px", human.stdout)
        self.assertIn("1280px", human.stdout)
        self.assertIn("clamp(1rem", human.stdout)


class AspectRatioCalculatorTests(unittest.TestCase):
    def test_ratio_reduces_integers(self) -> None:
        report = run_json(RATIO, {"width": 1920, "height": 1080})

        self.assertEqual(report["pair"], [16, 9])
        self.assertEqual(report["css"], "aspect-ratio: 16 / 9;")
        self.assertAlmostEqual(report["ratio"], 16 / 9)

    def test_decimal_dimensions_are_normalized(self) -> None:
        report = run_json(RATIO, {"width": 10.5, "height": 6.25})

        self.assertEqual(report["pair"], [1.68, 1])
        self.assertIsInstance(report["ratio"], float)
        self.assertEqual(report["css"], "aspect-ratio: 1.68 / 1;")

    def test_small_decimal_ratio_remains_nonzero_in_json_and_css(self) -> None:
        report = run_json(RATIO, {"width": 1e-8, "height": 1})

        self.assertEqual(report["pair"], [1e-8, 1])
        self.assertEqual(report["css"], "aspect-ratio: 1e-08 / 1;")
        self.assertEqual(report["ratio"], report["pair"][0])

    def test_large_integer_dimensions_reduce_exactly(self) -> None:
        cases = (
            (9007199254740993, 3, [3002399751580331, 1]),
            (18014398509481986, 6, [3002399751580331, 1]),
            (9007199254740995, 5, [1801439850948199, 1]),
        )

        for width, height, expected_pair in cases:
            with self.subTest(width=width, height=height):
                report = run_json(RATIO, {"width": width, "height": height})
                self.assertEqual(report["pair"], expected_pair)
                self.assertEqual(
                    report["css"],
                    f"aspect-ratio: {expected_pair[0]} / {expected_pair[1]};",
                )

    def test_large_integral_ratio_stays_exact_in_json_css_and_human_output(self) -> None:
        data = {"width": 9007199254740993, "height": 1}

        report = run_json(RATIO, data)
        human = run_raw(RATIO, data)

        self.assertEqual(report["pair"], [9007199254740993, 1])
        self.assertEqual(report["ratio"], 9007199254740993)
        self.assertIsInstance(report["ratio"], int)
        self.assertEqual(
            report["css"],
            "aspect-ratio: 9007199254740993 / 1;",
        )
        self.assertIn("reduces to 9007199254740993:1", human.stdout)
        self.assertIn("aspect-ratio: 9007199254740993 / 1;", human.stdout)

    def test_ratio_rejects_invalid_dimensions(self) -> None:
        for data, message in (
            ({"width": 0, "height": 9}, "width and height must be greater than zero"),
            ({"width": True, "height": 9}, "width must be a finite number"),
            ({"width": 16, "height": float("nan")}, "height must be a finite number"),
        ):
            with self.subTest(message=message):
                result = run_raw(RATIO, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_ratio_rejects_finite_inputs_that_overflow_the_model(self) -> None:
        result = run_raw(
            RATIO,
            {"width": 1e308, "height": 5e-324},
            "--format",
            "json",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("calculation must produce finite values", result.stderr)

    def test_human_format_names_the_reduction(self) -> None:
        result = run_raw(RATIO, {"width": 1920, "height": 1080})

        self.assertIn("1920", result.stdout)
        self.assertIn("16:9", result.stdout)


class PxToRemConverterTests(unittest.TestCase):
    def test_px_rem_uses_supplied_root(self) -> None:
        report = run_json(PX_REM, {"px": 20, "root_px": 16})

        self.assertEqual(report, {"px": 20.0, "root_px": 16.0, "rem": 1.25, "css": "1.25rem"})

    def test_px_rem_allows_negative_offsets(self) -> None:
        report = run_json(PX_REM, {"px": -8, "root_px": 16})

        self.assertEqual(report["rem"], -0.5)
        self.assertEqual(report["css"], "-0.5rem")

    def test_px_rem_preserves_small_nonzero_values_in_css(self) -> None:
        report = run_json(PX_REM, {"px": 1e-7, "root_px": 16})

        self.assertEqual(report["rem"], 6.25e-9)
        self.assertEqual(report["css"], "6.25e-09rem")
        self.assertEqual(float(str(report["css"]).removesuffix("rem")), report["rem"])

    def test_px_rem_normalizes_negative_zero_in_css(self) -> None:
        report = run_json(PX_REM, {"px": -0.0, "root_px": 16})

        self.assertEqual(report["rem"], -0.0)
        self.assertEqual(report["css"], "0rem")

    def test_px_rem_rejects_zero_root(self) -> None:
        result = run_raw(PX_REM, {"px": 16, "root_px": 0}, "--format", "json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("root_px must be greater than zero", result.stderr)

    def test_px_rem_rejects_non_finite_numbers(self) -> None:
        result = run_raw(PX_REM, {"px": float("inf"), "root_px": 16}, "--format", "json")

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("px must be a finite number", result.stderr)

    def test_px_rem_rejects_finite_inputs_that_overflow_the_conversion(self) -> None:
        result = run_raw(
            PX_REM,
            {"px": 1e308, "root_px": 5e-324},
            "--format",
            "json",
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("conversion must produce a finite value", result.stderr)

    def test_human_format_explains_the_conversion(self) -> None:
        result = run_raw(PX_REM, {"px": 20, "root_px": 16})

        self.assertEqual(result.stdout.strip(), "20px at a 16px root = 1.25rem")


class NumericCliContractTests(unittest.TestCase):
    def test_help_is_available_for_every_tool(self) -> None:
        for script in (CLAMP, RATIO, PX_REM):
            with self.subTest(script=script.name):
                result = run_raw(script, None, "--help")
                self.assertEqual(result.returncode, 0, result.stderr)
                self.assertIn("--input", result.stdout)
                self.assertIn("--format", result.stdout)
                self.assertIn("--evidence", result.stdout)

    def test_fixture_output_is_stable(self) -> None:
        cases = (
            (CLAMP, FIXTURES / "clamp-valid.json"),
            (RATIO, FIXTURES / "aspect-ratio-valid.json"),
            (PX_REM, FIXTURES / "px-rem-valid.json"),
        )

        for script, fixture in cases:
            with self.subTest(script=script.name):
                first = run_raw(script, None, "--input", str(fixture), "--format", "json")
                second = run_raw(script, None, "--input", str(fixture), "--format", "json")
                self.assertEqual(first.returncode, 0, first.stderr)
                self.assertEqual(first.stdout, second.stdout)
                self.assertIsInstance(json.loads(first.stdout), dict)

    def test_evidence_wraps_the_unmodified_report(self) -> None:
        cases = (
            (CLAMP, {"min_px": 16, "max_px": 24, "min_viewport_px": 320, "max_viewport_px": 1280, "root_px": 16}),
            (RATIO, {"width": 1920, "height": 1080}),
            (PX_REM, {"px": 20, "root_px": 16}),
        )

        for script, data in cases:
            with self.subTest(script=script.name):
                report = run_json(script, data)
                envelope = run_json(script, data, "--evidence")
                self.assertEqual(envelope["core"], report)
                self.assertEqual(envelope["classification"], "unavailable")
                self.assertEqual(envelope["observations"], [])

    def test_malformed_input_is_actionable(self) -> None:
        result = subprocess.run(
            [sys.executable, str(CLAMP), "--format", "json"],
            input="not-json",
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("Unable to read JSON input", result.stderr)


if __name__ == "__main__":
    unittest.main()
