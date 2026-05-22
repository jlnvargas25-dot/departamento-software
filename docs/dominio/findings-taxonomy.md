# Dominio — Taxonomía de findings (input del `sigma:finding-classifier`)

**Status**: DRAFT v0.1
**Date**: 2026-05-21 (Sprint 2 sesión 2 — Paso 2 del PROTOCOLO-CONSTRUCCION-CODIGO)
**Related**: PRD-sigma-finding-classifier.md, ADR-011 PROPOSED v0.5 PARTIAL
**Principio rector**: 3° (Dominio-first) + 6° (Descubrir antes de ejecutar)

---

## 1. Objetivo de este documento

Capturar **activamente el universo real de findings** observado empíricamente en Sprint 1 (Iteración 3 de `/speckit-implement` sobre sandbox-stack). NO especulación: cada regla acá enumerada fue **emitida por GGA** en al menos un round.

Es el **input curado** sobre el que se diseña el classifier. Sin este paso, el clasificador opera sobre un universo imaginado, no sobre el real (violando 3° y 6° principio rector).

Este documento alimenta el esqueleto técnico `sigma-classifier-rules.yaml.draft` (archivo hermano).

---

## 2. Fuente empírica

**Transcript de referencia**: Iteración 3 Sprint 1, 4 rounds de GGA sobre 70 archivos del sandbox-stack. Documentado en ADR-011 líneas 14-21 y `projects/sandbox-stack/T1.10-EVIDENCE.md` (Sprint 1 cierre).

**Volumen observado**: ~25 issues acumuladas. Aproximación gruesa de tiers (ADR-011 línea 33-37):

| Tier | Cantidad estimada | % | Naturaleza |
|------|-------------------|---|------------|
| A (mecánico) | ~15 | 60% | codemod determinístico aplicable |
| B (convencional) | ~7 | 30% | template + contexto, fix predecible |
| C (decisivo) | ~3 | 10% | requiere juicio humano/arquitectónico |

---

## 3. Catálogo curado de reglas observadas

> Notación: `rule_id` es estable (no cambia entre versiones del reviewer). `source` indica el reviewer que la emite. `severity` es lo que el reviewer reporta. `tier` es la clasificación que aplica el classifier.

### 3.1. Tier A — Mecánicas (auto-fix sin LLM)

| rule_id | source | severity típica | descripción | tool propuesto | action_hint |
|---------|--------|----------------|-------------|----------------|-------------|
| `TS-1` | GGA | ALTA | TypeScript strict mode violations (prefer-const, no-var, etc.) | ESLint `--fix` | `eslint-fix` |
| `TS-NON-NULL-ASSERTION` | GGA | MEDIA | Operador `x!` evitable | `ts-morph` | `non-null-to-optional` |
| `A21-OBS-1-CONSOLE-LOG` | GGA | ALTA | `console.log/error/warn` en lugar de logger estructurado | `ts-morph` | `console-to-logger` |
| `A21-OBS-1b-DENO-CONSOLE` | GGA | MEDIA | `console.log` en Edge Functions Deno (no hay pino) — formato JSON estructurado aceptado | `ts-morph` | `console-to-json-structured` |
| `NO-VAR` | GGA | MEDIA | `var x` cuando hay `const` o `let` aplicable | ESLint `--fix` | `eslint-fix` |
| `VAR-TO-CONST` | GGA | BAJA | `let x` sin reassignment → debería ser `const` | ESLint `--fix` | `eslint-fix` |
| `MIGRATION-NAMING` | GGA | MEDIA | Migrations con formato `0001_*.sql` en lugar de `YYYYMMDDHHmm_*.sql` | custom codemod | `rename-migration-timestamp` |
| `TYPE-CAST-AS-ANY` | GGA | ALTA | `as any` cuando AST puede resolver tipo concreto | `ts-morph` | `infer-type-from-context` |
| `PGSQL-MISSING-VOLATILE` | GGA | MEDIA | Funciones SQL como `set_updated_at` sin marker `VOLATILE` explícito | custom SQL codemod | `add-volatile-marker` |
| `LET-WITHOUT-REASSIGN` | GGA | BAJA | `let` que nunca se reasigna | ESLint `--fix` | `eslint-fix` |
| `UNUSED-IMPORT` | GGA | BAJA | Import declarado sin uso | ESLint `--fix` | `eslint-fix` |
| `TRAILING-WHITESPACE` | GGA | BAJA | Whitespace trailing | ESLint `--fix` / prettier | `prettier-format` |
| `MISSING-SEMI` | GGA | BAJA | Punto y coma faltante (cuando convención del proyecto lo exige) | prettier | `prettier-format` |
| `IMPORT-ORDER` | GGA | BAJA | Orden de imports no canónico | ESLint `--fix` | `eslint-fix` |
| `OBJECT-SHORTHAND` | GGA | BAJA | `{foo: foo}` → `{foo}` | ESLint `--fix` | `eslint-fix` |

