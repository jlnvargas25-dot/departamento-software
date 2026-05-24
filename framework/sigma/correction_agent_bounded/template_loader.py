"""Carga templates YAML de correccion desde directorio."""

from __future__ import annotations

from pathlib import Path
from typing import Union

import yaml

from sigma.correction_agent_bounded.models import TemplateConfig

_REQUIRED_FIELDS = {"action_hint", "prompt_template", "verification_pattern"}


class TemplateLoadError(ValueError):
    """Template YAML malformado o con campos faltantes."""


def load_template(path: Union[str, Path]) -> TemplateConfig:
    """Load a single correction template YAML. Raises TemplateLoadError on invalid schema."""
    p = Path(path)
    if not p.exists():
        raise FileNotFoundError(f"Template not found: {p}")

    raw = yaml.safe_load(p.read_text(encoding="utf-8"))
    if not isinstance(raw, dict):
        raise TemplateLoadError(f"{p.name}: expected YAML mapping, got {type(raw).__name__}")

    missing = _REQUIRED_FIELDS - raw.keys()
    if missing:
        raise TemplateLoadError(f"{p.name}: missing required fields: {sorted(missing)}")

    return TemplateConfig(
        action_hint=str(raw["action_hint"]),
        prompt_template=str(raw["prompt_template"]),
        verification_pattern=str(raw["verification_pattern"]),
        opt_out_marker=raw.get("opt_out_marker"),
        creates_file=bool(raw.get("creates_file", False)),
        target_file_override=raw.get("target_file_override"),
    )


def load_all_templates(templates_dir: Union[str, Path]) -> dict[str, TemplateConfig]:
    """Load all .yaml templates from a directory, keyed by action_hint."""
    d = Path(templates_dir)
    if not d.is_dir():
        raise FileNotFoundError(f"Templates directory not found: {d}")

    result: dict[str, TemplateConfig] = {}
    for yml in sorted(d.glob("*.yaml")):
        t = load_template(yml)
        result[t.action_hint] = t
    return result
