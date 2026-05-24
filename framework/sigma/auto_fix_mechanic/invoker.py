"""Subprocess wrapper — S-2 (invoker.py).

Invoca `handler.invocation` reemplazando `<file>` con el path real.
Sin shell intermediario (shell=False). Timeout 30s default.
Errores explicitos: ToolNotFoundError, ToolTimeoutError.
"""

import shlex
import subprocess
import time
from dataclasses import dataclass
from pathlib import Path

from sigma.auto_fix_mechanic.models import Handler


@dataclass(frozen=True)
class InvokeResult:
    """Resultado de una invocacion subprocess."""

    exit_code: int
    stdout: str
    stderr: str
    elapsed_ms: int


class ToolNotFoundError(RuntimeError):
    """El binary del tool no se encontro en PATH al invocar."""


class ToolTimeoutError(RuntimeError):
    """El tool excedio el timeout configurado."""


def invoke_tool(
    handler: Handler,
    file: Path,
    timeout_s: int = 30,
) -> InvokeResult:
    """Invoca `handler.invocation` reemplazando `<file>` con el path real.

    Raise:
        ValueError si handler no tiene invocation (caso codemod_script — ese
            requiere runner separado, no este invoker generico).
        ToolNotFoundError si el binary no esta en PATH.
        ToolTimeoutError si excede timeout_s.
    """
    if not handler.invocation:
        raise ValueError(
            f"handler '{handler.rule_id}' no tiene invocation; usar codemod runner separado"
        )

    # Split ANTES de reemplazar <file> para que paths con espacios queden en un solo token
    raw_args = shlex.split(handler.invocation, posix=True)
    if not raw_args:
        raise ValueError(f"handler '{handler.rule_id}' invocation vacia post-split")
    args = [arg.replace("<file>", str(file)) for arg in raw_args]

    start = time.monotonic()
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            timeout=timeout_s,
            shell=False,
            text=True,
        )
    except FileNotFoundError as exc:
        raise ToolNotFoundError(f"tool no encontrado en PATH: {args[0]}") from exc
    except subprocess.TimeoutExpired as exc:
        raise ToolTimeoutError(
            f"tool '{args[0]}' excedio timeout {timeout_s}s"
        ) from exc

    elapsed_ms = int((time.monotonic() - start) * 1000)
    return InvokeResult(
        exit_code=result.returncode,
        stdout=result.stdout or "",
        stderr=result.stderr or "",
        elapsed_ms=elapsed_ms,
    )
