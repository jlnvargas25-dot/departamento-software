"""Auto-detect next ADR number from existing files in adr_directory."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Union

_ADR_NUMBER_RE = re.compile(r"ADR-(\d+)")


def next_adr_number(adr_directory: Union[str, Path]) -> int:
    """Scan adr_directory for existing ADR-NNN files and return max + 1.

    Args:
        adr_directory: Path to the directory containing ADR files.

    Returns:
        Next available ADR number. Returns 1 if no ADRs exist.
    """
    d = Path(adr_directory)
    if not d.is_dir():
        return 1

    numbers: list[int] = []
    for f in d.iterdir():
        m = _ADR_NUMBER_RE.search(f.name)
        if m:
            numbers.append(int(m.group(1)))

    return max(numbers) + 1 if numbers else 1


def adr_slug(rule_id: str, file_path: str) -> str:
    """Generate a kebab-case slug from rule_id and file context.

    Args:
        rule_id: The rule identifier (e.g. "CSP-UNSAFE-EVAL").
        file_path: Source file path for context.

    Returns:
        Kebab-case slug suitable for ADR filenames.
    """
    base = rule_id.lower().replace("_", "-")
    file_stem = Path(file_path).stem.replace("_", "-")
    return f"{base}-{file_stem}"
