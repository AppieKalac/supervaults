import contextlib
import io
import json
import shutil
import tempfile
import unittest
from datetime import date
from pathlib import Path

from skills.supervaults.scripts.supervaults.cli import main
from skills.supervaults.scripts.supervaults.validation import validate_vault


FIXTURES = Path(__file__).parent / "fixtures"


class ValidationTests(unittest.TestCase):
    def _copied_valid_vault(self, directory: str) -> Path:
        destination = Path(directory) / "vault"
        shutil.copytree(FIXTURES / "valid-vault", destination)
        return destination

    def _replace(self, path: Path, old: str, new: str) -> None:
        content = path.read_text(encoding="utf-8")
        self.assertIn(old, content)
        path.write_text(content.replace(old, new), encoding="utf-8")

    def test_valid_fixture_has_no_errors(self):
        report = validate_vault(FIXTURES / "valid-vault", date(2026, 8, 27))
        self.assertEqual(report.errors, ())

    def test_invalid_fixture_reports_each_integrity_fault(self):
        report = validate_vault(FIXTURES / "invalid-vault", date(2026, 8, 27))
        codes = {finding.code for finding in report.findings}
        self.assertEqual(codes, {
            "invalid-status", "dangling-current-session", "missing-handoff",
            "missing-completion-evidence", "stale-daily-plan", "broken-contract-link",
            "unsupported-delivery-state", "duplicate-canonical-workstream",
        })

    def test_findings_are_sorted_and_cli_json_has_stable_counts(self):
        vault = FIXTURES / "invalid-vault"
        report = validate_vault(vault, date(2026, 8, 27))
        self.assertEqual(
            list(report.findings),
            sorted(
                report.findings,
                key=lambda finding: (
                    {"error": 0, "warning": 1, "notice": 2}[finding.severity],
                    finding.path.as_posix().casefold(),
                    finding.code,
                    finding.message,
                ),
            ),
        )

        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            result = main(["validate", "--vault", str(vault), "--json"])
        payload = json.loads(output.getvalue())
        self.assertEqual(result, 1)
        self.assertEqual(payload["errors"], len(report.errors))
        self.assertEqual(payload["findings"], len(report.findings))
        self.assertEqual(payload["findings"], len(payload["finding_details"]))

    def test_relationship_targets_must_have_the_expected_type(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = self._copied_valid_vault(directory)
            workstream = vault / "workstreams/inventory-scanning/Inventory Scanning.md"
            self._replace(workstream, 'project: "[[Home]]"', 'project: "[[Inventory Scanning Plan]]"')

            codes = {finding.code for finding in validate_vault(vault, date(2026, 8, 27)).errors}

        self.assertIn("invalid-relationship-target", codes)

    def test_current_session_must_be_open_and_owned_by_its_workstream(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = self._copied_valid_vault(directory)
            workstream = vault / "workstreams/inventory-scanning/Inventory Scanning.md"
            self._replace(
                workstream,
                'latest_session: "[[2026-08-27-0930-verify-scanner]]"',
                'latest_session: "[[2026-08-27-0930-verify-scanner]]"\ncurrent_session: "[[2026-08-27-0930-verify-scanner]]"',
            )
            second = vault / "workstreams/second/Second.md"
            second.parent.mkdir()
            second.write_text(
                "---\n"
                "type: workstream\n"
                "stage: verification\n"
                "status: active\n"
                "project: \"[[Home]]\"\n"
                "---\n"
                "# Second\n\n## Outcome\n\nSecond outcome.\n",
                encoding="utf-8",
            )
            session = vault / "workstreams/inventory-scanning/sessions/2026-08-27-0930-verify-scanner.md"
            self._replace(session, 'workstream: "[[Inventory Scanning]]"', 'workstream: "[[Second]]"')

            codes = {finding.code for finding in validate_vault(vault, date(2026, 8, 27)).errors}

        self.assertIn("invalid-current-session-state", codes)
        self.assertIn("session-workstream-ownership", codes)

    def test_complete_workstream_cannot_use_another_workstreams_session_as_evidence(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = self._copied_valid_vault(directory)
            second = vault / "workstreams/second/Second.md"
            second.parent.mkdir()
            second.write_text(
                "---\n"
                "type: workstream\n"
                "stage: verification\n"
                "status: complete\n"
                "project: \"[[Home]]\"\n"
                "latest_session: \"[[2026-08-27-0930-verify-scanner]]\"\n"
                "---\n"
                "# Second\n\n"
                "## Outcome\n\nSecond outcome.\n\n"
                "## Completed\n\nThe outcome is complete.\n",
                encoding="utf-8",
            )

            codes = {finding.code for finding in validate_vault(vault, date(2026, 8, 27)).errors}

        self.assertIn("completion-evidence-ownership", codes)

    def test_delivery_claim_requires_substantive_environment_and_identifier(self):
        placeholders = ("", "   ", "TBD", "TODO", "placeholder", "unknown", "none", "{{ENVIRONMENT}}")
        for field in ("environments", "end_commit"):
            for placeholder in placeholders:
                with self.subTest(field=field, placeholder=placeholder), tempfile.TemporaryDirectory() as directory:
                    vault = self._copied_valid_vault(directory)
                    workstream = vault / "workstreams/inventory-scanning/Inventory Scanning.md"
                    environment = placeholder if field == "environments" else "staging"
                    commit = placeholder if field == "end_commit" else "abc1234"
                    self._replace(
                        workstream,
                        'latest_session: "[[2026-08-27-0930-verify-scanner]]"',
                        'latest_session: "[[2026-08-27-0930-verify-scanner]]"\nenvironments: "' + environment + '"\nend_commit: "' + commit + '"',
                    )
                    self._replace(workstream, "## Next action", "## Delivery state\n\nDeployed to staging.\n\n## Next action")

                    codes = {finding.code for finding in validate_vault(vault, date(2026, 8, 27)).errors}

                    self.assertIn("unsupported-delivery-state", codes)

    def test_delivery_claim_accepts_concrete_environment_and_commit(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = self._copied_valid_vault(directory)
            workstream = vault / "workstreams/inventory-scanning/Inventory Scanning.md"
            self._replace(
                workstream,
                'latest_session: "[[2026-08-27-0930-verify-scanner]]"',
                'latest_session: "[[2026-08-27-0930-verify-scanner]]"\nenvironments: "staging"\nend_commit: "abc1234"',
            )
            self._replace(workstream, "## Next action", "## Delivery state\n\nDeployed to staging.\n\n## Next action")

            report = validate_vault(vault, date(2026, 8, 27))

        self.assertEqual(report.errors, ())


if __name__ == "__main__":
    unittest.main()
