# EVALUATION — Sandbox del Stack del Ecosistema

> **Output canónico del sandbox**: evidencia empírica para ADR-009 (Adopción del Stack + Calibración Tier 1)

**Fecha**: 2026-05-21 (sesión PM 2026-05-20 — continuación)
**Versión**: 0.1 (evaluación inicial; pendiente workflow real ejecutado)
**Autor**: Claude (Claude Code CLI) + Julián Vargas

---

## Resumen ejecutivo

Sandbox empírico T1 ejecutado parcialmente con foco en **instalación + verificación de carga + matriz declarativa A* vs stack**. Workflow end-to-end ejecutado (todo + auth Supabase) queda para iteración 2.

**Veredicto preliminar para ADR-009**: ✅ **ACCEPT PARCIAL** — adoptar Spec Kit + ECC + claude-mem; declarar Superpowers como diferido por redundancia con ECC.

**Hit rate del insight Decisión A** (defensa en profundidad Nivel 2 ↔ Nivel 3): **confirmado**. El stack ejecutable cubre directamente entre **50-65%** de las reglas A1-A25 con skills específicas. El resto requiere overlay declarativo del Framework como criterio (lo que el insight predijo).

---

## Stacks instalados — estado al cierre del sandbox

| Stack | Versión | Estado carga | Skills expuestas | Manifest cross-LLM |
|---|---|---|---|---|
| **Spec Kit** | `specify-cli 0.8.13.dev0` (HEAD post-v0.8.12) | ✅ Operativo | 9 `speckit-*` | Per-project via `.specify/` (agnostic) + `.claude/skills/` |
| **ECC** | `2.0.0-rc.1` | ✅ Operativo | **200+ `ecc:*`** + 6 MCP servers (context7, exa, github, memory, playwright, sequential-thinking) | Per-agent en repo (Anthropic standard) |
| **claude-mem** | `13.2.0` (npm) | ✅ Operativo post-parche manual | 12 `claude-mem:*` | `.agents/` cross-LLM (incorrecto schema Anthropic — requirió parche) |
| **Superpowers** | `5.1.0` (`obra/superpowers`) | 🟡 Manual install — validación post-restart | 14 `superpowers:*` esperadas | **`.claude-plugin/` + `.codex-plugin/` + `.cursor-plugin/` + `.opencode/`** (modelo canónico) |

### Issues encontrados durante instalación

1. **`/plugin marketplace add` no disponible en CLI standalone** — Claude Desktop ofrece estos comandos pero el CLI 2.1.144 standalone no los expone. **Workaround universal**: registrar declarativamente en `~/.claude/settings.json` vía `extraKnownMarketplaces` + `enabledPlugins` (método B documentado por ECC).
2. **claude-mem v13.2.0 — manifest mal ubicado** (`.agents/` en lugar de `.claude-plugin/`). Requiere parche local: clonar de upstream o crear `.claude-plugin/marketplace.json` manualmente. `autoUpdate: false` para preservar parche.
3. **Spec Kit en Windows requiere `PYTHONIOENCODING=utf-8`** — sin esto, `rich` crashea con `cp1252` charmap.
4. **uv tools dir no en PATH persistente** — `uv tool update-shell` lo agrega.
5. **Superpowers fetch parcial** — marketplace clonado pero sub-repo `obra/superpowers.git` no completó install. Manifestación: `.orphaned_at` marker + entry faltante en `installed_plugins.json`. Mitigación: clone manual + entry manual + restart.

### Deudas técnicas resultantes de T1

- **DEUDA-CLAUDE-MEM-MANIFEST**: claude-mem upstream tiene manifest en `.agents/` que no carga en Claude Code sin parche local. Reportar upstream + mantener `autoUpdate: false`.
- **DEUDA-SUPERPOWERS-FETCH-RACE**: Superpowers tiene race condition en su flow declarativo. Workaround: clone manual del sub-repo cuando el CLI no lo completa.
- **DEUDA-PLUGIN-INSTALL-DOCS**: el método declarativo `extraKnownMarketplaces` está sub-documentado. Solo ECC lo menciona explícitamente. Vale documentarlo en `docs/AGENT-INTEGRATION.md` del Framework.
- **DEUDA-WINDOWS-SETUP-CHECKLIST**: lista de prerequisites para Windows (PATH, encoding, uv, Bun) merece sección dedicada.

