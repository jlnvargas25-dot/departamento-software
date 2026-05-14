# AGENTS.md — Reglas de Código del Departamento de Software

**Versión**: 1.1 (2026-05-14)
**Consumido por**: Gentleman Guardian Angel (GGA) en pre-commit hooks
**Referencia constitucional**: `CLAUDE.md`, `PROTOCOLO-CONSTRUCCION-CODIGO.md`, `DEPARTAMENTO-DE-SOFTWARE.md` § 8

---

## Propósito

Este archivo define las reglas que el code reviewer (GGA) aplica a cada commit. Es complementario a:
- `CLAUDE.md` (constitución de Claude, 7 principios rectores)
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` (12 pasos + reglas globales R-0 a R-6)
- `DEPARTAMENTO-DE-SOFTWARE.md` § 8 (10 dimensiones de calidad)

**Filosofía**: las reglas son **enforceable**, no aspiracionales. Si GGA detecta una violación, el commit se rechaza. Las excepciones requieren justificación explícita en el cuerpo del commit y referencia a un ADR.

---

## REGLAS GLOBALES (aplican a TODO código)

### G-1 — Reversibilidad por defecto (Regla R-5)

- Hard delete está PROHIBIDO en datos de negocio. Usar soft delete con campo `deleted_at` o equivalente.
- Migrations DEBEN ser idempotentes: `DROP IF EXISTS` antes de `CREATE`, re-ejecución segura.
- Operaciones POST/PUT críticas DEBEN aceptar `Idempotency-Key` header.
- Features nuevas DEBEN ir detrás de feature flag durante período de validación inicial.
- Excepciones requieren ADR explícito en `decisions/`.

### G-2 — Tiempo siempre en UTC (Regla R-6)

- Todo timestamp en base de datos: `TIMESTAMPTZ` (Postgres) o equivalente con timezone explícito.
- NUNCA confiar en `now()` o equivalente del cliente — siempre server-side.
- Conversiones a timezone del usuario solo en capa de presentación (frontend).
- Tests con timezones distintas obligatorios para código que maneja fechas.

### G-3 — Errores nunca silenciosos

- PROHIBIDO `except: pass` en Python sin razón documentada en comentario inline.
- PROHIBIDO `.catch(() => {})` vacío en JavaScript/TypeScript.
- PROHIBIDO swallowing de errores en cualquier forma.
- Todo error DEBE loggearse, propagarse, o resolverse explícitamente con razón comentada.

### G-4 — Zero-trust en boundaries

- Todo input externo (HTTP body, query params, DB rows, archivos, env vars) DEBE validarse con schema (Pydantic, Zod, JSON Schema, etc.).
- NUNCA usar string interpolation en queries SQL. Solo parametrized queries / prepared statements.
- Secrets fuera del código: env vars, secret manager, NUNCA hardcoded.
- API keys, tokens, passwords: rechazados automáticamente si aparecen en commits (regex match).

### G-5 — SOLID estructural

- Funciones ≤ 50 líneas (sin contar comments + blank lines).
- Clases ≤ 300 líneas.
- Sin god objects (clase con > 10 métodos públicos requiere justificación).
- Sin imports circulares (linter debe enforcement).
- Cada módulo con responsabilidad única clara documentada en docstring.

### G-6 — Observabilidad estructurada

- Todo error inesperado DEBE capturarse con stack trace + contexto (request_id, user_id si aplica).
- Logs en formato JSON estructurado, NO `print()` ni `console.log()` en producción.
- Cada request HTTP DEBE tener `request_id` único propagado en logs.
- Métricas de negocio (no solo CPU/RAM) requeridas para endpoints críticos.

### G-7 — Captura de dominio explícita (3° principio rector)

- Antes de implementar lógica de negocio, debe existir documentación del dominio en `openspec/specs/{domain}/spec.md` o en el proposal de la change activa.
- PROHIBIDO asumir reglas del negocio. Si no está documentado, hay que capturarlo primero.
- Invariantes del dominio explícitas en el código (assertions o type system).

---

## REGLAS POR LENGUAJE

### P — Python

**P-1 Type hints obligatorios**
- Toda función pública DEBE tener type hints en parámetros y retorno.
- `mypy` configurado en modo strict (`strict = true` en `pyproject.toml`).
- Sin `# type: ignore` salvo con comentario explicando por qué.

**P-2 Linters estrictos**
- `ruff` con reglas: `E`, `F`, `W`, `I`, `N`, `UP`, `B`, `C4`, `SIM`, `RUF`.
- Línea máxima: 100 caracteres (preferencia, no rígido).
- Imports ordenados (ruff/isort).

**P-3 Docstrings en funciones públicas**
- Formato Google o NumPy, consistente dentro del módulo.
- Incluir: descripción breve, args, returns, raises, ejemplos cuando ayudan.
- Funciones privadas (`_prefijo`) pueden omitir docstring si el nombre es auto-explicativo.

**P-4 Manejo de excepciones específico**
- `except Exception:` requiere justificación en comentario.
- Custom exceptions específicas del dominio en módulo `exceptions.py`.
- Cadenas de excepciones explícitas con `raise X from Y`.

