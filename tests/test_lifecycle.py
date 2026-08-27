import contextlib
import io
import json
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from skills.supervaults.scripts.supervaults.context import find_context
from skills.supervaults.scripts.supervaults.cli import main
from skills.supervaults.scripts.supervaults.lifecycle import (
    LifecycleStateError,
    close_session,
    open_daily_plan,
    open_session,
)
from skills.supervaults.scripts.supervaults.markdown import parse_note, write_note
from skills.supervaults.scripts.supervaults.vault import initialize_vault


class LifecycleTests(unittest.TestCase):
    def _workstream(self, vault: Path, relative: str = "barcode-scanning/Barcode Scanning.md") -> Path:
        workstream = vault / "workstreams" / relative
        workstream.parent.mkdir(parents=True, exist_ok=True)
        workstream.write_text("---\ntype: workstream\nstage: verification\nstatus: active\nproject: '[[Home]]'\n---\n# Barcode Scanning\n", encoding="utf-8")
        return workstream

    def _evidence_body(self, body: str, actual: str = "- Surface: Tests and tooling\n  State: changed\n  Detail: Focused lifecycle coverage was added.", verification: str = "Check: python -m unittest tests.test_lifecycle -v\nResult: passed — 10 lifecycle tests", handoff: str = "Current state: Lifecycle evidence is recorded.\nNext action: Review the release checklist.") -> str:
        body = body.replace("## Actual blast radius\n", f"## Actual blast radius\n\n{actual}\n")
        body = body.replace("## Verification evidence\n", f"## Verification evidence\n\n{verification}\n")
        return body.replace("## Handoff\n", f"## Handoff\n\n{handoff}\n")

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
            workstream = self._workstream(vault)
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
            workstream = self._workstream(vault)
            session = open_session(vault, workstream, "verify", datetime(2026, 8, 27, 9, 30), "agent-a")

            with self.assertRaisesRegex(ValueError, "Actual blast radius"):
                close_session(vault, session, "abc123")

            note = parse_note(session)
            body = self._evidence_body(note.body, verification="Check: python -m unittest tests.test_lifecycle -v\nResult: passed — 10 lifecycle tests")
            write_note(note.__class__(note.path, note.properties, body))
            close_session(vault, session, "abc123")

            closed = parse_note(session)
            owning = parse_note(workstream)
            self.assertEqual(closed.properties["status"], "verified")
            self.assertEqual(closed.properties["end_commit"], "abc123")
            self.assertEqual(owning.properties["latest_session"], f"[[{session.stem}]]")
            self.assertNotIn("current_session", owning.properties)

    def test_close_rejects_unstructured_placeholder_and_non_observable_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream = self._workstream(vault)
            for index, (actual, verification, handoff) in enumerate((
                ("hello world", "Check: focused test\nResult: passed — 1 check", "Current state: active\nNext action: review"),
                ("- Surface: Tests and tooling\n  State: changed\n  Detail: scanner parser", "Check: TBD\nResult: passed — 1 check", "Current state: active\nNext action: review"),
                ("- Surface: Tests and tooling\n  State: changed\n  Detail: scanner parser", "Check: focused test\nResult: passed content", "Current state: active\nNext action: review"),
                ("- Surface: Tests and tooling\n  State: changed\n  Detail: {{DETAIL}}", "Check: focused test\nResult: passed — 1 check", "Current state: active\nNext action: review"),
                ("- Surface: Tests and tooling\n  State: changed\n  Detail: scanner parser", "Check: focused test\nResult: NOT-RUN", "Current state: PLACEHOLDER\nNext action: review"),
                ("- Surface:\n  State:\n  Detail:", "Check:\nResult:", "Current state:\nNext action:"),
            )):
                session = open_session(vault, workstream, f"verify {index}", datetime(2026, 8, 27, 9, 30 + index), "agent-a")
                note = parse_note(session)
                write_note(note.__class__(note.path, note.properties, self._evidence_body(note.body, actual, verification, handoff)))
                with self.assertRaises(LifecycleStateError):
                    close_session(vault, session, None)

    def test_close_preserves_explicit_complete_and_nonmatching_current_session(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream = self._workstream(vault)
            session = open_session(vault, workstream, "verify", datetime(2026, 8, 27, 9, 30), "agent-a")
            note = parse_note(session)
            properties = dict(note.properties)
            properties["status"] = "complete"
            write_note(note.__class__(note.path, properties, self._evidence_body(note.body)))
            owner = parse_note(workstream)
            owner_properties = dict(owner.properties)
            owner_properties["current_session"] = "[[other-session]]"
            write_note(owner.__class__(owner.path, owner_properties, owner.body))

            close_session(vault, session, None)

            self.assertEqual(parse_note(session).properties["status"], "complete")
            self.assertEqual(parse_note(workstream).properties["current_session"], "[[other-session]]")

    def test_open_session_rejects_collision_invalid_metadata_and_noncanonical_paths(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream = self._workstream(vault)
            now = datetime(2026, 8, 27, 9, 30)
            open_session(vault, workstream, "design", now, "agent-a")
            with self.assertRaises(LifecycleStateError):
                open_session(vault, workstream, "design", now, "agent-a")

            malformed = vault / "workstreams/malformed/Malformed.md"
            malformed.parent.mkdir()
            malformed.write_text("---\ntype: workstream\nstatus: active\nproject: '[[Home]]'\n---\n# Malformed\n", encoding="utf-8")
            with self.assertRaises(LifecycleStateError):
                open_session(vault, malformed, "design", now, "agent-a")

            malformed_frontmatter = vault / "workstreams/broken/Broken.md"
            malformed_frontmatter.parent.mkdir()
            malformed_frontmatter.write_text("---\n  type: workstream\n---\n# Broken\n", encoding="utf-8")
            with self.assertRaises(ValueError):
                open_session(vault, malformed_frontmatter, "design", now, "agent-a")

            nested = self._workstream(vault, "barcode-scanning/notes/Nested.md")
            archived = self._workstream(vault, "archive/barcode-scanning/Archived.md")
            with self.assertRaises(LifecycleStateError):
                open_session(vault, nested, "design", now, "agent-a")
            with self.assertRaises(LifecycleStateError):
                open_session(vault, archived, "design", now, "agent-a")

    def test_close_rejects_session_outside_the_owning_sessions_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream = self._workstream(vault)
            session = vault / "records" / "misplaced.md"
            session.parent.mkdir(exist_ok=True)
            session.write_text("---\ntype: work-session\nstatus: active\nproject: '[[Home]]'\nworkstream: '[[Barcode Scanning]]'\n---\n# Misplaced\n\n## Actual blast radius\n\n- Surface: Tests and tooling\n  State: changed\n  Detail: Scanner tests changed.\n\n## Verification evidence\n\nCheck: focused scanner tests\nResult: passed — 1 test\n\n## Handoff\n\nCurrent state: Evidence is ready.\nNext action: Review the checklist.\n", encoding="utf-8")
            with self.assertRaises(LifecycleStateError):
                close_session(vault, session, None)

    def test_context_ranks_property_and_workstream_filename_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream = self._workstream(vault)
            workstream.write_text("---\ntype: workstream\nstage: design\nstatus: active\nproject: '[[Home]]'\narea: barcode\n---\n# Barcode Scanning\n\nSee [[Home]].\n", encoding="utf-8")
            secondary = vault / "knowledge" / "Note.md"
            secondary.write_text("---\ntype: knowledge\nstatus: current\nproject: '[[Home]]'\n---\n# A note\n\nbarcode appears only in the body.\n", encoding="utf-8")

            report = find_context(vault, ["BARCODE"])

            self.assertEqual(report.project, vault / "Home.md")
            self.assertEqual(report.candidates[0].path, workstream)
            self.assertGreater(report.candidates[0].score, report.candidates[1].score)
            self.assertTrue(all(len(reason) <= 240 for candidate in report.candidates for reason in candidate.reasons))

    def test_context_exact_match_outranks_repeated_body_matches(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream = self._workstream(vault)
            noisy = vault / "knowledge" / "Noisy.md"
            noisy.write_text("---\ntype: knowledge\nstatus: current\nproject: '[[Home]]'\n---\n# Notes\n\n" + "barcode body match.\n" * 100, encoding="utf-8")

            report = find_context(vault, ["barcode"])

            self.assertEqual(report.candidates[0].path, workstream)

    def test_cli_context_is_json_and_classifies_state_and_integrity_errors(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            output = io.StringIO()
            with contextlib.redirect_stdout(output):
                self.assertEqual(main(["context", "--vault", str(vault), "inventory"]), 0)
            payload = json.loads(output.getvalue())
            self.assertEqual(set(payload), {"project", "candidates", "git_branch", "git_commit", "warnings"})

            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["close-session", "--vault", str(vault), "--session", str(vault / "missing.md")]), 2)

            malformed = vault / "bad.md"
            malformed.write_text("not frontmatter\n", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["close-session", "--vault", str(vault), "--session", str(malformed)]), 1)

            broken = vault / "workstreams/barcode-scanning/sessions/2026-08-27-0930-verify.md"
            broken.parent.mkdir(parents=True)
            broken.write_text("---\ntype: work-session\nstatus: active\nproject: '[[Home]]'\nworkstream: '[[Missing]]'\n---\n# Broken\n\n## Actual blast radius\n\n- Surface: Tests and tooling\n  State: changed\n  Detail: Scanner tests changed.\n\n## Verification evidence\n\nCheck: focused scanner tests\nResult: passed — 1 test\n\n## Handoff\n\nCurrent state: Evidence is ready.\nNext action: Review the checklist.\n", encoding="utf-8")
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(main(["close-session", "--vault", str(vault), "--session", str(broken)]), 1)


if __name__ == "__main__":
    unittest.main()
