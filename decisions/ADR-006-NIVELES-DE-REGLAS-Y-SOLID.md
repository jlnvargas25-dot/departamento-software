# ADR-006: Niveles de Reglas y Aplicación de SOLID

**Status**: ACCEPTED
**Date**: 2026-05-15
**Decision makers**: Julián Vargas (con análisis Claude)
**Supersedes**: implícitamente refina ADR-005 (cierre Sprint 1)
**Related**: ADR-004 (calibración nivel comercial)

---

## Contexto

Durante la sesión post-cierre Sprint 1 (2026-05-14/15), revisamos el legacy
SigmaControl (en `C:\Users\Windows 11\sigmacontrol-camino-1\`) para depurar
qué destilar al Departamento nuevo.

El análisis reveló **mezcla de niveles de reglas** en el legacy:
- `CLAUDE_DEPARTAMENTO.md` mezclaba principios filosóficos, reglas universales,
  decisiones de momento, y configuración Stallen en un solo lugar
- Las 170+ reglas SQL estaban en `modo/programacion/reglas/` mezclando
  reglas universales (LIMIT en SETOF) con reglas Stallen (sufijos _sc)
- Las 55 skills mezclaban niveles distintos sin criterio explícito

Esta mezcla generaba problemas concretos:
1. **No portabilidad**: tomar un cliente nuevo requería re-leer todo y decidir
   manualmente qué se mantiene
2. **No auditabilidad**: imposible saber si una regla era universal o local
3. **Falta de SOLID claro**: violaciones de SRP, OCP, DIP detectables pero
   no formalizadas

En paralelo, durante la sesión se descubrió **Harness Engineering** como
disciplina formal (referencias OpenAI, Anthropic, Martin Fowler, Thoughtworks)
con vocabulario propio: instrucciones, state, verificación, scope, lifecycle.

Julián identificó (lúcidamente, en mensaje de las 9 AM aprox.) que la
depuración necesitaba:
- Separar **reglas universales de arquitectura aparte**
- Aplicar **SOLID** como framework explícito
- **Separación de carpetas** que materialice los niveles

Esta combinación de hallazgos motiva esta decisión formal.

---

## Decisión

### Adoptar formalmente 5 niveles de reglas

```
NIVEL 1 — Principios filosóficos
  Lugar: CLAUDE.md, AGENTS.md (raíz)
  Cambia: casi nunca (madurez filosófica)
  Aplica: a todos los proyectos, todos los stacks

NIVEL 2 — Reglas de arquitectura universal
  Lugar: architecture/ (nueva carpeta)
  Cambia: raramente (patrones estructurales nuevos)
  Aplica: a cualquier proyecto SaaS multi-tenant

NIVEL 3 — Reglas técnicas universales
  Lugar: .claude/skills/ + mcp-servers/ (nueva)
  Cambia: con cambios de stack
  Aplica: a cualquier proyecto del mismo stack (Supabase/PostgreSQL)

NIVEL 4 — Reglas de dominio específico
  Lugar: domain-captures/
  Cambia: con cada cliente nuevo
  Aplica: al cliente específico (Stallen, futuros)

NIVEL 5 — Reglas del proyecto/momento
  Lugar: decisions/ (ADRs)
  Cambia: con cada decisión técnica concreta
  Aplica: al proyecto/momento específico
```

### Adoptar SOLID como framework explícito

SOLID se adopta **no solo para código OOP**, sino para:
- Diseño de MCP servers (SRP, ISP, DIP)
- Diseño de skills (SRP, ISP)
- Estructura de carpetas (SRP, OCP)
- Schemas de configuración (LSP, DIP)
- Documentación (SRP)

Ver `architecture/PRINCIPIOS-SOLID.md` para aplicación detallada.

### Crear nueva carpeta `architecture/` para Nivel 2

Esta carpeta contiene exclusivamente documentos de Nivel 2:
- `README.md` (índice + explicación de niveles)
- `PRINCIPIOS-SOLID.md` (SOLID adaptado)
- `PRINCIPIOS-ARQUITECTURA.md` (10 reglas A1-A10 universales)
- `PATRONES-CARPETAS.md` (estructura + reglas C1-C6)
- `ANTI-PATRONES.md` (anti-patterns conocidos con evidencia empírica)

### Crear nueva carpeta `mcp-servers/` para Nivel 3 ejecutable

Esta carpeta contiene los MCP servers que se construirán en Sprint 2-3:
- `sigma-validators-r/` (Sprint 2 T2 — las 170+ reglas SQL destiladas)
- `sigma-close-session-validator/` (Sprint 2 T3)

Los servers son **agnósticos de proyecto**: reciben config desde
`domain-captures/`, NO hardcodean nada Stallen-specific (cumple DIP).

### Formalizar las 6 reglas C1-C6 de organización de carpetas

```
C1. La raíz solo contiene puntos de entrada
C2. architecture/ contiene SOLO documentos universales (Nivel 2)
C3. domain-captures/ contiene SOLO configuración de dominio
C4. mcp-servers/ contiene SOLO validators y tools agnósticos
C5. workspace/ contiene el código real del proyecto activo
C6. Cada carpeta tiene README.md propio
```

Detalle en `architecture/PATRONES-CARPETAS.md`.

### Formalizar las 15 reglas A1-A15 de arquitectura universal

```
A1.  Module Ownership (propiedad de datos por módulo)
A2.  Encapsulación de tablas (interfaces, no acceso directo)
A3.  Inter-Module Contracts (contratos explícitos)
A4.  Acíclicidad de Dependencias
A5.  Multi-tenant Strict Isolation
A6.  Immutability for Audit
A7.  Domain Validation Before Implementation
A8.  Idempotency or Explicit Rollback
A9.  Stop Conditions Explicit
A10. No Test Code in Production Artifacts
A11. DAO + DTO (patrones de acceso a datos)        ← v1.1
A12. Zero Trust (Never trust, always verify)        ← v1.1
A13. Concurrency Safety                              ← v1.1
A14. Explicit Failure (Anti Silent Errors)           ← v1.1
A15. Unhappy Path First (Anti Happy Path Bias)       ← v1.1
```

Detalle en `architecture/PRINCIPIOS-ARQUITECTURA.md`.

**Nota**: las reglas A11-A15 fueron agregadas tras audit empírico de Julián
(post creación inicial del documento). El audit detectó que aunque los
conceptos existían implícitamente en A1-A10 o en el legacy, no estaban
formalizados con vocabulario industrial reconocible (DAO/DTO, Zero Trust,
Happy Path Bias). Esta omisión fue corregida agregando A11-A15 con ejemplos
completos. Ver `architecture/ANTI-PATRONES.md` para anti-patterns vinculados
(AP-2.8, AP-2.9, AP-3.6, AP-3.7, AP-3.8).

---

## Implicaciones para Sprint 2

### Cambios al plan Sprint 2 (de ADR-005)

**T2 (validators R) - REFORMULADO**:

Original (ADR-005): "MCP server sigma-validators-r-mvp"
Nuevo (este ADR): MCP server `sigma-validators-r` que:

1. Vive en `mcp-servers/sigma-validators-r/` (regla C4)
2. Es agnóstico de Stallen (regla DIP, AP-2.2)
3. Tiene tools segregadas (regla ISP, AP-2.1):
   - `validate_sql_invariants(sql, rollback, config)`
   - `validate_sql_performance(sql)`
   - `validate_sql_security(sql, config)`
   - `validate_sql_concurrency(sql)`
   - `validate_sql_adversarial(sql, config)`
   - `validate_sql_scale(sql, escala_operativa)`
   - `split_sql(sql)`
4. Recibe config de Stallen via `domain-captures/stallen-domain.md`
5. Sub-tareas:
   - T2.1: Python validators (3 días)
   - T2.2: Skills markdown (1.5 días) — 11 skills nuevas en `.claude/skills/`
   - T2.3: Config Stallen (0.5 día)
   - T2.4: Tests adversariales (1 día)
   - **Total: 6 días** (vs 5 originales)

**Skills nuevas (Sprint 2 T2.2)**:
```
sigma-sql-production-rules/SKILL.md
sigma-multitenancy-bootstrap/SKILL.md
sigma-immutable-tables/SKILL.md
sigma-no-test-code/SKILL.md
sigma-detect-failures/SKILL.md
sigma-stop-conditions/SKILL.md
sigma-session-handoff/SKILL.md
sigma-memory-anti-degradation/SKILL.md
sigma-cleanup-staff-engineer/SKILL.md
sigma-naming-conventions/SKILL.md  (template, no hardcoded)
```

### Implicaciones para Sprint 3-5

Sprint 3 (CI/CD):
- Validar reglas C1-C6 automáticamente en CI
- Validar reglas A1-A10 que sean automatizables

Sprint 4 (observabilidad):
- Métricas por validator separado (gracias a ISP, podemos medir cada uno)

Sprint 5 (release):
- Release process aplica también a actualizaciones de `architecture/`
- Cambios a Nivel 2 requieren bump de versión MAYOR (breaking change posible)

### Implicaciones para futuros clientes

Cuando se tome un cliente nuevo (post-Stallen):

```
1. Reusar Niveles 1-3 sin tocar
2. Crear domain-captures/<cliente>.md (Nivel 4)
3. Crear ADRs específicos del proyecto (Nivel 5)
4. Inicializar workspace/<cliente>/ (código real)

Tiempo estimado para onboarding nuevo cliente: 1-2 días (vs semanas
en el legacy donde había que re-decidir todo)
```

---

## Alternativas consideradas

### Alternativa 1: Mantener todo mezclado (como legacy)

**Pros**:
- Cero esfuerzo de reorganización
- "Funciona" para 1 cliente

**Contras**:
- No escala a múltiples clientes
- Imposible reusar entre proyectos
- Viola SOLID en múltiples puntos
- Cada cliente nuevo = re-aprender todo

**Rechazada**: la pivotada del Sprint 1 (uso personal multi-proyecto) requiere
portabilidad.

### Alternativa 2: 3 niveles (universal / proyecto / específico)

**Pros**:
- Más simple que 5 niveles
- Más fácil de explicar

**Contras**:
- Mezcla principios filosóficos con reglas técnicas
- Mezcla dominio con scope decisions
- No es lo suficientemente granular para validation automation

**Rechazada**: granularidad insuficiente para los casos de uso identificados.

### Alternativa 3: 7+ niveles (más granular)

**Pros**:
- Máxima separación de preocupaciones
- Validación más fina

**Contras**:
- Overhead cognitivo alto
- Difícil decidir nivel correcto para cada regla nueva
- Niveles intermedios sin uso real

**Rechazada**: complejidad sin beneficio práctico.

### Alternativa 4: Adoptar vocabulario formal industrial (Clean Architecture)

**Pros**:
- Reconocible para devs con experiencia
- Hay literatura abundante

**Contras**:
- Clean Architecture es para apps, no para harness
- Capas de Clean Arch no mapean 1:1 a niveles de reglas
- Forzar Clean Architecture donde no aplica genera confusión

**Rechazada**: Harness Engineering + SOLID + niveles propios son mejor fit.

---

## Consecuencias

### Positivas

1. **Portabilidad**: tomar cliente nuevo NO requiere modificar Niveles 1-3
2. **Auditabilidad**: cada regla tiene nivel explícito
3. **Mantenibilidad**: cambios estructurales tienen alcance acotado
4. **SOLID enforced**: cada artefacto tiene SRP claro
5. **Onboarding más rápido**: 4 documentos en `architecture/` dan base teórica completa
6. **Validation automation**: la estructura misma es validable

### Negativas (trade-offs aceptados)

1. **Overhead inicial**: 8 archivos nuevos a crear, ~30-40 min de trabajo
2. **Reorganización mental**: pensar en nivel correcto al agregar regla nueva
3. **Más carpetas que antes**: requiere navegación inicial
4. **Posible "regla en limbo"**: a veces no es obvio si es Nivel 2 o 3

### Mitigaciones

1. El overhead inicial se amortiza tras 1 cliente nuevo (que será 5x más
   rápido de onboardear)
2. La reorganización mental se sistematiza con el test de nivel (4 preguntas)
3. Las carpetas tienen READMEs auto-explicativos
4. Para "reglas en limbo", default a Nivel más alto (más universal) y degrade
   después si se prueba que aplica solo a stack/dominio

---

## Validación de la decisión

**Criterios para considerar este ADR exitoso** (revisar en Sprint 3+):

1. **Sprint 2 T2 completable en ≤6 días** usando este framework
2. **Cero re-clasificaciones de nivel** durante Sprint 2 (señal de clasificación correcta)
3. **MCP server sigma-validators-r genuinamente agnóstico** de Stallen
4. **stallen-domain.md ≤ 50 líneas** (señal de captura compacta)
5. **Skills nuevas (10) todas siguen SRP** (test del título único)

**Criterios para considerar este ADR fallido** (justificarían revisión):

1. Necesidad de modificar Niveles 1-3 frecuentemente (señal de mala clasificación)
2. Reglas que no encajan en ningún nivel (puede que falte un nivel nuevo)
3. Overhead de gestión > 20% del tiempo de desarrollo (señal de over-engineering)

---

## Implementación inmediata

**En esta sesión (2026-05-15)**:
- ✅ Crear carpeta `architecture/` con 5 archivos (README + 4 docs)
- ✅ Crear carpeta `mcp-servers/` con README
- ✅ Crear este ADR (ADR-006)
- ✅ Actualizar README.md raíz con nueva estructura

**Sprint 2 (a partir de Día 2)**:
- T2.1: implementar Python validators agnósticos en `mcp-servers/sigma-validators-r/`
- T2.2: crear las 10 skills nuevas en `.claude/skills/`
- T2.3: capturar Stallen domain en `domain-captures/stallen-domain.md`
- T2.4: tests adversariales

**Tracking**:
- Cada commit relevante a esta reorganización menciona "ADR-006"
- Cualquier desviación se documenta en ADR posterior

---

## Referencias

- `architecture/PRINCIPIOS-SOLID.md` — SOLID adaptado
- `architecture/PRINCIPIOS-ARQUITECTURA.md` — reglas A1-A10
- `architecture/PATRONES-CARPETAS.md` — reglas C1-C6
- `architecture/ANTI-PATRONES.md` — anti-patterns con evidencia
- `decisions/ADR-005-cierre-sprint-1.md` — Sprint 2 plan original (este ADR lo refina)
- Legacy SigmaControl `C:\Users\Windows 11\sigmacontrol-camino-1\` — origen de reglas destiladas
- Harness Engineering disciplina formal (OpenAI, Anthropic, Fowler, Thoughtworks 2026)
- Robert C. Martin, "Agile Software Development" (2002) — SOLID original

---

## Histórico

- **2026-05-15**: Creado tras sesión post-cierre Sprint 1 con análisis de depuración legacy
- **2026-05-15** (mismo día, post audit empírico): ADR refinado para incluir A11-A15.
  Julián aplicó el 6° principio rector al propio ADR detectando 5 GAPS legitimos
  (DAO/DTO implícito, Zero Trust parcial, Concurrency parcial, Silent Errors
  no documentado, Happy Path Bias no documentado). Las reglas A11-A15 + anti-patterns
  AP-2.8/AP-2.9/AP-3.6/AP-3.7/AP-3.8 fueron agregadas en la misma sesión.
