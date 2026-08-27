# Supervaults behavioral evaluation contract

Task 8 defines and validates this deterministic behavioral contract. It does **not** execute an LLM or an installed clean agent. Task 9 owns installed live clean-agent execution against these fixtures.

`cases.json` is the machine-readable source of truth. Each case fixes one fixture, one `expected_lifecycle_action`, a run-date policy, an approval/stop dialogue, a terminal expectation, mutation domains, and observable selectors. Its complete prerequisite is the matching entry in `fixtures/case-overlays.json`; the helper applies those checked-in actions after the base fixture. A plausible explanation or private reasoning is never evidence.

## Fixture and date resolution

The setup helper expands `{{RUN_DATE}}`, `{{PREVIOUS_DATE}}`, and `{{RUN_DATETIME}}` in fixture files. During a live run, choose the actual local run date and use that same date for setup, case-token resolution, vault operations, and validation. Do not substitute the former development date or score literal token text.

| Fixture | Deterministic state |
|---|---|
| `empty-project` | One committed `.gitignore`; no `docs/` tree, vault, source, or prior handoff. |
| `established-multi-session` | Two fixed commits, a valid project vault, active Inventory Application and Authentication workstreams, linked verified sessions, an approved Inventory specification, canonical `docs/records/` directories, and stable source files. Case overlays add the stated stale link, scanner evidence, review diff, or local fake audit when needed. |

## Scoring selectors

Resolve tokens before scoring. Each required artifact embeds its concrete selector; that exact selector also appears in `must`. Each forbidden artifact likewise appears in `must_not`.

| Selector kind | Mechanical/manual scoring method |
|---|---|
| `file` | Compare before/after file inventory. `exists`, `absent`, `updated`, and `unchanged` apply to the path or glob shown. |
| `property` / `status` | Parse flat YAML frontmatter and compare the named property or lifecycle value. |
| `link` | Parse Markdown/wiki links and verify the named source-to-target relation after token resolution. |
| `validator` / `test` | Run the exact command fresh; retain command, stdout, stderr, and exit code. |
| `git` | Compare `git status --short`, `git diff --name-only`, and commit/history evidence against the stated assertion. |
| `response` / `evidence-gap` | Save the final agent response; it must name the required finding or unavailable evidence without fabricating a result. |
| `external-mutation` | Compare the evaluator-owned audit source. Staging cases use only the overlay's checked-in `local-fake://staging` JSON audit; no real external system is contacted. |
| `no-copy` | `normalized-task-blocks-v1` parses canonical `Task` heading blocks, normalizes heading level and file paths, then compares heading-plus-body structure across notes under `forbidden_paths`. Named links alone do not match; copied task prose does. |

Mutation domains are scored separately from artifact output:

- `product_source_tree: unchanged` means no source-tree path changes; it does not prohibit the explicitly permitted vault evidence.
- `vault: unchanged` means no vault path changes; these cases require response-only results.
- `vault: evidence-only` permits only the records/session/link changes named by `must`; `may-change` permits the bounded creation described by the case.
- `external: none` forbids every external write; `fake-audit:staging` permits one event only in the local fake audit file, never a real deployment.

## Broad-prompt terminal matrix

Every broad prompt has one empty and one established fixture. Follow its complete `gate_script` in order, including each user response, then score its exact `terminal_expectation`.

| Prompt | Empty case terminal | Established case terminal |
|---|---|---|
| Create a small inventory application. | `inventory-empty-design`: approved linked specification, then stop. | `inventory-established-new-outcome`: distinct approved mobile-app specification, then stop. |
| How about barcode scanning? | `barcode-empty-capture`: proposed idea only. | `barcode-established-extend`: extended canonical contract, no implementation. Its first clarification receives the complete checked-in barcode constraint packet; at most one later clarification receives the conservative browser-local fallback before the evaluator stops. |
| Let's add exports. | `exports-empty-capture`: proposed idea only. | `exports-established-extend`: extended canonical contract, no duplicate owner. Its first clarification receives the complete CSV constraint packet; at most one later clarification receives the conservative browser-local fallback before the evaluator stops. |
| Continue where we stopped. | `continue-empty-orient`: response-only missing-handoff gap. | `continue-established-resume`: linked successor evidence session after the approved focused check. |
| What happened with authentication? | `auth-empty-investigate`: response-only absent-history gap. | `auth-established-investigate-read-only`: response-only reconstruction, no durable record. |
| Plan today. | `plan-empty-daily`: dated discovery daily plan only. | `plan-established-daily-links`: dated plan linked to Inventory Application. |
| Consolidate recent work. | `consolidate-empty-no-invention`: response-only no-work gap. | `consolidate-established-small-corrections`: named vault correction and knowledge record only. |
| Ship it to staging. | `staging-empty-evidence-gap`: response-only missing-precondition gap. | `staging-established-authorized-only`: one local fake-audit staging record/event, no production or real deployment. |

## Conflict boundaries

| Case | Contract boundary |
|---|---|
| `superpowers-contract-linking` | A canonical plan is linked from the workstream; `no-copy` scans workstreams, daily notes, and work sessions for copied task headings/prose. |
| `authoritative-workstream-reuse` | The preinspected Inventory Application owner is extended; Barcode Import cannot be created. |
| `minor-debugging-stays-session` | The local root cause stays in named session evidence; no promoted `docs/records/investigations/` note. |
| `reusable-root-cause-promotion` | A reusable root cause is promoted to `docs/records/investigations/` with source-session provenance. |
| `read-only-review` | Findings are response-only; product source, vault, forge, and `docs/records/reviews/` are unchanged. |
| `consolidation-small-scope` | Only named vault link corrections occur; source, design, plans, and new sessions are excluded. |
| `optional-connector-evidence-gap` | Missing deployment access produces an explicit response gap, never an observed/released claim. |
| `staging-is-not-production` | One local fake-audit staging event is authorized; production audit events, production claims, and real deployment fail the case. |

## Pass/fail rule

Pass only when all `must` selectors match, all `must_not` selectors remain true, the scripted gates and terminal expectation were followed, and all mutation domains match. A missing fixture/audit source is inconclusive only when the case itself permits an evidence gap; fabricated state, a copied plan, an unsupported lifecycle action, or an unauthorized external write is a failure.
