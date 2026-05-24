"""Tests para sigma.auto_fix_mechanic.cli — S-8 CLI.

Cubre AC-S8-1 (empty input), AC-S8-2 (valid finding), AC-S8-3 (invalid JSON),
AC-S8-5 (metrics).
"""

from __future__ import annotations

import io
import json
import sys
from pathlib import Path

import pytest

from sigma.auto_fix_mechanic.cli import main as cli_main


PRODUCTIVE_YAML = Path(__file__).parent.parent / "rules.yaml"


def _run_cli(stdin_text: str, extra_args: list[str] | None = None):
    stdin = io.StringIO(stdin_text)
    stdout = io.StringIO()
    stderr = io.StringIO()
    argv = ["--rules-path", str(PRODUCTIVE_YAML)] + (extra_args or [])
    exit_code = cli_main(argv=argv, stdin=stdin, stdout=stdout, stderr=stderr)
    return exit_code, stdout.getvalue(), stderr.getvalue()


# AC-S8-1 — Empty input
def test_empty_stdin_returns_empty_array():
    exit_code, stdout, stderr = _run_cli("")
    assert exit_code == 0
    assert stdout.strip() == "[]"


def test_empty_array_input_returns_empty_array():
    exit_code, stdout, stderr = _run_cli("[]")
    assert exit_code == 0
    assert json.loads(stdout) == []


# AC-S8-2 — Valid finding
def test_unknown_rule_id_returns_escalation(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("data")
    finding = {
        "rule_id": "UNKNOWN-RULE-XYZ",
        "file": str(f),
        "line": 1,
        "tier": "A",
        "action_hint": "",
    }
    exit_code, stdout, stderr = _run_cli(json.dumps([finding]))
    assert exit_code == 0
    results = json.loads(stdout)
    assert len(results) == 1
    assert results[0]["fix_status"] == "escalated_to_c"
    assert results[0]["escalation_reason"] == "handler_not_implemented"


def test_non_tier_a_findings_are_filtered():
    finding_b = {"rule_id": "X", "file": "y.ts", "line": 1, "tier": "B"}
    finding_c = {"rule_id": "X", "file": "y.ts", "line": 1, "tier": "C"}
    exit_code, stdout, stderr = _run_cli(json.dumps([finding_b, finding_c]))
    assert exit_code == 0
    results = json.loads(stdout)
    assert results == []


# AC-S8-3 — Invalid JSON
def test_invalid_json_returns_exit_1():
    exit_code, stdout, stderr = _run_cli("not-json{")
    assert exit_code == 1
    assert "invalid JSON" in stderr or "JSON" in stderr


def test_json_root_not_list_returns_exit_1():
    exit_code, stdout, stderr = _run_cli('{"not": "a list"}')
    assert exit_code == 1
    assert "list" in stderr.lower()


def test_missing_required_field_returns_exit_1():
    # Missing 'file' field
    exit_code, stdout, stderr = _run_cli('[{"rule_id": "TS-1"}]')
    assert exit_code == 1


# AC-S8-5 — --metrics emits MM1-MM5
def test_metrics_flag_emits_summary(tmp_path: Path):
    f = tmp_path / "x.ts"
    f.write_text("data")
    finding = {
        "rule_id": "UNKNOWN",
        "file": str(f),
        "line": 1,
        "tier": "A",
    }
    exit_code, stdout, stderr = _run_cli(
        json.dumps([finding]), extra_args=["--metrics"]
    )
    assert exit_code == 0
    assert "[metrics]" in stderr
    assert "M3 applied ratio" in stderr
    assert "escalated_to_c" in stderr


def test_invalid_rules_path_returns_exit_1(tmp_path: Path):
    stdin = io.StringIO("[]")
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = cli_main(
        argv=["--rules-path", str(tmp_path / "nope.yaml")],
        stdin=stdin,
        stdout=stdout,
        stderr=stderr,
    )
    assert exit_code == 1
    assert "failed to load rules" in stderr.getvalue()
