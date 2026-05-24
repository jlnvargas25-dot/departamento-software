# Arquitectura tecnica — `sigma:correction-agent-bounded`

**Status**: DRAFT v0.1
**Date**: 2026-05-24 (Sprint 4 sesion 1 — Paso 3 del PROTOCOLO-CONSTRUCCION-CODIGO)
**Related**: PRD-sigma-correction-agent-bounded.md, correction-templates-catalog.md, ADR-011 ACCEPTED v1.0, ARQUITECTURA-sigma-auto-fix-mechanic.md (patron reutilizable)
**Principios rectores**: 1 (Python verifica), 2 (3 capas — correctiva), 4 (Auto-fix > finding), A20 (Hexagonal)

---

## 1. Vision general

El correction-agent es un **orquestador Python que delega generacion de patches a un LLM acotado** para findings clasificados como Tier B. A diferencia del mechanic (Tier A, 100% deterministico), este componente usa un LLM para generar el patch, pero lo acota con un contrato estricto: template predefinido + project_context declarativo + verificacion post-fix deterministica.

```
             ┌──────────────────────────────────────────────────┐
             │      sigma:finding_classifier (v0.1.0)            │
             │      ClassifiedFinding[] con tier + action_hint   │
             └─────────────────────┬────────────────────────────┘
                                   │
                    filter by tier == "B"
                                   │
                                   ▼
             ┌──────────────────────────────────────────────────┐
             │   sigma:correction_agent_bounded (ESTE DOC)       │
             │                                                   │
             │   Por cada Finding Tier B:                        │
             │   1. Lookup template por action_hint              │
             │   2. Load project_context.yaml                    │
             │   3. Read file snippet (line ± context window)    │
             │   4. Snapshot file pre-fix (FileSnapshot reuse)   │
             │   5. Build prompt: template + context + snippet   │
             │   6. LLM call → patch (diff o replacement)        │
             │   7. Apply patch al archivo                       │
             │   8. Verify post-fix (regex/grep deterministic)   │
             │   9. Si verify FAIL → rollback + escalate Tier C  │
             │  10. Si verify OK → mark applied                  │
             │                                                   │
             │   Output JSON: CorrectionResult[]                 │
             └─────────────────────┬────────────────────────────┘
                                   │
                        CorrectionResult[] (stdout)
                                   ▼
             ┌──────────────────────────────────────────────────┐
             │     Downstream: Tier C handler / human review     │
             │     Recibe escalaciones de Tier B fallidos        │
             └──────────────────────────────────────────────────┘
```

---

## 2. Decisiones arquitectonicas

### Decision 1 — LLM como generador de patch acotado (NO como reviewer)

**Elegida**: el LLM recibe un prompt estructurado (template + context + snippet) y retorna SOLO el bloque de codigo de reemplazo. No recibe el archivo completo. No "revisa" el fix — la verificacion es deterministica.

**Rechazada — LLM como reviewer del propio fix**: viola C2 del PRD ("NUNCA preguntar al LLM si esta bien su propio fix"). Permite que el LLM confirme su propia alucinacion.

**Rechazada — LLM recibe archivo completo**: infla tokens (~2000 → ~10000) sin beneficio. El snippet contextual (line ± 20 lines) es suficiente para los 7 templates v0.1.

**Rechazada — Agent framework (LangChain, CrewAI, etc.)**: agrega dependencia pesada para un ciclo simple de prompt → patch → verify. Python stdlib + `anthropic` SDK es suficiente. Alineado con C6 del PRD.

### Decision 2 — Reutilizar `FileSnapshot` del mechanic

**Elegida**: importar `FileSnapshot` de `sigma.auto_fix_mechanic.snapshot` para rollback atomico. Misma mecanica probada con 194 tests.

**Rechazada — snapshot propio**: duplicacion de codigo. `FileSnapshot` ya maneja threading.Lock, backup/restore, y cleanup.

### Decision 3 — Templates como archivos estaticos (no en DB ni en runtime)

