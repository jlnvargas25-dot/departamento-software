# PRD — `sigma:correction-agent-bounded`

**Status**: DRAFT v0.1
**Date**: 2026-05-24 (Sprint 4 sesion 1)
**Owner**: Departamento de Software
**Related**: ADR-011 ACCEPTED v1.0 (Phase 2 — Trinidad Correctiva, Tier B handler)
**Upstream**: `sigma:finding_classifier` v0.1.0 (73 tests), `sigma:auto_fix_mechanic` v0.1.0 (194 tests)
**Protocolo**: Paso 1 (Capturar intencion) del PROTOCOLO-CONSTRUCCION-CODIGO

---

## 1. Contexto

ADR-011 ACCEPTED v1.0 valido empiricamente la trinidad correctiva para Tier A (mecanico, sin LLM). El classifier clasifica findings y el mechanic aplica codemods deterministicos. Para Tier A, el ciclo esta cerrado.

Tier B es el **tercer componente de Phase 2**. A diferencia de Tier A (100% deterministico), Tier B requiere un sub-agente LLM **acotado** que aplica fixes predecibles pero que necesitan contexto del proyecto (ej. cual es el logger, donde esta el request_id, cual es la convencion de RLS). El LLM NO decide que fixear — el classifier ya decidio. El LLM solo genera el patch siguiendo un template + contexto.

La diferencia critica con dejar que el LLM "adivine" el fix (lo que GGA hacia en Sprint 1) es el **contrato estricto**: scope de 1 archivo, 1 fix, template predefinido, verificacion post-fix deterministica, rollback si falla. Esto acota el espacio de error del LLM a un rectangulo medible.

---

## 2. Problema que resuelve

**Hoy**: findings clasificados como `tier: B` (7 reglas: silent catches, missing ADR, request_id, console fallback, RLS, zod, auth check) requieren intervencion manual del operador. Cada fix toma 5-15 minutos porque necesita entender el contexto del archivo + aplicar un patron de la convencion del proyecto.

**Tras este PRD**: el correction-agent genera patches siguiendo templates + contexto declarado en `project_context.yaml`. Un verificador deterministico confirma que el patch aplico el patron esperado (ej. "ahora hay un `logger.warn` en el catch block"). Si no, rollback + escalacion a Tier C.

**Beneficio cuantificable**: M4 ADR-011 (Tier B debe cerrar >=70% de findings B con un solo patch). 7 findings B observados en Sprint 1 * 10 min promedio = ~70 min. Con agent-bounded: <5 min automatico + review humano del patch.

---

## 3. Intencion (one-liner)

> "Generar patches para findings Tier B usando templates + contexto del proyecto via LLM acotado, verificar el patch con AST/grep deterministico, y entregar diff atomico revisable — o rollback + escalacion a Tier C si la verificacion falla."

---

## 4. Scope

### In scope (este PRD)

- **Universo de findings**: los **7 rule_ids Tier B** de `rules.yaml` v0.1.0:
  - A21-OBS-2-SILENT-CATCH, A22-MISSING-ADR, A21-OBS-3-REQUEST-ID-MISSING, CONSOLE-FALLBACK, MISSING-RLS-POLICY, MISSING-ZOD-VALIDATION, MISSING-AUTH-CHECK.
- **Input estructurado por finding**:
  ```json
  {
    "rule_id": "A21-OBS-2-SILENT-CATCH",
    "file": "src/adapters/supabase/client.ts",
    "line": 42,
    "context_snippet": "catch (err) { }",
    "action_hint": "inject-logger-with-request-id"
  }
  ```
- **Project context declarativo** (`project_context.yaml`):
  ```yaml
  logger: pino
  logger_import: "@/lib/logger"
  request_id_source: middleware.request_id
  auth_library: supabase
  tenant_scope_field: organization_id
  rls_migration_file: supabase/migrations/001_security.sql
  zod_import: zod
  feature_flag_config: config.yaml
  adr_directory: decisions/
  ```
- **Templates por action_hint**: cada template define el patron de fix + placeholders a llenar con context. El LLM recibe template + context + snippet del archivo = genera patch acotado.
- **Scope minimo**: 1 archivo, 1 fix por invocacion. Multiples findings se procesan secuencialmente.
- **Verificacion post-fix deterministica**: re-check con regex/AST que el patron target fue aplicado (ej. "catch block ahora contiene logger.warn"). Si no, rollback + Tier C.
- **Rollback atomico**: si verificacion falla, revertir archivo a estado pre-patch. Reusar `FileSnapshot` del mechanic.
- **Escalacion a Tier C**: si LLM no puede generar patch valido o verificacion falla, el finding se re-clasifica como Tier C con motivo.
- **CLI invocable**: input JSON `ClassifiedFinding[]` (tier=B del classifier), output JSON `PatchResult[]` + exit code.

### Out of scope (este PRD)

- **Tier A**: ya operativo en `auto-fix-mechanic`.
- **Tier C**: PRD separado (`correction-adr-draft`).
- **Integracion E2E**: PRD separado (GGA -> classifier -> handler dispatch).
- **Seleccion del provider LLM**: v0.1 usa Claude via API directa. Provider-swap diferido.
- **Multi-file fixes**: v0.1 scope 1 archivo. Cross-file (ej. request_id propagation e2e) es v0.2.
- **Aprendizaje de templates nuevos**: v0.1 templates son estaticos. Template evolution es v0.2.

