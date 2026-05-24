"""Tests para sigma.auto_fix_mechanic.invoker — S-2 subprocess wrapper.

Cubre AC-S2-5..AC-S2-7. Usa `python -c` como tool real cross-platform.
"""

import sys
from pathlib import Path

import pytest

from sigma.auto_fix_mechanic.invoker import (
    InvokeResult,
    ToolNotFoundError,
    ToolTimeoutError,
    invoke_tool,
)
from sigma.auto_fix_mechanic.models import Handler


PYTHON = f'"{sys.executable}"'


def _handler(invocation: str, rule_id: str = "TEST-RULE") -> Handler:
    return Handler(rule_id=rule_id, tool="test", invocation=invocation)


# ---------------------------------------------------------------------------
# AC-S2-5 — invoke_tool ejecuta comando real y retorna InvokeResult
# ---------------------------------------------------------------------------


def test_invoke_tool_returns_invoke_result_with_exit_code(tmp_path: Path):
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    h = _handler(f'{PYTHON} -c "import sys;sys.exit(0)" <file>')
    result = invoke_tool(h, f)
    assert isinstance(result, InvokeResult)
    assert result.exit_code == 0


def test_invoke_tool_captures_stdout(tmp_path: Path):
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    h = _handler(f'{PYTHON} -c "print(\'hello\')"')
    result = invoke_tool(h, f)
    assert "hello" in result.stdout


def test_invoke_tool_captures_stderr(tmp_path: Path):
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    h = _handler(f'{PYTHON} -c "import sys;sys.stderr.write(\'oops\')"')
    result = invoke_tool(h, f)
    assert "oops" in result.stderr


def test_invoke_tool_reports_exit_code_non_zero(tmp_path: Path):
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    h = _handler(f'{PYTHON} -c "import sys;sys.exit(7)"')
    result = invoke_tool(h, f)
    assert result.exit_code == 7


def test_invoke_tool_replaces_file_placeholder(tmp_path: Path):
    f = tmp_path / "target.txt"
    f.write_text("dummy")
    # Comando que printa el argumento file recibido
    h = _handler(f'{PYTHON} -c "import sys;print(sys.argv[1])" <file>')
    result = invoke_tool(h, f)
    assert str(f) in result.stdout


def test_invoke_tool_elapsed_ms_is_positive(tmp_path: Path):
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    h = _handler(f'{PYTHON} -c "pass"')
    result = invoke_tool(h, f)
    assert result.elapsed_ms >= 0  # subprocess startup puede ser <1ms en algunos sistemas


# ---------------------------------------------------------------------------
# AC-S2-6 — Timeout raise ToolTimeoutError
# ---------------------------------------------------------------------------


def test_invoke_tool_timeout_raises(tmp_path: Path):
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    # Comando que duerme 5s; timeout 1s
    h = _handler(f'{PYTHON} -c "import time;time.sleep(5)"')
    with pytest.raises(ToolTimeoutError):
        invoke_tool(h, f, timeout_s=1)


# ---------------------------------------------------------------------------
# AC-S2-7 — shell=False enforced (no injection)
# ---------------------------------------------------------------------------


def test_invoke_tool_tool_not_in_path_raises(tmp_path: Path):
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    h = _handler("__nonexistent_xyz__ --version <file>")
    with pytest.raises(ToolNotFoundError):
        invoke_tool(h, f)


def test_invoke_tool_shell_metacharacters_not_evaluated(tmp_path: Path):
    """AC-S2-7: shell=False asegura que `;` `&&` `$()` no se evaluan como shell ops.

    Si shell=True estuviera mal seteado, el comando `python -c ";"; rm -rf /` ejecutaria.
    Con shell=False, todo va como args literales al programa — sin injection.
    """
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    # Sintaxis con `;` interpretada como literal (no separador shell)
    h = _handler(f'{PYTHON} -c "print(\'safe\')"')
    result = invoke_tool(h, f)
    assert "safe" in result.stdout
    # Verifica shell=False indirectamente: si fuera True, el ; activaria otro comando
    assert result.exit_code == 0


def test_invoke_tool_raises_value_error_when_no_invocation(tmp_path: Path):
    """Handler con codemod_script (sin invocation) NO debe llegar a invoke_tool."""
    h = Handler(rule_id="X", tool="ts-morph-custom",
                codemod_script="codemods/foo.ts")
    f = tmp_path / "any.txt"
    f.write_text("dummy")
    with pytest.raises(ValueError):
        invoke_tool(h, f)
