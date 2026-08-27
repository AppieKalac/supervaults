# Artifact model

Create the fewest artifacts that accurately preserve contract, coordination, evidence, and durable truth. Use `skills/supervaults/scripts/supervaults/schema.py` as the canonical type, status, stage, relationship, and impact vocabulary; use `skills/supervaults/templates/vault/` as the canonical body starting points.

## Core artifacts

Maintain `Home.md`, retained daily plans, workstream overviews, bounded work sessions, approved specifications when design agreement is warranted, and implementation plans when multi-step execution warrants one.

Use the matching templates:

- `Home.md.tmpl`, `daily.md.tmpl`, `workstream.md.tmpl`, and `session.md.tmpl` for coordination and evidence.
- `decision.md.tmpl`, `investigation.md.tmpl`, `review.md.tmpl`, `knowledge.md.tmpl`, and `release.md.tmpl` only after promotion.

Specifications and plans remain at their conventional `superpowers/specs/` and `superpowers/plans/` locations and are linked from the owning workstream.

## Promotion thresholds

Keep ordinary observations, small choices, debugging detail, and review notes in the session. Promote only when:

- an idea is worth revisiting without becoming a commitment;
- a decision has meaningful alternatives or reversal cost;
- an investigation will be reused independently;
- review findings/dispositions need independent tracking;
- operational impact requires an incident history;
- an implemented or freshly verified fact is stable current system truth; or
- a meaningful delivered milestone needs a release record.

External issues, pull requests, CI runs, deployments, dashboards, and incident systems remain references unless local continuity requires a durable conclusion.

## Links and lifecycle integrity

Use flat YAML frontmatter and intentional named relationships: `project`, `workstream`, `spec`, `plan`, `origin`, `promoted_to`, `previous_session`, `current_session`, `latest_session`, `supersedes`, and `superseded_by`. A backlink never substitutes for ownership, continuity, contract, promotion, provenance, or replacement.

Keep prospective expected impact in the contract/session entry and observed actual impact in the execution session. Do not overwrite history to make it match the plan. Supersede with explicit links. Do not move closed sessions independently; move the entire completed workstream only when archiving.

When editing notes, use the internal Obsidian Markdown method routed by [integrations](integrations.md). Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method. After any applicable vendored upstream design, planning, execution, review, or verification phase, explicitly return control to Supervaults to link or promote the artifact, reconcile current truth, validate, and hand off.
