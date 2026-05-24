#!/usr/bin/env python
"""add_volatile_marker.py — codemod Python (S-7.2).

Rule_id: PGSQL-MISSING-VOLATILE
Pattern: CREATE FUNCTION ... LANGUAGE plpgsql SIN VOLATILE/STABLE/IMMUTABLE marker.
Transformation: append `VOLATILE` al final del CREATE FUNCTION statement.

Conservador:
    - VOLATILE es el default de Postgres y la opcion mas segura (suboptimal
      performance pero correcto semanticamente). El operador puede sobreescribir
      a STABLE/IMMUTABLE post-fix si tiene certeza.
    - Funciones que YA tienen VOLATILE/STABLE/IMMUTABLE -> no-op (idempotente).

Modes:
    --verify <file>  : check todos los CREATE FUNCTION tienen marker, exit 0/1
    (default)        : apply transformation in-place
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# Match: CREATE [OR REPLACE] FUNCTION ... LANGUAGE plpgsql [marker]?;
# Captura: prefix + LANGUAGE plpgsql + optional whitespace + marker (or absent) + terminator
CREATE_FUNCTION_RE = re.compile(
    r"(CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION[\s\S]*?LANGUAGE\s+plpgsql)"
    r"(\s*(?:VOLATILE|STABLE|IMMUTABLE)\b)?"
    r"(\s*;)",
    re.IGNORECASE,
)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("file")
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    target = Path(args.file)
    if not target.exists():
        sys.stderr.write(f"file not found: {target}\n")
        return 2

    try:
        original = target.read_text(encoding="utf-8")
    except UnicodeDecodeError as exc:
        sys.stderr.write(f"file not UTF-8: {exc}\n")
        return 2

    if args.verify:
        return _verify(original)

    return _apply(target, original)


def _verify(content: str) -> int:
    """Check todos los CREATE FUNCTION tienen marker explicito."""
    missing = 0
    for match in CREATE_FUNCTION_RE.finditer(content):
        marker = match.group(2)
        if marker is None or not marker.strip():
            missing += 1
    if missing:
        sys.stderr.write(f"{missing} CREATE FUNCTION without volatility marker\n")
        return 1
    return 0


def _apply(target: Path, original: str) -> int:
    def replacer(m: re.Match[str]) -> str:
        prefix = m.group(1)
        marker = m.group(2)
        terminator = m.group(3)
        if marker and marker.strip():
            return m.group(0)
        return f"{prefix} VOLATILE{terminator}"

    new_content = CREATE_FUNCTION_RE.sub(replacer, original)

    if new_content == original:
        sys.stdout.write("no changes (all functions already have volatility marker)\n")
        return 0

    target.write_text(new_content, encoding="utf-8")
    applied = sum(
        1
        for m in CREATE_FUNCTION_RE.finditer(original)
        if not (m.group(2) and m.group(2).strip())
    )
    sys.stdout.write(f"applied={applied}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
