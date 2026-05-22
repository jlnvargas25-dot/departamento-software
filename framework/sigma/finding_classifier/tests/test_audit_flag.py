"""Tests for sigma.finding_classifier.cli --audit flag (S-5 acceptance)."""

from __future__ import annotations

import io
import json

from sigma.finding_classifier.cli import main


def _finding_dict(rule_id: str, **kw) -> dict:
    return {
        "rule_id": rule_id,
        "file": kw.get("file", "x.ts"),
        "line": kw.get("line", 1),
        "severity": kw.get("severity", "ALTA"),
        "message": kw.get("message", "test"),
        "source": kw.get("source", "GGA"),
    }


def _run(argv, stdin_text=""):
    stdin = io.StringIO(stdin_text)
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = main(argv, stdin=stdin, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def test_audit_flag_emits_tier_summary_to_stderr():
    payload = json.dumps([
        _finding_dict("TS-1"),
        _finding_dict("TS-1"),
        _finding_dict("A21-OBS-2-SILENT-CATCH"),
        _finding_dict("UNKNOWN-ZZZ"),
    ])
    code, out, err = _run(["--audit"], stdin_text=payload)
    assert code == 0
    assert "tier_A:" in err
    assert "tier_B:" in err
    assert "tier_C:" in err
    assert "unknown_rules:" in err
    assert "unknown_rules: 1" in err


def test_audit_flag_summary_counts_correctly():
    """2 tier_A (TS-1 x2), 1 tier_B (A21-OBS-2-SILENT-CATCH), 0 tier_C, 0 unknown."""
    payload = json.dumps([
        _finding_dict("TS-1"),
        _finding_dict("TS-1"),
        _finding_dict("A21-OBS-2-SILENT-CATCH"),
    ])
    code, out, err = _run(["--audit"], stdin_text=payload)
    assert code == 0
    assert "tier_A: 2" in err
    assert "tier_B: 1" in err
    assert "tier_C: 0" in err
    assert "unknown_rules: 0" in err


def test_without_audit_flag_no_tier_summary():
    payload = json.dumps([_finding_dict("TS-1")])
    code, out, err = _run([], stdin_text=payload)
    assert code == 0
    assert "tier_A:" not in err
    assert "tier_B:" not in err
    assert "tier_C:" not in err
    assert "unknown_rules:" not in err


def test_audit_all_unknown_falls_to_tier_c():
    payload = json.dumps([
        _finding_dict("UNK-1"),
        _finding_dict("UNK-2"),
        _finding_dict("UNK-3"),
    ])
    code, out, err = _run(["--audit"], stdin_text=payload)
    assert code == 0
    assert "tier_A: 0" in err
    assert "tier_B: 0" in err
    assert "tier_C: 3" in err
    assert "unknown_rules: 3" in err


def test_audit_empty_stdin_exits_one_no_table():
    code, out, err = _run(["--audit"], stdin_text="")
    assert code == 1
    assert "tier_A:" not in err
    assert "no findings provided" in err.lower()


def test_audit_does_not_modify_stdout_payload():
    """stdout JSON must remain identical with or without --audit."""
    payload = json.dumps([
        _finding_dict("TS-1"),
        _finding_dict("UNKNOWN-RULE"),
    ])
    code_a, out_a, _ = _run([], stdin_text=payload)
    code_b, out_b, _ = _run(["--audit"], stdin_text=payload)
    assert code_a == 0 and code_b == 0
    assert json.loads(out_a) == json.loads(out_b)
