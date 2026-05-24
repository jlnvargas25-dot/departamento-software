"""Tests para orchestrator.py — S-5."""

import pytest
import shutil
from pathlib import Path

from sigma.correction_agent_bounded.llm_client import MockLLMClient
from sigma.correction_agent_bounded.models import CorrectionStatus
from sigma.correction_agent_bounded.orchestrator import process_findings

FIXTURES_DIR = Path(__file__).parent / "fixtures"
TEMPLATES_DIR = Path(__file__).parent.parent / "templates" / "correction"


def _make_finding(rule_id, file, line, action_hint):
    return {
        "rule_id": rule_id,
        "file": file,
        "line": line,
        "action_hint": action_hint,
        "tier": "B",
    }


class TestProcessFindings:
    def test_applied_with_mock_llm(self, tmp_path):
        target = tmp_path / "client.ts"
        target.write_text(
            "try {\n  await fetch();\n} catch (err) {\n  // empty\n}\n"
        )
        client = MockLLMClient(default='  logger.warn({ err, requestId: req.requestId }, "Error");\n')
        findings = [_make_finding(
            "A21-OBS-2-SILENT-CATCH", str(target), 3, "inject-logger-with-request-id"
        )]
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client
        )
        assert len(results) == 1
        assert results[0].status == CorrectionStatus.APPLIED
        assert results[0].tokens_used > 0

    def test_escalation_on_verify_fail(self, tmp_path):
        target = tmp_path / "client.ts"
        target.write_text("try {\n  await fetch();\n} catch (err) {\n  // empty\n}\n")
        client = MockLLMClient(default="// still no logger here")
        findings = [_make_finding(
            "A21-OBS-2-SILENT-CATCH", str(target), 3, "inject-logger-with-request-id"
        )]
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client
        )
        assert results[0].status == CorrectionStatus.ESCALATED_TO_C
        assert "verification failed" in results[0].escalation_reason
        content = target.read_text()
        assert "still no logger" not in content

    def test_opt_out_marker_returns_no_op(self, tmp_path):
        target = tmp_path / "client.ts"
        target.write_text(
            "try {\n} catch (err) {\n  // @intentional-silent\n}\n"
        )
        client = MockLLMClient(default="should not be called")
        findings = [_make_finding(
            "A21-OBS-2-SILENT-CATCH", str(target), 2, "inject-logger-with-request-id"
        )]
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client
        )
        assert results[0].status == CorrectionStatus.NO_OP
        assert len(client.calls) == 0

    def test_template_not_found_escalates(self, tmp_path):
        target = tmp_path / "x.ts"
        target.write_text("code\n")
        client = MockLLMClient(default="patch")
        findings = [_make_finding("UNKNOWN", str(target), 1, "nonexistent-template")]
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client
        )
        assert results[0].status == CorrectionStatus.ESCALATED_TO_C
        assert "template not found" in results[0].escalation_reason

    def test_idempotency_returns_no_op(self, tmp_path):
        target = tmp_path / "already_fixed.ts"
        target.write_text(
            "try {\n} catch (err) {\n  logger.warn({err});\n}\n"
        )
        client = MockLLMClient(default="should not be called")
        findings = [_make_finding(
            "A21-OBS-2-SILENT-CATCH", str(target), 3, "inject-logger-with-request-id"
        )]
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client
        )
        assert results[0].status == CorrectionStatus.NO_OP
        assert len(client.calls) == 0

    def test_llm_error_escalates(self, tmp_path):
        target = tmp_path / "client.ts"
        target.write_text("try {\n} catch (err) {\n}\n")
        client = MockLLMClient()
        findings = [_make_finding(
            "A21-OBS-2-SILENT-CATCH", str(target), 2, "inject-logger-with-request-id"
        )]
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client
        )
        assert results[0].status == CorrectionStatus.ESCALATED_TO_C
        assert "LLM error" in results[0].escalation_reason

    def test_batch_mixed_results(self, tmp_path):
        f1 = tmp_path / "empty_catch.ts"
        f1.write_text("try {\n} catch (err) {\n  // empty\n}\n")
        f2 = tmp_path / "opt_out.ts"
        f2.write_text("try {\n} catch (err) {\n  // @intentional-silent\n}\n")
        f3 = tmp_path / "unknown.ts"
        f3.write_text("code\n")

        client = MockLLMClient(default='  logger.warn({ err }, "error");\n')
        findings = [
            _make_finding("A21-OBS-2-SILENT-CATCH", str(f1), 2, "inject-logger-with-request-id"),
            _make_finding("A21-OBS-2-SILENT-CATCH", str(f2), 2, "inject-logger-with-request-id"),
            _make_finding("UNKNOWN", str(f3), 1, "nonexistent-action"),
        ]
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client
        )
        statuses = [r.status for r in results]
        assert CorrectionStatus.APPLIED in statuses
        assert CorrectionStatus.NO_OP in statuses
        assert CorrectionStatus.ESCALATED_TO_C in statuses

    def test_creates_file_for_adr_stub(self, tmp_path):
        target = tmp_path / "dummy.ts"
        target.write_text("code with exception\n")
        adr_content = "# ADR-999\n\n## Decision\nPENDING\n\n## Alternatives\n"
        client = MockLLMClient(default=adr_content)
        findings = [_make_finding("A22-MISSING-ADR", str(target), 1, "generate-adr-stub")]
        adr_dir = str(tmp_path / "decisions")
        results = process_findings(
            findings, FIXTURES_DIR / "project_context.yaml", TEMPLATES_DIR, client,
            extra_values={"next_number": "999", "slug": "test", "title": "Test", "today": "2026-05-24",
                          "description": "test desc", "finding_description": "test finding",
                          "rule_id": "A22", "adr_directory": adr_dir},
        )
        assert results[0].status == CorrectionStatus.APPLIED
        assert (tmp_path / "decisions" / "ADR-999-test.md").exists()
