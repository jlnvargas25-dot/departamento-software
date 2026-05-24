# Dominio — Catalogo de templates de correccion (Tier B)

**Status**: DRAFT v0.1
**Date**: 2026-05-24 (Sprint 4 sesion 1)
**Related**: PRD-sigma-correction-agent-bounded.md, ADR-011 ACCEPTED v1.0
**Principio rector**: 3 (Dominio-first) + 4 (Auto-fix > finding cuando inequivoco)

---

## 1. Objetivo

Capturar el universo de templates de correccion que el `correction-agent-bounded` usa para generar patches. Cada template define:
- **Patron target**: que encontro el classifier (finding).
- **Patron fix**: que debe quedar en el archivo tras el patch.
- **Placeholders**: valores que vienen de `project_context.yaml`.
- **Verificacion**: regex/AST check deterministico post-fix.
- **Marker de opt-out**: si el developer marco intencionalmente el patron, skip.

---

## 2. Fuente empirica

Los 7 `action_hint` de las reglas Tier B en `rules.yaml` v0.1.0, observados en Sprint 1 Iteracion 3 (4 rounds GGA sobre sandbox-stack).

---

## 3. Templates detallados

### T1 — `inject-logger-with-request-id`

**Rule**: `A21-OBS-2-SILENT-CATCH`
**Patron target**: `catch (err) { }` o `catch (err) { /* comment */ }` sin llamada a logger.
**Patron fix**:
```typescript
catch (err) {
  {{logger_import_statement}}
  logger.warn({ err, requestId: {{request_id_source}} }, "{{contextual_message}}");
}
```
**Placeholders**:
- `logger_import_statement`: si `import { logger }` no existe en el archivo, agregar `import { logger } from "{{logger_import}}"`.
- `request_id_source`: de `project_context.yaml` (ej. `req.requestId`).
- `contextual_message`: inferir del contexto (nombre de funcion o endpoint). Ej. `"Error in createTodo"`.
**Verificacion**: regex `logger\.(warn|error)\(` presente dentro del catch block en el line range.
**Opt-out marker**: `// @intentional-silent` — si presente en el catch, retornar NO-OP.

### T2 — `generate-adr-stub`

**Rule**: `A22-MISSING-ADR`
**Patron target**: excepcion a regla documentada sin ADR existente.
**Patron fix**: crear archivo `{{adr_directory}}/ADR-{next_number}-{slug}.md`:
```markdown
# ADR-{next_number}: {title}

**Status**: PROPOSED
**Date**: {today}
**Related**: {related_rule_id}

## Context
{finding_description}

## Decision
[PENDING — requires human decision]

## Alternatives
- Option A: [fix the violation]
- Option B: [document exception with rationale]

## Consequences
[PENDING]
```
**Placeholders**:
- `adr_directory`: de `project_context.yaml` (ej. `decisions/`).
- `next_number`: max(existing ADR numbers) + 1.
- `slug`: kebab-case del `rule_id` + contexto.
**Verificacion**: archivo existe + contiene `## Decision` + `## Alternatives`.
**Opt-out**: no aplica (si hay ADR existente para esta excepcion, el classifier no la reporta).

### T3 — `inject-request-id-through-stack`

**Rule**: `A21-OBS-3-REQUEST-ID-MISSING`
**Patron target**: handler/funcion sin `requestId` en su scope o logs.
**Patron fix**: agregar pass-through de `requestId` desde el middleware context.
```typescript
// Si es handler Express/Hono:
const requestId = req.headers['x-request-id'] || crypto.randomUUID();
// Si es Server Action Next.js:
const requestId = headers().get('x-request-id') || crypto.randomUUID();
```
**Placeholders**:
- `request_id_source`: de `project_context.yaml`.
**Verificacion**: grep `request.?[Ii]d` en el archivo.
**Nota v0.1**: scope 1 archivo. Propagacion cross-file (middleware → handler → adapter) es v0.2.

### T4 — `wrap-fallback-in-feature-flag`

**Rule**: `CONSOLE-FALLBACK`
**Patron target**: `console.*` usado como fallback cuando logger no esta disponible.
**Patron fix**:
```typescript
if (config.enableConsoleFallback) {
  console.warn(msg);
}
```
**Placeholders**:
- `feature_flag_config`: de `project_context.yaml`.
**Verificacion**: regex `if.*config.*console` o `if.*enableConsole` presente.
**Opt-out**: no aplica (si es console intencional, deberia ser `A21-OBS-1` Tier A).

