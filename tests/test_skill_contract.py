import json
import re
import unittest
from pathlib import Path

from skills.supervaults.scripts.supervaults.lifecycle import (
    _has_valid_actual_blast_radius,
    _has_valid_handoff,
    _has_valid_verification_evidence,
    _section_content,
)
from skills.supervaults.scripts.supervaults.vault import render_template


ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/supervaults/SKILL.md"
MODES = ROOT / "skills/supervaults/references/operating-modes.md"
PLANNING = ROOT / "skills/supervaults/references/planning.md"
QUALITY = ROOT / "skills/supervaults/references/quality-gates.md"
ROUTING = ROOT / "skills/supervaults/references/lifecycle-routing.md"
SESSION_TEMPLATE = ROOT / "skills/supervaults/templates/vault/session.md.tmpl"
MANIFEST = ROOT / ".codex-plugin/plugin.json"


def section(text: str, heading: str) -> str:
    match = re.search(rf"^## {re.escape(heading)}\s*$", text, re.MULTILINE)
    if match is None:
        return ""
    following = re.search(r"^## ", text[match.end():], re.MULTILINE)
    end = match.end() + following.start() if following else len(text)
    return text[match.end():end]


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_has_broad_trigger_and_exclusions(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?s)^---\nname: supervaults\ndescription: .+\n---")
        description = text.split("---", 2)[1]
        for phrase in ("plan", "investigate", "implement", "review", "consolidate", "project vault"):
            self.assertIn(phrase, description.lower())
        self.assertIn("new software project where no vault exists yet", description.lower())

    def test_required_modes_and_gates_are_present(self):
        text = SKILL.read_text(encoding="utf-8").lower()
        for token in ("orient", "plan", "investigate", "design", "implement", "review", "consolidate", "deliver", "capture"):
            self.assertIn(token, text)
        for token in ("preinspect", "expected blast radius", "actual blast radius", "handoff", "validate"):
            self.assertIn(token, text)

    def test_every_markdown_reference_resolves(self):
        text = SKILL.read_text(encoding="utf-8")
        for target in re.findall(r"\[[^]]+\]\(([^)]+\.md)\)", text):
            self.assertTrue((SKILL.parent / target).resolve().exists(), target)

    def test_internal_methods_adapt_transport_without_exposing_vendor_skills(self):
        text = MODES.read_text(encoding="utf-8")
        adaptation = section(text, "Internal method adaptation")
        self.assertIn("Using Supervaults' <phase>", adaptation)
        self.assertIn("superpowers:<skill>", adaptation)
        self.assertIn("plugin-relative", adaptation)
        self.assertIn("never resolve it from the target repository", adaptation)
        self.assertIn("never tell the user to invoke", adaptation.lower())
        self.assertIn("approval", adaptation.lower())
        self.assertIn("review", adaptation.lower())
        self.assertIn("Never describe a bundled phase as a Superpowers", adaptation)

    def test_user_visible_phase_branding_is_always_supervaults(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertIn("Using Supervaults' <phase>", text)
        self.assertIn("first user-visible workflow update", text)
        self.assertIn("do not name Superpowers", text)
        self.assertIn("literal ASCII prefix", text)
        self.assertIn("Start the first user-visible workflow update with an inline-code span", text)
        self.assertIn("every user-visible update and final", text)
        self.assertIn("Never write `Superpowers`", text)
        self.assertIn("vendor skill ID", text)

    def test_daily_note_mechanics_do_not_change_resume_lifecycle_action(self):
        text = PLANNING.read_text(encoding="utf-8")
        plan_today = section(text, "Plan today")
        self.assertIn("lifecycle action is `resume`", plan_today)
        self.assertIn("artifact mechanics", plan_today)
        self.assertIn("not `create-new`", plan_today)

    def test_installed_skill_anchors_plugin_paths_and_absorbs_external_phase_handoffs(self):
        text = SKILL.read_text(encoding="utf-8")
        description = text.split("---", 2)[1].lower()
        self.assertIn("before separately installed vendor methods", description)
        self.assertIn("two directory levels above this `SKILL.md`", text)
        self.assertIn("do not run that separate phase", text)
        self.assertIn("working directory set to `<supervaults-root>`", text)

        references = ROOT / "skills/supervaults/references"
        corpus = "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(references.glob("*.md"))
        )
        self.assertNotRegex(corpus, r"(?<!\.\./\.\./)vendor/(?:superpowers|obsidian-skills)/")

    def test_empty_project_vault_requires_an_approved_resolved_destination(self):
        routing = ROUTING.read_text(encoding="utf-8").lower()
        self.assertIn("propose `docs/`", routing)
        self.assertIn("approved destination", routing)
        self.assertIn("before initialization", routing)

    def test_new_artifact_names_preserve_the_users_outcome_phrase(self):
        routing = ROUTING.read_text(encoding="utf-8")
        self.assertIn("preserve the user's outcome noun phrase", routing)
        self.assertIn("Inventory Application", routing)
        self.assertIn("inventory-application", routing)
        self.assertIn("Do not abbreviate", routing)

    def test_resolved_vault_overrides_vendor_contract_locations(self):
        text = PLANNING.read_text(encoding="utf-8")
        self.assertIn("<resolved-vault>/superpowers/specs/YYYY-MM-DD-<topic>-design.md", text)
        self.assertIn("<resolved-vault>/superpowers/plans/YYYY-MM-DD-<feature>.md", text)
        self.assertRegex(text.lower(), r"location override.+takes precedence.+vendored.+docs/")
        self.assertIn("competing", text.lower())

    def test_plain_review_is_read_only_and_fixing_requires_implement(self):
        text = MODES.read_text(encoding="utf-8")
        review = section(text, "Review")
        self.assertIn("read-only", review.lower())
        self.assertIn("stop after findings and dispositions", review.lower())
        self.assertIn("do not apply fixes, commit, merge", review.lower())
        self.assertIn("separate Implement lifecycle action", review)
        self.assertLess(review.index("requesting-code-review/SKILL.md"), review.lower().index("stop after findings"))

    def test_each_mode_orders_prerequisites_before_method_and_return(self):
        text = MODES.read_text(encoding="utf-8")
        self.assertIn("No vendored method may be invoked before", text)
        for mode in ("Orient", "Plan", "Investigate", "Design", "Implement", "Review", "Consolidate", "Deliver", "Capture"):
            mode_text = section(text, mode)
            with self.subTest(mode=mode):
                self.assertTrue(mode_text, mode)
                prerequisite = mode_text.index("1. **Prerequisites:**")
                method = mode_text.index("2. **Internal method:**")
                lifecycle_return = mode_text.index("3. **Supervaults return:**")
                self.assertLess(prerequisite, method)
                self.assertLess(method, lifecycle_return)

    def test_evidence_grammar_is_explicit_and_template_prompts_cannot_close(self):
        quality = QUALITY.read_text(encoding="utf-8")
        template = SESSION_TEMPLATE.read_text(encoding="utf-8")
        results = (
            "passed — <substantive detail>",
            "failed — <substantive detail>",
            "not-run — <reason>",
            "manual-check — <substantive observation>",
        )
        for result in results:
            self.assertIn(result, quality)
            self.assertIn(result, template)
        for field in ("Surface: <canonical impact surface>", "State: <changed | unchanged | not-applicable | unknown | not-checked>", "Detail: <substantive detail>", "Current state: <substantive current state>", "Next action: <exact next action>"):
            self.assertIn(field, template)
        self.assertIn("Blank or placeholder fields cannot pass closure", quality)

        for result in (
            "passed — 46 tests passed",
            "failed — one regression remains",
            "not-run — CI access unavailable",
            "manual-check — rendered correctly in Obsidian",
        ):
            self.assertTrue(_has_valid_verification_evidence(f"Check: focused verification\nResult: {result}"))

        rendered = render_template(
            SESSION_TEMPLATE,
            {"WORKSTREAM_NAME": "Example", "DATE": "2026-08-27", "SESSION_OUTCOME": "verify contract"},
        )
        self.assertFalse(_has_valid_actual_blast_radius(_section_content(rendered, "Actual blast radius")))
        self.assertFalse(_has_valid_verification_evidence(_section_content(rendered, "Verification evidence")))
        self.assertFalse(_has_valid_handoff(_section_content(rendered, "Handoff")))

    def test_all_vendor_routes_and_single_registered_skill_remain_intact(self):
        references = (ROOT / "skills/supervaults/references")
        corpus = SKILL.read_text(encoding="utf-8") + "\n" + "\n".join(
            path.read_text(encoding="utf-8") for path in sorted(references.glob("*.md"))
        )
        superpowers = (
            "brainstorming", "dispatching-parallel-agents", "executing-plans",
            "finishing-a-development-branch", "receiving-code-review",
            "requesting-code-review", "subagent-driven-development",
            "systematic-debugging", "test-driven-development", "using-git-worktrees",
            "using-superpowers", "verification-before-completion", "writing-plans",
        )
        obsidian = ("json-canvas", "obsidian-bases", "obsidian-cli", "obsidian-markdown")
        for name in superpowers:
            self.assertIn(f"../../vendor/superpowers/skills/{name}/SKILL.md", corpus)
        for name in obsidian:
            self.assertIn(f"../../vendor/obsidian-skills/skills/{name}/SKILL.md", corpus)
        manifest = json.loads(MANIFEST.read_text(encoding="utf-8"))
        registered = [path.name for path in (ROOT / manifest["skills"]).iterdir() if path.is_dir()]
        self.assertEqual(registered, ["supervaults"])


if __name__ == "__main__":
    unittest.main()