---

## 5. Acceptance criteria

### Funcionales

- **AB1**: dado un finding `tier: B` con `action_hint` conocido, el agent genera un patch que aplica el patron del template al archivo target.
- **AB2**: la verificacion post-patch confirma que el patron fue aplicado (ej. `logger.warn` presente en el catch block).
- **AB3**: si verificacion falla, rollback automatico + finding re-clasificado como Tier C con motivo.
- **AB4**: `project_context.yaml` es la unica fuente de contexto del proyecto — el LLM NO busca contexto adicional.
- **AB5**: idempotencia — aplicar el agent 2 veces sobre el mismo finding = segundo run detecta que el patron ya fue aplicado y retorna NO-OP.
- **AB6**: el marker `// @intentional-silent` en un catch block hace que `A21-OBS-2-SILENT-CATCH` retorne NO-OP (respeta intencion del developer).
- **AB7**: CLI recibe JSON por stdin, emite JSON por stdout, exit 0 si todos los patches aplicaron o NO-OP, exit 1 si alguno escalo a Tier C.

### No funcionales

- **AB8**: latencia por finding < 30s (incluye LLM call + verificacion).
- **AB9**: el prompt al LLM no excede 2000 tokens (template + context + snippet). Prompts mas largos son señal de scope creep.
- **AB10**: logs estructurados a stderr con formato `[correction-agent] event=<x> rule_id=<y> file=<z> status=<s>`.

---

## 6. Constraints (no negociables)

- **C1**: el LLM genera el PATCH, no la DECISION. La decision ya fue tomada por el classifier (tier=B). El LLM es ejecutor acotado.
- **C2**: verificacion post-fix siempre deterministica (regex/AST). NUNCA preguntar al LLM "esta bien tu propio fix?".
- **C3**: scope 1 archivo, 1 fix. NO batch multi-file por invocacion.
- **C4**: rollback atomico obligatorio si verificacion falla. Usar `FileSnapshot` del mechanic.
- **C5**: project_context.yaml es declarativo, versionable, NO mutable en runtime.
- **C6**: sin dependencias nuevas fuera de stdlib Python + `anthropic` SDK (o provider-neutral wrapper). No instalar frameworks de agents.
- **C7**: template library es estatica v0.1. Cada template es un archivo `.md` o `.yaml` en `templates/correction/`.

---

## 7. Templates (7 action_hints)

| action_hint | Template | Verificacion post-fix |
|-------------|----------|----------------------|
| `inject-logger-with-request-id` | Inject `logger.{level}({context}, msg)` en catch block vacio | regex: `logger\.(warn\|error)` dentro del catch block del line target |
| `generate-adr-stub` | Crear `decisions/ADR-{next}-{slug}.md` con header + sections + related ADRs | file exists + contiene `## Decision` + `## Alternatives` |
| `inject-request-id-through-stack` | Agregar `requestId` param/header pass-through en handler | grep: `request.?id` en el archivo target (v0.1 single-file) |
| `wrap-fallback-in-feature-flag` | Envolver `console.*` fallback en `if (config.enableConsoleFallback)` | regex: `if.*config.*console` pattern presente |
| `generate-rls-policy-stub` | Agregar policy SQL en migration file referenciado en context | grep: `CREATE POLICY.*ON.*{table}` en el archivo RLS |
| `generate-zod-schema-for-input` | Crear schema `z.object({...})` + `.parse(input)` en el Server Action | grep: `z\.object` + `\.parse` en el archivo target |
| `inject-auth-check-with-tenant-scope` | Agregar auth guard con tenant scope check al inicio del handler | grep: `getUser\|getSession` + `organization_id` en el archivo |

---

## 8. Metricas

- **M4 (ADR-011)**: >=70% de findings B cerrados con un solo patch (no requiere multiples iteraciones).
- **MM1**: latencia promedio por fix (target: <30s).
- **MM2**: tasa de escalacion a Tier C (target: <30% — si >30%, los templates necesitan calibracion).
- **MM3**: ratio de rollback (target: <10% — alto rollback indica templates fragiles).
- **MM4**: tokens consumidos por fix (target: <3000 tokens totales por invocacion).

---

## 9. Riesgos

- **RB1**: LLM genera patch que pasa verificacion pero introduce bug sutil (ej. logger importado pero nunca llamado correctamente). Mitigacion: verificacion post-fix especifica por template, no generica.
- **RB2**: `project_context.yaml` desactualizado respecto al proyecto real (ej. logger cambio de pino a winston). Mitigacion: validar que imports del context existen en el proyecto antes de generar patch.
- **RB3**: templates demasiado rigidos para variantes del patron (ej. Express vs Hono auth check). Mitigacion: v0.1 cubre solo la convencion principal del proyecto; variantes se escalan a Tier C.
- **RB4**: LLM hallucina imports o APIs que no existen. Mitigacion: C2 (verificacion deterministica) + rollback si import no resuelve.

---

## 10. Dependencias

- `sigma:finding_classifier` v0.1.0 — provee `ClassifiedFinding` con `tier: B` + `action_hint`.
- `sigma:auto_fix_mechanic` — reusar `FileSnapshot` para rollback atomico.
- `anthropic` SDK (o wrapper) — para LLM call. v0.1 asume Claude como provider.
- `project_context.yaml` — creado por el operador por proyecto. Template minimo provisto.
