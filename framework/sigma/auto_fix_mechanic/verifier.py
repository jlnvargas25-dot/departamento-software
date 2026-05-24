"""Verifier dispatcher — S-4.

Despacha por `verification.method` a uno de 5 implementaciones:
    - re-run-eslint        — re-corre eslint en modo quiet
    - re-run-prettier-check — re-corre prettier --check
    - ast-check            — invoca codemod script en modo --verify
    - filename-regex       — glob directory + regex match sobre filenames
    - regex-grep           — re.findall + assertion sobre file content

Cada method retorna VerifyResult(passed, detail). Timeout 15s default.
Detail string truncado a 200 chars para uso en PatchResult.rollback_reason.
"""

import re
import shlex
import subprocess
from dataclasses import dataclass
from pathlib import Path


SUPPORTED_METHODS = {
    "re-run-eslint",
    "re-run-prettier-check",
    "ast-check",
    "filename-regex",
    "regex-grep",
}

DEFAULT_TIMEOUT_S = 15
DETAIL_MAX_CHARS = 200


@dataclass(frozen=True)
class VerifyResult:
    passed: bool
    detail: str


class UnknownVerificationMethodError(ValueError):
    """`spec.method` no esta en SUPPORTED_METHODS."""


class InvalidVerificationSpecError(ValueError):
    """Spec malformado: campos requeridos faltantes para el method."""


# ---------------------------------------------------------------------------
# Public dispatcher
# ---------------------------------------------------------------------------


def run_verification(
    spec: dict, file: Path, timeout_s: int = DEFAULT_TIMEOUT_S
) -> VerifyResult:
    """Dispatch a la implementacion segun spec.method.

    Raise:
        InvalidVerificationSpecError si spec carece de campo `method` o de
        campos requeridos por ese method.
        UnknownVerificationMethodError si method no es uno de SUPPORTED_METHODS.
    """
    method = spec.get("method")
    if not method:
        raise InvalidVerificationSpecError(
            "spec sin campo 'method'; esperado uno de: "
            + ", ".join(sorted(SUPPORTED_METHODS))
        )
    if method not in SUPPORTED_METHODS:
        raise UnknownVerificationMethodError(
            f"method '{method}' no soportado; supported: "
            + ", ".join(sorted(SUPPORTED_METHODS))
        )

    if method in ("re-run-eslint", "re-run-prettier-check", "ast-check"):
        return _run_subprocess_method(spec, method, timeout_s)
    if method == "filename-regex":
        return _run_filename_regex(spec)
    if method == "regex-grep":
        return _run_regex_grep(spec, file)
    # Defensivo (no deberia alcanzarse por el check de SUPPORTED_METHODS)
    raise UnknownVerificationMethodError(method)


# ---------------------------------------------------------------------------
# Subprocess-based methods: re-run-eslint, re-run-prettier-check, ast-check
# ---------------------------------------------------------------------------


def _run_subprocess_method(spec: dict, method: str, timeout_s: int) -> VerifyResult:
    command = spec.get("command")
    if not command:
        raise InvalidVerificationSpecError(
            f"spec method='{method}' requiere campo 'command'"
        )
    try:
        args = shlex.split(command, posix=True)
    except ValueError as exc:
        return VerifyResult(passed=False, detail=_truncate(f"command split error: {exc}"))
    if not args:
        return VerifyResult(passed=False, detail="command vacio post-split")
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            timeout=timeout_s,
            shell=False,
            text=True,
        )
    except FileNotFoundError as exc:
        return VerifyResult(passed=False, detail=_truncate(f"tool not found: {exc}"))
    except subprocess.TimeoutExpired:
        return VerifyResult(
            passed=False, detail=f"verification_timeout_exceeded:{timeout_s}s"
        )
    except OSError as exc:
        return VerifyResult(passed=False, detail=_truncate(f"os error: {exc}"))

    if result.returncode == 0:
        return VerifyResult(passed=True, detail="exit 0")
    detail = result.stderr or result.stdout or f"exit {result.returncode}"
    return VerifyResult(passed=False, detail=_truncate(detail.strip()))


# ---------------------------------------------------------------------------
# Method: filename-regex (glob directory + regex match)
# ---------------------------------------------------------------------------


def _run_filename_regex(spec: dict) -> VerifyResult:
    pattern = spec.get("pattern")
    directory = spec.get("directory")
    if not pattern or not directory:
        raise InvalidVerificationSpecError(
            "spec method='filename-regex' requiere 'pattern' y 'directory'"
        )
    regex = re.compile(pattern)
    dir_path = Path(directory)
    if not dir_path.is_dir():
        return VerifyResult(passed=False, detail=_truncate(f"directory not found: {directory}"))

    mismatches: list[str] = []
    for child in sorted(dir_path.iterdir()):
        if child.is_file() and not regex.match(child.name):
            mismatches.append(child.name)

    if mismatches:
        return VerifyResult(
            passed=False, detail=_truncate(f"non-matching: {', '.join(mismatches)}")
        )
    return VerifyResult(passed=True, detail="all filenames match pattern")


# ---------------------------------------------------------------------------
# Method: regex-grep (re.findall sobre file content + assertion)
# ---------------------------------------------------------------------------


def _run_regex_grep(spec: dict, file: Path) -> VerifyResult:
    pattern = spec.get("pattern")
    assertion = spec.get("assertion", "must_not_appear")
    if not pattern:
        raise InvalidVerificationSpecError(
            "spec method='regex-grep' requiere campo 'pattern'"
        )
    if assertion not in ("must_appear", "must_not_appear"):
        raise InvalidVerificationSpecError(
            f"assertion '{assertion}' debe ser 'must_appear' o 'must_not_appear'"
        )
    try:
        content = file.read_text(encoding="utf-8")
    except (FileNotFoundError, UnicodeDecodeError) as exc:
        return VerifyResult(passed=False, detail=_truncate(f"file read error: {exc}"))

    matches = re.findall(pattern, content)
    if assertion == "must_appear":
        if matches:
            return VerifyResult(passed=True, detail=f"{len(matches)} match(es) found")
        return VerifyResult(passed=False, detail=f"pattern '{pattern}' not found")
    # must_not_appear
    if not matches:
        return VerifyResult(passed=True, detail="pattern absent (good)")
    return VerifyResult(
        passed=False,
        detail=_truncate(f"pattern still present: {len(matches)} occurrence(s)"),
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _truncate(s: str) -> str:
    return s if len(s) <= DETAIL_MAX_CHARS else s[: DETAIL_MAX_CHARS - 3] + "..."