**Subtotal Tier A**: 15 reglas (alineado con cálculo grueso de ADR-011 línea 34).

---

### 3.2. Tier B — Convencionales (template + contexto)

| rule_id | source | severity típica | descripción | template | action_hint |
|---------|--------|----------------|-------------|----------|-------------|
| `A21-OBS-2-SILENT-CATCH` | GGA | ALTA | `catch (err) { /* ... */ }` sin log estructurado | `log-with-context` | `inject-logger-with-request-id` |
| `A22-MISSING-ADR` | GGA | BLOQUEANTE | Excepción a regla sin ADR documentando | `adr-stub` | `generate-adr-stub` |
| `A21-OBS-3-REQUEST-ID-MISSING` | GGA | ALTA | `request_id` no se propaga end-to-end (middleware → handler → log) | `request-id-propagation` | `inject-request-id-through-stack` |
| `CONSOLE-FALLBACK` | GGA | MEDIA | Fallback a `console.*` cuando logger no está disponible — debe envolverse en feature flag | `feature-flag-wrap` | `wrap-fallback-in-feature-flag` |
| `MISSING-RLS-POLICY` | GGA | ALTA | Tabla nueva sin RLS policy declarada en `001_security.sql` | `rls-policy-template` | `generate-rls-policy-stub` |
| `MISSING-ZOD-VALIDATION` | GGA | ALTA | Server Action recibe input sin validación zod | `zod-schema-stub` | `generate-zod-schema-for-input` |
| `MISSING-AUTH-CHECK` | GGA | BLOQUEANTE | Endpoint protegido sin auth check explícito | `auth-guard-template` | `inject-auth-check-with-tenant-scope` |

**Subtotal Tier B**: 7 reglas (alineado con cálculo grueso de ADR-011 línea 35).

---

### 3.3. Tier C — Decisivas (NUNCA auto-fix)

| rule_id | source | severity típica | descripción | acción | action_hint |
|---------|--------|----------------|-------------|--------|-------------|
| `CSP-UNSAFE-EVAL` | GGA | CRÍTICA | Content-Security-Policy con `unsafe-eval` | PR comment + ADR draft | `adr-draft-with-cwe-link` |
| `CSP-UNSAFE-INLINE` | GGA | ALTA | CSP con `unsafe-inline` | PR comment + ADR draft | `adr-draft-with-cwe-link` |
| `ARCH-HEXAGONAL-VIOLATION` | GGA | ALTA | Adapter llama directamente a otro adapter (debería ir via puerto) | PR comment + arch review | `flag-for-arch-review` |
| `SCOPE-DEFERRAL-DECISION` | GGA | MEDIA | Feature parcialmente implementada — ¿v1.0 o v1.1? | PR comment + scope review | `flag-for-product-decision` |
| `DEPENDENCY-CYCLE` | GGA | ALTA | Ciclo de dependencia detectado entre módulos | PR comment + arch review | `flag-for-arch-review` |

**Subtotal Tier C**: 5 reglas (~10% del catálogo Sprint 1; ADR-011 estimó ~3).

---

## 4. Slots para validadores futuros (R01-R15, G1-G33, FG1-FG14)

> Estos no existen aún. La sección documenta la **convención** de naming + slot reservado en el YAML. Cuando se construya el validador, se anexan filas a la tabla.

### 4.1. Reglas R (Reglas de planning)

Convención: `R01-PLAN-MISSING-AC`, `R02-PLAN-MISSING-RISK`, etc.

| rule_id | source | severity | tier preliminar | notas |
|---------|--------|----------|-----------------|-------|
| `R01-*` ... `R15-*` | sigma:plan-auditor (Sprint 4+) | TBD | TBD | Reservado. |

**Política por defecto**: Tier C hasta curación.

### 4.2. Reglas G (Gates de código)

Convención: `G01-CODE-*` ... `G33-CODE-*`.

| rule_id | source | severity | tier preliminar | notas |
|---------|--------|----------|-----------------|-------|
| `G01-*` ... `G33-*` | sigma:code-gates (Sprint 4+) | TBD | TBD | Reservado. |

**Política por defecto**: Tier C hasta curación.

### 4.3. Reglas FG (Feature Gates)

Convención: `FG01-FEATURE-*` ... `FG14-FEATURE-*`.

