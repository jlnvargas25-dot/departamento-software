"""Tests for emit_calibration_log — S-3 acceptance (default Tier C + structured log)."""

from __future__ import annotations

import io
import json
from pathlib import Path

import pytest

from sigma.finding_classifier.classifier import classify, emit_calibration_log
from sigma.finding_classifier.loader import load_rules
from sigma.finding_classifier.models import (
    ClassifierRules,
    Defaults,
    Finding,
    RuleConfig,
)

REAL_RULES_PATH = Path(__file__).resolve().parent.parent / "rules.yaml"


def _finding(rule_id: str, file: str = "x.ts", line: int = 1) -> Finding:
    return Finding(
        rule_id=rule_id,
        file=file,
        line=line,
        severity="ALTA",
        message="test",
        source="GGA",
    )


@pytest.fixture
def minimal_rules() -> ClassifierRules:
    return ClassifierRules(
        version="0.1.0",
        rules={
            "TS-1": RuleConfig(tier="A", source="GGA", severity="ALTA"),
        },
        defaults=Defaults(
            unknown_rule_tier="C",
            unknown_rule_action_hint="unknown-rule-log-for-calibration",
        ),
    )


@pytest.fixture(scope="module")
def real_rules() -> ClassifierRules:
    return load_rules(REAL_RULES_PATH)


# ----- S-3 Default tier C ante unknown rule ---------------------------------


def test_unknown_rule_defaults_to_tier_C(minimal_rules: ClassifierRules) -> None:
    finding = _finding("UNKNOWN-RULE-XYZ", file="src/a.ts", line=42)
    result = classify([finding], minimal_rules)

    assert result[0].tier == "C"
    assert result[0].action_hint == "unknown-rule-log-for-calibration"
    assert result[0].matched_rule is False


def test_unknown_rule_with_real_yaml(real_rules: ClassifierRules) -> None:
    """Sanity: regla inventada cae a C con el YAML productivo."""
    result = classify([_finding("R99-INEXISTENT")], real_rules)
    assert result[0].tier == "C"
    assert result[0].matched_rule is False


# ----- S-3 emit_calibration_log: dedup + cuenta + first_file/line ----------


def test_emit_empty_when_no_unknowns(minimal_rules: ClassifierRules) -> None:
    """No-op silencioso si todos matchean."""
    buf = io.StringIO()
    n = emit_calibration_log([_finding("TS-1")], minimal_rules, stream=buf)
    assert n == 0
    assert buf.getvalue() == ""


def test_emit_empty_with_empty_findings(minimal_rules: ClassifierRules) -> None:
    buf = io.StringIO()
    n = emit_calibration_log([], minimal_rules, stream=buf)
    assert n == 0
    assert buf.getvalue() == ""


def test_emit_single_unknown_emits_one_line(minimal_rules: ClassifierRules) -> None:
    buf = io.StringIO()
    finding = _finding("UNKNOWN-X", file="src/a.ts", line=42)
    n = emit_calibration_log([finding], minimal_rules, stream=buf)

    assert n == 1
    output = buf.getvalue().strip().split("\n")
    assert len(output) == 1
    entry = json.loads(output[0])
    assert entry == {
        "event": "unknown_rule",
        "rule_id": "UNKNOWN-X",
        "count": 1,
        "first_file": "src/a.ts",
        "first_line": 42,
    }


def test_emit_dedups_same_rule_id_with_count(minimal_rules: ClassifierRules) -> None:
    """5 findings con el mismo unknown rule_id -> 1 linea con count=5."""
    buf = io.StringIO()
    findings = [
        _finding("UNKNOWN-Y", file="a.ts", line=1),
        _finding("UNKNOWN-Y", file="b.ts", line=2),
        _finding("UNKNOWN-Y", file="c.ts", line=3),
        _finding("UNKNOWN-Y", file="d.ts", line=4),
        _finding("UNKNOWN-Y", file="e.ts", line=5),
    ]
    n = emit_calibration_log(findings, minimal_rules, stream=buf)

    assert n == 1
    output = buf.getvalue().strip().split("\n")
    assert len(output) == 1
    entry = json.loads(output[0])
    assert entry["rule_id"] == "UNKNOWN-Y"
    assert entry["count"] == 5
    assert entry["first_file"] == "a.ts"
    assert entry["first_line"] == 1


