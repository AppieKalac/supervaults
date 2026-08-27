"""Command-line interface for Supervaults lifecycle helpers."""

from __future__ import annotations

import argparse
from datetime import date, datetime
import json
from pathlib import Path
import re
import sys

from .context import find_context
from .lifecycle import close_session, open_daily_plan, open_session
from .markdown import parse_note
from .vault import initialize_vault


_WIKI_LINK = re.compile(r"^\[\[([^\]|]+)(?:\|[^\]]+)?\]\]$")


def _parse_date(value: str) -> date:
    return date.fromisoformat(value)


def _parse_datetime(value: str) -> datetime:
    return datetime.fromisoformat(value)


def _report_json(report: object) -> str:
    return json.dumps(
        {
            "project": str(report.project),
            "candidates": [
                {
                    "path": str(candidate.path),
                    "artifact_type": candidate.artifact_type,
                    "status": candidate.status,
                    "score": candidate.score,
                    "reasons": list(candidate.reasons),
                }
                for candidate in report.candidates
            ],
            "git_branch": report.git_branch,
            "git_commit": report.git_commit,
            "warnings": list(report.warnings),
        },
        sort_keys=True,
    )


def _linked_workstream(vault: Path, session: Path) -> Path | None:
    value = parse_note(session).properties.get("workstream")
    match = _WIKI_LINK.fullmatch(value) if isinstance(value, str) else None
    if match is None:
        return None
    matches = [path for path in vault.rglob("*.md") if path.stem == match.group(1)]
    return matches[0] if len(matches) == 1 else None


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="supervaults")
    subcommands = parser.add_subparsers(dest="command", required=True)

    init = subcommands.add_parser("init")
    init.add_argument("--vault", type=Path, required=True)
    init.add_argument("--project", required=True)
    init.add_argument("--date", type=_parse_date, default=date.today())

    context = subcommands.add_parser("context")
    context.add_argument("--vault", type=Path, required=True)
    context.add_argument("terms", nargs="*")

    daily = subcommands.add_parser("plan-today")
    daily.add_argument("--vault", type=Path, required=True)
    daily.add_argument("--date", type=_parse_date, default=date.today())

    session = subcommands.add_parser("open-session")
    session.add_argument("--vault", type=Path, required=True)
    session.add_argument("--workstream", type=Path, required=True)
    session.add_argument("--outcome", required=True)
    session.add_argument("--owner", required=True)
    session.add_argument("--now", type=_parse_datetime, default=datetime.now())

    close = subcommands.add_parser("close-session")
    close.add_argument("--vault", type=Path, required=True)
    close.add_argument("--session", type=Path, required=True)
    close.add_argument("--end-commit")
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    try:
        args = parser.parse_args(argv)
        if args.command == "init":
            for path in initialize_vault(args.vault, args.project, args.date):
                print(path)
        elif args.command == "context":
            print(_report_json(find_context(args.vault, args.terms)))
        elif args.command == "plan-today":
            print(open_daily_plan(args.vault, args.date))
        elif args.command == "open-session":
            created = open_session(args.vault, args.workstream, args.outcome, args.now, args.owner)
            print(created)
            print(args.workstream)
        elif args.command == "close-session":
            close_session(args.vault, args.session, args.end_commit)
            print(args.session)
            workstream = _linked_workstream(args.vault, args.session)
            if workstream is not None:
                print(workstream)
        return 0
    except ValueError as error:
        parser.error(str(error))
        return 2
    except OSError as error:
        print(str(error), file=sys.stderr)
        return 1
