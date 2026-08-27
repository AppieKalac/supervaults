# Operating modes and internal methods

Select one primary mode after preinspection. If internal method applicability is unclear, read `vendor/superpowers/skills/using-superpowers/SKILL.md` completely to select among the vendored methods while keeping `$supervaults` as the only user-visible surface. Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method; Supervaults adds lifecycle entry, continuity, evidence, reconciliation, and closure around it.

## Orient

Report current health, active workstreams, recent evidence, gaps, blockers, and likely next action. Stay read-only and distinguish vault claims from live Git/external state. Return directly to Supervaults reconciliation only if stale local truth must be corrected within scope.

## Plan

Use [planning](planning.md). For an engineering plan after an approved design, invoke `vendor/superpowers/skills/writing-plans/SKILL.md`. After planning, return control to Supervaults to link the contract, reconcile the workstream/daily plan, validate, and hand off.

## Investigate

Stay read-only by default. Separate freshly verified facts, historical claims, current inferences, conflicts, and unknowns. For a bug, test failure, or unexpected behavior, invoke `vendor/superpowers/skills/systematic-debugging/SKILL.md`; if a fix follows, also invoke `vendor/superpowers/skills/test-driven-development/SKILL.md`. Promote an investigation record only when it will be reused independently. After investigation or debugging, return control to Supervaults to record evidence, actual impact, durable findings, reconciliation, validation, and handoff.

## Design

For new behavior, creative work, or design uncertainty, invoke `vendor/superpowers/skills/brainstorming/SKILL.md`. Preserve its approval gates and prospective specification. If it routes to implementation planning, then read and invoke `vendor/superpowers/skills/writing-plans/SKILL.md`. After each design/planning phase, return control to Supervaults to link provenance and canonical contracts, reconcile the owning workstream, validate, and hand off.

## Implement

Require the approved contract appropriate to risk. Establish isolation with `vendor/superpowers/skills/using-git-worktrees/SKILL.md` when needed. Always use `vendor/superpowers/skills/test-driven-development/SKILL.md` for feature/bug behavior unless the authoritative method obtains the user's exception.

For an approved plan, choose one authoritative execution route:

- `vendor/superpowers/skills/executing-plans/SKILL.md` for sequential execution in a separate session with checkpoints.
- `vendor/superpowers/skills/subagent-driven-development/SKILL.md` for independent plan tasks in the current session when multi-agent delegation is available and authorized.
- `vendor/superpowers/skills/dispatching-parallel-agents/SKILL.md` only for multiple independent problem domains without shared write ownership.

In multi-agent work, every worker owns a unique session and the coordinator alone mutates shared overviews. After each execution phase/task, return control to Supervaults to record actual impact/evidence, reconcile ownership and next action, validate, and hand off.

## Review

For requested or completion review, invoke `vendor/superpowers/skills/requesting-code-review/SKILL.md`. When applying received feedback, invoke `vendor/superpowers/skills/receiving-code-review/SKILL.md` and verify it against this codebase before mutation. Create a promoted review record only when findings/dispositions need independent tracking. After review, return control to Supervaults to record findings and evidence, route fixes back through implementation, reconcile readiness, validate, and hand off.

## Consolidate

Compare specifications, plans, sessions, commits, reviews, current overviews, daily plans, and delivery evidence. Fix small in-scope metadata/link drift, promote qualifying durable truth, and route material new behavior back through Design. Return control to Supervaults after any invoked upstream phase to reconcile, validate, and hand off.

## Deliver

Keep verification, review, merge, release, deployment, and observation distinct. Before any completion claim invoke `vendor/superpowers/skills/verification-before-completion/SKILL.md`. When implementation is complete and integration choice is needed, invoke `vendor/superpowers/skills/finishing-a-development-branch/SKILL.md`. External mutations still require the authorization rules in [integrations](integrations.md). After each verification or delivery phase, return control to Supervaults to record version/environment evidence, reconcile stage/status, validate, and hand off.

## Capture

Create or update an inbox idea with provenance, without creating a selected workstream, daily commitment, specification, or plan. Return to Supervaults to link the retained possibility and leave current priorities unchanged.
