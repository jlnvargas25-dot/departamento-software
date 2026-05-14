# AGENTS.md — Reglas de Código del Departamento de Software

**Versión**: 1.0 (2026-05-13)
**Consumido por**: Gentleman Guardian Angel (GGA) en pre-commit hooks
**Referencia constitucional**: `CLAUDE.md`, `PROTOCOLO-CONSTRUCCION-CODIGO.md`

---

## Propósito

Este archivo define las reglas que el code reviewer (GGA) aplica a cada commit. Es complementario a `CLAUDE.md` (constitución de Claude) y `PROTOCOLO-CONSTRUCCION-CODIGO.md` (12 pasos + reglas globales).

Reglas mínimas v1.0. Ampliar en Sprint 2 cuando empecemos a generar código real de Stallen.

---

## REGLAS GLOBALES (aplican a TODO código)

### 1. Reversibilidad por defecto (Regla R-5)

- Hard delete está prohibido en datos de negocio. Usar soft delete con campo `deleted_at`.
- Migrations deben ser idempotentes: `DROP IF EXISTS` antes de `CREATE`, re-ejecución segura.
- Operaciones críticas con Idempotency-Key.
- Features nuevas detrás de feature flag durante período de validación.

### 2. Tiempo siempre en UTC (Regla R-6)

- Todo timestamp en base de datos: `TIMESTAMPTZ` (Postgres) o equivalente con timezone.
- Nunca confiar en `now()` del cliente, siempre server-side.
- Conversiones a timezone del usuario solo en capa de presentación.

### 3. Errores nunca silenciosos

- Prohibido `except: pass` en Python sin razón documentada.
- Prohibido `.catch(() => {})` vacío en JavaScript/TypeScript.
- Todo error debe loggearse, propagarse, o resolverse explícitamente.

### 4. Zero-trust en boundaries

- Todo input externo (HTTP, DB, archivos, env vars) debe validarse con schema (Pydantic, Zod, etc.).
- Nunca usar string interpolation en queries SQL. Solo parametrized queries.
- Secrets fuera del código (env vars, secret managers).

### 5. SOLID estructural

- Funciones ≤ 50 líneas.
- Clases ≤ 300 líneas.
- Sin god objects.
- Sin imports circulares.

---

## REGLAS POR LENGUAJE

### Python

- Type hints obligatorios en funciones públicas.
- `pyproject.toml` con linters estrictos (ruff, mypy).
- Imports ordenados (isort).
- Docstrings en funciones públicas (formato Google o NumPy).

### SQL (Postgres / Supabase)

- NUNCA acceso directo a tablas con datos sensibles. SIEMPRE via RPCs `SECURITY DEFINER`.
- RLS (Row Level Security) habilitada en todas las tablas con datos de negocio.
- `search_path` explícito en SECURITY DEFINER functions.
- Migrations idempotentes.

### TypeScript / JavaScript

- `strict: true` en `tsconfig.json`.
- Sin `any` types salvo cuando hay justificación documentada.
- Prefer interfaces over types para objetos.
- Functional components en React (no class components nuevos).

---

## REGLAS DE COMMITS

- Conventional Commits: `feat:`, `fix:`, `chore:`, `docs:`, `refactor:`, `test:`.
- Mensaje en español o inglés, consistente dentro del proyecto.
- Cuerpo del commit con contexto si el cambio no es trivial.
- No commits de "WIP" en `main`. Solo en branches.

---

## REGLAS DE TESTS

- Cobertura mínima: 70% en código de dominio.
- Tests adversariales obligatorios para inputs externos.
- Tests con timezones distintas para código que maneja fechas.

---

## REGLAS DE DOCUMENTACIÓN

- README.md por módulo importante.
- ADRs (Architecture Decision Records) en `decisions/` para decisiones técnicas importantes.
- Comentarios solo cuando el código no es auto-explicativo.

---

## EVOLUCIÓN DE ESTE ARCHIVO

- v1.0 (2026-05-13): Reglas mínimas para arrancar Sprint 2.
- Próximas versiones: agregar reglas específicas cuando aparezcan patrones repetidos.
- Toda regla nueva debe referenciar el meta-patrón de origen (5° principio rector: polinización cruzada).

---

**Referencias**:
- `CLAUDE.md` — Constitución de Claude (7 principios rectores)
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` — 12 pasos + 6 reglas globales (R-0 a R-6)
- `DEPARTAMENTO-DE-SOFTWARE.md` § 8 — 10 dimensiones adicionales de calidad
