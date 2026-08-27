# Architecture and ownership

Use Supervaults as a lifecycle overlay, not a replacement source of truth. Keep one user-visible skill, `$supervaults`; modules below `vendor/` are internal methods and never a second command surface.

## Evidence graph

Maintain four layers:

| Layer | Owns |
|---|---|
| Contract | Approved specifications and prospective implementation plans |
| Coordination | `Home.md`, retained daily plans, and current workstream overviews |
| Evidence | Bounded sessions, verification, debugging, reviews, and incidents |
| Durable truth | Promoted decisions, knowledge, and release records |

Let detail flow down into sessions, compress current truth upward into workstreams and `Home.md`, and promote durable discoveries sideways by intentional links. Do not turn specifications or plans into execution logs.

Navigate project → active workstream → session evidence. Treat the workstream as canonical owner of one outcome's current state and next action. Update `Home.md` only when project-level health, direction, blockers, or active work changes.

## Ownership boundaries

Create a unique session for each independent execution owner and link `previous_session`. In parallel or multi-agent work, workers edit only their owned session and work area. The coordinator alone updates shared workstream, daily, and project overviews. Require each worker roll-up to state actual changes, structured evidence, deviations, risks, recommended state transitions, and the exact next action.

Keep closed sessions in their workstream's `sessions/` directory. Archive only a complete workstream directory as one intact unit under `workstreams/archive/`.

Use ordinary Obsidian Markdown and intentional wikilinks as the core. Bases are native derived views, not stored truth. The workflow must continue to work offline without a running Obsidian application.

Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method. When that phase ends, explicitly return control to the Supervaults lifecycle to record observed results, reconcile ownership surfaces, validate, and hand off.
