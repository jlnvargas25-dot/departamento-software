"""CLI entry point for sigma:finding_classifier (S-4).

Reads findings from stdin or --input file, writes ClassifiedFinding[] to stdout,
emits unknown_rule calibration log to stderr (S-3 integration). Exit codes:

  0 — success (clasificacion completa, incluso si array vacio)
  1 — error fatal (parse, schema, IO, validacion)

Default streams (sys.stdin/stdout/stderr) inyectables via kwargs para tests.
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import IO

from sigma.finding_classifier.classifier import classify, emit_calibration_log
from sigma.finding_classifier.loader import load_rules
from sigma.finding_classifier.models import (
    ClassifiedFinding,
    Finding,
    SchemaError,
)

_DEFAULT_RULES_PATH = Path(__file__).resolve().parent / "rules.yaml"

_REQUIRED_FINDING_FIELDS: tuple[str, ...] = (
    "rule_id",
    "file",
    "line",
    "severity",
    "message",
    "source",
)


def main(
    argv: list[str] | None = None,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    stderr: IO[str] | None = None,
) -> int:
    """CLI entry point. Returns exit code (0 ok, 1 error)."""
    if stdin is None:
        stdin = sys.stdin
    if stdout is None:
        stdout = sys.stdout
    if stderr is None:
        stderr = sys.stderr

    args = _parse_args(argv)

    try:
        rules = load_rules(args.rules)
    except SchemaError as exc:
        stderr.write(f"schema error: {exc}\n")
        return 1
    except FileNotFoundError as exc:
        stderr.write(f"rules file not found: {exc.filename}\n")
        return 1

    raw = _read_input(args.input, stdin)
    if raw is None:
        stderr.write(f"input file not found: {args.input}\n")
        return 1
    if not raw.strip():
        stderr.write("no findings provided\n")
        return 1

    try:
        findings_data = json.loads(raw)
    except json.JSONDecodeError as exc:
        stderr.write(
            f"invalid JSON: {exc.msg} at line {exc.lineno} col {exc.colno}\n"
        )
        return 1

    if not isinstance(findings_data, list):
        stderr.write(
            f"findings input must be a JSON array (list), "
            f"got {type(findings_data).__name__}\n"
        )
        return 1

    try:
        findings = [_finding_from_dict(item, idx) for idx, item in enumerate(findings_data)]
    except SchemaError as exc:
        stderr.write(f"finding schema error: {exc}\n")
        return 1

    classified = classify(findings, rules)
    emit_calibration_log(findings, rules, stream=stderr)

    if args.audit:
        _emit_audit_summary(classified, stream=stderr)

    stdout.write(json.dumps([_classified_to_dict(c) for c in classified], ensure_ascii=False))
    stdout.write("\n")
    return 0


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        prog="sigma-classify",
        description="Determines tier (A/B/C) for findings from stdin or --input.",
    )
    parser.add_argument(
        "--input",
        type=Path,
        default=None,
        help="Path to JSON file with findings (default: read from stdin).",
    )
    parser.add_argument(
        "--rules",
        type=Path,
        default=_DEFAULT_RULES_PATH,
        help="Path to sigma-classifier-rules.yaml (default: packaged rules.yaml).",
    )
    parser.add_argument(
        "--audit",
        action="store_true",
        default=False,
        help="Emit tier->count summary + unknown_rules count to stderr.",
    )
    return parser.parse_args(argv)


def _read_input(input_path: Path | None, stdin: IO[str]) -> str | None:
    if input_path is None:
        return stdin.read()
    try:
        return input_path.read_text(encoding="utf-8-sig")
    except FileNotFoundError:
        return None


def _finding_from_dict(item: object, idx: int) -> Finding:
    if not isinstance(item, dict):
        raise SchemaError(
            f"finding[{idx}] must be an object, got {type(item).__name__}"
        )
    missing = [k for k in _REQUIRED_FINDING_FIELDS if k not in item]
    if missing:
        raise SchemaError(
            f"finding[{idx}] missing required fields: {', '.join(missing)}"
        )
    return Finding(
        rule_id=str(item["rule_id"]),
        file=str(item["file"]),
        line=int(item["line"]),
        severity=str(item["severity"]),
        message=str(item["message"]),
        source=str(item["source"]),
        raw=item.get("raw") if isinstance(item.get("raw"), dict) else None,
    )


def _emit_audit_summary(
    classified: list[ClassifiedFinding],
    stream: IO[str],
) -> None:
    """Emit tier->count summary + unknown_rules count to stderr (S-5)."""
    counts = {"A": 0, "B": 0, "C": 0}
    unknown = 0
    for c in classified:
        counts[c.tier] += 1
        if not c.matched_rule:
            unknown += 1
    stream.write(f"tier_A: {counts['A']}\n")
    stream.write(f"tier_B: {counts['B']}\n")
    stream.write(f"tier_C: {counts['C']}\n")
    stream.write(f"unknown_rules: {unknown}\n")


def _classified_to_dict(c: ClassifiedFinding) -> dict:
    return {
        "finding": asdict(c.finding),
        "tier": c.tier,
        "action_hint": c.action_hint,
        "matched_rule": c.matched_rule,
    }


if __name__ == "__main__":
    sys.exit(main())
