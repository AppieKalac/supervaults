import json
import unittest
from pathlib import Path

from scripts.sync_upstreams import verify

ROOT = Path(__file__).resolve().parents[1]


class UpstreamIntegrityTests(unittest.TestCase):
    def test_lock_matches_vendor_tree(self):
        lock = json.loads((ROOT / "upstream-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(verify(ROOT, lock), [])

    def test_vendor_is_not_registered_as_plugin_skills(self):
        registered = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
        self.assertEqual(registered, {"supervaults"})

    def test_lock_contains_exact_selected_paths(self):
        selection = json.loads((ROOT / "upstream-selection.json").read_text())
        lock = json.loads((ROOT / "upstream-lock.json").read_text())
        for name, source in selection.items():
            self.assertEqual(lock["sources"][name]["paths"], source["paths"])
            self.assertRegex(lock["sources"][name]["commit"], r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
