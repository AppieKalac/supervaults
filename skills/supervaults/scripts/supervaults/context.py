"""Read-only discovery of relevant Supervaults artifacts."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import re
import subprocess
from typing import Sequence

from .markdown import Note, parse_note


_WIKI_LINK = re.compile(r"\[\[([^\]]+)\]\]")
_CODE_PATH = re.compile(r"(?:^|[ `])(?:[A-Za-z0-9_.-]+/)+[A-Za-z0-9_.-]+")


@dataclass(frozen=True)
class ContextCandidate:
    path: Path
    artifact_type: str
    status: str
    score: int
    reasons: Sequence[str]


@dataclass(frozen=True)
class ContextReport:
    project: Path
    candidates: Sequence[ContextCandidate]
    git_branch: str | None
    git_commit: str | None
    warnings: Sequence[str]


def _excerpt(text: str) -> str:
    normalized = " ".join(text.strip().split())
    return normalized[:240]


def _reason(prefix: str, evidence: str) -> str:
    """Keep the evidence portion of a reason bounded for JSON consumers."""

    return f"{prefix}{_excerpt(evidence)[: max(0, 240 - len(prefix))]}"


def _git_value(vault: Path, args: list[str]) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(vault), *args],
            capture_output=True, text=True, check=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def _linked_names(note: Note) -> set[str]:
    names: set[str] = set()
    for field in ("current_session", "latest_session"):
        value = note.properties.get(field)
        if isinstance(value, str):
            names.update(link.split("|", 1)[0].strip() for link in _WIKI_LINK.findall(value))
    return names


def _matches(text: str, terms: list[str]) -> list[str]:
    lowered = text.casefold()
    return [term for term in terms if term in lowered]


def _score_note(note: Note, terms: list[str], baseline: bool) -> tuple[int, list[str]]:
    if not terms:
        return (1, ["lifecycle context"] if baseline else [])

    score = 0
    reasons: list[str] = []
    stem_matches = _matches(note.path.stem, terms)
    if stem_matches:
        increment = 120 if note.properties.get("type") == "workstream" else 80
        score += increment * len(stem_matches)
        prefix = f"filename exact match ({', '.join(stem_matches)}): "
        reasons.append(_reason(prefix, note.path.name))

    for key, value in note.properties.items():
        rendered = ", ".join(str(item) for item in value) if isinstance(value, list) else str(value)
        matches = _matches(rendered, terms)
        if matches:
            score += 110 * len(matches)
            prefix = f"property {key} match ({', '.join(matches)}): "
            reasons.append(_reason(prefix, rendered))

    for line in note.body.splitlines():
        matches = _matches(line, terms)
        if not matches:
            continue
        if line.lstrip().startswith("#"):
            weight, kind = 60, "heading"
        elif _WIKI_LINK.search(line):
            weight, kind = 55, "wiki link"
        elif _CODE_PATH.search(line):
            weight, kind = 50, "code path"
        else:
            weight, kind = 25, "body"
        score += weight * len(matches)
        prefix = f"{kind} match ({', '.join(matches)}): "
        reasons.append(_reason(prefix, line))

    return score, reasons


def find_context(vault: Path, terms: list[str]) -> ContextReport:
    """Rank related notes without selecting or changing a lifecycle action."""

    vault = Path(vault)
    project = vault / "Home.md"
    normalized_terms = [term.casefold().strip() for term in terms if term.strip()]
    warnings: list[str] = []
    notes: list[Note] = []
    for path in sorted(vault.rglob("*.md"), key=lambda item: item.as_posix().casefold()):
        if ".obsidian" in path.parts:
            continue
        try:
            notes.append(parse_note(path))
        except (OSError, ValueError) as error:
            warnings.append(str(error))

    by_path = {note.path: note for note in notes}
    home = by_path.get(project)
    if home is None:
        warnings.append(f"{project}: project overview is missing or unreadable")
    active_workstreams = [
        note for note in notes
        if note.properties.get("type") == "workstream" and note.properties.get("status") == "active"
    ]
    session_names = {name for workstream in active_workstreams for name in _linked_names(workstream)}
    baseline_paths = {project, *(note.path for note in active_workstreams)}
    baseline_paths.update(note.path for note in notes if note.path.stem in session_names)

    candidates: list[ContextCandidate] = []
    for note in notes:
        score, reasons = _score_note(note, normalized_terms, note.path in baseline_paths)
        if not score and note.path not in baseline_paths:
            continue
        if not reasons:
            reasons = ["linked lifecycle context"]
            score = 1
        candidates.append(
            ContextCandidate(
                path=note.path,
                artifact_type=str(note.properties.get("type", "unknown")),
                status=str(note.properties.get("status", "unknown")),
                score=score,
                reasons=tuple(reasons),
            )
        )
    candidates.sort(key=lambda item: (-item.score, item.path.as_posix().casefold()))
    return ContextReport(
        project=project,
        candidates=tuple(candidates),
        git_branch=_git_value(vault, ["rev-parse", "--abbrev-ref", "HEAD"]),
        git_commit=_git_value(vault, ["rev-parse", "HEAD"]),
        warnings=tuple(warnings),
    )
