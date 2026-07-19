import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "css-selectors" / "scripts"
SCRIPT = SCRIPTS / "specificity_calculator.py"
sys.path.insert(0, str(SCRIPTS))

from selector_tokens import SelectorSyntaxError, tokenize_selector

CASES = {
    "a::before": [[0, 0, 2]],
    '[href="#x"]': [[0, 1, 0]],
    ":is(:not(#x), .a)": [[1, 0, 0]],
    ":where(:is(:not(#x)))": [[0, 0, 0]],
    ":nth-child(odd of .a, #b)": [[1, 1, 0]],
    ".a, #b": [[0, 1, 0], [1, 0, 0]],
    "svg|a": [[0, 0, 1]],
    "é": [[0, 0, 1]],
}


def run_cli(selector: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, str(SCRIPT), "--format", "json"],
        input=json.dumps({"selector": selector}),
        text=True,
        capture_output=True,
        check=False,
    )


class SpecificityCalculatorTests(unittest.TestCase):
    def test_selectors_level_four_normative_cases(self) -> None:
        for selector, expected in CASES.items():
            with self.subTest(selector=selector):
                result = run_cli(selector)
                self.assertEqual(result.returncode, 0, result.stderr)
                payload = json.loads(result.stdout)
                self.assertEqual(
                    [member["specificity"] for member in payload["selectors"]],
                    expected,
                )

    def test_results_include_half_open_source_spans_and_standards_notes(self) -> None:
        result = run_cli("  .a, #b  ")
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)

        self.assertEqual(payload["standard"], "Selectors Level 4")
        self.assertEqual(payload["inline_style"], "outside-selector-specificity")
        self.assertEqual(
            [member["span"] for member in payload["selectors"]],
            [{"start": 2, "end": 4}, {"start": 6, "end": 8}],
        )
        self.assertTrue(all(member["notes"] for member in payload["selectors"]))

    def test_escaped_identifiers_and_nested_functions_are_parsed(self) -> None:
        result = run_cli(r'.foo\+bar:is([data-value="a,b"], :has(> #x)), \66 oo')
        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            [member["specificity"] for member in payload["selectors"]],
            [[1, 1, 0], [0, 0, 1]],
        )

    def test_malformed_syntax_exits_nonzero(self) -> None:
        malformed = [
            "a,",
            "[href='x'",
            ":is(.a",
            ".",
            ":is (.a)",
            "a/*",
            ":nth-child(foo)",
            ":nth-child(2 n)",
            ":nth-child(３n+1)",
            ":nth-child(2n+١)",
            ":nth-child(2n of)",
        ]
        for selector in malformed:
            with self.subTest(selector=selector):
                result = run_cli(selector)
                self.assertNotEqual(result.returncode, 0, result.stdout)
                self.assertIn("specificity-calculator", result.stderr)

    def test_valid_nth_child_of_clause_preserves_report_schema(self) -> None:
        result = run_cli(":nth-child(2n of .item)")

        self.assertEqual(result.returncode, 0, result.stderr)
        payload = json.loads(result.stdout)
        self.assertEqual(
            set(payload),
            {"inline_style", "selector", "selectors", "standard"},
        )
        self.assertEqual(payload["selectors"][0]["specificity"], [0, 2, 0])

    def test_tokenizer_preserves_balanced_syntax_without_splitting_nested_commas(self) -> None:
        tokens = tokenize_selector(r'a/* note */:is(.x\,y, [data-x="a,b"])')
        # Only the selector-list separator is syntax. The escaped comma in the
        # class name and the comma inside the string stay within their tokens.
        self.assertEqual([token.kind for token in tokens].count("COMMA"), 1)
        self.assertIn("COMMENT", [token.kind for token in tokens])
        self.assertIn("STRING", [token.kind for token in tokens])
        self.assertEqual([token.kind for token in tokens].count("LPAREN"), 1)
        self.assertEqual([token.kind for token in tokens].count("LBRACKET"), 1)

    def test_tokenizer_rejects_unbalanced_or_unterminated_syntax(self) -> None:
        for selector in ["a)", "[a", 'a[title="x]', "a/* x"]:
            with self.subTest(selector=selector):
                with self.assertRaises(SelectorSyntaxError):
                    tokenize_selector(selector)


if __name__ == "__main__":
    unittest.main()
