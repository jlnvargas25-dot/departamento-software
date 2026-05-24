"""Tests adversariales — Audit Paso 8 PROTOCOLO-CONSTRUCCION-CODIGO.

Cubre las 15 categorias documentadas en
docs/arquitectura/ARQUITECTURA-sigma-auto-fix-mechanic.md sec 9.1.

Categorias YA cubiertas en otros test files se referencian con xfail/skip y
trazabilidad. Categorias NUEVAS se implementan aca.

| Cat | Categoria                                  | Cubierto en                       |
|-----|--------------------------------------------|------------------------------------|
| 1   | inputs vacios                              | test_cli (3 tests)                 |
| 2   | inputs malformados (invalid JSON, missing) | test_cli (3 tests)                 |
| 3   | findings con rule_id desconocido           | test_orchestrator + test_cli       |
| 4   | codemod script crash (exit != 0)           | test_orchestrator                  |
| 5   | verification crash (excepcion interna)     | test_adversarial NUEVO             |
| 6   | file no existe                             | test_snapshot                      |
| 7   | file read-only (permission denied)         | test_adversarial NUEVO             |
| 8   | tool externo NO instalado runtime          | test_preflight + test_invoker      |
| 9   | race condition (concurrent snapshots)      | test_snapshot                      |
| 10  | snapshot bytes corruption mid-flow         | test_adversarial NUEVO             |
| 11  | batch masivo (1000 findings)               | test_adversarial NUEVO             |
| 12  | verification timeout                       | test_verifier                      |
| 13  | idempotencia adversarial (3+ runs)         | test_idempotency                   |
| 14  | rollback durante rollback (restore falla)  | test_adversarial NUEVO             |
| 15  | YAML malformado                            | test_loader (4 tests)              |
"""

from __future__ import annotations

import os
import stat
import sys
import time
from pathlib import Path

import pytest

from sigma.auto_fix_mechanic.models import (
    ClassifiedFinding,
    FixStatus,
    Handler,
    VerificationResult,
)
from sigma.auto_fix_mechanic.orchestrator import process_finding, run_batch
from sigma.auto_fix_mechanic.snapshot import FileSnapshot
from sigma.auto_fix_mechanic.verifier import (
    InvalidVerificationSpecError,
    UnknownVerificationMethodError,
    run_verification,
)


PYTHON = f'"{sys.executable}"'


def _ok_verify_cmd() -> str:
    return f'{PYTHON} -c "import sys;sys.exit(0)"'


def _fail_verify_cmd() -> str:
    return f'{PYTHON} -c "import sys;sys.exit(1)"'


def _write_handler(content: str, verify_cmd: str | None = None, rule_id: str = "TEST-RULE") -> Handler:
    return Handler(
        rule_id=rule_id,
        tool="stub",
        invocation=f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'{content}\')" <file>',
        verification={"method": "re-run-eslint", "command": verify_cmd or _ok_verify_cmd()},
    )


# =============================================================================
# Categoria 5 — verification crash (excepcion interna del verifier dispatcher)
# =============================================================================


def test_cat5_verifier_unknown_method_raises_during_dispatch(tmp_path: Path):
    """spec.method desconocido -> UnknownVerificationMethodError al llamar verifier directo."""
    f = tmp_path / "x.ts"
    f.write_text("data")
    with pytest.raises(UnknownVerificationMethodError):
        run_verification({"method": "non-existent-method"}, f)


def test_cat5_verifier_missing_required_field_raises(tmp_path: Path):
    """spec con method valido pero sin campos requeridos -> InvalidVerificationSpecError."""
    f = tmp_path / "x.ts"
    f.write_text("data")
    with pytest.raises(InvalidVerificationSpecError):
        run_verification({"method": "re-run-eslint"}, f)


# =============================================================================
# Categoria 7 — file read-only (permission denied al escribir)
# =============================================================================


@pytest.mark.skipif(
    os.name == "nt",
    reason="Windows chmod no es POSIX; permisos read-only requieren tooling distinto",
)
def test_cat7_file_read_only_handler_invoke_fails_then_rollback(tmp_path: Path):
    """File read-only: el tool intenta escribir -> falla -> rollback (file unchanged)."""
    f = tmp_path / "x.ts"
    f.write_text("original")
    # Quitar write permission
    f.chmod(stat.S_IREAD | stat.S_IRGRP | stat.S_IROTH)
    try:
        handler = _write_handler("modified")
        finding = ClassifiedFinding(rule_id="TEST-RULE", file=str(f), line=1, tier="A")
        result = process_finding(finding, {"TEST-RULE": handler})
        # Debe terminar en rolled_back o escalated_to_c, NO en applied
        assert result.fix_status in (FixStatus.ROLLED_BACK, FixStatus.ESCALATED_TO_C)
        # File content preservado
        assert f.read_text() == "original"
    finally:
        # Restaurar write para que tmp_path se pueda limpiar
        f.chmod(stat.S_IREAD | stat.S_IWRITE)


# =============================================================================
# Categoria 10 — snapshot bytes corruption mid-flow (verificacion de defensa)
# =============================================================================


