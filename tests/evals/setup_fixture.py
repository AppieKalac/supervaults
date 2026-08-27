"""Create deterministic disposable repositories for behavioral evaluations."""

from __future__ import annotations

import argparse
from datetime import date, datetime, time, timedelta, timezone
import json
import os
from pathlib import Path
import subprocess
import sys


FIXTURE_DIR = Path(__file__).with_name("fixtures")
CASE_OVERLAYS_PATH = FIXTURE_DIR / "case-overlays.json"


def load_fixture(name: str) -> dict[str, object]:
    """Load one checked-in fixture definition by its stable name."""

    path = FIXTURE_DIR / f"{name}.json"
    if not path.is_file():
        raise ValueError(f"unknown fixture: {name}")
    fixture = json.loads(path.read_text(encoding="utf-8"))
    if fixture.get("name") != name or not isinstance(fixture.get("commits"), list):
        raise ValueError(f"invalid fixture definition: {path}")
    return fixture


def load_case_overlay(case_id: str) -> dict[str, object]:
    """Load the deterministic setup actions for one evaluation case."""

    overlays = json.loads(CASE_OVERLAYS_PATH.read_text(encoding="utf-8"))
    overlay = overlays.get(case_id)
    if not isinstance(overlay, dict) or not isinstance(overlay.get("actions"), list):
        raise ValueError(f"unknown or invalid case overlay: {case_id}")
    return overlay


def _tokens(run_date: date) -> dict[str, str]:
    run_datetime = datetime.combine(run_date, time(9, tzinfo=timezone.utc))
    return {
        "{{RUN_DATE}}": run_date.isoformat(),
        "{{PREVIOUS_DATE}}": (run_date - timedelta(days=1)).isoformat(),
        "{{RUN_DATETIME}}": run_datetime.isoformat().replace("+00:00", "Z"),
    }


def _render(value: str, tokens: dict[str, str]) -> str:
    for marker, replacement in tokens.items():
        value = value.replace(marker, replacement)
    return value


def _run(arguments: list[str], destination: Path, environment: dict[str, str] | None = None) -> None:
    subprocess.run(arguments, cwd=destination, env=environment, check=True, capture_output=True, text=True)


def _safe_destination(destination: Path, relative: str) -> Path:
    path = (destination / relative).resolve()
    if path == destination.resolve() or destination.resolve() not in path.parents:
        raise ValueError(f"fixture file escapes destination: {relative}")
    return path


def _apply_overlay(destination: Path, case_id: str, fixture_name: str, tokens: dict[str, str]) -> None:
    overlay = load_case_overlay(case_id)
    if overlay.get("fixture") != fixture_name:
        raise ValueError(f"{case_id}: overlay fixture does not match {fixture_name}")
    for action in overlay["actions"]:
        if not isinstance(action, dict):
            raise ValueError(f"{case_id}: invalid overlay action")
        kind = action.get("kind")
        path = _safe_destination(destination, _render(str(action["path"]), tokens))
        if kind == "assert-path":
            exists = action.get("assertion") == "exists"
            if path.exists() != exists:
                raise ValueError(f"{case_id}: expected {action['assertion']} at {path}")
        elif kind == "write-file":
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_render(str(action["content"]), tokens), encoding="utf-8", newline="\n")
        elif kind == "replace-text":
            text = path.read_text(encoding="utf-8")
            old = _render(str(action["old"]), tokens)
            if text.count(old) != 1:
                raise ValueError(f"{case_id}: expected one replace target in {path}")
            path.write_text(text.replace(old, _render(str(action["new"]), tokens)), encoding="utf-8", newline="\n")
        else:
            raise ValueError(f"{case_id}: unsupported overlay action {kind}")


def create_fixture(name: str, destination: Path, run_date: date, case_id: str | None = None) -> Path:
    """Render a fixture into a new Git repository with deterministic commits."""

    fixture = load_fixture(name)
    destination = Path(destination)
    if destination.exists():
        raise ValueError(f"destination already exists: {destination}")
    destination.mkdir(parents=True)
    _run(["git", "init", "--quiet", "--initial-branch", "main"], destination)
    _run(["git", "config", "user.name", "Supervaults Eval"], destination)
    _run(["git", "config", "user.email", "eval@example.invalid"], destination)

    tokens = _tokens(run_date)
    for relative in fixture.get("directories", []):
        _safe_destination(destination, _render(str(relative), tokens)).mkdir(parents=True, exist_ok=True)

    for commit in fixture["commits"]:
        if not isinstance(commit, dict):
            raise ValueError(f"invalid commit in fixture: {name}")
        for entry in commit.get("files", []):
            path = _safe_destination(destination, _render(str(entry["path"]), tokens))
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(_render(str(entry["content"]), tokens), encoding="utf-8", newline="\n")
        timestamp = _render(str(commit["timestamp"]), tokens)
        environment = os.environ.copy()
        environment.update({"GIT_AUTHOR_DATE": timestamp, "GIT_COMMITTER_DATE": timestamp})
        _run(["git", "add", "--all"], destination, environment)
        _run(["git", "commit", "--quiet", "-m", str(commit["message"])], destination, environment)
    if case_id is not None:
        _apply_overlay(destination, case_id, name, tokens)
    return destination


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", required=True)
    parser.add_argument("--destination", type=Path, required=True)
    parser.add_argument("--date", type=_parse_date, required=True)
    parser.add_argument("--case")
    args = parser.parse_args(argv)
    try:
        print(create_fixture(args.fixture, args.destination, args.date, args.case))
    except (OSError, ValueError, subprocess.CalledProcessError) as error:
        print(error, file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