def test_emit_multiple_distinct_unknowns(minimal_rules: ClassifierRules) -> None:
    """3 unknown distintos -> 3 lineas. Cada una JSON parseable."""
    buf = io.StringIO()
    findings = [
        _finding("UNKNOWN-A"),
        _finding("UNKNOWN-B"),
        _finding("UNKNOWN-C"),
    ]
    n = emit_calibration_log(findings, minimal_rules, stream=buf)

    assert n == 3
    lines = [l for l in buf.getvalue().split("\n") if l]
    assert len(lines) == 3
    rule_ids = {json.loads(l)["rule_id"] for l in lines}
    assert rule_ids == {"UNKNOWN-A", "UNKNOWN-B", "UNKNOWN-C"}


def test_emit_ignores_matched_rules(minimal_rules: ClassifierRules) -> None:
    """Findings que matchean no aparecen en el calibration log."""
    buf = io.StringIO()
    findings = [
        _finding("TS-1"),
        _finding("TS-1"),
        _finding("UNKNOWN-Z", file="z.ts", line=99),
    ]
    n = emit_calibration_log(findings, minimal_rules, stream=buf)

    assert n == 1
    entry = json.loads(buf.getvalue().strip())
    assert entry["rule_id"] == "UNKNOWN-Z"
    assert entry["count"] == 1


def test_emit_100_distinct_unknowns_no_cap(minimal_rules: ClassifierRules) -> None:
    """STORIES adversarial: 100 unknown distintos -> 100 lineas, no truncamiento."""
    buf = io.StringIO()
    findings = [_finding(f"UNKNOWN-{i:03d}") for i in range(100)]
    n = emit_calibration_log(findings, minimal_rules, stream=buf)

    assert n == 100
    lines = [l for l in buf.getvalue().split("\n") if l]
    assert len(lines) == 100
    for line in lines:
        entry = json.loads(line)
        assert entry["event"] == "unknown_rule"
        assert entry["count"] == 1


def test_emit_default_stream_is_stderr(
    minimal_rules: ClassifierRules, capsys: pytest.CaptureFixture
) -> None:
    """Sin stream parameter, default es sys.stderr (NO stdout)."""
    emit_calibration_log([_finding("UNKNOWN-DEFAULT")], minimal_rules)

    captured = capsys.readouterr()
    assert captured.out == ""
    assert "UNKNOWN-DEFAULT" in captured.err
    entry = json.loads(captured.err.strip())
    assert entry["rule_id"] == "UNKNOWN-DEFAULT"


# ----- S-3 integration: classify + emit_calibration_log together -----------


def test_classify_and_emit_combined(
    minimal_rules: ClassifierRules, capsys: pytest.CaptureFixture
) -> None:
    """Flujo real del CLI: classify retorna estructura, emit reporta unknowns."""
    findings = [
        _finding("TS-1", file="a.ts", line=1),
        _finding("UNKNOWN-FUTURE-RULE", file="b.ts", line=42),
    ]

    classified = classify(findings, minimal_rules)
    n_unknown = emit_calibration_log(findings, minimal_rules)

    assert [c.tier for c in classified] == ["A", "C"]
    assert [c.matched_rule for c in classified] == [True, False]
    assert n_unknown == 1

    captured = capsys.readouterr()
    entry = json.loads(captured.err.strip())
    assert entry["rule_id"] == "UNKNOWN-FUTURE-RULE"
    assert entry["first_file"] == "b.ts"
    assert entry["first_line"] == 42
