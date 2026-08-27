# Supervaults

Supervaults is a Codex plugin for workstream-centered, repository-local development memory. It combines the engineering discipline of Superpowers with an Obsidian-native Markdown vault so a project can retain current state, decisions, evidence, and next actions across sessions.

## Status

Supervaults is a single visible `$supervaults` skill backed by Markdown vault templates, a cross-platform Python helper/validator, and pinned internal Superpowers and Obsidian methods. Release candidate `0.1.0+codex.20260827161121` passes the 73-test automated suite, vendored-integrity checks, and plugin/vault validation.

Installed clean-agent tests passed implicit activation, empty-project design/spec creation, established-vault planning, and a barcode-scanning extension. The complete eight-session acceptance sequence remains incomplete: the exports session exposed an evaluator dialogue gap before any repository mutation. See [Testing](docs/testing.md) for the exact boundary.

## Design and specification

- [Approved design](docs/superpowers/specs/2026-08-27-supervaults-design.md)
- [Implementation plan](docs/superpowers/plans/2026-08-27-supervaults.md)
- [Testing and clean-agent protocol](docs/testing.md)
- [Behavioral evaluation expectations](tests/evals/expected-behaviors.md)

## Install and prerequisites

Install the plugin through Codex from this repository after the release-candidate branch is integrated into the repository's main worktree. The plugin requires Python 3.10+ and Git on `PATH`; its core helpers use only the Python standard library and ordinary Markdown, so they work on Windows, macOS, and Linux without a running Obsidian application.

Optional connectors (forge, CI, deployment, observability, and an Obsidian live-app CLI) enrich evidence but are never required for local planning or implementation. Their absence must be recorded as an evidence gap when it prevents a delivery or observation claim.

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

The skill resolves and preinspects the vault before choosing `resume`, `extend`, `promote`, `implement`, `supersede`, `merge`, `create-new`, or `reference-only`. It links contracts and plans to their workstream rather than copying them. Plain investigation and review are read-only; staging authorization does not authorize production deployment.

## Vault layout

```text
docs/
├── Home.md
├── daily/
├── workstreams/<slug>/
│   ├── <Outcome>.md
│   └── sessions/
├── superpowers/specs/
├── superpowers/plans/
├── knowledge/
└── records/
    ├── investigations/
    ├── reviews/
    └── releases/
```

`Home.md` holds project-level truth; a workstream owns the current outcome; sessions contain bounded observed evidence and handoffs. Specifications and implementation plans stay under `superpowers/` and are connected through named `spec` and `plan` links. Use the validator to check links, statuses, evidence-gated sessions, duplicate owners, delivery claims, and stale lifecycle metadata.

## Core commands

Run from the repository root. Use `python` on Windows when it resolves to Python 3, `py -3` if available, or `python3` on macOS/Linux.

```text
python -m skills.supervaults.scripts.supervaults init --vault docs --project "Project Name"
python -m skills.supervaults.scripts.supervaults context --vault docs authentication recovery
python -m skills.supervaults.scripts.supervaults plan-today --vault docs
python -m skills.supervaults.scripts.supervaults open-session --vault docs --workstream "docs/workstreams/account-recovery/Account Recovery.md" --outcome "verify recovery" --owner "agent-name"
python -m skills.supervaults.scripts.supervaults close-session --vault docs --session "docs/workstreams/account-recovery/sessions/2026-08-27-0930-verify-recovery.md" --end-commit abc1234
python -m skills.supervaults.scripts.supervaults validate --vault docs --json
```

Helpers automate deterministic Markdown mechanics only. They do not select lifecycle actions, replace preinspection, authorize external writes, or replace fresh project checks.

## Upstream attribution and update policy

Selected Superpowers and Obsidian modules are vendored at the pinned commits and hashes in [upstream-lock.json](upstream-lock.json). They remain byte-unchanged and authoritative for their engineering or vault methods; Supervaults adds lifecycle routing, evidence, reconciliation, and continuity around them. Attribution is retained in [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

Upstream updates are deliberate maintenance work only: review the selected source diff, update the lock and notices through `scripts/sync_upstreams.py`, run `python scripts/sync_upstreams.py --verify`, run the full test suite, and commit the update separately. Ordinary skill use never fetches or changes vendored upstream content.

## License

MIT. See [LICENSE](LICENSE).
