"""Tests para sigma.auto_fix_mechanic.preflight — S-2 Pre-flight check (AM9).

Cubre AC-S2-1..AC-S2-4. Usa `python --version` como tool siempre-disponible
y nombres inexistentes (`__nonexistent_tool_xyz__`) para simular tool faltante.
"""

import sys

import pytest

from sigma.auto_fix_mechanic.models import Handler
from sigma.auto_fix_mechanic.preflight import ToolSpec, run_preflight_check


PYTHON_EXE = sys.executable  # path absoluto al python actual — siempre disponible
PYTHON_CHECK = f'"{PYTHON_EXE}" --version'


def _h(rule_id: str, tool: str = "eslint") -> Handler:
    return Handler(rule_id=rule_id, tool=tool, invocation=f"{tool} <file>")


# ---------------------------------------------------------------------------
# AC-S2-1 — Todo OK
# ---------------------------------------------------------------------------


def test_all_tools_available_returns_ok():
    required = [
        ToolSpec(name="python_ok", check_command=PYTHON_CHECK),
    ]
    optional = [
        ToolSpec(name="python_opt_ok", check_command=PYTHON_CHECK,
                 required_for_handlers=("TS-NON-NULL-ASSERTION",)),
    ]
    handlers = {"TS-NON-NULL-ASSERTION": _h("TS-NON-NULL-ASSERTION", "ts-morph-custom")}

    status, handlers_out = run_preflight_check(required, optional, handlers)

    assert status.required_tools_ok is True
    assert status.optional_tools_ok is True
    assert status.missing_required == []
    assert status.missing_optional == []
    assert status.disabled_handlers == []
    assert handlers_out["TS-NON-NULL-ASSERTION"].optional_tool_unavailable is False


# ---------------------------------------------------------------------------
# AC-S2-2 — Required tool ausente
# ---------------------------------------------------------------------------


def test_required_tool_missing_marks_not_ok():
    required = [
        ToolSpec(name="__nonexistent_tool_xyz__",
                 check_command="__nonexistent_tool_xyz__ --version"),
    ]
    optional: list[ToolSpec] = []
    handlers: dict[str, Handler] = {}

    status, _ = run_preflight_check(required, optional, handlers)

    assert status.required_tools_ok is False
    assert "__nonexistent_tool_xyz__" in status.missing_required


def test_required_partial_missing_only_those_in_missing():
    required = [
        ToolSpec(name="python_ok", check_command=PYTHON_CHECK),
        ToolSpec(name="__missing_tool__", check_command="__missing_tool__ --version"),
    ]
    status, _ = run_preflight_check(required, [], {})
    assert status.required_tools_ok is False
    assert status.missing_required == ["__missing_tool__"]


# ---------------------------------------------------------------------------
# AC-S2-3 — Required falta, optional OK
# ---------------------------------------------------------------------------


def test_required_missing_optional_present():
    required = [ToolSpec(name="__missing__", check_command="__missing__ --version")]
    optional = [ToolSpec(name="python_opt", check_command=PYTHON_CHECK,
                         required_for_handlers=("FAKE-RULE",))]
    handlers = {"FAKE-RULE": _h("FAKE-RULE", "ts-morph-custom")}

    status, handlers_out = run_preflight_check(required, optional, handlers)

    assert status.required_tools_ok is False
    assert status.optional_tools_ok is True
    assert handlers_out["FAKE-RULE"].optional_tool_unavailable is False


# ---------------------------------------------------------------------------
# AC-S2-4 — Optional falta, disabled_handlers contiene rule_ids afectados
# ---------------------------------------------------------------------------


def test_optional_missing_disables_associated_handlers():
    required = [ToolSpec(name="python_ok", check_command=PYTHON_CHECK)]
    optional = [
        ToolSpec(
            name="__missing_opt_tool__",
            check_command="__missing_opt_tool__ --version",
            required_for_handlers=(
                "TS-NON-NULL-ASSERTION",
                "TYPE-CAST-AS-ANY",
            ),
        ),
    ]
    handlers = {
        "TS-NON-NULL-ASSERTION": _h("TS-NON-NULL-ASSERTION", "ts-morph-custom"),
        "TYPE-CAST-AS-ANY": _h("TYPE-CAST-AS-ANY", "ts-morph-custom"),
        "TS-1": _h("TS-1", "eslint"),  # no afectado por el missing optional
    }

    status, handlers_out = run_preflight_check(required, optional, handlers)

    assert status.required_tools_ok is True
    assert status.optional_tools_ok is False
    assert "__missing_opt_tool__" in status.missing_optional
    assert set(status.disabled_handlers) == {"TS-NON-NULL-ASSERTION", "TYPE-CAST-AS-ANY"}
    # Handlers afectados marcados optional_tool_unavailable
    assert handlers_out["TS-NON-NULL-ASSERTION"].optional_tool_unavailable is True
    assert handlers_out["TYPE-CAST-AS-ANY"].optional_tool_unavailable is True
    # Handler NO afectado sigue OK
    assert handlers_out["TS-1"].optional_tool_unavailable is False


# ---------------------------------------------------------------------------
# Edge cases adversariales
# ---------------------------------------------------------------------------


def test_empty_handlers_dict_no_crash():
    required = [ToolSpec(name="python_ok", check_command=PYTHON_CHECK)]
    status, handlers_out = run_preflight_check(required, [], {})
    assert status.required_tools_ok is True
    assert handlers_out == {}


def test_optional_tool_for_rule_id_not_in_handlers():
    # required_for_handlers menciona rule_id que no esta en handlers dict
    optional = [
        ToolSpec(
            name="__missing__",
            check_command="__missing__ --v",
            required_for_handlers=("RULE-NOT-IN-HANDLERS",),
        ),
    ]
    status, handlers_out = run_preflight_check([], optional, {})
    # No crash; disabled_handlers solo lista rule_ids que estaban en handlers
    assert status.optional_tools_ok is False
    assert status.disabled_handlers == []


def test_handlers_dict_immutable_to_caller_when_no_optional_disabled():
    """Si nada queda disabled, handlers_out puede ser el mismo dict que input
    o copy — pero ningun Handler interior debe estar mutado."""
    h_in = _h("TS-1", "eslint")
    handlers = {"TS-1": h_in}
    status, handlers_out = run_preflight_check([], [], handlers)
    assert handlers_out["TS-1"].optional_tool_unavailable is False
    # Handler original no mutado (frozen igual previene)
    assert h_in.optional_tool_unavailable is False
