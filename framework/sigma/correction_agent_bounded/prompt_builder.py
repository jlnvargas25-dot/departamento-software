"""Ensambla prompts a partir de template + context + file snippet."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Union

from sigma.correction_agent_bounded.models import ProjectContext, TemplateConfig

TOKEN_ESTIMATE_DIVISOR = 4
TOKEN_WARN_THRESHOLD = 2000

_PLACEHOLDER_RE = re.compile(r"\{\{(\w+)\}\}")

SYSTEM_HEADER = (
    "You are a code patch generator. Generate ONLY the replacement code block.\n"
    "Do NOT explain. Do NOT add comments beyond what the template requires.\n"
)


class UnresolvedPlaceholderError(ValueError):
    """Template contiene placeholder sin valor en context."""


def _resolve_placeholders(
    template: str, values: dict[str, str], *, strict: bool = False
) -> str:
    def _replace(m: re.Match) -> str:
        key = m.group(1)
        if key in values:
            return values[key]
        if strict:
            raise UnresolvedPlaceholderError(
                f"Unresolved placeholder: {{{{{key}}}}} — not found in context values"
            )
        return f"<{key}>"

    return _PLACEHOLDER_RE.sub(_replace, template)


def read_snippet(
    file_path: Union[str, Path], line: int, window: int = 20
) -> tuple[str, str]:
    """Read lines around `line` from file. Returns (snippet_text, language)."""
    p = Path(file_path)
    lines = p.read_text(encoding="utf-8").splitlines()
    start = max(0, line - 1 - window)
    end = min(len(lines), line + window)
    snippet = "\n".join(lines[start:end])
    suffix = p.suffix.lstrip(".")
    lang = {"ts": "typescript", "tsx": "typescript", "js": "javascript",
            "sql": "sql", "py": "python"}.get(suffix, suffix)
    return snippet, lang


def build_prompt(
    template: TemplateConfig,
    context: ProjectContext,
    file_path: str,
    line: int,
    snippet: str,
    language: str,
    extra_values: dict[str, str] | None = None,
) -> str:
    """Assemble a prompt from template + context + snippet for LLM patch generation."""
    values: dict[str, str] = {
        "logger": context.logger,
        "logger_import": context.logger_import,
        "request_id_source": context.request_id_source,
        "auth_library": context.auth_library,
        "tenant_scope_field": context.tenant_scope_field,
        "rls_migration_file": context.rls_migration_file,
        "zod_import": context.zod_import,
        "feature_flag_config": context.feature_flag_config,
        "adr_directory": context.adr_directory,
        "file": file_path,
        "line": str(line),
    }
    if extra_values:
        values.update(extra_values)

    resolved_template = _resolve_placeholders(template.prompt_template, values)

    prompt = (
        f"{SYSTEM_HEADER}\n"
        f"## Template\n{resolved_template}\n\n"
        f"## Project Context\n"
        f"- Logger: {context.logger} (import: {context.logger_import})\n"
        f"- Request ID: {context.request_id_source}\n"
        f"- Auth: {context.auth_library}\n\n"
        f"## Current Code (line {line} ± context)\n"
        f"```{language}\n{snippet}\n```\n\n"
        f"## Task\n"
        f"Replace the code at line {line} to fix the issue described above.\n"
        f"Return ONLY the replacement code block, no explanation.\n"
    )
    return prompt


def estimate_tokens(text: str) -> int:
    """Rough token count estimate (chars / 4)."""
    return len(text) // TOKEN_ESTIMATE_DIVISOR
