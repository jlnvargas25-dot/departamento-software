"""Dataclasses inmutables del correction-agent-bounded — S-1 foundation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Optional


class CorrectionStatus(str, Enum):
    """Terminal status of a Tier B correction attempt."""

    APPLIED = "applied"
    NO_OP = "no_op"
    ESCALATED_TO_C = "escalated_to_c"


@dataclass(frozen=True)
class TemplateConfig:
    """Correction template loaded from YAML.

    Attributes:
        action_hint: Matches the action_hint field in rules.yaml.
        prompt_template: Template string with {{placeholders}} for the LLM prompt.
        verification_pattern: Regex pattern to verify the fix was applied.
        opt_out_marker: If present in the file near the finding, skip the fix.
        creates_file: True if this template creates a new file (e.g. ADR stub).
        target_file_override: Path for the new file if creates_file is True.
    """

    action_hint: str
    prompt_template: str
    verification_pattern: str
    opt_out_marker: Optional[str] = None
    creates_file: bool = False
    target_file_override: Optional[str] = None


@dataclass(frozen=True)
class ProjectContext:
    """Declarative project context loaded from project_context.yaml.

    Attributes:
        logger: Logger library name (e.g. "pino", "winston").
        logger_import: Import path for the logger (e.g. "@/lib/logger").
        request_id_source: How to access request ID in handlers.
        auth_library: Auth library name (e.g. "supabase", "clerk").
        tenant_scope_field: Field name for tenant isolation.
        rls_migration_file: Path to the RLS migration file.
        zod_import: Import path for zod (default: "zod").
        feature_flag_config: Path to feature flag config file.
        adr_directory: Directory for ADR files.
    """

    logger: str
    logger_import: str
    request_id_source: str
    auth_library: str
    tenant_scope_field: str
    rls_migration_file: str
    zod_import: str = "zod"
    feature_flag_config: str = "config.yaml"
    adr_directory: str = "decisions/"


@dataclass(frozen=True)
class CorrectionResult:
    """Result of processing a single Tier B finding.

    Attributes:
        rule_id: The rule that triggered the finding.
        file: Path to the file that was (or would be) patched.
        line: Line number of the finding.
        action_hint: The action_hint from rules.yaml.
        status: Terminal status (applied, no_op, or escalated_to_c).
        escalation_reason: Why the fix was escalated (only if status is escalated_to_c).
        patch_summary: Short description of the change applied.
        tokens_used: Estimated tokens consumed by the LLM call.
        latency_ms: Total time for this fix in milliseconds.
    """

    rule_id: str
    file: str
    line: int
    action_hint: str
    status: CorrectionStatus
    escalation_reason: Optional[str] = None
    patch_summary: Optional[str] = None
    tokens_used: int = 0
    latency_ms: int = 0