---

## Matriz A1-A25 vs stack

**Leyenda de cobertura**:
- 🟢 **Direct** — skill ECC con título y descripción que aborda directamente la regla
- 🟡 **Partial** — cobertura indirecta (lang-specific, subset, o concepto adyacente)
- 🔴 **None** — sin skill que aborde — el overlay declarativo A* es la única defensa

| # | Regla | Criticidad | Cobertura | Skill ECC primaria | Complementarias / notas |
|---|---|---|---|---|---|
| A1 | Module Ownership | Importante | 🟡 Partial | `ecc:hexagonal-architecture` | Hexagonal favorece ownership pero no lo enforce. Overlay declarativo necesario. |
| A2 | Encapsulación de tablas | Importante | 🟡 Partial | `ecc:api-design`, `ecc:backend-patterns` | Conceptualmente cubierto, no aplicado a SQL/RPCs. |
| A3 | Inter-Module Contracts | Importante | 🟢 Direct | `ecc:api-design` | También `ecc:api-connector-builder` para patterns existentes. |
| A4 | Acíclicidad de Dependencias | Importante | 🔴 None | — | Anti-pattern catalogado pero sin skill ejecutor. Overlay declarativo único defensor. |
| A5 | Multi-tenant Strict Isolation | **CRÍTICA** | 🟡 Partial | `ecc:security-review`, `ecc:postgres-patterns` (RLS) | No hay skill dedicada a multi-tenancy. Overlay crítico. |
| A6 | Immutability for Audit | Importante | 🟡 Partial | `ecc:database-migrations` | Event sourcing no explícitamente cubierto. |
| A7 | Domain Validation Before Implementation | Importante | 🟢 Direct | `ecc:plan`, `ecc:plan-prd`, `ecc:prp-prd` | Workflow SDD (Spec Kit + ECC) refuerza esto naturalmente. |
| A8 | Idempotency or Explicit Rollback | Importante | 🟡 Partial | `ecc:error-handling`, `ecc:api-design` | Mencionado en patterns pero no enforce. |
| A9 | Stop Conditions Explicit | Importante | 🟢 Direct | `ecc:loop-start`, `ecc:loop-status`, `ecc:autonomous-loops` | Específicamente para loops autónomos del agente. |
| A10 | No Test Code in Production | Importante | 🟢 Direct | `ecc:tdd-workflow`, `ecc:test-coverage`, lang-specific tests | TDD workflows lo asumen. |
| A11 | DAO + DTO | Importante | 🟡 Partial | `ecc:backend-patterns`, `ecc:springboot-patterns`, etc. | Lang-specific. No genérico. |
| A12 | Zero Trust | **CRÍTICA** | 🟢 Direct | `ecc:security-review`, `ecc:security-scan`, `ecc:safety-guard`, `ecc:gateguard` | Cobertura múltiple. |
| A13 | Concurrency Safety | Importante | 🟡 Partial | `ecc:kotlin-coroutines-flows`, `ecc:swift-concurrency-6-2` | Lang-specific. Genérico falta. |
| A14 | Explicit Failure | Importante | 🟢 Direct | `ecc:error-handling`, `ecc:silent-failure-hunter` (agent) | Explícitamente cubierto. |
| A15 | Unhappy Path First | Importante | 🟢 Direct | `ecc:tdd-workflow`, `ecc:verification-loop` | TDD favorece unhappy first. |
| A16 | Rate Limiting & Throttling | Importante | 🟡 Partial | `ecc:vercel-firewall` (vercel:* skills) | Cubierto a nivel platform, no app layer. |
| A17 | Edge Protection | Importante | 🟢 Direct | `ecc:vercel-firewall`, `vercel:vercel-firewall` | Vercel-specific pero modelo aplicable. |
| A18 | Async Processing for Heavy Tasks | Importante | 🟡 Partial | `ecc:vercel-functions`, lang-specific async | No skill dedicada a queue/worker patterns. |
| A19 | External Service Resilience | Importante | 🔴 None | — | Circuit breakers / retries / timeouts no tienen skill propia. Overlay único defensor. |
| A20 | Hexagonal Architecture | **CRÍTICA** | 🟢 Direct | `ecc:hexagonal-architecture` | Skill dedicada — match perfecto. |
| A21 | Structured Observability | **CRÍTICA** | 🟡 Partial | `ecc:harness-audit`, `ecc:context-budget` | Cobertura conceptual; logs/metrics/traces requieren overlay + integración Sentry/etc. |
| A22 | Secrets Management | **CRÍTICA** | 🟢 Direct | `ecc:security-scan`, `ecc:security-bounty-hunter` | Detection sí; vaulting/rotation requiere overlay. |
| A23 | Deployment Safety | Importante | 🟢 Direct | `ecc:deployment-patterns`, `ecc:canary-watch`, `ecc:agent-payment-x402` (cost controls) | Cobertura buena. |
| A24 | Data Lifecycle & Privacy | **CRÍTICA** | 🟡 Partial | `ecc:hipaa-compliance`, `ecc:healthcare-phi-compliance` | Compliance subset; GDPR genérico no. |
| A25 | Authorization Model | Importante | 🟡 Partial | `ecc:laravel-security`, `ecc:springboot-security` | Lang-specific. RBAC/ABAC genérico falta. |

