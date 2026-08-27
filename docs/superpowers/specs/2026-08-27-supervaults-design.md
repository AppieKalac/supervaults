# Supervaults Design

**Date:** 2026-08-27  
**Status:** Approved in conversation; awaiting written-spec review

## Purpose

Supervaults is an opinionated development-workflow skill that combines the engineering discipline of Superpowers with an Obsidian-native, repository-local project memory. It helps a developer plan, design, implement, investigate, review, deliver, and consolidate work across many coding sessions without creating a second competing source of truth.

The vault must answer five questions quickly:

1. What am I working on?
2. What happened recently?
3. What should happen next?
4. Why was this choice made?
5. Where is the supporting evidence?

Superpowers owns the engineering method. Git, tests, CI, issue trackers, release systems, deployment platforms, and observability systems remain authoritative for their respective state. Supervaults owns lifecycle routing, continuity, provenance, evidence summaries, blast-radius reconciliation, and progressive aggregation into current project truth.

## Design principles

- Organize the vault around projects, workstreams, and time—not around a catalog of document types.
- Enter through the project, navigate through active work, descend into detailed evidence, and promote only durable information outward.
- Create the fewest artifacts that accurately represent the work.
- Keep prospective contracts separate from observed execution.
- Preserve detail at the session level and compress current truth upward.
- Treat links as typed relationships, not graph decoration.
- Keep delivery states distinct and evidence-backed.
- Work offline with Markdown and Git; enrich the workflow when optional tools are available.
- Never store secrets, credentials, raw log dumps, or private chain-of-thought in the vault.

The core information flow is:

```text
Detail flows downward.
Current truth flows upward by compression.
Durable discoveries are promoted sideways by reference.
```

## Architecture

Supervaults uses an evidence graph with bounded session journals. It has four information layers:

| Layer | Purpose | Principal artifacts |
|---|---|---|
| Contract | Agreed behavior and intended engineering method | Ideas, Superpowers specifications, Superpowers implementation plans |
| Coordination | Current project and workstream state | `Home.md`, retained daily plans, workstream overviews |
| Evidence | What actually occurred | Sessions, verification, debugging, reviews, incidents |
| Durable truth | Reusable rationale and implemented system knowledge | Decisions, knowledge, releases |

A complete lifecycle is:

```text
Discuss
  → Preinspect related work
  → Define the outcome
  → Record expected blast radius
  → Use the applicable Superpowers phase
  → Preserve execution evidence
  → Compare expected and actual blast radius
  → Extract durable knowledge
  → Reconcile current project truth
```

The plugin has one visible skill, `$supervaults`. Selected upstream Superpowers and Obsidian skill modules are vendored unchanged at pinned commits and used as internal methods. Supervaults supplies the orchestration and lifecycle contract; it does not rewrite upstream instructions or expose a second competing command surface.

## Development lifecycle

Supervaults supports the complete development loop:

```text
Intake → Discover → Route → Contract → Coordinate → Execute → Verify
       → Review → Integrate → Release → Deploy → Observe → Consolidate
```

The lifecycle is non-linear. Investigation may return work to design; review may return it to implementation; observation may create maintenance or incident work.

Every workstream has separate `stage` and `status` properties.

Allowed stages are:

- `discovery`
- `design`
- `planning`
- `implementation`
- `verification`
- `review`
- `integration`
- `release`
- `deployment`
- `observation`
- `maintenance`

Allowed workstream statuses are:

- `proposed`
- `ready`
- `active`
- `blocked`
- `parked`
- `complete`
- `superseded`

The workstream is the canonical owner of current outcome state. A workstream is complete only at the terminal stage defined by the project. The skill must not equate these states:

```text
implemented ≠ verified ≠ reviewed ≠ merged ≠ released ≠ deployed ≠ observed
```

Deployment and observation are optional for projects that do not ship a running system. When they apply, delivery continues through production observation rather than stopping at merge or release.

## Vault structure and navigation

The recommended repository-local project vault is:

```text
docs/
├── Home.md
├── daily/
│   └── YYYY-MM-DD.md
├── workstreams/
│   ├── <workstream>/
│   │   ├── <Workstream>.md
│   │   └── sessions/
│   │       └── YYYY-MM-DD-HHmm-<outcome>.md
│   └── archive/
├── superpowers/
│   ├── specs/
│   └── plans/
├── records/
│   ├── decisions/
│   ├── investigations/
│   ├── reviews/
│   ├── incidents/
│   └── releases/
├── knowledge/
├── inbox/
├── views/
└── templates/
```

