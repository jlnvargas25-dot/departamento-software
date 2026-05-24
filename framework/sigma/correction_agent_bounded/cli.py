"""CLI stdin/stdout JSON interface para correction-agent-bounded."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import TextIO

from sigma.correction_agent_bounded.llm_client import AnthropicClient, LLMClient, MockLLMClient
from sigma.correction_agent_bounded.models import CorrectionStatus
from sigma.correction_agent_bounded.orchestrator import process_findings

_DEFAULT_TEMPLATES = str(
    Path(__file__).parent / "templates" / "correction"
)

_REQUIRED_FINDING_KEYS = {"rule_id", "file", "line"}


def _validate_findings(findings: list) -> list[str]:
    """Validate each finding dict has required keys. Returns list of errors."""
    errors: list[str] = []
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"findings[{i}]: expected dict, got {type(f).__name__}")
            continue
        missing = _REQUIRED_FINDING_KEYS - f.keys()
        if missing:
            errors.append(f"findings[{i}]: missing keys {sorted(missing)}")
    return errors


def _log_error(msg: str, stderr: TextIO) -> None:
    """Emit JSON error to stderr (G-6 compliant)."""
    print(json.dumps({"component": "correction-agent", "error": msg}), file=stderr)


def main(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """CLI entry point for the Tier B correction agent.

    Args:
        argv: Command-line arguments (default: sys.argv).
        stdin: Input stream with ClassifiedFinding[] JSON.
        stdout: Output stream for CorrectionResult[] JSON.
        stderr: Error/log stream.

    Returns:
        0 if all findings applied or no-op, 1 if any escalated, 2 on input error.
    """
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    parser = argparse.ArgumentParser(
        prog="sigma-correct",
        description="Tier B correction agent — bounded LLM patch generator",
    )
    parser.add_argument(
        "--context-path", default="project_context.yaml",
        help="Path to project_context.yaml",
    )
    parser.add_argument(
        "--templates-dir", default=_DEFAULT_TEMPLATES,
        help="Path to templates/correction/ directory",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Build prompts and log, but do not call LLM",
    )
    parser.add_argument(
        "--model", default="claude-sonnet-4-20250514",
        help="Model to use for LLM calls",
    )

    args = parser.parse_args(argv)

    raw = stdin.read()
    if not raw.strip():
        json.dump([], stdout)
        stdout.write("\n")
        return 0

    try:
        findings = json.loads(raw)
    except json.JSONDecodeError as e:
        _log_error(f"invalid_json: {e}", stderr)
        return 2

    if not isinstance(findings, list):
        _log_error("expected_json_array", stderr)
        return 2

    validation_errors = _validate_findings(findings)
    if validation_errors:
        for err in validation_errors:
            _log_error(err, stderr)
        return 2

    client: LLMClient
    if args.dry_run:
        client = MockLLMClient(default="<dry-run: no LLM call>")
    else:
        client = AnthropicClient(model=args.model)

    results = process_findings(findings, args.context_path, args.templates_dir, client)

    json.dump([asdict(r) for r in results], stdout, indent=2)
    stdout.write("\n")

    has_escalation = any(r.status == CorrectionStatus.ESCALATED_TO_C for r in results)
    return 1 if has_escalation else 0


if __name__ == "__main__":
    sys.exit(main())