**P-5 Async/await consistencia**
- No mezclar sync y async dentro del mismo módulo sin razón documentada.
- Funciones async marcadas claramente, no usar wrappers ocultos.

**P-6 Tests pytest**
- Tests en directorio `tests/` paralelo a `src/`.
- Nombres: `test_<modulo>_<comportamiento>` para funciones, `Test<Clase>` para clases.
- Hypothesis para property-based testing en código de dominio.
- Cobertura mínima 70% en código de dominio (medida con `coverage`).

### S — SQL (Postgres / Supabase)

**S-1 Zero-trust en datos**
- NUNCA acceso directo a tablas con datos sensibles desde aplicación. SIEMPRE via RPCs `SECURITY DEFINER`.
- RLS (Row Level Security) HABILITADA en todas las tablas con datos de negocio o usuarios.
- Policies de RLS específicas por rol (no usar `true` como policy en producción).

**S-2 RPCs SECURITY DEFINER**
- Funciones con `SECURITY DEFINER` DEBEN tener `search_path` explícito (ej: `SET search_path = public, pg_temp`).
- Volatilidad declarada: `IMMUTABLE`, `STABLE` o `VOLATILE`.
- Ownership del schema explícito y documentado.

**S-3 Migrations idempotentes**
- `CREATE TABLE IF NOT EXISTS`, `DROP IF EXISTS`, `CREATE OR REPLACE FUNCTION`.
- Migrations nombradas con timestamp: `YYYYMMDDHHmm_descripcion.sql`.
- Re-ejecución segura validada con dry-run antes de aplicar.

**S-4 Constraints explícitas**
- Foreign keys con `ON DELETE` explícito (CASCADE, RESTRICT, SET NULL — decisión documentada).
- Check constraints para invariantes del dominio cuando aplique.
- NOT NULL salvo cuando NULL tiene significado documentado.

**S-5 Indexes pensados**
- Indexes en columnas usadas en JOINs frecuentes.
- Indexes parciales cuando WHERE clauses son consistentes.
- Documentar índices con comentarios sobre qué query optimizan.

**S-6 No tipos genéricos sin razón**
- Preferir tipos específicos: `UUID`, `TIMESTAMPTZ`, `JSONB`, `NUMERIC(10,2)`.
- Evitar `TEXT` para columnas que tienen formato (usar dominio o constraint).
- `JSONB` con schema documentado (validación en aplicación o trigger).

### TS — TypeScript / JavaScript

**TS-1 Strict mode obligatorio**
- `tsconfig.json` con `"strict": true`.
- Sin `any` types salvo con comentario `// @ts-expect-error: <razón>`.
- `noImplicitAny`, `strictNullChecks`, `strictFunctionTypes` activados.

**TS-2 Interfaces para datos**
- Prefer interfaces over types para objetos con identidad.
- Types solo para uniones, intersecciones, o transformaciones de tipos.
- Schemas Zod para validación runtime de boundaries.

**TS-3 React (si aplica)**
- Functional components, no class components nuevos.
- Hooks con dependency arrays correctas (eslint-plugin-react-hooks).
- Sin lógica de negocio en componentes — extraer a custom hooks o services.

**TS-4 Svelte/SvelteKit (si aplica)**
- Stores con tipos explícitos.
- Server actions con validación Zod en endpoints.
- Sin lógica de negocio en componentes — extraer a `lib/services/`.

**TS-5 Error handling**
- `Result<T, E>` pattern preferido sobre throwing en business logic.
- Promises siempre con `.catch()` o `try/await/catch`.
- No swallowing de promesas con `.catch(() => {})` vacío.

---

## REGLAS DE COMMITS

### C-1 Conventional Commits

Formato obligatorio: `<type>(<scope>): <descripción corta>`

Types permitidos:
- `feat`: nueva funcionalidad
- `fix`: bug fix
- `chore`: tareas de mantenimiento (deps, build, config)
- `docs`: solo documentación
- `refactor`: refactor sin cambio funcional
- `test`: agregar/modificar tests
- `perf`: mejoras de performance
- `style`: formateo, sin cambio de lógica
- `revert`: revertir commit previo
- `build`: cambios en sistema de build o deps externas
- `ci`: cambios en configuración CI/CD

### C-2 Mensajes informativos

- Línea 1: ≤ 72 caracteres, imperativo presente ("add", "fix", no "added", "fixes").
- Línea 2: en blanco.
- Cuerpo: contexto, por qué (no qué — el diff dice el qué), referencias a ADRs/issues.
- Idioma: consistente en el proyecto (español o inglés, no mezclar).

### C-3 No commits "WIP" en main

- Commits en `main` deben ser working states.
- "WIP" o "checkpoint" solo en branches.
- Si hay que dejar trabajo a medias, push a branch personal, no main.

### C-4 Granularidad

- Un commit = un cambio lógico coherente.
- Cambios no relacionados → commits separados.
- Refactors masivos sin cambio funcional → un commit propio con tag `refactor`.

---

## REGLAS DE TESTS

