"""Tests para sigma.auto_fix_mechanic.snapshot — S-3 snapshot + rollback.

Cubre AC-S3-1..AC-S3-7. R04 cerrado: lock via threading (intra-process).
Cross-process locking (fcntl/msvcrt) diferido a Sprint 5+ si necesario.
"""

import threading
import time
from pathlib import Path

import pytest

from sigma.auto_fix_mechanic.snapshot import (
    FileSnapshot,
    FileTooLargeForSnapshotError,
)


# ---------------------------------------------------------------------------
# AC-S3-1 — write + restore -> contenido original
# ---------------------------------------------------------------------------


def test_restore_reverts_modification(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("original", encoding="utf-8")
    with FileSnapshot(p) as snap:
        p.write_text("modified", encoding="utf-8")
        assert p.read_text(encoding="utf-8") == "modified"
        snap.restore()
        assert p.read_text(encoding="utf-8") == "original"


def test_restore_preserves_binary_content(tmp_path: Path):
    p = tmp_path / "bin.dat"
    payload = bytes(range(256))
    p.write_bytes(payload)
    with FileSnapshot(p) as snap:
        p.write_bytes(b"corrupted")
        snap.restore()
        assert p.read_bytes() == payload


# ---------------------------------------------------------------------------
# AC-S3-2 — unchanged() detecta cambios
# ---------------------------------------------------------------------------


def test_unchanged_true_when_no_write(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("data", encoding="utf-8")
    with FileSnapshot(p) as snap:
        assert snap.unchanged() is True


def test_unchanged_false_when_modified(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("data", encoding="utf-8")
    with FileSnapshot(p) as snap:
        p.write_text("data2", encoding="utf-8")
        assert snap.unchanged() is False


def test_unchanged_after_restore_is_true_again(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("data", encoding="utf-8")
    with FileSnapshot(p) as snap:
        p.write_text("modified", encoding="utf-8")
        snap.restore()
        assert snap.unchanged() is True


# ---------------------------------------------------------------------------
# AC-S3-3 — diff_summary formato sha256:<8> -> sha256:<8>
# ---------------------------------------------------------------------------


def test_diff_summary_format(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("before", encoding="utf-8")
    with FileSnapshot(p) as snap:
        p.write_text("after", encoding="utf-8")
        summary = snap.diff_summary()
    # Formato: "sha256:<8chars> -> sha256:<8chars>" (con arrow ASCII o unicode)
    assert summary.startswith("sha256:")
    assert "sha256:" in summary[8:]
    # Dos hashes de 8 chars hex
    parts = summary.replace("→", "->").split("->")
    assert len(parts) == 2
    for part in parts:
        prefix, _, hash_part = part.strip().partition(":")
        assert prefix == "sha256"
        assert len(hash_part) == 8
        int(hash_part, 16)  # debe ser hex valido


def test_diff_summary_unchanged_hashes_equal(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("same", encoding="utf-8")
    with FileSnapshot(p) as snap:
        summary = snap.diff_summary()
    pre, _, post = summary.replace("→", "->").partition("->")
    assert pre.strip() == post.strip()


# ---------------------------------------------------------------------------
# AC-S3-4 — excepcion no controlada -> archivo restaurado
# ---------------------------------------------------------------------------


def test_exception_inside_with_triggers_rollback(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("original", encoding="utf-8")

    with pytest.raises(RuntimeError, match="boom"):
        with FileSnapshot(p):
            p.write_text("corrupted", encoding="utf-8")
            raise RuntimeError("boom")

    assert p.read_text(encoding="utf-8") == "original"


def test_no_exception_no_auto_rollback(tmp_path: Path):
    """Sin excepcion, restore() NO se llama automaticamente al salir del with."""
    p = tmp_path / "f.txt"
    p.write_text("original", encoding="utf-8")
    with FileSnapshot(p):
        p.write_text("intentional change", encoding="utf-8")
    # Cambio intencional preservado, no auto-restored
    assert p.read_text(encoding="utf-8") == "intentional change"


# ---------------------------------------------------------------------------
# AC-S3-5 — archivo >100MB raise FileTooLargeForSnapshotError
# ---------------------------------------------------------------------------


def test_large_file_raises(tmp_path: Path, monkeypatch):
    p = tmp_path / "big.txt"
    p.write_text("x", encoding="utf-8")
    # Mockear stat().st_size para simular > 100MB sin crear el file real
    real_stat = Path.stat
    big_size = 101 * 1024 * 1024

    class FakeStatResult:
        def __init__(self, real_result):
            self._real = real_result
        @property
        def st_size(self):
            return big_size
        def __getattr__(self, name):
            return getattr(self._real, name)

    def fake_stat(self_path, *args, **kwargs):
        return FakeStatResult(real_stat(self_path, *args, **kwargs))

    monkeypatch.setattr(Path, "stat", fake_stat)
    with pytest.raises(FileTooLargeForSnapshotError):
        FileSnapshot(p)


# ---------------------------------------------------------------------------
# AC-S3-6 — concurrencia: segunda FileSnapshot espera lock
# ---------------------------------------------------------------------------


def test_concurrent_snapshots_serialize_via_lock(tmp_path: Path):
    """Dos threads tomando FileSnapshot del mismo path -> serializan via lock.
    El segundo entra solo cuando el primero sale del with.
    """
    p = tmp_path / "f.txt"
    p.write_text("orig", encoding="utf-8")
    events: list[str] = []
    inside_first = threading.Event()
    release_first = threading.Event()

    def worker_a():
        with FileSnapshot(p):
            events.append("A_inside")
            inside_first.set()
            release_first.wait(timeout=2.0)
            events.append("A_exit")

    def worker_b():
        inside_first.wait(timeout=2.0)
        with FileSnapshot(p):
            events.append("B_inside")

    t_a = threading.Thread(target=worker_a)
    t_b = threading.Thread(target=worker_b)
    t_a.start()
    t_b.start()
    # Esperar que A este dentro + B este esperando
    time.sleep(0.1)
    assert events == ["A_inside"]
    # Soltar A; B entra ahora
    release_first.set()
    t_a.join(timeout=2.0)
    t_b.join(timeout=2.0)
    # Orden estricto: A entra, A sale, B entra
    assert events == ["A_inside", "A_exit", "B_inside"]


# ---------------------------------------------------------------------------
# AC-S3-7 — restore() doble es no-op (idempotente)
# ---------------------------------------------------------------------------


def test_double_restore_is_idempotent(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("orig", encoding="utf-8")
    with FileSnapshot(p) as snap:
        p.write_text("modified", encoding="utf-8")
        snap.restore()
        # Tras restore, write algo nuevo
        p.write_text("post-restore-write", encoding="utf-8")
        # Segundo restore debe ser no-op (NO sobreescribir el post-restore-write)
        snap.restore()
        assert p.read_text(encoding="utf-8") == "post-restore-write"


# ---------------------------------------------------------------------------
# Adversariales adicionales
# ---------------------------------------------------------------------------


def test_snapshot_nonexistent_file_raises(tmp_path: Path):
    with pytest.raises((FileNotFoundError, OSError)):
        FileSnapshot(tmp_path / "does_not_exist.txt")


def test_snapshot_accepts_str_path(tmp_path: Path):
    p = tmp_path / "f.txt"
    p.write_text("data", encoding="utf-8")
    snap = FileSnapshot(str(p))  # str en lugar de Path
    assert snap.path == p
