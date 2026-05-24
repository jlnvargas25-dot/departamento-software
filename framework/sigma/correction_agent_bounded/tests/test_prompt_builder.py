"""Tests para prompt_builder.py — S-2."""

import pytest
from pathlib import Path

from sigma.correction_agent_bounded.prompt_builder import (
    build_prompt,
    read_snippet,
    estimate_tokens,
    UnresolvedPlaceholderError,
    TOKEN_WARN_THRESHOLD,
)
from sigma.correction_agent_bounded.models import ProjectContext, TemplateConfig

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TARGET_DIR = FIXTURES_DIR / "target_files"


@pytest.fixture
def ctx():
    return ProjectContext(
        logger="pino",
        logger_import="@/lib/logger",
        request_id_source="req.requestId",
        auth_library="supabase",
        tenant_scope_field="organization_id",
        rls_migration_file="supabase/migrations/001_security.sql",
    )


@pytest.fixture
def template():
    return TemplateConfig(
        action_hint="inject-logger-with-request-id",
        prompt_template="Fix catch at line {{line}} using {{logger}} from {{logger_import}}.",
        verification_pattern=r"logger\.(warn|error)",
    )


class TestBuildPrompt:
    def test_contains_template_resolved(self, ctx, template):
        prompt = build_prompt(template, ctx, "client.ts", 42, "catch(err){}", "typescript")
        assert "pino" in prompt
        assert "@/lib/logger" in prompt
        assert "line 42" in prompt

    def test_contains_snippet(self, ctx, template):
        prompt = build_prompt(template, ctx, "client.ts", 42, "catch(err){}", "typescript")
        assert "```typescript" in prompt
        assert "catch(err){}" in prompt

    def test_contains_system_header(self, ctx, template):
        prompt = build_prompt(template, ctx, "x.ts", 1, "code", "typescript")
        assert "code patch generator" in prompt
        assert "ONLY the replacement" in prompt

    def test_extra_values_resolved(self, ctx):
        t = TemplateConfig(
            action_hint="test",
            prompt_template="Table: {{table_name}}",
            verification_pattern="x",
        )
        prompt = build_prompt(t, ctx, "x.sql", 1, "code", "sql",
                              extra_values={"table_name": "items"})
        assert "Table: items" in prompt

    def test_unresolved_placeholder_uses_fallback(self, ctx):
        t = TemplateConfig(
            action_hint="test",
            prompt_template="Unknown: {{nonexistent_field}}",
            verification_pattern="x",
        )
        prompt = build_prompt(t, ctx, "x.ts", 1, "code", "typescript")
        assert "<nonexistent_field>" in prompt

    def test_token_estimate_under_threshold(self, ctx, template):
        prompt = build_prompt(template, ctx, "x.ts", 1, "short", "typescript")
        tokens = estimate_tokens(prompt)
        assert tokens < TOKEN_WARN_THRESHOLD


class TestReadSnippet:
    def test_read_ts_file(self):
        snippet, lang = read_snippet(TARGET_DIR / "silent_catch.ts", 11)
        assert "catch" in snippet
        assert lang == "typescript"

    def test_read_sql_file(self):
        snippet, lang = read_snippet(TARGET_DIR / "missing_rls.sql", 3)
        assert "CREATE TABLE" in snippet
        assert lang == "sql"

    def test_window_clamps_to_file_bounds(self):
        snippet, _ = read_snippet(TARGET_DIR / "silent_catch.ts", 1, window=100)
        assert "createTodo" in snippet


class TestEstimateTokens:
    def test_short_text(self):
        assert estimate_tokens("hello world") == 2

    def test_empty(self):
        assert estimate_tokens("") == 0
