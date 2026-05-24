"""Tests para cli.py — S-6."""

import json
import pytest
from io import StringIO
from pathlib import Path

from sigma.correction_agent_bounded.cli import main

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "correction"


def _run_cli(input_json, extra_args=None):
    stdin = StringIO(json.dumps(input_json) if isinstance(input_json, list) else input_json)
    stdout = StringIO()
    stderr = StringIO()
    argv = [
        "--context-path", str(FIXTURES_DIR / "project_context.yaml"),
        "--templates-dir", str(TEMPLATES_DIR),
        "--dry-run",
    ]
    if extra_args:
        argv.extend(extra_args)
    code = main(argv=argv, stdin=stdin, stdout=stdout, stderr=stderr)
    stdout.seek(0)
    return code, stdout.read(), stderr.getvalue()


class TestCLI:
    def test_empty_input(self):
        code, out, _ = _run_cli("")
        assert code == 0
        assert json.loads(out) == []

    def test_empty_array(self):
        code, out, _ = _run_cli([])
        assert code == 0
        assert json.loads(out) == []

    def test_dry_run_no_llm_call(self, tmp_path):
        f = tmp_path / "catch.ts"
        f.write_text("try {\n} catch (err) {\n  // empty\n}\n")
        findings = [{
            "rule_id": "A21-OBS-2-SILENT-CATCH",
            "file": str(f), "line": 2,
            "action_hint": "inject-logger-with-request-id", "tier": "B",
        }]
        code, out, _ = _run_cli(findings)
        results = json.loads(out)
        assert len(results) == 1

    def test_exit_1_on_escalation(self, tmp_path):
        f = tmp_path / "x.ts"
        f.write_text("code\n")
        findings = [{
            "rule_id": "UNKNOWN", "file": str(f), "line": 1,
            "action_hint": "nonexistent", "tier": "B",
        }]
        code, out, _ = _run_cli(findings)
        assert code == 1
        results = json.loads(out)
        assert results[0]["status"] == "escalated_to_c"

    def test_invalid_json(self):
        stdin = StringIO("not valid json{{{")
        stdout = StringIO()
        stderr = StringIO()
        code = main(
            argv=["--context-path", str(FIXTURES_DIR / "project_context.yaml"),
                  "--templates-dir", str(TEMPLATES_DIR), "--dry-run"],
            stdin=stdin, stdout=stdout, stderr=stderr,
        )
        assert code == 2
        assert "invalid_json" in stderr.getvalue()

    def test_non_array_json(self):
        stdin = StringIO('{"not": "array"}')
        stdout = StringIO()
        stderr = StringIO()
        code = main(
            argv=["--context-path", str(FIXTURES_DIR / "project_context.yaml"),
                  "--templates-dir", str(TEMPLATES_DIR), "--dry-run"],
            stdin=stdin, stdout=stdout, stderr=stderr,
        )
        assert code == 2

    def test_opt_out_returns_exit_0(self, tmp_path):
        f = tmp_path / "opt.ts"
        f.write_text("try {\n} catch (err) {\n  // @intentional-silent\n}\n")
        findings = [{
            "rule_id": "A21-OBS-2-SILENT-CATCH",
            "file": str(f), "line": 2,
            "action_hint": "inject-logger-with-request-id", "tier": "B",
        }]
        code, out, _ = _run_cli(findings)
        assert code == 0
        results = json.loads(out)
        assert results[0]["status"] == "no_op"
