"""sigma:pipeline — E2E dispatcher (ADR-011 Phase 2 integration).

Routes classified findings to tier-specific handlers:
  tier=A → auto_fix_mechanic
  tier=B → correction_agent_bounded
  tier=C → correction_adr_draft
"""

from sigma.pipeline.dispatcher import dispatch

__all__ = ["dispatch"]
