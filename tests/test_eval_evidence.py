import json
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tests.evals.evidence import capture_snapshot, validate_record
from tests.evals.setup_fixture import create_fixture


ROOT = Path(__file__).resolve().parents[1]
CASES = json.loads((ROOT / "tests/evals/cases.json").read_text(encoding="utf-8"))


class EvaluationEvidenceTests(unittest.TestCase):
    def test_snapshot_retains_files_frontmatter_links_git_and_fake_audit(self):
        with tempfile.TemporaryDirectory() as directory:
            project = Path(directory) / "fixture"
            create_fixture(
                "established-multi-session", project, date(2031, 4, 5),
                "staging-established-authorized-only",
            )
            snapshot = capture_snapshot(project)
            self.assertTrue(snapshot["files"])
            self.assertTrue(snapshot["markdown"])
            self.assertTrue(snapshot["fake_audits"])
            self.assertEqual(snapshot["git"]["status"]["exit_code"], 0)
            workstream = next(
                note for note in snapshot["markdown"]
                if note["path"] == "docs/workstreams/inventory-application/Inventory Application.md"
            )
            self.assertIn("type", workstream["frontmatter"])
            self.assertTrue(workstream["links"])

    def test_record_requires_every_protocol_field_and_per_oracle_result(self):
        case = next(item for item in CASES if item["id"] == "plan-established-daily-links")
        minimal_snapshot = {"files": [], "markdown": [], "git": {}, "fake_audits": []}
        result = {
            "case_id": case["id"], "prompt": case["prompt"],
            "fixture_context": case["context"], "agent_identifier": "clean-agent-1",
            "model": "test-model", "plugin_metadata": {}, "environment": {},
            "started_at": "2031-04-05T09:00:00Z", "finished_at": "2031-04-05T09:01:00Z",
            "dialogue": [{"speaker": "user", "text": case["prompt"]}],
            "before_snapshot": minimal_snapshot, "after_snapshot": minimal_snapshot,
            "commands": [{"command": ["test"], "stdout": "ok", "stderr": "", "exit_code": 0}],
            "changed_artifacts": [], "external_mutations": [],
            "must_results": [{"oracle": oracle, "result": "pass", "evidence": "observed"} for oracle in case["must"]],
            "must_not_results": [{"oracle": oracle, "result": "pass", "evidence": "not observed"} for oracle in case["must_not"]],
            "score": "pass", "failure_or_evidence_gap": "none",
        }
        self.assertEqual(validate_record(result, case), [])
        result["must_results"].pop()
        self.assertIn("must_results must contain one result per oracle", validate_record(result, case))


if __name__ == "__main__":
    unittest.main()