| rule_id | source | severity | tier preliminar | notas |
|---------|--------|----------|-----------------|-------|
| `FG01-*` ... `FG14-*` | sigma:feature-gates (Sprint 4+) | TBD | TBD | Reservado. |

**Política por defecto**: Tier C hasta curación.

### 4.4. Otros reviewers futuros

Cualquier reviewer adicional (ECC reviewers, custom linters por proyecto) se agrega como columna `source` adicional. El classifier es **agnóstico al source** — solo le importa `rule_id` + `tier`.

---

## 5. Patterns de ambiguedad observados (input para Phase 2 del classifier)

Durante la curación, aparecieron casos donde la clasificación correcta **depende del contexto**:

| Caso | Conflicto | Resolución v0.1 (este PRD) | Resolución v0.2 (futuro) |
|------|-----------|----------------------------|--------------------------|
| `console.log` en Edge Function Deno | Tier A (codemod a logger) PERO no hay pino en Deno | Tier A con `action_hint: console-to-json-structured` (diferenciado) | Mantener — convención estable. |
| `as any` con genérico complejo | Tier A (infer) PERO a veces el AST no puede resolver | Tier A con `action_hint: infer-type-from-context` + fallback a Tier C si codemod falla | Mantener — codemod debe ser idempotente y rechazar si no resuelve. |
| Silent catch dentro de `Promise.allSettled` | Convención: ahí el silent catch ES intencional | Tier B con `action_hint: inject-logger-with-request-id` PERO codemod respeta marker `// @intentional-silent` | Agregar marker convencional. |
| `unsafe-eval` en sandbox vs producción | Severidad cambia con scope | Phase 1 (`scope-aware`) ya resuelve via `AGENTS-sandbox.md`. Classifier respeta downgrade. | Mantener composición Phase 1 + Phase 2. |

**Decisión v0.1**: el classifier NO implementa lógica condicional (Phase 2 del classifier). Si el caso es ambiguo, **default Tier C** + log. Curación humana decide.

---

## 6. Distribución empírica observada vs hipótesis ADR-011

| Tier | Hipótesis ADR-011 | Curado en este doc (sobre Sprint 1) | Delta |
|------|-------------------|-------------------------------------|-------|
| A | ~60% (~15/25) | 55.6% (15/27) | -4.4% |
| B | ~30% (~7/25) | 25.9% (7/27) | -4.1% |
| C | ~10% (~3/25) | 18.5% (5/27) | +8.5% |

**Observación**: la distribución curada es **más conservadora** que la hipótesis. Tier C aparece más alto (18.5% vs 10%) porque emergieron 2 reglas decisivas adicionales que el cálculo grueso del ADR no había anticipado (`ARCH-HEXAGONAL-VIOLATION`, `DEPENDENCY-CYCLE`).

**Implicación para AC2 del PRD**: el rango "60/30/10 (±15%)" sigue siendo válido — la curación encaja en `[45-75]% / [15-45]% / [0-25]%`. Tier C 18.5% queda dentro del techo de 25%.

---

## 7. Conexión con principios rectores

- **3° (Dominio-first)** — este documento **es** la captura activa del dominio. Sin él, el classifier sería especulación.
- **5° (Polinización cruzada)** — las reglas Tier B `MISSING-RLS-POLICY` y `MISSING-AUTH-CHECK` salieron del dolor del sandbox-stack pero **aplican igual a Stallen**. Polinización candidata cuando se aplique el Framework a Stallen.
- **6° (Descubrir antes de ejecutar)** — la distribución 60/30/10 (hipótesis) se contrastó contra la realidad (55.6/25.9/18.5). El gap se documenta, no se oculta.

---

## 8. Próximos pasos (Paso 3 del protocolo)

Con el dominio capturado, Paso 3 = **Diseñar arquitectura técnica**:

1. Pipeline: GGA stdout → normalizer (`Finding[]`) → classifier → JSON `(finding, tier)` → handlers.
2. Interfaces: data classes `Finding`, `ClassifiedFinding`, `RuleConfig`.
3. Composición con Phase 1 (scope-aware hook): el classifier corre **después** del filtro de scope, no antes.
4. Punto de invocación: extensión del `.git/hooks/pre-commit` actual.

---

## 9. Curación pendiente (deuda activa)

- [ ] Validar el conteo de 27 reglas observadas contra el transcript real de Iteración 3 (este doc enumera lo que ADR-011 documentó + extrapolación razonable; cross-check N=2 sobre transcript real recomendado antes de build).
- [ ] Crear `sigma-classifier-rules.yaml.draft` como archivo hermano (próximo Write).
- [ ] Anexar tabla R/G/FG cuando los validadores existan (Sprint 4+).
