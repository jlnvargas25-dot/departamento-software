# Sandbox-Stack Constitution

> Constitución del proyecto sandbox para validación empírica del stack del ecosistema integrado con el Framework Departamento de Software.

**Version**: 0.1 | **Ratified**: 2026-05-21 | **Last Amended**: 2026-05-21

---

## Propósito de este sandbox

Validar empíricamente la integración del stack del ecosistema (Spec Kit + Everything Claude Code + claude-mem + Superpowers) con el Framework Departamento de Software. Output esperado: matriz A1-A25 vs stack en `EVALUATION.md` + insumo para ADR-009.

Este proyecto **NO** es un producto. Es laboratorio empírico del Framework aplicado a sí mismo (7° principio rector — meta-producto recursivo).

---

## Marco arquitectónico heredado del Framework

Este sandbox opera bajo el **Framework Departamento de Software** (`../../` desde este path).

Documentación canónica del Framework:
- `../../CLAUDE.md` — constitución global del Framework + 7 principios
- `../../NORTE.md` — visión harness anti-alucinación senior
- `../../architecture/PRINCIPIOS-ARQUITECTURA.md` — reglas A1-A25 detalladas
- `../../architecture/ANTI-PATRONES.md` — 36 anti-patterns con evidencia
- `../../architecture/PRINCIPIOS-SOLID.md` — SOLID adaptado
- `../../decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md` — 5 niveles del Framework

**Principio operativo del sandbox** (insight Decisión A — sesión PM 2026-05-20):
> Las reglas A* (Nivel 2 declarativo) y el stack del ecosistema (Nivel 3 ejecutable) **NO son sustitutos sino complementos por diseño**. Las A* funcionan como "doble advertencia" — si el skill del stack falla, la regla A* en CLAUDE.md sigue ahí. Defensa en profundidad — 2° principio rector aplicado al meta-trabajo.

---

## Core Principles (Nivel 1 del Framework — 7 principios rectores)

### I. Python traza → IA recorre → Python verifica
Código determinístico orquesta y valida. La IA produce. Nunca al revés.

### II. 3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA
Cada output del sistema pasa por las 3 capas. La correctiva auto-arregla cuando puede. Defensa en profundidad para mitigar fallos del LLM.

### III. Dominio-first
El dominio del negocio se captura activamente antes de cualquier código. No se asume.

### IV. Auto-fix > finding
Cuando una corrección es determinísticamente inequívoca, se aplica. No se devuelve al LLM para que adivine.

### V. Polinización cruzada
Un patrón de dolor descubierto en un subsistema es candidato a propagarse a los demás estructuralmente similares.

### VI. Descubrir antes de ejecutar
Auditoría empírica precede a estimación o diseño. El estado del sistema vivo especifica el scope.

### VII. Meta-producto recursivo
Toda entidad productiva merece el mismo ambiente anti-degradación que su supervisor diseñó para sí mismo. Este sandbox aplica el principio al Framework mismo.

---

## Architecture Rules (Nivel 2 del Framework — A1 a A25)

Las 25 reglas A* son **overlay declarativo universal** para SaaS multi-tenant Tier 1 commercial robust. Cada feature implementada en este sandbox debe pasar el checklist A1-A25 (criterios objetivos verificables).

### Dominio y modularidad (A1-A5)

- **A1 — Module Ownership** — Cada módulo es dueño de sus datos; solo él escribe en sus tablas; otros consumen vía interface explícita.
- **A2 — Encapsulación de tablas** — Tablas son detalles de implementación. Interface pública = RPCs/eventos, NO tablas.
- **A3 — Inter-Module Contracts** — Contratos explícitos tipados entre módulos. Sin acoplamiento implícito.
- **A4 — Acíclicidad de Dependencias** — Grafo de dependencias sin ciclos.
- **A5 — Multi-tenant Strict Isolation [CRÍTICA]** — Aislamiento estricto entre tenants. Una sola fuga = comprometido el SaaS.

### Estado y comportamiento (A6-A10)

- **A6 — Immutability for Audit** — Eventos inmutables para auditabilidad y replay.
- **A7 — Domain Validation Before Implementation** — Validar reglas de dominio antes de codear.
- **A8 — Idempotency or Explicit Rollback** — Operaciones idempotentes o rollback explícito si no.
- **A9 — Stop Conditions Explicit** — Condiciones de parada visibles en loops, retries, recursiones.
- **A10 — No Test Code in Production Artifacts** — Código de test fuera del artefacto productivo.

### Acceso y resiliencia lógica (A11-A15)

- **A11 — DAO + DTO** — Patrones de acceso a datos separados de lógica de dominio.
- **A12 — Zero Trust [CRÍTICA]** — Never trust, always verify. 6 sub-reglas ZT-1..ZT-6.
- **A13 — Concurrency Safety** — Locks, transacciones, optimistic concurrency según contexto.
- **A14 — Explicit Failure** — Anti silent errors. Toda falla es observable.
- **A15 — Unhappy Path First** — Anti happy path bias. Diseñar primero qué puede fallar.

### Infraestructura resiliente (A16-A19)

- **A16 — Rate Limiting & Throttling** — Límites explícitos por tenant/endpoint/usuario.
- **A17 — Edge Protection** — CDN + WAF + DDoS Mitigation en perímetro.
- **A18 — Async Processing for Heavy Tasks** — Operaciones pesadas fuera del thread de respuesta.
- **A19 — External Service Resilience** — Circuit breakers, timeouts, fallbacks para terceros.

### Paradigma y operaciones (A20-A25)

