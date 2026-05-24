"""Tests para pipeline CLI."""

import json
from io import StringIO
from pathlib import Path

from sigma.pipeline.cli import main

RULES_PATH = str(Path(__file__).parents[3] / "sigma" / "finding_classifier" / "rules.yaml")


def _run(input_json, tmp_path, extra_args=None):
    stdin = StringIO(json.dumps(input_json) if isinstance(input_json, list) else input_json)
    stdout = StringIO()
    stderr = StringIO()
    argv = ["--rules", RULES_PATH, "--adr-directory", str(tmp_path), "--dry-run"]
    if extra_args:
        argv.extend(extra_args)
    code = main(argv=argv, stdin=stdin, stdout=stdout, stderr=stderr)
    stdout.seek(0)
    return code, stdout.read(), stderr.getvalue()


class TestPipelineCLI:
    def test_empty_input(self, tmp_path):
        code, out, _ = _run("", tmp_path)
        assert code == 0
        result = json.loads(out)
        assert result["summary"]["total"] == 0

    def test_dry_run_mixed(self, tmp_path):
        findings = [
            {"rule_id": "TS-1", "file": "x.ts", "line": 1, "severity": "ALTA", "source": "GGA", "message": "test"},
            {"rule_id": "CSP-UNSAFE-EVAL", "file": "y.ts", "line": 5, "severity": "CRITICA", "source": "GGA", "message": "csp"},
        ]
        code, out, _ = _run(findings, tmp_path)
        assert code == 0
        result = json.loads(out)
        assert result["summary"]["tier_a"] == 1
        assert result["summary"]["tier_c"] == 1

    def test_invalid_json(self, tmp_path):
        code, _, stderr = _run("{{{bad", tmp_path)
        assert code == 2
        assert "invalid_json" in stderr

    def test_exit_0_on_success(self, tmp_path):
        code, _, _ = _run([], tmp_path)
        assert code == 0
