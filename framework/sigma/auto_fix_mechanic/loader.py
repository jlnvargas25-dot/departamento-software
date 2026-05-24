"""Loader del rules.yaml — S-1 foundation.

Carga + valida `auto-fix-mechanic-rules.yaml` y construye un dict
`{rule_id: Handler}` listo para consumo del orquestador.

Politica ante YAML invalido (PRD C9, AC-S1-3): raise `InvalidRulesYamlError`
con mensaje claro indicando que campo falta y en que handler. NO silencia.
"""

from pathlib import Path
from typing import Union

import yaml

from sigma.auto_fix_mechanic.models import Handler


class InvalidRulesYamlError(Exception):
    """YAML de rules malformado o incompleto."""


REQUIRED_TOP_LEVEL_FIELDS = ("version", "handlers", "defaults", "preflight")


def load_handlers(yaml_path: Union[str, Path]) -> dict[str, Handler]:
    """Carga `rules.yaml` y retorna `{rule_id: Handler}`.

    Lanza `InvalidRulesYamlError` si:
    - El archivo no existe (con `FileNotFoundError` envuelto).
    - El YAML es sintacticamente invalido (yaml.YAMLError envuelto).
    - El root no es mapping.
    - Faltan campos top-level requeridos: version, handlers, defaults, preflight.
    - Algun handler no tiene `tool`.
    - Algun handler no tiene `invocation` ni `codemod_script`.
    """
    path = Path(yaml_path)
    raw_bytes = _read_bytes(path)
    raw_text = _decode_utf8(raw_bytes, path)
    data = _parse_yaml(raw_text, path)
    _validate_top_level_shape(data, path)
    handlers_section = data["handlers"]
    if not isinstance(handlers_section, dict):
        raise InvalidRulesYamlError(
            f"{path}: 'handlers' debe ser mapping; encontrado {type(handlers_section).__name__}"
        )

    handlers: dict[str, Handler] = {}
    for rule_id, raw_entry in handlers_section.items():
        handlers[rule_id] = _build_handler(rule_id, raw_entry, path)
    return handlers


# ---------------------------------------------------------------------------
# Helpers privados
# ---------------------------------------------------------------------------


def _read_bytes(path: Path) -> bytes:
    try:
        return path.read_bytes()
    except FileNotFoundError as exc:
        raise InvalidRulesYamlError(f"{path}: archivo no encontrado") from exc


def _decode_utf8(raw_bytes: bytes, path: Path) -> str:
    try:
        return raw_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise InvalidRulesYamlError(
            f"{path}: bytes no son UTF-8 validos (byte={exc.start})"
        ) from exc


def _parse_yaml(text: str, path: Path) -> object:
    if not text.strip():
        raise InvalidRulesYamlError(f"{path}: YAML vacio")
    try:
        return yaml.safe_load(text)
    except yaml.YAMLError as exc:
        raise InvalidRulesYamlError(f"{path}: YAML sintacticamente invalido — {exc}") from exc


def _validate_top_level_shape(data: object, path: Path) -> None:
    if not isinstance(data, dict):
        raise InvalidRulesYamlError(
            f"{path}: root debe ser mapping; encontrado {type(data).__name__}"
        )
    missing = [f for f in REQUIRED_TOP_LEVEL_FIELDS if f not in data]
    if missing:
        raise InvalidRulesYamlError(
            f"{path}: faltan campos top-level requeridos: {', '.join(missing)}"
        )


def _build_handler(rule_id: str, raw_entry: object, path: Path) -> Handler:
    if not isinstance(raw_entry, dict):
        raise InvalidRulesYamlError(
            f"{path}: handler '{rule_id}' debe ser mapping; "
            f"encontrado {type(raw_entry).__name__}"
        )
    tool = raw_entry.get("tool")
    if not tool:
        raise InvalidRulesYamlError(
            f"{path}: handler '{rule_id}' no tiene campo 'tool'"
        )
    invocation = raw_entry.get("invocation")
    codemod_script = raw_entry.get("codemod_script")
    if not invocation and not codemod_script:
        raise InvalidRulesYamlError(
            f"{path}: handler '{rule_id}' debe tener 'invocation' o 'codemod_script'"
        )
    return Handler(
        rule_id=rule_id,
        tool=tool,
        invocation=invocation,
        codemod_script=codemod_script,
        pattern_target=raw_entry.get("pattern_target", ""),
        transformation=raw_entry.get("transformation", ""),
        verification=raw_entry.get("verification") or {},
        rollback_strategy=raw_entry.get("rollback_strategy", "file-level-revert"),
        notes=raw_entry.get("notes"),
    )
