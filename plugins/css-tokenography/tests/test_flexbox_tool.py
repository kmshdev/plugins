import importlib.util
import io
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"
FLEX = ROOT / "skills" / "css-flexbox" / "scripts" / "flexbox_playground.py"
FLEX_MODEL = ROOT / "skills" / "css-flexbox" / "scripts" / "flexbox_model.py"


def invoke(
    data: object | None = None,
    *args: str,
    raw_stdin: str | None = None,
) -> subprocess.CompletedProcess[str]:
    stdin = raw_stdin if raw_stdin is not None else None if data is None else json.dumps(data)
    return subprocess.run(
        [sys.executable, str(FLEX), *args],
        input=stdin,
        text=True,
        capture_output=True,
        check=False,
    )


def run_json_raw(data: object) -> subprocess.CompletedProcess[str]:
    return invoke(data, "--format", "json")


def run_json(data: object) -> dict[str, object]:
    result = run_json_raw(data)
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def run_fixture(script: Path, fixture: str) -> dict[str, object]:
    result = subprocess.run(
        [sys.executable, str(script), "--input", str(FIXTURES / fixture), "--format", "json"],
        text=True,
        capture_output=True,
        check=False,
    )
    if result.returncode != 0:
        raise AssertionError(result.stderr)
    return json.loads(result.stdout)


def load_flexbox_cli():
    sys.path.insert(0, str(FLEX.parent))
    spec = importlib.util.spec_from_file_location("flexbox_playground", FLEX)
    if spec is None or spec.loader is None:
        raise AssertionError("unable to load flexbox CLI")
    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


