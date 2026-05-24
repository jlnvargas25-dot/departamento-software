"""Tests para M3 empirical measurement — S-8 / AM8.

M3 target real: ≥90% Tier A auto-fix sin intervencion humana (target del ADR-011
para promotion a v1.0 ACCEPTED).

Test gate: ≥50% sobre fixture sintetica (sandbox-friendly threshold).
Real measurement contra ESLint/Prettier/ts-morph reales se ejecutara en CI cuando
el environment tenga el stack TS completo instalado.

Estrategia del test:
  - Usar python -c como tool sintetico (NO requiere eslint/prettier en CI Python)
  - Construir handlers stub que aplican fix "siempre OK" para medir el flow del
    orchestrator, NO la calidad real del codemod
  - El M3 real sobre catalogo Tier A v0.1.0 se mide en E2E con stack TS
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

from sigma.auto_fix_mechanic.models import (
    ClassifiedFinding,
    FixStatus,
    Handler,
)
from sigma.auto_fix_mechanic.orchestrator import run_batch


PYTHON = f'"{sys.executable}"'


def _make_handler_writes_then_verifies_ok(rule_id: str) -> Handler:
    """Handler stub: tool aplica un cambio + verify exit 0."""
    return Handler(
        rule_id=rule_id,
        tool="stub",
        invocation=f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'fixed-by-{rule_id}\')" <file>',
        verification={
            "method": "re-run-eslint",
            "command": f'{PYTHON} -c "import sys;sys.exit(0)"',
        },
    )


def _make_handler_writes_then_verifies_fails(rule_id: str) -> Handler:
    """Handler stub: tool aplica pero verify fail -> rollback."""
    return Handler(
        rule_id=rule_id,
        tool="stub",
        invocation=f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'bad\')" <file>',
        verification={
            "method": "re-run-eslint",
            "command": f'{PYTHON} -c "import sys;sys.exit(1)"',
        },
    )


def _finding(rule_id: str, file: Path) -> ClassifiedFinding:
    return ClassifiedFinding(
        rule_id=rule_id, file=str(file), line=1, tier="A", action_hint="stub-fix"
    )


def test_m3_all_handlers_succeed(tmp_path: Path):
    """M3 = 100% cuando todos los handlers aplican exitosamente."""
    findings = []
    handlers = {}
    for i in range(10):
        f = tmp_path / f"f{i}.ts"
        f.write_text("pre-fix")
        rule_id = f"R-{i}"
        findings.append(_finding(rule_id, f))
        handlers[rule_id] = _make_handler_writes_then_verifies_ok(rule_id)

    results = run_batch(findings, handlers)
    applied = sum(1 for r in results if r.fix_status is FixStatus.APPLIED)
    m3 = applied / len(results)
    assert m3 == 1.0, f"expected M3=100%, got {m3:.2%}"


def test_m3_partial_failures_reflected_in_metric(tmp_path: Path):
    """M3 baja proporcionalmente cuando algunos handlers fallan verify."""
    findings = []
    handlers = {}
    for i in range(10):
        f = tmp_path / f"f{i}.ts"
        f.write_text("pre-fix")
        rule_id = f"R-{i}"
        findings.append(_finding(rule_id, f))
        # 3 de 10 fallan verify
        if i < 3:
            handlers[rule_id] = _make_handler_writes_then_verifies_fails(rule_id)
        else:
            handlers[rule_id] = _make_handler_writes_then_verifies_ok(rule_id)

    results = run_batch(findings, handlers)
    applied = sum(1 for r in results if r.fix_status is FixStatus.APPLIED)
    rolled_back = sum(1 for r in results if r.fix_status is FixStatus.ROLLED_BACK)
    m3 = applied / len(results)
    assert applied == 7
    assert rolled_back == 3
    assert m3 == 0.7


def test_m3_above_sandbox_threshold_on_fixture(tmp_path: Path):
    """Gate del test: M3 >= 0.5 sobre fixture sintetica.

    Sandbox threshold; M3 real >= 0.9 se mide en E2E con stack TS completo.
    """
    findings = []
    handlers = {}
    # 8 de 10 succeed, 2 escalated por handler missing
    for i in range(10):
        f = tmp_path / f"f{i}.ts"
        f.write_text("pre-fix")
        rule_id = f"R-{i}"
        findings.append(_finding(rule_id, f))
        if i < 8:
            handlers[rule_id] = _make_handler_writes_then_verifies_ok(rule_id)
        # rule_ids 8 y 9 no tienen handler -> escalation

    results = run_batch(findings, handlers)
    applied = sum(1 for r in results if r.fix_status is FixStatus.APPLIED)
    m3 = applied / len(results)
    assert m3 >= 0.5, f"sandbox gate M3>=0.5 failed: got {m3:.2%}"