### T-1 Cobertura mínima
- Código de dominio (lógica de negocio): ≥ 70% cobertura.
- Endpoints HTTP / APIs públicas: ≥ 80% cobertura incluyendo error paths.
- Migrations SQL: smoke test (apply + rollback) por cada migration.

### T-2 Tests adversariales obligatorios

Para cada función pública del dominio, tests que cubran:
- Input vacío / null / undefined
- Input malformado (tipo incorrecto, formato inválido)
- Boundary conditions (0, -1, máximo, mínimo)
- Race conditions si hay concurrencia
- Network failures simuladas para llamadas externas

Property-based testing (Hypothesis en Python, fast-check en JS) preferido sobre ejemplos manuales en código de dominio.

### T-3 Tests con timezones

Código que maneja fechas DEBE tener tests con:
- UTC
- Timezone del usuario (Lima, Bogotá)
- Daylight saving transitions si aplica
- Año bisiesto / fin de año

### T-4 No tests "smoke" disfrazados de unit tests

- Un test que solo verifica que la función no tira excepción NO es unit test.
- Tests deben verificar comportamiento esperado con asserts específicos sobre output.

---

## REGLAS DE DOCUMENTACIÓN

### D-1 README por módulo importante
- Cada paquete top-level: README.md con propósito, uso, dependencias.
- Generación automática de API docs (Sphinx para Python, TypeDoc para TS).

### D-2 ADRs para decisiones técnicas
- Toda decisión arquitectónica significativa: ADR en `decisions/ADR-NNN-titulo.md`.
- Formato: ver `decisions/README.md`.
- Numeración secuencial, nunca renumerar.

### D-3 Docstrings auto-explicativos
- Código auto-explicativo preferido sobre comentarios.
- Comentarios solo para explicar **por qué**, no **qué**.
- TODO comments con autor y fecha: `# TODO(julian, 2026-05-14): ...`

### D-4 Schemas documentados
- API endpoints con OpenAPI/Swagger auto-generado.
- DB schema documentado con comentarios en columnas críticas (`COMMENT ON COLUMN ... IS ...`).

---

## REGLAS DE ARQUITECTURA

### A-1 Boundaries explícitos
- Módulos con responsabilidad única clara.
- Imports cross-módulo solo via interfaces públicas (no internals).
- Linter de arquitectura (import-linter en Python) configurado.

### A-2 Inyección de dependencias
- Dependencias inyectadas, no hardcodeadas.
- Singletons solo cuando hay justificación clara.
- Factories para construcción compleja.

### A-3 Separation of concerns
- Lógica de negocio separada de I/O (DB, HTTP, filesystem).
- Lógica de presentación separada de lógica de negocio.
- Tests unitarios de dominio sin mocks de infraestructura.

### A-4 3 capas (2° principio rector)
- Toda funcionalidad nueva identifica explícitamente sus 3 capas:
  - **Preventiva**: enforcement en compile-time o por design
  - **Verificable**: tests / asserts / monitoring
  - **Correctiva**: auto-fix cuando es determinístico (4° principio)

---

## EVOLUCIÓN DE ESTE ARCHIVO

- **v1.0** (2026-05-13): Reglas mínimas para arrancar Sprint 2 (3 secciones).
- **v1.1** (2026-05-14): Versión completa para arrancar código real. Estructura por bloques (G/P/S/TS/C/T/D/A) con códigos para referencia en commits.
- **Próximas versiones**: agregar reglas cuando aparezcan patrones repetidos.

Toda regla nueva DEBE:
1. Referenciar el meta-patrón de origen (5° principio rector: polinización cruzada)
2. Tener código único asignado (G-X, P-X, S-X, etc.)
3. Ser enforceable (no aspiracional)
4. Ser excepcionable solo con ADR explícito

---

## EXCEPCIONES Y BYPASSES

GGA puede ser bypaseado con `git commit --no-verify`. Esto está PERMITIDO solo en estos casos:

1. **Commits puramente documentales** que claramente no tocan código (ej: ajustar README).
2. **Cierre de sesión** cuando los gates de Sprint 1 todavía no están construidos.
3. **Emergencias documentadas** con razón explícita en el cuerpo del commit + tarea de follow-up en `DEUDA-TECNICA.md`.

PROHIBIDO usar `--no-verify` para:
- Saltarse type checks o linters
- Hacer commits que vendrían rechazados legítimamente por GGA
- "Apurarse" sin razón estructural

Cada uso de `--no-verify` debe quedar registrado con razón en el commit. Audits periódicos detectan bypasses no justificados.

---

## REFERENCIAS

- `CLAUDE.md` — Constitución de Claude (7 principios rectores)
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` — 12 pasos + 6 reglas globales (R-0 a R-6)
- `DEPARTAMENTO-DE-SOFTWARE.md` § 8 — 10 dimensiones adicionales de calidad
- `decisions/ADR-004-calibracion-nivel-comercial.md` — Nivel comercial apuntado
- `decisions/ADR-005-cierre-sprint-1.md` — Cierre Sprint 1 + plan Sprint 2
- `.gga` — Configuración del code reviewer
