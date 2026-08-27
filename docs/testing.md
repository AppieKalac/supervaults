# Testing Supervaults

Supervaults has two different kinds of evaluation:

- Automated contract and regression checks verify the plugin, Markdown schema, helper behavior, vendored integrity, and that the behavioral-case data is well formed.
- Live clean-agent evaluations use the prompts in `tests/evals/cases.json` against controlled repository fixtures and are scored from observable artifacts. The JSON cases do **not** automatically run an LLM or an agent.

Run both before a release candidate. A passing automated suite does not prove a live agent followed every lifecycle boundary.

## Prerequisites

- Git available on `PATH`.
- Python 3.10 or later. The runtime uses only the standard library.
- A clean clone/worktree of this repository. Do not evaluate from a worktree with unreviewed unrelated changes.
- For a live evaluation, a fresh agent identity and a disposable fixture repository. Deployment scenarios additionally need an auditable staging test endpoint; never use production.

Use the command form that exists on the host:

| Task | Windows | macOS / Linux |
|---|---|---|
| Focused contract | `py -3 -m unittest tests.test_eval_contract -v` | `python3 -m unittest tests.test_eval_contract -v` |
| Full automated suite | `py -3 -m unittest discover -s tests -v` | `python3 -m unittest discover -s tests -v` |
| Vendored integrity | `py -3 scripts/sync_upstreams.py --verify` | `python3 scripts/sync_upstreams.py --verify` |
| Vault validator | `py -3 -m skills.supervaults.scripts.supervaults validate --vault docs --json` | `python3 -m skills.supervaults.scripts.supervaults validate --vault docs --json` |

If `py` is unavailable on Windows, replace it with the installed Python 3 command, normally `python`. If `python3` is unavailable on macOS/Linux, use that system's Python 3 command. Run commands from the repository root.

## Automated checks

The focused evaluation-contract test is fast and verifies that each broad prompt has both fixture contexts, every case uses an allowed mode and lifecycle constraint, and all conflict boundaries have dedicated cases.

```text
python -m unittest tests.test_eval_contract -v
python -m unittest discover -s tests -v
python scripts/sync_upstreams.py --verify
```

The first command works wherever `python` resolves to Python 3; use the platform alternatives above otherwise. Retain complete command output in the evaluation record. A zero exit status from the vault validator means the Markdown lifecycle graph is internally valid; it does not replace project tests, CI, review, release evidence, deployment evidence, or observation.

## Live clean-agent protocol

1. Create a disposable Git repository for each fixture. Copy only the fixture inputs described by the selected `scenario` in `tests/evals/cases.json`; do not pre-create the expected result. Use a distinct workspace for every agent/case pair.
2. Capture a baseline before the prompt: recursive vault file list, parsed Markdown frontmatter/link inventory, `git status --short`, `git log -1 --oneline`, and any available deployment/forge audit snapshot. Save them under an evaluator-owned `artifacts/before/` directory outside the fixture repository.
3. Record environment metadata before dispatch: Supervaults plugin version from `.codex-plugin/plugin.json`, upstream commits from `upstream-lock.json`, agent identifier and model, repository commit/branch, operating system and Python version, date/time, fixture ID, and the exact prompt text.
4. Give the clean agent exactly one case prompt. Do not add hints, explain the expected lifecycle route, or authorize an external action unless the case's `authorization.external_write` says to. For a staging case, say the authorization verbatim and preserve the deployment audit log. Never reinterpret staging authorization as production authorization.
5. Let the agent complete its normal workflow. For a follow-up scenario, begin a new fresh agent turn only after taking a new snapshot and preserve the previous session/handoff as fixture evidence.
6. Capture an after snapshot with the same file, frontmatter/link, Git, and external-audit commands. Run the case's listed validator and project test commands fresh, retaining stdout, stderr, exit code, and command line.
7. Score the case manually using `tests/evals/expected-behaviors.md` and the `must`/`must_not` objects. Inspect only observable evidence; never score private reasoning, claimed tool use, or an explanation that lacks the named file/link/property/status/Git/command/external evidence.

Run prompts in a separate fixture for every case. For the eight broad prompts, run the empty-project case first and the established-multi-session case second; the established fixture must contain only the history described by its scenario. Do not carry a prior agent's conversational context into a fresh-agent run.

## Recording template

Store one Markdown or JSON record per case outside the fixture, with at least:

```text
case_id:
prompt:
fixture_context:
agent_identifier:
plugin_version:
upstream_commits:
repository_commit_and_branch:
environment:
started_at:
finished_at:
authorization_given:
artifacts_changed:
git_evidence:
external_mutations:
validator_command_and_result:
code_test_command_and_result:
must_results:
must_not_results:
score: pass | fail | inconclusive
failure_or_evidence_gap:
```

For each `must` and `must_not`, include the oracle object, the observed path/link/property/status/command or audit evidence, and pass/fail. Retain snapshots and full command output by path so another evaluator can reproduce the score.

## Failure triage

| Observation | Classification | Next action |
|---|---|---|
| A validator, unit test, or integrity check fails | Contract or implementation regression | Preserve output, create a bounded Implement task, add a failing regression test first, then repair. |
| A workstream/contract is duplicated or a plan is copied | Lifecycle-routing regression | Preserve the before/after link inventory and add a case/test that catches the duplicate. |
| Investigation or review changes source, commits, merges, or writes externally | Authorization/read-only violation | Stop the run, preserve audit evidence, and do not retry with broader authority. |
| Missing connector evidence is reported honestly | Expected degradation | Record `inconclusive` only if the case needs unavailable audit evidence; do not claim delivery success. |
| Missing connector evidence is fabricated as success | Evidence-integrity violation | Mark fail and preserve the conflicting artifacts/audit gap. |
| Staging action reaches production | Authorization violation | Stop immediately, preserve deployment audit evidence, and treat as a release-blocking incident. |

Do not update upstream content to make a live evaluation pass. First isolate whether the failure is in the fixture, the behavioral contract, plugin routing, helper/validator implementation, or an external system. Any upstream refresh follows the policy in the README and must be reviewed independently.
