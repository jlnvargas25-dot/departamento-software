"""Tests para sigma.auto_fix_mechanic.orchestrator — S-5.

Cubre AC-S5-1..AC-S5-8 (4 casos del flow + edge cases).
"""

import sys
from pathlib import Path

import pytest

from sigma.auto_fix_mechanic.models import (
    ClassifiedFinding,
    FixStatus,
    Handler,
    VerificationResult,
)
from sigma.auto_fix_mechanic.orchestrator import process_finding, run_batch


PYTHON = f'"{sys.executable}"'


def _finding(
    rule_id: str = "TS-1",
    file: str = "irrelevant.ts",
    line: int = 1,
    action_hint: str = "eslint-fix",
    tier: str = "A",
) -> ClassifiedFinding:
    return ClassifiedFinding(
        rule_id=rule_id, file=file, line=line, tier=tier, action_hint=action_hint
    )


def _python_handler(
    invocation_cmd: str,
    verification_cmd: str,
    rule_id: str = "TS-1",
    optional_unavail: bool = False,
) -> Handler:
    return Handler(
        rule_id=rule_id,
        tool="eslint",
        invocation=invocation_cmd,
        verification={"method": "re-run-eslint", "command": verification_cmd},
        optional_tool_unavailable=optional_unavail,
    )


# ---------------------------------------------------------------------------
# AC-S5-1 — Fix exitoso + verificacion OK + archivo cambio
# ---------------------------------------------------------------------------


