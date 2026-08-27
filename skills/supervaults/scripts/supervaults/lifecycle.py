"""Retained daily plans and evidence-gated work-session transitions."""

from __future__ import annotations

from datetime import date, datetime
from pathlib import Path
import re
import tempfile

from .markdown import Note, parse_note, write_note
from .schema import IMPACT_SURFACES, TYPE_STATUSES, WORKSTREAM_STAGES
from .vault import render_template


_TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "vault"
_WIKI_LINK = re.compile(r"^\[\[([^\]|]+)(?:\|[^\]]+)?\]\]$")
_HEADING = re.compile(r"^##\s+(.+?)\s*$", re.MULTILINE)
_SLUG = re.compile(r"[^a-z0-9]+")
_UNRESOLVED_MARKER = re.compile(r"\{\{[^{}]+\}\}|<[^>\n]+>")
_PLACEHOLDER = re.compile(
    r"\b(?:tbd|todo|to do|placeholder|copied filler|lorem ipsum|sample text|example text)\b",
    re.IGNORECASE,
)
_RESULT_VALUE = re.compile(
    r"^(?:passed|failed|not-run|manual-check)\s*(?:(?::|--|—|-)\s*.+|\(.+\))$",
    re.IGNORECASE,
)
_FILLER_COMPACT = frozenset(
    {
        "details",
        "detailshere",
        "adddetailshere",
        "insertevidencehere",
        "actualblastradius",
        "verificationevidence",
        "handoff",
        "notapplicable",
    }
)


class LifecycleStateError(ValueError):
    """An invalid requested lifecycle transition or session state."""


def _render_note(destination: Path, template: Path, values: dict[str, str]) -> Note:
    rendered = render_template(template, values)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=destination.parent,
            prefix=f".{destination.name}.", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(rendered)
        parsed = parse_note(Path(temporary_name))
        return Note(destination, dict(parsed.properties), parsed.body)
    finally:
        if temporary_name is not None:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()


def _slug(value: str) -> str:
    result = _SLUG.sub("-", value.casefold()).strip("-")
    if not result:
        raise LifecycleStateError("outcome must contain letters or digits")
    return result


def _require_workstream(workstream: Path) -> Note:
    if not workstream.is_file():
        raise LifecycleStateError(f"{workstream}: workstream note does not exist")
    note = parse_note(workstream)
    required = ("type", "stage", "status", "project")
    missing = [field for field in required if not isinstance(note.properties.get(field), str) or not note.properties[field]]
    if (
        note.properties.get("type") != "workstream"
        or missing
        or note.properties.get("stage") not in WORKSTREAM_STAGES
        or note.properties.get("status") not in TYPE_STATUSES["workstream"]
        or note.properties.get("status") in {"complete", "superseded"}
    ):
        raise LifecycleStateError(f"{workstream}: missing or invalid workstream metadata")
    return note


def _link_target(value: object, property_name: str, path: Path) -> str:
    if not isinstance(value, str):
        raise ValueError(f"{path}: property '{property_name}' must be a wiki link")
    match = _WIKI_LINK.fullmatch(value)
    if not match:
        raise ValueError(f"{path}: property '{property_name}' must be a wiki link")
    return match.group(1)


def _find_named_note(vault: Path, stem: str) -> Path:
    matches = sorted((path for path in vault.rglob("*.md") if path.stem == stem), key=lambda path: path.as_posix())
    if len(matches) != 1:
        description = "missing" if not matches else "ambiguous"
        raise ValueError(f"{vault}: {description} wiki link target '{stem}'")
    return matches[0]


def _section_content(body: str, name: str) -> str:
    match = re.search(rf"^##\s+{re.escape(name)}\s*$", body, re.MULTILINE)
    if match is None:
        return ""
    next_heading = _HEADING.search(body, match.end())
    return body[match.end(): next_heading.start() if next_heading else len(body)].strip()


