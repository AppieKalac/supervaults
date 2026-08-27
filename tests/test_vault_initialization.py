import tempfile
import unittest
from datetime import date
from pathlib import Path

from skills.supervaults.scripts.supervaults.markdown import parse_note
from skills.supervaults.scripts.supervaults.vault import initialize_vault, render_template


class VaultInitializationTests(unittest.TestCase):
    def test_initializes_work_centered_structure_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            created = initialize_vault(vault, "Inventory", date(2026, 8, 27))
            self.assertTrue((vault / "Home.md").exists())
            for relative in (
                "daily", "workstreams", "workstreams/archive",
                "superpowers/specs", "superpowers/plans",
                "records/decisions", "records/investigations",
                "records/reviews", "records/incidents", "records/releases",
                "knowledge", "inbox", "views", "templates",
            ):
                self.assertTrue((vault / relative).is_dir(), relative)
            self.assertEqual(parse_note(vault / "Home.md").properties["type"], "project")
            self.assertGreater(len(created), 0)
            self.assertEqual(initialize_vault(vault, "Inventory", date(2026, 8, 27)), [])

    def test_initialization_renders_templates_and_preserves_existing_notes(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            vault.mkdir()
            home = vault / "Home.md"
            home.write_text("Keep this note.\n", encoding="utf-8")

            created = initialize_vault(vault, "Inventory", date(2026, 8, 27))

            self.assertEqual(home.read_text(encoding="utf-8"), "Keep this note.\n")
            self.assertNotIn(home, created)
            self.assertIn(vault / "daily" / "2026-08-27.md", created)
            daily = parse_note(vault / "daily" / "2026-08-27.md")
            self.assertEqual(daily.properties["type"], "daily-plan")
            self.assertEqual(daily.properties["date"], "2026-08-27")
            self.assertIn("## End-of-day reconciliation", daily.body)

    def test_render_template_replaces_known_markers_and_rejects_unresolved_ones(self):
        with tempfile.TemporaryDirectory() as directory:
            template = Path(directory) / "note.tmpl"
            template.write_text("# {{PROJECT_NAME}} on {{DATE}}\n", encoding="utf-8")
            self.assertEqual(
                render_template(template, {"PROJECT_NAME": "Inventory", "DATE": "2026-08-27"}),
                "# Inventory on 2026-08-27\n",
            )
            template.write_text("# {{MISSING}}\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "unresolved template marker"):
                render_template(template, {})

    def test_daily_planning_base_displays_daily_plan_selections(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))

            daily = parse_note(vault / "daily" / "2026-08-27.md")
            base = (vault / "views" / "Daily Planning.base").read_text(encoding="utf-8")

            self.assertEqual(daily.properties["selected_workstreams"], "")
            self.assertIn('name: "Open daily plans"', base)
            self.assertIn("      - selected_workstreams", base)
            self.assertNotIn('name: "Selected workstreams"', base)
            self.assertNotIn('type == "workstream"', base)


if __name__ == "__main__":
    unittest.main()
