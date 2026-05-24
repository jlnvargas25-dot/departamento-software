"""CLI stdin/stdout JSON interface para correction-adr-draft."""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from typing import TextIO

from sigma.correction_adr_draft.drafter import draft_all

_REQUIRED_KEYS = {"rule_id", "file", "line"}


def _validate_findings(findings: list) -> list[str]:
    """Validate each finding dict has required keys and types."""
    errors: list[str] = []
    for i, f in enumerate(findings):
        if not isinstance(f, dict):
            errors.append(f"findings[{i}]: expected dict")
            continue
        missing = _REQUIRED_KEYS - f.keys()
        if missing:
            errors.append(f"findings[{i}]: missing {sorted(missing)}")
        elif not isinstance(f.get("line"), int):
            errors.append(f"findings[{i}]: line must be int")
    return errors


def main(
    argv: list[str] | None = None,
    stdin: TextIO | None = None,
    stdout: TextIO | None = None,
    stderr: TextIO | None = None,
) -> int:
    """CLI entry point for the Tier C ADR draft generator.

    Args:
        argv: Command-line arguments.
        stdin: Input stream with ClassifiedFinding[] JSON (tier=C).
        stdout: Output stream for DraftResult[] JSON.
        stderr: Error/log stream.

    Returns:
        0 always (Tier C findings are documented, never "fail").
    """
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    parser = argparse.ArgumentParser(
        prog="sigma-adr-draft",
        description="Tier C — generate ADR drafts for findings requiring human decision",
    )
    parser.add_argument(
        "--adr-directory", default="decisions/",
        help="Directory for generated ADR files",
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
        print(json.dumps({"component": "correction-adr-draft", "error": f"invalid_json: {e}"}), file=stderr)
        return 0

    if not isinstance(findings, list):
        print(json.dumps({"component": "correction-adr-draft", "error": "expected_json_array"}), file=stderr)
        return 0

    validation_errors = _validate_findings(findings)
    if validation_errors:
        for err in validation_errors:
            print(json.dumps({"component": "correction-adr-draft", "error": err}), file=stderr)
        return 0

    results = draft_all(findings, args.adr_directory)

    json.dump([asdict(r) for r in results], stdout, indent=2)
    stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
