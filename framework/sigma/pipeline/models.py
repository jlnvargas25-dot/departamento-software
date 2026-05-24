"""Modelos del pipeline E2E."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class PipelineResult:
    """Aggregated result from dispatching findings through all tier handlers.

    Attributes:
        tier_a_results: PatchResult dicts from auto_fix_mechanic.
        tier_b_results: CorrectionResult dicts from correction_agent_bounded.
        tier_c_results: DraftResult dicts from correction_adr_draft.
        summary: Aggregate counts by tier and status.
    """

    tier_a_results: list[dict[str, Any]] = field(default_factory=list)
    tier_b_results: list[dict[str, Any]] = field(default_factory=list)
    tier_c_results: list[dict[str, Any]] = field(default_factory=list)
    summary: dict[str, int] = field(default_factory=dict)
