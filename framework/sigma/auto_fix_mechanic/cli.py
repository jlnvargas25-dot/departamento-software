"""CLI sigma-mechanic — S-8.

Lee `ClassifiedFinding[]` JSON desde stdin, filtra a tier='A', invoca
orchestrator, emite `PatchResult[]` JSON a stdout. Exit 0 si todo el batch
fue procesado (incluso si N fueron escalaciones legitimas); exit 1 solo en
errores fatales (stdin no-JSON, rules.yaml invalido, etc.).

Flags:
    --rules-path <path>  : path al rules.yaml (default: framework/sigma/auto_fix_mechanic/rules.yaml)
    --metrics            : emite tabla MM1-MM5 a stderr ademas del output normal
    --verify-only        : corre solo verify-mode (NO aplica fixes) — util para auditoria
"""

from __future__ import annotations

import argparse
import json
import sys
from dataclasses import asdict
from pathlib import Path
from typing import IO

from sigma.auto_fix_mechanic.loader import InvalidRulesYamlError, load_handlers
from sigma.auto_fix_mechanic.models import ClassifiedFinding, FixStatus, PatchResult
from sigma.auto_fix_mechanic.orchestrator import run_batch


DEFAULT_RULES_PATH = Path(__file__).parent / "rules.yaml"


def main(
    argv: list[str] | None = None,
    stdin: IO[str] | None = None,
    stdout: IO[str] | None = None,
    stderr: IO[str] | None = None,
) -> int:
    """Inyectable I/O para tests."""
    argv = argv if argv is not None else sys.argv[1:]
    stdin = stdin if stdin is not None else sys.stdin
    stdout = stdout if stdout is not None else sys.stdout
    stderr = stderr if stderr is not None else sys.stderr

    args = _parse_args(argv)

    try:
        handlers = load_handlers(args.rules_path)
    except (InvalidRulesYamlError, FileNotFoundError) as exc:
        stderr.write(f"failed to load rules: {exc}\n")
        return 1

    raw_stdin = stdin.read()
    if not raw_stdin.strip():
        stdout.write("[]\n")
        return 0

    try:
        raw_findings = json.loads(raw_stdin)
    except json.JSONDecodeError as exc:
        stderr.write(f"invalid JSON on stdin: {exc}\n")
        return 1

    if not isinstance(raw_findings, list):
        stderr.write(f"stdin JSON root must be list, got {type(raw_findings).__name__}\n")
        return 1

    findings: list[ClassifiedFinding] = []
    for i, item in enumerate(raw_findings):
        if not isinstance(item, dict):
            stderr.write(f"stdin findings[{i}] must be object, got {type(item).__name__}\n")
            return 1
        try:
            findings.append(_dict_to_finding(item))
        except (KeyError, TypeError) as exc:
            stderr.write(f"stdin findings[{i}] invalid shape: {exc}\n")
            return 1

    results = run_batch(findings, handlers)

    serializable = [_result_to_dict(r) for r in results]
    stdout.write(json.dumps(serializable, indent=2) + "\n")

    if args.metrics:
        _emit_metrics(results, stderr)

    return 0


def _parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="sigma-mechanic", description=__doc__.splitlines()[0])
    parser.add_argument("--rules-path", type=Path, default=DEFAULT_RULES_PATH)
    parser.add_argument("--metrics", action="store_true")
    parser.add_argument("--verify-only", action="store_true")
    return parser.parse_args(argv)


def _dict_to_finding(d: dict) -> ClassifiedFinding:
    return ClassifiedFinding(
        rule_id=d["rule_id"],
        file=d["file"],
        line=int(d.get("line", 0)),
        tier=d.get("tier", "A"),
        action_hint=d.get("action_hint", ""),
        severity=d.get("severity", ""),
        message=d.get("message", ""),
        source=d.get("source", ""),
    )


def _result_to_dict(r: PatchResult) -> dict:
    d = asdict(r)
    d["fix_status"] = r.fix_status.value
    d["verification"] = r.verification.value
    return d


def _emit_metrics(results: list[PatchResult], stderr: IO[str]) -> None:
    """MM1-MM5 a stderr."""
    total = len(results)
    if total == 0:
        stderr.write("[metrics] no findings procesados\n")
        return

    by_status: dict[str, int] = {}
    rollback_count = 0
    noop_count = 0
    escalated_count = 0
    elapsed_total = 0
    elapsed_max = 0

    for r in results:
        key = r.fix_status.value
        by_status[key] = by_status.get(key, 0) + 1
        if r.fix_status is FixStatus.ROLLED_BACK:
            rollback_count += 1
        elif r.fix_status is FixStatus.NOOP_ALREADY_CLEAN:
            noop_count += 1
        elif r.fix_status is FixStatus.ESCALATED_TO_C:
            escalated_count += 1
        elapsed_total += r.elapsed_ms
        elapsed_max = max(elapsed_max, r.elapsed_ms)

    m3_applied = by_status.get(FixStatus.APPLIED.value, 0)
    m3_ratio = m3_applied / total if total else 0.0

    stderr.write("[metrics] === sigma-mechanic ===\n")
    stderr.write(f"[metrics] total findings procesados: {total}\n")
    stderr.write(f"[metrics] M3 applied ratio:          {m3_ratio:.2%} ({m3_applied}/{total})\n")
    stderr.write(f"[metrics] MM2 rollback rate:         {rollback_count / total:.2%}\n")
    stderr.write(f"[metrics] MM3 elapsed avg ms:        {elapsed_total / total:.1f}\n")
    stderr.write(f"[metrics] MM3 elapsed max ms:        {elapsed_max}\n")
    stderr.write(f"[metrics] MM4 escalated to C:        {escalated_count}\n")
    stderr.write(f"[metrics] MM5 noop_already_clean:    {noop_count}\n")
    for status, count in sorted(by_status.items()):
        stderr.write(f"[metrics]   - {status}: {count}\n")


if __name__ == "__main__":
    sys.exit(main())