def _is_non_placeholder_value(value: str) -> bool:
    """Accept a populated evidence field only when it is not a template placeholder."""

    normalized = " ".join(value.strip().split())
    if not normalized or _UNRESOLVED_MARKER.search(normalized) or _PLACEHOLDER.search(normalized):
        return False
    if _compact(normalized) in _FILLER_COMPACT:
        return False
    return not _has_filler_detail_segment(normalized)


def _compact(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _has_filler_detail_segment(value: str) -> bool:
    """Reject a separator suffix when it contains only template filler."""

    segments = re.split(r"\s*(?:—|--)\s*|\s+-\s+|:\s*", value)
    for segment in segments[1:]:
        if _compact(segment) in _FILLER_COMPACT:
            return True
        if _UNRESOLVED_MARKER.search(segment) or _PLACEHOLDER.search(segment):
            return True
    return False


def _field_values(content: str, label: str) -> list[str]:
    pattern = re.compile(rf"^\s*(?:-\s*)?{re.escape(label)}:\s*(.*)$", re.IGNORECASE | re.MULTILINE)
    return [match.group(1).strip() for match in pattern.finditer(content)]


def _has_valid_actual_blast_radius(content: str) -> bool:
    canonical_surfaces = {surface.casefold() for surface in IMPACT_SURFACES}
    surface_pattern = re.compile(r"^\s*(?:-\s*)?Surface:\s*(.*)$", re.IGNORECASE | re.MULTILINE)
    surfaces = list(surface_pattern.finditer(content))
    for index, surface_match in enumerate(surfaces):
        if surface_match.group(1).strip().casefold() not in canonical_surfaces:
            continue
        block_end = surfaces[index + 1].start() if index + 1 < len(surfaces) else len(content)
        block = content[surface_match.end():block_end]
        states = _field_values(block, "State")
        if not states:
            continue
        state = states[0].casefold()
        if state not in {"changed", "unchanged", "not-applicable", "unknown", "not-checked"}:
            continue
        details = _field_values(block, "Detail")
        if state == "unchanged" or (details and _is_non_placeholder_value(details[0])):
            return True
    return False


def _has_valid_verification_evidence(content: str) -> bool:
    checks = _field_values(content, "Check")
    results = _field_values(content, "Result")
    return bool(
        checks
        and results
        and _is_non_placeholder_value(checks[0])
        and _is_non_placeholder_value(results[0])
        and _RESULT_VALUE.fullmatch(results[0])
    )


def _has_valid_handoff(content: str) -> bool:
    current_states = _field_values(content, "Current state")
    next_actions = _field_values(content, "Next action")
    return bool(
        current_states
        and next_actions
        and _is_non_placeholder_value(current_states[0])
        and _is_non_placeholder_value(next_actions[0])
    )


def _canonical_workstream(vault: Path, workstream: Path) -> Path:
    root = (vault / "workstreams").resolve()
    resolved = workstream.resolve()
    if (
        resolved.suffix.casefold() != ".md"
        or resolved.parent.parent != root
        or resolved.parent.name == "archive"
    ):
        raise LifecycleStateError(f"{workstream}: workstream must be a direct child of workstreams/<slug>/")
    return resolved


def open_daily_plan(vault: Path, day: date) -> Path:
    """Create one retained daily plan and link it to the nearest preceding plan."""

    vault = Path(vault)
    destination = vault / "daily" / f"{day.isoformat()}.md"
    if destination.exists():
        return destination
    if not (vault / "Home.md").is_file():
        raise LifecycleStateError(f"{vault}: project overview is missing")
    destination.parent.mkdir(parents=True, exist_ok=True)
    note = _render_note(destination, _TEMPLATE_ROOT / "daily.md.tmpl", {"DATE": day.isoformat()})
    prior: list[tuple[date, Path]] = []
    for path in destination.parent.glob("*.md"):
        try:
            note_date = date.fromisoformat(path.stem)
            prior_note = parse_note(path)
        except ValueError:
            continue
        if note_date < day and prior_note.properties.get("type") == "daily-plan":
            prior.append((note_date, path))
    if prior:
        note.properties["previous_day"] = f"[[{max(prior, key=lambda item: item[0])[1].stem}]]"
    write_note(note)
    return destination


def open_session(vault: Path, workstream: Path, outcome: str, now: datetime, owner: str) -> Path:
    """Open a unique owned session, retaining the workstream relationship."""

    vault = Path(vault)
    workstream = Path(workstream)
    workstream = _canonical_workstream(vault, workstream)
    workstream_note = _require_workstream(workstream)
    if not owner.strip():
        raise LifecycleStateError("owner must not be empty")
    filename = f"{now:%Y-%m-%d-%H%M}-{_slug(outcome)}.md"
    destination = workstream.parent / "sessions" / filename
    if destination.exists():
        raise LifecycleStateError(f"{destination}: session collision")
    destination.parent.mkdir(parents=True, exist_ok=True)
    note = _render_note(
        destination,
        _TEMPLATE_ROOT / "session.md.tmpl",
        {
            "WORKSTREAM_NAME": workstream.stem,
            "DATE": now.date().isoformat(),
            "SESSION_OUTCOME": outcome,
        },
    )
    note.properties["owner"] = owner
    previous_field = "current_session" if workstream_note.properties.get("current_session") else "latest_session"
    previous = workstream_note.properties.get(previous_field)
    if previous is not None:
        note.properties["previous_session"] = _link_target(previous, previous_field, workstream)
        note.properties["previous_session"] = f"[[{note.properties['previous_session']}]]"
    write_note(note)
    updated_properties = dict(workstream_note.properties)
    updated_properties["current_session"] = f"[[{destination.stem}]]"
    write_note(Note(workstream, updated_properties, workstream_note.body))
    return destination


def close_session(vault: Path, session: Path, end_commit: str | None) -> None:
    """Close an owned session only after substantive impact, evidence, and handoff."""

    vault = Path(vault)
    session = Path(session)
    if not session.is_file():
        raise LifecycleStateError(f"{session}: session note does not exist")
    note = parse_note(session)
    if note.properties.get("type") != "work-session":
        raise LifecycleStateError(f"{session}: not a work-session note")
    if note.properties.get("status") not in {"active", "blocked", "verified", "complete"}:
        raise LifecycleStateError(f"{session}: invalid lifecycle status")
    workstream_name = _link_target(note.properties.get("workstream"), "workstream", session)
    workstream_path = _find_named_note(vault, workstream_name)
    workstream_path = _canonical_workstream(vault, workstream_path)
    workstream_note = _require_workstream(workstream_path)
    expected_session_directory = workstream_path.parent / "sessions"
    if session.resolve().parent != expected_session_directory:
        raise LifecycleStateError(f"{session}: session must be inside {expected_session_directory}")
    required_sections = (
        ("Actual blast radius", _has_valid_actual_blast_radius),
        ("Verification evidence", _has_valid_verification_evidence),
        ("Handoff", _has_valid_handoff),
    )
    for heading, is_valid in required_sections:
        if not is_valid(_section_content(note.body, heading)):
            raise LifecycleStateError(f"{session}: ## {heading} does not meet the structured evidence contract")

    updated_properties = dict(note.properties)
    # `complete` is an explicit requested state; mechanical closure otherwise only verifies evidence.
    updated_properties["status"] = "complete" if note.properties.get("status") == "complete" else "verified"
    if end_commit is not None:
        updated_properties["end_commit"] = end_commit
    write_note(Note(session, updated_properties, note.body))

    workstream_properties = dict(workstream_note.properties)
    session_link = f"[[{session.stem}]]"
    workstream_properties["latest_session"] = session_link
    if workstream_properties.get("current_session") == session_link:
        workstream_properties.pop("current_session")
    write_note(Note(workstream_path, workstream_properties, workstream_note.body))
