"""Tests for sigma:finding_classifier M2 empirical distribution (S-8 acceptance — AC2).

Mide la distribucion sobre el fixture sprint1-iteracion3.json y verifica
que cada tier cae dentro del band hypothesis ADR-011 ± 15pp.
"""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from sigma.finding_classifier.classifier import classify, unknown_rule_ids
from sigma.finding_classifier.loader import load_rules
from sigma.finding_classifier.models import Finding

FIXTURE = (
    Path(__file__).resolve().parent
    / "fixtures"
    / "sprint1-iteracion3.json"
)
RULES_PATH = Path(__file__).resolve().parent.parent / "rules.yaml"


_BANDS = {
    "A": (45.0, 75.0),
    "B": (15.0, 45.0),
    "C": (0.0, 25.0),
}


def _load_fixture_findings() -> list[Finding]:
    data = json.loads(FIXTURE.read_text(encoding="utf-8-sig"))
    return [
        Finding(
            rule_id=d["rule_id"],
            file=d["file"],
            line=d["line"],
            severity=d["severity"],
            message=d["message"],
            source=d["source"],
        )
        for d in data
    ]


def test_distribution_within_acceptable_range():
    """AC2: cada tier observado cae dentro de hypothesis ±15pp."""
    rules = load_rules(RULES_PATH)
    findings = _load_fixture_findings()
    assert len(findings) > 0, "fixture vacio"

    classified = classify(findings, rules)
    counts = {"A": 0, "B": 0, "C": 0}
    for c in classified:
        counts[c.tier] += 1
    total = len(classified)

    for tier, (lo, hi) in _BANDS.items():
        observed_pct = 100.0 * counts[tier] / total
        assert lo <= observed_pct <= hi, (
            f"Tier {tier}: observed {observed_pct:.1f}% fuera de banda [{lo}-{hi}]%"
        )


def test_mc1_coverage_above_95_percent():
    """Cobertura del catalogo de reglas sobre el fixture debe ser >=95% (MC1)."""
    rules = load_rules(RULES_PATH)
    findings = _load_fixture_findings()
    total = len(findings)
    unknown = len(unknown_rule_ids(findings, rules))
    coverage_pct = 100.0 * (total - unknown) / total
    assert coverage_pct >= 95.0, (
        f"MC1 coverage {coverage_pct:.1f}% por debajo de threshold 95%"
    )


def test_mc2_stability_inter_run_identical_output():
    """MC2: misma entrada en 10 corridas seguidas -> output identico (determinismo)."""
    rules = load_rules(RULES_PATH)
    findings = _load_fixture_findings()
    outputs = []
    for _ in range(10):
        classified = classify(findings, rules)
        snapshot = [
            (c.finding.rule_id, c.finding.file, c.finding.line, c.tier, c.matched_rule)
            for c in classified
        ]
        outputs.append(snapshot)
    assert all(o == outputs[0] for o in outputs), (
        "MC2 violado: salidas no identicas entre corridas"
    )


def test_fixture_size_above_min_threshold():
    """Si fixture <10 findings, AC2 marca low_sample_warning."""
    findings = _load_fixture_findings()
    assert len(findings) >= 10, (
        f"fixture N={len(findings)} <10 — distribucion no es inferible"
    )