class FlexboxPlaygroundTests(unittest.TestCase):
    def test_row_reverse_changes_main_axis_without_reordering_source(self) -> None:
        report = run_fixture(FLEX, "flexbox-wrapped.json")

        self.assertEqual(report["source_order"], ["a", "b", "c"])
        self.assertEqual(report["main_axis"], "inline-end-to-inline-start")
        self.assertEqual(report["cross_axis"], "block-start-to-block-end")

    def test_container_controls_emit_canonical_declarations(self) -> None:
        report = run_fixture(FLEX, "flexbox-wrapped.json")

        self.assertEqual(
            report["declarations"],
            {
                "display": "flex",
                "flex-direction": "row-reverse",
                "flex-wrap": "wrap",
                "justify-content": "space-between",
                "align-items": "center",
                "gap": "1rem",
            },
        )
        self.assertEqual(
            report["css"],
            "display: flex;\n"
            "flex-direction: row-reverse;\n"
            "flex-wrap: wrap;\n"
            "justify-content: space-between;\n"
            "align-items: center;\n"
            "gap: 1rem;",
        )

    def test_column_wrap_reverse_normalizes_both_logical_axes(self) -> None:
        report = run_json({"direction": "column", "wrap": "wrap-reverse"})

        self.assertEqual(report["main_axis"], "block-start-to-block-end")
        self.assertEqual(report["cross_axis"], "inline-end-to-inline-start")

    def test_unknown_alignment_and_enum_controls_are_rejected(self) -> None:
        cases = (
            ({"align_items": "middle"}, "align_items must be one of"),
            ({"justify_content": "left"}, "justify_content must be one of"),
            ({"direction": "horizontal"}, "direction must be one of"),
            ({"wrap": "reverse"}, "wrap must be one of"),
        )

        for data, message in cases:
            with self.subTest(data=data):
                result = run_json_raw(data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_defaults_apply_only_when_controls_are_absent(self) -> None:
        defaults = run_json({})["declarations"]
        self.assertEqual(defaults["flex-direction"], "row")
        self.assertEqual(defaults["flex-wrap"], "nowrap")
        self.assertEqual(defaults["justify-content"], "normal")
        self.assertEqual(defaults["align-items"], "normal")
        self.assertEqual(defaults["gap"], "normal")

        cases = (
            ("direction", "direction must be one of"),
            ("wrap", "wrap must be one of"),
            ("justify_content", "justify_content must be one of"),
            ("align_items", "align_items must be one of"),
            ("gap", "gap must be normal or a supported CSS length or percentage"),
        )
        for field, message in cases:
            with self.subTest(field=field):
                result = run_json_raw({field: None})
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_gap_and_closed_input_shape_are_validated(self) -> None:
        cases = (
            ({"gap": "-1px"}, "gap must not be negative"),
            ({"gap": "1.px"}, "gap must be normal or a supported CSS length or percentage"),
            ({"gap": "1rem; color: red"}, "gap must be normal or a supported CSS length or percentage"),
            ({"extra": True}, "Input supports only"),
        )

        for data, message in cases:
            with self.subTest(data=data):
                result = run_json_raw(data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

    def test_items_preserve_source_order_and_expose_order_modified_order(self) -> None:
        report = run_json(
            {
                "items": [
                    {"id": "first", "order": 2},
                    {"id": "second", "order": -1},
                    {"id": "third"},
                ]
            }
        )

        self.assertEqual(report["source_order"], ["first", "second", "third"])
        self.assertEqual(report["order_modified_source_order"], ["second", "third", "first"])
        self.assertEqual([item["source_index"] for item in report["items"]], [0, 1, 2])
        self.assertIn("DOM", report["accessibility"][0])

    def test_invalid_items_are_rejected_without_inferring_layout(self) -> None:
        cases = (
            ({"items": "a"}, "items must be an array"),
            ({"items": ["a"]}, "items[0] must be an object"),
            ({"items": [{"id": ""}]}, "items[0].id must be a simple identifier"),
            ({"items": [{"id": "a", "order": True}]}, "items[0].order must be an integer"),
            ({"items": [{"id": "a"}, {"id": "a"}]}, "item ids must be unique"),
            ({"items": [{"id": "a", "size": "20px"}]}, "items[0] supports only id and order"),
        )

        for data, message in cases:
            with self.subTest(data=data):
                result = run_json_raw(data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

        report = run_json({})
        self.assertNotIn("sizes", report)
        self.assertTrue(any("dimensions" in limitation for limitation in report["limitations"]))

    def test_item_identifier_and_order_bounds_are_explicit(self) -> None:
        maximum_identifier = "a" + "x" * 127
        report = run_json(
            {
                "items": [
                    {"id": maximum_identifier, "order": -2_147_483_648},
                    {"id": "maximum-order", "order": 2_147_483_647},
                ]
            }
        )
        self.assertEqual(report["source_order"], [maximum_identifier, "maximum-order"])

        cases = (
            (
                {"items": [{"id": "a" + "x" * 128}]},
                "items[0].id must be at most 128 characters",
            ),
            (
                {"items": [{"id": "a", "order": -2_147_483_649}]},
                "items[0].order must be between -2147483648 and 2147483647",
            ),
            (
                {"items": [{"id": "a", "order": 2_147_483_648}]},
                "items[0].order must be between -2147483648 and 2147483647",
            ),
        )
        for data, message in cases:
            with self.subTest(message=message):
                result = run_json_raw(data)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)
                self.assertNotIn("Traceback", result.stderr)

    def test_items_array_has_a_deterministic_limit(self) -> None:
        at_limit = [{"id": f"item-{index}"} for index in range(1000)]
        self.assertEqual(len(run_json({"items": at_limit})["items"]), 1000)

        result = run_json_raw({"items": [*at_limit, {"id": "one-too-many"}]})
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("items must contain at most 1000 entries", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_input_size_and_python_integer_digit_failures_are_actionable(self) -> None:
        oversized_input = invoke(None, "--format", "json", raw_stdin=" " * 65_537)
        self.assertNotEqual(oversized_input.returncode, 0)
        self.assertIn("JSON input must not exceed 65536 UTF-8 bytes", oversized_input.stderr)
        self.assertNotIn("Traceback", oversized_input.stderr)

        with tempfile.TemporaryDirectory() as directory:
            oversized_path = Path(directory) / "oversized.json"
            oversized_path.write_text(" " * 65_537, encoding="utf-8")
            oversized_file = invoke(
                None, "--input", str(oversized_path), "--format", "json"
            )
        self.assertNotEqual(oversized_file.returncode, 0)
        self.assertIn("JSON input must not exceed 65536 UTF-8 bytes", oversized_file.stderr)
        self.assertNotIn("Traceback", oversized_file.stderr)

        oversized_integer = invoke(
            None,
            "--format",
            "json",
            raw_stdin='{"items":[{"id":"a","order":' + "9" * 5000 + "}]}",
        )
        self.assertNotEqual(oversized_integer.returncode, 0)
        self.assertIn("Unable to read JSON input", oversized_integer.stderr)
        self.assertNotIn("Traceback", oversized_integer.stderr)

    def test_exact_maximum_input_size_is_accepted_for_stdin_and_file(self) -> None:
        maximum_input = "{}" + " " * (65_536 - 2)
        self.assertEqual(len(maximum_input.encode("utf-8")), 65_536)

        stdin_result = invoke(None, "--format", "json", raw_stdin=maximum_input)
        self.assertEqual(stdin_result.returncode, 0, stdin_result.stderr)
        self.assertEqual(json.loads(stdin_result.stdout)["source_order"], [])

        with tempfile.TemporaryDirectory() as directory:
            maximum_path = Path(directory) / "maximum.json"
            maximum_path.write_text(maximum_input, encoding="utf-8")
            file_result = invoke(None, "--input", str(maximum_path), "--format", "json")
        self.assertEqual(file_result.returncode, 0, file_result.stderr)
        self.assertEqual(json.loads(file_result.stdout)["source_order"], [])

    def test_deeply_nested_valid_json_is_an_actionable_parser_error(self) -> None:
        nested_input = '{"items":' + "[" * 10_000 + "0" + "]" * 10_000 + "}"
        self.assertLess(len(nested_input.encode("utf-8")), 65_536)

        result = invoke(None, "--format", "json", raw_stdin=nested_input)

        self.assertNotEqual(result.returncode, 0)
        self.assertIn("JSON nesting exceeds the supported parser depth", result.stderr)
        self.assertNotIn("Traceback", result.stderr)

    def test_json_nesting_limit_accepts_256_and_rejects_257(self) -> None:
        module = load_flexbox_cli()
        at_limit = '{"items":' + "[" * 255 + "0" + "]" * 255 + "}"
        over_limit = '{"items":' + "[" * 256 + "0" + "]" * 256 + "}"

        parsed = module.read_json("-", io.StringIO(at_limit))
        self.assertIn("items", parsed)

        with self.assertRaisesRegex(
            module.InputError, "JSON nesting exceeds the supported parser depth"
        ):
            module.read_json("-", io.StringIO(over_limit))

    def test_json_depth_scanner_ignores_brackets_and_escaped_quotes_in_strings(self) -> None:
        module = load_flexbox_cli()
        raw = r'{"direction":"row","note":"[{\"]}] escaped brackets"}'

        parsed = module.read_json("-", io.StringIO(raw))

        self.assertEqual(parsed["note"], '[{"]}] escaped brackets')

    def test_json_depth_limit_applies_to_file_input(self) -> None:
        module = load_flexbox_cli()
        over_limit = '{"items":' + "[" * 256 + "0" + "]" * 256 + "}"
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nested.json"
            path.write_text(over_limit, encoding="utf-8")

            with self.assertRaisesRegex(
                module.InputError, "JSON nesting exceeds the supported parser depth"
            ):
                module.read_json(str(path), io.StringIO(""))

    def test_model_exposes_frozen_typed_item_records(self) -> None:
        spec = importlib.util.spec_from_file_location("flexbox_model", FLEX_MODEL)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)

        flexbox = module.Flexbox.from_data({"items": [{"id": "item"}]})

        self.assertIsInstance(flexbox.items, tuple)
        with self.assertRaisesRegex(Exception, "cannot assign to field"):
            flexbox.items[0].order = 2

    def test_file_stdin_css_human_evidence_and_help_are_supported(self) -> None:
        data = json.loads((FIXTURES / "flexbox-wrapped.json").read_text(encoding="utf-8"))
        first = run_json_raw(data)
        second = run_json_raw(data)
        css = invoke(data, "--format", "css")
        human = invoke(data)
        evidence = invoke(data, "--format", "json", "--evidence")
        help_result = invoke(None, "--help")

        self.assertEqual(first.returncode, 0, first.stderr)
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(css.stdout.strip(), json.loads(first.stdout)["css"])
        self.assertIn("inline-end-to-inline-start", human.stdout)
        envelope = json.loads(evidence.stdout)
        self.assertEqual(envelope["core"], json.loads(first.stdout))
        self.assertEqual(envelope["classification"], "unavailable")
        self.assertEqual(envelope["observations"], [])
        self.assertEqual(help_result.returncode, 0, help_result.stderr)
        self.assertIn("Flexbox", help_result.stdout)

    def test_malformed_json_and_invalid_utf8_are_actionable(self) -> None:
        malformed = invoke(None, "--format", "json", raw_stdin="{")
        self.assertNotEqual(malformed.returncode, 0)
        self.assertIn("Unable to read JSON input", malformed.stderr)
        self.assertNotIn("Traceback", malformed.stderr)

        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "flexbox.json"
            path.write_bytes(b"\xff")
            invalid_utf8 = invoke(None, "--input", str(path), "--format", "json")

        self.assertNotEqual(invalid_utf8.returncode, 0)
        self.assertIn("input is not valid UTF-8", invalid_utf8.stderr)
        self.assertNotIn("Traceback", invalid_utf8.stderr)


if __name__ == "__main__":
    unittest.main()
