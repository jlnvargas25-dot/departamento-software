"""Deterministic classifier — etiqueta findings con tier (A/B/C) segun rules YAML."""

from __future__ import annotations

import json
import sys
from typing import IO

from sigma.finding_classifier.models import (
    ClassifiedFinding,
    ClassifierRules,
    Finding,
)


def classify(
    findings: list[Finding],
    rules: ClassifierRules,
) -> list[ClassifiedFinding]:
    """Asigna tier a cada finding. Mismo input -> mismo output (MC2 estabilidad).

    Funcion pura: no escribe a stderr ni filesystem. Reglas no presentes en
    `rules.rules` reciben `rules.defaults.unknown_rule_tier` y `matched_rule=False`.
    El CLI invoca `emit_calibration_log` despues de classify para reportar
    rule_ids desconocidos (separacion de responsabilidades).
    """
    out: list[ClassifiedFinding] = []

    for f in findings:
        rule = rules.rules.get(f.rule_id)
        if rule is not None:
            out.append(
                ClassifiedFinding(
                    finding=f,
                    tier=rule.tier,
                    action_hint=rule.action_hint,
                    matched_rule=True,
                )
            )
        else:
            out.append(
                ClassifiedFinding(
                    finding=f,
                    tier=rules.defaults.unknown_rule_tier,
                    action_hint=rules.defaults.unknown_rule_action_hint or None,
                    matched_rule=False,
                )
            )

    return out


def unknown_rule_ids(
    findings: list[Finding],
    rules: ClassifierRules,
) -> set[str]:
    """Set de rule_ids que NO matchearon — input para emit_calibration_log."""
    return {f.rule_id for f in findings if f.rule_id not in rules.rules}


def emit_calibration_log(
    findings: list[Finding],
    rules: ClassifierRules,
    stream: IO[str] | None = None,
) -> int:
    """Emite a stderr una linea JSON por rule_id desconocido (dedup por rule_id).

    Cada linea incluye `count` (frecuencia del rule_id en el batch) y
    `first_file`/`first_line` (referencia para curacion humana al editar el YAML).

    Retorna la cantidad de rule_ids unicos emitidos (0 si no hay unknowns).
    `stream` default es `sys.stderr` — inyectable para tests.

    No-op silencioso si no hay unknowns (no emite nada, no contamina stderr).
    """
    if stream is None:
        stream = sys.stderr

    aggregated: dict[str, dict[str, object]] = {}
    for f in findings:
        if f.rule_id in rules.rules:
            continue
        entry = aggregated.get(f.rule_id)
        if entry is None:
            aggregated[f.rule_id] = {
                "event": "unknown_rule",
                "rule_id": f.rule_id,
                "count": 1,
                "first_file": f.file,
                "first_line": f.line,
            }
        else:
            entry["count"] = int(entry["count"]) + 1  # type: ignore[arg-type]

    for entry in aggregated.values():
        stream.write(json.dumps(entry, ensure_ascii=False, sort_keys=True))
        stream.write("\n")

    return len(aggregated)
