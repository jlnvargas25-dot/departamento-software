"""Pre-flight check del toolbox — S-2 (AM9 del PRD).

Verifica disponibilidad de tools externos al arrancar el mechanic.
Required tools faltantes -> fail-fast (mechanic NO arranca).
Optional tools faltantes -> handlers asociados quedan marcados
`optional_tool_unavailable=True` y el orquestador los escala a Tier C.
"""

import shlex
import subprocess
from dataclasses import dataclass, field, replace

from sigma.auto_fix_mechanic.models import Handler, ToolboxStatus


@dataclass(frozen=True)
class ToolSpec:
    """Una entry de `preflight.required_tools[]` o `preflight.optional_tools[]`.

    `required_for_handlers` se ignora para required tools; para optional tools
    enumera los rule_ids que deshabilitar si el tool falta.
    """

    name: str
    check_command: str
    install_hint: str = ""
    required_for_handlers: tuple[str, ...] = field(default_factory=tuple)


def run_preflight_check(
    required: list[ToolSpec],
    optional: list[ToolSpec],
    handlers: dict[str, Handler],
    timeout_s: int = 5,
) -> tuple[ToolboxStatus, dict[str, Handler]]:
    """Verifica required + optional tools y retorna (status, handlers_post_check).

    handlers_post_check es un nuevo dict donde los handlers cuyo optional tool
    falta tienen `optional_tool_unavailable=True` (via `dataclasses.replace`).
    Si nada esta disabled, los Handler son los mismos objetos que el input
    (frozen, sin necesidad de copy defensiva).
    """
    missing_required = [t.name for t in required if not _is_tool_available(t, timeout_s)]
    missing_optional_specs = [t for t in optional if not _is_tool_available(t, timeout_s)]
    missing_optional = [t.name for t in missing_optional_specs]

    disabled_rule_ids: list[str] = []
    handlers_out = dict(handlers)
    for spec in missing_optional_specs:
        for rule_id in spec.required_for_handlers:
            if rule_id in handlers_out:
                handlers_out[rule_id] = replace(
                    handlers_out[rule_id], optional_tool_unavailable=True
                )
                disabled_rule_ids.append(rule_id)

    status = ToolboxStatus(
        required_tools_ok=not missing_required,
        optional_tools_ok=not missing_optional,
        missing_required=missing_required,
        missing_optional=missing_optional,
        disabled_handlers=disabled_rule_ids,
    )
    return status, handlers_out


def _is_tool_available(spec: ToolSpec, timeout_s: int) -> bool:
    """Ejecuta `check_command` con shell=False + timeout corto.

    Retorna True solo si exit_code == 0. Cualquier error (FileNotFoundError,
    timeout, permission denied) -> False sin propagar.
    """
    try:
        args = shlex.split(spec.check_command, posix=True)
    except ValueError:
        return False
    if not args:
        return False
    try:
        result = subprocess.run(
            args,
            capture_output=True,
            timeout=timeout_s,
            shell=False,
        )
        return result.returncode == 0
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError, PermissionError):
        return False
