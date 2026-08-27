"""Deterministic dialogue-policy helpers for live evaluation."""

from __future__ import annotations

from typing import Any


def clarification_response(
    policy: dict[str, Any], turn_index: int, question: str
) -> str | None:
    """Return the bounded packet-policy reply without inspecting question wording."""

    if policy.get("mode") != "constraint-packet-then-fallback":
        raise ValueError("unsupported clarification policy mode")
    if turn_index < 0:
        raise ValueError("turn_index must be non-negative")
    if turn_index >= policy["max_turns"]:
        return None

    # The question is intentionally not classified. Packet policies are finite and
    # deterministic regardless of how an agent phrases a clarification.
    del question
    if turn_index == 0:
        return " ".join(
            clause["user_response"].strip()
            for clause in policy["constraint_packet"]
        )
    return policy["fallback_response"]
