"""E2E dispatcher: classify findings then route to tier handlers."""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Union

from sigma.finding_classifier.classifier import classify
from sigma.finding_classifier.loader import load_rules
from sigma.finding_classifier.models import Finding
from sigma.pipeline.models import PipelineResult


def _log(msg: str, **kwargs: object) -> None:
    """Emit JSON-structured log line to stderr."""
    print(json.dumps({"component": "sigma-pipeline", "event": msg, **kwargs}), file=sys.stderr)


def _to_finding(raw: dict) -> Finding:
    """Convert a raw finding dict to a Finding dataclass."""
    return Finding(
        rule_id=raw["rule_id"],
        file=raw.get("file", ""),
        line=raw.get("line", 0),
        severity=raw.get("severity", ""),
        message=raw.get("message", ""),
        source=raw.get("source", "GGA"),
    )


def _to_handler_input(classified: Any) -> dict:
    """Convert a ClassifiedFinding to a dict for tier handlers."""
    f = classified.finding
    return {
        "rule_id": f.rule_id,
        "file": f.file,
        "line": f.line,
        "severity": f.severity,
        "message": f.message,
        "source": f.source,
        "tier": classified.tier,
        "action_hint": classified.action_hint or "",
    }


def dispatch(
    raw_findings: list[dict],
    rules_path: Union[str, Path],
    mechanic_rules_path: Union[str, Path] | None = None,
    context_path: Union[str, Path] | None = None,
    templates_dir: Union[str, Path] | None = None,
    adr_directory: Union[str, Path] | None = None,
    llm_client: Any = None,
    dry_run: bool = False,
) -> PipelineResult:
    """Classify findings and dispatch to tier-specific handlers.

    Args:
        raw_findings: List of finding dicts with rule_id, file, line, etc.
        rules_path: Path to classifier rules.yaml.
        mechanic_rules_path: Path to mechanic rules.yaml (for Tier A).
        context_path: Path to project_context.yaml (for Tier B).
        templates_dir: Path to correction templates dir (for Tier B).
        adr_directory: Directory for ADR drafts (for Tier C).
        llm_client: LLMClient instance for Tier B (None skips Tier B).
        dry_run: If True, classify only — don't execute handlers.

    Returns:
        PipelineResult with results from each tier handler.
    """
    rules = load_rules(Path(rules_path))
    findings = [_to_finding(r) for r in raw_findings]
    classified = classify(findings, rules)

    tier_a = [_to_handler_input(c) for c in classified if c.tier == "A"]
    tier_b = [_to_handler_input(c) for c in classified if c.tier == "B"]
    tier_c = [_to_handler_input(c) for c in classified if c.tier == "C"]

    _log("classified", total=len(classified), tier_a=len(tier_a), tier_b=len(tier_b), tier_c=len(tier_c))

    if dry_run:
        return PipelineResult(
            tier_a_results=[{"rule_id": f["rule_id"], "status": "dry_run"} for f in tier_a],
            tier_b_results=[{"rule_id": f["rule_id"], "status": "dry_run"} for f in tier_b],
            tier_c_results=[{"rule_id": f["rule_id"], "status": "dry_run"} for f in tier_c],
            summary={"total": len(classified), "tier_a": len(tier_a), "tier_b": len(tier_b), "tier_c": len(tier_c)},
        )

    a_results: list[dict[str, Any]] = []
    b_results: list[dict[str, Any]] = []
    c_results: list[dict[str, Any]] = []

    if tier_a and mechanic_rules_path:
        _dispatch_tier_a(tier_a, mechanic_rules_path, a_results)

    if tier_b and context_path and templates_dir and llm_client:
        _dispatch_tier_b(tier_b, context_path, templates_dir, llm_client, b_results)

    if tier_c and adr_directory:
        _dispatch_tier_c(tier_c, adr_directory, c_results)

    summary = {
        "total": len(classified),
        "tier_a": len(tier_a), "tier_a_processed": len(a_results),
        "tier_b": len(tier_b), "tier_b_processed": len(b_results),
        "tier_c": len(tier_c), "tier_c_processed": len(c_results),
    }
    _log("done", **summary)

    return PipelineResult(
        tier_a_results=a_results,
        tier_b_results=b_results,
        tier_c_results=c_results,
        summary=summary,
    )


def _dispatch_tier_a(
    findings: list[dict], rules_path: Union[str, Path], results: list[dict[str, Any]]
) -> None:
    """Dispatch Tier A findings to auto_fix_mechanic."""
    from dataclasses import asdict

    from sigma.auto_fix_mechanic.orchestrator import process_findings

    patch_results = process_findings(findings, str(rules_path))
    results.extend(asdict(r) for r in patch_results)


def _dispatch_tier_b(
    findings: list[dict],
    context_path: Union[str, Path],
    templates_dir: Union[str, Path],
    llm_client: Any,
    results: list[dict[str, Any]],
) -> None:
    """Dispatch Tier B findings to correction_agent_bounded."""
    from dataclasses import asdict

    from sigma.correction_agent_bounded.orchestrator import process_findings

    correction_results = process_findings(findings, context_path, templates_dir, llm_client)
    results.extend(asdict(r) for r in correction_results)


def _dispatch_tier_c(
    findings: list[dict], adr_directory: Union[str, Path], results: list[dict[str, Any]]
) -> None:
    """Dispatch Tier C findings to correction_adr_draft."""
    from dataclasses import asdict

    from sigma.correction_adr_draft.drafter import draft_all

    draft_results = draft_all(findings, adr_directory)
    results.extend(asdict(r) for r in draft_results)