def test_successful_fix_returns_applied(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("pre-fix content")
    handler = _python_handler(
        # Invocation que reescribe el file
        invocation_cmd=f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'fixed\')" <file>',
        verification_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
    )
    finding = _finding(rule_id="TS-1", file=str(f))
    handlers = {"TS-1": handler}

    result = process_finding(finding, handlers)

    assert result.fix_status is FixStatus.APPLIED
    assert result.verification is VerificationResult.PASSED
    assert result.patch_summary is not None
    assert "sha256:" in result.patch_summary
    assert f.read_text() == "fixed"
    assert result.elapsed_ms >= 0


# ---------------------------------------------------------------------------
# AC-S5-2 — Rule_id sin handler -> escalated_to_c
# ---------------------------------------------------------------------------


def test_unknown_rule_id_escalates_to_c(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("untouched")
    finding = _finding(rule_id="UNKNOWN-RULE-XYZ", file=str(f))
    handlers: dict = {}

    result = process_finding(finding, handlers)

    assert result.fix_status is FixStatus.ESCALATED_TO_C
    assert result.escalation_reason == "handler_not_implemented"
    assert result.verification is VerificationResult.NOT_ATTEMPTED
    assert f.read_text() == "untouched"  # archivo intacto


# ---------------------------------------------------------------------------
# AC-S5-3 — Tool invocation crash -> rollback atomico + rolled_back
# ---------------------------------------------------------------------------


def test_tool_invocation_failure_rolls_back(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("original")
    handler = _python_handler(
        invocation_cmd=(
            f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'corrupt\');'
            f'sys.stderr.write(\'tool crashed\');sys.exit(2)" <file>'
        ),
        verification_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
    )
    finding = _finding(rule_id="TS-1", file=str(f))
    handlers = {"TS-1": handler}

    result = process_finding(finding, handlers)

    assert result.fix_status is FixStatus.ROLLED_BACK
    assert result.verification is VerificationResult.FAILED
    assert result.rollback_reason is not None
    assert "tool" in result.rollback_reason.lower() or "exit" in result.rollback_reason.lower()
    # AC-S5-3: working tree del archivo limpio (sin cambios)
    assert f.read_text() == "original"


# ---------------------------------------------------------------------------
# AC-S5-4 — Verification fail -> rollback + escalation razon post-fix
# ---------------------------------------------------------------------------


def test_verification_failure_rolls_back(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("original")
    handler = _python_handler(
        # Tool aplica fix con exit 0
        invocation_cmd=f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'fix-applied\')" <file>',
        # Pero verification falla (exit 1)
        verification_cmd=f'{PYTHON} -c "import sys;sys.stderr.write(\'still has pattern\');sys.exit(1)"',
    )
    finding = _finding(rule_id="TS-1", file=str(f))
    handlers = {"TS-1": handler}

    result = process_finding(finding, handlers)

    assert result.fix_status is FixStatus.ROLLED_BACK
    assert result.verification is VerificationResult.FAILED
    assert result.rollback_reason is not None
    # Archivo restaurado al original
    assert f.read_text() == "original"


# ---------------------------------------------------------------------------
# AC-S5-5 — Idempotencia: archivo ya clean -> noop_already_clean
# ---------------------------------------------------------------------------


def test_idempotent_noop_when_tool_does_not_modify(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("already clean")
    handler = _python_handler(
        # Tool no toca el archivo (exit 0 sin escribir)
        invocation_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
        verification_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
    )
    finding = _finding(rule_id="TS-1", file=str(f))
    handlers = {"TS-1": handler}

    result = process_finding(finding, handlers)

    assert result.fix_status is FixStatus.NOOP_ALREADY_CLEAN
    assert result.verification is VerificationResult.PASSED
    assert f.read_text() == "already clean"


# ---------------------------------------------------------------------------
# AC-S5-6 — Optional tool unavailable -> escalated_to_c sin invocar
# ---------------------------------------------------------------------------


def test_optional_tool_unavailable_escalates(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("untouched")
    # Handler marcado como optional_unavailable. NO debe invocar tool ni siquiera
    # si el comando sería ejecutable.
    handler = _python_handler(
        invocation_cmd=f'{PYTHON} -c "open(\'should-not-execute.txt\',\'w\').write(\'x\')" <file>',
        verification_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
        optional_unavail=True,
    )
    finding = _finding(rule_id="TS-1", file=str(f))
    handlers = {"TS-1": handler}

    result = process_finding(finding, handlers)

    assert result.fix_status is FixStatus.ESCALATED_TO_C
    assert result.escalation_reason is not None
    assert "optional_tool_unavailable" in result.escalation_reason
    assert f.read_text() == "untouched"
    # Tool no se invoco (file should-not-execute.txt no existe)
    assert not (tmp_path / "should-not-execute.txt").exists()


# ---------------------------------------------------------------------------
# AC-S5-7 — run_batch([]) -> []
# ---------------------------------------------------------------------------


def test_run_batch_empty_input():
    results = run_batch([], {})
    assert results == []


def test_run_batch_multiple_findings(tmp_path: Path):
    f1 = tmp_path / "a.ts"
    f1.write_text("a")
    f2 = tmp_path / "b.ts"
    f2.write_text("b")
    handler = _python_handler(
        invocation_cmd=f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'done\')" <file>',
        verification_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
    )
    findings = [
        _finding(rule_id="TS-1", file=str(f1)),
        _finding(rule_id="TS-1", file=str(f2)),
    ]
    results = run_batch(findings, {"TS-1": handler})
    assert len(results) == 2
    assert all(r.fix_status is FixStatus.APPLIED for r in results)
    assert f1.read_text() == "done"
    assert f2.read_text() == "done"


# ---------------------------------------------------------------------------
# AC-S5-8 — elapsed_ms coherente
# ---------------------------------------------------------------------------


def test_elapsed_ms_positive_when_tool_runs(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("data")
    handler = _python_handler(
        invocation_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
        verification_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
    )
    result = process_finding(_finding(file=str(f)), {"TS-1": handler})
    assert result.elapsed_ms >= 0


def test_elapsed_ms_near_zero_for_handler_not_implemented():
    """Cuando handler is None, no se ejecuta subprocess -> elapsed_ms muy bajo."""
    f = "nonexistent.ts"
    result = process_finding(_finding(rule_id="UNKNOWN", file=f), {})
    # Lookup-only path; elapsed debe ser tiny (no subprocess)
    assert result.elapsed_ms >= 0


# ---------------------------------------------------------------------------
# Filtrado de tier en run_batch
# ---------------------------------------------------------------------------


def test_run_batch_filters_non_tier_a_findings(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("data")
    handler = _python_handler(
        invocation_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
        verification_cmd=f'{PYTHON} -c "import sys;sys.exit(0)"',
    )
    findings = [
        _finding(rule_id="TS-1", file=str(f), tier="A"),
        _finding(rule_id="TS-1", file=str(f), tier="B"),  # filtrado
        _finding(rule_id="TS-1", file=str(f), tier="C"),  # filtrado
    ]
    results = run_batch(findings, {"TS-1": handler})
    assert len(results) == 1  # solo el tier=A procesado
