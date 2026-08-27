import json
import re
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
            r"^0\.1\.0\+codex\.\d{14}$",
        )
        self.assertEqual(manifest["skills"], "./skills/")

    def test_release_version_rejects_plain_or_malformed_cachebusters(self):
        release_version = re.compile(r"^0\.1\.0\+codex\.\d{14}$")
        invalid_versions = (
            "0.1.0",
            "0.1.0+codex.2026082715003",
            "0.1.0+codex.202608271500370",
            "0.1.0+codex.2026.08.27.150037",
            "0.1.0+codex.local-20260827150037",
            "0.1.0+codex.20260827150037+codex.20260827150038",
        )
        for version in invalid_versions:
            with self.subTest(version=version):
                self.assertIsNone(release_version.fullmatch(version))

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