- **A20 — Hexagonal Architecture [CRÍTICA]** — Ports & Adapters. Dominio sin dependencias de infraestructura.
- **A21 — Structured Observability [CRÍTICA]** — 3 pilares: logs estructurados + métricas + traces distribuidos. 6 sub-reglas OBS-1..OBS-6.
- **A22 — Secrets Management [CRÍTICA]** — Vaulting + rotation + CI detection. Vector ataque #1.
- **A23 — Deployment Safety** — Zero-downtime + versioning + feature flags + canary.
- **A24 — Data Lifecycle & Privacy [CRÍTICA]** — Retention policies + GDPR + PII classification.
- **A25 — Authorization Model** — RBAC/ABAC granular intra-tenant.

---

## Stack del ecosistema integrado (Nivel 3 ejecutable)

### Spec Kit — workflow SDD backbone
9 skills `speckit-*`: constitution, specify, plan, tasks, implement, clarify, analyze, checklist, taskstoissues.

Provee: estructura de specs/plans/tasks + workflow agent-skill-based + templates markdown.

Cobertura A*: ninguna directa — Spec Kit es **el orquestador del proceso**, no el ejecutor de reglas.

### Everything Claude Code (ECC) — stack ejecutable principal
200+ skills `ecc:*` en 25+ sub-familias. Cobertura directa de múltiples A*:

| Regla A* | Skill ECC que la cubre |
|---|---|
| A20 Hexagonal | `ecc:hexagonal-architecture` |
| A21 Observability | `ecc:harness-audit` + `ecc:context-budget` |
| A22 Secrets | `ecc:security-scan` + `ecc:security-bounty-hunter` |
| A23 Deployment | `ecc:deployment-patterns` + `ecc:canary-watch` |
| A24 Data Lifecycle | `ecc:hipaa-compliance` (compliance subset) |
| A25 Authorization | parcial via `ecc:laravel-security`, `ecc:springboot-security` |
| A12 Zero Trust | `ecc:security-review` + `ecc:security-scan` + `ecc:safety-guard` + `ecc:gateguard` |
| A13 Concurrency | `ecc:kotlin-coroutines-flows` + lang-specific patterns |
| A14 Explicit Failure | `ecc:error-handling` |
| A15 Unhappy Path | `ecc:tdd-workflow` (TDD favorece unhappy path first) |
| A16 Rate Limiting | indirecto via `ecc:vercel-firewall` patterns |
| A18 Async | lang-specific patterns |
| Workflow general | `ecc:plan-orchestrate`, `ecc:multi-plan`, `ecc:multi-execute`, `ecc:council` |
| Validation | `ecc:quality-gate`, `ecc:verification-loop`, `ecc:code-review`, `ecc:judgment-day`, `ecc:santa-loop` |
| ADR pattern | `ecc:architecture-decision-records` |
| Harness vision | `ecc:harness-audit`, `ecc:harness-optimizer`, `ecc:autonomous-agent-harness` |

### claude-mem — memoria persistente cross-sesión
12 skills `claude-mem:*`. Sucesor de Engram (bloqueado por SAC).

Cobertura A*: ninguna directa. **Es infraestructura del agente** (no del producto).

### Superpowers — capa de productividad
14 skills core (TDD, debugging, collaboration, write-plan, execute-plan).

Cobertura A*: redundante con ECC en mayoría. Útil para `/brainstorm` Socrático.

---

## Workflow operativo del sandbox

Ciclo central del Framework (visión Julián 2026-05-15): **Analizar → Planificar → Ejecutar → Verificar**.

Mapping a stack ejecutable:

| Fase | Skills primarias del stack |
|---|---|
| Analizar | `speckit-clarify`, `ecc:plan-prd`, `ecc:prp-prd`, `ecc:codebase-onboarding` |
| Planificar | `speckit-plan`, `speckit-tasks`, `ecc:plan`, `ecc:plan-orchestrate`, `ecc:multi-plan` |
| Ejecutar | `speckit-implement`, `ecc:multi-execute`, `ecc:prp-implement`, `ecc:gan-build` |
| Verificar | `ecc:quality-gate`, `ecc:code-review`, `ecc:security-review`, `ecc:verification-loop`, `ecc:judgment-day`, `ecc:harness-audit` |

Memoria continua entre fases: `claude-mem:learn-codebase`, `claude-mem:knowledge-agent`, `claude-mem:mem-search`.

---

## Compliance verificable

Antes de declarar un feature "DONE" en este sandbox:

- [ ] Checklist A1-A25 reviewed con referencia a reglas violadas (si aplica)
- [ ] Anti-patterns evitados (referencia `../../architecture/ANTI-PATRONES.md`)
- [ ] Tests adversariales pasados (A14 + A15)
- [ ] Observability instrumentada (A21)
- [ ] Secrets fuera del código (A22)
- [ ] Deployment seguro planeado (A23)
- [ ] Skills del stack del ecosistema usadas como **ejecutores** del overlay A* — no como sustitutos

---

## Governance

Esta constitution es **derivada del Framework Departamento de Software**. Cambios estructurales requieren:

1. ADR aprobado en `../../decisions/`
2. No desviarse de A1-A25 sin justificación explícita documentada
3. Versionado semántico de esta constitution
4. Sincronización con `../../CLAUDE.md` cuando aplique

Cuando el stack del ecosistema cubre directamente una regla A*, eso **refuerza** la regla (defensa en profundidad — insight Decisión A). NO la sustituye. Si cambiamos de stack o el skill se rompe, la regla A* en el Framework sigue siendo criterio de aceptación.

---

**Sandbox del Framework Departamento — input empírico para ADR-009 (Adopción del Stack + Calibración Tier 1)**

**Cierre Decisión A** (sesión PM 2026-05-20): el overlay declarativo A1-A25 sobrevive a cambios del stack. El stack lo ejecuta hoy; mañana puede ser otro stack. La constitución del proyecto consumidor (esto) hace explícito ese mapping.
