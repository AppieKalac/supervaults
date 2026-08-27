# Supervaults Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Build and install one `$supervaults` Codex plugin that combines pinned, unchanged Superpowers and Obsidian methods with a workstream-centered, multi-session development-memory workflow.

**Architecture:** The plugin exposes one orchestration skill and keeps selected upstream modules under `vendor/`, outside the registered skill directory. A Python 3 standard-library toolkit initializes and validates repository-local Markdown vaults, discovers lifecycle context, and opens or closes bounded work sessions; the skill's focused references and templates define planning, routing, delivery, and consolidation behavior.

**Tech Stack:** Codex plugin manifest, Markdown skills, YAML frontmatter, Obsidian Bases/Canvas, Python 3 standard library, `unittest`, Git.

**Spec:** `docs/superpowers/specs/2026-08-27-supervaults-design.md`

## Global Constraints

- `$supervaults` is the plugin's only user-visible skill.
- Vendor exactly the 13 Superpowers and 4 Obsidian modules named in the specification; keep imported files byte-for-byte unchanged.
- Pin upstream repository commits and SHA-256 hashes in `upstream-lock.json`.
- The core workflow must work without a running Obsidian application or optional external connector.
- Use Python 3 standard library only for core automation.
- Organize initialized vaults around `Home.md`, daily plans, and workstream directories; artifact-type libraries are secondary promoted records.
- Keep specifications and plans prospective, sessions evidentiary, workstreams current, and `Home.md` project-level.
- Scale expected and actual blast-radius recording to risk.
- Keep implemented, verified, reviewed, merged, released, deployed, and observed states distinct.
- Never retain secrets, credentials, raw log dumps, or private reasoning.
- Never mutate an external system without authorization for the named action and scope.
- Preserve unrelated worktree changes and commit only task-owned files.

---

### Task 1: Plugin shell and manifest contract

**Files:**
- Create: `.codex-plugin/plugin.json`
- Create: `skills/supervaults/agents/openai.yaml`
- Create: `README.md`
- Create: `LICENSE`
- Create: `tests/test_plugin_structure.py`

**Interfaces:**
- Produces: a Codex plugin named `supervaults` whose registered skills root is `./skills/`.
- Produces: one discoverable skill directory, `skills/supervaults/`.
- Consumes: no earlier task output.

- [ ] **Step 1: Read the plugin-creator and skill-creator instructions**

Read both installed `SKILL.md` files completely before creating plugin files. Follow their manifest requirements when they are stricter than this plan; preserve the design requirement that only `$supervaults` is registered.

- [ ] **Step 2: Write the failing plugin-structure test**

```python
# tests/test_plugin_structure.py
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class PluginStructureTests(unittest.TestCase):
    def test_manifest_registers_exactly_one_skills_root(self):
        manifest = json.loads(
            (ROOT / ".codex-plugin" / "plugin.json").read_text(encoding="utf-8")
        )
        self.assertEqual(manifest["name"], "supervaults")
        self.assertEqual(manifest["version"], "0.1.0")
        self.assertEqual(manifest["skills"], "./skills/")

    def test_only_supervaults_is_registered(self):
        skills = sorted(
            path.name for path in (ROOT / "skills").iterdir() if path.is_dir()
        )
        self.assertEqual(skills, ["supervaults"])

    def test_skill_metadata_exists(self):
        self.assertTrue((ROOT / "skills/supervaults/SKILL.md").exists())
        self.assertTrue((ROOT / "skills/supervaults/agents/openai.yaml").exists())


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the test and verify it fails**

Run: `python -m unittest tests.test_plugin_structure -v`

Expected: FAIL because the plugin manifest and skill files do not exist.

- [ ] **Step 4: Create the minimal plugin shell**

Create `.codex-plugin/plugin.json` with this contract, adding only fields required by the current plugin-creator instructions:

```json
{
  "name": "supervaults",
  "version": "0.1.0",
  "description": "Workstream-centered development memory powered by Superpowers and Obsidian.",
  "skills": "./skills/",
  "license": "MIT",
  "interface": {
    "displayName": "Supervaults",
    "shortDescription": "Plan, build, and preserve project context",
    "category": "Developer Tools",
    "capabilities": ["Interactive", "Read", "Write"]
  }
}
```

Create the discoverability metadata:

```yaml
# skills/supervaults/agents/openai.yaml
interface:
  display_name: "Supervaults"
  short_description: "Run development through linked, multi-session project vaults"