### T5 — `generate-rls-policy-stub`

**Rule**: `MISSING-RLS-POLICY`
**Patron target**: tabla nueva en migration sin `CREATE POLICY` correspondiente.
**Patron fix**: agregar policy stub en `{{rls_migration_file}}`:
```sql
-- RLS policy for {{table_name}} (auto-generated stub, review required)
ALTER TABLE {{table_name}} ENABLE ROW LEVEL SECURITY;

CREATE POLICY "{{table_name}}_select_own"
  ON {{table_name}}
  FOR SELECT
  USING ({{tenant_scope_field}} = auth.jwt() ->> '{{tenant_scope_field}}');

CREATE POLICY "{{table_name}}_insert_own"
  ON {{table_name}}
  FOR INSERT
  WITH CHECK ({{tenant_scope_field}} = auth.jwt() ->> '{{tenant_scope_field}}');
```
**Placeholders**:
- `rls_migration_file`, `tenant_scope_field`: de `project_context.yaml`.
- `table_name`: extraido del finding context.
**Verificacion**: grep `CREATE POLICY.*ON.*{{table_name}}` en el archivo RLS.

### T6 — `generate-zod-schema-for-input`

**Rule**: `MISSING-ZOD-VALIDATION`
**Patron target**: Server Action recibe `formData` o parametros sin `.parse()`.
**Patron fix**:
```typescript
import { z } from "{{zod_import}}";

const inputSchema = z.object({
  // TODO: define fields based on form/API contract
});

const validated = inputSchema.parse(input);
```
**Placeholders**:
- `zod_import`: de `project_context.yaml` (default: `"zod"`).
**Verificacion**: grep `z\.object` + `\.parse` en el archivo target.
**Nota**: el LLM infiere los campos del schema del contexto del Server Action (parametros, formData keys).

### T7 — `inject-auth-check-with-tenant-scope`

**Rule**: `MISSING-AUTH-CHECK`
**Patron target**: endpoint/handler sin verificacion de autenticacion.
**Patron fix**:
```typescript
const { data: { user }, error } = await supabase.auth.getUser();
if (error || !user) {
  throw new Error("Unauthorized");
}
// Tenant scope check
const userOrg = user.user_metadata?.{{tenant_scope_field}};
if (!userOrg) {
  throw new Error("Missing tenant scope");
}
```
**Placeholders**:
- `auth_library`, `tenant_scope_field`: de `project_context.yaml`.
**Verificacion**: grep `getUser|getSession` + `{{tenant_scope_field}}` en el archivo.
**Nota**: template varia segun auth library (Supabase vs Clerk vs custom). v0.1 asume Supabase.

---

## 4. `project_context.yaml` — schema minimo

```yaml
# project_context.yaml — contexto del proyecto para correction-agent-bounded
# Ubicacion: raiz del proyecto target (ej. projects/sandbox-stack/project_context.yaml)

logger: pino                          # nombre del logger library
logger_import: "@/lib/logger"         # import path del logger
request_id_source: req.requestId      # como acceder al request ID en handlers
auth_library: supabase                # supabase | clerk | custom
tenant_scope_field: organization_id   # campo de tenant isolation
rls_migration_file: supabase/migrations/001_security.sql
zod_import: zod                       # import path de zod
feature_flag_config: config.yaml      # archivo de feature flags
adr_directory: decisions/             # directorio de ADRs
```

---

## 5. Distinciones criticas Tier A vs Tier B

| Dimension | Tier A (mechanic) | Tier B (correction-agent) |
|-----------|-------------------|---------------------------|
| Usa LLM | NO | SI (acotado) |
| Input extra | solo finding + file | finding + file + project_context + template |
| Determinismo del fix | 100% (codemod = mismo input → mismo output) | ~90% (LLM puede variar en detalle, pero patron verificado) |
| Verificacion | re-run tool (eslint, prettier, AST) | regex/grep pattern match |
| Riesgo principal | codemod mal escrito | LLM hallucina import/API |
| Rollback trigger | tool verification falla | pattern verification falla |
| Latencia | <2s | <30s (incluye LLM call) |
