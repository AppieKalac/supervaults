# Quality gates and evidence

Apply every relevant gate; scale detail with risk rather than omitting the gate.

## Gates

1. **Entry:** Resolve repository/vault, preinspect the lifecycle neighborhood, and choose one lifecycle action.
2. **Scope:** Before material mutation, record bounded outcome, exclusions, risk, and expected blast radius.
3. **Engineering:** Route design uncertainty through the vendored brainstorming method, multi-step planning through writing-plans, bugs through systematic debugging, and behavior changes through TDD.
4. **Evidence:** Record observed actual blast radius, exact checks, time, commit/version, environment, scope, concise result, and important checks not run.
5. **Closure:** Write the handoff, reconcile workstream and daily plan, update `Home.md` only for project-level truth, and close a session only after actual impact, evidence, and handoff are substantive.
6. **Delivery:** Require distinct evidence for verification, review, merge, release, deployment, and observation. Never infer a later transition from an earlier one.
7. **Consolidation:** Detect drift, broken/ambiguous links, stale statuses, duplicate owners/contracts, unpromoted durable findings, and delivery gaps. Route material new behavior back through Design.

## Blast radius

Use the canonical surfaces in `skills/supervaults/scripts/supervaults/schema.py`: user behavior; API/contracts; data/migrations; configuration/environment; dependencies/licensing; security/privacy; performance/reliability; concurrency/recovery; observability; deployment/rollback; documentation; tests/tooling; downstream consumers.

For each relevant surface record `changed`, `unchanged`, `not-applicable`, `unknown`, or `not-checked`, plus a substantive detail when required. Compare actual to expected and retain deviations; never rewrite the expectation after the fact.

The session template at `skills/supervaults/templates/vault/session.md.tmpl` is the structured evidence contract. Record actual impact in this canonical shape:

```text
Surface: <canonical impact surface>
State: <changed | unchanged | not-applicable | unknown | not-checked>
Detail: <substantive detail>
```

Record a concrete `Check` and one canonical `Result` form:

- `passed — <substantive detail>`
- `failed — <substantive detail>`
- `not-run — <reason>`
- `manual-check — <substantive observation>`

The parser also accepts its supported delimiter variants (`:`, `--`, `-`, or parenthesized detail), but use the forms above when authoring new evidence. Record handoff as `Current state: <substantive current state>` and `Next action: <exact next action>`.

A closable session needs:

- at least one canonical actual-impact surface with state and substantive detail (or justified `unchanged`);
- at least one concrete `Check` and allowed `Result` with version/commit/environment context as applicable; and
- substantive `Current state` and exact `Next action` handoff fields.

Blank or placeholder fields cannot pass closure. Replace every template prompt with observed content before calling `close-session`; examples shown in angle brackets are instructions, not evidence.

## Fresh verification

Before a claim of success, completion, fix, readiness, or delivery, read `../../vendor/superpowers/skills/verification-before-completion/SKILL.md` completely and follow it as authoritative. Run the command that proves the specific claim and inspect its fresh full output. Return control to Supervaults after verification to record evidence and unchecked areas, reconcile state, validate, and hand off.

Validate lifecycle integrity with:

`python -m skills.supervaults.scripts.supervaults validate --vault <vault> --json`

Errors mean lifecycle integrity is broken; warnings require reconciliation or an explicit retained explanation. Passing vault validation does not replace project tests, CI, review, external delivery evidence, or `python scripts/sync_upstreams.py --verify` when vendored integrity is in scope.

Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method. After its applicable phase, explicitly return control to Supervaults to preserve evidence, reconcile current truth, validate, and hand off.
