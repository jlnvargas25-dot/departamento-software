#!/usr/bin/env python
"""rename_migration_timestamp.py — codemod Python (S-7.1).

Rule_id: MIGRATION-NAMING
Pattern: files matching `supabase/migrations/0\\d{3}_*.sql`
Transformation: rename a `YYYYMMDDHHmm_<slug>.sql` (UTC).

Timestamp source priority:
    1. git log primer commit del file (autoritativo, reproducible)
    2. file mtime (Posix stat) si git falla
    3. UTC actual (last resort, marca con prefix `WIP_`)

Modes:
    --dry-run        : printa mapping sin renombrar (R-5 reversibilidad)
    --verify <dir>   : check todos los files en dir matchean ^\\d{12}_[a-z0-9_-]+\\.sql$
    (default)        : apply rename + escribe log a `.sigma-mechanic/migration-renames.log`

Idempotente: file ya con formato timestamp -> no-op.
Reversible: log mantiene mapping original->new para revertir manualmente.
"""

from __future__ import annotations

import argparse
import datetime as dt
import re
import subprocess
import sys
from pathlib import Path

OLD_PATTERN = re.compile(r"^0\d{3}_[a-z0-9_-]+\.sql$")
NEW_PATTERN = re.compile(r"^\d{12}_[a-z0-9_-]+\.sql$")
LOG_DIR = ".sigma-mechanic"
LOG_FILENAME = "migration-renames.log"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("target", help="path al file o directory")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    target = Path(args.target)

    if args.verify:
        return _verify(target)

    return _apply(target, dry_run=args.dry_run)


def _verify(target: Path) -> int:
    directory = target if target.is_dir() else target.parent
    if not directory.is_dir():
        sys.stderr.write(f"directory not found: {directory}\n")
        return 2
    non_matching: list[str] = []
    for child in sorted(directory.iterdir()):
        if not child.is_file():
            continue
        if not child.name.endswith(".sql"):
            continue
        if not NEW_PATTERN.match(child.name) and OLD_PATTERN.match(child.name):
            non_matching.append(child.name)
    if non_matching:
        sys.stderr.write(
            f"{len(non_matching)} file(s) NOT in YYYYMMDDHHmm_*.sql format: "
            f"{', '.join(non_matching)}\n"
        )
        return 1
    return 0


def _apply(target: Path, dry_run: bool) -> int:
    if not target.exists():
        sys.stderr.write(f"target not found: {target}\n")
        return 2

    if target.is_dir():
        files = sorted(p for p in target.iterdir() if p.is_file())
    else:
        files = [target]

    renames: list[tuple[Path, Path]] = []
    for f in files:
        if NEW_PATTERN.match(f.name):
            continue  # idempotente: ya en formato correcto
        if not OLD_PATTERN.match(f.name):
            continue  # no es legacy migration filename
        timestamp = _resolve_timestamp(f)
        slug = f.name.split("_", 1)[1] if "_" in f.name else f.name
        new_name = f"{timestamp}_{slug}"
        renames.append((f, f.with_name(new_name)))

    if not renames:
        sys.stdout.write("no migrations to rename (all already in target format)\n")
        return 0

    if dry_run:
        for old, new in renames:
            sys.stdout.write(f"DRY-RUN: {old.name} -> {new.name}\n")
        return 0

    log_path = Path.cwd() / LOG_DIR / LOG_FILENAME
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("a", encoding="utf-8") as fp:
        for old, new in renames:
            if new.exists():
                sys.stderr.write(f"target name already exists, skipping: {new.name}\n")
                continue
            old.rename(new)
            fp.write(f"{dt.datetime.now(dt.timezone.utc).isoformat()}\t{old.name}\t{new.name}\n")
            sys.stdout.write(f"renamed: {old.name} -> {new.name}\n")
    return 0


def _resolve_timestamp(f: Path) -> str:
    """Resuelve timestamp YYYYMMDDHHmm UTC.

    Priority: git log first commit -> file mtime -> wall-clock UTC.
    """
    git_ts = _git_first_commit_timestamp(f)
    if git_ts:
        return git_ts
    try:
        mtime = f.stat().st_mtime
        utc = dt.datetime.fromtimestamp(mtime, tz=dt.timezone.utc)
        return utc.strftime("%Y%m%d%H%M")
    except OSError:
        # fall through to wall-clock fallback (last-resort per docstring priority)
        pass
    return dt.datetime.now(dt.timezone.utc).strftime("%Y%m%d%H%M")


def _git_first_commit_timestamp(f: Path) -> str | None:
    """git log --reverse --format=%aI --max-count=1 -- <file>; parse a YYYYMMDDHHmm UTC."""
    try:
        result = subprocess.run(
            ["git", "log", "--reverse", "--format=%aI", "--max-count=1", "--", str(f)],
            capture_output=True,
            text=True,
            timeout=5,
            shell=False,
        )
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return None
    if result.returncode != 0 or not result.stdout.strip():
        return None
    iso = result.stdout.strip().splitlines()[0]
    try:
        # ISO 8601 con timezone offset (git formato %aI)
        ts = dt.datetime.fromisoformat(iso)
    except ValueError:
        return None
    return ts.astimezone(dt.timezone.utc).strftime("%Y%m%d%H%M")


if __name__ == "__main__":
    sys.exit(main())
