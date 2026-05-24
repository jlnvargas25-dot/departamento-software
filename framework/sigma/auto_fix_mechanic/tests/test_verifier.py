"""Tests para sigma.auto_fix_mechanic.verifier — S-4 verification dispatcher.

Cubre AC-S4-1..AC-S4-5 + los 5 methods con passed + failed cases.
"""

import sys
from pathlib import Path

import pytest

from sigma.auto_fix_mechanic.verifier import (
    InvalidVerificationSpecError,
    UnknownVerificationMethodError,
    VerifyResult,
    run_verification,
)


PYTHON = f'"{sys.executable}"'


# ---------------------------------------------------------------------------
# AC-S4-1 — Dispatcher invoca method correcto
# ---------------------------------------------------------------------------


def test_run_verification_returns_verify_result(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("ok")
    spec = {"method": "regex-grep", "pattern": r"ok", "assertion": "must_appear"}
    result = run_verification(spec, f)
    assert isinstance(result, VerifyResult)


# ---------------------------------------------------------------------------
# AC-S4-2 — Method desconocido raise UnknownVerificationMethodError
# ---------------------------------------------------------------------------


def test_unknown_method_raises(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("ok")
    spec = {"method": "no-such-method"}
    with pytest.raises(UnknownVerificationMethodError) as exc:
        run_verification(spec, f)
    # Mensaje claro con lista de methods soportados
    msg = str(exc.value)
    assert "re-run-eslint" in msg or "supported" in msg.lower() or "methods" in msg.lower()


# ---------------------------------------------------------------------------
# AC-S4-5 — Spec malformado raise InvalidVerificationSpecError
# ---------------------------------------------------------------------------


def test_missing_method_field_raises(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("ok")
    with pytest.raises(InvalidVerificationSpecError):
        run_verification({}, f)


def test_re_run_eslint_missing_command_raises(tmp_path: Path):
    f = tmp_path / "x.txt"
    f.write_text("ok")
    with pytest.raises(InvalidVerificationSpecError):
        run_verification({"method": "re-run-eslint"}, f)


# ---------------------------------------------------------------------------
# Method: regex-grep
# ---------------------------------------------------------------------------


def test_regex_grep_pattern_present_must_appear_passes(tmp_path: Path):
    f = tmp_path / "x.py"
    f.write_text("VOLATILE marker added\n")
    spec = {"method": "regex-grep", "pattern": r"VOLATILE", "assertion": "must_appear"}
    result = run_verification(spec, f)
    assert result.passed is True


def test_regex_grep_pattern_missing_must_appear_fails(tmp_path: Path):
    f = tmp_path / "x.py"
    f.write_text("no marker here\n")
    spec = {"method": "regex-grep", "pattern": r"VOLATILE", "assertion": "must_appear"}
    result = run_verification(spec, f)
    assert result.passed is False


def test_regex_grep_must_not_appear(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("clean code")
    spec = {"method": "regex-grep", "pattern": r"console\.log", "assertion": "must_not_appear"}
    result = run_verification(spec, f)
    assert result.passed is True


def test_regex_grep_must_not_appear_but_appears_fails(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("console.log('still here')")
    spec = {"method": "regex-grep", "pattern": r"console\.log", "assertion": "must_not_appear"}
    result = run_verification(spec, f)
    assert result.passed is False


# ---------------------------------------------------------------------------
# Method: filename-regex
# ---------------------------------------------------------------------------


def test_filename_regex_all_match_passes(tmp_path: Path):
    (tmp_path / "20260522_alpha.sql").write_text("")
    (tmp_path / "20260523_beta.sql").write_text("")
    spec = {
        "method": "filename-regex",
        "pattern": r"^\d{8}_[a-z0-9_-]+\.sql$",
        "directory": str(tmp_path),
    }
    result = run_verification(spec, tmp_path / "20260522_alpha.sql")
    assert result.passed is True


def test_filename_regex_one_mismatch_fails(tmp_path: Path):
    (tmp_path / "20260522_alpha.sql").write_text("")
    (tmp_path / "0001_bad.sql").write_text("")  # non-matching
    spec = {
        "method": "filename-regex",
        "pattern": r"^\d{8}_[a-z0-9_-]+\.sql$",
        "directory": str(tmp_path),
    }
    result = run_verification(spec, tmp_path / "20260522_alpha.sql")
    assert result.passed is False
    assert "0001_bad.sql" in result.detail


# ---------------------------------------------------------------------------
# Method: re-run-eslint (sintetico via python)
# ---------------------------------------------------------------------------


def test_re_run_eslint_exit_zero_passes(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("ok")
    spec = {
        "method": "re-run-eslint",
        "command": f'{PYTHON} -c "import sys;sys.exit(0)"',
    }
    result = run_verification(spec, f)
    assert result.passed is True


def test_re_run_eslint_exit_nonzero_fails(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("ok")
    spec = {
        "method": "re-run-eslint",
        "command": f'{PYTHON} -c "import sys;sys.stderr.write(\'lint err\');sys.exit(1)"',
    }
    result = run_verification(spec, f)
    assert result.passed is False
    assert "lint err" in result.detail or "exit" in result.detail.lower()


# ---------------------------------------------------------------------------
# Method: re-run-prettier-check
# ---------------------------------------------------------------------------


def test_re_run_prettier_check_passes(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("formatted")
    spec = {
        "method": "re-run-prettier-check",
        "command": f'{PYTHON} -c "import sys;sys.exit(0)"',
    }
    result = run_verification(spec, f)
    assert result.passed is True


def test_re_run_prettier_check_fails(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("unformatted")
    spec = {
        "method": "re-run-prettier-check",
        "command": f'{PYTHON} -c "import sys;sys.exit(2)"',
    }
    result = run_verification(spec, f)
    assert result.passed is False


# ---------------------------------------------------------------------------
# Method: ast-check (codemod script en --verify mode)
# ---------------------------------------------------------------------------


def test_ast_check_passes(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("no pattern")
    spec = {
        "method": "ast-check",
        "command": f'{PYTHON} -c "import sys;sys.exit(0)"',
    }
    result = run_verification(spec, f)
    assert result.passed is True


def test_ast_check_pattern_still_present_fails(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("pattern still here")
    spec = {
        "method": "ast-check",
        "command": f'{PYTHON} -c "import sys;sys.exit(1)"',
    }
    result = run_verification(spec, f)
    assert result.passed is False


# ---------------------------------------------------------------------------
# AC-S4-4 — Timeout
# ---------------------------------------------------------------------------


def test_verification_timeout_returns_failed(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("ok")
    spec = {
        "method": "re-run-eslint",
        "command": f'{PYTHON} -c "import time;time.sleep(5)"',
    }
    result = run_verification(spec, f, timeout_s=1)
    assert result.passed is False
    assert "timeout" in result.detail.lower()
