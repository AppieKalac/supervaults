import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginStructureTests(unittest.TestCase):
    def test_manifest_registers_exactly_one_skills_root(self):
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "supervaults")
        self.assertRegex(
            manifest["version"],
            r"^0\.1\.0(?:\+codex\.[A-Za-z0-9.-]+)?$",
        )
        self.assertEqual(manifest["skills"], "./skills/")

    def test_only_supervaults_is_registered(self):
        skills = sorted(
            path.name for path in (ROOT / "skills").iterdir() if path.is_dir()
        )
        self.assertEqual(skills, ["supervaults"])

    def test_skill_metadata_exists(self):
        self.assertTrue((ROOT / "skills/supervaults/SKILL.md").exists())
        self.assertTrue((ROOT / "skills/supervaults/agents/openai.yaml").exists())


if __name__ == "__main__":
    unittest.main()
