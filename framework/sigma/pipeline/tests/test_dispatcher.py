"""Tests para dispatcher.py — E2E pipeline."""

import pytest
from pathlib import Path

from sigma.pipeline.dispatcher import dispatch
from sigma.pipeline.models import PipelineResult

RULES_PATH = Path(__file__).parents[3] / "sigma" / "finding_classifier" / "rules.yaml"


def _finding(rule_id, file="src/app.ts", line=10, message="test"):
    return {"rule_id": rule_id, "file": file, "line": line, "message": message, "severity": "ALTA", "source": "GGA"}


class TestDispatchDryRun:
    def test_empty_findings(self):
        result = dispatch([], RULES_PATH, dry_run=True)
        assert isinstance(result, PipelineResult)
        assert result.summary["total"] == 0

    def test_classifies_tier_a(self):
        findings = [_finding("TS-1"), _finding("NO-VAR")]
        result = dispatch(findings, RULES_PATH, dry_run=True)
        assert result.summary["tier_a"] == 2
        assert result.summary["tier_b"] == 0
        assert result.summary["tier_c"] == 0

    def test_classifies_tier_b(self):
        findings = [_finding("A21-OBS-2-SILENT-CATCH"), _finding("MISSING-AUTH-CHECK")]
        result = dispatch(findings, RULES_PATH, dry_run=True)
        assert result.summary["tier_b"] == 2

    def test_classifies_tier_c(self):
        findings = [_finding("CSP-UNSAFE-EVAL"), _finding("DEPENDENCY-CYCLE")]
        result = dispatch(findings, RULES_PATH, dry_run=True)
        assert result.summary["tier_c"] == 2

    def test_mixed_tiers(self):
        findings = [
            _finding("TS-1"),
            _finding("A21-OBS-2-SILENT-CATCH"),
            _finding("CSP-UNSAFE-EVAL"),
            _finding("NO-VAR"),
            _finding("MISSING-RLS-POLICY"),
        ]
        result = dispatch(findings, RULES_PATH, dry_run=True)
        assert result.summary["tier_a"] == 2
        assert result.summary["tier_b"] == 2
        assert result.summary["tier_c"] == 1
        assert result.summary["total"] == 5

    def test_unknown_rule_defaults_to_c(self):
        findings = [_finding("TOTALLY-UNKNOWN-RULE")]
        result = dispatch(findings, RULES_PATH, dry_run=True)
        assert result.summary["tier_c"] == 1

    def test_dry_run_results_have_status(self):
        findings = [_finding("TS-1")]
        result = dispatch(findings, RULES_PATH, dry_run=True)
        assert result.tier_a_results[0]["status"] == "dry_run"


class TestDispatchTierC:
    def test_creates_adr_for_tier_c(self, tmp_path):
        findings = [_finding("CSP-UNSAFE-EVAL", message="unsafe-eval in CSP header")]
        result = dispatch(
            findings, RULES_PATH,
            adr_directory=str(tmp_path),
        )
        assert len(result.tier_c_results) == 1
        assert result.tier_c_results[0]["status"] == "created"
        adrs = list(tmp_path.glob("ADR-*.md"))
        assert len(adrs) == 1
        content = adrs[0].read_text()
        assert "## Decision" in content
        assert "cwe.mitre.org" in content

    def test_idempotency_tier_c(self, tmp_path):
        findings = [_finding("CSP-UNSAFE-EVAL")]
        dispatch(findings, RULES_PATH, adr_directory=str(tmp_path))
        result2 = dispatch(findings, RULES_PATH, adr_directory=str(tmp_path))
        assert result2.tier_c_results[0]["status"] == "no_op"

    def test_multiple_tier_c(self, tmp_path):
        findings = [
            _finding("CSP-UNSAFE-EVAL"),
            _finding("ARCH-HEXAGONAL-VIOLATION"),
            _finding("DEPENDENCY-CYCLE", file="src/mod.ts"),
        ]
        result = dispatch(findings, RULES_PATH, adr_directory=str(tmp_path))
        created = sum(1 for r in result.tier_c_results if r["status"] == "created")
        assert created == 3
        assert len(list(tmp_path.glob("ADR-*.md"))) == 3