**Elegida**: cada template es un archivo `.yaml` en `templates/correction/` con estructura: `prompt_template`, `verification_pattern`, `opt_out_marker`.

**Rechazada — templates en DB/runtime**: no versionable via git, viola C5 (declarativo, versionable, no mutable runtime).

### Decision 4 — Verificacion por regex/grep (no por AST)

**Elegida**: verificacion post-fix usa regex patterns (definidos en el template). Rapido, simple, suficiente para los 7 patrones v0.1.

**Rechazada — AST verification**: overhead de parsear el archivo con ts-morph/libcst post-fix. Los patrones Tier B son mas estructurales (ej. "hay un logger.warn en el catch") que sintacticos. Regex es adecuado.

**Nota**: si futuros templates requieren AST verification, el dispatch de verificacion puede extenderse sin romper la interfaz.

### Decision 5 — Provider abstraction minima

**Elegida**: wrapper minimo sobre `anthropic` SDK que expone `generate_patch(prompt: str) -> str`. v0.1 hardcodea Claude. Provider-swap (OpenAI, Ollama, etc.) es un cambio de 1 funcion.

**Rechazada — provider framework (litellm, etc.)**: dependencia extra para un solo call type. El wrapper minimo es ~20 LOC.

---

## 3. Modulos

```
framework/sigma/correction_agent_bounded/
├── __init__.py              # public API
├── models.py                # CorrectionResult, TemplateConfig, ProjectContext
├── template_loader.py       # carga templates desde templates/correction/
├── context_loader.py        # carga project_context.yaml
├── prompt_builder.py        # ensambla prompt: template + context + snippet
├── llm_client.py            # wrapper minimo sobre anthropic SDK
├── patcher.py               # aplica patch al archivo (string replacement)
├── verifier.py              # regex verification post-fix
├── orchestrator.py          # loop principal: load → prompt → patch → verify
├── cli.py                   # stdin/stdout JSON interface
├── templates/
│   └── correction/
│       ├── inject-logger-with-request-id.yaml
│       ├── generate-adr-stub.yaml
│       ├── inject-request-id-through-stack.yaml
│       ├── wrap-fallback-in-feature-flag.yaml
│       ├── generate-rls-policy-stub.yaml
│       ├── generate-zod-schema-for-input.yaml
│       └── inject-auth-check-with-tenant-scope.yaml
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_template_loader.py
    ├── test_context_loader.py
    ├── test_prompt_builder.py
    ├── test_llm_client.py        # mock LLM responses
    ├── test_patcher.py
    ├── test_verifier.py
    ├── test_orchestrator.py
    ├── test_cli.py
    ├── test_idempotency.py
    ├── test_escalation.py
    └── fixtures/
        ├── project_context.yaml   # test context
        └── target_files/          # archivos con patrones Tier B
```

---

## 4. Modelos de datos

### CorrectionResult

```python
@dataclass
class CorrectionResult:
    rule_id: str
    file: str
    line: int
    action_hint: str
    status: Literal["applied", "no_op", "escalated_to_c"]
    escalation_reason: str | None  # solo si status == escalated_to_c
    patch_summary: str             # descripcion corta del cambio
    tokens_used: int               # tokens consumidos en LLM call
    latency_ms: int                # tiempo total del fix
```

### TemplateConfig

```python
@dataclass
class TemplateConfig:
    action_hint: str
    prompt_template: str           # template con {{placeholders}}
    verification_pattern: str      # regex para verificar post-fix
    opt_out_marker: str | None     # marker que hace skip (ej. @intentional-silent)
    creates_file: bool             # True para generate-adr-stub
    target_file_override: str | None  # si el fix va a otro archivo (ej. RLS migration)
```

### ProjectContext

```python
@dataclass
class ProjectContext:
    logger: str
    logger_import: str
    request_id_source: str
    auth_library: str
    tenant_scope_field: str
    rls_migration_file: str
    zod_import: str
    feature_flag_config: str
    adr_directory: str
```

---

## 5. Flujo detallado por finding

