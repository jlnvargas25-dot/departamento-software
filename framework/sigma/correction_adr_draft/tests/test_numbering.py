"""Tests para numbering.py."""

from sigma.correction_adr_draft.numbering import next_adr_number, adr_slug


class TestNextAdrNumber:
    def test_empty_dir(self, tmp_path):
        assert next_adr_number(tmp_path) == 1

    def test_nonexistent_dir(self, tmp_path):
        assert next_adr_number(tmp_path / "nope") == 1

    def test_existing_adrs(self, tmp_path):
        (tmp_path / "ADR-001-first.md").write_text("x")
        (tmp_path / "ADR-005-fifth.md").write_text("x")
        (tmp_path / "ADR-003-third.md").write_text("x")
        assert next_adr_number(tmp_path) == 6

    def test_ignores_non_adr_files(self, tmp_path):
        (tmp_path / "README.md").write_text("x")
        (tmp_path / "ADR-002-real.md").write_text("x")
        assert next_adr_number(tmp_path) == 3


class TestAdrSlug:
    def test_simple(self):
        assert adr_slug("CSP-UNSAFE-EVAL", "src/app.ts") == "csp-unsafe-eval-app"

    def test_underscores_converted(self):
        assert adr_slug("ARCH_HEX_VIOLATION", "my_file.ts") == "arch-hex-violation-my-file"

    def test_nested_path(self):
        assert adr_slug("DEP-CYCLE", "src/deep/module.ts") == "dep-cycle-module"
