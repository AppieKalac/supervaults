import json
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tests.evals.evidence import capture_snapshot, scan_user_visible_branding, validate_record
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
            "transcript_branding_scan": {"result": "pass", "hits": []},
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

    def test_branding_scan_checks_every_agent_update_and_final(self):
        clean = [
            {"speaker": "agent", "text": "`Using Supervaults' design` to inspect the contract."},
            {"speaker": "user", "text": "Does Superpowers run internally?"},
            {"speaker": "agent", "text": "The design is documented at docs/superpowers/specs/example.md."},
        ]
        self.assertEqual(scan_user_visible_branding(clean), [])
        branded = [
            *clean,
            {"speaker": "agent", "text": "I am also applying the required Superpowers workflow."},
            {"speaker": "agent", "text": "Next use superpowers:writing-plans."},
            {"speaker": "agent", "text": "The vendored method now takes over."},
        ]
        hits = scan_user_visible_branding(branded)
        self.assertEqual([hit["exchange_index"] for hit in hits], [3, 4, 5])

    def test_record_verifier_rejects_false_clean_branding_claim(self):
        case = next(item for item in CASES if item["id"] == "plan-established-daily-links")
        snapshot = {"files": [], "markdown": [], "git": {}, "fake_audits": []}
        dialogue = [
            {"speaker": "user", "text": case["prompt"]},
            {"speaker": "agent", "text": "Using the Superpowers planning workflow."},
        ]
        record = {
            "case_id": case["id"], "prompt": case["prompt"], "fixture_context": case["context"],
            "agent_identifier": "agent", "model": "model", "plugin_metadata": {}, "environment": {},
            "started_at": "2031-04-05T09:00:00Z", "finished_at": "2031-04-05T09:01:00Z",
            "dialogue": dialogue, "transcript_branding_scan": {"result": "pass", "hits": []},
            "before_snapshot": snapshot, "after_snapshot": snapshot, "commands": [],
            "changed_artifacts": [], "external_mutations": [],
            "must_results": [{"oracle": oracle, "result": "pass", "evidence": "observed"} for oracle in case["must"]],
            "must_not_results": [{"oracle": oracle, "result": "pass", "evidence": "absent"} for oracle in case["must_not"]],
            "score": "pass", "failure_or_evidence_gap": "none",
        }
        errors = validate_record(record, case)
        self.assertIn("transcript_branding_scan does not match complete agent dialogue", errors)


if __name__ == "__main__":
    unittest.main()