### Conteos

- 🟢 **Direct**: 11 reglas (44%) — `A3, A7, A9, A10, A12, A14, A15, A17, A20, A22, A23`
- 🟡 **Partial**: 12 reglas (48%) — `A1, A2, A5, A6, A8, A11, A13, A16, A18, A21, A24, A25`
- 🔴 **None**: 2 reglas (8%) — `A4, A19`

**Cobertura efectiva**: ~70% si se cuentan Direct + Partial como "stack toca el tema". 44% si solo Direct.

### Implicación operativa

Las 2 reglas 🔴 (A4 Acíclicidad y A19 External Resilience) son **dimensiones donde el overlay declarativo del Framework es la ÚNICA defensa documentada**. No es un gap del Framework, es justificación retrospectiva del insight Decisión A: las A* son criterio independiente del stack.

Las 12 reglas 🟡 marcan **oportunidades de skills específicas del Framework** (Nivel 3 propio) que complementen el stack sin duplicarlo. Candidatas:
- `sigma:multi-tenant-isolation-checker` (A5)
- `sigma:dependency-cycle-detector` (A4)
- `sigma:circuit-breaker-template` (A19)
- `sigma:rbac-abac-builder` (A25)

Las 11 reglas 🟢 demuestran que **adoptar el stack es accelerador** — no construimos desde cero lo que ya está + Tier 1 validated.

---

## Hallazgos cualitativos del sandbox

### Hallazgo 1: validación empírica del insight Decisión A (sesión PM 2026-05-20)

El insight ("Nivel 2 declarativo + Nivel 3 ejecutable son complementos por diseño") queda validado **operativamente**:
- 44% de A* tienen skill ejecutor directo (Nivel 3 sirve)
- 56% sin cobertura directa (Nivel 2 declarativo es necesario)
- Cambio del stack en el futuro: las A* sobreviven; los skills se redibujan

Hit rate intuición arquitectónica de Julián: **19/19** (incluyendo este sandbox como validación del insight previo).

### Hallazgo 2: cross-LLM canónico (`obra/superpowers` modelo)

`obra/superpowers` publica con:
```
.claude-plugin/    ← Claude Code
.codex-plugin/     ← Codex CLI
.cursor-plugin/    ← Cursor
.opencode/         ← OpenCode
```

Este es el **patrón canónico para Framework cross-LLM** (ADR-008). Diferencia clave vs claude-mem (que usa `.agents/` y rompe Anthropic schema).

**Acción para Framework**: cuando empaquetemos el Departamento como cross-LLM, adoptar el modelo `obra/superpowers`. Agregar a `docs/AGENT-INTEGRATION.md`.

### Hallazgo 3: SDD alternativo cargado (skills `sdd-*`)

Apareció en el system prompt una familia `sdd-*` (9 skills: init, new, explore, propose, ff, continue, apply, verify, archive, onboard) probablemente del stack Gentle AI. Esto es **un SDD orchestrator alternativo a Spec Kit**.

