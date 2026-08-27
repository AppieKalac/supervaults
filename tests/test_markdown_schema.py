import tempfile
import unittest
from pathlib import Path

from skills.supervaults.scripts.supervaults.markdown import Note, parse_note, write_note
from skills.supervaults.scripts.supervaults.schema import TYPE_STATUSES


class MarkdownSchemaTests(unittest.TestCase):
    def test_schema_contains_daily_and_workstream_states(self):
        self.assertEqual(TYPE_STATUSES["daily-plan"], {"open", "reconciled"})
        self.assertIn("complete", TYPE_STATUSES["workstream"])

    def test_frontmatter_round_trip_preserves_links_and_lists(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.md"
            original = Note(
                path,
                {
                    "type": "work-session",
                    "status": "active",
                    "project": "[[Home]]",
                    "components": ["api", "web"],
                },
                "# Session\n\nEvidence.\n",
            )
            write_note(original)
            parsed = parse_note(path)
            self.assertEqual(parsed.properties, original.properties)
            self.assertEqual(parsed.body, original.body)

    def test_missing_frontmatter_raises_clear_error(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.md"
            path.write_text("# No metadata\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "frontmatter"):
                parse_note(path)

    def test_scalar_subset_round_trips_and_orders_known_keys(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.md"
            note = Note(
                path,
                {
                    "zebra": "kept",
                    "created": "2026-08-27T12:00:00Z",
                    "risk": "low",
                    "project": "[[Home]]",
                    "date": "2026-08-27",
                    "flag": True,
                    "count": 3,
                    "stage": "implementation",
                    "type": "workstream",
                },
                "Body\r\n",
            )
            write_note(note)
            self.assertEqual(parse_note(path).properties, note.properties)
            self.assertEqual(parse_note(path).body, "Body\n")
            self.assertEqual(
                path.read_text(encoding="utf-8").splitlines()[1:10],
                [
                    'type: "workstream"',
                    'stage: "implementation"',
                    'project: "[[Home]]"',
                    'date: "2026-08-27"',
                    'risk: "low"',
                    'created: "2026-08-27T12:00:00Z"',
                    'count: 3',
                    'flag: true',
                    'zebra: "kept"',
                ],
            )

    def test_nested_mapping_names_file_and_property(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "note.md"
            path.write_text("---\ncontext:\n  owner: team\n---\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, r"note\.md.*context"):
                parse_note(path)


if __name__ == "__main__":
    unittest.main()
