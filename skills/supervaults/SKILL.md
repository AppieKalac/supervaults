---
name: supervaults
description: Plan, investigate, design, implement, review, deliver, and consolidate repository-local project-vault development across multiple sessions. Use for durable project continuity, daily planning, and evidence-backed lifecycle work; do not use for general personal knowledge management, unrelated Obsidian editing, explanation-only requests, or trivial edits with no durable context.
---

# Supervaults

Use Supervaults to coordinate durable development work through a repository-local project vault. The vault records current project and workstream truth while Git, tests, CI, issue trackers, release systems, deployment platforms, and observability systems remain authoritative for their own state.

## Top-level protocol

For every substantial request:

1. Resolve the repository and project vault.
2. Preinspect the relevant project state, workstreams, contracts, recent sessions, evidence, and repository state.
3. Choose the lifecycle action: `resume`, `extend`, `promote`, `implement`, `supersede`, `merge`, `create-new`, or `reference-only`.
4. Route to the applicable mode: orient, plan, investigate, design, implement, review, consolidate, deliver, or capture.
5. State the bounded outcome and expected blast radius before material changes.
6. Invoke the applicable engineering method; Superpowers owns that method, while Supervaults owns continuity and lifecycle records.
7. Record the actual result, actual blast radius, concise verification evidence, deviations, and handoff.
8. Reconcile the owning workstream and project-level truth when it changed.
9. Validate the vault before making closure or delivery claims.

Keep specifications and plans prospective; keep sessions evidentiary; keep workstreams current. Do not treat implemented, verified, reviewed, merged, released, deployed, or observed as interchangeable states. Do not record secrets, credentials, raw log dumps, or private reasoning. Never mutate an external system without authorization for the named action and scope.

## Lifecycle routing

Use the closest matching mode and preserve the return path to this protocol:

| Request shape | Mode | Lifecycle result |
| --- | --- | --- |
| Current state or next action | Orient | Explain or resume an existing workstream |
| Time-horizon selection | Plan | Retained daily or workstream coordination |
| Prior state, history, or root cause | Investigate | Evidence-backed conclusion or promoted record |
| Uncertain feature or behavior | Design | Approved prospective specification when warranted |
| Approved bounded change | Implement | Evidence and handoff for the owning workstream |
| Quality, risk, or readiness assessment | Review | Findings and disposition |
| Close gaps and improve durable memory | Consolidate | Reconciled project truth and promoted knowledge |
| Integration, release, deployment, or observation | Deliver | Evidence-backed delivery state |
| Uncommitted possibility | Capture | Inbox retention without a commitment |

Scale the expected and actual blast radius to risk: trivial work normally needs no session; bounded work records affected areas and verification; substantial work records expected and actual impact plus unchecked areas; high-risk work additionally requires design review, rollout, rollback, approvals, and operational evidence.

Detailed mode rules, templates, tooling, and upstream-method routing will be added as this plugin is constructed. Until then, apply this protocol directly and leave no claim of validation, completion, or delivery unsupported by observed evidence.
