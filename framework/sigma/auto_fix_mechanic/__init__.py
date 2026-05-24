"""sigma.auto_fix_mechanic — Tier A handler de la trinidad correctiva (ADR-011).

Componente que aplica codemods deterministicos a findings clasificados como
Tier A por sigma.finding_classifier. Sin LLM en el path de fix. Verificacion
post-fix obligatoria. Rollback atomico si verificacion falla.

Public API (se va poblando con cada story S-1..S-8):
    load_handlers(yaml_path) -> dict[str, Handler]   (S-1)
    run_preflight_check(handlers) -> ToolboxStatus   (S-2)
    FileSnapshot(path)                                (S-3)
    run_verification(spec, file) -> VerifyResult     (S-4)
    process_finding(finding, handlers) -> PatchResult (S-5)
    run_batch(findings, handlers) -> list[PatchResult] (S-5)
"""

from sigma.auto_fix_mechanic.loader import load_handlers
from sigma.auto_fix_mechanic.models import (
    ClassifiedFinding,
    FixStatus,
    Handler,
    PatchResult,
    ToolboxStatus,
    VerificationResult,
)
from sigma.auto_fix_mechanic.orchestrator import process_finding, run_batch

__all__ = [
    "ClassifiedFinding",
    "FixStatus",
    "Handler",
    "PatchResult",
    "ToolboxStatus",
    "VerificationResult",
    "load_handlers",
    "process_finding",
    "run_batch",
]
__version__ = "0.1.0"