```

Create a valid `skills/supervaults/SKILL.md` with `name: supervaults`, the complete trigger boundary in one description, and an executable top-level protocol covering vault resolution, preinspection, lifecycle routing, evidence, reconciliation, and validation. Task 7 factors the detailed mode rules into focused references without changing this top-level contract.

Create `README.md` with the purpose, current construction status, design/spec links, upstream attribution summary, and the intended `$supervaults` examples. Add the standard MIT license text with copyright `2026 Appie Kalac`.

- [ ] **Step 5: Run the structure test**

Run: `python -m unittest tests.test_plugin_structure -v`

Expected: 3 tests PASS.

- [ ] **Step 6: Commit the plugin shell**

```bash
git add .codex-plugin/plugin.json skills/supervaults/agents/openai.yaml skills/supervaults/SKILL.md README.md LICENSE tests/test_plugin_structure.py
git commit -m "feat: scaffold Supervaults plugin"
```

---

### Task 2: Reproducible upstream import and integrity lock

**Files:**
- Create: `upstream-selection.json`
- Create: `scripts/sync_upstreams.py`
- Create: `upstream-lock.json`
- Create: `THIRD_PARTY_NOTICES.md`
- Create: `vendor/superpowers/skills/<selected modules>/**`
- Create: `vendor/obsidian-skills/skills/<selected modules>/**`
- Create: `tests/test_upstream_integrity.py`

**Interfaces:**
- Produces: `sync_upstreams.sync(selection_path: Path, root: Path, update: bool) -> dict`.
- Produces: `sync_upstreams.verify(root: Path, lock: dict) -> list[str]`, returning human-readable integrity errors.
- Produces: `upstream-lock.json` with `repository`, `commit`, `paths`, and per-file SHA-256 hashes.
- Consumes: plugin repository root from Task 1.

- [ ] **Step 1: Define the immutable selection manifest**

Create `upstream-selection.json` with repository URLs and these exact paths:

```json
{
  "superpowers": {
    "repository": "https://github.com/obra/superpowers.git",
    "paths": [
      "skills/brainstorming",
      "skills/dispatching-parallel-agents",
      "skills/executing-plans",
      "skills/finishing-a-development-branch",
      "skills/receiving-code-review",
      "skills/requesting-code-review",
      "skills/subagent-driven-development",
      "skills/systematic-debugging",
      "skills/test-driven-development",
      "skills/using-git-worktrees",
      "skills/using-superpowers",
      "skills/verification-before-completion",
      "skills/writing-plans"
    ]
  },
  "obsidian-skills": {
    "repository": "https://github.com/kepano/obsidian-skills.git",
    "paths": [
      "skills/json-canvas",
      "skills/obsidian-bases",
      "skills/obsidian-cli",
      "skills/obsidian-markdown"
    ]
  }
}
```

- [ ] **Step 2: Write failing integrity tests**

```python
# tests/test_upstream_integrity.py
import json
import unittest
from pathlib import Path

from scripts.sync_upstreams import verify

ROOT = Path(__file__).resolve().parents[1]


class UpstreamIntegrityTests(unittest.TestCase):
    def test_lock_matches_vendor_tree(self):
        lock = json.loads((ROOT / "upstream-lock.json").read_text(encoding="utf-8"))
        self.assertEqual(verify(ROOT, lock), [])

    def test_vendor_is_not_registered_as_plugin_skills(self):
        registered = {path.name for path in (ROOT / "skills").iterdir() if path.is_dir()}
        self.assertEqual(registered, {"supervaults"})

    def test_lock_contains_exact_selected_paths(self):
        selection = json.loads((ROOT / "upstream-selection.json").read_text())
        lock = json.loads((ROOT / "upstream-lock.json").read_text())
        for name, source in selection.items():
            self.assertEqual(lock["sources"][name]["paths"], source["paths"])
            self.assertRegex(lock["sources"][name]["commit"], r"^[0-9a-f]{40}$")


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the integrity tests and verify they fail**

Run: `python -m unittest tests.test_upstream_integrity -v`

Expected: FAIL because the sync module, lock, and vendor tree do not exist.

- [ ] **Step 4: Implement deterministic sync and verification**

Implement public functions with these exact signatures: `sha256_file(path: Path) -> str`, `list_files(path: Path) -> list[Path]`, `verify(root: Path, lock: dict) -> list[str]`, `sync(selection_path: Path, root: Path, update: bool) -> dict`, and `main(argv: list[str] | None = None) -> int`.

`sync` must clone each repository into a `tempfile.TemporaryDirectory`, resolve `HEAD` with `git rev-parse HEAD`, copy only selected paths to `vendor/<source>/`, generate sorted forward-slash relative paths and hashes, and write the lock atomically. Without `--update`, refuse to replace an existing lock or vendor tree. With `--verify`, perform no network or filesystem mutation.

The command surface is:

```text
python scripts/sync_upstreams.py --initialize
python scripts/sync_upstreams.py --update
python scripts/sync_upstreams.py --verify
```

Return `0` on success and `1` for integrity errors. Print the old/new commit and changed-file summary before accepting `--update` output.

- [ ] **Step 5: Initialize the vendor tree and notices**

Run: `python scripts/sync_upstreams.py --initialize`

Create `THIRD_PARTY_NOTICES.md` naming both projects, their repository URLs, pinned commits from the generated lock, imported paths, copyright notices from their licenses, and full MIT license text. Do not claim that Supervaults is endorsed by either upstream maintainer.

- [ ] **Step 6: Verify byte integrity and tests**

Run:

```text
python scripts/sync_upstreams.py --verify
python -m unittest tests.test_upstream_integrity -v
```

Expected: integrity verification succeeds and all 3 tests PASS.

- [ ] **Step 7: Commit the upstream bundle**

```bash
git add upstream-selection.json upstream-lock.json THIRD_PARTY_NOTICES.md scripts/sync_upstreams.py vendor tests/test_upstream_integrity.py
git commit -m "build: vendor pinned workflow dependencies"
```

---

### Task 3: Markdown schema and vault model

**Files:**
- Create: `skills/supervaults/scripts/supervaults/__init__.py`
- Create: `skills/supervaults/scripts/supervaults/schema.py`
- Create: `skills/supervaults/scripts/supervaults/markdown.py`
- Create: `tests/test_markdown_schema.py`

**Interfaces:**
- Produces: schema constants `TYPE_STATUSES`, `WORKSTREAM_STAGES`, `RELATIONSHIP_FIELDS`, and `IMPACT_SURFACES`.
- Produces: `parse_note(path: Path) -> Note` and `write_note(note: Note) -> None`.
- Produces: immutable `Note(path: Path, properties: dict[str, object], body: str)`.
- Consumes: only Python 3 standard library.

- [ ] **Step 1: Write schema and round-trip tests**

```python
# tests/test_markdown_schema.py
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
            original = Note(path, {
                "type": "work-session",
                "status": "active",
                "project": "[[Home]]",
                "components": ["api", "web"],
            }, "# Session\n\nEvidence.\n")
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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `python -m unittest tests.test_markdown_schema -v`

Expected: FAIL because the package and model do not exist.

- [ ] **Step 3: Implement the schema constants**

Copy the exact artifact types, status vocabularies, workstream stages, relationship fields, and impact surfaces from the approved spec into immutable Python sets and tuples. Do not create additional artifact categories.

- [ ] **Step 4: Implement the constrained frontmatter reader/writer**

Support the subset emitted by Supervaults: strings, integers, booleans, ISO date strings, and indented lists of scalar values. Reject nested mappings and malformed frontmatter with `ValueError` naming the file and property. Serialize keys in this order when present: `type`, `stage`, `status`, `project`, `workstream`, `spec`, `plan`, `date`, relationship fields, context fields, and timestamps; append unknown keys in lexical order so user metadata is preserved.

Use atomic writes through a sibling temporary file and `Path.replace`. Never rewrite the body when only properties change except for newline normalization to UTF-8 LF.

- [ ] **Step 5: Run the schema tests**

Run: `python -m unittest tests.test_markdown_schema -v`

Expected: all 3 tests PASS.

- [ ] **Step 6: Commit the model**

```bash
git add skills/supervaults/scripts/supervaults tests/test_markdown_schema.py
git commit -m "feat: add vault markdown model"
```

---

### Task 4: Workstream-centered vault initialization and native views

**Files:**
- Create: `skills/supervaults/templates/vault/Home.md.tmpl`
- Create: `skills/supervaults/templates/vault/daily.md.tmpl`
- Create: `skills/supervaults/templates/vault/workstream.md.tmpl`
- Create: `skills/supervaults/templates/vault/session.md.tmpl`
- Create: `skills/supervaults/templates/vault/decision.md.tmpl`
- Create: `skills/supervaults/templates/vault/investigation.md.tmpl`
- Create: `skills/supervaults/templates/vault/review.md.tmpl`
- Create: `skills/supervaults/templates/vault/knowledge.md.tmpl`
- Create: `skills/supervaults/templates/vault/release.md.tmpl`
- Create: `skills/supervaults/templates/vault/views/Development Lifecycle.base`
- Create: `skills/supervaults/templates/vault/views/Delivery Gaps.base`
- Create: `skills/supervaults/templates/vault/views/Daily Planning.base`
- Create: `skills/supervaults/scripts/supervaults/vault.py`
- Create: `tests/test_vault_initialization.py`

**Interfaces:**
- Produces: `initialize_vault(vault: Path, project_name: str, today: date) -> list[Path]`.
- Produces: `render_template(template: Path, values: dict[str, str]) -> str`.
- Consumes: `Note`, `parse_note`, and `write_note` from Task 3.

- [ ] **Step 1: Write a failing initialization test**

```python
# tests/test_vault_initialization.py
import tempfile
import unittest
from datetime import date
from pathlib import Path

from skills.supervaults.scripts.supervaults.markdown import parse_note
from skills.supervaults.scripts.supervaults.vault import initialize_vault


class VaultInitializationTests(unittest.TestCase):
    def test_initializes_work_centered_structure_idempotently(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            created = initialize_vault(vault, "Inventory", date(2026, 8, 27))
            self.assertTrue((vault / "Home.md").exists())
            for relative in (
                "daily", "workstreams", "workstreams/archive",
                "superpowers/specs", "superpowers/plans",
                "records/decisions", "records/investigations",
                "records/reviews", "records/incidents", "records/releases",
                "knowledge", "inbox", "views", "templates",
            ):
                self.assertTrue((vault / relative).is_dir(), relative)
            self.assertEqual(parse_note(vault / "Home.md").properties["type"], "project")
            self.assertGreater(len(created), 0)
            self.assertEqual(initialize_vault(vault, "Inventory", date(2026, 8, 27)), [])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `python -m unittest tests.test_vault_initialization -v`

Expected: FAIL because initialization and templates do not exist.

- [ ] **Step 3: Create minimal, role-specific templates**

Each template must contain only useful sections for its role. In particular:

```markdown
# Workstream — {{WORKSTREAM_NAME}}

## Outcome
## Current state
## Completed
## Remaining
## Current blockers
## Latest verification
## Delivery state
## Next action
## Sessions
```

```markdown
# Work Session — {{SESSION_OUTCOME}}

## Goal
## Starting state
## Lifecycle checkpoint
## Expected blast radius
## Work performed
## Decisions and deviations
## Actual blast radius
## Verification evidence
## Blockers and assumptions
## Handoff
```

The daily template must use the approved sections: intent, primary outcome and finish conditions, optional secondary outcome, small work, constraints, not today, sessions, interruptions and replanning, and end-of-day reconciliation.

- [ ] **Step 4: Create valid native Obsidian Bases**

Use the vendored `obsidian-bases` instructions. `Development Lifecycle.base` groups active workstreams by `stage`; `Delivery Gaps.base` filters incomplete workstreams at verification or later and groups by stage; `Daily Planning.base` shows open daily plans and selected workstreams. Filters must derive from source properties and must not create graph-only links.

- [ ] **Step 5: Implement idempotent initialization**

`initialize_vault` creates missing directories and files but never overwrites an existing note or view. It returns only newly created paths, sorted relative to the vault. Render `{{PROJECT_NAME}}` and `{{DATE}}`; reject any unresolved double-brace template marker before writing.

- [ ] **Step 6: Run initialization and full unit tests**

Run:

```text
python -m unittest tests.test_vault_initialization -v
python -m unittest discover -s tests -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit initialization**

```bash
git add skills/supervaults/templates skills/supervaults/scripts/supervaults/vault.py tests/test_vault_initialization.py
git commit -m "feat: initialize workstream-centered vaults"
```

---

### Task 5: Context discovery, planning, and session transitions

**Files:**
- Create: `skills/supervaults/scripts/supervaults/context.py`
- Create: `skills/supervaults/scripts/supervaults/lifecycle.py`
- Create: `skills/supervaults/scripts/supervaults/cli.py`
- Create: `skills/supervaults/scripts/supervaults/__main__.py`
- Create: `tests/test_lifecycle.py`

**Interfaces:**
- Produces: `find_context(vault: Path, terms: list[str]) -> ContextReport`.
- Produces: `open_daily_plan(vault: Path, day: date) -> Path`.
- Produces: `open_session(vault: Path, workstream: Path, outcome: str, now: datetime, owner: str) -> Path`.
- Produces: `close_session(vault: Path, session: Path, end_commit: str | None) -> None`.
- Produces CLI subcommands `init`, `context`, `plan-today`, `open-session`, `close-session`, and later `validate`.
- Consumes: Markdown model and vault templates from Tasks 3–4.

- [ ] **Step 1: Write failing lifecycle tests**

```python
# tests/test_lifecycle.py
import tempfile
import unittest
from datetime import date, datetime
from pathlib import Path

from skills.supervaults.scripts.supervaults.lifecycle import open_daily_plan, open_session
from skills.supervaults.scripts.supervaults.markdown import parse_note
from skills.supervaults.scripts.supervaults.vault import initialize_vault


class LifecycleTests(unittest.TestCase):
    def test_daily_plan_is_retained_and_linked_to_previous_day(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 26))
            first = open_daily_plan(vault, date(2026, 8, 26))
            second = open_daily_plan(vault, date(2026, 8, 27))
            self.assertEqual(parse_note(second).properties["previous_day"], f"[[{first.stem}]]")

    def test_new_owner_gets_unique_session_with_workstream_link(self):
        with tempfile.TemporaryDirectory() as directory:
            vault = Path(directory) / "docs"
            initialize_vault(vault, "Inventory", date(2026, 8, 27))
            workstream_dir = vault / "workstreams/barcode-scanning"
            workstream_dir.mkdir()
            workstream = workstream_dir / "Barcode Scanning.md"
            workstream.write_text("---\ntype: workstream\nstage: design\nstatus: active\nproject: '[[Home]]'\n---\n# Barcode Scanning\n", encoding="utf-8")
            session = open_session(vault, workstream, "design", datetime(2026, 8, 27, 9, 30), "agent-a")
            note = parse_note(session)
            self.assertEqual(note.properties["workstream"], "[[Barcode Scanning]]")
            self.assertEqual(note.properties["owner"], "agent-a")
            self.assertIn("0930", session.name)


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run tests and verify they fail**

Run: `python -m unittest tests.test_lifecycle -v`

Expected: FAIL because lifecycle functions do not exist.

- [ ] **Step 3: Implement focused context discovery**

`find_context` reads `Home.md`, active workstreams, their current/latest sessions, and candidates matching case-insensitive terms in filenames, properties, headings, code paths, and wiki links. Rank exact workstream/property matches above body matches. Return metadata and 240-character evidence excerpts; never choose a lifecycle action automatically.

Define:

```python
from typing import Sequence


@dataclass(frozen=True)
class ContextCandidate:
    path: Path
    artifact_type: str
    status: str
    score: int
    reasons: Sequence[str]

@dataclass(frozen=True)
class ContextReport:
    project: Path
    candidates: Sequence[ContextCandidate]
    git_branch: str | None
    git_commit: str | None
    warnings: Sequence[str]
```

- [ ] **Step 4: Implement daily planning and session ownership**

`open_daily_plan` creates a retained plan from the daily template, links the latest prior daily note when present, and returns an existing same-day plan unchanged. `open_session` creates `workstreams/<slug>/sessions/YYYY-MM-DD-HHmm-<outcome>.md`, adds owner and lifecycle relationships, and refuses collision or missing workstream metadata. It must not mark any artifact complete.

`close_session` requires non-empty `## Actual blast radius`, `## Verification evidence`, and `## Handoff` sections. It sets `end_commit` when supplied, changes status only to `verified` or `complete` when the body explicitly contains fresh evidence, updates the owning workstream's `latest_session`, clears matching `current_session`, and never updates `Home.md` automatically.

- [ ] **Step 5: Implement the CLI**

Use `argparse`. Every subcommand accepts `--vault`; mutation commands print created or changed paths. `context` emits JSON with stable keys for agent consumption. Invalid lifecycle state returns exit code `2`; validation or integrity failure returns `1`; success returns `0`.

- [ ] **Step 6: Run lifecycle and full tests**

Run:

```text
python -m unittest tests.test_lifecycle -v
python -m unittest discover -s tests -v
```

Expected: all tests PASS.

- [ ] **Step 7: Commit lifecycle tools**

```bash
git add skills/supervaults/scripts/supervaults tests/test_lifecycle.py
git commit -m "feat: add vault lifecycle tooling"
```

---

### Task 6: Lifecycle validator and consolidation diagnostics

**Files:**
- Create: `skills/supervaults/scripts/supervaults/validation.py`
- Create: `tests/fixtures/valid-vault/**`
- Create: `tests/fixtures/invalid-vault/**`
- Create: `tests/test_validation.py`
- Modify: `skills/supervaults/scripts/supervaults/cli.py`

**Interfaces:**
- Produces: `validate_vault(vault: Path, today: date) -> ValidationReport`.
- Produces immutable `Finding(code: str, severity: str, path: Path, message: str)`.
- Produces CLI `validate --vault <path> [--json]`.
- Consumes: schema and Markdown parser from Task 3.

- [ ] **Step 1: Create valid and invalid fixtures**

The valid fixture contains one active workstream, a linked approved spec and ready plan, one closed verified session with expected/actual blast radius and evidence, a reconciled daily plan, and a current knowledge note.

The invalid fixture contains exactly these faults: invalid workstream status, dangling `current_session`, closed session without handoff, complete workstream without evidence, open old daily plan, broken plan-to-spec link, unsupported deployed claim without environment/version evidence, and two active workstreams declaring the same canonical outcome.

- [ ] **Step 2: Write failing validator tests**

```python
# tests/test_validation.py
import unittest
from datetime import date
from pathlib import Path

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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 3: Run the tests and verify they fail**

Run: `python -m unittest tests.test_validation -v`

Expected: FAIL because the validator does not exist.

- [ ] **Step 4: Implement deterministic validation**

Scan Markdown files excluding `.obsidian`, Git internals, and vendored sources. Validate types, artifact-specific statuses, applicable stages, required relationships, wiki-link targets, session closure sections, daily reconciliation, workstream completion evidence, delivery evidence, overview freshness, and canonical duplicates. A basename collision makes an unqualified wiki link ambiguous and produces an error.

Severity rules:

- `error`: broken lifecycle integrity or unsupported completion/delivery claim.
- `warning`: likely stale aggregation, missing optional verification detail, or unreconciled plan less than one day old.
- `notice`: safe optional promotion or navigation improvement.

Sort findings by severity, normalized path, code, and message. JSON output contains `errors`, `warnings`, `notices`, and `findings` counts plus stable finding objects.

- [ ] **Step 5: Add the CLI command and run all tests**

Run:

```text
python -m skills.supervaults.scripts.supervaults validate --vault tests/fixtures/valid-vault --json
python -m unittest discover -s tests -v
```

Expected: JSON reports zero errors for the valid fixture and all tests PASS.

- [ ] **Step 6: Commit validation**

```bash
git add skills/supervaults/scripts/supervaults/validation.py skills/supervaults/scripts/supervaults/cli.py tests/fixtures tests/test_validation.py
git commit -m "feat: validate Supervaults lifecycle integrity"
```

---

### Task 7: Complete the `$supervaults` orchestration skill

**Files:**
- Replace: `skills/supervaults/SKILL.md`
- Create: `skills/supervaults/references/architecture.md`
- Create: `skills/supervaults/references/lifecycle-routing.md`
- Create: `skills/supervaults/references/planning.md`
- Create: `skills/supervaults/references/artifact-model.md`
- Create: `skills/supervaults/references/operating-modes.md`
- Create: `skills/supervaults/references/integrations.md`
- Create: `skills/supervaults/references/quality-gates.md`
- Create: `tests/test_skill_contract.py`

**Interfaces:**
- Produces: one skill that routes natural development requests through the approved lifecycle.
- Produces: explicit internal references to vendored upstream modules using repository-relative paths.
- Consumes: all tooling, schema, templates, and vendored methods from Tasks 2–6.

- [ ] **Step 1: Write failing skill-contract tests**

```python
# tests/test_skill_contract.py
import re
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SKILL = ROOT / "skills/supervaults/SKILL.md"


class SkillContractTests(unittest.TestCase):
    def test_frontmatter_has_broad_trigger_and_exclusions(self):
        text = SKILL.read_text(encoding="utf-8")
        self.assertRegex(text, r"(?s)^---\nname: supervaults\ndescription: .+\n---")
        description = text.split("---", 2)[1]
        for phrase in ("plan", "investigate", "implement", "review", "consolidate", "project vault"):
            self.assertIn(phrase, description.lower())

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


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the contract tests and verify they fail**

Run: `python -m unittest tests.test_skill_contract -v`

Expected: FAIL because the temporary skill does not contain the complete contract and references.

- [ ] **Step 3: Write focused reference modules**

Translate the approved spec into imperative agent instructions. Avoid duplicating whole sections between references. Routing owns preinspection and lifecycle choice; planning owns four planning layers and daily reconciliation; artifact model owns schemas, links, promotion thresholds, and templates; operating modes owns mode-specific behavior; integrations owns authority and external-write boundaries; quality gates owns evidence, validation, and completion claims.

Each reference must explicitly return control to the Supervaults lifecycle after an applicable vendored Superpowers phase. The reference must say that vendored upstream files are read completely when invoked and remain authoritative for their engineering method.

- [ ] **Step 4: Replace the main skill with the orchestration surface**

Keep `SKILL.md` concise enough to load on every substantial development request. Its mandatory sequence is:

```text
Resolve vault → preinspect → choose lifecycle action → choose operating mode
→ state outcome and expected blast radius → invoke applicable upstream method
→ record actual result and evidence → reconcile workstream → validate → hand off
```

The description must trigger on repository-local project-vault development, multi-session continuity, daily planning, investigation of prior work, implementation, review, delivery, and consolidation. It must exclude general personal knowledge management, unrelated Obsidian editing, explanation-only requests, and trivial edits with no durable context.

Add a mode-routing table and a risk-sizing table. Link the exact reference needed at each decision point and avoid instructions to read every reference upfront. Include executable CLI examples using `python -m skills.supervaults.scripts.supervaults`.

- [ ] **Step 5: Run skill and full tests**

Run:

```text
python -m unittest tests.test_skill_contract -v
python -m unittest discover -s tests -v
```

Expected: all tests PASS.

- [ ] **Step 6: Commit the complete skill**

```bash
git add skills/supervaults/SKILL.md skills/supervaults/references tests/test_skill_contract.py
git commit -m "feat: orchestrate the Supervaults workflow"
```

---

### Task 8: Behavioral evaluation suite and documentation

**Files:**
- Create: `tests/evals/cases.json`
- Create: `tests/evals/expected-behaviors.md`
- Create: `tests/test_eval_contract.py`
- Create: `docs/testing.md`
- Modify: `README.md`

**Interfaces:**
- Produces: machine-readable prompt cases with expected mode, lifecycle action constraints, required artifacts, forbidden artifacts, and authorization boundary.
- Produces: a repeatable clean-agent evaluation protocol.
- Consumes: complete skill from Task 7.

- [ ] **Step 1: Write the failing evaluation-contract test**

```python
# tests/test_eval_contract.py
import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EvaluationContractTests(unittest.TestCase):
    def test_required_broad_prompts_are_covered(self):
        cases = json.loads((ROOT / "tests/evals/cases.json").read_text())
        prompts = {case["prompt"] for case in cases}
        required = {
            "Create a small inventory application.",
            "How about barcode scanning?",
            "Let's add exports.",
            "Continue where we stopped.",
            "What happened with authentication?",
            "Plan today.",
            "Consolidate recent work.",
            "Ship it to staging.",
        }
        self.assertTrue(required.issubset(prompts))

    def test_each_case_has_observable_oracle(self):
        cases = json.loads((ROOT / "tests/evals/cases.json").read_text())
        for case in cases:
            self.assertIn(case["mode"], {"orient", "plan", "investigate", "design", "implement", "review", "consolidate", "deliver", "capture"})
            self.assertTrue(case["must"])
            self.assertTrue(case["must_not"])


if __name__ == "__main__":
    unittest.main()
```

- [ ] **Step 2: Run the test and verify it fails**

Run: `python -m unittest tests.test_eval_contract -v`

Expected: FAIL because evaluation cases do not exist.

- [ ] **Step 3: Define observable evaluation cases**

For each required prompt, add at least two contexts: empty project and established multi-session project when applicable. Oracles must inspect observable output only: files created or updated, named links, status transitions, validation output, Git evidence, and unauthorized external mutations. Do not score hidden reasoning.

Include conflict cases proving that:

- A Superpowers plan stays in `superpowers/plans/` and is linked rather than copied.
- A new feature prompt preinspects and extends an authoritative workstream when appropriate.
- Minor debugging stays in a session; reusable root cause is promoted.
- Consolidation makes only small approved-scope corrections.
- Staging authorization cannot become production deployment.
- Missing optional connectors produce an explicit evidence gap rather than fabricated state.

- [ ] **Step 4: Document the clean-agent test protocol**

`docs/testing.md` defines setup, prompt order, vault snapshots, validator commands, manual scoring, and failure triage. Every run records plugin version, upstream commits, agent identifier, repository commit, environment, prompt, artifacts changed, validator result, and code-test result.

Update `README.md` with installation prerequisites, `$supervaults` examples, vault structure, core commands, upstream-update policy, and links to design and testing documents.

- [ ] **Step 5: Run all automated tests**

Run:

```text
python -m unittest tests.test_eval_contract -v
python -m unittest discover -s tests -v
python scripts/sync_upstreams.py --verify
```

Expected: all tests and integrity verification PASS.

- [ ] **Step 6: Commit evaluation and documentation**

```bash
git add tests/evals tests/test_eval_contract.py docs/testing.md README.md
git commit -m "test: define Supervaults behavioral acceptance"
```

---

### Task 9: Install, cache-bust, and run the multi-session acceptance workflow

**Files:**
- Modify: `C:/Users/AppieKalac/.agents/plugins/marketplace.json`
- Create in throwaway workspace: project source and repository-local `docs/` vault produced by the evaluation workflow
- Modify as failures require: task-owned plugin files only

**Interfaces:**
- Produces: an installed personal plugin discoverable as `$supervaults`.
- Produces: a timestamped installed cache version through the plugin-creator flow.
- Produces: a scored multi-session acceptance report in the throwaway project's vault and summarized in `docs/testing.md` only if the result changes the stable test protocol.
- Consumes: completed plugin and evaluation suite from Tasks 1–8.

- [ ] **Step 1: Run complete local verification**

Run:

```text
python -m unittest discover -s tests -v
python scripts/sync_upstreams.py --verify
python -m skills.supervaults.scripts.supervaults validate --vault tests/fixtures/valid-vault --json
git status --short
```

Expected: all tests PASS, vendor verification succeeds, fixture validation has zero errors, and the worktree contains no unexplained changes.

- [ ] **Step 2: Install through the plugin-creator cachebuster flow**

Follow the current plugin-creator instructions exactly. Add or replace one personal marketplace entry named `supervaults` pointing at `./plugins/supervaults`, category `Developer Tools`, installation policy `AVAILABLE`, and authentication policy appropriate for a local no-auth plugin. Do not delete the existing `obsidian-superpowers` entry unless the user separately requests its removal.

Run the prescribed validation, cachebuster versioning, and reinstall commands. Confirm the installed cache contains `.codex-plugin/plugin.json`, `skills/supervaults/SKILL.md`, references, templates, scripts, vendor modules, and the lock file.

- [ ] **Step 3: Run a clean activation smoke test**

Start a clean agent context in a new throwaway Git project and prompt: `Create a small inventory application.` Verify that `$supervaults` activates implicitly, initializes the work-centered vault, conducts preinspection, and routes design through the bundled Superpowers method before implementation.

- [ ] **Step 4: Run the multi-session broad-prompt sequence**

Use fresh agent ownership boundaries for:

```text
Create a small inventory application.
How about barcode scanning?
Let's add exports.
Continue where we stopped.
Plan today.
What happened with barcode scanning?
Consolidate recent work.
Ship it to staging.
```

Do not over-specify filenames or artifact categories. Let the skill make lifecycle decisions. Preserve every generated vault state and run the validator after each session.

- [ ] **Step 5: Audit the resulting vault independently**

The auditor must determine from `Home.md`, today's plan, and workstream overviews—without first reading every session—the current project health, active outcomes, exact next actions, canonical contracts, verification gaps, important rationale, and delivery state. It then checks detailed sessions for agreement with those summaries.

The acceptance run passes only when:

- No duplicate specification, plan, or canonical workstream exists.
- Every substantial session has expected/actual impact, evidence, and handoff.
- Daily planning selects outcomes without copying implementation tasks.
- Durable records exist only when promotion thresholds were met.
- Superpowers phase artifacts and vault checkpoints both occurred.
- No external write exceeded the prompt's authorization.
- The final validator reports zero errors.

- [ ] **Step 6: Correct failures through the appropriate workflow**

For deterministic script failures, use Superpowers systematic debugging and add a failing regression test before changing code. For instruction-following failures, tighten the smallest responsible `SKILL.md` or reference section and add or strengthen its observable evaluation oracle. Do not patch the throwaway vault to hide a plugin failure.

- [ ] **Step 7: Reinstall and repeat failed scenarios**

Use the plugin-creator cachebuster after every plugin change. Repeat the failed case in a fresh throwaway copy, then rerun the full automated suite and vendor-integrity verification.

- [ ] **Step 8: Commit the accepted release candidate**

```bash
git add .codex-plugin skills scripts tests upstream-selection.json upstream-lock.json THIRD_PARTY_NOTICES.md README.md LICENSE docs/testing.md
git commit -m "release: validate Supervaults 0.1.0 workflow"
```

If there are no post-test plugin changes, do not create an empty release commit; record the tested commit ID in the acceptance report instead.
