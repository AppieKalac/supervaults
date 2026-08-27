# Operating modes and internal methods

Select one primary mode after preinspection and follow its numbered recipe without reordering. No vendored method may be invoked before that mode's prerequisite references are loaded and its focused preinspection is complete. Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method.

## Internal method adaptation

Vendored files remain byte-unchanged and authoritative for engineering procedure, approval gates, review gates, and stopping conditions. Adapt only their transport and branding inside the one visible `$supervaults` skill:

- Announce an internal phase as `Using Supervaults' <phase>`; do not advertise an unregistered vendored skill.
- Translate a vendored `superpowers:<skill>` handoff into a repository-relative read and route to `vendor/superpowers/skills/<skill>/SKILL.md`, after the destination mode's prerequisites are loaded.
- Never tell the user to invoke a vendored skill directly. `$supervaults` retains control of the user-visible lifecycle.
- Preserve the method's substantive procedure and every approval/review gate. This adaptation does not authorize skipping, weakening, or silently satisfying a gate.
- Apply the vendored procedure only inside the selected Supervaults action's scope and authorization boundary. A vendored mutation instruction cannot expand a read-only Review or authorize an external write.

If internal method applicability remains unclear after the mode prerequisites are loaded, read `vendor/superpowers/skills/using-superpowers/SKILL.md` completely and apply its selection rule through this adaptation.

## Orient

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md). Preinspect `Home.md`, active/ready/blocked workstreams, current/latest sessions, recent handoffs, Git state, and relevant external references.
2. **Internal method:** None. Orient is read-only; distinguish retained vault claims from freshly observed repository or external state.
3. **Supervaults return:** Report current health, evidence, gaps, blockers, and likely next action. Validate current vault integrity; reconcile only if the user separately authorizes a mutation.

## Plan

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md) and [planning](planning.md). Inspect the planning layer in scope, linked contracts, prior/daily plans, handoffs, delivery gaps, Git state, and constraints. Establish the resolved-vault contract-location override before any engineering planning method.
2. **Internal method:** For daily/project/workstream planning, no vendor method is required. For an engineering plan after an approved design, read `vendor/superpowers/skills/writing-plans/SKILL.md` completely and apply it with the resolved-vault path override.
3. **Supervaults return:** Link the plan to its canonical workstream, record planning evidence, reconcile daily/workstream state and next action, validate, and hand off.

## Investigate

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md) and [quality gates](quality-gates.md); read [artifact model](artifact-model.md) before promoting an independently reusable investigation. Preinspect the symptom/history, contracts, sessions, code, Git changes, and available external evidence. Investigation is read-only by default.
2. **Internal method:** For a bug, test failure, or unexpected behavior, read `vendor/superpowers/skills/systematic-debugging/SKILL.md` completely. If the user also wants a fix, finish and return from Investigate first, then select a separate Implement action where `vendor/superpowers/skills/test-driven-development/SKILL.md` applies.
3. **Supervaults return:** Separate verified facts, historical claims, inferences, conflicts, and unknowns; record findings/evidence and actual inspected scope, promote only when justified, reconcile, validate, and hand off.

## Design

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md), [planning](planning.md), and [artifact model](artifact-model.md). Preinspect related ideas, canonical workstreams/contracts, code, recent decisions, and Git state. State the resolved-vault specification and plan locations before method invocation.
2. **Internal method:** Read `vendor/superpowers/skills/brainstorming/SKILL.md` completely for new behavior or design uncertainty. Preserve its classification and approval gates. If an approved architectural design proceeds to planning, read `vendor/superpowers/skills/writing-plans/SKILL.md` completely only after the planning prerequisites remain satisfied.
3. **Supervaults return:** Store/link the approved contract at the resolved-vault location, preserve provenance, record the phase result/evidence, reconcile stage/status and next action, validate, and hand off after each design or planning phase.

## Implement

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md), [planning](planning.md), and [quality gates](quality-gates.md); also read [architecture](architecture.md) for multi-agent ownership. Preinspect the approved contract, current session/handoff, worktree and Git state, expected blast radius, and execution ownership.
2. **Internal method:** Read `vendor/superpowers/skills/using-git-worktrees/SKILL.md` when isolation is needed and `vendor/superpowers/skills/test-driven-development/SKILL.md` for feature/bug behavior. For an approved plan, choose one route after prerequisites: `vendor/superpowers/skills/executing-plans/SKILL.md` for sequential separate-session execution; `vendor/superpowers/skills/subagent-driven-development/SKILL.md` for authorized independent tasks in the current session; or `vendor/superpowers/skills/dispatching-parallel-agents/SKILL.md` only for independent domains without shared write ownership.
3. **Supervaults return:** After each execution phase/task, record actual blast radius, checks, deviations, blockers, and next action; collect owned worker roll-ups, reconcile the canonical workstream, validate, and hand off.

## Review

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md) and [quality gates](quality-gates.md), plus [integrations](integrations.md) when external review context is relevant. Preinspect the requested scope, requirements, diff/commits, tests, prior findings, and authorization. A plain review or audit request is read-only.
2. **Internal method:** Read `vendor/superpowers/skills/requesting-code-review/SKILL.md` completely to produce findings. Read `vendor/superpowers/skills/receiving-code-review/SKILL.md` completely when evaluating received feedback. Adapt either method to stop after findings and dispositions; even if it says to fix Important/Critical issues, do not apply fixes, commit, merge, or enter a fix loop during Review.
3. **Supervaults return:** Record findings, dispositions, evidence, and unchecked areas; reconcile review readiness and validate, then stop. Applying findings requires explicit user intent and a separate Implement lifecycle action with bounded scope.

## Consolidate

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md), [artifact model](artifact-model.md), and [quality gates](quality-gates.md). Preinspect specifications, plans, sessions, commits, reviews, daily/current overviews, promoted records, and delivery evidence.
2. **Internal method:** None by default. Correct only small in-scope lifecycle metadata/link drift. Route unexpected behavior to Investigate and material new behavior to Design, then load that mode's prerequisites before any method.
3. **Supervaults return:** Promote qualifying durable truth, reconcile workstream/project/daily state and delivery gaps, record corrections/evidence, validate, and hand off.

## Deliver

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md), [integrations](integrations.md), and [quality gates](quality-gates.md). Preinspect verification/review/integration state, Git/CI/release/deployment evidence, target environment, rollback, observation needs, and exact external-write authorization.
2. **Internal method:** Before any completion claim, read `vendor/superpowers/skills/verification-before-completion/SKILL.md` completely. When implementation is complete and the user must choose integration, read `vendor/superpowers/skills/finishing-a-development-branch/SKILL.md` completely. Do not treat its options as authorization for an external write.
3. **Supervaults return:** Record version/commit/environment evidence and unchecked areas for each distinct transition, reconcile stage/status and next action, validate, and hand off after verification, integration, release, deployment, or observation.

## Capture

1. **Prerequisites:** Read [lifecycle routing](lifecycle-routing.md), [artifact model](artifact-model.md), and [integrations](integrations.md). Preinspect related inbox ideas and workstreams to avoid duplication; confirm this remains an uncommitted possibility.
2. **Internal method:** If editing the vault, read `vendor/obsidian-skills/skills/obsidian-markdown/SKILL.md` completely. Do not invoke a design or planning method.
3. **Supervaults return:** Create/update the inbox idea with provenance, link related context, leave priorities and commitments unchanged, validate, and hand off.
