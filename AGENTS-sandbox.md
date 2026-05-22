# AGENTS-sandbox.md — Reglas de Código (SCOPE: SANDBOX)

**Versión**: 1.0 (2026-05-21, Phase 1 ADR-011)
**Activado por**: `FRAMEWORK_SCOPE=sandbox` en pre-commit hook.
**Sustituye a**: `AGENTS.md` solo cuando el scope es sandbox.
**Referencia**: `decisions/ADR-011-capa-correctiva-y-scope-aware.md` Phase 1.

---

## Propósito

Este archivo es el **subset relaxed** de `AGENTS.md` que GGA aplica cuando el código está en un sandbox de validación empírica del Framework (no producción, sin usuarios finales).

**Filosofía**: mismo rigor en lo que importa para seguridad real, downgrade en lo que es ruido para scope de sandbox.

**Qué se relaja vs AGENTS.md**:
- Migration naming estricto (`YYYYMMDDHHmm_*.sql`) → WARN, no bloqueante
- `console.log/error/warn` → WARN, no bloqueante (sandbox no tiene observability productiva)
- Non-null assertions `x!` → WARN
- ADRs obligatorios para cada excepción → WARN (sandbox aprende, no audita)
- Type casts `as any` con justificación inline → WARN
- CSP policies (`unsafe-eval`, `unsafe-inline`) → WARN (sandbox no expone a usuarios)
- Cobertura de tests mínima → WARN si <50% (vs 70% en prod)

**Qué se mantiene CRÍTICO incluso en sandbox**:
- Secrets hardcoded → BLOQUEANTE (siempre)
- SQL injection (string interpolation en queries) → BLOQUEANTE (siempre)
- RLS deshabilitada en tablas con datos → BLOQUEANTE
- `SECURITY DEFINER` sin `search_path` explícito → BLOQUEANTE
- TypeScript `strict: false` o `// @ts-ignore` sin razón → BLOQUEANTE
- Errores swallowed en código de seguridad/auth → BLOQUEANTE

---

## REGLAS GLOBALES (sandbox)

### G-1 — Reversibilidad por defecto

- Hard delete en datos de negocio → BLOQUEANTE (siempre).
- Migrations idempotentes → BLOQUEANTE (siempre).
- Idempotency-Key en POST/PUT críticos → WARN en sandbox (BLOQUEANTE en prod).
- Feature flags → WARN en sandbox (no requeridos).

### G-2 — Tiempo siempre en UTC

- `TIMESTAMPTZ` en DB → BLOQUEANTE (siempre).
- `now()` del cliente → WARN en sandbox.
- Tests con timezones → WARN en sandbox.

### G-3 — Errores nunca silenciosos

- `except: pass` sin comentario → WARN en sandbox.
- `.catch(() => {})` vacío en código de auth/security → BLOQUEANTE.
- `.catch(() => {})` vacío en código de UI/logging → WARN.
- Errores swallowed en boundaries (HTTP, DB, auth) → BLOQUEANTE.

### G-4 — Zero-trust en boundaries (CRÍTICO incluso en sandbox)

- Validación schema en boundaries → BLOQUEANTE (siempre).
- String interpolation en SQL → BLOQUEANTE (siempre).
- Secrets hardcoded → BLOQUEANTE (siempre).
- API keys, tokens en commits → BLOQUEANTE (siempre).

### G-5 — SOLID estructural

- Funciones ≤ 50 líneas → WARN en sandbox (BLOQUEANTE en prod).
- Clases ≤ 300 líneas → WARN en sandbox.
- God objects → WARN en sandbox.
- Imports circulares → BLOQUEANTE (siempre).

### G-6 — Observabilidad (RELAJADA en sandbox)

- `console.log/error/warn` → WARN en sandbox (BLOQUEANTE en prod).
- `print()` en Python → WARN en sandbox.
- `request_id` propagado → WARN en sandbox (sandbox no tiene tracing productivo).
- Logs JSON estructurados → WARN en sandbox.
- Stack trace + contexto en errores → WARN en sandbox.

### G-7 — Captura de dominio explícita

- Spec del dominio antes de implementar → WARN en sandbox.
- Invariantes en código → BLOQUEANTE (siempre, simple a expresar).

---

## REGLAS POR LENGUAJE (sandbox)

### P — Python

