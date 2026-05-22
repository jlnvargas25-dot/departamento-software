"""Tests for sigma.finding_classifier.classifier — S-2 acceptance (known rules)."""

from __future__ import annotations

from pathlib import Path

import pytest

from sigma.finding_classifier.classifier import classify, unknown_rule_ids
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


@pytest.fixture(scope="module")
def real_rules() -> ClassifierRules:
    return load_rules(REAL_RULES_PATH)


@pytest.fixture
def minimal_rules() -> ClassifierRules:
    return ClassifierRules(
        version="0.1.0",
        rules={
            "TS-1": RuleConfig(
                tier="A", source="GGA", severity="ALTA", action_hint="eslint-fix"
            ),
            "A21-OBS-2-SILENT-CATCH": RuleConfig(
                tier="B",
                source="GGA",
                severity="ALTA",
                action_hint="inject-logger-with-request-id",
            ),
            "CSP-UNSAFE-EVAL": RuleConfig(
                tier="C",
                source="GGA",
                severity="CRITICA",
                action_hint="adr-draft-with-cwe-link",
            ),
        },
        defaults=Defaults(
            unknown_rule_tier="C",
            unknown_rule_action_hint="unknown-rule-log-for-calibration",
        ),
    )


# ----- S-2 Happy path: known rules ------------------------------------------


def test_classify_single_known_finding(minimal_rules: ClassifierRules) -> None:
    finding = _finding("TS-1")
    result = classify([finding], minimal_rules)

    assert len(result) == 1
    classified = result[0]
    assert classified.finding == finding
    assert classified.tier == "A"
    assert classified.action_hint == "eslint-fix"
    assert classified.matched_rule is True


def test_classify_batch_all_known(minimal_rules: ClassifierRules) -> None:
    findings = [
        _finding("TS-1", "auth.ts", 1),
        _finding("TS-1", "todos.ts", 5),
        _finding("A21-OBS-2-SILENT-CATCH", "rep.ts", 10),
        _finding("CSP-UNSAFE-EVAL", "next.config.ts", 28),
        _finding("TS-1", "middleware.ts", 23),
    ]
    result = classify(findings, minimal_rules)

    assert len(result) == 5
    assert all(c.matched_rule for c in result)

    tiers = [c.tier for c in result]
    assert tiers == ["A", "A", "B", "C", "A"]


def test_classify_real_yaml_covers_all_three_tiers(real_rules: ClassifierRules) -> None:
    """Smoke: el YAML productivo discrimina los 3 tiers correctamente."""
    findings = [
        _finding("TS-1"),
        _finding("A22-MISSING-ADR"),
        _finding("CSP-UNSAFE-EVAL"),
    ]
    result = classify(findings, real_rules)

    assert [c.tier for c in result] == ["A", "B", "C"]
    assert all(c.matched_rule for c in result)


# ----- S-2 Adversariales: strict semantics ----------------------------------


def test_classify_is_case_sensitive(minimal_rules: ClassifierRules) -> None:
    """TS-1 != ts-1 — sin lower() silencioso."""
    result = classify([_finding("ts-1")], minimal_rules)
    assert result[0].matched_rule is False
    assert result[0].tier == "C"


def test_classify_rejects_trailing_whitespace(minimal_rules: ClassifierRules) -> None:
    """'TS-1 ' (con espacio final) NO matchea — sin trimming silencioso."""
    result = classify([_finding("TS-1 ")], minimal_rules)
    assert result[0].matched_rule is False


def test_classify_preserves_finding_metadata(minimal_rules: ClassifierRules) -> None:
    """El finding original se preserva sin mutar (frozen dataclass)."""
    finding = _finding("TS-1", file="src/a.ts", line=99)
    result = classify([finding], minimal_rules)
    assert result[0].finding.file == "src/a.ts"
    assert result[0].finding.line == 99
    assert result[0].finding.message == "test"
    assert result[0].finding.source == "GGA"


def test_classify_empty_batch_returns_empty_list(minimal_rules: ClassifierRules) -> None:
    assert classify([], minimal_rules) == []


def test_classify_idempotency_mc2(minimal_rules: ClassifierRules) -> None:
    """MC2: mismo input -> mismo output en 10 corridas seguidas."""
    findings = [
        _finding("TS-1", "a.ts", 1),
        _finding("A21-OBS-2-SILENT-CATCH", "b.ts", 5),
        _finding("UNKNOWN-XYZ", "c.ts", 10),
        _finding("CSP-UNSAFE-EVAL", "d.ts", 15),
    ]
    expected = classify(findings, minimal_rules)
    for _ in range(9):
        assert classify(findings, minimal_rules) == expected


def test_unknown_rule_ids_collects_only_unknown(minimal_rules: ClassifierRules) -> None:
    findings = [
        _finding("TS-1"),
        _finding("UNKNOWN-A"),
        _finding("UNKNOWN-B"),
        _finding("UNKNOWN-A"),  # duplicate
        _finding("CSP-UNSAFE-EVAL"),
    ]
    assert unknown_rule_ids(findings, minimal_rules) == {"UNKNOWN-A", "UNKNOWN-B"}


def test_unknown_rule_ids_empty_when_all_match(minimal_rules: ClassifierRules) -> None:
    findings = [_finding("TS-1"), _finding("CSP-UNSAFE-EVAL")]
    assert unknown_rule_ids(findings, minimal_rules) == set()


# ----- Sanity: classifier no muta filesystem ni red (C1/C4 PRD) ------------


def test_classify_does_not_call_network(minimal_rules: ClassifierRules, monkeypatch) -> None:
    """C1 PRD: sin LLM/network en path de clasificacion."""
    import socket

    def _fail(*args, **kwargs):
        raise RuntimeError("classify must not open sockets")

    monkeypatch.setattr(socket, "socket", _fail)
    monkeypatch.setattr(socket, "create_connection", _fail)
    # Si classify intenta hacer cualquier socket, falla
    result = classify([_finding("TS-1")], minimal_rules)
    assert result[0].tier == "A"
