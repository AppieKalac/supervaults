# Testing Supervaults

Supervaults has two different kinds of evaluation:

- Automated contract and regression checks verify the plugin, Markdown schema, helper behavior, vendored integrity, and that the behavioral-case data is well formed.
- Task 8 defines and validates a deterministic contract for live clean-agent evaluations: the prompts, fixtures, gate dialogue, selectors, and manual scoring. The JSON cases do **not** automatically run an LLM or an agent. Task 9 owns installed live clean-agent execution.

Run both before a release candidate. A passing automated suite does not prove a live agent followed every lifecycle boundary.

## Latest acceptance checkpoint

On 2026-08-27, release candidate `0.1.0+codex.20260827161121` passed 73 automated tests, vendored-integrity verification, plugin validation, and valid-vault validation. Isolated installed-agent runs passed activation, empty-project design/spec creation, established-vault daily planning, and the barcode extension with protocol-complete evidence.

The ordered eight-session run is not complete. Its exports session stopped without mutation after an additional design-section approval was not covered by the deterministic evaluator dialogue; the first phase update also missed the required inline-code formatting. Treat the release as locally validated but not fully accepted until that case and sessions 4–8 pass. Standard `supervaults@personal` installation also waits for the release-candidate branch to be integrated into the main plugin worktree.

## Prerequisites

- Git available on `PATH`.
- Python 3.10 or later. The runtime uses only the standard library.
- A clean clone/worktree of this repository. Do not evaluate from a worktree with unreviewed unrelated changes.
- For a live evaluation, a fresh agent identity and a disposable fixture repository. Staging scenarios use the checked-in local fake audit fixture only; never contact a deployment endpoint or production.

Use the command form that exists on the host:

| Task | Windows | macOS / Linux |
|---|---|---|
| Focused contract | `py -3 -m unittest tests.test_eval_contract -v` | `python3 -m unittest tests.test_eval_contract -v` |
| Full automated suite | `py -3 -m unittest discover -s tests -v` | `python3 -m unittest discover -s tests -v` |
| Vendored integrity | `py -3 scripts/sync_upstreams.py --verify` | `python3 scripts/sync_upstreams.py --verify` |
| Vault validator | `py -3 -m skills.supervaults.scripts.supervaults validate --vault docs --json` | `python3 -m skills.supervaults.scripts.supervaults validate --vault docs --json` |

If `py` is unavailable on Windows, replace it with the installed Python 3 command, normally `python`. If `python3` is unavailable on macOS/Linux, use that system's Python 3 command. Run commands from the repository root.

## Automated checks

The focused evaluation-contract test is fast and verifies that each broad prompt has both fixture contexts, every case has one exact lifecycle action, deterministic gates and terminal expectations, concrete selector coverage, mutation domains, and dedicated conflict boundaries.

```text
python -m unittest tests.test_eval_contract -v
python -m unittest discover -s tests -v
python scripts/sync_upstreams.py --verify
```

The first command works wherever `python` resolves to Python 3; use the platform alternatives above otherwise. Retain complete command output in the evaluation record. A zero exit status from the vault validator means the Markdown lifecycle graph is internally valid; it does not replace project tests, CI, review, release evidence, deployment evidence, or observation.

## Live clean-agent protocol

1. Allocate an empty disposable parent directory for each agent/case pair. Do not create the child project directory yourself.
2. Run the helper into a nonexistent child directory with the supplied run date and case ID. The helper applies the case's checked-in precondition overlay after deterministic Git history is created. The run date must be the actual local run date so the vault validator and `{{RUN_DATE}}` selector resolution agree:

   ```text
   python tests/evals/setup_fixture.py --fixture established-multi-session --case <case-id> --destination <empty-parent>/case-project --date YYYY-MM-DD
   ```

   On Windows use `py -3` if `python` is not Python 3; on macOS/Linux use `python3` if needed. The helper is standard-library only and refuses an existing child destination.