- **P-1** Type hints obligatorios → BLOQUEANTE (siempre).
- **P-2** Linters (`ruff`) → BLOQUEANTE (siempre, configurado base).
- **P-3** Docstrings → WARN en sandbox.
- **P-4** Custom exceptions específicas → WARN en sandbox.
- **P-5** Async/sync consistency → BLOQUEANTE (siempre, bug surface).
- **P-6** Cobertura ≥ 50% en sandbox (vs 70% prod) → WARN si menos.

### S — SQL (CRÍTICO incluso en sandbox)

- **S-1** Zero-trust + RLS → BLOQUEANTE (siempre).
- **S-2** SECURITY DEFINER + `search_path` → BLOQUEANTE (siempre).
- **S-3** Migrations idempotentes → BLOQUEANTE.
- **S-3-naming** Migration naming `YYYYMMDDHHmm_*` → WARN en sandbox (numeración simple OK).
- **S-4** Foreign keys con ON DELETE explícito → WARN en sandbox.
- **S-5** Indexes pensados → WARN en sandbox.
- **S-6** Tipos específicos (UUID, TIMESTAMPTZ, JSONB) → BLOQUEANTE (siempre, costo bajo).

### TS — TypeScript / JavaScript

- **TS-1** Strict mode → BLOQUEANTE (siempre).
- **TS-1-any** `any` sin `// @ts-expect-error: <razón>` → WARN en sandbox (BLOQUEANTE en prod).
- **TS-1-nonnull** Non-null assertion `x!` → WARN en sandbox.
- **TS-1-cast** `as any` con justificación inline → WARN en sandbox.
- **TS-2** Interfaces / Zod schemas → WARN en sandbox.
- **TS-3** React hooks deps → BLOQUEANTE (siempre, runtime bugs).
- **TS-5** Promises sin catch → WARN en sandbox (BLOQUEANTE en prod).

---

## SEGURIDAD WEB (sandbox)

- **CSP `unsafe-eval`** → WARN en sandbox (BLOQUEANTE en prod).
- **CSP `unsafe-inline`** → WARN en sandbox (BLOQUEANTE en prod).
- **CORS wildcard `*`** → WARN en sandbox (BLOQUEANTE en prod).
- **Headers de seguridad (HSTS, X-Frame-Options)** → WARN en sandbox.

---

## REGLAS DE COMMITS (idénticas)

- **C-1** Conventional Commits → BLOQUEANTE (siempre).
- **C-2** Mensajes informativos → WARN.
- **C-3** No WIP en main → BLOQUEANTE (siempre).
- **C-4** Granularidad → WARN.

---

## REGLAS DE TESTS (sandbox)

- **T-1** Cobertura ≥ 50% en sandbox (vs 70% prod) → WARN.
- **T-2** Tests adversariales → WARN en sandbox.
- **T-3** Tests con timezones → WARN en sandbox.
- **T-4** No smoke tests disfrazados → WARN en sandbox.

---

## REGLAS DE DOCUMENTACIÓN (sandbox)

- **D-1** README por módulo → WARN en sandbox.
- **D-2** ADRs para decisiones técnicas → WARN en sandbox (excepción puntual OK sin ADR formal).
- **D-3** Docstrings → WARN en sandbox.
- **D-4** Schemas documentados → WARN en sandbox.

---

## REGLAS DE ARQUITECTURA (sandbox)

- **A-1** Boundaries → WARN en sandbox.
- **A-2** Inyección de dependencias → WARN en sandbox.
- **A-3** Separation of concerns → WARN en sandbox.
- **A-4** 3 capas (preventiva/verificable/correctiva) explícitas → WARN en sandbox.

---

## CRITERIO DE BLOQUEO (sandbox)

GGA debe **BLOQUEAR el commit** solo si:
1. Alguna regla marcada BLOQUEANTE arriba se viola.
2. Hay secrets hardcoded.
3. Hay SQL injection literal.
4. RLS deshabilitada o policy permisiva en tabla con datos.
5. TypeScript `strict: false` o `// @ts-ignore` sin razón documentada.
6. Imports circulares.

Todo lo demás es WARN: se reporta, no se bloquea.

---

## EVOLUCIÓN

- **v1.0** (2026-05-21): Phase 1 ADR-011. Subset inicial basado en findings empíricos Iteración 3.
- **v1.x próximas**: calibrar según métrica M1 (rounds de GGA esperados ≤2 en sandbox).

---

## REFERENCIAS

- `AGENTS.md` — Reglas completas (scope=production, default).
- `decisions/ADR-011-capa-correctiva-y-scope-aware.md` — Decisión de scope-aware.
- `docs/SCOPE-AWARENESS.md` — Doc operativo de cómo activar scopes.
