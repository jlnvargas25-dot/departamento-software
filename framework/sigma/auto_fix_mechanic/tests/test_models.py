"""Tests para sigma.auto_fix_mechanic.models — S-1 foundation.

Cubre AC-S1-4 (PatchResult frozen) + tipos esperados por contrato del PRD.
"""

import dataclasses

import pytest

from sigma.auto_fix_mechanic.models import (
    FixStatus,
    Handler,
    PatchResult,
    ToolboxStatus,
    VerificationResult,
)


# ---------------------------------------------------------------------------
# FixStatus + VerificationResult enums
# ---------------------------------------------------------------------------


def test_fix_status_has_4_variants():
    assert {s.value for s in FixStatus} == {
        "applied",
        "rolled_back",
        "escalated_to_c",
        "noop_already_clean",
    }


def test_verification_result_has_3_variants():
    assert {v.value for v in VerificationResult} == {
        "passed",
        "failed",
        "not_attempted",
    }


def test_fix_status_value_is_string_literal():
    # Para serializacion JSON downstream
    assert FixStatus.APPLIED.value == "applied"
    assert FixStatus.ROLLED_BACK.value == "rolled_back"


# ---------------------------------------------------------------------------
# Handler — modelo interno
# ---------------------------------------------------------------------------


def test_handler_required_fields():
    h = Handler(rule_id="TS-1", tool="eslint")
    assert h.rule_id == "TS-1"
    assert h.tool == "eslint"


def test_handler_optional_fields_have_safe_defaults():
    h = Handler(rule_id="TS-1", tool="eslint")
    assert h.invocation is None
    assert h.codemod_script is None
    assert h.pattern_target == ""
    assert h.transformation == ""
    assert h.verification == {}
    assert h.rollback_strategy == "file-level-revert"
    assert h.notes is None
    assert h.optional_tool_unavailable is False


def test_handler_is_frozen():
    h = Handler(rule_id="TS-1", tool="eslint")
    with pytest.raises(dataclasses.FrozenInstanceError):
        h.rule_id = "TS-2"


def test_handler_verification_factory_not_shared_between_instances():
    # field(default_factory=dict) debe crear dict nuevo por instancia, no compartirlo
    h1 = Handler(rule_id="TS-1", tool="eslint")
    h2 = Handler(rule_id="TS-2", tool="eslint")
    assert h1.verification is not h2.verification


# ---------------------------------------------------------------------------
# ToolboxStatus
# ---------------------------------------------------------------------------


def test_toolbox_status_minimal_construction():
    s = ToolboxStatus(required_tools_ok=True, optional_tools_ok=True)
    assert s.required_tools_ok is True
    assert s.optional_tools_ok is True
    assert s.missing_required == []
    assert s.missing_optional == []
    assert s.disabled_handlers == []


def test_toolbox_status_with_missing_tools():
    s = ToolboxStatus(
        required_tools_ok=False,
        optional_tools_ok=True,
        missing_required=["node"],
    )
    assert s.required_tools_ok is False
    assert s.missing_required == ["node"]


def test_toolbox_status_is_frozen():
    s = ToolboxStatus(required_tools_ok=True, optional_tools_ok=True)
    with pytest.raises(dataclasses.FrozenInstanceError):
        s.required_tools_ok = False


# ---------------------------------------------------------------------------
# PatchResult — output publico (AC-S1-4)
# ---------------------------------------------------------------------------


def test_patch_result_required_fields():
    r = PatchResult(
        rule_id="TS-1",
        file="src/foo.ts",
        line=42,
        action_hint="eslint-fix",
        fix_status=FixStatus.APPLIED,
        verification=VerificationResult.PASSED,
    )
    assert r.rule_id == "TS-1"
    assert r.file == "src/foo.ts"
    assert r.line == 42
    assert r.action_hint == "eslint-fix"
    assert r.fix_status is FixStatus.APPLIED
    assert r.verification is VerificationResult.PASSED


def test_patch_result_optional_fields_defaults():
    r = PatchResult(
        rule_id="TS-1",
        file="src/foo.ts",
        line=42,
        action_hint="eslint-fix",
        fix_status=FixStatus.APPLIED,
        verification=VerificationResult.PASSED,
    )
    assert r.patch_summary is None
    assert r.rollback_reason is None
    assert r.escalation_reason is None
    assert r.tool_used is None
    assert r.elapsed_ms == 0


def test_patch_result_is_frozen():
    # AC-S1-4: mutacion raise FrozenInstanceError
    r = PatchResult(
        rule_id="TS-1",
        file="src/foo.ts",
        line=42,
        action_hint="eslint-fix",
        fix_status=FixStatus.APPLIED,
        verification=VerificationResult.PASSED,
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        r.fix_status = FixStatus.ROLLED_BACK


def test_patch_result_with_rollback_reason():
    r = PatchResult(
        rule_id="TS-1",
        file="src/foo.ts",
        line=42,
        action_hint="eslint-fix",
        fix_status=FixStatus.ROLLED_BACK,
        verification=VerificationResult.FAILED,
        rollback_reason="post_fix_verification_failed:pattern still present",
        elapsed_ms=312,
    )
    assert r.fix_status is FixStatus.ROLLED_BACK
    assert r.rollback_reason.startswith("post_fix_verification_failed")
    assert r.elapsed_ms == 312


def test_patch_result_with_escalation_reason():
    r = PatchResult(
        rule_id="UNKNOWN-RULE",
        file="src/foo.ts",
        line=10,
        action_hint="",
        fix_status=FixStatus.ESCALATED_TO_C,
        verification=VerificationResult.NOT_ATTEMPTED,
        escalation_reason="handler_not_implemented",
    )
    assert r.fix_status is FixStatus.ESCALATED_TO_C
    assert r.verification is VerificationResult.NOT_ATTEMPTED
    assert r.escalation_reason == "handler_not_implemented"
