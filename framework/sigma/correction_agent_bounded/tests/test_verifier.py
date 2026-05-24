"""Tests para verifier.py — S-4."""

import pytest
from pathlib import Path

from sigma.correction_agent_bounded.verifier import (
    check_pattern,
    check_file_exists,
    check_opt_out,
)

TARGET_DIR = Path(__file__).parent / "fixtures" / "target_files"


class TestCheckPattern:
    def test_pattern_found_in_file(self, tmp_path):
        f = tmp_path / "fixed.ts"
        f.write_text("try {\n} catch (err) {\n  logger.warn({err});\n}\n")
        assert check_pattern(f, r"logger\.(warn|error)\(") is True

    def test_pattern_not_found(self, tmp_path):
        f = tmp_path / "unfixed.ts"
        f.write_text("try {\n} catch (err) {\n  // empty\n}\n")
        assert check_pattern(f, r"logger\.(warn|error)\(") is False

    def test_pattern_scoped_to_line_window(self, tmp_path):
        f = tmp_path / "scoped.ts"
        lines = ["line\n"] * 100
        lines[50] = "logger.warn(err);\n"
        f.write_text("".join(lines))
        assert check_pattern(f, r"logger\.warn", line=51, window=5) is True
        assert check_pattern(f, r"logger\.warn", line=1, window=5) is False

    def test_nonexistent_file(self):
        assert check_pattern("/nonexistent/file.ts", "anything") is False

    def test_regex_special_chars(self, tmp_path):
        f = tmp_path / "zod.ts"
        f.write_text('const s = z.object({}).parse(input);\n')
        assert check_pattern(f, r"z\.object.*\.parse") is True


class TestCheckFileExists:
    def test_existing_file(self, tmp_path):
        f = tmp_path / "exists.md"
        f.write_text("content")
        assert check_file_exists(f) is True

    def test_nonexistent_file(self):
        assert check_file_exists("/nonexistent/ADR-999.md") is False


class TestCheckOptOut:
    def test_opt_out_marker_present(self):
        assert check_opt_out(
            TARGET_DIR / "silent_catch.ts",
            "// @intentional-silent",
            line=18,
        ) is True

    def test_opt_out_marker_absent(self):
        assert check_opt_out(
            TARGET_DIR / "silent_catch.ts",
            "// @intentional-silent",
            line=11,
        ) is False

    def test_nonexistent_file(self):
        assert check_opt_out("/nonexistent.ts", "marker", line=1) is False

    def test_custom_window(self, tmp_path):
        f = tmp_path / "test.ts"
        lines = ["code\n"] * 20
        lines[10] = "// @skip-fix\n"
        f.write_text("".join(lines))
        assert check_opt_out(f, "// @skip-fix", line=11, window=1) is True
        assert check_opt_out(f, "// @skip-fix", line=1, window=1) is False
