"""YAML loader and schema validation for sigma-classifier-rules.yaml."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from sigma.finding_classifier.models import (
    ClassifierRules,
    Defaults,
    RuleConfig,
    SchemaError,
    Tier,
)

_VALID_TIERS: tuple[Tier, ...] = ("A", "B", "C")
_REQUIRED_TOP_LEVEL_KEYS: tuple[str, ...] = ("version", "rules", "defaults")


def load_rules(path: Path) -> ClassifierRules:
    """Load and validate sigma-classifier-rules.yaml. Fails fast on schema errors."""
    try:
        with path.open(encoding="utf-8-sig") as fh:
            raw = yaml.safe_load(fh)
    except yaml.YAMLError as exc:
        raise SchemaError(f"YAML parse error in {path}: {exc}") from exc

    if raw is None:
        raise SchemaError(f"YAML is empty: {path}")

    if not isinstance(raw, dict):
        raise SchemaError(
            f"YAML top-level must be a mapping, got {type(raw).__name__}: {path}"
        )

    missing = [k for k in _REQUIRED_TOP_LEVEL_KEYS if k not in raw]
    if missing:
        raise SchemaError(
            f"YAML missing required top-level keys: {', '.join(missing)}"
        )

    rules = _parse_rules(raw["rules"])
    defaults = _parse_defaults(raw["defaults"])

    return ClassifierRules(
        version=str(raw["version"]),
        rules=rules,
        defaults=defaults,
    )


def _parse_rules(rules_raw: Any) -> dict[str, RuleConfig]:
    if not isinstance(rules_raw, dict):
        raise SchemaError(
            f"'rules' must be a mapping, got {type(rules_raw).__name__}"
        )

    out: dict[str, RuleConfig] = {}
    for rule_id, cfg in rules_raw.items():
        if not isinstance(cfg, dict):
            raise SchemaError(
                f"Rule {rule_id!r} config must be a mapping, "
                f"got {type(cfg).__name__}"
            )

        tier = cfg.get("tier")
        if tier not in _VALID_TIERS:
            raise SchemaError(
                f"Rule {rule_id!r} has invalid tier: {tier!r} "
                f"(must be one of {_VALID_TIERS})"
            )

        source = cfg.get("source")
        if not isinstance(source, str) or not source:
            raise SchemaError(f"Rule {rule_id!r} missing or empty 'source'")

        out[str(rule_id)] = RuleConfig(
            tier=tier,
            source=source,
            severity=str(cfg.get("severity", "UNKNOWN")),
            action_hint=cfg.get("action_hint"),
            description=cfg.get("description"),
        )

    return out


def _parse_defaults(defaults_raw: Any) -> Defaults:
    if not isinstance(defaults_raw, dict):
        raise SchemaError(
            f"'defaults' must be a mapping, got {type(defaults_raw).__name__}"
        )

    unknown_tier = defaults_raw.get("unknown_rule_tier")
    if unknown_tier not in _VALID_TIERS:
        raise SchemaError(
            f"defaults.unknown_rule_tier must be one of {_VALID_TIERS}, "
            f"got {unknown_tier!r}"
        )

    return Defaults(
        unknown_rule_tier=unknown_tier,
        unknown_rule_action_hint=str(
            defaults_raw.get("unknown_rule_action_hint", "")
        ),
    )
