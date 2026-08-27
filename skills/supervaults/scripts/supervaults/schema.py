"""Canonical Supervaults frontmatter vocabulary."""

from types import MappingProxyType


TYPE_STATUSES = MappingProxyType(
    {
        "project": frozenset({"active", "blocked", "maintenance", "complete", "archived"}),
        "daily-plan": frozenset({"open", "reconciled"}),
        "workstream": frozenset(
            {"proposed", "ready", "active", "blocked", "parked", "complete", "superseded"}
        ),
        "work-session": frozenset({"active", "blocked", "verified", "complete"}),
        "idea": frozenset({"proposed", "parked", "promoted", "rejected", "superseded"}),
        "specification": frozenset({"draft", "approved", "superseded"}),
        "implementation-plan": frozenset(
            {"draft", "ready", "active", "complete", "superseded"}
        ),
        "decision": frozenset({"proposed", "accepted", "superseded"}),
        "investigation": frozenset({"active", "blocked", "complete", "superseded"}),
        "review": frozenset({"active", "complete", "superseded"}),
        "incident": frozenset({"active", "mitigated", "resolved", "superseded"}),
        "knowledge": frozenset({"current", "superseded"}),
        "release": frozenset({"planned", "released", "superseded"}),
        "template": frozenset({"template"}),
    }
)

WORKSTREAM_STAGES = frozenset(
    {
        "discovery",
        "design",
        "planning",
        "implementation",
        "verification",
        "review",
        "integration",
        "release",
        "deployment",
        "observation",
        "maintenance",
    }
)

RELATIONSHIP_FIELDS = (
    "project",
    "workstream",
    "spec",
    "plan",
    "origin",
    "promoted_to",
    "previous_session",
    "current_session",
    "latest_session",
    "supersedes",
    "superseded_by",
)

IMPACT_SURFACES = (
    "User behavior",
    "API and contracts",
    "Data and migrations",
    "Configuration and environment",
    "Dependencies and licensing",
    "Security and privacy",
    "Performance and reliability",
    "Concurrency and recovery",
    "Observability",
    "Deployment and rollback",
    "Documentation",
    "Tests and tooling",
    "Downstream consumers",
)
