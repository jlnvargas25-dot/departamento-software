"""Tests para patcher.py — S-3."""

import pytest
from pathlib import Path

from sigma.correction_agent_bounded.patcher import apply_patch, apply_new_file


class TestApplyPatch:
    def test_replaces_block(self, tmp_path):
        f = tmp_path / "test.ts"
        f.write_text("line1\nline2\nline3\nline4\nline5\n", encoding="utf-8")
        changed = apply_patch(f, 3, "replaced\n", context_window=1)
        assert changed is True
        content = f.read_text(encoding="utf-8")
        assert "replaced" in content
        assert "line1" in content

    def test_no_op_when_same_content(self, tmp_path):
        f = tmp_path / "test.ts"
        original = "line1\nline2\nline3\n"
        f.write_text(original, encoding="utf-8")
        changed = apply_patch(f, 2, original, context_window=100)
        assert changed is False

    def test_handles_small_file(self, tmp_path):
        f = tmp_path / "small.ts"
        f.write_text("only line\n", encoding="utf-8")
        changed = apply_patch(f, 1, "new line\n", context_window=20)
        assert changed is True
        assert f.read_text(encoding="utf-8").strip() == "new line"

    def test_preserves_lines_outside_window(self, tmp_path):
        f = tmp_path / "big.ts"
        lines = [f"line{i}\n" for i in range(50)]
        f.write_text("".join(lines), encoding="utf-8")
        apply_patch(f, 25, "REPLACED\n", context_window=2)
        result = f.read_text(encoding="utf-8")
        assert "line0" in result
        assert "line49" in result
        assert "REPLACED" in result


class TestApplyNewFile:
    def test_creates_file(self, tmp_path):
        f = tmp_path / "new" / "ADR-999.md"
        result = apply_new_file(f, "# ADR-999\n\n## Decision\nPENDING")
        assert result is True
        assert f.exists()
        assert "## Decision" in f.read_text(encoding="utf-8")

    def test_creates_parent_dirs(self, tmp_path):
        f = tmp_path / "deep" / "nested" / "file.md"
        apply_new_file(f, "content")
        assert f.exists()
