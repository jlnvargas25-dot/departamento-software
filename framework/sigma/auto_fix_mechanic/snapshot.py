"""FileSnapshot — S-3 snapshot + rollback atomico (R-5 reversibilidad).

Context manager que captura el contenido bytes de un archivo al entrar,
ofrece restore() para revertir, y rollback automatico si una excepcion no
controlada sale del with.

Lock cross-platform via stdlib threading (intra-process). R04 cerrado:
cero deps externas (consistente con classifier). Cross-process locking
(fcntl/msvcrt) queda diferido a Sprint 5+ si surge necesidad.
"""

import hashlib
import threading
from pathlib import Path
from typing import Union


class FileTooLargeForSnapshotError(RuntimeError):
    """Archivo excede el limite de tamano seguro para snapshot in-memory."""


# Registry de locks por path absoluto. Modulo-level → process-wide. NO cross-process.
_LOCKS: dict[Path, threading.Lock] = {}
_LOCKS_DICT_LOCK = threading.Lock()


def _get_lock(abs_path: Path) -> threading.Lock:
    with _LOCKS_DICT_LOCK:
        existing = _LOCKS.get(abs_path)
        if existing is None:
            existing = threading.Lock()
            _LOCKS[abs_path] = existing
        return existing


class FileSnapshot:
    """Snapshot in-memory de un archivo + rollback atomico via context manager.

    Uso tipico:
        with FileSnapshot(path) as snap:
            apply_codemod(path)
            if not verify(path):
                snap.restore()  # rollback explicito
        # Si una excepcion no controlada sale del with, rollback automatico.

    AC-S3-5: archivos > MAX_SIZE_BYTES raise FileTooLargeForSnapshotError
    al construir (NO al entrar al with) — fail-fast antes de iniciar el flujo.
    """

    MAX_SIZE_BYTES = 100 * 1024 * 1024  # 100 MB

    def __init__(self, path: Union[str, Path]):
        self.path = Path(path)
        size = self.path.stat().st_size
        if size > self.MAX_SIZE_BYTES:
            raise FileTooLargeForSnapshotError(
                f"{self.path}: {size} bytes > {self.MAX_SIZE_BYTES} bytes limit "
                f"(snapshot in-memory no es seguro)"
            )
        self.original_content: bytes = self.path.read_bytes()
        self.original_mtime: float = self.path.stat().st_mtime
        self._restored: bool = False
        self._lock = _get_lock(self.path.resolve())
        self._lock_acquired: bool = False

    # -----------------------------------------------------------------------
    # Public API
    # -----------------------------------------------------------------------

    def restore(self) -> None:
        """Restaura el archivo al contenido capturado en __init__.

        Idempotente (AC-S3-7): segunda invocacion es no-op.
        """
        if self._restored:
            return
        self.path.write_bytes(self.original_content)
        self._restored = True

    def unchanged(self) -> bool:
        """Retorna True si el contenido actual matchea el original."""
        return self.path.read_bytes() == self.original_content

    def diff_summary(self) -> str:
        """Hashes SHA256 truncados pre/post — formato: 'sha256:<8> -> sha256:<8>'."""
        pre = hashlib.sha256(self.original_content).hexdigest()[:8]
        post = hashlib.sha256(self.path.read_bytes()).hexdigest()[:8]
        return f"sha256:{pre} -> sha256:{post}"

    # -----------------------------------------------------------------------
    # Context manager protocol
    # -----------------------------------------------------------------------

    def __enter__(self) -> "FileSnapshot":
        self._lock.acquire()
        self._lock_acquired = True
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> bool:
        try:
            # AC-S3-4: excepcion no controlada -> rollback automatico
            if exc_type is not None and not self._restored:
                self.restore()
        finally:
            if self._lock_acquired:
                self._lock.release()
                self._lock_acquired = False
        return False  # NO suprimir la excepcion
