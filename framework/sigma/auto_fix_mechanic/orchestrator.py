"""Orchestrator + escalation logic — S-5.

Orquesta el flow per finding:
    1. Lookup handler por rule_id
    2. Si None -> escalated_to_c (handler_not_implemented)
    3. Si optional_tool_unavailable -> escalated_to_c sin invocar
    4. Snapshot pre-fix (atomic rollback ready)
    5. Invocar tool via invoker
    6a. Tool crash -> rollback atomico + rolled_back
    6b. Verification fail -> rollback + rolled_back
    6c. Verification OK + archivo cambio -> applied
    6d. Verification OK + archivo NO cambio -> noop_already_clean (AM7)
"""

import sys
import time
from pathlib import Path

from sigma.auto_fix_mechanic.invoker import (
    InvokeResult,
    ToolNotFoundError,
    ToolTimeoutError,
    invoke_tool,
)
from sigma.auto_fix_mechanic.models import (
    ClassifiedFinding,
    FixStatus,
    Handler,
    PatchResult,
    VerificationResult,
)
from sigma.auto_fix_mechanic.snapshot import FileSnapshot
from sigma.auto_fix_mechanic.verifier import run_verification


def process_finding(
    finding: ClassifiedFinding, handlers: dict[str, Handler]
) -> PatchResult:
    """Procesa un finding Tier A. Retorna PatchResult con el resultado terminal.

    NO modifica archivos fuera de finding.file. NO escala silenciosamente.
    """
    start_ms = _now_ms()

    handler = handlers.get(finding.rule_id)
    if handler is None:
        _log("escalated_to_c", finding, reason="handler_not_implemented")
        return PatchResult(
            rule_id=finding.rule_id,
            file=finding.file,
            line=finding.line,
            action_hint=finding.action_hint,
            fix_status=FixStatus.ESCALATED_TO_C,
            verification=VerificationResult.NOT_ATTEMPTED,
            escalation_reason="handler_not_implemented",
            elapsed_ms=_elapsed(start_ms),
        )

    if handler.optional_tool_unavailable:
        reason = f"optional_tool_unavailable:{handler.tool}"
        _log("escalated_to_c", finding, reason=reason)
        return PatchResult(
            rule_id=finding.rule_id,
            file=finding.file,
            line=finding.line,
            action_hint=finding.action_hint,
            tool_used=handler.tool,
            fix_status=FixStatus.ESCALATED_TO_C,
            verification=VerificationResult.NOT_ATTEMPTED,
            escalation_reason=reason,
            elapsed_ms=_elapsed(start_ms),
        )

    file_path = Path(finding.file)
    try:
        snapshot = FileSnapshot(file_path)
    except (FileNotFoundError, OSError) as exc:
        _log("escalated_to_c", finding, reason=f"file_not_accessible:{exc}")
        return PatchResult(
            rule_id=finding.rule_id,
            file=finding.file,
            line=finding.line,
            action_hint=finding.action_hint,
            tool_used=handler.tool,
            fix_status=FixStatus.ESCALATED_TO_C,
            verification=VerificationResult.NOT_ATTEMPTED,
            escalation_reason=f"file_not_accessible:{type(exc).__name__}",
            elapsed_ms=_elapsed(start_ms),
        )

    with snapshot:
        # 1. Invoke tool
        invoke_result = _safe_invoke(handler, file_path)
        if isinstance(invoke_result, _InvokeFailure):
            snapshot.restore()
            _log("rolled_back", finding, reason=invoke_result.reason)
            return PatchResult(
                rule_id=finding.rule_id,
                file=finding.file,
                line=finding.line,
                action_hint=finding.action_hint,
                tool_used=handler.tool,
                fix_status=FixStatus.ROLLED_BACK,
                verification=VerificationResult.FAILED,
                rollback_reason=invoke_result.reason,
                elapsed_ms=_elapsed(start_ms),
            )

        # 2. Verify post-fix
        verify_result = run_verification(handler.verification, file_path)
        if not verify_result.passed:
            snapshot.restore()
            reason = f"post_fix_verification_failed:{verify_result.detail}"
            _log("rolled_back", finding, reason=reason)
            return PatchResult(
                rule_id=finding.rule_id,
                file=finding.file,
                line=finding.line,
                action_hint=finding.action_hint,
                tool_used=handler.tool,
                fix_status=FixStatus.ROLLED_BACK,
                verification=VerificationResult.FAILED,
                rollback_reason=reason,
                elapsed_ms=_elapsed(start_ms),
            )

        # 3. Verify OK -> applied or noop (AM7 idempotencia)
        if snapshot.unchanged():
            _log("noop_already_clean", finding, reason="pattern_absent_pre_fix")
            return PatchResult(
                rule_id=finding.rule_id,
                file=finding.file,
                line=finding.line,
                action_hint=finding.action_hint,
                tool_used=handler.tool,
                fix_status=FixStatus.NOOP_ALREADY_CLEAN,
                verification=VerificationResult.PASSED,
                elapsed_ms=_elapsed(start_ms),
            )

        patch_summary = snapshot.diff_summary()
        _log("applied", finding, reason=patch_summary)
        return PatchResult(
            rule_id=finding.rule_id,
            file=finding.file,
            line=finding.line,
            action_hint=finding.action_hint,
            tool_used=handler.tool,
            fix_status=FixStatus.APPLIED,
            verification=VerificationResult.PASSED,
            patch_summary=patch_summary,
            elapsed_ms=_elapsed(start_ms),
        )


def run_batch(
    findings: list[ClassifiedFinding], handlers: dict[str, Handler]
) -> list[PatchResult]:
    """Procesa una lista de findings. Filtra a tier='A' (los otros tier los ignora).

    AC-S5-7: input vacio -> retorna [].
    """
    tier_a = [f for f in findings if f.tier == "A"]
    return [process_finding(f, handlers) for f in tier_a]


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------


class _InvokeFailure:
    """Wrapper para resultado de invocacion que requiere rollback."""

    __slots__ = ("reason",)

    def __init__(self, reason: str):
        self.reason = reason


def _safe_invoke(handler: Handler, file: Path):
    """Invoca tool y wrappea errores como _InvokeFailure (para forzar rollback).

    Retorna InvokeResult si exit_code == 0, _InvokeFailure si:
    - exit_code != 0 (tool reporto error)
    - ToolNotFoundError (tool no en PATH al runtime)
    - ToolTimeoutError (excedio timeout)
    - ValueError (invocation malformada — no deberia pasar post-loader)
    """
    try:
        result = invoke_tool(handler, file)
    except ToolNotFoundError as exc:
        return _InvokeFailure(f"tool_not_found_at_runtime:{exc}")
    except ToolTimeoutError as exc:
        return _InvokeFailure(f"tool_timeout:{exc}")
    except ValueError as exc:
        return _InvokeFailure(f"invocation_malformed:{exc}")

    if result.exit_code != 0:
        detail = (result.stderr or result.stdout or f"exit {result.exit_code}").strip()
        if len(detail) > 200:
            detail = detail[:197] + "..."
        return _InvokeFailure(f"tool_invocation_failed:{detail}")
    return result


def _now_ms() -> int:
    return int(time.monotonic() * 1000)


def _elapsed(start_ms: int) -> int:
    return _now_ms() - start_ms


def _log(event: str, finding: ClassifiedFinding, reason: str = "") -> None:
    """Logging estructurado a stderr (line-per-event, parseable)."""
    print(
        f"[mechanic] event={event} rule_id={finding.rule_id} "
        f"file={finding.file}:{finding.line} reason={reason}",
        file=sys.stderr,
    )
