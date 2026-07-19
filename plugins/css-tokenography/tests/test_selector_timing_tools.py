import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
SELECTOR_SCRIPTS = ROOT / "skills" / "css-selectors" / "scripts"
TRANSITION_SCRIPTS = ROOT / "skills" / "css-transitions" / "scripts"
NTH = SELECTOR_SCRIPTS / "nth_child_selector.py"
BEZIER = TRANSITION_SCRIPTS / "cubic_bezier_studio.py"


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


class NthChildSelectorTests(unittest.TestCase):
    def test_nth_child_normalizes_an_plus_b(self) -> None:
        report = run_json(NTH, {"expression": "2n + 1", "element": "li"})

        self.assertEqual(report["coefficients"], {"a": 2, "b": 1})
        self.assertEqual(report["expression"], "2n+1")
        self.assertEqual(report["selector"], "li:nth-child(2n+1)")
        self.assertEqual(
            report["css"],
            "li:nth-child(2n+1) {\n  /* styles */\n}",
        )

    def test_parser_returns_normalized_coefficients_for_all_branches(self) -> None:
        sys.path.insert(0, str(SELECTOR_SCRIPTS))
        try:
            from nth_child_selector import parse_an_plus_b

            cases = {
                "ODD": {"a": 2, "b": 1, "expression": "2n+1"},
                "even": {"a": 2, "b": 0, "expression": "2n"},
                "+6": {"a": 0, "b": 6, "expression": "6"},
                "-3": {"a": 0, "b": -3, "expression": "-3"},
                "n": {"a": 1, "b": 0, "expression": "n"},
                "+n": {"a": 1, "b": 0, "expression": "n"},
                "-n+ 6": {"a": -1, "b": 6, "expression": "-n+6"},
                "+3n - 2": {"a": 3, "b": -2, "expression": "3n-2"},
                "0n+5": {"a": 0, "b": 5, "expression": "5"},
            }
            for source, expected in cases.items():
                with self.subTest(source=source):
                    self.assertEqual(parse_an_plus_b(source), expected)
        finally:
            sys.path.remove(str(SELECTOR_SCRIPTS))

    def test_nth_child_preserves_css_token_whitespace_boundaries(self) -> None:
        valid = {
            "3n + 1": {"a": 3, "b": 1},
            "+3n - 2": {"a": 3, "b": -2},
            "-n+ 6": {"a": -1, "b": 6},
            "n +1": {"a": 1, "b": 1},
            "n- 1": {"a": 1, "b": -1},
        }
        invalid = (
            "3 n",
            "+ 2n",
            "+ 2",
            "n 1",
            "3n + -6",
            "2 n + 1",
            "n/**/+1",
            "３n+1",
            "2n+١",
            "2n+\v1",
        )

        for expression, expected in valid.items():
            with self.subTest(expression=expression, status="valid"):
                self.assertEqual(
                    run_json(NTH, {"expression": expression})["coefficients"],
                    expected,
                )
        for expression in invalid:
            with self.subTest(expression=expression, status="invalid"):
                result = run_raw(NTH, {"expression": expression}, "--format", "json")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("nth-child-selector", result.stderr)

    def test_nth_child_rejects_selector_injection_and_malformed_element_tokens(self) -> None:
        invalid_elements = (
            "",
            "li, body",
            "li .item",
            "li:hover",
            "li/*comment*/",
            "li) { color: red; }",
            ".item",
        )

        for element in invalid_elements:
            with self.subTest(element=element):
                result = run_raw(
                    NTH,
                    {"expression": "odd", "element": element},
                    "--format",
                    "json",
                )
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("element", result.stderr)

    def test_nth_child_defaults_to_li_and_rejects_non_string_expression(self) -> None:
        self.assertEqual(
            run_json(NTH, {"expression": "even"})["selector"],
            "li:nth-child(2n)",
        )
        result = run_raw(NTH, {"expression": 2}, "--format", "json")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("expression", result.stderr)

    def test_nth_child_cli_supports_fixture_css_human_help_and_evidence(self) -> None:
        fixture = FIXTURES / "nth-child-valid.json"
        css = run_raw(NTH, None, "--input", str(fixture), "--format", "css")
        human = run_raw(NTH, None, "--input", str(fixture))
        help_result = run_raw(NTH, None, "--help")
        evidence = run_raw(
            NTH,
            None,
            "--input",
            str(fixture),
            "--format",
            "json",
            "--evidence",
        )

        self.assertEqual(css.returncode, 0, css.stderr)
        self.assertEqual(css.stdout.strip(), "li:nth-child(2n+1) {\n  /* styles */\n}")
        self.assertEqual(human.returncode, 0, human.stderr)
        self.assertIn("a=2", human.stdout)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--evidence", help_result.stdout)
        self.assertEqual(evidence.returncode, 0, evidence.stderr)
        self.assertEqual(json.loads(evidence.stdout)["core"]["selector"], "li:nth-child(2n+1)")


