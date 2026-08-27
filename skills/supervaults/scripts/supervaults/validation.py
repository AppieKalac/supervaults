"""Deterministic lifecycle-integrity checks for a Supervaults Markdown vault."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from pathlib import Path
import re
from typing import Iterable

from .lifecycle import (
    _has_valid_actual_blast_radius,
    _has_valid_handoff,
    _has_valid_verification_evidence,
    _section_content,
)
from .markdown import Note, parse_note
from .schema import RELATIONSHIP_FIELDS, TYPE_STATUSES, WORKSTREAM_STAGES


_SKIPPED_DIRECTORIES = frozenset({".git", ".obsidian", "vendor", "__pycache__"})
_WIKI_LINK = re.compile(r"^\[\[([^\]|]+)(?:\|[^\]]+)?\]\]$")
_DELIVERY_CLAIM = re.compile(r"\b(?:deployed|released|in production)\b", re.IGNORECASE)
_NEGATED_DELIVERY_CLAIM = re.compile(r"\b(?:not|never|pending|planned|awaiting)\s+(?:deployed|released)\b", re.IGNORECASE)
_SEVERITY_ORDER = {"error": 0, "warning": 1, "notice": 2}


@dataclass(frozen=True)
class Finding:
    """One actionable lifecycle observation, retained in deterministic order."""

    code: str
    severity: str
    path: Path
    message: str


@dataclass(frozen=True)
class ValidationReport:
    """An immutable classified collection of validator findings."""

    findings: tuple[Finding, ...]

    @property
    def errors(self) -> tuple[Finding, ...]:
        return tuple(finding for finding in self.findings if finding.severity == "error")

    @property
    def warnings(self) -> tuple[Finding, ...]:
        return tuple(finding for finding in self.findings if finding.severity == "warning")

    @property
    def notices(self) -> tuple[Finding, ...]:
        return tuple(finding for finding in self.findings if finding.severity == "notice")


def _paths(vault: Path) -> list[Path]:
    return sorted(
        (
            path for path in vault.rglob("*.md")
            if not any(part.casefold() in _SKIPPED_DIRECTORIES for part in path.relative_to(vault).parts)
        ),
        key=lambda path: path.relative_to(vault).as_posix().casefold(),
    )


def _section(body: str, name: str) -> str:
    return _section_content(body, name)


def _substantive(value: str) -> bool:
    normalized = " ".join(value.split()).casefold()
    return bool(normalized and normalized not in {"tbd", "todo", "placeholder", "none", "n/a"})


def _link_values(value: object) -> tuple[str, ...] | None:
    values = value if isinstance(value, list) else [value]
    targets: list[str] = []
    for item in values:
        if not isinstance(item, str):
            return None
        match = _WIKI_LINK.fullmatch(item)
        if match is None:
            return None
        targets.append(match.group(1).strip())
    return tuple(targets)


def _normal_path(value: Path) -> str:
    return value.as_posix().casefold()


def _link_index(notes: Iterable[Note], vault: Path) -> tuple[dict[str, list[Path]], dict[str, list[Path]]]:
    by_stem: dict[str, list[Path]] = {}
    by_relative: dict[str, list[Path]] = {}
    for note in notes:
        by_stem.setdefault(note.path.stem.casefold(), []).append(note.path)
        relative = note.path.relative_to(vault).with_suffix("").as_posix().casefold()
        by_relative.setdefault(relative, []).append(note.path)
    return by_stem, by_relative


def _resolve_link(target: str, by_stem: dict[str, list[Path]], by_relative: dict[str, list[Path]]) -> list[Path]:
    normalized = target.replace("\\", "/").removesuffix(".md").strip("/").casefold()
    if "/" in normalized:
        return by_relative.get(normalized, [])
    return by_stem.get(normalized, [])


def _add(findings: list[Finding], code: str, severity: str, path: Path, message: str) -> None:
    findings.append(Finding(code, severity, path, message))


def _validate_metadata(note: Note, findings: list[Finding]) -> None:
    artifact_type = note.properties.get("type")
    if not isinstance(artifact_type, str) or artifact_type not in TYPE_STATUSES:
        _add(findings, "invalid-type", "error", note.path, "type must be a supported artifact type")
        return
    status = note.properties.get("status")
    if not isinstance(status, str) or status not in TYPE_STATUSES[artifact_type]:
        _add(
            findings,
            "invalid-status",
            "error",
            note.path,
            f"status must be valid for {artifact_type}",
        )
    stage = note.properties.get("stage")
    if artifact_type in {"workstream", "work-session"}:
        if artifact_type == "workstream" and (not isinstance(stage, str) or stage not in WORKSTREAM_STAGES):
            _add(findings, "invalid-stage", "error", note.path, "workstream stage must be a supported lifecycle stage")
        elif stage is not None and (not isinstance(stage, str) or stage not in WORKSTREAM_STAGES):
            _add(findings, "invalid-stage", "error", note.path, "session stage must be a supported lifecycle stage")
    elif stage is not None:
        _add(findings, "invalid-stage", "error", note.path, "stage applies only to workstreams and work sessions")


def _validate_required_relationships(note: Note, findings: list[Finding]) -> None:
    artifact_type = note.properties.get("type")
    if artifact_type in TYPE_STATUSES and artifact_type != "project" and "project" not in note.properties:
        _add(findings, "missing-relationship", "error", note.path, "artifact must link to its project")
    if artifact_type == "work-session" and "workstream" not in note.properties:
        _add(findings, "missing-relationship", "error", note.path, "work session must link to its workstream")


def _validate_links(
    note: Note,
    notes_by_path: dict[Path, Note],
    by_stem: dict[str, list[Path]],
    by_relative: dict[str, list[Path]],
    findings: list[Finding],
) -> None:
    for field in RELATIONSHIP_FIELDS:
        if field not in note.properties:
            continue
        targets = _link_values(note.properties[field])
        if targets is None:
            _add(findings, "invalid-relationship", "error", note.path, f"{field} must contain a wiki link")
            continue
        for target in targets:
            matches = _resolve_link(target, by_stem, by_relative)
            contract_link = field in {"spec", "plan"}
            if not matches:
                code = "broken-contract-link" if contract_link else "dangling-current-session" if field == "current_session" else "broken-wiki-link"
                _add(findings, code, "error", note.path, f"{field} target [[{target}]] does not exist")
                continue
            if len(matches) > 1:
                _add(findings, "ambiguous-wiki-link", "error", note.path, f"{field} target [[{target}]] is ambiguous")
                continue
            if field == "spec" and notes_by_path[matches[0]].properties.get("type") != "specification":
                _add(findings, "broken-contract-link", "error", note.path, f"spec target [[{target}]] is not a specification")
            if field == "plan" and notes_by_path[matches[0]].properties.get("type") != "implementation-plan":
                _add(findings, "broken-contract-link", "error", note.path, f"plan target [[{target}]] is not an implementation plan")


def _validate_closed_session(note: Note, findings: list[Finding]) -> None:
    if note.properties.get("type") != "work-session" or note.properties.get("status") not in {"verified", "complete"}:
        return
    if not _has_valid_actual_blast_radius(_section(note.body, "Actual blast radius")):
        _add(findings, "missing-actual-blast-radius", "error", note.path, "closed session lacks structured Actual blast radius")
    if not _has_valid_verification_evidence(_section(note.body, "Verification evidence")):
        _add(findings, "missing-verification-evidence", "error", note.path, "closed session lacks structured Verification evidence")
    if not _has_valid_handoff(_section(note.body, "Handoff")):
        _add(findings, "missing-handoff", "error", note.path, "closed session lacks structured Handoff")


def _validate_daily_plan(note: Note, today: date, findings: list[Finding]) -> None:
    if note.properties.get("type") != "daily-plan" or note.properties.get("status") != "open":
        return
    raw_day = note.properties.get("date")
    try:
        planned_day = date.fromisoformat(raw_day) if isinstance(raw_day, str) else None
    except ValueError:
        planned_day = None
    if planned_day is None:
        _add(findings, "invalid-date", "error", note.path, "daily plan date must be ISO-8601")
    elif planned_day < today:
        _add(findings, "stale-daily-plan", "error", note.path, "open daily plan predates today and needs reconciliation")
    else:
        _add(findings, "unreconciled-daily-plan", "warning", note.path, "open daily plan has not yet been reconciled")


def _resolved_single_link(note: Note, field: str, by_stem: dict[str, list[Path]], by_relative: dict[str, list[Path]]) -> Path | None:
    targets = _link_values(note.properties.get(field))
    if targets is None or len(targets) != 1:
        return None
    matches = _resolve_link(targets[0], by_stem, by_relative)
    return matches[0] if len(matches) == 1 else None


def _validate_workstream_evidence(
    note: Note,
    notes_by_path: dict[Path, Note],
    by_stem: dict[str, list[Path]],
    by_relative: dict[str, list[Path]],
    findings: list[Finding],
) -> None:
    if note.properties.get("type") != "workstream" or note.properties.get("status") != "complete":
        return
    latest = _resolved_single_link(note, "latest_session", by_stem, by_relative)
    latest_note = notes_by_path.get(latest) if latest is not None else None
    session_is_evidenced = bool(
        latest_note
        and latest_note.properties.get("type") == "work-session"
        and latest_note.properties.get("status") in {"verified", "complete"}
        and _has_valid_verification_evidence(_section(latest_note.body, "Verification evidence"))
    )
    if not _substantive(_section(note.body, "Completed")) or not session_is_evidenced:
        _add(findings, "missing-completion-evidence", "error", note.path, "complete workstream needs a completed summary and evidenced latest session")


def _delivery_has_evidence(note: Note) -> bool:
    environment = note.properties.get("environments")
    has_environment = bool(environment if isinstance(environment, list) else isinstance(environment, str) and environment.strip())
    version_fields = ("version", "release_version", "deployment_version", "end_commit")
    has_version = any(isinstance(note.properties.get(field), str) and note.properties[field].strip() for field in version_fields)
    return has_environment and has_version


def _validate_delivery_state(note: Note, findings: list[Finding]) -> None:
    delivery = _section(note.body, "Delivery state")
    if not _DELIVERY_CLAIM.search(delivery) or _NEGATED_DELIVERY_CLAIM.search(delivery):
        return
    if not _delivery_has_evidence(note):
        _add(findings, "unsupported-delivery-state", "error", note.path, "deployed or released state needs environment and version evidence")


def _validate_overview_freshness(
    notes: list[Note],
    by_stem: dict[str, list[Path]],
    by_relative: dict[str, list[Path]],
    findings: list[Finding],
) -> None:
    closed_sessions: dict[str, list[Note]] = {}
    for note in notes:
        if note.properties.get("type") != "work-session" or note.properties.get("status") not in {"verified", "complete"}:
            continue
        target = _resolved_single_link(note, "workstream", by_stem, by_relative)
        if target is not None:
            closed_sessions.setdefault(_normal_path(target), []).append(note)
    for note in notes:
        if note.properties.get("type") != "workstream" or note.properties.get("status") != "active":
            continue
        sessions = closed_sessions.get(_normal_path(note.path), [])
        if not sessions:
            continue
        newest = max(sessions, key=lambda item: (str(item.properties.get("date", "")), _normal_path(item.path)))
        latest = _resolved_single_link(note, "latest_session", by_stem, by_relative)
        if latest != newest.path:
            _add(findings, "stale-workstream-overview", "warning", note.path, "latest_session does not reflect the newest closed work session")


def _canonical_outcome(note: Note) -> str:
    return " ".join(_section(note.body, "Outcome").casefold().split())


def _validate_duplicate_workstreams(notes: list[Note], findings: list[Finding]) -> None:
    outcomes: dict[str, list[Note]] = {}
    for note in notes:
        if note.properties.get("type") != "workstream" or note.properties.get("status") != "active":
            continue
        outcome = _canonical_outcome(note)
        if outcome:
            outcomes.setdefault(outcome, []).append(note)
    for outcome, duplicates in outcomes.items():
        if len(duplicates) > 1:
            paths = ", ".join(sorted(item.path.name for item in duplicates))
            _add(findings, "duplicate-canonical-workstream", "error", min(duplicates, key=lambda item: _normal_path(item.path)).path, f"active workstreams share canonical outcome: {paths}")


def validate_vault(vault: Path, today: date) -> ValidationReport:
    """Validate lifecycle records without mutating the supplied Markdown vault."""

    vault = Path(vault)
    findings: list[Finding] = []
    notes: list[Note] = []
    for path in _paths(vault):
        try:
            notes.append(parse_note(path))
        except (OSError, ValueError) as error:
            _add(findings, "invalid-markdown", "error", path, str(error))

    by_path = {note.path: note for note in notes}
    by_stem, by_relative = _link_index(notes, vault)
    for note in notes:
        _validate_metadata(note, findings)
        _validate_required_relationships(note, findings)
        _validate_links(note, by_path, by_stem, by_relative, findings)
        _validate_closed_session(note, findings)
        _validate_daily_plan(note, today, findings)
        _validate_workstream_evidence(note, by_path, by_stem, by_relative, findings)
        _validate_delivery_state(note, findings)
    _validate_overview_freshness(notes, by_stem, by_relative, findings)
    _validate_duplicate_workstreams(notes, findings)

    return ValidationReport(
        tuple(
            sorted(
                findings,
                key=lambda finding: (
                    _SEVERITY_ORDER[finding.severity],
                    _normal_path(finding.path),
                    finding.code,
                    finding.message,
                ),
            )
        )
    )
