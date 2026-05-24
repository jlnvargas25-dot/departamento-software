"""Aplica patches de texto a archivos — reemplazo por line range."""

from __future__ import annotations

from pathlib import Path
from typing import Union


def apply_patch(
    file_path: Union[str, Path],
    line: int,
    replacement: str,
    context_window: int = 20,
) -> bool:
    """Replace a block of lines around `line` with `replacement`. Returns True if changed."""
    p = Path(file_path)
    lines = p.read_text(encoding="utf-8").splitlines(keepends=True)

    start = max(0, line - 1 - context_window)
    end = min(len(lines), line + context_window)

    original_block = "".join(lines[start:end])

    if not replacement.endswith("\n"):
        replacement += "\n"

    if original_block.strip() == replacement.strip():
        return False

    new_lines = lines[:start] + [replacement] + lines[end:]
    p.write_text("".join(new_lines), encoding="utf-8")
    return True


def apply_new_file(file_path: Union[str, Path], content: str) -> bool:
    """Create a new file with content, creating parent directories as needed."""
    p = Path(file_path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(content, encoding="utf-8")
    return True
