import json
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from scripts.sync_upstreams import sync, verify

ROOT = Path(__file__).resolve().parents[1]


class UpstreamIntegrityTests(unittest.TestCase):
    def test_update_restores_vendor_when_lock_install_fails(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            selection_path = root / "selection.json"
            selection_path.write_text(
                json.dumps(
                    {
                        "source": {
                            "repository": "https://example.invalid/source.git",
                            "paths": ["skills/module"],
                        }
                    }
                ),
                encoding="utf-8",
            )
            old_vendor_file = root / "vendor" / "source" / "skills" / "module" / "SKILL.md"
            old_vendor_file.parent.mkdir(parents=True)
            old_vendor_file.write_text("old vendor", encoding="utf-8")
            old_lock = {"sources": {"source": {"commit": "0" * 40, "files": {}}}}
            (root / "upstream-lock.json").write_text(json.dumps(old_lock), encoding="utf-8")

            def fake_run_git(arguments, cwd=None):
                if arguments[0] == "clone":
                    clone = Path(arguments[-1])
                    imported = clone / "skills" / "module"
                    imported.mkdir(parents=True)
                    (imported / "SKILL.md").write_text("new vendor", encoding="utf-8")
                    return ""
                self.assertEqual(arguments, ["rev-parse", "HEAD"])
                return "1" * 40

            real_replace = os.replace

            def fail_lock_replace(source, destination):
                if Path(destination) == root / "upstream-lock.json":
                    raise OSError("simulated lock replacement failure")
                real_replace(source, destination)

            with (
                mock.patch("scripts.sync_upstreams._run_git", side_effect=fake_run_git),
                mock.patch("scripts.sync_upstreams.os.replace", side_effect=fail_lock_replace),
            ):
                with self.assertRaisesRegex(OSError, "simulated lock replacement failure"):
                    sync(selection_path, root, update=True)

            self.assertEqual(old_vendor_file.read_text(encoding="utf-8"), "old vendor")
            self.assertEqual(
                json.loads((root / "upstream-lock.json").read_text(encoding="utf-8")), old_lock
            )
            self.assertFalse((root / ".vendor-sync-backup").exists())
            self.assertEqual(
                {entry.name for entry in root.iterdir()},
                {"selection.json", "upstream-lock.json", "vendor"},
            )

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
