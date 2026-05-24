"""Tests para drafter.py."""

from sigma.correction_adr_draft.drafter import draft_one, draft_all
from sigma.correction_adr_draft.models import DraftStatus


def _finding(rule_id, action_hint, file="src/app.ts", line=10):
    return {
        "rule_id": rule_id, "file": file, "line": line,
        "action_hint": action_hint, "tier": "C",
        "message": f"Test finding for {rule_id}",
    }


class TestDraftOne:
    def test_creates_adr_for_csp(self, tmp_path):
        r = draft_one(_finding("CSP-UNSAFE-EVAL", "adr-draft-with-cwe-link"), tmp_path)
        assert r.status == DraftStatus.CREATED
        assert r.adr_path is not None
        content = (tmp_path / r.adr_path.split("/")[-1]).read_text()
        assert "## Decision" in content
        assert "PENDING" in content
        assert "cwe.mitre.org" in content

    def test_creates_adr_for_arch_review(self, tmp_path):
        r = draft_one(_finding("ARCH-HEXAGONAL-VIOLATION", "flag-for-arch-review"), tmp_path)
        assert r.status == DraftStatus.CREATED
        content = (tmp_path / r.adr_path.split("/")[-1]).read_text()
        assert "Architecture review" in content

    def test_creates_adr_for_product_decision(self, tmp_path):
        r = draft_one(_finding("SCOPE-DEFERRAL-DECISION", "flag-for-product-decision"), tmp_path)
        assert r.status == DraftStatus.CREATED
        content = (tmp_path / r.adr_path.split("/")[-1]).read_text()
        assert "Product/scope decision" in content

    def test_unknown_hint_skipped(self, tmp_path):
        r = draft_one(_finding("UNKNOWN", "nonexistent-hint"), tmp_path)
        assert r.status == DraftStatus.SKIPPED

    def test_idempotency_no_op(self, tmp_path):
        r1 = draft_one(_finding("CSP-UNSAFE-EVAL", "adr-draft-with-cwe-link"), tmp_path)
        assert r1.status == DraftStatus.CREATED
        r2 = draft_one(_finding("CSP-UNSAFE-EVAL", "adr-draft-with-cwe-link"), tmp_path)
        assert r2.status == DraftStatus.NO_OP

    def test_auto_numbering(self, tmp_path):
        (tmp_path / "ADR-005-existing.md").write_text("x")
        r = draft_one(_finding("CSP-UNSAFE-INLINE", "adr-draft-with-cwe-link"), tmp_path)
        assert "ADR-006" in r.adr_path

    def test_cwe_link_for_csp_inline(self, tmp_path):
        r = draft_one(_finding("CSP-UNSAFE-INLINE", "adr-draft-with-cwe-link"), tmp_path)
        content = (tmp_path / r.adr_path.split("/")[-1]).read_text()
        assert "CWE" in content
        assert "OWASP" in content

    def test_no_cwe_for_arch_rules(self, tmp_path):
        r = draft_one(_finding("DEPENDENCY-CYCLE", "flag-for-arch-review"), tmp_path)
        content = (tmp_path / r.adr_path.split("/")[-1]).read_text()
        assert "Security References" not in content


class TestDraftAll:
    def test_batch_mixed(self, tmp_path):
        findings = [
            _finding("CSP-UNSAFE-EVAL", "adr-draft-with-cwe-link"),
            _finding("ARCH-HEXAGONAL-VIOLATION", "flag-for-arch-review"),
            _finding("UNKNOWN", "nonexistent"),
        ]
        results = draft_all(findings, tmp_path)
        statuses = [r.status for r in results]
        assert DraftStatus.CREATED in statuses
        assert DraftStatus.SKIPPED in statuses
        assert sum(1 for s in statuses if s == DraftStatus.CREATED) == 2

    def test_empty_batch(self, tmp_path):
        results = draft_all([], tmp_path)
        assert results == []
