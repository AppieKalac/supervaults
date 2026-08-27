---
name: supervaults
description: Plan, investigate, design, implement, review, consolidate, deliver, and capture repository-local project vault development across sessions. Use before separately installed Superpowers methods for durable project continuity, daily planning, prior-work reconstruction, multi-agent handoffs, and evidence-backed lifecycle work; do not use for general personal knowledge management, unrelated Obsidian editing, explanation-only requests, or trivial edits with no durable context.
---

# Supervaults

Use one repository-local Obsidian project vault as durable development memory while the vendored Superpowers modules remain authoritative for engineering method. Git, tests, CI, issue trackers, release systems, deployments, and observability remain authoritative for their own state.

Resolve the installed plugin root before following any path. Define `<supervaults-root>` as **two directory levels above this `SKILL.md`** (`skills/supervaults/../..`). All `../../vendor/...` routes below and in references are relative to the directory containing this `SKILL.md`, not the developer's target repository. References and templates are relative to this skill directory.

When a global skill-discovery rule has already loaded a separately installed Superpowers skill for the same request, read Supervaults next and do not run that separate phase, announce it as the active workflow, or follow its handoff directly. Supervaults absorbs the handoff, establishes its prerequisites and authorization boundary, and then reads the matching bundled method under `<supervaults-root>/vendor/` internally.

Do not load every reference. Follow the shared protocol, select a mode, then follow that mode's ordered recipe: load its prerequisite references and complete its focused preinspection before reading or invoking a vendored method. Read any invoked vendored file completely before following it.

## Shared protocol

For every substantial request, run this sequence:

```text
Resolve vault → preinspect → choose lifecycle action → choose operating mode
→ state outcome and expected blast radius → invoke applicable upstream method
→ record actual result and evidence → reconcile workstream → validate → hand off
```

1. Resolve the repository and vault. Start at `Home.md`; a conventional vault lives at `docs/`. Read [architecture](references/architecture.md) when project ownership, evidence layers, navigation, or multi-agent ownership matters.
2. Preinspect the relevant lifecycle neighborhood before creating anything. Read [lifecycle routing](references/lifecycle-routing.md), inspect current contracts, workstreams, recent sessions, Git state, and available external references, then choose `resume`, `extend`, `promote`, `implement`, `supersede`, `merge`, `create-new`, or `reference-only`.
3. Select the operating mode below. If intent could reasonably select different lifecycle actions, report the evidence found and ask the user to choose; do not create a competing workstream or contract.
4. Before material mutation, state the bounded outcome, explicit exclusions, risk, and expected blast radius. Open one uniquely owned session for each independent execution owner. Trivial edits need no session unless durable context would otherwise be lost.
5. Read [operating modes](references/operating-modes.md), load the selected mode's prerequisites in order, and only then read the applicable `../../vendor/.../SKILL.md` completely. That vendored module is authoritative for its engineering procedure and gates; apply Supervaults' internal-method branding and handoff adaptation.
6. After every design, planning, execution, review, or verification phase, explicitly return control to Supervaults. Record the actual result and actual blast radius, evidence, deviations, blockers, and exact next action; reconcile the session into the owning workstream and project truth.
7. Read [quality gates](references/quality-gates.md), run fresh project checks and vault validation, then make only evidence-supported state or delivery claims. Write a handoff before closing a session.

Never store secrets, credentials, private chain-of-thought, raw log dumps, or copied external-system histories in the vault.

## Ordered mode routing

Every row means: **1. load prerequisites and preinspect → 2. run only the applicable internal method → 3. return to Supervaults for evidence, reconciliation, validation, and handoff.** No vendored method may run before step 1. Read [operating modes](references/operating-modes.md) for the exact recipe.

| Mode | Select when | Ordered route |
|---|---|---|
| Orient | Explain current state and likely next action without mutation | [lifecycle routing](references/lifecycle-routing.md) → no vendor method → report evidence and validate current vault state |
| Plan | Select project, workstream, engineering, or daily outcomes | [lifecycle routing](references/lifecycle-routing.md) + [planning](references/planning.md) → planning method if applicable → reconcile plan/workstream and validate |
| Investigate | Reconstruct history, state, or root cause; read-only by default | [lifecycle routing](references/lifecycle-routing.md) + [quality gates](references/quality-gates.md) → debugging method if applicable → record findings, reconcile, and validate |
| Design | Turn an idea into an approved behavior contract | [lifecycle routing](references/lifecycle-routing.md) + [planning](references/planning.md) + [artifact model](references/artifact-model.md) → design method → link contract, reconcile, and validate |
| Implement | Execute an approved bounded design or implementation plan | [lifecycle routing](references/lifecycle-routing.md) + [planning](references/planning.md) + [quality gates](references/quality-gates.md) → execution/TDD method → record actual evidence, reconcile, and validate |
| Review | Assess code, behavior, risk, feedback, or readiness without mutation | [lifecycle routing](references/lifecycle-routing.md) + [quality gates](references/quality-gates.md) → review method → stop after findings/dispositions, reconcile, and validate |
| Consolidate | Audit drift, close small in-scope lifecycle gaps, and promote durable truth | [lifecycle routing](references/lifecycle-routing.md) + [artifact model](references/artifact-model.md) + [quality gates](references/quality-gates.md) → no vendor method unless rerouted → reconcile and validate |
| Deliver | Move verified work through integration, release, deployment, and observation | [lifecycle routing](references/lifecycle-routing.md) + [integrations](references/integrations.md) + [quality gates](references/quality-gates.md) → verification/branch method → record delivery evidence, reconcile, and validate |
| Capture | Retain an unresolved possibility without committing to it | [lifecycle routing](references/lifecycle-routing.md) + [artifact model](references/artifact-model.md) → Obsidian Markdown method if editing → link provenance and validate |

Natural-language requests are valid. Infer the likely mode only after focused preinspection.

## Risk sizing

| Risk | Vault treatment |
|---|---|
| Trivial | No session unless context would be lost; run a proportionate check |
| Bounded | Concise expected/actual affected areas and verification |
| Substantial | Expected and actual impact matrix, evidence, and explicit unchecked areas |
| High | Full impact matrix, design review, approvals, rollout, rollback, and operational evidence |

Use the canonical impact surfaces and structured evidence contract in [quality gates](references/quality-gates.md). Separate stage from status and never collapse `implemented`, `verified`, `reviewed`, `merged`, `released`, `deployed`, and `observed` into one claim.

## Helpers

Run helpers with the working directory set to `<supervaults-root>`, passing the target repository's vault and artifact paths as absolute paths when the target is elsewhere. They automate Markdown mechanics but do not choose lifecycle actions or replace engineering checks.

```text
python -m skills.supervaults.scripts.supervaults init --vault docs --project "Project Name"
python -m skills.supervaults.scripts.supervaults context --vault docs authentication recovery
python -m skills.supervaults.scripts.supervaults plan-today --vault docs
python -m skills.supervaults.scripts.supervaults open-session --vault docs --workstream "docs/workstreams/account-recovery/Account Recovery.md" --outcome "verify recovery" --owner "agent-name"
python -m skills.supervaults.scripts.supervaults close-session --vault docs --session docs/workstreams/account-recovery/sessions/2026-08-27-0930-verify-recovery.md --end-commit abc1234
python -m skills.supervaults.scripts.supervaults validate --vault docs --json
```

If helpers are unavailable, edit the corresponding Markdown from `skills/supervaults/templates/vault/` manually and preserve the same schema and gates. For system authority, external-write permission boundaries, native Obsidian editing, Bases, optional Canvas maps, and optional live Obsidian CLI use, read [integrations](references/integrations.md).