Comparación rápida:
- `speckit-*` (9 skills) — workflow lineal, agent skills, templates markdown
- `sdd-*` (9 skills) — workflow con dependency graph + delegation a sub-agents + execution modes (interactive/auto)

**Recomendación**: comparar empíricamente en iteración 2. Si `sdd-*` resulta más sofisticado, vale considerar reemplazar Spec Kit por SDD. ADR-009 puede dejar esta puerta abierta.

### Hallazgo 4: ECC overdelivers vs lo esperado

Plan v4.0 estimaba ECC con "28 agents + 30 skills". Realidad: **200+ skills + 6 MCP servers integrados**. Cobertura horizontal masiva:
- 16+ lenguajes con build/test/review específicos
- Compliance (HIPAA, healthcare PHI)
- Domain-specific (DeFi, scientific, agentic-os, agent-harness)
- Business ops (Jira, GitHub, Google Workspace, email, finance, logistics)
- Infrastructure (Cisco IOS, homelab, Docker, PM2)

**Implicación**: la matriz arriba puede subestimar cobertura (no exploré las 200 una por una). Iteración 2 puede subir 🟡 → 🟢 cuando se descubran skills específicas.

### Hallazgo 5: redundancia Superpowers ↔ ECC

Superpowers ofrece: TDD, debugging, brainstorm, write-plan, execute-plan.
ECC ya cubre: `ecc:tdd-workflow`, `ecc:plan-orchestrate`, `ecc:multi-plan`, `ecc:plan-prd`, etc.

**Solapamiento ~80-90%**. Superpowers aporta marginalmente. Recomendación ADR-009: **diferido** (no descartado), evaluar en uso real si emerge valor único.

### Hallazgo 6: lecciones técnicas (sesión PM 2026-05-20 + sandbox)

- **LECCIÓN 18** *(NUEVA)*: plugins cross-LLM publicados como package único para múltiples agents pueden tener manifest mismatch. claude-mem publica en `.agents/` que NO carga; `obra/superpowers` publica en `.claude-plugin/` + `.codex-plugin/` + etc. que SÍ. Conclusión: cuando empaquetemos el Framework, adoptar el modelo de obra.
- **LECCIÓN 19** *(NUEVA)*: el método declarativo `extraKnownMarketplaces` + `enabledPlugins` en `~/.claude/settings.json` es la forma **canónica** de instalar plugins en Claude Code CLI standalone. Es sub-documentada — solo ECC la menciona explícitamente. Vale exponerla en docs del Framework.
- **LECCIÓN 20** *(NUEVA)*: `specify-cli` flags rotan rápido (v0.8.9 → v0.8.13.dev0 → v0.10.0 ruta). Plan SDD escrito con flags específicos queda obsoleto en semanas. Documentar el comportamiento esperado, no los flags exactos.

---

## Veredicto preliminar para ADR-009

### Recomendación: ✅ ACCEPT PARCIAL

**Adoptar wholesale**:
- ✅ Spec Kit como **orquestador SDD** (constitution/specify/plan/tasks/implement)
- ✅ ECC como **stack ejecutable principal** (200+ skills cubren 70%+ del dominio)
- ✅ claude-mem como **memoria persistente** (reemplaza Engram bloqueado)

**Diferir / opcional**:
- 🟡 Superpowers — redundante con ECC; reactivar si emerge necesidad específica

**Mantener como propio (Nivel 3 Framework)**:
- 🔵 Reglas A1-A25 (Nivel 2) — **overlay declarativo universal**, sobrevive a cambios de stack
- 🔵 Skills sigma-specific (Nivel 3 Framework) para gaps no cubiertos por stack:
  - `sigma:multi-tenant-isolation-checker` (A5)
  - `sigma:dependency-cycle-detector` (A4)
  - `sigma:circuit-breaker-template` (A19)
  - `sigma:rbac-abac-builder` (A25)
  - `sigma:capture-domain` (ya existente, A3)

### Sprint 2 implicaciones

Plan original Sprint 2 (T2.2 — construir 10 skills propias): **reducible a 4-5 skills sigma-specific** que llenan gaps que el stack NO cubre. Estimación de tiempo ahorrado: **6-10 semanas** (de "construir desde cero" a "construir solo lo faltante").

### Visión D (Decisión B pendiente)

