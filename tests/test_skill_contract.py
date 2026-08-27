import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/supervaults/SKILL.md"


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_has_broad_trigger_and_exclusions(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?s)^---\nname: supervaults\ndescription: .+\n---")
        description = text.split("---", 2)[1]
        for phrase in ("plan", "investigate", "implement", "review", "consolidate", "project vault"):
            self.assertIn(phrase, description.lower())

    def test_required_modes_and_gates_are_present(self):
        text = SKILL.read_text(encoding="utf-8").lower()
        for token in ("orient", "plan", "investigate", "design", "implement", "review", "consolidate", "deliver", "capture"):
            self.assertIn(token, text)
        for token in ("preinspect", "expected blast radius", "actual blast radius", "handoff", "validate"):
            self.assertIn(token, text)

    def test_every_markdown_reference_resolves(self):
        text = SKILL.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", text):
            self.assertTrue((SKILL.parent / target).resolve().exists(), target)


if __name__ == "__main__":
    unittest.main()