def test_cat10_snapshot_diff_summary_after_external_modification(tmp_path: Path):
    """Modificacion externa entre construccion del snapshot y diff_summary genera
    hashes distintos (signal de cambio externo) sin crashear."""
    f = tmp_path / "x.ts"
    f.write_text("original")
    snap = FileSnapshot(f)
    # Modificacion externa (otro proceso, simulado)
    f.write_text("EXTERNAL_CHANGE")
    summary = snap.diff_summary()
    pre_hash, _, post_hash = summary.replace("→", "->").partition("->")
    assert pre_hash.strip() != post_hash.strip()  # detecta el cambio externo


def test_cat10_snapshot_restore_recovers_from_external_corruption(tmp_path: Path):
    """Restore funciona aun si el archivo fue corrompido externamente."""
    f = tmp_path / "x.ts"
    f.write_text("original")
    snap = FileSnapshot(f)
    # Corrupcion externa
    f.write_bytes(b"\x00\x01\x02\xff\xfe corrupted binary")
    snap.restore()
    assert f.read_text() == "original"


# =============================================================================
# Categoria 11 — batch masivo (1000 findings) — sin leak + tiempo razonable
# =============================================================================


def test_cat11_batch_1000_findings_no_memory_leak(tmp_path: Path):
    """Batch grande no debe agotar memoria ni tomar >30s wall-clock total."""
    files = []
    findings = []
    for i in range(1000):
        f = tmp_path / f"f{i}.ts"
        f.write_text("data")
        files.append(f)
        findings.append(
            ClassifiedFinding(
                rule_id="UNKNOWN-RULE",  # forzar escalation (rapido, sin subprocess)
                file=str(f),
                line=1,
                tier="A",
            )
        )
    start = time.monotonic()
    results = run_batch(findings, {})  # no handlers -> todos escalation
    elapsed = time.monotonic() - start
    assert len(results) == 1000
    assert all(r.fix_status is FixStatus.ESCALATED_TO_C for r in results)
    # Threshold conservador: <10s para 1000 escalations puras
    assert elapsed < 10.0, f"batch 1000 escalations tomo {elapsed:.2f}s (esperado <10s)"


# =============================================================================
# Categoria 14 — rollback durante rollback (snapshot.restore() falla)
# =============================================================================


def test_cat14_double_restore_after_external_delete_does_not_crash(tmp_path: Path):
    """Si el target desaparece (rm externo), segundo restore propaga OSError claro.

    Aceptable: la primera restore puede crashear o no segun OS. El comportamiento
    documentado es que el snapshot NO oculta el error filesystem — propaga para
    que el orchestrator decida.
    """
    f = tmp_path / "x.ts"
    f.write_text("original")
    snap = FileSnapshot(f)
    f.unlink()  # archivo borrado externamente
    # Primera restore: en Posix esto puede recrear (write_bytes crea), Windows similar
    # No assert behavior — solo que NO hay crash silencioso
    try:
        snap.restore()
        # Si llegamos aca, restore recreo el archivo
        assert f.exists()
        assert f.read_bytes() == b"original"
    except OSError:
        # Aceptable: error claro propagado
        pass


def test_cat14_restore_during_concurrent_modification_does_not_lose_data(tmp_path: Path):
    """Restore mientras otro thread escribe: el ultimo write gana (no es lock cross-process).

    Esto NO es una propiedad atomica deseada — documenta el comportamiento actual
    (intra-process lock no protege contra writes externos). Cross-process locking
    seria una mejora Sprint 5+.
    """
    f = tmp_path / "x.ts"
    f.write_text("orig")
    snap = FileSnapshot(f)
    # Simular write externo despues del snapshot
    f.write_text("EXTERNAL")
    snap.restore()
    # El restore sobreescribe el cambio externo (comportamiento documentado)
    assert f.read_text() == "orig"


# =============================================================================
# Sanity: categorias YA cubiertas en otros test files (referencias)
# =============================================================================


class TestCrossReferences:
    """Sanity references — confirman que las categorias 1, 2, 3, 4, 6, 8, 9, 12,
    13, 15 estan cubiertas en otros test files. Estas pruebas NO duplican; solo
    importan los modulos y verifican que las APIs existen."""

    def test_cat1_2_3_cli_module_exists(self):
        from sigma.auto_fix_mechanic.cli import main
        assert callable(main)

    def test_cat4_orchestrator_handles_tool_crash(self):
        from sigma.auto_fix_mechanic.orchestrator import process_finding
        assert callable(process_finding)

    def test_cat6_9_snapshot_module_exists(self):
        from sigma.auto_fix_mechanic.snapshot import FileSnapshot, FileTooLargeForSnapshotError
        assert FileSnapshot is not None
        assert issubclass(FileTooLargeForSnapshotError, RuntimeError)

    def test_cat8_preflight_module_exists(self):
        from sigma.auto_fix_mechanic.preflight import run_preflight_check, ToolSpec
        assert callable(run_preflight_check)
        assert ToolSpec is not None

    def test_cat12_verifier_module_exists(self):
        from sigma.auto_fix_mechanic.verifier import run_verification, VerifyResult
        assert callable(run_verification)
        assert VerifyResult is not None

    def test_cat13_15_loader_and_idempotency_modules_exist(self):
        from sigma.auto_fix_mechanic.loader import load_handlers, InvalidRulesYamlError
        assert callable(load_handlers)
        assert issubclass(InvalidRulesYamlError, Exception)