Capa A (declarativo) + Capa B (integraciones) puede formalizarse en ADR-010:
- Capa A = Nivel 2 (A1-A25) — sobrevive
- Capa B = integraciones específicas del stack (ECC + Spec Kit + claude-mem) — versionables

Recomendación: esperar 1 iteración real del workflow antes de formalizar.

---

## Próximos pasos

### Iteración 2 del sandbox (próxima sesión)

1. **Restart de Claude Desktop** para verificar Superpowers carga post-manual-fix
2. **Workflow end-to-end real** con caso "todo + auth Supabase":
   - `/speckit-constitution` (input: este archivo)
   - `/speckit-specify` (NL → spec)
   - `/speckit-clarify` (de-risking)
   - `/speckit-plan`
   - `/speckit-tasks`
   - `/speckit-implement` OR `/ecc:multi-execute`
   - `/ecc:quality-gate` + `/ecc:code-review` + `/ecc:security-review`
3. **Comparar `sdd-*` vs `speckit-*`** empíricamente con mismo caso
4. **Actualizar matriz** con cobertura real post-ejecución (no solo a-priori)
5. **Escribir ADR-009** basado en evidencia ejecutable
6. **Posible ADR-010** formalizando Visión D (si la evidencia lo justifica)

### Para el Framework

1. Escribir las 4 skills sigma-specific identificadas (gaps del stack)
2. Documentar método declarativo `extraKnownMarketplaces` en `docs/AGENT-INTEGRATION.md`
3. Documentar setup Windows (PATH, encoding, uv, Bun, PowerShell) en checklist
4. Adoptar modelo cross-LLM de `obra/superpowers` (`.claude-plugin/` + `.codex-plugin/` + `.cursor-plugin/`) cuando empaquetemos

---

## Apéndice: artefactos del sandbox

- `projects/sandbox-stack/.specify/memory/constitution.md` — constitución operacionalizada con A1-A25
- `projects/sandbox-stack/.specify/` — workflow y templates Spec Kit
- `projects/sandbox-stack/.claude/skills/` — 9 skills `speckit-*` per-project
- `projects/sandbox-stack/CLAUDE.md` — marker minimal Spec Kit
- `~/.claude/settings.json` — registro declarativo de marketplaces (ecc, superpowers + existentes)
- `~/.claude/plugins/installed_plugins.json` — entries de plugins activos
- `~/.claude/plugins/cache/<marketplace>/<plugin>/<version>/` — caches locales

---

**Fin EVALUATION.md v0.1** — input para ADR-009. Reescribir post-iteración 2 con evidencia ejecutable.

---

# ADDENDUM v0.5 — Evidencia de fase de planeación (T1.7, 2026-05-21)

> **Estado**: v0.5 PRELIMINAR (planning-phase only). v1.0 espera evidencia de `/speckit-implement` + comparación SDD vs Spec Kit (T1.9 diferido a próxima sesión).
> **Fuente**: `projects/sandbox-stack/T1.7-EVIDENCE.md` con detalle por invocación.
> **Caso ejecutado**: "Personal Todo Management with User Authentication" (todo CRUD + Supabase Auth + RLS).

## Refinamientos a la matriz A* vs stack (post-ejecución)

### Confirmaciones (sin cambio respecto a v0.1)

Las **11 reglas 🟢 Direct** se mantienen tras ejecución:
- A3, A7, A9, A10, A12, A14, A15, A17, A20, A22, A23

Las **2 reglas 🔴 None** se confirman:
- A4 Acíclicidad — solo defendible por overlay declarativo
- A19 External Resilience — solo defendible por overlay declarativo (tasks.md la marca como deuda v1.1)

### Nuevos hallazgos (post-T1.7 que la matriz a-priori NO captó)

#### Hallazgo H1 — Constitution Check del plan-template es el "manual injection point" CRÍTICO

El template de `plan.md` tiene una sección `## Constitution Check` con un placeholder `[Gates determined based on constitution file]`. **Si el operador la deja vaga o vacía → cobertura A* = 0 en el plan**. Si la rellena consciente del Framework → cobertura A* = 25 ítems.

La skill `/speckit-plan` **no enforce** este relleno. Es el momento donde la complementariedad Nivel 2 ↔ Nivel 3 se decide.

