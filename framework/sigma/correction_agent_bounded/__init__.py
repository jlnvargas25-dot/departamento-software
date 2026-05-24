"""sigma:correction_agent_bounded — Tier B handler (ADR-011 Phase 2).

Sub-agente correctivo acotado: genera patches via LLM con contrato estricto
(template + project_context + verificacion deterministica post-fix).
"""

from sigma.correction_agent_bounded.models import (
    CorrectionResult,
    CorrectionStatus,
    ProjectContext,
    TemplateConfig,
)

__all__ = [
    "CorrectionResult",
    "CorrectionStatus",
    "ProjectContext",
    "TemplateConfig",
]
