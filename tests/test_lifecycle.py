import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from skills.supervaults.scripts.supervaults.context import find_context
from skills.supervaults.scripts.supervaults.lifecycle import close_session, open_daily_plan, open_session
from skills.supervaults.scripts.supervaults.markdown import parse_note, write_note
from skills.supervaults.scripts.supervaults.vault import initialize_vault


class LifecycleTests(unittest.TestCase):
    def test_daily_plan_is_retained_and_linked_to_previous_day(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 26))
            first = open_daily_plan(vault, date(2026, 8, 26))
            second = open_daily_plan(vault, date(2026, 8, 27))
            self.assertEqual(parse_note(second).properties["previous_day"], f"[[{first.stem}]]")
            self.assertEqual(open_daily_plan(vault, date(2026, 8, 27)), second)

    def test_new_owner_gets_unique_session_with_workstream_link(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream_dir = vault / "workstreams/barcode-scanning"
            workstream_dir.mkdir()
            workstream = workstream_dir / "Barcode Scanning.md"
            workstream.write_text("---\ntype: workstream\nstage: design\nstatus: active\nproject: '[[Home]]'\n---\n# Barcode Scanning\n", encoding="utf-8")
            session = open_session(vault, workstream, "design", datetime(2026, 8, 27, 9, 30), "agent-a")
            note = parse_note(session)
            self.assertEqual(note.properties["workstream"], "[[Barcode Scanning]]")
            self.assertEqual(note.properties["owner"], "agent-a")
            self.assertIn("0930", session.name)
            self.assertEqual(parse_note(workstream).properties["current_session"], f"[[{session.stem}]]")

    def test_close_requires_evidence_then_reconciles_workstream(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream_dir = vault / "workstreams/barcode-scanning"
            workstream_dir.mkdir()
            workstream = workstream_dir / "Barcode Scanning.md"
            workstream.write_text("---\ntype: workstream\nstage: verification\nstatus: active\nproject: '[[Home]]'\n---\n# Barcode Scanning\n", encoding="utf-8")
            session = open_session(vault, workstream, "verify", datetime(2026, 8, 27, 9, 30), "agent-a")

            with self.assertRaisesRegex(ValueError, "Actual blast radius"):
                close_session(vault, session, "abc123")

            note = parse_note(session)
            body = note.body.replace("## Actual blast radius\n", "## Actual blast radius\n\nAffected scanner parsing only.\n")
            body = body.replace("## Verification evidence\n", "## Verification evidence\n\nAll focused tests pass.\n")
            body = body.replace("## Handoff\n", "## Handoff\n\nReview the release checklist.\n")
            write_note(note.__class__(note.path, note.properties, body))
            close_session(vault, session, "abc123")

            closed = parse_note(session)
            owning = parse_note(workstream)
            self.assertEqual(closed.properties["status"], "verified")
            self.assertEqual(closed.properties["end_commit"], "abc123")
            self.assertEqual(owning.properties["latest_session"], f"[[{session.stem}]]")
            self.assertNotIn("current_session", owning.properties)

    def test_context_ranks_property_and_workstream_filename_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream_dir = vault / "workstreams/barcode-scanning"
            workstream_dir.mkdir()
            workstream = workstream_dir / "Barcode Scanning.md"
            workstream.write_text("---\ntype: workstream\nstage: design\nstatus: active\nproject: '[[Home]]'\narea: barcode\n---\n# Barcode Scanning\n\nSee [[Home]].\n", encoding="utf-8")
            secondary = vault / "knowledge" / "Note.md"
            secondary.write_text("---\ntype: knowledge\nstatus: current\nproject: '[[Home]]'\n---\n# A note\n\nbarcode appears only in the body.\n", encoding="utf-8")

            report = find_context(vault, ["BARCODE"])

            self.assertEqual(report.project, vault / "Home.md")
            self.assertEqual(report.candidates[0].path, workstream)
            self.assertGreater(report.candidates[0].score, report.candidates[1].score)
            self.assertTrue(all(len(reason) <= 240 for candidate in report.candidates for reason in candidate.reasons))


if __name__ == "__main__":
    unittest.main()