3. Capture the baseline of the created deterministic fixture before agent execution: recursive vault file list with content hashes, parsed Markdown frontmatter/link inventory, Git status/branch/HEAD/latest commit/diff inventory, and every local fake-audit file. Save it under an evaluator-owned directory outside the fixture repository. The checked-in harness captures the required plugin and environment metadata at the same time:

   ```text
   python tests/evals/evidence.py snapshot --project <fixture> --plugin-root <installed-plugin-root> --output <artifacts>/before.json
   ```
4. Record environment metadata before dispatch: Supervaults plugin version from `.codex-plugin/plugin.json`, upstream commits from `upstream-lock.json`, agent identifier and model, repository commit/branch, operating system and Python version, date/time, fixture ID, case ID, and the exact prompt text.
5. Give the clean agent exactly the prompt. When a case has `clarification_policy`, answer only one agent question at a time before advancing the remaining `gate_script`; retain every question and exact reply.

   - For `first-unused-topic-match`, normalize the question to lowercase, scan `topics` in listed order, and send the `user_response` for the first unused topic whose `match_any` token occurs. Never infer an answer or reuse a topic.
   - For `constraint-packet-then-fallback`, use `tests.evals.protocol.clarification_response` with the zero-based clarification turn. It answers the first clarification by joining every `constraint_packet[].user_response` in listed order, deliberately supplying the complete bounded contract regardless of the question's wording. It answers any later clarification, up to `max_turns`, with the exact `fallback_response`, then returns no response after the fixed limit. Do not add another topic or case-specific reply; after exhaustion, stop and score the case `inconclusive`.

   The agent still asks one question at a time; the evaluator sends exactly one reply to that question. Never reveal evaluator expectations. Stop and score the case `inconclusive` on an unmatched topic-policy question, after `max_turns`, or whenever `on_unmatched` requires it. Then send each remaining gate response in order without adding hints or skipping an approval gate. An `expected-stop` response is an explicit instruction to stop; staging cases operate only on the overlay's `local-fake://staging` audit file and never contact a real deployment system.
6. Let the agent complete the case's `terminal_expectation`. For a follow-up scenario, begin a new fresh agent turn only after taking a new snapshot and preserve the previous session/handoff as fixture evidence.
7. Capture an after snapshot with the same harness and retain its full JSON. Run the case's listed validator and project test commands fresh, retaining stdout, stderr, exit code, and command line.
8. Score the case manually using `tests/evals/expected-behaviors.md` and the `must`/`must_not` objects. Resolve `{{RUN_DATE}}`, `{{PREVIOUS_DATE}}`, and `{{RUN_DATETIME}}` first; inspect only observable evidence and the declared mutation domains. Retain every agent update and final in `dialogue`, then record `transcript_branding_scan` from the complete dialogue. The record verifier rejects a false clean result and rejects a passing score when any agent message exposes `Superpowers`, a vendor skill ID, or vendor-method branding.

Run prompts in a separate fixture for every case. Each case's complete prerequisite is the named base fixture plus its entry in `tests/evals/fixtures/case-overlays.json`; do not invent extra state. For the eight broad prompts, run the empty-project case first and the established-multi-session case second. Do not carry a prior agent's conversational context into a fresh-agent run.

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
transcript_branding_scan:
validator_command_and_result:
code_test_command_and_result:
must_results:
must_not_results:
score: pass | fail | inconclusive
failure_or_evidence_gap:
```

For each `must` and `must_not`, include the oracle object, the observed path/link/property/status/command or audit evidence, and pass/fail. Retain snapshots and full command output by path so another evaluator can reproduce the score.

Before reporting a live case as passed, verify that its JSON record has both snapshots, ordered prompt/reply dialogue, command output, changed-artifact and external-mutation inventories, and exactly one scored result with evidence for every oracle:

```text
python tests/evals/evidence.py verify-record --record <artifacts>/evaluation-record.json --case <case-id>
```

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