class CubicBezierStudioTests(unittest.TestCase):
    def test_bezier_allows_overshooting_y_but_not_x(self) -> None:
        report = run_json(
            BEZIER,
            {"x1": 0.2, "y1": 1.4, "x2": 0.8, "y2": -0.2},
        )

        self.assertEqual(report["status"], "valid")
        self.assertEqual(report["css"], "cubic-bezier(0.2, 1.4, 0.8, -0.2)")
        self.assertEqual(report["control_points"], [0.2, 1.4, 0.8, -0.2])
        result = run_raw(
            BEZIER,
            {"x1": 1.2, "y1": 0, "x2": 0.8, "y2": 1},
            "--format",
            "json",
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("x1", result.stderr)

    def test_build_bezier_accepts_closed_x_boundaries(self) -> None:
        sys.path.insert(0, str(TRANSITION_SCRIPTS))
        try:
            from cubic_bezier_studio import build_bezier

            self.assertEqual(
                build_bezier(0, -2, 1, 3)["css"],
                "cubic-bezier(0, -2, 1, 3)",
            )
        finally:
            sys.path.remove(str(TRANSITION_SCRIPTS))

    def test_bezier_rejects_out_of_range_x_non_finite_and_non_numeric_values(self) -> None:
        invalid = (
            ({"x1": -0.01, "y1": 0, "x2": 0.8, "y2": 1}, "x1"),
            ({"x1": 0.2, "y1": 0, "x2": 1.01, "y2": 1}, "x2"),
            ({"x1": 0.2, "y1": float("inf"), "x2": 0.8, "y2": 1}, "y1"),
            ({"x1": 0.2, "y1": 0, "x2": 0.8, "y2": float("nan")}, "y2"),
            ({"x1": True, "y1": 0, "x2": 0.8, "y2": 1}, "x1"),
            ({"x1": "0.2", "y1": 0, "x2": 0.8, "y2": 1}, "x1"),
        )

        for data, field in invalid:
            with self.subTest(field=field, data=data):
                result = run_raw(BEZIER, data, "--format", "json")
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn(field, result.stderr)

    def test_bezier_cli_supports_fixture_css_human_help_and_evidence(self) -> None:
        fixture = FIXTURES / "cubic-bezier-valid.json"
        css = run_raw(BEZIER, None, "--input", str(fixture), "--format", "css")
        human = run_raw(BEZIER, None, "--input", str(fixture))
        help_result = run_raw(BEZIER, None, "--help")
        evidence = run_raw(
            BEZIER,
            None,
            "--input",
            str(fixture),
            "--format",
            "json",
            "--evidence",
        )

        self.assertEqual(css.returncode, 0, css.stderr)
        self.assertEqual(css.stdout.strip(), "cubic-bezier(0.2, 1.4, 0.8, -0.2)")
        self.assertEqual(human.returncode, 0, human.stderr)
        self.assertIn("P1=(0.2, 1.4)", human.stdout)
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("--evidence", help_result.stdout)
        self.assertEqual(evidence.returncode, 0, evidence.stderr)
        self.assertEqual(json.loads(evidence.stdout)["core"]["status"], "valid")

    def test_bezier_fixture_output_is_deterministic(self) -> None:
        fixture = FIXTURES / "cubic-bezier-valid.json"
        command = ("--input", str(fixture), "--format", "json")

        first = run_raw(BEZIER, None, *command)
        second = run_raw(BEZIER, None, *command)

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)


if __name__ == "__main__":
    unittest.main()
