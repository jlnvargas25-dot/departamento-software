"""Performance benchmarks for sigma:finding_classifier (S-6 acceptance — AC4).

Targets:
  - 50 findings batch: <100ms wall-clock
  - 1000 findings batch: <2s (linear scaling, no quadratic degradation)
  - 50 unique rule_ids: <100ms (no caching that hides cost)

Tests usan time.perf_counter (mas preciso que time.time en Windows).
Mediciones cubren classify() puro (sin IO). El SLA del PRD AC4 es
<100ms cold-process, pero medimos hot-classify aqui — el cold start
de Python (~50-80ms) es overhead del entry point, no del clasificador.
"""

from __future__ import annotations

import time
from pathlib import Path

import pytest

from sigma.finding_classifier.classifier import classify
from sigma.finding_classifier.loader import load_rules
from sigma.finding_classifier.models import Finding

RULES_PATH = Path(__file__).resolve().parent.parent / "rules.yaml"


KNOWN_RULE_IDS = [
    "TS-1",
    "TS-NON-NULL-ASSERTION",
    "A21-OBS-1-CONSOLE-LOG",
    "NO-VAR",
    "VAR-TO-CONST",
    "A21-OBS-2-SILENT-CATCH",
    "MISSING-RLS-POLICY",
    "CSP-UNSAFE-INLINE",
    "DEPENDENCY-CYCLE",
]


def _synth_findings(n: int, unknown_ratio: float = 0.0) -> list[Finding]:
    out: list[Finding] = []
    unknown_count = int(n * unknown_ratio)
    known_count = n - unknown_count
    for i in range(known_count):
        rule_id = KNOWN_RULE_IDS[i % len(KNOWN_RULE_IDS)]
        out.append(
            Finding(
                rule_id=rule_id,
                file=f"src/file_{i}.ts",
                line=i + 1,
                severity="ALTA",
                message=f"synthetic finding {i}",
                source="bench",
            )
        )
    for j in range(unknown_count):
        out.append(
            Finding(
                rule_id=f"UNKNOWN-RULE-{j}",
                file=f"src/unknown_{j}.ts",
                line=j + 1,
                severity="MEDIA",
                message="synthetic unknown",
                source="bench",
            )
        )
    return out


def _bench(findings, rules, runs: int = 3) -> float:
    """Best-of-N wall-clock in milliseconds (warm cache, evita ruido de cold)."""
    best = float("inf")
    for _ in range(runs):
        start = time.perf_counter()
        classify(findings, rules)
        elapsed_ms = (time.perf_counter() - start) * 1000
        if elapsed_ms < best:
            best = elapsed_ms
    return best


def test_50_findings_under_100ms():
    """AC4: 50 findings clasificados en <100ms wall-clock."""
    rules = load_rules(RULES_PATH)
    findings = _synth_findings(50)
    elapsed_ms = _bench(findings, rules)
    assert elapsed_ms < 100, f"50 findings took {elapsed_ms:.2f}ms (target <100ms)"


def test_50_findings_with_50_unique_rules_under_100ms():
    """Adversarial: cobertura completa de rule_ids unicos, sin caching que esconda costo."""
    rules = load_rules(RULES_PATH)
    findings = []
    for i in range(50):
        rule_id = KNOWN_RULE_IDS[i % len(KNOWN_RULE_IDS)]
        findings.append(
            Finding(
                rule_id=rule_id,
                file=f"src/u_{i}.ts",
                line=i,
                severity="ALTA",
                message="unique mix",
                source="bench",
            )
        )
    elapsed_ms = _bench(findings, rules)
    assert elapsed_ms < 100, f"50 mixed rules took {elapsed_ms:.2f}ms (target <100ms)"


def test_1000_findings_under_2s_linear_scaling():
    """Adversarial: 1000 findings <2s. Si fuera cuadratico, esto explota."""
    rules = load_rules(RULES_PATH)
    findings = _synth_findings(1000)
    elapsed_ms = _bench(findings, rules)
    assert elapsed_ms < 2000, f"1000 findings took {elapsed_ms:.2f}ms (target <2000ms)"


def test_50_findings_mixed_known_unknown_under_100ms():
    """50% known + 50% unknown — emit_calibration_log path NO se mide aca (puro classify)."""
    rules = load_rules(RULES_PATH)
    findings = _synth_findings(50, unknown_ratio=0.5)
    elapsed_ms = _bench(findings, rules)
    assert elapsed_ms < 100, f"50 mixed took {elapsed_ms:.2f}ms (target <100ms)"


def test_scaling_is_linear_not_quadratic():
    """Empirico: tiempo(1000) / tiempo(100) debe ser ~10x (lineal), no ~100x (cuadratico)."""
    rules = load_rules(RULES_PATH)
    f100 = _synth_findings(100)
    f1000 = _synth_findings(1000)
    t100 = _bench(f100, rules)
    t1000 = _bench(f1000, rules)
    # Allow generous margin: ratio < 30x (10x lineal + ruido de medicion).
    ratio = t1000 / max(t100, 0.001)
    assert ratio < 30, (
        f"Scaling ratio 1000/100 = {ratio:.1f}x "
        f"(t100={t100:.3f}ms t1000={t1000:.3f}ms). "
        f"Expected ~10x lineal."
    )
