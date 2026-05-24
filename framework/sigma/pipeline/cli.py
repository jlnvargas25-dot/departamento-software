"""CLI for the sigma pipeline — classify + dispatch in one shot."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import TextIO

from sigma.pipeline.dispatcher import dispatch


def main(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """CLI entry point for the sigma pipeline.

    Args:
        argv: Command-line arguments.
        stdin: Input stream with Finding[] JSON.
        stdout: Output stream for PipelineResult JSON.
        stderr: Error/log stream.

    Returns:
        0 on success, 1 if any Tier A/B escalated, 2 on input error.
    """
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    parser = argparse.ArgumentParser(
        prog="sigma-pipeline",
        description="E2E pipeline: classify findings → dispatch to tier handlers",
    )
    parser.add_argument(
        "--rules", required=True,
        help="Path to classifier rules.yaml",
    )
    parser.add_argument(
        "--mechanic-rules",
        help="Path to mechanic rules.yaml (enables Tier A)",
    )
    parser.add_argument(
        "--context-path",
        help="Path to project_context.yaml (enables Tier B)",
    )
    parser.add_argument(
        "--templates-dir",
        help="Path to correction templates directory (enables Tier B)",
    )
    parser.add_argument(
        "--adr-directory", default="decisions/",
        help="Directory for ADR drafts (Tier C)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Classify only — do not execute handlers",
    )
    args = parser.parse_args(argv)

    raw = stdin.read()
    if not raw.strip():
        json.dump(asdict(dispatch([], args.rules, dry_run=True)), stdout, indent=2)
        stdout.write("\n")
        return 0

    try:
        findings = json.loads(raw)
    except json.JSONDecodeError as e:
        print(json.dumps({"component": "sigma-pipeline", "error": f"invalid_json: {e}"}), file=stderr)
        return 2

    if not isinstance(findings, list):
        print(json.dumps({"component": "sigma-pipeline", "error": "expected_json_array"}), file=stderr)
        return 2

    result = dispatch(
        raw_findings=findings,
        rules_path=args.rules,
        mechanic_rules_path=args.mechanic_rules,
        context_path=args.context_path,
        templates_dir=args.templates_dir,
        adr_directory=args.adr_directory,
        dry_run=args.dry_run,
    )

    json.dump(asdict(result), stdout, indent=2)
    stdout.write("\n")

    has_escalation = any(
        r.get("status") in ("escalated_to_c", "rolled_back")
        for r in result.tier_a_results + result.tier_b_results
    )
    return 1 if has_escalation else 0


if __name__ == "__main__":
    sys.exit(main())
