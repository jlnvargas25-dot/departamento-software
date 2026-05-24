"""Tests para cli.py."""

import json
from io import StringIO

from sigma.correction_adr_draft.cli import main


def _run(input_json, tmp_path, extra_args=None):
    stdin = StringIO(json.dumps(input_json) if isinstance(input_json, list) else input_json)
    stdout = StringIO()
    stderr = StringIO()
    argv = ["--adr-directory", str(tmp_path)]
    if extra_args:
        argv.extend(extra_args)
    code = main(argv=argv, stdin=stdin, stdout=stdout, stderr=stderr)
    stdout.seek(0)
    return code, stdout.read(), stderr.getvalue()


class TestCLI:
    def test_empty_input(self, tmp_path):
        code, out, _ = _run("", tmp_path)
        assert code == 0
        assert json.loads(out) == []

    def test_empty_array(self, tmp_path):
        code, out, _ = _run([], tmp_path)
        assert code == 0
        assert json.loads(out) == []

    def test_creates_adr(self, tmp_path):
        findings = [{
            "rule_id": "CSP-UNSAFE-EVAL", "file": "app.ts", "line": 5,
            "action_hint": "adr-draft-with-cwe-link", "tier": "C",
        }]
        code, out, _ = _run(findings, tmp_path)
        assert code == 0
        results = json.loads(out)
        assert len(results) == 1
        assert results[0]["status"] == "created"

    def test_always_exit_0(self, tmp_path):
        findings = [{"rule_id": "X", "file": "x.ts", "line": 1, "action_hint": "unknown", "tier": "C"}]
        code, _, _ = _run(findings, tmp_path)
        assert code == 0

    def test_invalid_json(self, tmp_path):
        code, _, stderr = _run("{{{bad", tmp_path)
        assert code == 0
        assert "invalid_json" in stderr
