"""Synchronize the selected upstream skill directories into the vendor tree."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def sha256_file(path: Path) -> str:
    """Return the SHA-256 digest of *path*'s bytes."""
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def list_files(path: Path) -> list[Path]:
    """Return all files below *path*, sorted by forward-slash relative path."""
    return sorted(
        (entry for entry in path.rglob("*") if entry.is_file()),
        key=lambda entry: entry.relative_to(path).as_posix(),
    )


def verify(root: Path, lock: dict) -> list[str]:
    """Check the local vendor tree against *lock* without changing anything."""
    errors: list[str] = []
    sources = lock.get("sources")
    if not isinstance(sources, dict):
        return ["lock is missing a sources object"]

    for name in sorted(sources):
        source = sources[name]
        if not isinstance(source, dict):
            errors.append(f"source {name!r} is not an object")
            continue
        files = source.get("files")
        if not isinstance(files, dict):
            errors.append(f"source {name!r} is missing a files object")
            continue

        vendor_root = root / "vendor" / name
        expected_paths = set(files)
        actual_paths = (
            {file.relative_to(vendor_root).as_posix() for file in list_files(vendor_root)}
            if vendor_root.is_dir()
            else set()
        )
        for relative_path in sorted(expected_paths - actual_paths):
            errors.append(f"missing vendor file: vendor/{name}/{relative_path}")
        for relative_path in sorted(actual_paths - expected_paths):
            errors.append(f"unexpected vendor file: vendor/{name}/{relative_path}")
        for relative_path in sorted(expected_paths & actual_paths):
            expected_hash = files[relative_path]
            actual_hash = sha256_file(vendor_root / relative_path)
            if actual_hash != expected_hash:
                errors.append(f"hash mismatch: vendor/{name}/{relative_path}")

    vendor = root / "vendor"
    if vendor.is_dir():
        expected_sources = set(sources)
        for entry in sorted(vendor.iterdir(), key=lambda item: item.name):
            if not entry.is_dir() or entry.name not in expected_sources:
                errors.append(f"unexpected vendor entry: vendor/{entry.name}")
    return errors


def _atomic_write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        "w", encoding="utf-8", dir=path.parent, delete=False, newline="\n"
    ) as handle:
        json.dump(value, handle, indent=2, sort_keys=True)
        handle.write("\n")
        temporary_path = Path(handle.name)
    try:
        os.replace(temporary_path, path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def _replace_vendor(root: Path, staged_vendor: Path) -> Path:
    """Install a staged vendor tree and retain its predecessor for rollback."""
    vendor = root / "vendor"
    backup = root / ".vendor-sync-backup"
    if backup.exists():
        raise RuntimeError(f"refusing to overwrite existing backup directory: {backup}")
    if vendor.exists():
        os.replace(vendor, backup)
    try:
        os.replace(staged_vendor, vendor)
    except Exception:
        if backup.exists():
            os.replace(backup, vendor)
        raise
    return backup


def _restore_vendor(root: Path, backup: Path) -> None:
    """Remove the newly installed vendor tree and restore its backup, if any."""
    vendor = root / "vendor"
    if vendor.exists():
        shutil.rmtree(vendor)
    if backup.exists():
        os.replace(backup, vendor)


def _run_git(arguments: list[str], cwd: Path | None = None) -> str:
    completed = subprocess.run(
        ["git", *arguments],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return completed.stdout.strip()


def _changed_files(old_lock: dict, new_lock: dict) -> list[str]:
    changed: list[str] = []
    old_sources = old_lock.get("sources", {})
    for name, source in new_lock["sources"].items():
        old_files = old_sources.get(name, {}).get("files", {})
        new_files = source["files"]
        changed.extend(
            f"vendor/{name}/{path}"
            for path in sorted(set(old_files) | set(new_files))
            if old_files.get(path) != new_files.get(path)
        )
    return changed


def sync(selection_path: Path, root: Path, update: bool) -> dict:
    """Fetch selected paths, construct a lock, and replace the vendor tree."""
    selection = json.loads(selection_path.read_text(encoding="utf-8"))
    lock_path = root / "upstream-lock.json"
    vendor_path = root / "vendor"
    if not update and (lock_path.exists() or vendor_path.exists()):
        raise RuntimeError("refusing to replace an existing upstream lock or vendor tree; use --update")

    old_lock = (
        json.loads(lock_path.read_text(encoding="utf-8")) if lock_path.exists() else {"sources": {}}
    )
    with tempfile.TemporaryDirectory(prefix="supervaults-upstreams-") as temporary:
        temporary_root = Path(temporary)
        staged_vendor = temporary_root / "vendor"
        sources: dict[str, dict] = {}
        for name in sorted(selection):
            selected = selection[name]
            clone = temporary_root / name
            _run_git(["clone", "--quiet", selected["repository"], str(clone)])
            commit = _run_git(["rev-parse", "HEAD"], cwd=clone)
            destination_root = staged_vendor / name
            for relative_path in selected["paths"]:
                source_path = clone / relative_path
                if not source_path.is_dir():
                    raise RuntimeError(f"selected upstream path does not exist: {name}/{relative_path}")
                shutil.copytree(source_path, destination_root / relative_path)
            files = {
                file.relative_to(destination_root).as_posix(): sha256_file(file)
                for file in list_files(destination_root)
            }
            sources[name] = {
                "repository": selected["repository"],
                "commit": commit,
                "paths": selected["paths"],
                "files": files,
            }

        lock = {"sources": sources}
        if update:
            for name in sorted(sources):
                old_commit = old_lock.get("sources", {}).get(name, {}).get("commit", "(none)")
                print(f"{name}: {old_commit} -> {sources[name]['commit']}")
            changed = _changed_files(old_lock, lock)
            print(f"changed files: {len(changed)}")
            for path in changed:
                print(f"  {path}")

        backup = _replace_vendor(root, staged_vendor)
        try:
            _atomic_write_json(lock_path, lock)
        except Exception:
            _restore_vendor(root, backup)
            raise
        if backup.exists():
            shutil.rmtree(backup)
    return lock


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument("--initialize", action="store_true")
    actions.add_argument("--update", action="store_true")
    actions.add_argument("--verify", action="store_true")
    args = parser.parse_args(argv)
    root = Path(__file__).resolve().parents[1]
    lock_path = root / "upstream-lock.json"
    try:
        if args.verify:
            lock = json.loads(lock_path.read_text(encoding="utf-8"))
            errors = verify(root, lock)
            if errors:
                print("upstream integrity verification failed:", file=sys.stderr)
                for error in errors:
                    print(f"  {error}", file=sys.stderr)
                return 1
            print("upstream integrity verification passed")
            return 0
        sync(root / "upstream-selection.json", root, update=args.update)
        print("upstream vendor tree synchronized")
        return 0
    except (OSError, RuntimeError, subprocess.CalledProcessError, json.JSONDecodeError) as error:
        print(f"sync failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
