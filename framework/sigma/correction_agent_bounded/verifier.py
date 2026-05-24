"""Verificacion post-fix deterministica (regex) + opt-out detection."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Union


def check_pattern(
    file_path: Union[str, Path], pattern: str, line: int | None = None, window: int = 30
) -> bool:
    """Return True if regex `pattern` matches in the file, optionally scoped to a line window."""
    p = Path(file_path)
    if not p.exists():
        return False
    content = p.read_text(encoding="utf-8")

    if line is not None:
        lines = content.splitlines()
        start = max(0, line - 1 - window)
        end = min(len(lines), line + window)
        content = "\n".join(lines[start:end])

    return bool(re.search(pattern, content))


def check_file_exists(path: Union[str, Path]) -> bool:
    """Return True if file exists at path."""
    return Path(path).exists()


def check_opt_out(
    file_path: Union[str, Path], marker: str, line: int, window: int = 5
) -> bool:
    """Return True if opt-out marker string is found near the given line."""
    p = Path(file_path)
    if not p.exists():
        return False
    lines = p.read_text(encoding="utf-8").splitlines()
    start = max(0, line - 1 - window)
    end = min(len(lines), line + window)
    region = "\n".join(lines[start:end])
    return marker in region
