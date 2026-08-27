"""Initialize the minimal workstream-centered Supervaults vault layout."""

from __future__ import annotations

from datetime import date
from pathlib import Path
import re
import tempfile

from .markdown import Note, parse_note, write_note


_UNRESOLVED_MARKER = re.compile(r"{{[^{}]+}}")
_TEMPLATE_ROOT = Path(__file__).resolve().parents[2] / "templates" / "vault"
_DIRECTORIES = (
    Path("daily"),
    Path("workstreams"),
    Path("workstreams/archive"),
    Path("superpowers/specs"),
    Path("superpowers/plans"),
    Path("records/decisions"),
    Path("records/investigations"),
    Path("records/reviews"),
    Path("records/incidents"),
    Path("records/releases"),
    Path("knowledge"),
    Path("inbox"),
    Path("views"),
    Path("templates"),
)


def render_template(template: Path, values: dict[str, str]) -> str:
    """Render supported double-brace markers and reject any missing values."""

    rendered = Path(template).read_text(encoding="utf-8")
    for key, value in values.items():
        rendered = rendered.replace(f"{{{{{key}}}}}", value)
    match = _UNRESOLVED_MARKER.search(rendered)
    if match:
        raise ValueError(f"{template}: unresolved template marker {match.group(0)}")
    return rendered


def _write_rendered_note(destination: Path, template: Path, values: dict[str, str]) -> None:
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
        write_note(Note(destination, parsed.properties, parsed.body))
    finally:
        if temporary_name is not None:
            temporary_path = Path(temporary_name)
            if temporary_path.exists():
                temporary_path.unlink()


def initialize_vault(vault: Path, project_name: str, today: date) -> list[Path]:
    """Create missing vault artifacts without changing existing notes or views."""

    vault = Path(vault)
    created: list[Path] = []
    for relative in _DIRECTORIES:
        directory = vault / relative
        if not directory.exists():
            directory.mkdir(parents=True)
            created.append(directory)

    values = {"PROJECT_NAME": project_name, "DATE": today.isoformat()}
    notes = (
        (Path("Home.md"), _TEMPLATE_ROOT / "Home.md.tmpl"),
        (Path("daily") / f"{today.isoformat()}.md", _TEMPLATE_ROOT / "daily.md.tmpl"),
    )
    for relative, template in notes:
        destination = vault / relative
        if not destination.exists():
            _write_rendered_note(destination, template, values)
            created.append(destination)

    for template in (_TEMPLATE_ROOT / "views").glob("*.base"):
        destination = vault / "views" / template.name
        if not destination.exists():
            destination.write_text(template.read_text(encoding="utf-8"), encoding="utf-8", newline="\n")
            created.append(destination)

    return sorted(created, key=lambda path: path.relative_to(vault).as_posix())
