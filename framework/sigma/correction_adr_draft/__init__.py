"""sigma:correction_adr_draft — Tier C handler (ADR-011 Phase 2).

Generates ADR drafts and structured summaries for findings that require
human decision. No LLM, no auto-fix — template-based document generation.
"""

from sigma.correction_adr_draft.models import DraftResult, DraftStatus

__all__ = ["DraftResult", "DraftStatus"]
