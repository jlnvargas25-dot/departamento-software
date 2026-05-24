# Stories — `sigma:correction-agent-bounded`

**Status**: DRAFT v0.1
**Date**: 2026-05-24 (Sprint 4 sesion 1 — Paso 4 del PROTOCOLO-CONSTRUCCION-CODIGO)
**Related**: PRD, ARQUITECTURA, correction-templates-catalog.md
**Estimacion total**: ~12hs en 2 sesiones

---

## DAG de dependencias

```
S-1 (models + template_loader + context_loader)
 │
 ├── S-2 (prompt_builder)
 │    │
 │    └── S-3 (llm_client + patcher)
 │         │
 │         └── S-4 (verifier + escalation)
 │              │
 │              └── S-5 (orchestrator)
 │                   │
 │                   └── S-6 (CLI + metrics)
 │
 └── S-7 (7 templates YAML)
```

S-7 (templates) puede ejecutarse en paralelo con S-2..S-6 (no tiene dependencia de codigo). Pero el testing de S-5+ necesita los templates.

---

## Stories

### S-1 — Foundation: models + template_loader + context_loader (~2hs)

**Que**: package Python `framework/sigma/correction_agent_bounded/` con models, template loader y context loader.

**DoD**:
- `models.py` con `CorrectionResult`, `TemplateConfig`, `ProjectContext` dataclasses
- `template_loader.py` carga `.yaml` de `templates/correction/`, valida schema
- `context_loader.py` carga `project_context.yaml`, valida campos requeridos
- Fixture: `project_context.yaml` de test + 1 template de test
- Tests: ~12 (models validation + loader happy/error paths)

**AC**:
- Template con campo faltante → `ValueError` con mensaje claro
- Context con campo faltante → `ValueError` con campo especifico
- Template cargado tiene todos los campos de `TemplateConfig`

---

### S-2 — Prompt builder (~1.5hs)

**Que**: ensambla prompt a partir de template + context + file snippet.

**DoD**:
- `prompt_builder.py` con `build_prompt(template, context, finding, snippet) -> str`
- Resuelve `{{placeholders}}` del template con valores del context
- Valida que prompt resultante <2000 tokens (estimacion por caracteres / 4)
- Tests: ~8 (happy path, placeholder resolution, token limit warning)

**AC**:
- Prompt resultante contiene template instructions + context values + snippet
- Placeholder no resuelto → `ValueError`
- Prompt >2000 tokens estimados → warning log (no error, pero metric tracked)

---

### S-3 — LLM client + patcher (~2hs)

**Que**: wrapper minimo sobre `anthropic` SDK + applicador de patches.

**DoD**:
- `llm_client.py` con `generate_patch(prompt: str, max_tokens: int = 1000) -> str`
  - Wrapper sobre `anthropic.Anthropic().messages.create()`
  - Timeout configurable (default 30s)
  - Retorna solo el content text del response
- `patcher.py` con `apply_patch(file: str, line: int, context_window: int, replacement: str) -> bool`
  - Lee archivo, reemplaza bloque en line range, escribe
  - Retorna True si cambio algo, False si no-op
- Tests: ~10 (mock LLM responses, patcher line replacement, edge cases)

**AC**:
- LLM timeout → raise `TimeoutError` (orchestrator atrapa y escala)
- LLM retorna texto vacio → raise `ValueError`
- Patcher no modifica archivo si replacement == original (idempotency)

**Nota**: tests de `llm_client` usan mock (no LLM real). Tests E2E con LLM real van en S-5.

---

### S-4 — Verifier + escalation logic (~2hs)

**Que**: verificacion post-fix con regex + logica de escalacion a Tier C.

**DoD**:
- `verifier.py` con:
  - `check_pattern(file: str, pattern: str, line_range: tuple) -> bool` — regex search
  - `check_file_exists(path: str) -> bool` — para templates que crean archivos (ADR stub)
  - `check_opt_out(file: str, marker: str, line: int) -> bool` — detecta opt-out markers
- Escalation logic: si verify falla → `CorrectionResult(status="escalated_to_c", reason=...)`
- Reusar `FileSnapshot` del mechanic para rollback
- Tests: ~12 (regex match, no match, opt-out present, rollback after verify fail, file creation verify)

**AC**:
- Pattern match en line range → True
- Pattern no match → False + rollback triggered
- Opt-out marker → NO-OP antes de invocar LLM
- `FileSnapshot` importado de `sigma.auto_fix_mechanic.snapshot` sin duplicacion

---

### S-5 — Orchestrator (~2.5hs)

**Que**: loop principal que procesa findings Tier B secuencialmente.

**DoD**:
- `orchestrator.py` con `process_findings(findings: list[ClassifiedFinding], context_path: str, templates_dir: str) -> list[CorrectionResult]`
- Flujo por finding: load template → check opt-out → snapshot → build prompt → LLM call → apply patch → verify → result
- Manejo de errores: cada finding se procesa independientemente (1 fallo no aborta el batch)
- Metricas agregadas: total_applied, total_no_op, total_escalated, total_tokens, total_latency
- Tests: ~14 (happy path, escalation, opt-out, timeout, idempotency, batch processing, metrics aggregation)

**AC**:
- Finding con template existente → applied o escalated
- Finding con template faltante → escalated con reason "template not found"
- 2da corrida sobre mismos findings → all NO-OP (idempotency)
- Batch de 5 findings: 3 applied + 1 no-op + 1 escalated → exit summary correcto

---

### S-6 — CLI + metrics (~1.5hs)

**Que**: interfaz stdin/stdout JSON + metricas.

**DoD**:
- `cli.py` con:
  - `--context-path` (default: `project_context.yaml`)
  - `--templates-dir` (default: `templates/correction/`)
  - `--dry-run` (build prompts + log, no LLM call)
  - stdin: `ClassifiedFinding[]` JSON
  - stdout: `CorrectionResult[]` JSON
  - exit 0 si todo applied/no-op, exit 1 si alguno escalated
- Metricas a stderr: `[correction-agent] total=N applied=X no_op=Y escalated=Z tokens=T latency=Lms`
- Tests: ~8 (stdin/stdout, exit codes, dry-run, metrics output)

**AC**:
- `echo '[]' | sigma-correct` → exit 0, output `[]`
- `--dry-run` → NO LLM calls, prompts logged to stderr
- Exit 1 si alguno escalo a Tier C

---

### S-7 — 7 templates YAML (~1.5hs)

**Que**: los 7 archivos de template en `templates/correction/`.

**DoD**:
- 7 archivos `.yaml` con: `action_hint`, `prompt_template`, `verification_pattern`, `opt_out_marker`, `creates_file`, `target_file_override`
- Cada template validado contra `TemplateConfig` schema
- Tests: ~7 (1 load test por template)

**AC**:
- Todos los templates cargan sin error
- Cada `action_hint` coincide con los 7 action_hints de `rules.yaml` Tier B
- `verification_pattern` es regex valida (compilable)

---

## Estimacion por sesion

| Sesion | Stories | Estimacion |
|--------|---------|-----------|
| Sprint 4 sesion 2 | S-1 + S-2 + S-3 + S-7 | ~7hs |
| Sprint 4 sesion 3 | S-4 + S-5 + S-6 + audits Paso 7+8 | ~8hs |

**Tests proyectados**: ~71 tests (12 + 8 + 10 + 12 + 14 + 8 + 7)
**LOC produccion estimada**: ~500-700 Python + ~200 YAML templates
**Ratio tests:prod**: ~1.5:1 (consistente con mechanic)
