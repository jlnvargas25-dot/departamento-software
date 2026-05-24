"""Template-based ADR draft generation for Tier C findings."""

from __future__ import annotations

import json
import sys
from datetime import date, timezone, datetime
from pathlib import Path
from typing import Union

from sigma.correction_adr_draft.cwe_links import get_security_links
from sigma.correction_adr_draft.models import DraftResult, DraftStatus
from sigma.correction_adr_draft.numbering import adr_slug, next_adr_number

_KNOWN_HINTS = {"adr-draft-with-cwe-link", "flag-for-arch-review", "flag-for-product-decision"}


def _log(msg: str, **kwargs: object) -> None:
    """Emit JSON-structured log line to stderr."""
    print(json.dumps({"component": "correction-adr-draft", "event": msg, **kwargs}), file=sys.stderr)


def _render_adr(
    number: int,
    rule_id: str,
    file_path: str,
    line: int,
    action_hint: str,
    description: str,
    today: str,
) -> str:
    """Render the ADR markdown from template + finding metadata.

    Args:
        number: ADR sequence number.
        rule_id: Finding rule identifier.
        file_path: Source file where finding was detected.
        line: Line number.
        action_hint: The action_hint from rules.yaml.
        description: Human-readable finding description.
        today: ISO date string.

    Returns:
        Complete ADR markdown content.
    """
    links = get_security_links(rule_id)
    refs_section = ""
    if links:
        refs_lines = ["\n## Security References\n"]
        if "cwe" in links:
            refs_lines.append(f"- CWE: {links['cwe']}")
        if "owasp" in links:
            refs_lines.append(f"- OWASP: {links['owasp']}")
        refs_section = "\n".join(refs_lines) + "\n"

    review_type = {
        "adr-draft-with-cwe-link": "Security policy decision",
        "flag-for-arch-review": "Architecture review",
        "flag-for-product-decision": "Product/scope decision",
    }.get(action_hint, "Review required")

    return (
        f"# ADR-{number:03d}: {rule_id}\n\n"
        f"**Status**: PROPOSED\n"
        f"**Date**: {today}\n"
        f"**Type**: {review_type}\n"
        f"**Related**: {rule_id}\n"
        f"**Source**: `{file_path}:{line}`\n\n"
        f"---\n\n"
        f"## Context\n\n"
        f"{description}\n\n"
        f"Detected at `{file_path}:{line}` by automated classifier (tier: C).\n"
        f"This finding requires human decision — auto-fix is NOT appropriate.\n\n"
        f"## Decision\n\n"
        f"**[PENDING — requires human decision]**\n\n"
        f"## Alternatives\n\n"
        f"- **Option A**: Fix the violation as reported.\n"
        f"- **Option B**: Document as accepted exception with rationale.\n"
        f"- **Option C**: Defer to next version with scope tag.\n\n"
        f"## Consequences\n\n"
        f"[PENDING — fill after decision]\n"
        f"{refs_section}"
    )


def draft_one(
    finding: dict,
    adr_directory: Union[str, Path],
) -> DraftResult:
    """Generate an ADR draft for a single Tier C finding.

    Args:
        finding: Dict with rule_id, file, line, action_hint, and optional message.
        adr_directory: Directory where ADR files are written.

    Returns:
        DraftResult with status and path to generated file.
    """
    rule_id = finding["rule_id"]
    file_path = finding["file"]
    line = finding["line"]
    action_hint = finding.get("action_hint", "")
    description = finding.get("message", f"Finding {rule_id} requires human decision.")

    if action_hint not in _KNOWN_HINTS:
        _log("skipped", rule_id=rule_id, reason="unknown action_hint")
        return DraftResult(
            rule_id=rule_id, file=file_path, line=line,
            action_hint=action_hint, status=DraftStatus.SKIPPED,
            summary=f"unknown action_hint: {action_hint}",
        )

    adr_dir = Path(adr_directory)
    adr_dir.mkdir(parents=True, exist_ok=True)

    slug = adr_slug(rule_id, file_path)
    existing = list(adr_dir.glob(f"ADR-*-{slug}.md"))
    if existing:
        _log("no_op", rule_id=rule_id, reason="ADR already exists")
        return DraftResult(
            rule_id=rule_id, file=file_path, line=line,
            action_hint=action_hint, status=DraftStatus.NO_OP,
            adr_path=str(existing[0]),
            summary="ADR already exists",
        )

    number = next_adr_number(adr_dir)
    filename = f"ADR-{number:03d}-{slug}.md"
    adr_path = adr_dir / filename

    today_utc = datetime.now(timezone.utc).date().isoformat()
    content = _render_adr(number, rule_id, file_path, line, action_hint, description, today_utc)
    adr_path.write_text(content, encoding="utf-8")

    _log("created", rule_id=rule_id, adr=str(adr_path))
    return DraftResult(
        rule_id=rule_id, file=file_path, line=line,
        action_hint=action_hint, status=DraftStatus.CREATED,
        adr_path=str(adr_path),
        summary=f"ADR-{number:03d} draft created",
    )


def draft_all(
    findings: list[dict],
    adr_directory: Union[str, Path],
) -> list[DraftResult]:
    """Process a batch of Tier C findings, generating ADR drafts.

    Args:
        findings: List of finding dicts with rule_id, file, line, action_hint.
        adr_directory: Directory where ADR files are written.

    Returns:
        List of DraftResult with aggregate metrics logged to stderr.
    """
    results = [draft_one(f, adr_directory) for f in findings]

    created = sum(1 for r in results if r.status == DraftStatus.CREATED)
    no_op = sum(1 for r in results if r.status == DraftStatus.NO_OP)
    skipped = sum(1 for r in results if r.status == DraftStatus.SKIPPED)

    _log("summary", total=len(results), created=created, no_op=no_op, skipped=skipped)
    return results
