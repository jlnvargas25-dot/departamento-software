"""Tests para sigma.auto_fix_mechanic.loader — S-1 foundation.

Cubre AC-S1-1 (import), AC-S1-2 (15 entries del productivo),
AC-S1-3 (YAML invalido raise), AC-S1-5 (adversariales).
"""

from pathlib import Path

import pytest

from sigma.auto_fix_mechanic import load_handlers
from sigma.auto_fix_mechanic.loader import InvalidRulesYamlError

PRODUCTIVE_YAML = (
    Path(__file__).parent.parent / "rules.yaml"
)


# ---------------------------------------------------------------------------
# AC-S1-1 — Public API importable
# ---------------------------------------------------------------------------


def test_load_handlers_is_importable_from_package_root():
    # AC-S1-1: `from sigma.auto_fix_mechanic import load_handlers` funciona
    from sigma.auto_fix_mechanic import load_handlers as imported
    assert callable(imported)


# ---------------------------------------------------------------------------
# AC-S1-2 — Productive YAML carga 15 handlers
# ---------------------------------------------------------------------------


def test_load_handlers_returns_dict_with_15_entries():
    handlers = load_handlers(PRODUCTIVE_YAML)
    assert isinstance(handlers, dict)
    assert len(handlers) == 15


def test_load_handlers_each_entry_has_tool_and_invocation_or_codemod():
    handlers = load_handlers(PRODUCTIVE_YAML)
    for rule_id, h in handlers.items():
        assert h.tool, f"handler {rule_id} sin tool"
        assert h.invocation or h.codemod_script, (
            f"handler {rule_id} sin invocation ni codemod_script"
        )


def test_load_handlers_covers_all_15_tier_a_rule_ids():
    expected = {
        "TS-1",
        "TS-NON-NULL-ASSERTION",
        "A21-OBS-1-CONSOLE-LOG",
        "A21-OBS-1b-DENO-CONSOLE",
        "NO-VAR",
        "VAR-TO-CONST",
        "MIGRATION-NAMING",
        "TYPE-CAST-AS-ANY",
        "PGSQL-MISSING-VOLATILE",
        "LET-WITHOUT-REASSIGN",
        "UNUSED-IMPORT",
        "TRAILING-WHITESPACE",
        "MISSING-SEMI",
        "IMPORT-ORDER",
        "OBJECT-SHORTHAND",
    }
    handlers = load_handlers(PRODUCTIVE_YAML)
    assert set(handlers.keys()) == expected


def test_load_handlers_tool_distribution_matches_toolbox():
    handlers = load_handlers(PRODUCTIVE_YAML)
    by_tool: dict[str, int] = {}
    for h in handlers.values():
        by_tool[h.tool] = by_tool.get(h.tool, 0) + 1
    # codemod-toolbox.md sec 1: 8/15 eslint + 2-3 prettier + 4 ts-morph custom + 2 python custom
    # MISSING-SEMI cae en eslint OR prettier segun config (.prettierrc) del proyecto target.
    # El YAML productivo lo asigna a prettier por default (respeta .prettierrc local).
    # Por eso eslint=7 + prettier=2 (no 8+2), totalizando 15 con los demas tools.
    assert by_tool.get("ts-morph-custom", 0) == 4
    assert by_tool.get("python-custom-script", 0) == 2
    eslint_count = by_tool.get("eslint", 0)
    prettier_count = by_tool.get("prettier", 0)
    assert eslint_count + prettier_count == 9  # 8 eslint-candidates + 1 prettier-only (TRAILING-WS)
    assert prettier_count in (1, 2, 3)  # MISSING-SEMI flexible, TRAILING-WS siempre prettier
    # Verificar que MISSING-SEMI esta correctamente clasificado en uno u otro
    assert handlers["MISSING-SEMI"].tool in {"eslint", "prettier"}


# ---------------------------------------------------------------------------
# AC-S1-3 — YAML invalido raise InvalidRulesYamlError
# ---------------------------------------------------------------------------