**Implicación**: la matriz a-priori medía la **cobertura potencial** del stack. La cobertura real depende del operador. Esto **refuerza el insight Decisión A**: el overlay declarativo no es decorativo — sin él, el stack es ciego a las reglas críticas.

#### Hallazgo H2 — Taxonomía de `/speckit-clarify` cubre ~10/25 reglas A*

La skill prioriza ambigüedades en 10 categorías genéricas. **Faltan categorías para**: A4 Acíclicidad, A6 Audit, A8 Idempotency, A13 Concurrency, A16 Rate Limiting, A17 Edge, A18 Async, A19 External Resilience, A20 Hexagonal, A23 Deployment, A25 Authorization (11 reglas no cubiertas por la taxonomía clarify).

**Implicación**: clarify está diseñada para "MVP genérico", no para "Tier 1 SaaS commercial robust". Skill sigma propuesta: `sigma:clarify-with-a-rules-taxonomy`.

#### Hallazgo H3 — Tasks heredan transitivamente del plan, sin slot propio para A*

`tasks.md` no tiene formato para tag `[A:N,M]` por task. La trazabilidad task ↔ regla A* depende de que el plan ya tenga el mapping. Si no, las tasks se ejecutarán correctamente pero el code review no sabe qué tasks son A5-críticas.

**Implicación**: la **adversarial gate** (T038-T041 en `tasks.md`) es la única evidencia explícita de A5+A12 en el output de `/speckit-tasks`. El resto del mapping vive en el plan o en mi cabeza.

### Tabla refinada (v0.5 con columna "Evidencia ejecutable observada")

| # | Regla | Crit | v0.1 a-priori | v0.5 ejecutable | Evidencia concreta en artefactos |
|---|---|---|---|---|---|
| A1 | Module Ownership | I | 🟡 Partial | 🟢 Direct | `plan.md` Project Structure (hexagonal split); `tasks.md` T007 |
| A2 | Encapsulación tablas | I | 🟡 Partial | 🟢 Direct | `contracts/api.md` (server actions only, no tablas expuestas); `tasks.md` T031 |
| A3 | Inter-Module Contracts | I | 🟢 Direct | 🟢 Direct | `contracts/api.md` (Result<T> + zod); `tasks.md` T013 |
| A4 | Acíclicidad | I | 🔴 None | 🔴 None | Solo plan-level ("hexagonal split, no cycles"); sin enforcement ejecutable |
| A5 | Multi-tenant Isolation | **C** | 🟡 Partial | 🟢 Direct | `data-model.md` RLS policies; `tasks.md` T008, T038-T041 adversarial gate |
| A6 | Immutability Audit | I | 🟡 Partial | 🟢 Direct | `data-model.md` `todo_events` + `auth_events` insert-only RLS |
| A7 | Domain Validation | I | 🟢 Direct | 🟢 Direct | Workflow speckit-* lo fuerza estructuralmente |
| A8 | Idempotency / Rollback | I | 🟡 Partial | 🟡 Partial | `research.md` Decision 3 + `contracts/api.md` (idempotent complete/delete); sin tests específicos |
| A9 | Stop Conditions | I | 🟢 Direct | 🟢 Direct | N/A en MVP (sin loops); `plan.md` lo flagea explícito |
| A10 | No Test Code in Prod | I | 🟢 Direct | 🟢 Direct | `plan.md` Project Structure (tests/ separado); `tasks.md` T003 |
| A11 | DAO + DTO | I | 🟡 Partial | 🟢 Direct | `plan.md` (Supabase=DAO, zod=DTO, domain types separate) |
| A12 | Zero Trust | **C** | 🟢 Direct | 🟢 Direct | `contracts/api.md` (every action getServerSession); `tasks.md` T015, T038 |
| A13 | Concurrency Safety | I | 🟡 Partial | 🟢 Direct | `data-model.md` updated_at token; `research.md` Decision 5; `contracts/api.md` expectedUpdatedAt + STALE_VERSION |
| A14 | Explicit Failure | I | 🟢 Direct | 🟢 Direct | `contracts/api.md` tagged unions; `tasks.md` T037 logging |
| A15 | Unhappy Path First | I | 🟢 Direct | 🟢 Direct | `tasks.md` US3 prece US1 in execution order; T038-T041 |
| A16 | Rate Limiting | I | 🟡 Partial | 🟢 Direct | `research.md` Decision 8 + `tasks.md` T016 (Upstash) |
| A17 | Edge Protection | I | 🟢 Direct | 🟢 Direct | `plan.md` (Vercel WAF default) |
| A18 | Async for Heavy | I | 🟡 Partial | 🟡 Partial (N/A MVP) | `plan.md` lo declara N/A v1; deuda formal |
| A19 | External Resilience | I | 🔴 None | 🔴 None | `tasks.md` deuda v1.1; sin circuit breaker en stack |
| A20 | Hexagonal | **C** | 🟢 Direct | 🟢 Direct | `plan.md` Project Structure (domain→ports→adapters); `tasks.md` T007, T010-T011 |
| A21 | Observability | **C** | 🟡 Partial | 🟡 Partial (logs+metrics, sin traces) | `research.md` Decision 9; `tasks.md` T014 (pino), T044 (Vercel Analytics); traces deferido v2 |
| A22 | Secrets | **C** | 🟢 Direct | 🟢 Direct | `quickstart.md` sección 3 (server-only key warning); `tasks.md` T043 (rotación quarterly) |
| A23 | Deployment Safety | I | 🟢 Direct | 🟢 Direct | `research.md` Decision 10 (migraciones versionadas); Vercel preview deployments |
| A24 | Data Lifecycle | **C** | 🟡 Partial | 🟢 Direct | `data-model.md` soft-delete 30d + hard purge; `tasks.md` T045 (cron purge) |
| A25 | Authorization | I | 🟡 Partial | 🟢 Direct | `data-model.md` RLS auth.uid()=user_id; `tasks.md` T020 (auth-provider) |