Navigation begins with `Home.md`, which shows today's plan, active workstreams, project health, major blockers, and important current knowledge. A daily plan selects workstreams for a particular day. A workstream links its current state, next action, specification, implementation plan, chronological sessions, durable records, and delivery state. A session contains the detailed record of what actually happened.

The `records/` directory is a promoted durable-reference library, not the normal entry point. Most observations, minor choices, debugging steps, and review notes remain in the relevant session unless they cross a promotion threshold.

The `inbox/` directory holds unresolved possibilities that deserve retention but are not commitments. When selected, an inbox idea becomes or joins a workstream. The idea remains as provenance when useful; the workstream becomes the active coordination surface.

Superpowers specifications and plans retain their conventional paths. They appear inside the workstream through intentional named links and do not form a separate navigation system.

## Artifact model

### Core artifacts

- **Project home:** project-level phase, health, active workstreams, major blockers, and global next actions.
- **Daily plan:** deliberate selection and reconciliation of today's outcomes.
- **Workstream:** aggregated current state for one outcome across sessions.
- **Work session:** bounded observed work, evidence, deviations, and handoff.
- **Specification:** an approved behavior and design contract when design agreement is warranted.
- **Implementation plan:** the intended technical sequence when execution is multi-step, risky, cross-component, or likely to span sessions.

### Conditional artifacts and promotion thresholds

- **Idea:** an unresolved possibility worth revisiting outside the current session.
- **Decision:** a choice has meaningful alternatives or reversal cost.
- **Investigation:** a diagnosis or reconstruction will be reused independently.
- **Review:** findings and their dispositions must be tracked beyond the session.
- **Incident:** operational impact and response require a separate history.
- **Knowledge:** an implemented or freshly verified fact represents stable current system truth.
- **Release:** a meaningful delivered milestone needs a durable record.

External issues, pull requests, CI runs, deployments, dashboards, and incidents remain references unless a local durable record is needed for project continuity.

### Common properties

Artifacts use ordinary Markdown with flat YAML frontmatter. Common properties include:

- `type`
- `stage`
- `status`
- `project`
- `workstream`
- `spec`
- `plan`
- `area`
- `components`
- `affected_surfaces`
- `repository`
- `branch`
- `base_commit`
- `end_commit`
- `external_refs`
- `environments`
- `risk`
- `created`
- `updated`
- `aliases`

Canonical `type` values are `project`, `daily-plan`, `workstream`, `work-session`, `idea`, `specification`, `implementation-plan`, `decision`, `investigation`, `review`, `incident`, `knowledge`, `release`, and `template`.

Status vocabularies are deliberately artifact-specific:

| Artifact | Allowed statuses |
|---|---|
| Project | `active`, `blocked`, `maintenance`, `complete`, `archived` |
| Daily plan | `open`, `reconciled` |
| Workstream | `proposed`, `ready`, `active`, `blocked`, `parked`, `complete`, `superseded` |
| Work session | `active`, `blocked`, `verified`, `complete` |
| Idea | `proposed`, `parked`, `promoted`, `rejected`, `superseded` |
| Specification | `draft`, `approved`, `superseded` |
| Implementation plan | `draft`, `ready`, `active`, `complete`, `superseded` |
| Decision | `proposed`, `accepted`, `superseded` |
| Investigation | `active`, `blocked`, `complete`, `superseded` |
| Review | `active`, `complete`, `superseded` |
| Incident | `active`, `mitigated`, `resolved`, `superseded` |
| Knowledge | `current`, `superseded` |
| Release | `planned`, `released`, `superseded` |
| Template | `template` |

The validator applies `stage` only where a lifecycle stage is meaningful, primarily workstreams and sessions. A status describes observable state and must not be used as an informal progress estimate.

Important named relationship properties include:

- `project`
- `workstream`
- `spec`
- `plan`
- `origin`
- `promoted_to`
- `previous_session`
- `current_session`
- `latest_session`
- `supersedes`
- `superseded_by`

Backlinks aid discovery but never substitute for an intentional ownership, continuity, promotion, replacement, contract, or provenance link. Body links may represent evidence collections when their relationship is explained in context.

## Session lifecycle

Each independent execution ownership boundary uses one uniquely named session note:

