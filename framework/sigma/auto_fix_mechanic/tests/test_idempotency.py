"""Tests para idempotencia AM7 — S-8.

AM7: aplicar dos veces el mismo input -> segunda corrida los findings que ya
fueron applied retornan NOOP_ALREADY_CLEAN.
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


def _idempotent_handler(rule_id: str) -> Handler:
    """Handler que escribe contenido fijo. Idempotente: segunda corrida no cambia bytes."""
    return Handler(
        rule_id=rule_id,
        tool="stub",
        invocation=f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'fixed\')" <file>',
        verification={
            "method": "re-run-eslint",
            "command": f'{PYTHON} -c "import sys;sys.exit(0)"',
        },
    )


def test_first_run_applies_second_run_is_noop(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("pre-fix-content")
    handler = _idempotent_handler("R-1")
    finding = ClassifiedFinding(
        rule_id="R-1", file=str(f), line=1, tier="A", action_hint="fix"
    )

    first = run_batch([finding], {"R-1": handler})
    assert first[0].fix_status is FixStatus.APPLIED
    assert f.read_text() == "fixed"

    # Segunda corrida: archivo ya esta fixed -> handler escribe 'fixed' (no cambia) -> noop
    second = run_batch([finding], {"R-1": handler})
    assert second[0].fix_status is FixStatus.NOOP_ALREADY_CLEAN
    assert f.read_text() == "fixed"


def test_third_run_also_noop(tmp_path: Path):
    """Idempotencia estable: tercera, cuarta corrida tambien noop."""
    f = tmp_path / "x.ts"
    f.write_text("pre")
    handler = _idempotent_handler("R-1")
    finding = ClassifiedFinding(
        rule_id="R-1", file=str(f), line=1, tier="A", action_hint="fix"
    )
    handlers = {"R-1": handler}

    run_batch([finding], handlers)  # first
    second = run_batch([finding], handlers)
    third = run_batch([finding], handlers)

    assert second[0].fix_status is FixStatus.NOOP_ALREADY_CLEAN
    assert third[0].fix_status is FixStatus.NOOP_ALREADY_CLEAN


def test_idempotency_with_mixed_status(tmp_path: Path):
    """Mix de findings: applied + escalation. Segunda corrida applied->noop, escalation->escalation."""
    f1 = tmp_path / "a.ts"
    f1.write_text("a")
    f2 = tmp_path / "b.ts"
    f2.write_text("b")
    findings = [
        ClassifiedFinding(rule_id="R-1", file=str(f1), line=1, tier="A"),
        ClassifiedFinding(rule_id="UNKNOWN", file=str(f2), line=1, tier="A"),
    ]
    handlers = {"R-1": _idempotent_handler("R-1")}

    first = run_batch(findings, handlers)
    assert first[0].fix_status is FixStatus.APPLIED
    assert first[1].fix_status is FixStatus.ESCALATED_TO_C

    second = run_batch(findings, handlers)
    assert second[0].fix_status is FixStatus.NOOP_ALREADY_CLEAN
    assert second[1].fix_status is FixStatus.ESCALATED_TO_C  # escalation deterministic