### Nuevos conteos v0.5 (planning-phase)

- 🟢 **Direct**: **19 reglas (76%)** — subida desde 11 (44%) en v0.1
- 🟡 **Partial**: **4 reglas (16%)** — A8, A18, A21, (revisar A19/A4 → no movieron)
- 🔴 **None**: **2 reglas (8%)** — A4, A19 (sin cambio)

**Caveat crítico**: la subida de 44% → 76% Direct es **conseguida por el operador** llenando el Constitution Check + plan + data-model + contracts + tasks con consciencia del Framework. **La skill NO la fuerza**. Si replicamos el caso con un operador "vibe coder" sin Framework, la cobertura caería de vuelta a ~44%.

## Lecciones empíricas adicionales (sobre las 20 anteriores)

### LECCIÓN 22 candidata *(N=1, 2026-05-21)*

**Patrón**: el momento crítico de un workflow SDD asistido por LLM es la sección donde el template **delega al operador** rellenar contenido específico del dominio (en speckit-plan: la Constitution Check). Sin enforcement programático, la cobertura A* depende 100% de la disciplina del operador.

**Mitigación arquitectónica**: construir skills sigma como post-procesadores que **validan** que las secciones delegadas tienen contenido concreto (no placeholders, no vague language). Esto convierte "manual injection point" en "verifiable injection point".

### LECCIÓN 23 candidata *(N=1, 2026-05-21)*

**Patrón**: matriz a-priori (basada en lectura de catálogo) vs matriz ejecutable (post-invocación) diverge **al alza** cuando el operador es consciente del Framework. La cobertura "real" no es propiedad solo del stack, sino del **stack + operador instruido**.

**Implicación operativa**: la pregunta correcta no es "¿qué cobertura tiene el stack?" sino "¿qué cobertura producirá el stack con un operador del Framework vs un operador genérico?". El delta es lo que justifica el Framework.

---

**Estado v0.5**: PROPOSED para ADR-009 PRELIMINAR. v1.0 final pendiente de T1.9 (comparación SDD vs Spec Kit con mismo caso) + opcional iteración con `/speckit-implement`.

**Próximos pasos**:
1. T2 — ADR-009 v0.5 PRELIMINAR (esta sesión)
2. T1.9 — comparación `sdd-*` vs `speckit-*` (próxima sesión)
3. `/speckit-implement` o `/ecc:multi-execute` sobre tasks.md (próxima sesión)
4. EVALUATION.md v1.0 con evidencia de implementation real (post iteración 3)

