import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPTS = ROOT / "skills" / "css-grid" / "scripts"
FIXTURES = ROOT / "tests" / "fixtures"
CLI = SCRIPTS / "z_index_visualizer.py"
sys.path.insert(0, str(SCRIPTS))


def analyze_inline(elements):
    from stacking_context_model import analyze_tree

    return analyze_tree(elements)


def analyze_fixture(name):
    return analyze_inline(json.loads((FIXTURES / name).read_text())["elements"])


def element(identifier, parent="root", order=1, style=None, **facts):
    return {"id": identifier, "parent": parent, "order": order, "style": style or {}, **facts}


class StackingContextTests(unittest.TestCase):
    def test_nested_9999_cannot_escape_parent_context(self):
        report = analyze_fixture("stacking-nested-contexts.json")
        self.assertEqual(report["contexts"]["modal"]["parent_context"], "panel")
        self.assertLess(report["contexts"]["panel"]["z_index"], report["contexts"]["overlay"]["z_index"])
        self.assertEqual(report["contexts"]["root"]["children_in_paint_order"], ["panel", "overlay"])

    def test_trigger_matrix_records_independent_reasons(self):
        cases = [
            ("positioned", {"position": "relative", "z_index": 1}, {}, "positioned-z-index"),
            ("fixed", {"position": "fixed"}, {}, "fixed-or-sticky"),
            ("sticky", {"position": "sticky"}, {}, "fixed-or-sticky"),
            ("flex", {"z_index": 0}, {"is_flex_item": True}, "flex-or-grid-item-z-index"),
            ("grid", {"z_index": -1}, {"is_grid_item": True}, "flex-or-grid-item-z-index"),
            ("opacity", {"opacity": 0.9}, {}, "opacity"),
            ("blend", {"mix_blend_mode": "multiply"}, {}, "mix-blend-mode"),
            ("transform", {"transform": "translateX(0px)"}, {}, "transform"),
            ("scale", {"scale": "1"}, {}, "scale"),
            ("rotate", {"rotate": "0deg"}, {}, "rotate"),
            ("translate", {"translate": "0px"}, {}, "translate"),
            ("filter", {"filter": "blur(0px)"}, {}, "filter"),
            ("backdrop", {"backdrop_filter": "blur(1px)"}, {}, "backdrop-filter"),
            ("perspective", {"perspective": "800px"}, {}, "perspective"),
            ("clip", {"clip_path": "circle(50%)"}, {}, "clip-path"),
            ("mask", {"mask_image": "linear-gradient(black, transparent)"}, {}, "mask"),
            ("isolate", {"isolation": "isolate"}, {}, "isolation"),
            ("contain", {"contain": "paint"}, {}, "contain"),
            ("container", {"container_type": "inline-size"}, {}, "container-type"),
            ("will-change", {"will_change": "transform"}, {}, "will-change"),
        ]
        elements = [{"id": "root", "parent": None, "order": 0, "is_root": True, "style": {}}]
        for index, (identifier, style, facts, _) in enumerate(cases, 1):
            elements.append(element(identifier, order=index, style=style, **facts))
        elements.extend([
            element("top", order=30, top_layer=True),
            element("animated", order=31, retained_animation_properties=["opacity"]),
        ])
        report = analyze_inline(elements)
        for identifier, _, _, reason in cases:
            with self.subTest(identifier=identifier):
                self.assertIn(reason, report["elements"][identifier]["context_reasons"])
        self.assertIn("top-layer", report["elements"]["top"]["context_reasons"])
        self.assertIn("retained-animation", report["elements"]["animated"]["context_reasons"])

    def test_opacity_context_does_not_trap_fixed_descendant(self):
        report = analyze_fixture("stacking-containing-blocks.json")
        self.assertTrue(report["elements"]["opacity-surface"]["creates_context"])
        self.assertFalse(report["elements"]["opacity-surface"]["creates_fixed_containing_block"])
        self.assertEqual(report["elements"]["fixed-through-opacity"]["fixed_containing_block"], "viewport")
        self.assertEqual(report["elements"]["fixed-in-transform"]["fixed_containing_block"], "transformed")
        self.assertEqual(report["elements"]["absolute-in-transform"]["absolute_containing_block"], "transformed")

    def test_paint_phases_sort_negative_auto_zero_positive_and_equal_z_by_document_order(self):
        elements = [{"id": "root", "parent": None, "order": 0, "is_root": True, "style": {}}]
        elements += [
            element("positive-late", order=6, style={"position": "relative", "z_index": 2}),
            element("negative", order=4, style={"position": "relative", "z_index": -1}),
            element("zero", order=3, style={"position": "fixed", "z_index": 0}),
            element("auto", order=2, style={"position": "fixed", "z_index": "auto"}),
            element("positive-early", order=5, style={"position": "relative", "z_index": 2}),
        ]
        report = analyze_inline(elements)
        self.assertEqual(
            report["contexts"]["root"]["children_in_paint_order"],
            ["negative", "auto", "zero", "positive-early", "positive-late"],
        )
        self.assertEqual(report["contexts"]["negative"]["paint_phase"], "negative-z-index")
        self.assertEqual(report["contexts"]["positive-early"]["paint_phase"], "positive-z-index")

    def test_z_index_accepts_only_auto_integers_and_global_keywords(self):
        valid = ["auto", -1, 0, 2, "inherit", "initial", "revert", "revert-layer", "unset"]
        for index, value in enumerate(valid, 1):
            with self.subTest(value=value):
                analyze_inline([
                    {"id": "root", "parent": None, "order": 0, "is_root": True, "style": {}},
                    element("item", order=index, style={"position": "relative", "z_index": value}),
                ])
        for value in ["9999px", 1.5, "high", True]:
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "z_index"):
                    analyze_inline([
                        {"id": "root", "parent": None, "order": 0, "is_root": True, "style": {}},
                        element("item", style={"position": "relative", "z_index": value}),
                    ])

    def test_cli_rejects_raw_html_or_css_and_reports_collection_boundary(self):
        for payload in ({"html": "<div></div>"}, {"css": "div { z-index: 1 }"}):
            result = subprocess.run(
                [sys.executable, str(CLI), "--format", "json"],
                input=json.dumps(payload), text=True, capture_output=True, check=False,
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("pre-collected", result.stderr)
        result = subprocess.run(
            [sys.executable, str(CLI), "--input", str(FIXTURES / "stacking-nested-contexts.json"), "--format", "json"],
            text=True, capture_output=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("does not parse raw HTML/CSS", json.loads(result.stdout)["warnings"][0])


if __name__ == "__main__":
    unittest.main()
