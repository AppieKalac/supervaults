# Planning

Keep four linked planning layers distinct:

| Layer | Question | Canonical location |
|---|---|---|
| Project direction | Which outcomes matter, and in what order? | `Home.md`, optionally `Roadmap.md` |
| Workstream planning | What is this outcome's state and next milestone? | Workstream overview |
| Engineering planning | How will an approved design be implemented? | `superpowers/plans/` |
| Daily planning | What will be deliberately advanced today? | `daily/YYYY-MM-DD.md` |

Link layers instead of copying their content. Keep outcome selection out of engineering task lists, and keep observed execution out of prospective plans.

## Resolved-vault contract locations

Before reading or invoking the vendored brainstorming or writing-plans method, resolve the project vault and state these output locations:

- Specification: `<resolved-vault>/superpowers/specs/YYYY-MM-DD-<topic>-design.md`
- Implementation plan: `<resolved-vault>/superpowers/plans/YYYY-MM-DD-<feature>.md`

This user/project location override takes precedence over the vendored `docs/` defaults. Pass the resolved path into the internal method, preserve it through any `superpowers:<skill>` handoff adaptation, and do not create a competing specification or plan tree elsewhere in the repository.

## Plan today

Inspect the previous plan and unfinished selections, active/ready/blocked workstreams, recent handoffs, Git state, verification/review/delivery gaps, available external constraints, and inbox ideas. Do not automatically promote an inbox idea.

Rank candidates by continuity, delivery gaps, unblocking value, risk, user value, urgency, dependencies, available focus/access, and staleness. Explain recommendations and leave selection to the developer. Prefer one primary outcome, one optional secondary outcome, small maintenance, known constraints, and `Not today`. Record outcome-level finish conditions and link the workstream/engineering plan.

Create or reuse today's retained plan with:

`python -m skills.supervaults.scripts.supervaults plan-today --vault <vault>`

Record meaningful replanning: what arrived, why it displaced or did not displace selected work, which outcome changed, and whether the change is temporary or a priority change.

At end of day, never silently roll work forward. Reconcile every selection as finished, advanced but unfinished, blocked, deliberately deferred, dropped, or still active. Record the first likely next action without creating tomorrow's commitment.

## Engineering plans

When an approved design needs multi-step, risky, cross-component, or multi-session execution, read `../../vendor/superpowers/skills/writing-plans/SKILL.md` completely and follow it as the authoritative planning method with the resolved-vault location override above. Preserve its specification link and prospective task contract. For bounded approved work that its method says needs no plan document, do not create one merely for vault symmetry.

Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method. After the vendored planning phase ends, explicitly return control to Supervaults: link the plan to its workstream, record the planning outcome and evidence, reconcile stage/status and next action, validate the vault, and hand off. The plan never replaces the workstream's current state.
