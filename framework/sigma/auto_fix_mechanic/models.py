"""Dataclasses inmutables del mechanic — S-1 foundation.

Contrato publico:
    PatchResult       — un resultado por finding Tier A procesado.

Tipos internos:
    Handler           — entry del rules.yaml.
    ToolboxStatus     — output del pre-flight check (S-2).

Enums:
    FixStatus         — applied | rolled_back | escalated_to_c | noop_already_clean
    VerificationResult — passed | failed | not_attempted

Todos los dataclasses son frozen (R-5 reversibilidad, A12 zero trust testabilidad,
inmutabilidad del PRD C8). La inmutabilidad transitiva del campo verification (dict)
no esta garantizada por el sistema de tipos — convencion: NO mutar tras construccion.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class FixStatus(str, Enum):
    """Resultado terminal del intento de fix sobre un finding Tier A."""

    APPLIED = "applied"
    ROLLED_BACK = "rolled_back"
    ESCALATED_TO_C = "escalated_to_c"
    NOOP_ALREADY_CLEAN = "noop_already_clean"


class VerificationResult(str, Enum):
    """Resultado de la verificacion post-fix (AC-S4-1..AC-S4-5)."""

    PASSED = "passed"
    FAILED = "failed"
    NOT_ATTEMPTED = "not_attempted"


@dataclass(frozen=True)
class Handler:
    """Entry declarativa del rules.yaml. Un Handler por rule_id Tier A.

    Si optional_tool_unavailable=True, el pre-flight check detecto que un tool
    opcional requerido por este handler falta del environment. El orquestador
    escala a Tier C en lugar de invocar.
    """

    rule_id: str
    tool: str  # eslint | prettier | ts-morph-custom | python-custom-script
    invocation: Optional[str] = None
    codemod_script: Optional[str] = None
    pattern_target: str = ""
    transformation: str = ""
    verification: dict = field(default_factory=dict)
    rollback_strategy: str = "file-level-revert"
    notes: Optional[str] = None
    optional_tool_unavailable: bool = False


@dataclass(frozen=True)
class ToolboxStatus:
    """Salida del pre-flight check (AM9 del PRD).

    required_tools_ok=False => el mechanic NO arranca (fail-fast).
    optional_tools_ok=False => handlers cuyo tool opcional falta quedan disabled.
    disabled_handlers contiene los rule_ids afectados.
    """

    required_tools_ok: bool
    optional_tools_ok: bool
    missing_required: list[str] = field(default_factory=list)
    missing_optional: list[str] = field(default_factory=list)
    disabled_handlers: list[str] = field(default_factory=list)


@dataclass(frozen=True)
class ClassifiedFinding:
    """Input al mechanic — formato esperado del output del classifier.

    Modelo minimo provider-agnostic. El mechanic solo procesa los que tienen
    tier == 'A'. Otros campos (severity, message, source) son informativos.
    """

    rule_id: str
    file: str
    line: int
    tier: str  # "A" | "B" | "C"
    action_hint: str = ""
    severity: str = ""
    message: str = ""
    source: str = ""


@dataclass(frozen=True)
class PatchResult:
    """Un resultado por finding Tier A procesado. Contrato publico del mechanic.

    fix_status:
        APPLIED            — codemod aplico + verificacion paso.
        ROLLED_BACK        — codemod aplico pero verificacion fallo -> rollback atomico.
                             rollback_reason explica por que.
        ESCALATED_TO_C     — handler ausente o optional tool unavailable -> nada se toco.
                             escalation_reason explica por que.
        NOOP_ALREADY_CLEAN — codemod corrio pero patron ya no estaba (idempotencia AM7).
    """

    rule_id: str
    file: str
    line: int
    action_hint: str
    fix_status: FixStatus
    verification: VerificationResult
    patch_summary: Optional[str] = None
    rollback_reason: Optional[str] = None
    escalation_reason: Optional[str] = None
    tool_used: Optional[str] = None
    elapsed_ms: int = 0