```
Input: ClassifiedFinding(rule_id="A21-OBS-2-SILENT-CATCH", file="client.ts", line=42, ...)

1. template = template_loader.load("inject-logger-with-request-id")
2. context = context_loader.load("project_context.yaml")
3. snippet = read_lines(file, line-20, line+20)

4. IF template.opt_out_marker AND opt_out_marker in snippet:
     RETURN CorrectionResult(status="no_op", reason="opt-out marker found")

5. snapshot = FileSnapshot.capture(file)  # reuse from mechanic

6. prompt = prompt_builder.build(template, context, snippet, finding)
   # prompt ~1500 tokens: template instructions + context values + code snippet

7. patch_text = llm_client.generate_patch(prompt)
   # LLM returns ONLY the replacement code block

8. patcher.apply(file, line_range, patch_text)

9. IF verifier.check(file, template.verification_pattern):
     RETURN CorrectionResult(status="applied", patch_summary=...)
   ELSE:
     snapshot.restore(file)
     RETURN CorrectionResult(status="escalated_to_c",
            escalation_reason="verification failed: pattern not found post-fix")
```

---

## 6. Prompt structure (constraint: <2000 tokens)

```
You are a code patch generator. Generate ONLY the replacement code block.
Do NOT explain. Do NOT add comments beyond what the template requires.

## Template
{template.prompt_template with placeholders resolved}

## Project Context
- Logger: {context.logger} (import: {context.logger_import})
- Request ID: {context.request_id_source}
- Auth: {context.auth_library}

## Current Code (line {line} ± context)
```{language}
{snippet}
```

## Task
Replace the code at line {line} to fix: {finding.description}
Return ONLY the replacement code block, no explanation.
```

---

## 7. Interaccion con otros componentes

| Componente | Relacion | Detalle |
|------------|----------|---------|
| `finding_classifier` | upstream | provee `ClassifiedFinding` con `tier: B` |
| `auto_fix_mechanic` | peer (reuse) | importa `FileSnapshot` para rollback |
| `correction_adr_draft` (Tier C) | downstream | recibe escalaciones cuando verification falla |
| `project_context.yaml` | config | declarativo por proyecto, leido al inicio |
| `anthropic` SDK | dependency | unico provider v0.1 |

---

## 8. Extensibilidad

- **Nuevo template**: agregar `.yaml` en `templates/correction/` + entry en `rules.yaml` con `action_hint` correspondiente. No requiere cambio de codigo.
- **Nuevo provider LLM**: cambiar `llm_client.py` (~20 LOC). Interface `generate_patch(prompt) -> str` se preserva.
- **Verificacion AST**: agregar metodo al `verifier.py` dispatch. Template declara `verification_type: ast` vs `regex`.

---

## 9. Adversarial categories (Paso 8)

| Cat | Scenario | Expectativa |
|-----|----------|-------------|
| 1 | LLM retorna texto vacio | escalate Tier C, rollback |
| 2 | LLM retorna codigo con syntax error | patcher aplica pero verifier falla → rollback |
| 3 | LLM retorna fix correcto pero para linea equivocada | verifier falla (pattern not at target line) → rollback |
| 4 | Template no encontrado para action_hint | escalate Tier C con reason "template not found" |
| 5 | project_context.yaml no existe | error explicito al inicio, NO fallback a defaults |
| 6 | Archivo target read-only | escalate Tier C con reason "file not writable" |
| 7 | opt-out marker presente | NO-OP, log skip reason |
| 8 | Finding ya fixeado (idempotency) | verifier detecta patron ya presente → NO-OP |
| 9 | LLM timeout (>30s) | escalate Tier C con reason "llm timeout" |
| 10 | Multiples findings en mismo archivo | procesar secuencialmente, snapshot por finding |
| 11 | LLM hallucina import inexistente | verificacion pasa (regex solo chequea patron target), pero import invalido queda — RB4 risk accepted v0.1 |
| 12 | Batch >20 findings | procesar todos, log performance metrics |
