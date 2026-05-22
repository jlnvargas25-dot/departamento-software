"""Tests for sigma.finding_classifier.loader — S-1 acceptance."""

from __future__ import annotations

import textwrap
from pathlib import Path

import pytest

from sigma.finding_classifier.loader import load_rules
from sigma.finding_classifier.models import ClassifierRules, SchemaError


REAL_RULES_PATH = Path(__file__).resolve().parent.parent / "rules.yaml"


def _write(tmp_path: Path, content: str) -> Path:
    p = tmp_path / "rules.yaml"
    p.write_text(textwrap.dedent(content).lstrip(), encoding="utf-8")
    return p


# ----- Happy path -----------------------------------------------------------


def test_load_minimal_valid_yaml(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        rules:
          TS-1:
            tier: A
            source: GGA
            severity: ALTA
            action_hint: eslint-fix
            description: "Some desc"
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: unknown-rule-log-for-calibration
        """,
    )

    rules = load_rules(path)

    assert isinstance(rules, ClassifierRules)
    assert rules.version == "0.1.0"
    assert "TS-1" in rules.rules
    assert rules.rules["TS-1"].tier == "A"
    assert rules.rules["TS-1"].source == "GGA"
    assert rules.rules["TS-1"].action_hint == "eslint-fix"
    assert rules.defaults.unknown_rule_tier == "C"


def test_load_productive_rules_yaml() -> None:
    """Smoke test del rules.yaml productivo (catalogo Sprint 1 curado: 15A + 7B + 5C)."""
    rules = load_rules(REAL_RULES_PATH)

    assert len(rules.rules) == 27

    tiers = [r.tier for r in rules.rules.values()]
    assert tiers.count("A") == 15
    assert tiers.count("B") == 7
    assert tiers.count("C") == 5

    assert rules.defaults.unknown_rule_tier == "C"
    assert (
        rules.defaults.unknown_rule_action_hint
        == "unknown-rule-log-for-calibration"
    )


def test_load_ignores_optional_metadata(tmp_path: Path) -> None:
    """Forward-compat: keys top-level adicionales (metadata) no rompen."""
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        metadata:
          created: "2026-05-22"
          curator: "operador"
        rules:
          TS-1:
            tier: A
            source: GGA
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: x
        """,
    )

    rules = load_rules(path)
    assert "TS-1" in rules.rules


# ----- Schema errors (S-1 adversariales) -----------------------------------


def test_empty_yaml_raises(tmp_path: Path) -> None:
    path = _write(tmp_path, "")
    with pytest.raises(SchemaError, match="empty"):
        load_rules(path)


def test_yaml_missing_rules_key(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: x
        """,
    )
    with pytest.raises(SchemaError, match=r"missing required top-level keys.*rules"):
        load_rules(path)


def test_yaml_missing_version_key(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
        rules: {}
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: x
        """,
    )
    with pytest.raises(SchemaError, match=r"missing required top-level keys.*version"):
        load_rules(path)


def test_yaml_invalid_tier_raises_with_rule_id(tmp_path: Path) -> None:
    """SchemaError debe apuntar al rule_id ofensor (no genérico)."""
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        rules:
          BAD-RULE:
            tier: Z
            source: GGA
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: x
        """,
    )
    with pytest.raises(SchemaError, match=r"'BAD-RULE'.*invalid tier.*'Z'"):
        load_rules(path)


def test_yaml_missing_source_raises(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        rules:
          NO-SOURCE-RULE:
            tier: A
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: x
        """,
    )
    with pytest.raises(SchemaError, match=r"'NO-SOURCE-RULE'.*'source'"):
        load_rules(path)


def test_yaml_with_bom_loads_ok(tmp_path: Path) -> None:
    """BOM UTF-8 debe ser eliminado, file debe cargar."""
    path = tmp_path / "rules.yaml"
    path.write_bytes(
        b"\xef\xbb\xbf"
        b'version: "0.1.0"\n'
        b"rules:\n"
        b"  TS-1:\n"
        b"    tier: A\n"
        b"    source: GGA\n"
        b"defaults:\n"
        b"  unknown_rule_tier: C\n"
        b"  unknown_rule_action_hint: x\n"
    )
    rules = load_rules(path)
    assert "TS-1" in rules.rules


def test_yaml_with_tabs_raises_parser_error(tmp_path: Path) -> None:
    """YAML no permite tabs para indentacion; parser falla loud."""
    path = tmp_path / "rules.yaml"
    path.write_text(
        'version: "0.1.0"\n'
        "rules:\n"
        "\tTS-1:\n"
        "\t\ttier: A\n"
        "defaults:\n"
        "  unknown_rule_tier: C\n"
        "  unknown_rule_action_hint: x\n",
        encoding="utf-8",
    )
    with pytest.raises(SchemaError, match=r"YAML parse error"):
        load_rules(path)


def test_invalid_default_tier(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        rules: {}
        defaults:
          unknown_rule_tier: Z
          unknown_rule_action_hint: x
        """,
    )
    with pytest.raises(SchemaError, match=r"unknown_rule_tier.*'Z'"):
        load_rules(path)


def test_top_level_not_mapping(tmp_path: Path) -> None:
    path = _write(tmp_path, "- just\n- a\n- list\n")
    with pytest.raises(SchemaError, match=r"must be a mapping"):
        load_rules(path)


def test_rule_config_not_mapping(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        rules:
          BROKEN-RULE: "this should be a mapping not a string"
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: x
        """,
    )
    with pytest.raises(SchemaError, match=r"'BROKEN-RULE'.*must be a mapping"):
        load_rules(path)


def test_defaults_not_mapping(tmp_path: Path) -> None:
    path = _write(
        tmp_path,
        """
        version: "0.1.0"
        rules: {}
        defaults: "broken"
        """,
    )
    with pytest.raises(SchemaError, match=r"'defaults' must be a mapping"):
        load_rules(path)
