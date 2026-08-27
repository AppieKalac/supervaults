# Lifecycle routing

Own preinspection and lifecycle choice here. Do not choose a mode or create an artifact from the request wording alone.

## Resolve and preinspect

1. Resolve the repository root and vault. Prefer the repository's existing `Home.md`. If no vault exists in a new project where Supervaults applies, propose `docs/` as the resolved vault during clarification or design. Include that destination in the design gate; initialize only after it is the approved destination and before initialization of durable project artifacts. Without that approval, report the gap and do not initialize a vault.
2. Inspect `Home.md`, relevant active/ready/blocked workstreams, canonical `spec` and `plan` links, current/latest sessions, recent handoffs, today's and previous daily plan, inbox candidates, and durable records.
3. Inspect Git branch/commit/status and relevant project files. Read available issue, review, CI, delivery, or observability references when they affect the request.
4. Use the context helper for ranked candidates, not automatic selection:

   `python -m skills.supervaults.scripts.supervaults context --vault <vault> <terms...>`

5. Check for conflicting outcomes, duplicate contracts, stale state, and incomplete delivery before proposing new work.

For a genuinely new outcome, preserve the user's outcome noun phrase as the canonical display name unless the user explicitly approves a rename. Derive slugs mechanically from that phrase and reuse them for the workstream and contract paths. For example, “inventory application” becomes display name `Inventory Application` and slug `inventory-application`. Do not abbreviate `Application` to `App`, invent a product name, or let an implementation method silently rename lifecycle artifacts.

## Choose one lifecycle action

| Action | Meaning |
|---|---|
| `resume` | Continue the same bounded outcome from its handoff |
| `extend` | Add scope that remains inside the current approved contract |
| `promote` | Move a retained idea or session finding into a durable artifact/workstream |
| `implement` | Execute an existing approved contract |
| `supersede` | Replace an obsolete contract or current-truth artifact with explicit links |
| `merge` | Combine duplicate candidates under one canonical owner |
| `create-new` | Start a genuinely distinct outcome after ruling out reuse |
| `reference-only` | Retain or report context without changing lifecycle ownership |

Ask when evidence supports multiple actions with materially different consequences. Never silently reinterpret an idea as a commitment or duplicate an existing canonical workstream.

## Route the lifecycle

Keep `stage` and `status` separate. Stages describe the lifecycle neighborhood (`discovery` through `maintenance`); statuses describe observable artifact state. The canonical values live in `skills/supervaults/scripts/supervaults/schema.py`.

Before mutation, record the outcome, exclusions, risk, and expected blast radius. During execution, keep one owned session in this order:

```text
opened → context inspected → bounded outcome → expected blast radius
→ work performed → actual blast radius → evidence → handoff → closed
```

After an interruption, leave the current state and exact next action rather than an optimistic completion claim. Any vendored upstream file invoked from this reference must be read completely and remains authoritative for its engineering method. After any applicable vendored design, planning, execution, review, or verification phase, explicitly return control to Supervaults; capture its observed result in the session, reconcile the workstream and daily plan, validate, and hand off.