```text
opened
  → context inspected
  → bounded outcome recorded
  → expected blast radius recorded
  → work performed
  → actual blast radius recorded
  → evidence recorded
  → handoff written
  → archived
```

A new agent or handed-off run creates a new session and links `previous_session`. During parallel work, each worker owns a unique session. The coordinator alone updates shared workstream and project overviews. Workers contribute proposed roll-ups containing actual changes, evidence, deviations, risks, recommended state transitions, and the exact next action.

Sessions record meaningful change sets, not every edit or transient thought. A trivial typo, formatting-only change, or explanation does not require a session unless the user asks.

## Risk-scaled blast radius

Blast-radius recording scales with risk:

| Risk | Required treatment |
|---|---|
| Trivial | No session required unless durable context would otherwise be lost |
| Bounded | Concise affected areas and verification |
| Substantial | Expected and actual impact matrix plus explicit unchecked areas |
| High | Full matrix, design review, rollout, rollback, approvals, and operational evidence |

Standard impact surfaces are:

- User behavior
- API and contracts
- Data and migrations
- Configuration and environment
- Dependencies and licensing
- Security and privacy
- Performance and reliability
- Concurrency and recovery
- Observability
- Deployment and rollback
- Documentation
- Tests and tooling
- Downstream consumers

Each relevant surface may be marked `changed`, `unchanged`, `not-applicable`, `unknown`, or `not-checked`. Actual impact is reconciled against expected impact before closure. Evidence identifies time, version or commit, environment, check, scope, and result.

## Planning module

Supervaults distinguishes four planning levels:

| Level | Question | Canonical location |
|---|---|---|
| Project direction | What outcomes matter and in what order? | `Home.md`, optionally `Roadmap.md` |
| Workstream planning | What is the current outcome, state, and next milestone? | Workstream overview |
| Engineering planning | How will an approved design be implemented? | `superpowers/plans/` |
| Daily planning | What will be deliberately advanced today? | `daily/YYYY-MM-DD.md` |

These layers link to each other without repeating each other.

### Planning today

`$supervaults plan today` inspects:

- The previous daily plan and unfinished selections
- Active, ready, and blocked workstreams
- Recent session handoffs
- Current Git state
- Review and verification gaps
- Implemented work awaiting integration or delivery
- External issues, pull requests, CI, or calendar constraints when available
- New inbox ideas, without turning them automatically into commitments

The planner recommends work using continuity, delivery gaps, unblocking value, risk, user value, urgency, dependencies, available focus, access constraints, and staleness. It explains the recommendation and leaves selection to the developer.

A healthy default is one primary outcome, one optional secondary outcome, small maintenance items, known constraints, and an explicit `Not today` section. The daily plan records outcome-level commitments and finish conditions. It links to the workstream and implementation plan rather than copying technical plan steps.

The daily planning lifecycle is:

```text
Candidates → Selection → Finish conditions → Sessions → Interruptions
           → Reconciliation → Finish, block, defer, drop, or reselect
```

The planner must not silently roll unfinished work into tomorrow. End-of-day reconciliation classifies it as finished, advanced but unfinished, blocked, deliberately deferred, dropped, or still active, and records the first likely action for the next session without creating a future commitment prematurely.

Meaningful replanning records what arrived, why it displaced or did not displace selected work, the affected outcome, and whether the change is temporary or a genuine priority change.

Native Obsidian views expose open plans, today's selected workstreams, repeatedly deferred work, stale active work, delivery gaps, and blockers grouped by dependency.

## Operating modes

The single `$supervaults` skill accepts concise or natural-language intents:

| Mode | Purpose | Example |
|---|---|---|
| Orient | Explain current state and likely next action | `$supervaults where are we?` |
| Plan | Select and retain work for a time horizon | `$supervaults plan today` |
| Investigate | Reconstruct history, state, or cause | `$supervaults investigate recent authentication work` |
| Design | Develop an idea into an approved specification | `$supervaults design account recovery` |
| Implement | Execute an approved contract | `$supervaults implement the approved plan` |
| Review | Assess code, behavior, risk, or readiness | `$supervaults review recent authentication changes` |
| Consolidate | Audit work, close gaps, and improve durable memory | `$supervaults consolidate recent work` |
| Deliver | Move verified work through delivery and observation | `$supervaults deliver the authentication refresh` |
| Capture | Retain an idea without committing to it | `$supervaults capture an idea about offline login` |

