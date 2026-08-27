"""Capture and validate protocol-complete live-evaluation evidence."""

from __future__ import annotations

import argparse
import hashlib
import json
import platform
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[2]
WIKI_LINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]+)?(?:\|[^\]]+)?\]\]")
REQUIRED_RECORD_KEYS = {
    "case_id", "prompt", "fixture_context", "agent_identifier", "model",
    "plugin_metadata", "environment", "started_at", "finished_at",
    "dialogue", "before_snapshot", "after_snapshot", "commands",
    "changed_artifacts", "external_mutations", "must_results",
    "must_not_results", "score", "failure_or_evidence_gap",
}


def _run_git(project: Path, *args: str) -> dict[str, Any]:
    completed = subprocess.run(
        ["git", *args], cwd=project, capture_output=True, text=True, check=False
    )
    return {
        "command": ["git", *args],
        "exit_code": completed.returncode,
        "stdout": completed.stdout,
        "stderr": completed.stderr,
    }


def _frontmatter(text: str) -> dict[str, Any]:
    if not text.startswith("---\n"):
        return {}
    end = text.find("\n---\n", 4)
    if end < 0:
        return {}
    result: dict[str, Any] = {}
    current_key: str | None = None
    for raw in text[4:end].splitlines():
        if raw.startswith("  - ") and current_key:
            result.setdefault(current_key, []).append(raw[4:].strip().strip('"\''))
            continue
        if ":" not in raw or raw.startswith(" "):
            continue
        key, value = raw.split(":", 1)
        current_key = key.strip()
        parsed = value.strip().strip('"\'')
        result[current_key] = parsed if parsed else []
    return result


def capture_snapshot(project: Path) -> dict[str, Any]:
    project = project.resolve()
    files: list[dict[str, Any]] = []
    markdown: list[dict[str, Any]] = []
    audits: list[dict[str, Any]] = []
    for path in sorted(p for p in project.rglob("*") if p.is_file() and ".git" not in p.parts):
        relative = path.relative_to(project).as_posix()
        data = path.read_bytes()
        files.append({
            "path": relative,
            "size": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
        })
        if path.suffix.lower() == ".md":
            text = data.decode("utf-8", errors="replace")
            markdown.append({
                "path": relative,
                "frontmatter": _frontmatter(text),
                "links": sorted(set(WIKI_LINK.findall(text))),
            })
        if relative.startswith("audits/") and path.suffix.lower() == ".json":
            try:
                content: Any = json.loads(data)
            except (UnicodeDecodeError, json.JSONDecodeError) as error:
                content = {"parse_error": str(error)}
            audits.append({"path": relative, "content": content})
    return {
        "captured_at": datetime.now(timezone.utc).isoformat(),
        "project": str(project),
        "files": files,
        "markdown": markdown,
        "git": {
            "status": _run_git(project, "status", "--short"),
            "head": _run_git(project, "rev-parse", "HEAD"),
            "branch": _run_git(project, "branch", "--show-current"),
            "last_commit": _run_git(project, "log", "-1", "--format=fuller"),
            "diff_name_status": _run_git(project, "diff", "--name-status"),
        },
        "fake_audits": audits,
    }


def plugin_metadata(plugin_root: Path) -> dict[str, Any]:
    plugin_root = plugin_root.resolve()
    return {
        "root": str(plugin_root),
        "manifest": json.loads((plugin_root / ".codex-plugin/plugin.json").read_text(encoding="utf-8")),
        "upstream_lock": json.loads((plugin_root / "upstream-lock.json").read_text(encoding="utf-8")),
        "git_head": _run_git(plugin_root, "rev-parse", "HEAD"),
        "git_branch": _run_git(plugin_root, "branch", "--show-current"),
    }


def validate_record(record: dict[str, Any], case: dict[str, Any]) -> list[str]:
    errors = [f"missing key: {key}" for key in sorted(REQUIRED_RECORD_KEYS - set(record))]
    if errors:
        return errors
    if record["case_id"] != case["id"]:
        errors.append("case_id does not match case")
    if record["prompt"] != case["prompt"]:
        errors.append("prompt does not match exact case prompt")
    for name in ("before_snapshot", "after_snapshot"):
        snapshot = record.get(name, {})
        for key in ("files", "markdown", "git", "fake_audits"):
            if key not in snapshot:
                errors.append(f"{name} missing {key}")
    if not record.get("dialogue") or any(
        set(exchange) != {"speaker", "text"} for exchange in record.get("dialogue", [])
    ):
        errors.append("dialogue must retain ordered speaker/text exchanges")
    for command in record.get("commands", []):
        if not {"command", "stdout", "stderr", "exit_code"}.issubset(command):
            errors.append("every command needs command/stdout/stderr/exit_code")
    for field, oracles in (("must_results", case["must"]), ("must_not_results", case["must_not"])):
        results = record.get(field, [])
        if len(results) != len(oracles):
            errors.append(f"{field} must contain one result per oracle")
            continue
        for index, (result, oracle) in enumerate(zip(results, oracles)):
            if result.get("oracle") != oracle:
                errors.append(f"{field}[{index}] oracle does not match case order")
            if result.get("result") not in {"pass", "fail", "inconclusive"}:
                errors.append(f"{field}[{index}] has invalid result")
            if not str(result.get("evidence", "")).strip():
                errors.append(f"{field}[{index}] lacks evidence")
    if record.get("score") not in {"pass", "fail", "inconclusive"}:
        errors.append("invalid score")
    return errors


def _write_json(path: Path, value: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="action", required=True)
    snapshot_parser = subparsers.add_parser("snapshot")
    snapshot_parser.add_argument("--project", type=Path, required=True)
    snapshot_parser.add_argument("--output", type=Path, required=True)
    snapshot_parser.add_argument("--plugin-root", type=Path, default=ROOT)
    verify_parser = subparsers.add_parser("verify-record")
    verify_parser.add_argument("--record", type=Path, required=True)
    verify_parser.add_argument("--case", required=True)
    args = parser.parse_args(argv)
    if args.action == "snapshot":
        result = capture_snapshot(args.project)
        result["plugin_metadata"] = plugin_metadata(args.plugin_root)
        result["environment"] = {
            "platform": platform.platform(),
            "python": sys.version,
        }
        _write_json(args.output, result)
        return 0
    cases = json.loads((ROOT / "tests/evals/cases.json").read_text(encoding="utf-8"))
    case = next((item for item in cases if item["id"] == args.case), None)
    if case is None:
        print(f"unknown case: {args.case}", file=sys.stderr)
        return 2
    record = json.loads(args.record.read_text(encoding="utf-8"))
    errors = validate_record(record, case)
    print(json.dumps({"valid": not errors, "errors": errors}, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
