"""Tests para context_loader.py — S-1 foundation."""

import pytest
from pathlib import Path

from sigma.correction_agent_bounded.context_loader import (
    load_context,
    ContextLoadError,
)
from sigma.correction_agent_bounded.models import ProjectContext

FIXTURES_DIR = Path(__file__).parent / "fixtures"


class TestLoadContext:
    def test_load_valid_context(self):
        ctx = load_context(FIXTURES_DIR / "project_context.yaml")
        assert isinstance(ctx, ProjectContext)
        assert ctx.logger == "pino"
        assert ctx.logger_import == "@/lib/logger"
        assert ctx.auth_library == "supabase"
        assert ctx.tenant_scope_field == "organization_id"

    def test_defaults_applied(self):
        ctx = load_context(FIXTURES_DIR / "project_context.yaml")
        assert ctx.zod_import == "zod"
        assert ctx.feature_flag_config == "config.yaml"
        assert ctx.adr_directory == "decisions/"

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_context("/nonexistent/context.yaml")

    def test_malformed_yaml_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("just a string", encoding="utf-8")
        with pytest.raises(ContextLoadError, match="expected YAML mapping"):
            load_context(bad)

    def test_missing_required_field_raises(self, tmp_path):
        incomplete = tmp_path / "incomplete.yaml"
        incomplete.write_text("logger: pino\nlogger_import: x\n", encoding="utf-8")
        with pytest.raises(ContextLoadError, match="missing required fields"):
            load_context(incomplete)

    def test_custom_optional_fields(self, tmp_path):
        full = tmp_path / "full.yaml"
        full.write_text(
            "logger: winston\n"
            "logger_import: winston\n"
            "request_id_source: ctx.rid\n"
            "auth_library: clerk\n"
            "tenant_scope_field: org_id\n"
            "rls_migration_file: db/rls.sql\n"
            "zod_import: '@/zod'\n"
            "feature_flag_config: flags.json\n"
            "adr_directory: docs/adrs/\n",
            encoding="utf-8",
        )
        ctx = load_context(full)
        assert ctx.zod_import == "@/zod"
        assert ctx.adr_directory == "docs/adrs/"