Natural requests such as “How about barcode scanning?” or “Let's add exports” are supported. Supervaults infers the likely mode, performs focused preinspection, and asks when the request could reasonably represent different lifecycle actions.

### Universal entry protocol

Every substantial mode:

1. Resolves the project and vault.
2. Identifies the relevant workstream or lifecycle candidates.
3. Inspects current state, contracts, recent sessions, and external references.
4. Checks repository state when relevant.
5. Selects `resume`, `extend`, `promote`, `implement`, `supersede`, `merge`, `create-new`, or `reference-only`.
6. States the bounded outcome and expected blast radius before material changes.

### Mode-specific rules

- **Plan** coordinates outcomes and finish conditions without copying implementation tasks.
- **Investigate** is read-only by default and distinguishes verified facts, historical claims, current inferences, conflicts, and unknowns. It creates a standalone record only when promotion is justified.
- **Design** invokes the applicable Superpowers design method and then returns to the vault lifecycle to link provenance and reconcile state.
- **Implement** requires approved contracts when risk and complexity warrant them. Superpowers owns execution method; Supervaults owns continuity, actual impact, evidence, and handoff.
- **Review** creates a separate review record only when findings require independent tracking.
- **Consolidate** compares plans, sessions, commits, reviews, and delivery evidence; corrects small in-scope gaps; promotes durable findings; and routes new behavior back through design.
- **Deliver** keeps integration, release, deployment, and observation separate and evidence-backed.
- **Capture** preserves a possibility in the inbox without treating it as planned work.

## External-tool integration contract

The core works with a filesystem, Markdown, and Git when the project is a Git repository. Other integrations are optional capability adapters.

| System | Authoritative state | Vault retention |
|---|---|---|
| Git | Files, commits, branches, worktrees | Commit IDs, branch, change summary, provenance |
| GitHub/GitLab/Azure DevOps | Issues, pull requests, reviews | Links, IDs, state snapshots, conclusions |
| Jira/Linear/Asana | Team backlog and assignment | Linked workstream, relevant status, contextual decisions |
| CI | Machine verification | Run link, commit or version, check, result |
| Package managers | Resolved dependencies and lockfiles | Meaningful dependency decision or risk |
| Release systems | Published versions | Release ID, included outcomes, evidence |
| Deployment platforms | Environment state | Deployment ID, version, environment, result |
| Observability tools | Runtime evidence | Time window, query or dashboard link, conclusion |
| Incident systems | Operational coordination | Incident link, impact, resolution, learning |

The vault does not copy full issue descriptions, CI logs, pull-request discussions, or monitoring output. It stores the relationship and conclusion required for future understanding.

Optional integrations degrade gracefully. Missing access may prevent a delivery claim when required evidence cannot be inspected, but it does not block local planning or implementation.

Reading available context is part of preinspection. External writes require user authorization scoped to the named system and action. Reviewing a pull request does not authorize merging it; preparing a release does not authorize publication; staging deployment does not authorize production deployment.

## Quality gates

### Entry gate

Resolve the repository and vault, inspect the relevant lifecycle neighborhood, and choose the lifecycle routing action.

### Scope gate

Record the bounded outcome, proportionate expected blast radius, and explicit exclusions before material mutation.

### Engineering gate

Route design uncertainty through Superpowers brainstorming and approved multi-step work through Superpowers planning. Keep contracts prospective.

### Evidence gate

Record actual changed surfaces, exact checks, environment, version or commit, concise results, and important checks not run.

### Closure gate

Write the handoff, reconcile the workstream, update `Home.md` only when project-level truth changed, and archive only after evidence and handoff are complete.

### Delivery gate

Require evidence for each claimed transition through verification, review, merge, release, deployment, and observation.

### Consolidation gate

Detect drift, missing links, stale statuses, unpromoted durable findings, and delivery gaps. Permit small corrections within approved scope and route material new behavior through design.

## Validation

A cross-platform, standard-library validator checks:

- Plugin manifest and skill metadata
- Required bundled references
- Pinned upstream versions and file hashes
- Valid artifact types, stages, and statuses
- Required named relationships
- Broken or ambiguous lifecycle links
- Dangling `current_session` values
- Archived sessions missing evidence or handoff
- Completed workstreams without completion evidence
- Open daily plans that were never reconciled
- Delivery claims lacking environment or version evidence
- Overviews that are stale relative to newer sessions
- Duplicate canonical workstreams or contracts

