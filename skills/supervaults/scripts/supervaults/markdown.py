"""A deliberately small YAML-frontmatter reader and writer for vault notes."""

from __future__ import annotations

from dataclasses import dataclass
import json
from pathlib import Path
import re
import tempfile
from typing import Any

from .schema import RELATIONSHIP_FIELDS


_KEY_VALUE = re.compile(r"^([^\s:#][^:]*?):(?:[ ](.*))?$")
_INTEGER = re.compile(r"^-?(?:0|[1-9][0-9]*)$")
_PRIMARY_FIELDS = ("type", "stage", "status", "project", "workstream", "spec", "plan", "date")
_CONTEXT_FIELDS = (
    "area",
    "components",
    "affected_surfaces",
    "repository",
    "branch",
    "base_commit",
    "end_commit",
    "external_refs",
    "environments",
    "risk",
    "aliases",
)
_TIMESTAMP_FIELDS = ("created", "updated")


@dataclass(frozen=True)
class Note:
    """An immutable note record; property values may be scalar values or scalar lists."""

    path: Path
    properties: dict[str, object]
    body: str


def _error(path: Path, property_name: str, message: str) -> ValueError:
    return ValueError(f"{path}: property '{property_name}': {message}")


def _parse_scalar(value: str, path: Path, property_name: str) -> object:
    if value.startswith('"'):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError as error:
            raise _error(path, property_name, "malformed quoted scalar") from error
        if not isinstance(parsed, str):
            raise _error(path, property_name, "quoted scalar must be a string")
        return parsed
    if value.startswith("'"):
        if len(value) < 2 or not value.endswith("'"):
            raise _error(path, property_name, "malformed quoted scalar")
        return value[1:-1].replace("''", "'")
    if value in {"true", "false"}:
        return value == "true"
    if _INTEGER.fullmatch(value):
        return int(value)
    return value


def parse_note(path: Path) -> Note:
    """Read a UTF-8 Markdown note with the supported flat frontmatter subset."""

    path = Path(path)
    text = path.read_text(encoding="utf-8")
    lines = text.replace("\r\n", "\n").replace("\r", "\n").splitlines(keepends=True)
    if not lines or lines[0].rstrip("\n") != "---":
        raise ValueError(f"{path}: frontmatter must begin with '---'")

    closing_index = next(
        (index for index, line in enumerate(lines[1:], 1) if line.rstrip("\n") == "---"),
        None,
    )
    if closing_index is None:
        raise ValueError(f"{path}: frontmatter is missing its closing '---'")

    properties: dict[str, object] = {}
    index = 1
    while index < closing_index:
        raw = lines[index].rstrip("\n")
        if not raw or raw.lstrip().startswith("#"):
            raise ValueError(f"{path}: frontmatter contains an unsupported blank or comment line")
        if raw[0].isspace():
            raise ValueError(f"{path}: property '<frontmatter>': unexpected indentation")
        match = _KEY_VALUE.fullmatch(raw)
        if not match:
            raise ValueError(f"{path}: property '<frontmatter>': malformed frontmatter")
        key, inline_value = match.groups()
        if key in properties:
            raise _error(path, key, "duplicate property")
        if inline_value is not None:
            properties[key] = _parse_scalar(inline_value, path, key)
            index += 1
            continue

        index += 1
        values: list[object] = []
        while index < closing_index and lines[index].startswith((" ", "\t")):
            item = lines[index].rstrip("\n")
            if item.startswith("\t") or not item.startswith("  - "):
                raise _error(path, key, "nested mappings are unsupported")
            values.append(_parse_scalar(item[4:], path, key))
            index += 1
        if not values:
            raise _error(path, key, "a value or indented scalar list is required")
        properties[key] = values

    body = "".join(lines[closing_index + 1 :])
    return Note(path, properties, body)


def _serialize_scalar(value: object, path: Path, property_name: str) -> str:
    if isinstance(value, str):
        return json.dumps(value, ensure_ascii=False)
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    raise _error(path, property_name, "unsupported scalar type")


def _ordered_keys(properties: dict[str, object]) -> list[str]:
    preferred = _PRIMARY_FIELDS + RELATIONSHIP_FIELDS + _CONTEXT_FIELDS + _TIMESTAMP_FIELDS
    seen: set[str] = set()
    ordered: list[str] = []
    for key in preferred:
        if key in properties and key not in seen:
            ordered.append(key)
            seen.add(key)
    ordered.extend(sorted(key for key in properties if key not in seen))
    return ordered


def _serialize_frontmatter(note: Note) -> str:
    lines = ["---\n"]
    for key in _ordered_keys(note.properties):
        if not isinstance(key, str) or not _KEY_VALUE.fullmatch(f"{key}: value"):
            raise _error(note.path, str(key), "invalid property name")
        value: Any = note.properties[key]
        if isinstance(value, list):
            lines.append(f"{key}:\n")
            for item in value:
                lines.append(f"  - {_serialize_scalar(item, note.path, key)}\n")
        else:
            lines.append(f"{key}: {_serialize_scalar(value, note.path, key)}\n")
    lines.append("---\n")
    return "".join(lines)


def write_note(note: Note) -> None:
    """Atomically write a note, normalizing line endings to UTF-8 LF."""

    content = _serialize_frontmatter(note) + note.body.replace("\r\n", "\n").replace("\r", "\n")
    note.path.parent.mkdir(parents=True, exist_ok=True)
    temporary_name: str | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", encoding="utf-8", newline="\n", dir=note.path.parent,
            prefix=f".{note.path.name}.", suffix=".tmp", delete=False,
        ) as temporary:
            temporary_name = temporary.name
            temporary.write(content)
        Path(temporary_name).replace(note.path)
    finally:
        if temporary_name is not None:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()
