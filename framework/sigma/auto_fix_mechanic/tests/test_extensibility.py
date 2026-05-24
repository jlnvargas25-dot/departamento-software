"""Tests para extensibilidad AM5 — S-8.

AM5: agregar rule_id nuevo al rules.yaml -> el mechanic lo invoca sin tocar
el core Python. Esto es lo que el plan auditado llama "extensibilidad sin
reescritura".
"""

from __future__ import annotations

import sys
from pathlib import Path

import yaml

from sigma.auto_fix_mechanic.loader import load_handlers
from sigma.auto_fix_mechanic.models import ClassifiedFinding, FixStatus
from sigma.auto_fix_mechanic.orchestrator import run_batch


PYTHON = f'"{sys.executable}"'
WRITE_INVOCATION = (
    f'{PYTHON} -c "import sys;open(sys.argv[1],\'w\').write(\'mock-applied\')" <file>'
)
NOOP_VERIFY = f'{PYTHON} -c "import sys;sys.exit(0)"'


def _write_yaml_via_dump(yaml_path: Path, handlers_dict: dict) -> None:
    """Construye YAML via pyyaml.dump — evita issues de escaping inline."""
    data = {
        "version": "0.1.0-test",
        "handlers": handlers_dict,
        "defaults": {"missing_handler_action": "escalate_to_tier_c"},
        "preflight": {"required_tools": [], "optional_tools": []},
    }
    yaml_path.write_text(yaml.safe_dump(data, sort_keys=False), encoding="utf-8")


def _stub_handler(invocation: str = WRITE_INVOCATION) -> dict:
    return {
        "tool": "stub",
        "invocation": invocation,
        "verification": {"method": "re-run-eslint", "command": NOOP_VERIFY},
    }


def test_new_rule_id_in_yaml_is_invoked_without_code_change(tmp_path: Path):
    yaml_path = tmp_path / "extended.yaml"
    _write_yaml_via_dump(yaml_path, {"MOCK-NEW-RULE": _stub_handler()})

    handlers = load_handlers(yaml_path)
    assert "MOCK-NEW-RULE" in handlers

    target = tmp_path / "target.ts"
    target.write_text("pre")
    finding = ClassifiedFinding(
        rule_id="MOCK-NEW-RULE", file=str(target), line=1, tier="A",
        action_hint="mock-action",
    )
    results = run_batch([finding], handlers)
    assert len(results) == 1
    assert results[0].fix_status is FixStatus.APPLIED
    assert target.read_text() == "mock-applied"


def test_multiple_extended_rules_load_independently(tmp_path: Path):
    yaml_path = tmp_path / "extended.yaml"
    _write_yaml_via_dump(
        yaml_path,
        {
            "R-1": _stub_handler(),
            "R-2": _stub_handler(),
            "R-3": _stub_handler(),
        },
    )
    handlers = load_handlers(yaml_path)
    assert set(handlers.keys()) == {"R-1", "R-2", "R-3"}


def test_unknown_rule_id_still_escalates_with_extended_yaml(tmp_path: Path):
    """El default fallback sigue funcionando con YAML extendido."""
    yaml_path = tmp_path / "extended.yaml"
    _write_yaml_via_dump(yaml_path, {"MOCK-NEW-RULE": _stub_handler()})

    handlers = load_handlers(yaml_path)
    target = tmp_path / "x.ts"
    target.write_text("data")
    finding = ClassifiedFinding(
        rule_id="NOT-IN-YAML", file=str(target), line=1, tier="A",
    )
    results = run_batch([finding], handlers)
    assert results[0].fix_status is FixStatus.ESCALATED_TO_C
    assert results[0].escalation_reason == "handler_not_implemented"
