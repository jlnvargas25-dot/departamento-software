"""Dataclasses inmutables del correction-adr-draft."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Optional


class DraftStatus(str, Enum):
    """Terminal status of a Tier C draft generation attempt.

    Attributes:
        CREATED: ADR draft file was created successfully.
        NO_OP: ADR draft already exists for this finding (idempotency).
        SKIPPED: action_hint not recognized.
    """

    CREATED = "created"
    NO_OP = "no_op"
    SKIPPED = "skipped"


@dataclass(frozen=True)
class DraftResult:
    """Result of processing a single Tier C finding.

    Attributes:
        rule_id: The rule that triggered the finding.
        file: Source file where the finding was detected.
        line: Line number of the finding.
        action_hint: The action_hint from rules.yaml.
        status: Terminal status (created, no_op, or skipped).
        adr_path: Path to the generated ADR file (only if status is CREATED).
        summary: Short description of what was generated.
    """

    rule_id: str
    file: str
    line: int
    action_hint: str
    status: DraftStatus
    adr_path: Optional[str] = None
    summary: Optional[str] = None
