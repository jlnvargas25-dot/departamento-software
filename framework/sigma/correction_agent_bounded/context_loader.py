"""Carga project_context.yaml — contexto declarativo del proyecto target."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import yaml

from sigma.correction_agent_bounded.models import ProjectContext

_REQUIRED_FIELDS = {
    "logger", "logger_import", "request_id_source",
    "auth_library", "tenant_scope_field", "rls_migration_file",
}


class ContextLoadError(ValueError):
    """project_context.yaml malformado o con campos faltantes."""


def load_context(path: Union[str, Path]) -> ProjectContext:
    """Load and validate project_context.yaml. Raises ContextLoadError on invalid schema."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Project context not found: {p}")

    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise ContextLoadError(
            f"{p.name}: expected YAML mapping, got {type(raw).__name__}"
        )

    missing = _REQUIRED_FIELDS - raw.keys()
    if missing:
        raise ContextLoadError(
            f"{p.name}: missing required fields: {sorted(missing)}"
        )

    return ProjectContext(
        logger=str(raw["logger"]),
        logger_import=str(raw["logger_import"]),
        request_id_source=str(raw["request_id_source"]),
        auth_library=str(raw["auth_library"]),
        tenant_scope_field=str(raw["tenant_scope_field"]),
        rls_migration_file=str(raw["rls_migration_file"]),
        zod_import=str(raw.get("zod_import", "zod")),
        feature_flag_config=str(raw.get("feature_flag_config", "config.yaml")),
        adr_directory=str(raw.get("adr_directory", "decisions/")),
    )
