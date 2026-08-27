import json
import subprocess
import tempfile
import unittest
from datetime import date
from pathlib import Path

from tests.evals.setup_fixture import create_fixture, load_fixture


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests/evals/cases.json"
FIXTURE_DIR = ROOT / "tests/evals/fixtures"

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
                self.assertIn(case["mutation_domains"]["external"], {"none", "deployment:staging"})

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
        self.assertIn("## Task", protection["forbidden_headings"])
        self.assertTrue(protection["forbidden_phrases"])

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
