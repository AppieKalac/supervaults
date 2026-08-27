import json
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tests.evals.setup_fixture import create_fixture, load_fixture
from tests.evals.scoring import copied_plan_blocks, score_no_copy


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests/evals/cases.json"
FIXTURE_DIR = ROOT / "tests/evals/fixtures"
CASE_OVERLAYS_PATH = FIXTURE_DIR / "case-overlays.json"
TESTING_DOC = ROOT / "docs/testing.md"

REQUIRED_PROMPTS = {
    "Create a small inventory application.",
    "How about barcode scanning?",
    "Let's add exports.",
    "Continue where we stopped.",
    "What happened with authentication?",
    "Plan today.",
    "Consolidate recent work.",
    "Ship it to staging.",
}
CONTEXTS = {"empty-project", "established-multi-session"}
MODES = {
    "orient", "plan", "investigate", "design", "implement", "review", "consolidate", "deliver", "capture",
}
LIFECYCLE_ACTIONS = {
    "resume", "extend", "promote", "implement", "supersede", "merge", "create-new", "reference-only",
}
ORACLE_KINDS = {
    "file", "link", "property", "status", "validator", "test", "git", "external-mutation", "evidence-gap", "response", "no-copy",
}
GATES = {"clarification", "design-approval", "written-spec-approval", "execution-choice", "expected-stop"}
MUTATION_DOMAINS = {"product_source_tree", "vault", "external"}
TOPIC_POLICY_KEYS = {"mode", "max_turns", "on_unmatched", "topics"}
PACKET_POLICY_KEYS = {
    "mode", "max_turns", "on_unmatched", "constraint_packet", "fallback_response",
}
CANONICAL_RECORD_ROOTS = (
    "docs/records/investigations", "docs/records/reviews", "docs/records/releases",
)


def _serialized(value: object) -> str:
    return json.dumps(value, sort_keys=True)


class EvaluationContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))

    def test_required_broad_prompts_cover_empty_and_established_contexts(self):
        prompts = {case["prompt"] for case in self.cases}
        self.assertTrue(REQUIRED_PROMPTS.issubset(prompts))
        for prompt in REQUIRED_PROMPTS:
            with self.subTest(prompt=prompt):
                contexts = {case["context"] for case in self.cases if case["prompt"] == prompt}
                self.assertEqual(contexts, CONTEXTS)

    def test_cases_have_deterministic_fixture_action_gates_and_terminal(self):
        self.assertTrue(self.cases)
        identifiers = set()
        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertIsInstance(case.get("id"), str)
                self.assertNotIn(case["id"], identifiers)
                identifiers.add(case["id"])
                self.assertIn(case.get("context"), CONTEXTS)
                self.assertIn(case.get("mode"), MODES)
                self.assertIn(case.get("expected_lifecycle_action"), LIFECYCLE_ACTIONS)
                self.assertNotIn("lifecycle", case)
                self.assertEqual(case.get("date_mode"), "run-date")
                fixture_name = case.get("fixture")
                self.assertIsInstance(fixture_name, str)
                self.assertTrue((FIXTURE_DIR / f"{fixture_name}.json").is_file())
                self.assertEqual(load_fixture(fixture_name)["context"], case["context"])
                self.assertTrue(case.get("gate_script"))
                for step in case["gate_script"]:
                    self.assertIn(step.get("gate"), GATES)
                    self.assertTrue(step.get("agent_expectation", "").strip())
                    self.assertTrue(step.get("user_response", "").strip())
                self.assertTrue(case.get("terminal_expectation", "").strip())

    def test_empty_project_design_has_deterministic_multi_question_policy(self):
        case = next(case for case in self.cases if case["id"] == "inventory-empty-design")
        policy = case.get("clarification_policy", {})
        self.assertEqual(set(policy), TOPIC_POLICY_KEYS)
        self.assertEqual(policy["mode"], "first-unused-topic-match")
        self.assertGreaterEqual(policy["max_turns"], 6)
        self.assertEqual(policy["on_unmatched"], "stop-inconclusive")
        topics = policy["topics"]
        self.assertEqual(
            {topic["id"] for topic in topics},
            {"form-factor", "persistence", "core-behavior", "scope", "success", "vault"},
        )
        for topic in topics:
            with self.subTest(topic=topic["id"]):
                self.assertTrue(topic["match_any"])
                self.assertTrue(topic["user_response"].strip())
                self.assertNotIn("reasoning", _serialized(topic))
        form = next(topic for topic in topics if topic["id"] == "form-factor")
        self.assertTrue({"form", "browser", "desktop", "command-line"}.issubset(set(form["match_any"])))
        self.assertIn("browser-based web app", form["user_response"])

    def test_barcode_extension_uses_one_complete_packet_and_a_bounded_fallback(self):
        case = next(case for case in self.cases if case["id"] == "barcode-established-extend")
        policy = case.get("clarification_policy", {})
        self.assertEqual(set(policy), PACKET_POLICY_KEYS)
        self.assertEqual(policy["mode"], "constraint-packet-then-fallback")
        self.assertEqual(policy["max_turns"], 2)
        self.assertEqual(policy["on_unmatched"], "use-fallback-then-stop-at-limit")
        clauses = {clause["id"]: clause["user_response"] for clause in policy["constraint_packet"]}
        self.assertEqual(
            set(clauses),
            {
                "known-scan-action", "unknown-scan-assignment", "error-handling",
                "input-modes", "editing-boundary", "manual-controls", "contract-stability",
            },
        )
        self.assertIn("exactly one", clauses["known-scan-action"].lower())
        self.assertIn("existing item", clauses["unknown-scan-assignment"].lower())
        for term in ("duplicate", "invalid", "unmatched"):
            self.assertIn(term, clauses["error-handling"].lower())
        for term in ("browser", "keyboard-wedge", "manual"):
            self.assertIn(term, clauses["input-modes"].lower())
        self.assertIn("never renames", clauses["editing-boundary"].lower())
        self.assertIn("manual stock controls remain", clauses["manual-controls"].lower())
        self.assertIn("otherwise unchanged", clauses["contract-stability"].lower())

        fallback = policy["fallback_response"].lower()
        self.assertIn("existing approved behavior", fallback)
        self.assertIn("simplest browser-local option", fallback)
        self.assertIn("state the assumption", fallback)
        self.assertIn("do not add", fallback)

    def test_barcode_fallback_is_wording_independent_and_cannot_grow_topic_by_topic(self):
        case = next(case for case in self.cases if case["id"] == "barcode-established-extend")
        policy = case["clarification_policy"]
        serialized = _serialized(policy)
        self.assertNotIn("match_any", serialized)
        self.assertNotIn("topics", serialized)
        self.assertLessEqual(policy["max_turns"], 2)

    def test_plan_today_resume_contract_distinguishes_note_creation(self):
        case = next(case for case in self.cases if case["id"] == "plan-established-daily-links")
        self.assertEqual(case["expected_lifecycle_action"], "resume")
        response_oracles = [oracle for oracle in case["must"] if oracle["kind"] == "response"]
        self.assertEqual(len(response_oracles), 1)
        self.assertEqual(response_oracles[0]["assertion"], "announces-resume-not-create-new")

    def test_cases_use_concrete_selectors_and_observable_artifact_coverage(self):
        for case in self.cases:
            with self.subTest(case=case["id"]):
                self.assertIsInstance(case.get("required_artifacts"), list)
                self.assertIsInstance(case.get("forbidden_artifacts"), list)
                self.assertTrue(case.get("must"))
                self.assertTrue(case.get("must_not"))
                must_serialized = {_serialized(oracle) for oracle in case["must"]}
                must_not_serialized = {_serialized(oracle) for oracle in case["must_not"]}
                for artifact in case["required_artifacts"]:
                    self.assertIsInstance(artifact.get("name"), str)
                    self.assertIn(_serialized(artifact.get("selector")), must_serialized)
                for artifact in case["forbidden_artifacts"]:
                    self.assertIsInstance(artifact.get("name"), str)
                    self.assertIn(_serialized(artifact.get("selector")), must_not_serialized)
                for oracle in [*case["must"], *case["must_not"]]:
                    self.assertIn(oracle.get("kind"), ORACLE_KINDS)
                    self.assertIsInstance(oracle.get("assertion"), str)
                    self.assertTrue(oracle["assertion"].strip())
                    self.assertNotIn("reasoning", oracle)
                    self.assertNotIn("2026" + "-08-27", _serialized(oracle))
                self.assertEqual(set(case.get("mutation_domains", {})), MUTATION_DOMAINS)
                self.assertIn(case["mutation_domains"]["product_source_tree"], {"unchanged", "may-change", "not-applicable"})
                self.assertIn(case["mutation_domains"]["vault"], {"unchanged", "evidence-only", "may-change"})
                self.assertIn(case["mutation_domains"]["external"], {"none", "fake-audit:staging"})

    def test_every_case_has_reproducible_machine_defined_preconditions(self):
        overlays = json.loads(CASE_OVERLAYS_PATH.read_text(encoding="utf-8"))
        self.assertEqual(set(overlays), {case["id"] for case in self.cases})
        for case in self.cases:
            overlay = overlays[case["id"]]
            with self.subTest(case=case["id"]):
                self.assertEqual(overlay["fixture"], case["fixture"])
                self.assertTrue(overlay["description"].strip())
                self.assertTrue(overlay["actions"])
                for action in overlay["actions"]:
                    self.assertIn(action["kind"], {"assert-path", "write-file", "replace-text"})

    def test_documented_protocol_creates_child_before_baseline_capture(self):
        text = TESTING_DOC.read_text(encoding="utf-8")
        allocate = text.index("Allocate an empty disposable parent directory")
        create = text.index("Run the helper into a nonexistent child directory")
        baseline = text.index("Capture the baseline of the created deterministic fixture")
        dispatch = text.index("Give the clean agent exactly the prompt")
        self.assertLess(allocate, create)
        self.assertLess(create, baseline)
        self.assertLess(baseline, dispatch)

    def test_canonical_records_and_strong_plan_copy_protection(self):
        corpus = _serialized(self.cases)
        for legacy_directory in ("investigations", "reviews", "releases"):
            self.assertNotIn(f"docs/{legacy_directory}", corpus)
        for root in CANONICAL_RECORD_ROOTS:
            self.assertIn(root, corpus)

        contract = next(case for case in self.cases if case["id"] == "superpowers-contract-linking")
        canonical = "docs/superpowers/plans/{{RUN_DATE}}-inventory-application.md"
        self.assertIn(canonical, _serialized(contract["must"]))
        protections = [oracle for oracle in contract["must_not"] if oracle["kind"] == "no-copy"]
        self.assertEqual(len(protections), 1)
        protection = protections[0]
        self.assertEqual(protection["canonical_path"], canonical)
        self.assertEqual(protection["forbidden_paths"], ["docs/workstreams", "docs/daily"])
        self.assertEqual(protection["scorer"], "normalized-task-blocks-v1")

        review = next(case for case in self.cases if case["id"] == "read-only-review")
        self.assertEqual(review["mutation_domains"], {"product_source_tree": "unchanged", "vault": "unchanged", "external": "none"})
        self.assertIn("response", {oracle["kind"] for oracle in review["must"]})
        self.assertIn("docs/**", {oracle.get("path") for oracle in review["must_not"]})

    def test_fixture_setup_is_reproducible_and_renders_run_date(self):
        run_date = date(2031, 4, 5)
        with tempfile.TemporaryDirectory() as directory:
            first = Path(directory) / "first"
            second = Path(directory) / "second"
            create_fixture("established-multi-session", first, run_date)
            create_fixture("established-multi-session", second, run_date)
            expected = first / "docs/workstreams/inventory-application/sessions/2031-04-05-0900-baseline.md"
            self.assertTrue(expected.is_file())
            self.assertIn("2031-04-05", expected.read_text(encoding="utf-8"))
            self.assertTrue((first / "docs/records/investigations").is_dir())
            self.assertTrue((first / "src/inventory.py").is_file())
            for path in (first, second):
                self.assertEqual(
                    subprocess.run(["git", "log", "--format=%s"], cwd=path, capture_output=True, text=True, check=True).stdout.splitlines(),
                    ["fixture: inventory history", "fixture: project baseline"],
                )
            self.assertEqual(
                subprocess.run(["git", "rev-parse", "HEAD"], cwd=first, capture_output=True, text=True, check=True).stdout,
                subprocess.run(["git", "rev-parse", "HEAD"], cwd=second, capture_output=True, text=True, check=True).stdout,
            )

    def test_case_overlay_creates_stated_stale_and_safe_fake_prerequisites(self):
        with tempfile.TemporaryDirectory() as directory:
            stale = Path(directory) / "stale"
            small_scope = Path(directory) / "small-scope"
            recurring = Path(directory) / "recurring"
            staging = Path(directory) / "staging"
            create_fixture("established-multi-session", stale, date(2031, 4, 5), "consolidate-established-small-corrections")
            create_fixture("established-multi-session", small_scope, date(2031, 4, 5), "consolidation-small-scope")
            create_fixture("established-multi-session", recurring, date(2031, 4, 5), "reusable-root-cause-promotion")
            create_fixture("established-multi-session", staging, date(2031, 4, 5), "staging-is-not-production")
            self.assertIn("[[stale-baseline]]", (stale / "docs/workstreams/inventory-application/Inventory Application.md").read_text(encoding="utf-8"))
            self.assertIn("[[stale-baseline]]", (small_scope / "docs/workstreams/inventory-application/Inventory Application.md").read_text(encoding="utf-8"))
            self.assertIn("malformed EAN prefix", (recurring / "docs/workstreams/scanner-a/Scanner A.md").read_text(encoding="utf-8"))
            audit = json.loads((staging / "audits/staging-deployment.json").read_text(encoding="utf-8"))
            self.assertEqual(audit["endpoint"], "local-fake://staging")
            self.assertEqual(audit["events"], [])

    def test_normalized_plan_copy_scorer_rejects_evasive_heading_and_path_variants(self):
        canonical = "## Task 1: Add barcode parsing\nFiles: src/barcode.py\nRun the parser tests.\n"
        copied = "### Task 1: Add barcode parsing\nFiles: src/alternate.py\nRun the parser tests.\n"
        self.assertTrue(copied_plan_blocks(canonical, copied))
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            plan = root / "docs/superpowers/plans/plan.md"
            copied_note = root / "docs/workstreams/scanner/Scanner.md"
            linked_note = root / "docs/daily/today.md"
            plan.parent.mkdir(parents=True)
            copied_note.parent.mkdir(parents=True)
            linked_note.parent.mkdir(parents=True)
            plan.write_text(canonical, encoding="utf-8")
            copied_note.write_text(copied, encoding="utf-8")
            linked_note.write_text("See [[plan]].\n", encoding="utf-8")
            findings = score_no_copy(plan, [root / "docs/workstreams", root / "docs/daily"])
            self.assertEqual([path for path, _ in findings], [copied_note])

    def test_empty_fixture_has_only_deterministic_repository_baseline(self):
        with tempfile.TemporaryDirectory() as directory:
            destination = Path(directory) / "empty"
            create_fixture("empty-project", destination, date(2031, 4, 5))
            self.assertTrue((destination / ".git").is_dir())
            self.assertFalse((destination / "docs").exists())
            self.assertEqual(
                subprocess.run(["git", "log", "--format=%s"], cwd=destination, capture_output=True, text=True, check=True).stdout.splitlines(),
                ["fixture: empty baseline"],
            )


if __name__ == "__main__":
    unittest.main()
