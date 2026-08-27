# Supervaults

Supervaults is a Codex plugin for workstream-centered, repository-local development memory. It combines the engineering discipline of Superpowers with an Obsidian-native Markdown vault so a project can retain current state, decisions, evidence, and next actions across sessions.

## Status

Supervaults is under construction. This first release scaffold registers a single discoverable skill, `$supervaults`; vault tooling, templates, vendored upstream modules, and full orchestration references will follow in subsequent implementation tasks.

## Design and specification

- [Approved design](docs/superpowers/specs/2026-08-27-supervaults-design.md)
- [Implementation plan](docs/superpowers/plans/2026-08-27-supervaults.md)

## Intended use

Examples of the intended command surface:

```text
$supervaults where are we?
$supervaults plan today
$supervaults investigate recent authentication work
$supervaults design account recovery
$supervaults implement the approved plan
$supervaults review recent authentication changes
$supervaults consolidate recent work
$supervaults deliver the authentication refresh
$supervaults capture an idea about offline login
```

## Upstream attribution

Supervaults will vendor selected Superpowers and Obsidian modules at pinned upstream commits. Those files will remain unchanged and authoritative for their respective engineering and vault methods; Supervaults provides the lifecycle routing, evidence, reconciliation, and multi-session continuity around them. The final plugin will include a lock file and third-party notices for the exact imported sources.

## License

MIT. See [LICENSE](LICENSE).
