import json
import shutil
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))

from validate_coverage import validate


def validate_copy(
    *,
    mutate_fixtures=None,
    mutate_tools=None,
) -> dict[str, object]:
    with tempfile.TemporaryDirectory() as temporary_directory:
        plugin = Path(temporary_directory) / "css-tokenography"
        shutil.copytree(ROOT, plugin)
        fixture_path = plugin / "references" / "browser-fixtures.json"
        tool_path = plugin / "references" / "tool-coverage.json"
        fixtures = json.loads(fixture_path.read_text(encoding="utf-8"))
        tools = json.loads(tool_path.read_text(encoding="utf-8"))
        if mutate_fixtures is not None:
            mutate_fixtures(fixtures)
        if mutate_tools is not None:
            mutate_tools(tools)
        fixture_path.write_text(
            json.dumps(fixtures, indent=2) + "\n", encoding="utf-8"
        )
        tool_path.write_text(json.dumps(tools, indent=2) + "\n", encoding="utf-8")
        return validate(plugin)


class BrowserCoverageTests(unittest.TestCase):
    def test_manifest_covers_ten_three_engine_visual_fixtures(self) -> None:
        fixtures = json.loads(
            (ROOT / "references" / "browser-fixtures.json").read_text(
                encoding="utf-8"
            )
        )

        self.assertEqual(len(fixtures), 10)
        self.assertEqual(len({row["id"] for row in fixtures}), 10)
        for fixture in fixtures:
            self.assertEqual(
                set(fixture["required_engines"]),
                {"chromium", "firefox", "webkit"},
            )
            self.assertTrue(fixture["visual_baseline"])
            self.assertTrue((ROOT / fixture["fixture"]).is_file())

    def test_each_manifest_tool_has_exact_fixture_ownership(self) -> None:
        fixtures = json.loads(
            (ROOT / "references" / "browser-fixtures.json").read_text(
                encoding="utf-8"
            )
        )
        tools = json.loads(
            (ROOT / "references" / "tool-coverage.json").read_text(encoding="utf-8")
        )
        expected: dict[str, set[str]] = {}
        for fixture in fixtures:
            for url in fixture["tool_urls"]:
                expected.setdefault(url, set()).add(fixture["id"])

        by_url = {tool["url"]: tool for tool in tools}
        for url, fixture_ids in expected.items():
            evidence = by_url[url]["browser_evidence"]
            self.assertEqual(
                evidence["protocol"], "css-tokenography-browser-lab/v1"
            )
            self.assertEqual(set(evidence["fixtures"]), fixture_ids)

    def test_validator_rejects_missing_fixture_file(self) -> None:
        report = validate_copy(
            mutate_fixtures=lambda fixtures: fixtures[0].update(
                {"fixture": "laboratory/browser/fixtures/missing.html"}
            )
        )

        self.assertIn(
            "browser fixture gradient-runtime file is missing",
            report["errors"],
        )

    def test_validator_rejects_unknown_or_missing_browser_evidence(self) -> None:
        def mutate_unknown(tools):
            tool = next(
                row
                for row in tools
                if row["url"] == "https://design.dev/tools/gradient-mixer/"
            )
            tool["browser_evidence"]["fixtures"] = ["unknown-runtime"]

        unknown = validate_copy(mutate_tools=mutate_unknown)
        self.assertIn(
            "tool https://design.dev/tools/gradient-mixer/ browser_evidence names unknown fixtures: unknown-runtime",
            unknown["errors"],
        )

        def mutate_missing(tools):
            tool = next(
                row
                for row in tools
                if row["url"]
                == "https://design.dev/tools/backdrop-filter-playground/"
            )
            tool["browser_evidence"] = None

        missing = validate_copy(mutate_tools=mutate_missing)
        self.assertIn(
            "implemented browser-dependent tool https://design.dev/tools/backdrop-filter-playground/ requires browser_evidence",
            missing["errors"],
        )


if __name__ == "__main__":
    unittest.main()
