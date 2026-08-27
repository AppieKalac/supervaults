import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CASES_PATH = ROOT / "tests/evals/cases.json"

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
    "orient",
    "plan",
    "investigate",
    "design",
    "implement",
    "review",
    "consolidate",
    "deliver",
    "capture",
}
ORACLE_KINDS = {
    "file",
    "link",
    "property",
    "status",
    "validator",
    "test",
    "git",
    "external-mutation",
    "evidence-gap",
}


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

    def test_each_case_has_machine_readable_observable_oracles(self):
        self.assertTrue(self.cases)
        identifiers = set()
        for case in self.cases:
            with self.subTest(case=case.get("id")):
                self.assertIsInstance(case.get("id"), str)
                self.assertNotIn(case["id"], identifiers)
                identifiers.add(case["id"])
                self.assertIn(case.get("context"), CONTEXTS)
                self.assertIn(case.get("mode"), MODES)
                self.assertTrue(case.get("lifecycle", {}).get("allowed"))
                self.assertTrue(case["lifecycle"].get("forbidden"))
                self.assertTrue(case.get("required_artifacts"))
                self.assertTrue(case.get("forbidden_artifacts"))
                self.assertIn("external_write", case.get("authorization", {}))
                self.assertTrue(case.get("must"))
                self.assertTrue(case.get("must_not"))
                for oracle in [*case["must"], *case["must_not"]]:
                    self.assertIn(oracle.get("kind"), ORACLE_KINDS)
                    self.assertIsInstance(oracle.get("assertion"), str)
                    self.assertTrue(oracle["assertion"].strip())
                    self.assertNotIn("reasoning", oracle)

    def test_conflict_boundaries_have_dedicated_cases(self):
        by_id = {case["id"]: case for case in self.cases}
        required = {
            "superpowers-contract-linking",
            "authoritative-workstream-reuse",
            "minor-debugging-stays-session",
            "reusable-root-cause-promotion",
            "read-only-review",
            "consolidation-small-scope",
            "optional-connector-evidence-gap",
            "staging-is-not-production",
        }
        self.assertTrue(required.issubset(by_id))

        contract = by_id["superpowers-contract-linking"]
        self.assertIn("link", {oracle["kind"] for oracle in contract["must"]})
        self.assertIn("file", {oracle["kind"] for oracle in contract["must_not"]})

        reuse = by_id["authoritative-workstream-reuse"]
        self.assertEqual(reuse["lifecycle"]["allowed"], ["extend"])
        self.assertIn("create-new", reuse["lifecycle"]["forbidden"])

        minor = by_id["minor-debugging-stays-session"]
        promoted = by_id["reusable-root-cause-promotion"]
        self.assertIn("investigation", minor["forbidden_artifacts"])
        self.assertIn("investigation", promoted["required_artifacts"])

        review = by_id["read-only-review"]
        self.assertEqual(review["authorization"]["external_write"], "none")
        self.assertIn("git", {oracle["kind"] for oracle in review["must_not"]})

        consolidate = by_id["consolidation-small-scope"]
        self.assertIn("design", consolidate["lifecycle"]["forbidden"])
        self.assertIn("implementation-plan", consolidate["forbidden_artifacts"])

        connector = by_id["optional-connector-evidence-gap"]
        self.assertIn("evidence-gap", {oracle["kind"] for oracle in connector["must"]})

        staging = by_id["staging-is-not-production"]
        self.assertEqual(staging["authorization"]["external_write"], "deployment:staging")
        self.assertIn("external-mutation", {oracle["kind"] for oracle in staging["must_not"]})


if __name__ == "__main__":
    unittest.main()
