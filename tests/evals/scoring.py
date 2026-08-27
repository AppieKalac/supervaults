"""Deterministic selector helpers for manual or mechanical evaluation scoring."""

from __future__ import annotations

from pathlib import Path
import re


_HEADING = re.compile(r"^(#{1,6})\s+(.+?)\s*$")
_PATH = re.compile(r"(?<![\w.-])(?:[\w.-]+/)+[\w.-]+")
_NON_ALPHANUMERIC = re.compile(r"[^a-z0-9]+")


def _normalized(value: str) -> str:
    value = _PATH.sub(" path ", value.casefold())
    return " ".join(_NON_ALPHANUMERIC.sub(" ", value).split())


def _task_blocks(markdown: str) -> set[str]:
    """Return normalized task-heading-and-content blocks regardless of heading level/path."""

    lines = markdown.splitlines()
    blocks: set[str] = set()
    for index, line in enumerate(lines):
        heading = _HEADING.match(line)
        if heading is None or not _normalized(heading.group(2)).startswith("task"):
            continue
        following: list[str] = []
        for candidate in lines[index + 1:]:
            if _HEADING.match(candidate):
                break
            following.append(candidate)
        blocks.add(_normalized("\n".join((heading.group(2), *following))))
    return blocks


def copied_plan_blocks(canonical_markdown: str, candidate_markdown: str) -> set[str]:
    """Find task blocks copied from a canonical plan into another note."""

    return _task_blocks(canonical_markdown) & _task_blocks(candidate_markdown)


def score_no_copy(canonical_path: Path, forbidden_paths: list[Path]) -> list[tuple[Path, set[str]]]:
    """Find normalized plan task copies under noncanonical note roots."""

    canonical_path = Path(canonical_path)
    canonical = canonical_path.read_text(encoding="utf-8")
    findings: list[tuple[Path, set[str]]] = []
    candidates = {
        path
        for root in forbidden_paths
        if root.exists()
        for path in root.rglob("*.md")
        if path != canonical_path
    }
    for path in sorted(candidates, key=lambda item: item.as_posix().casefold()):
        copies = copied_plan_blocks(canonical, path.read_text(encoding="utf-8"))
        if copies:
            findings.append((path, copies))
    return findings