def test_missing_version_field_raises(tmp_path: Path):
    p = tmp_path / "no_version.yaml"
    p.write_text("handlers: {}\ndefaults: {}\npreflight: {}\n", encoding="utf-8")
    with pytest.raises(InvalidRulesYamlError) as exc:
        load_handlers(p)
    assert "version" in str(exc.value)


def test_missing_handlers_field_raises(tmp_path: Path):
    p = tmp_path / "no_handlers.yaml"
    p.write_text(
        "version: '0.1.0'\ndefaults: {}\npreflight: {}\n", encoding="utf-8"
    )
    with pytest.raises(InvalidRulesYamlError) as exc:
        load_handlers(p)
    assert "handlers" in str(exc.value)


def test_handler_without_tool_raises(tmp_path: Path):
    p = tmp_path / "no_tool.yaml"
    p.write_text(
        "version: '0.1.0'\n"
        "handlers:\n"
        "  TS-1:\n"
        "    invocation: 'eslint <file>'\n"
        "defaults: {}\n"
        "preflight: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidRulesYamlError) as exc:
        load_handlers(p)
    assert "tool" in str(exc.value)
    assert "TS-1" in str(exc.value)


def test_handler_without_invocation_or_codemod_raises(tmp_path: Path):
    p = tmp_path / "no_action.yaml"
    p.write_text(
        "version: '0.1.0'\n"
        "handlers:\n"
        "  TS-1:\n"
        "    tool: eslint\n"
        "defaults: {}\n"
        "preflight: {}\n",
        encoding="utf-8",
    )
    with pytest.raises(InvalidRulesYamlError) as exc:
        load_handlers(p)
    assert "invocation" in str(exc.value) or "codemod_script" in str(exc.value)


def test_nonexistent_file_raises(tmp_path: Path):
    with pytest.raises((InvalidRulesYamlError, FileNotFoundError)):
        load_handlers(tmp_path / "no_such_file.yaml")


# ---------------------------------------------------------------------------
# AC-S1-5 — Adversariales
# ---------------------------------------------------------------------------


def test_empty_yaml_raises(tmp_path: Path):
    p = tmp_path / "empty.yaml"
    p.write_text("", encoding="utf-8")
    with pytest.raises(InvalidRulesYamlError):
        load_handlers(p)


def test_yaml_with_tabs_in_indentation_raises(tmp_path: Path):
    # YAML no permite tabs en indentacion
    p = tmp_path / "tabs.yaml"
    p.write_text(
        "version: '0.1.0'\nhandlers:\n\tTS-1:\n\t\ttool: eslint\n", encoding="utf-8"
    )
    with pytest.raises(InvalidRulesYamlError):
        load_handlers(p)


def test_yaml_with_non_utf8_bytes_raises(tmp_path: Path):
    p = tmp_path / "latin1.yaml"
    # Bytes invalidos UTF-8 (0xff es valido latin1 pero invalido UTF-8 standalone)
    p.write_bytes(b"version: '0.1.0'\nhandlers:\n  TS\xff-1:\n    tool: eslint\n")
    with pytest.raises((InvalidRulesYamlError, UnicodeDecodeError)):
        load_handlers(p)


def test_yaml_root_is_not_mapping_raises(tmp_path: Path):
    # YAML root como list en lugar de dict
    p = tmp_path / "list_root.yaml"
    p.write_text("- not_a_mapping\n- just_a_list\n", encoding="utf-8")
    with pytest.raises(InvalidRulesYamlError):
        load_handlers(p)


def test_load_handlers_accepts_str_path(tmp_path: Path):
    # Funcion debe aceptar str y Path indistintamente
    handlers_from_path = load_handlers(PRODUCTIVE_YAML)
    handlers_from_str = load_handlers(str(PRODUCTIVE_YAML))
    assert set(handlers_from_path.keys()) == set(handlers_from_str.keys())
