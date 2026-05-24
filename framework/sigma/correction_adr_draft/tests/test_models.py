"""Tests para models.py."""

import pytest
from sigma.correction_adr_draft.models import DraftResult, DraftStatus


class TestDraftStatus:
    def test_values(self):
        assert DraftStatus.CREATED == "created"
        assert DraftStatus.NO_OP == "no_op"
        assert DraftStatus.SKIPPED == "skipped"


class TestDraftResult:
    def test_created(self):
        r = DraftResult(
            rule_id="CSP-UNSAFE-EVAL", file="app.ts", line=10,
            action_hint="adr-draft-with-cwe-link",
            status=DraftStatus.CREATED,
            adr_path="decisions/ADR-012-csp-unsafe-eval-app.md",
            summary="ADR-012 draft created",
        )
        assert r.status == DraftStatus.CREATED
        assert "ADR-012" in r.adr_path

    def test_no_op(self):
        r = DraftResult(
            rule_id="CSP-UNSAFE-EVAL", file="app.ts", line=10,
            action_hint="adr-draft-with-cwe-link",
            status=DraftStatus.NO_OP,
        )
        assert r.adr_path is None

    def test_frozen(self):
        r = DraftResult(
            rule_id="X", file="x.ts", line=1,
            action_hint="x", status=DraftStatus.SKIPPED,
        )
        with pytest.raises(AttributeError):
            r.rule_id = "changed"
