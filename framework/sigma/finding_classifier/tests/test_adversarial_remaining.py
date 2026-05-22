"""Adversariales restantes del Paso 8 del PROTOCOLO-CONSTRUCCION-CODIGO.

Cubre:
- test_output_json_schema_valid: stdout valida contra jsonschema formal.
- test_classifier_does_not_mutate_filesystem: classify() es funcion pura sin IO.
"""

from __future__ import annotations

import builtins
import io
import json
from pathlib import Path

import jsonschema
import pytest

from sigma.finding_classifier.cli import main
from sigma.finding_classifier.classifier import classify
from sigma.finding_classifier.loader import load_rules
from sigma.finding_classifier.models import Finding

RULES_PATH = (
    Path(__file__).resolve().parent.parent / "rules.yaml"
)


CLASSIFIED_FINDING_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "required": ["finding", "tier", "action_hint", "matched_rule"],
        "additionalProperties": False,
        "properties": {
            "finding": {
                "type": "object",
                "required": [
                    "rule_id",
                    "file",
                    "line",
                    "severity",
                    "message",
                    "source",
                ],
                "properties": {
                    "rule_id": {"type": "string"},
                    "file": {"type": "string"},
                    "line": {"type": "integer"},
                    "severity": {"type": "string"},
                    "message": {"type": "string"},
                    "source": {"type": "string"},
                    "raw": {"type": ["object", "null"]},
                },
            },
            "tier": {"enum": ["A", "B", "C"]},
            "action_hint": {"type": ["string", "null"]},
            "matched_rule": {"type": "boolean"},
        },
    },
}


def _finding_dict(rule_id: str) -> dict:
    return {
        "rule_id": rule_id,
        "file": "x.ts",
        "line": 1,
        "severity": "ALTA",
        "message": "test",
        "source": "adv",
    }


def _run(argv, stdin_text=""):
    stdin = io.StringIO(stdin_text)
    stdout = io.StringIO()
    stderr = io.StringIO()
    code = main(argv, stdin=stdin, stdout=stdout, stderr=stderr)
    return code, stdout.getvalue(), stderr.getvalue()


def test_output_json_schema_valid_for_known_and_unknown_mix():
    """stdout debe validar contra ClassifiedFinding[] schema formal (jsonschema draft-07)."""
    payload = json.dumps([
        _finding_dict("TS-1"),
        _finding_dict("A21-OBS-2-SILENT-CATCH"),
        _finding_dict("UNKNOWN-RULE-XYZ"),
    ])
    code, out, _ = _run([], stdin_text=payload)
    assert code == 0
    parsed = json.loads(out)
    jsonschema.validate(instance=parsed, schema=CLASSIFIED_FINDING_SCHEMA)


def test_output_json_schema_valid_for_empty_array():
    """Array vacio debe ser ClassifiedFinding[] valido (lista vacia es lista)."""
    code, out, _ = _run([], stdin_text="[]")
    assert code == 0
    parsed = json.loads(out)
    jsonschema.validate(instance=parsed, schema=CLASSIFIED_FINDING_SCHEMA)


def test_output_json_schema_rejects_invalid_tier_injection():
    """Sanity check: si por algun bug stdout tuviera tier='Z', jsonschema lo cazaria."""
    bad = [{"finding": _finding_dict("X"), "tier": "Z", "action_hint": None, "matched_rule": False}]
    with pytest.raises(jsonschema.ValidationError):
        jsonschema.validate(instance=bad, schema=CLASSIFIED_FINDING_SCHEMA)


def test_classifier_does_not_mutate_filesystem(monkeypatch, tmp_path):
    """C4: classify() puro — cero open(write), cero mkdir, cero Path.write_*.

    Property: dado cualquier batch de findings, classify() solo lee de los
    objetos en memoria pasados como argumentos. Ninguna invocacion debe
    abrir archivos en modos de escritura, ni crear directorios, ni mutar
    el filesystem de ninguna forma.
    """
    write_calls: list[tuple] = []
    real_open = builtins.open

    def tracking_open(file, mode="r", *args, **kwargs):
        if any(c in mode for c in ("w", "a", "x", "+")):
            write_calls.append((str(file), mode))
        return real_open(file, mode, *args, **kwargs)

    mkdir_calls: list[str] = []
    real_mkdir = Path.mkdir

    def tracking_mkdir(self, *args, **kwargs):
        mkdir_calls.append(str(self))
        return real_mkdir(self, *args, **kwargs)

    write_text_calls: list[str] = []
    real_write_text = Path.write_text

    def tracking_write_text(self, *args, **kwargs):
        write_text_calls.append(str(self))
        return real_write_text(self, *args, **kwargs)

    write_bytes_calls: list[str] = []
    real_write_bytes = Path.write_bytes

    def tracking_write_bytes(self, *args, **kwargs):
        write_bytes_calls.append(str(self))
        return real_write_bytes(self, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", tracking_open)
    monkeypatch.setattr(Path, "mkdir", tracking_mkdir)
    monkeypatch.setattr(Path, "write_text", tracking_write_text)
    monkeypatch.setattr(Path, "write_bytes", tracking_write_bytes)

    # Ejecutar classify() con findings variados (known + unknown).
    rules = load_rules(RULES_PATH)
    findings = [
        Finding("TS-1", "x.ts", 1, "ALTA", "m", "GGA"),
        Finding("UNKNOWN-A", "y.ts", 2, "ALTA", "m", "GGA"),
        Finding("A21-OBS-2-SILENT-CATCH", "z.ts", 3, "ALTA", "m", "GGA"),
    ]
    classify(findings, rules)

    assert write_calls == [], (
        f"classify() abrio archivos en modo escritura: {write_calls}"
    )
    assert mkdir_calls == [], (
        f"classify() creo directorios: {mkdir_calls}"
    )
    assert write_text_calls == [], (
        f"classify() llamo Path.write_text: {write_text_calls}"
    )
    assert write_bytes_calls == [], (
        f"classify() llamo Path.write_bytes: {write_bytes_calls}"
    )


def test_cli_does_not_mutate_filesystem_with_stdin_input(monkeypatch):
    """C4 a nivel CLI: invocacion con stdin (sin --input) no escribe filesystem.

    Permite lectura de rules.yaml (necesaria), pero ningun write.
    """
    write_calls: list[tuple] = []
    real_open = builtins.open

    def tracking_open(file, mode="r", *args, **kwargs):
        if any(c in mode for c in ("w", "a", "x", "+")):
            write_calls.append((str(file), mode))
        return real_open(file, mode, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", tracking_open)

    payload = json.dumps([_finding_dict("TS-1")])
    code, out, err = _run([], stdin_text=payload)
    assert code == 0
    assert write_calls == [], (
        f"CLI con stdin escribio filesystem: {write_calls}"
    )
