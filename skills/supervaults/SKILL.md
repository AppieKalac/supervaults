---
name: supervaults
description: Plan, investigate, design, implement, review, consolidate, deliver, and capture repository-local project vault development across sessions. Use for durable project continuity, daily planning, prior-work reconstruction, multi-agent handoffs, and evidence-backed lifecycle work; do not use for general personal knowledge management, unrelated Obsidian editing, explanation-only requests, or trivial edits with no durable context.
---

# Supervaults

Use one repository-local Obsidian project vault as durable development memory while the vendored Superpowers modules remain authoritative for engineering method. Git, tests, CI, issue trackers, release systems, deployments, and observability remain authoritative for their own state.

Do not load every reference. Follow the shared protocol, select a mode, then read only the focused references and vendored method named by that route. Read any invoked vendored file completely before following it.

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
5. Read [operating modes](references/operating-modes.md), then read the applicable `vendor/.../SKILL.md` completely. That vendored module is authoritative for its engineering phase.
6. After every design, planning, execution, review, or verification phase, explicitly return control to Supervaults. Record the actual result and actual blast radius, evidence, deviations, blockers, and exact next action; reconcile the session into the owning workstream and project truth.
7. Read [quality gates](references/quality-gates.md), run fresh project checks and vault validation, then make only evidence-supported state or delivery claims. Write a handoff before closing a session.

Never store secrets, credentials, private chain-of-thought, raw log dumps, or copied external-system histories in the vault.

## Mode routing

| Mode | Select when | Read next |
|---|---|---|
| Orient | Explain current state and likely next action without mutation | [lifecycle routing](references/lifecycle-routing.md), then [operating modes](references/operating-modes.md) |
| Plan | Select project, workstream, engineering, or daily outcomes | [planning](references/planning.md), then [operating modes](references/operating-modes.md) |
| Investigate | Reconstruct history, state, or root cause; read-only by default | [operating modes](references/operating-modes.md), then [artifact model](references/artifact-model.md) only if promotion is justified |
| Design | Turn an idea into an approved behavior contract | [operating modes](references/operating-modes.md), then [artifact model](references/artifact-model.md) |
| Implement | Execute an approved bounded design or implementation plan | [operating modes](references/operating-modes.md), then [quality gates](references/quality-gates.md) |
| Review | Assess code, behavior, risk, feedback, or readiness | [operating modes](references/operating-modes.md), then [quality gates](references/quality-gates.md) |
| Consolidate | Audit drift, close small in-scope gaps, and promote durable truth | [artifact model](references/artifact-model.md), then [quality gates](references/quality-gates.md) |
| Deliver | Move verified work through integration, release, deployment, and observation | [integrations](references/integrations.md), then [quality gates](references/quality-gates.md) |
| Capture | Retain an unresolved possibility without committing to it | [artifact model](references/artifact-model.md) |

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

Run helpers from the repository root. They automate Markdown mechanics but do not choose lifecycle actions or replace engineering checks.

```text
python -m skills.supervaults.scripts.supervaults init --vault docs --project "Project Name"
python -m skills.supervaults.scripts.supervaults context --vault docs authentication recovery
python -m skills.supervaults.scripts.supervaults plan-today --vault docs
python -m skills.supervaults.scripts.supervaults open-session --vault docs --workstream "docs/workstreams/account-recovery/Account Recovery.md" --outcome "verify recovery" --owner "agent-name"
python -m skills.supervaults.scripts.supervaults close-session --vault docs --session docs/workstreams/account-recovery/sessions/2026-08-27-0930-verify-recovery.md --end-commit abc1234
python -m skills.supervaults.scripts.supervaults validate --vault docs --json
```

If helpers are unavailable, edit the corresponding Markdown from `skills/supervaults/templates/vault/` manually and preserve the same schema and gates. For system authority, external-write permission boundaries, native Obsidian editing, Bases, optional Canvas maps, and optional live Obsidian CLI use, read [integrations](references/integrations.md).
