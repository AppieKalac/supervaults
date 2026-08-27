# Supervaults behavioral evaluation expectations

`cases.json` is the machine-readable source of truth. This file explains how a human evaluator should interpret its observable oracles. The JSON files are **not** an LLM runner: they define prompts, fixture contexts, and pass/fail assertions for a clean-agent run that is performed separately.

## Oracle vocabulary

Each `must` or `must_not` object has a `kind` and an `assertion`. Score only the files, frontmatter, named links, status values, Git evidence, validator/test output, or externally observable mutation named by that object. Do not infer a pass from a plausible explanation or hidden reasoning.

| Kind | Inspect |
|---|---|
| `file` | Presence, absence, or changed state at the supplied repository-relative path |
| `link` | A named Markdown/wiki relationship from the stated source to target |
| `property` / `status` | Parsed YAML frontmatter or an explicit lifecycle status transition |
| `validator` / `test` | Fresh command output and exit status retained with the run |
| `git` | `git status`, `git diff`, commit IDs, and session evidence that names them |
| `external-mutation` | Deployment/forge/tracker audit evidence; `no-event` means no observed write |
| `evidence-gap` | An explicit note of unavailable required evidence, connector, or prior state |

## Broad-prompt matrix

Every broad prompt has both an empty and established multi-session fixture. The empty fixture proves the agent does not invent continuity. The established fixture proves it can reuse evidence and canonical ownership.

| Prompt | Empty case | Established case | Observable distinction |
|---|---|---|---|
| Create a small inventory application. | `inventory-empty-design` | `inventory-established-new-outcome` | Creates a bounded contract only after vault setup; established context still creates a distinct owner only after preinspection rules out reuse. |
| How about barcode scanning? | `barcode-empty-capture` | `barcode-established-extend` | Captures an uncommitted possibility when context is absent; extends the canonical Inventory Application owner when the contract permits it. |
| Let's add exports. | `exports-empty-capture` | `exports-established-extend` | Does not turn a vague suggestion into implementation; uses a named existing contract link when it is an in-scope extension. |
| Continue where we stopped. | `continue-empty-orient` | `continue-established-resume` | Reports missing continuity without mutation; opens a linked successor session from an exact existing handoff. |
| What happened with authentication? | `auth-empty-investigate` | `auth-established-investigate-read-only` | Reports the evidence gap or reconstructs linked history without source changes, commits, or external writes. |
| Plan today. | `plan-empty-daily` | `plan-established-daily-links` | Creates/reuses a retained daily plan; established plan links selected owners rather than copying engineering tasks or promoting inbox items. |
| Consolidate recent work. | `consolidate-empty-no-invention` | `consolidate-established-small-corrections` | Makes no invented work on an empty repository; fixes only vault drift and promotes verified durable truth. |
| Ship it to staging. | `staging-empty-evidence-gap` | `staging-established-authorized-only` | Missing prerequisites yields an evidence gap; explicit staging authorization permits only a staging event and evidence record. |

## Boundary cases

| Case | Required observable result | Required absence |
|---|---|---|
| `superpowers-contract-linking` | One plan at `docs/superpowers/plans/` and a named `plan` link from the owner. | No copied plan below the workstream or alternate plans tree. |
| `authoritative-workstream-reuse` | Existing Inventory Application note updated with a new owned session and preinspection evidence. | No Barcode Import workstream. |
| `minor-debugging-stays-session` | Reproduction/root-cause evidence stays in the session and source remains unchanged. | No promoted investigation, decision, or knowledge record. |
| `reusable-root-cause-promotion` | A complete investigation links its source sessions and captures the reusable root cause. | No source mutation or implementation plan. |
| `read-only-review` | Findings/dispositions with provenance and reported checks. | No code mutation, commit, merge, or forge comment. |
| `consolidation-small-scope` | Only named link/metadata repairs and a passing validator. | No product source mutation, design, or plan. |
| `optional-connector-evidence-gap` | Explicit missing deployment-observation evidence and no lifecycle advancement to observed. | No invented deployment query/success claim. |
| `staging-is-not-production` | One staging deployment event, release environment evidence, version/commit, and rollback reference. | Production event or production deployment status. |

## Scoring rule

Mark a case pass only when every `must` oracle is observed and every `must_not` oracle remains absent. Mark it fail for an unsupported state transition, duplicate owner, copied contract, unauthorized external write, fabricated connector result, or any failed required command. Mark it inconclusive only when the fixture or audit source is unavailable; preserve that as a run-level evidence gap rather than converting it to a pass.
