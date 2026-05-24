"""Tests para template_loader.py — S-1 foundation."""

import pytest
from pathlib import Path

from sigma.correction_agent_bounded.template_loader import (
    load_template,
    load_all_templates,
    TemplateLoadError,
)
from sigma.correction_agent_bounded.models import TemplateConfig

TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "correction"


class TestLoadTemplate:
    def test_load_valid_template(self):
        t = load_template(TEMPLATES_DIR / "inject-logger-with-request-id.yaml")
        assert isinstance(t, TemplateConfig)
        assert t.action_hint == "inject-logger-with-request-id"
        assert t.opt_out_marker == "// @intentional-silent"
        assert t.creates_file is False

    def test_load_adr_stub_template(self):
        t = load_template(TEMPLATES_DIR / "generate-adr-stub.yaml")
        assert t.creates_file is True
        assert t.target_file_override is not None

    def test_missing_file_raises(self):
        with pytest.raises(FileNotFoundError):
            load_template(TEMPLATES_DIR / "nonexistent.yaml")

    def test_malformed_yaml_raises(self, tmp_path):
        bad = tmp_path / "bad.yaml"
        bad.write_text("just a string", encoding="utf-8")
        with pytest.raises(TemplateLoadError, match="expected YAML mapping"):
            load_template(bad)

    def test_missing_required_field_raises(self, tmp_path):
        incomplete = tmp_path / "incomplete.yaml"
        incomplete.write_text(
            "action_hint: test\nprompt_template: hello\n", encoding="utf-8"
        )
        with pytest.raises(TemplateLoadError, match="verification_pattern"):
            load_template(incomplete)


class TestLoadAllTemplates:
    def test_load_all_seven(self):
        templates = load_all_templates(TEMPLATES_DIR)
        assert len(templates) == 7
        assert "inject-logger-with-request-id" in templates
        assert "generate-adr-stub" in templates
        assert "generate-zod-schema-for-input" in templates

    def test_missing_dir_raises(self):
        with pytest.raises(FileNotFoundError):
            load_all_templates("/nonexistent/path")

    def test_empty_dir(self, tmp_path):
        templates = load_all_templates(tmp_path)
        assert templates == {}