Results are classified as errors, warnings, or notices. Errors mean lifecycle integrity is broken. Warnings identify likely drift or missing quality. Notices are optional improvements. Passing vault validation never replaces project code tests.

## Plugin composition and upstream management

The repository layout is:

```text
supervaults/
├── .codex-plugin/plugin.json
├── skills/supervaults/
│   ├── SKILL.md
│   ├── references/
│   ├── templates/
│   └── scripts/
├── vendor/
│   ├── superpowers/
│   └── obsidian-skills/
├── tests/
├── upstream-lock.json
├── THIRD_PARTY_NOTICES.md
└── README.md
```

The initial bundle imports these upstream Superpowers modules:

- `brainstorming`
- `dispatching-parallel-agents`
- `executing-plans`
- `finishing-a-development-branch`
- `receiving-code-review`
- `requesting-code-review`
- `subagent-driven-development`
- `systematic-debugging`
- `test-driven-development`
- `using-git-worktrees`
- `using-superpowers`
- `verification-before-completion`
- `writing-plans`

It imports these Obsidian modules:

- `obsidian-markdown`
- `obsidian-bases`
- `json-canvas`
- `obsidian-cli`

`obsidian-cli` is an optional live-application enhancement; the Markdown and Bases workflow must work without a running Obsidian application. `defuddle` and Superpowers' `writing-skills` are excluded because web-content extraction and authoring new skills are not part of the project's runtime development lifecycle.

Imported files remain unchanged. `upstream-lock.json` records repository, exact commit, selected paths, and hashes. `THIRD_PARTY_NOTICES.md` preserves MIT attribution. Vendored modules are stored outside the plugin's registered `skills/` directory, so `$supervaults` is the only user-visible skill supplied by this plugin.

An update tool fetches upstream sources into a temporary location, verifies origin and commit, shows the diff, updates only explicitly selected modules, refreshes hashes and attribution, and requires review before acceptance. Updates never happen implicitly during ordinary skill use.

Core automation uses Python 3 and its standard library so validation, initialization, context discovery, session closure, and upstream-integrity checks behave consistently on Windows, macOS, and Linux. Each automated action exposes a clear manual Markdown fallback. Live Obsidian CLI behavior is optional; the core workflow operates directly on Markdown.

## Testing strategy

### Static and integrity tests

- Validate plugin and skill manifests.
- Validate all internal references and templates.
- Verify vendored files against pinned hashes.
- Verify imported upstream files were not modified.
- Test validators against valid and deliberately invalid fixture vaults.

### Behavioral activation tests

Exercise broad prompts rather than only exact commands:

- “Create a small inventory application.”
- “How about barcode scanning?”
- “Let's add exports.”
- “Continue where we stopped.”
- “What happened with authentication?”
- “Plan today.”
- “Consolidate recent work.”
- “Ship it to staging.”

Tests verify implicit activation, focused preinspection, correct lifecycle routing, tandem Superpowers/vault checkpoints, and the absence of duplicate contracts.

### Multi-session workflow tests

A throwaway project is developed across multiple fresh-agent sessions using deliberately broad prompts. The suite checks:

- Workstream-centered navigation
- Unique session ownership and correct handoffs
- Reuse rather than duplicate creation
- Correct promotion of decisions, investigations, reviews, and knowledge
- Accurate expected-versus-actual impact
- Evidence-backed stage transitions
- Clean daily planning and reconciliation
- Correct coordinator roll-ups during parallel work
- Vault comprehensibility after repeated sessions

### Integration and safety tests

- Verify graceful operation without optional tools.
- Test normalized external references and evidence conclusions.
- Verify external mutations require appropriate user authorization.
- Confirm that unavailable delivery evidence prevents unsupported completion claims.
- Confirm secrets and raw logs are not retained.

### Acceptance criteria

Supervaults is acceptable when a fresh agent or developer can open a mature project vault and, without reading every session, determine:

- The project's current health and direction
- Active workstreams and their exact next actions
- Today's deliberate commitments
- The canonical specification and implementation plan for each active outcome
- What was changed, where, by whom, and at which commit or environment
- What has and has not been verified
- Why important decisions were made
- Which delivery stages remain
- Where detailed supporting evidence lives

It must achieve this without duplicating external systems, turning every observation into a separate note, or allowing Superpowers documents to become a competing execution log.
