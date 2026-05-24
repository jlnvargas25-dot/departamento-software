"""Loop principal: load -> prompt -> LLM -> patch -> verify -> result."""

from __future__ import annotations

import sys
import time
from pathlib import Path
from typing import Union

from sigma.auto_fix_mechanic.snapshot import FileSnapshot
from sigma.correction_agent_bounded.context_loader import load_context
from sigma.correction_agent_bounded.llm_client import LLMClient
from sigma.correction_agent_bounded.models import (
    CorrectionResult,
    CorrectionStatus,
    ProjectContext,
    TemplateConfig,
)
from sigma.correction_agent_bounded.patcher import apply_new_file, apply_patch
from sigma.correction_agent_bounded.prompt_builder import (
    build_prompt,
    estimate_tokens,
    read_snippet,
)
from sigma.correction_agent_bounded.template_loader import load_all_templates
from sigma.correction_agent_bounded.verifier import (
    check_file_exists,
    check_opt_out,
    check_pattern,
)


def _log(msg: str, **kwargs: object) -> None:
    """Emit JSON-structured log line to stderr (G-6 compliant)."""
    import json as _json
    print(_json.dumps({"component": "correction-agent", "event": msg, **kwargs}), file=sys.stderr)


def _make_result(
    finding: dict, status: CorrectionStatus, **kwargs: object
) -> CorrectionResult:
    """Build a CorrectionResult from a finding dict and status."""
    return CorrectionResult(
        rule_id=finding["rule_id"],
        file=finding["file"],
        line=finding["line"],
        action_hint=finding.get("action_hint", ""),
        status=status,
        **kwargs,
    )


def _check_skip(
    finding: dict, template: TemplateConfig
) -> CorrectionResult | None:
    """Return a NO_OP result if the finding should be skipped, else None.

    Checks opt-out markers and idempotency (pattern already present).
    """
    file_path = finding["file"]
    line = finding["line"]

    if template.opt_out_marker and check_opt_out(file_path, template.opt_out_marker, line):
        _log("no_op", rule_id=finding["rule_id"], reason="opt-out marker found")
        return _make_result(finding, CorrectionStatus.NO_OP, patch_summary="opt-out marker found")

    if not template.creates_file and check_pattern(file_path, template.verification_pattern, line):
        _log("no_op", rule_id=finding["rule_id"], reason="pattern already present (idempotency)")
        return _make_result(finding, CorrectionStatus.NO_OP, patch_summary="pattern already present")

    return None


def _apply_and_verify(
    template: TemplateConfig,
    file_path: str,
    line: int,
    patch_text: str,
    context: ProjectContext,
    extra_values: dict[str, str] | None,
) -> bool:
    """Apply patch and run deterministic verification.

    For creates_file templates, writes a new file and checks existence.
    For in-place templates, snapshots the file, applies patch, verifies
    with regex, and rolls back on failure.

    Returns True if the verification passed.
    """
    if template.creates_file:
        target = template.target_file_override or file_path
        if "{{" in target:
            vals = {"adr_directory": context.adr_directory, "rls_migration_file": context.rls_migration_file}
            if extra_values:
                vals.update(extra_values)
            for k, v in vals.items():
                target = target.replace("{{" + k + "}}", v)
        apply_new_file(target, patch_text)
        return check_file_exists(target)

    snap = FileSnapshot(file_path)
    with snap:
        apply_patch(file_path, line, patch_text)
        verified = check_pattern(file_path, template.verification_pattern, line)
        if not verified:
            snap.restore()
    return verified


def _call_llm(
    client: LLMClient, prompt: str, finding: dict, tokens_est: int, start: float
) -> str | CorrectionResult:
    """Call LLM and return patch text, or a CorrectionResult on failure.

    Catches ValueError, TimeoutError, and OSError (network failures).
    Programming bugs (KeyError, AttributeError) propagate intentionally.
    """
    try:
        return client.generate_patch(prompt)
    except (ValueError, TimeoutError, OSError, RuntimeError) as exc:
        elapsed = int((time.monotonic() - start) * 1000)
        _log("escalate", rule_id=finding["rule_id"], reason=str(exc))
        return _make_result(
            finding, CorrectionStatus.ESCALATED_TO_C,
            escalation_reason=f"LLM error: {exc}", tokens_used=tokens_est, latency_ms=elapsed,
        )


def _process_one(
    finding: dict,
    templates: dict[str, TemplateConfig],
    context: ProjectContext,
    client: LLMClient,
    extra_values: dict[str, str] | None = None,
) -> CorrectionResult:
    """Process a single Tier B finding: prompt LLM, apply patch, verify."""
    action_hint = finding.get("action_hint", "")
    start = time.monotonic()

    if action_hint not in templates:
        _log("escalate", rule_id=finding["rule_id"], reason="template not found")
        return _make_result(
            finding, CorrectionStatus.ESCALATED_TO_C,
            escalation_reason=f"template not found for action_hint={action_hint}",
        )

    template = templates[action_hint]
    skip = _check_skip(finding, template)
    if skip:
        return skip

    snippet, lang = read_snippet(finding["file"], finding["line"])
    prompt = build_prompt(template, context, finding["file"], finding["line"], snippet, lang, extra_values)
    tokens_est = estimate_tokens(prompt)

    result_or_patch = _call_llm(client, prompt, finding, tokens_est, start)
    if isinstance(result_or_patch, CorrectionResult):
        return result_or_patch
    patch_text = result_or_patch

    verified = _apply_and_verify(template, finding["file"], finding["line"], patch_text, context, extra_values)
    elapsed = int((time.monotonic() - start) * 1000)

    if verified:
        _log("applied", rule_id=finding["rule_id"], file=finding["file"])
        return _make_result(
            finding, CorrectionStatus.APPLIED,
            patch_summary=f"patch applied via {action_hint}", tokens_used=tokens_est, latency_ms=elapsed,
        )

    _log("escalate", rule_id=finding["rule_id"], reason="verification failed")
    return _make_result(
        finding, CorrectionStatus.ESCALATED_TO_C,
        escalation_reason="verification failed: pattern not found post-fix",
        tokens_used=tokens_est, latency_ms=elapsed,
    )


def process_findings(
    findings: list[dict],
    context_path: Union[str, Path],
    templates_dir: Union[str, Path],
    client: LLMClient,
    extra_values: dict[str, str] | None = None,
) -> list[CorrectionResult]:
    """Process a batch of Tier B findings sequentially.

    Each finding is processed independently; one failure does not abort the batch.
    Returns a list of CorrectionResult with aggregate metrics logged to stderr.
    """
    context = load_context(context_path)
    templates = load_all_templates(templates_dir)
    results = [_process_one(f, templates, context, client, extra_values) for f in findings]

    applied = sum(1 for r in results if r.status == CorrectionStatus.APPLIED)
    no_op = sum(1 for r in results if r.status == CorrectionStatus.NO_OP)
    escalated = sum(1 for r in results if r.status == CorrectionStatus.ESCALATED_TO_C)

    _log("summary", total=len(results), applied=applied, no_op=no_op,
         escalated=escalated, tokens=sum(r.tokens_used for r in results),
         latency_ms=sum(r.latency_ms for r in results))

    return results
