import json
import unittest
from pathlib import Path


PLUGIN = Path(__file__).resolve().parents[1]
SKILLS = PLUGIN / "skills"
GUIDE_COVERAGE = PLUGIN / "references" / "guide-coverage.json"
TEXT_SUFFIXES = {".json", ".md", ".py", ".yaml", ".yml"}
FORBIDDEN_TERMS = (
    "wind" + "surf",
    "de" + "vin",
    "cursor" + " rules",
    "clau" + "de",
)


class CodexOnlySurfaceTests(unittest.TestCase):
    def test_guide_inventory_has_exactly_seventeen_skills_and_rows(self) -> None:
        skill_directories = sorted(path for path in SKILLS.iterdir() if path.is_dir())
        guide_rows = json.loads(GUIDE_COVERAGE.read_text(encoding="utf-8"))

        self.assertEqual(len(skill_directories), 17)
        self.assertEqual(len(guide_rows), 17)

    def test_removed_agent_product_skill_is_absent(self) -> None:
        removed_skill = SKILLS / ("wind" + "surf-rules")

        self.assertFalse(removed_skill.exists())

    def test_plugin_text_has_no_other_agent_product_references(self) -> None:
        matches: list[str] = []
        for path in sorted(PLUGIN.rglob("*")):
            if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
                continue
            text = path.read_text(encoding="utf-8").casefold()
            for term in FORBIDDEN_TERMS:
                if term in text:
                    matches.append(f"{path.relative_to(PLUGIN)}: {term}")

        self.assertEqual(matches, [])

    def test_every_skill_has_codex_packaging_files(self) -> None:
        for skill_directory in sorted(path for path in SKILLS.iterdir() if path.is_dir()):
            with self.subTest(skill=skill_directory.name):
                self.assertTrue((skill_directory / "SKILL.md").is_file())
                self.assertTrue((skill_directory / "agents" / "openai.yaml").is_file())


if __name__ == "__main__":
    unittest.main()
