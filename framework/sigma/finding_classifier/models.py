"""Data models for sigma:finding-classifier (ADR-011 Phase 2)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Tier = Literal["A", "B", "C"]


class SchemaError(ValueError):
    """Raised when sigma-classifier-rules.yaml is malformed or invalid."""


@dataclass(frozen=True)
class Finding:
    rule_id: str
    file: str
    line: int
    severity: str
    message: str
    source: str
    raw: dict | None = None


@dataclass(frozen=True)
class ClassifiedFinding:
    finding: Finding
    tier: Tier
    action_hint: str | None
    matched_rule: bool


@dataclass(frozen=True)
class RuleConfig:
    tier: Tier
    source: str
    severity: str
    action_hint: str | None = None
    description: str | None = None


@dataclass(frozen=True)
class Defaults:
    unknown_rule_tier: Tier
    unknown_rule_action_hint: str


@dataclass(frozen=True)
class ClassifierRules:
    version: str
    rules: dict[str, RuleConfig] = field(default_factory=dict)
    defaults: Defaults = field(
        default_factory=lambda: Defaults(
            unknown_rule_tier="C",
            unknown_rule_action_hint="unknown-rule-log-for-calibration",
        )
    )
