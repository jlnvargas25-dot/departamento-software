"""Tests para models.py — S-1 foundation."""

import pytest

from sigma.correction_agent_bounded.models import (
    CorrectionResult,
    CorrectionStatus,
    ProjectContext,
    TemplateConfig,
)


class TestCorrectionStatus:
    def test_values(self):
        assert CorrectionStatus.APPLIED == "applied"
        assert CorrectionStatus.NO_OP == "no_op"
        assert CorrectionStatus.ESCALATED_TO_C == "escalated_to_c"

    def test_from_string(self):
        assert CorrectionStatus("applied") is CorrectionStatus.APPLIED


class TestTemplateConfig:
    def test_required_fields(self):
        t = TemplateConfig(
            action_hint="inject-logger",
            prompt_template="Fix the catch block",
            verification_pattern=r"logger\.(warn|error)",
        )
        assert t.action_hint == "inject-logger"
        assert t.opt_out_marker is None
        assert t.creates_file is False

    def test_all_fields(self):
        t = TemplateConfig(
            action_hint="generate-adr-stub",
            prompt_template="Generate ADR",
            verification_pattern="## Decision",
            opt_out_marker=None,
            creates_file=True,
            target_file_override="decisions/ADR-999.md",
        )
        assert t.creates_file is True
        assert t.target_file_override == "decisions/ADR-999.md"

    def test_frozen(self):
        t = TemplateConfig(
            action_hint="x", prompt_template="y", verification_pattern="z"
        )
        with pytest.raises(AttributeError):
            t.action_hint = "changed"


class TestProjectContext:
    def test_required_fields(self):
        ctx = ProjectContext(
            logger="pino",
            logger_import="@/lib/logger",
            request_id_source="req.requestId",
            auth_library="supabase",
            tenant_scope_field="organization_id",
            rls_migration_file="supabase/migrations/001_security.sql",
        )
        assert ctx.logger == "pino"
        assert ctx.zod_import == "zod"
        assert ctx.adr_directory == "decisions/"

    def test_custom_defaults(self):
        ctx = ProjectContext(
            logger="winston",
            logger_import="winston",
            request_id_source="ctx.requestId",
            auth_library="clerk",
            tenant_scope_field="org_id",
            rls_migration_file="db/security.sql",
            zod_import="@/lib/zod",
            feature_flag_config="flags.json",
            adr_directory="docs/adrs/",
        )
        assert ctx.zod_import == "@/lib/zod"
        assert ctx.adr_directory == "docs/adrs/"

    def test_frozen(self):
        ctx = ProjectContext(
            logger="pino",
            logger_import="@/lib/logger",
            request_id_source="req.requestId",
            auth_library="supabase",
            tenant_scope_field="organization_id",
            rls_migration_file="x.sql",
        )
        with pytest.raises(AttributeError):
            ctx.logger = "changed"


class TestCorrectionResult:
    def test_applied(self):
        r = CorrectionResult(
            rule_id="A21-OBS-2-SILENT-CATCH",
            file="client.ts",
            line=42,
            action_hint="inject-logger-with-request-id",
            status=CorrectionStatus.APPLIED,
            patch_summary="Added logger.warn in catch block",
            tokens_used=850,
            latency_ms=2400,
        )
        assert r.status == CorrectionStatus.APPLIED
        assert r.escalation_reason is None

    def test_escalated(self):
        r = CorrectionResult(
            rule_id="A21-OBS-2-SILENT-CATCH",
            file="client.ts",
            line=42,
            action_hint="inject-logger-with-request-id",
            status=CorrectionStatus.ESCALATED_TO_C,
            escalation_reason="verification failed: pattern not found",
        )
        assert r.status == CorrectionStatus.ESCALATED_TO_C
        assert "verification failed" in r.escalation_reason

    def test_no_op(self):
        r = CorrectionResult(
            rule_id="A21-OBS-2-SILENT-CATCH",
            file="client.ts",
            line=42,
            action_hint="inject-logger-with-request-id",
            status=CorrectionStatus.NO_OP,
        )
        assert r.tokens_used == 0
        assert r.latency_ms == 0
