"""Tests for sigma.finding_classifier.cli — S-4 acceptance (CLI stdin/stdout/exit codes)."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from sigma.finding_classifier.cli import main

FIXTURE_DIR = Path(__file__).resolve().parent / "fixtures"
SPRINT1_FIXTURE = FIXTURE_DIR / "sprint1-iteracion3.json"


def _finding_dict(
    rule_id: str = "TS-1",
    file: str = "x.ts",
    line: int = 1,
    severity: str = "ALTA",
    message: str = "test",
    source: str = "GGA",
) -> dict:
    return {
        "rule_id": rule_id,
        "file": file,
        "line": line,
        "severity": severity,
        "message": message,
        "source": source,
    }


def _run(
    argv: list[str],
    stdin_text: str = "",
) -> tuple[int, str, str]:
    stdin = io.StringIO(stdin_text)
    stdout = io.StringIO()
    stderr = io.StringIO()
    exit_code = main(argv, stdin=stdin, stdout=stdout, stderr=stderr)
    return exit_code, stdout.getvalue(), stderr.getvalue()


# --- Happy path ---


def test_stdin_json_array_classifies_and_returns_zero():
    payload = json.dumps([_finding_dict(rule_id="TS-1")])
    code, out, err = _run([], stdin_text=payload)
    assert code == 0
    parsed = json.loads(out)
    assert isinstance(parsed, list)
    assert len(parsed) == 1
    assert parsed[0]["tier"] in ("A", "B", "C")
    assert "matched_rule" in parsed[0]
    assert "finding" in parsed[0]
    assert parsed[0]["finding"]["rule_id"] == "TS-1"


def test_input_flag_reads_from_file(tmp_path: Path):
    findings_file = tmp_path / "findings.json"
    findings_file.write_text(
        json.dumps([_finding_dict(rule_id="TS-1")]),
        encoding="utf-8",
    )
    code, out, err = _run(["--input", str(findings_file)])
    assert code == 0
    parsed = json.loads(out)
    assert len(parsed) == 1


def test_empty_json_array_exits_zero_with_empty_output():
    code, out, err = _run([], stdin_text="[]")
    assert code == 0
    assert json.loads(out) == []


def test_unknown_rule_classified_as_tier_c_and_logged_to_stderr():
    payload = json.dumps([_finding_dict(rule_id="UNKNOWN-RULE-XYZ")])
    code, out, err = _run([], stdin_text=payload)
    assert code == 0
    parsed = json.loads(out)
    assert parsed[0]["tier"] == "C"
    assert parsed[0]["matched_rule"] is False
    # Calibration log emitted to stderr (S-3 integration preserved)
    assert "UNKNOWN-RULE-XYZ" in err
    assert "unknown_rule" in err


def test_multiple_findings_classified_in_order():
    payload = json.dumps([
        _finding_dict(rule_id="TS-1"),
        _finding_dict(rule_id="A21-OBS-2-SILENT-CATCH"),
        _finding_dict(rule_id="UNKNOWN-XYZ"),
    ])
    code, out, err = _run([], stdin_text=payload)
    assert code == 0
    parsed = json.loads(out)
    assert len(parsed) == 3
    assert parsed[0]["finding"]["rule_id"] == "TS-1"
    assert parsed[0]["matched_rule"] is True
    assert parsed[0]["tier"] == "A"
    assert parsed[1]["matched_rule"] is True
    assert parsed[1]["tier"] == "B"
    assert parsed[2]["finding"]["rule_id"] == "UNKNOWN-XYZ"
    assert parsed[2]["matched_rule"] is False
    assert parsed[2]["tier"] == "C"


# --- Adversariales ---


def test_empty_stdin_exits_one():
    code, out, err = _run([], stdin_text="")
    assert code == 1
    assert "no findings provided" in err.lower()


def test_whitespace_only_stdin_exits_one():
    code, out, err = _run([], stdin_text="   \n\n  \t")
    assert code == 1
    assert "no findings provided" in err.lower()


def test_invalid_json_exits_one_with_parse_error():
    code, out, err = _run([], stdin_text="this is not json")
    assert code == 1
    assert "json" in err.lower() or "parse" in err.lower()


def test_input_flag_missing_file_exits_one(tmp_path: Path):
    code, out, err = _run(["--input", str(tmp_path / "nope.json")])
    assert code == 1
    assert "not found" in err.lower() or "no such file" in err.lower()


def test_rules_flag_missing_file_exits_one(tmp_path: Path):
    payload = json.dumps([_finding_dict()])
    code, out, err = _run(
        ["--rules", str(tmp_path / "ghost.yaml")], stdin_text=payload
    )
    assert code == 1


def test_findings_must_be_list_not_dict():
    code, out, err = _run([], stdin_text='{"rule_id": "TS-1"}')
    assert code == 1
    assert "list" in err.lower() or "array" in err.lower()


def test_finding_missing_required_field_exits_one():
    bad = {"rule_id": "TS-1"}  # missing file/line/severity/message/source
    code, out, err = _run([], stdin_text=json.dumps([bad]))
    assert code == 1


def test_main_default_streams_callable_from_entry_point(monkeypatch):
    """sigma-classify entry point calls main() with no kwargs — must not raise on import."""
    from sigma.finding_classifier import cli

    assert callable(cli.main)
