"""Tests for sigma:finding_classifier extensibility (S-7 acceptance — AC5).

Verifica que agregar / quitar reglas en YAML cambia la clasificacion
SIN tocar codigo Python. Usa rules.yaml temporal en tmp_path para no
mutar el catalogo productivo.
"""

from __future__ import annotations

import io
import json
import textwrap
from pathlib import Path

import pytest

from sigma.finding_classifier.cli import main


_MINIMAL_YAML = textwrap.dedent("""\
    version: "test-1.0"
    rules:
      R-EXISTING-001:
        tier: A
        source: "test"
        severity: "ALTA"
        action_hint: "fix-it"
    defaults:
      unknown_rule_tier: C
      unknown_rule_action_hint: "unknown-rule-log-for-calibration"
""")


def _finding(rule_id: str) -> dict:
    return {
        "rule_id": rule_id,
        "file": "x.ts",
        "line": 1,
        "severity": "ALTA",
        "message": "test",
        "source": "S-7",
    }


def _run(argv, stdin_text=""):
    stdin = io.StringIO(stdin_text)
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = main(argv, stdin=stdin, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def test_new_rule_added_to_yaml_classifies_without_code_change(tmp_path: Path):
    """AC5: agregar R-NEW-RULE-001 al YAML y el clasificador la reconoce.

    Sin reiniciar nada, sin recompilar, sin tocar Python.
    """
    rules_yaml = tmp_path / "rules.yaml"

    # Paso 1: YAML base sin R-NEW-RULE-001
    rules_yaml.write_text(_MINIMAL_YAML, encoding="utf-8")
    payload = json.dumps([_finding("R-NEW-RULE-001")])

    code_before, out_before, _ = _run(
        ["--rules", str(rules_yaml)], stdin_text=payload
    )
    parsed_before = json.loads(out_before)
    assert code_before == 0
    assert parsed_before[0]["matched_rule"] is False
    assert parsed_before[0]["tier"] == "C"

    # Paso 2: agregar R-NEW-RULE-001 al YAML (tier A) — sin tocar Python
    extended = textwrap.dedent("""\
        version: "test-1.0"
        rules:
          R-NEW-RULE-001:
            tier: A
            source: "sigma:plan-auditor"
            severity: "ALTA"
            action_hint: "eslint-fix"
          R-EXISTING-001:
            tier: A
            source: "test"
            severity: "ALTA"
            action_hint: "fix-it"
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: "unknown-rule-log-for-calibration"
    """)
    rules_yaml.write_text(extended, encoding="utf-8")

    code_after, out_after, _ = _run(
        ["--rules", str(rules_yaml)], stdin_text=payload
    )
    parsed_after = json.loads(out_after)
    assert code_after == 0
    assert parsed_after[0]["matched_rule"] is True
    assert parsed_after[0]["tier"] == "A"
    assert parsed_after[0]["action_hint"] == "eslint-fix"


def test_removed_rule_falls_back_to_tier_c(tmp_path: Path):
    """AC5 inverso: si una regla desaparece del YAML, el finding cae a tier C unknown."""
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text(_MINIMAL_YAML, encoding="utf-8")

    payload = json.dumps([_finding("R-EXISTING-001")])
    code, out, _ = _run(["--rules", str(rules_yaml)], stdin_text=payload)
    assert code == 0
    parsed = json.loads(out)
    assert parsed[0]["matched_rule"] is True
    assert parsed[0]["tier"] == "A"

    # Quitar R-EXISTING-001 del YAML
    stripped = textwrap.dedent("""\
        version: "test-1.0"
        rules: {}
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: "unknown-rule-log-for-calibration"
    """)
    rules_yaml.write_text(stripped, encoding="utf-8")

    code2, out2, _ = _run(["--rules", str(rules_yaml)], stdin_text=payload)
    assert code2 == 0
    parsed2 = json.loads(out2)
    assert parsed2[0]["matched_rule"] is False
    assert parsed2[0]["tier"] == "C"


def test_invalid_tier_in_yaml_rejected_at_load(tmp_path: Path):
    """Adversarial: tier invalido (Z) en YAML -> exit 1 inmediato (schema validation)."""
    rules_yaml = tmp_path / "rules.yaml"
    bad = textwrap.dedent("""\
        version: "test-1.0"
        rules:
          BAD-TIER:
            tier: Z
            source: "test"
            severity: "ALTA"
        defaults:
          unknown_rule_tier: C
          unknown_rule_action_hint: "x"
    """)
    rules_yaml.write_text(bad, encoding="utf-8")

    payload = json.dumps([_finding("BAD-TIER")])
    code, out, err = _run(["--rules", str(rules_yaml)], stdin_text=payload)
    assert code == 1
    assert "tier" in err.lower()


def test_re_running_cli_on_same_input_consistent(tmp_path: Path):
    """MC2 estabilidad inter-corrida: misma entrada -> mismo output en N corridas.

    No hay daemon ni cache cross-process; cada invocacion es proceso nuevo.
    """
    rules_yaml = tmp_path / "rules.yaml"
    rules_yaml.write_text(_MINIMAL_YAML, encoding="utf-8")
    payload = json.dumps([
        _finding("R-EXISTING-001"),
        _finding("UNKNOWN-XYZ"),
    ])
    outputs = []
    for _ in range(5):
        code, out, _ = _run(["--rules", str(rules_yaml)], stdin_text=payload)
        assert code == 0
        outputs.append(out)
    assert all(o == outputs[0] for o in outputs), "outputs diverged across 5 runs"
