# Integrations and authority

The filesystem, Markdown, and Git are the offline core. Optional integrations enrich preinspection and evidence but never create a competing source of truth.

| System | Authoritative state | Retain locally |
|---|---|---|
| Git | Files, branches, commits, worktrees | IDs, branch, concise change/provenance summary |
| Forge / tracker | Issues, pull requests, review, assignment | Link/ID, relevant snapshot, conclusion |
| CI | Machine verification | Run link, commit/version, check, result |
| Package manager | Resolved dependencies and lockfiles | Meaningful decision, license, or risk |
| Release / deployment | Published version and environment state | ID, version, environment, result, rollback evidence |
| Observability / incidents | Runtime evidence and operational coordination | Time window, query/dashboard/incident link, conclusion |

Read available context during preinspection when it affects routing. Degrade gracefully when an adapter is absent. Missing optional access does not block local planning or implementation, but missing required evidence prevents the corresponding review, release, deployment, observation, or completion claim.

## External-write boundary

Treat reading and writing as separate authority. Before an external mutation, obtain user authorization scoped to the named system and action. Reviewing a pull request does not authorize merging; preparing a release does not authorize publication; staging a deployment does not authorize production deployment; reading a tracker does not authorize editing it. Never broaden an authorization through retries or adjacent actions.

Store links and bounded conclusions, not full issue descriptions, PR discussions, CI/monitoring output, secrets, credentials, or raw logs.

## Native Obsidian methods

Before invoking any module, read its vendored `SKILL.md` completely; it is authoritative for its format/tool method.

- For every vault note creation or Obsidian-specific edit, use `../../vendor/obsidian-skills/skills/obsidian-markdown/SKILL.md`. Load its focused property/embed/callout references only when needed.
- For `.base` derived lifecycle views, use `../../vendor/obsidian-skills/skills/obsidian-bases/SKILL.md`. Bases query canonical Markdown; they do not own status.
- Use `../../vendor/obsidian-skills/skills/json-canvas/SKILL.md` only when the user explicitly requests a visual project map. JSON Canvas is optional and never replaces named lifecycle links.
- Use `../../vendor/obsidian-skills/skills/obsidian-cli/SKILL.md` only when a running Obsidian application is available and live-app behavior is useful. The CLI is optional; do not require it for core reads, writes, search, or validation.

Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method. After any applicable vendored engineering or Obsidian phase, explicitly return control to Supervaults. Record only the relevant observed result/evidence, reconcile the owning workstream and project surfaces, validate the filesystem artifacts, and hand off.
