import contextlib
import io
import json
import unittest
from datetime import date
from pathlib import Path

from skills.supervaults.scripts.supervaults.cli import main
from skills.supervaults.scripts.supervaults.validation import validate_vault


FIXTURES = Path(__file__).parent / "fixtures"


class ValidationTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
