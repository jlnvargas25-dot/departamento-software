# ADR-009: Adopción del Stack del Ecosistema + Calibración Tier 1

**Status**: PROPOSED v0.5 PRELIMINAR (planning-phase evidence only; pending T1.9 comparación SDD↔Spec Kit + iteración con `/speckit-implement`)
**Date**: 2026-05-21
**Sprint**: Sprint 1 — Sandbox del stack (iteración 2, fase planeación)
**Related**: ADR-006 (Niveles + SOLID), ADR-007 (Framework vs proyectos), ADR-008 (Cross-LLM), ADR-010 (Skill Routing via Foreman — depende de este ADR)

---

## Contexto

El Departamento de Software es un Framework anti-alucinación. Tras la implementación de A1-A25 (Nivel 2 declarativo universal, 25 reglas + 36 anti-patterns) y antes de construir skills/MCP servers propios, se ejecutó un **sandbox empírico T0+T1** en `projects/sandbox-stack/` para validar la adopción del stack del ecosistema (Spec Kit + ECC + claude-mem + Superpowers).

Insight previo a esta sesión (Decisión A, sesión PM 2026-05-20, validada empíricamente sesión 2026-05-21):

> Las reglas A* (Nivel 2 declarativo) y los skills del stack (Nivel 3 ejecutable) **NO son sustitutos sino complementos por diseño**. Las A* funcionan como overlay declarativo universal que sobrevive a cambios de stack; los skills son la implementación-de-momento ejecutable del overlay.

Esta sesión (2026-05-21) ejecutó **iteración 2 del sandbox** con la cadena T1.6 → T1.7 → T1.8 sobre el caso "Personal Todo Management with User Authentication (Supabase + Vercel)", produciendo 8 artefactos vía `/speckit-constitution` → `/speckit-specify` → `/speckit-clarify` → `/speckit-plan` → `/speckit-tasks`.

**Evidencia consolidada**: `projects/sandbox-stack/T1.7-EVIDENCE.md` (5 invocaciones con findings por skill) y `projects/sandbox-stack/EVALUATION.md` v0.5 (matriz A* refinada post-ejecución).

---

## Estado de las decisiones componentes

### SD-1 — Spec Kit como orquestador del proceso SDD

**Status**: ✅ **ACCEPT** (planning-phase evidencia suficiente)

- **Qué adoptamos**: 9 skills `speckit-*` como backbone del workflow Analizar→Planificar→Ejecutar→Verificar (parcial).
- **Evidencia ejecutable**: cadena specify→clarify→plan→tasks generó artefactos coherentes (`spec.md` con 3 stories priorizadas, `plan.md` con Constitution Check estructural, `data-model.md` con RLS policies concretas, `contracts/api.md` con tagged Result<T>, `tasks.md` con 47 tareas en 6 phases con dependency graph y parallel opportunities).
- **Cobertura A* directa**: 0 reglas — Spec Kit es orquestador del proceso, no ejecutor de reglas.
- **Gap principal**: el `Constitution Check` del plan-template es un **slot delegado al operador** — la skill no enforce su relleno. Si se deja vago o vacío, la cobertura A* en el plan = 0. Si el operador lo llena consciente del Framework, cobertura plan ≈ 25/25.

### SD-2 — Everything Claude Code (ECC) como stack ejecutable principal

**Status**: 🟡 **ACCEPT pendiente de evidencia /implement** (planning-phase no ejercitó ECC en su mayoría)

- **Qué adoptamos provisionalmente**: 200+ skills `ecc:*` + 6 MCP servers (context7, exa, github, memory, playwright, sequential-thinking).
- **Cobertura A* directa observada en planning-phase**: 11/25 directa (A3, A7, A9, A10, A12, A14, A15, A17, A20, A22, A23) confirmadas; 12 Partial; 2 None (A4, A19).
- **Pendiente de iteración con `/ecc:multi-execute` + `/ecc:code-review` + `/ecc:security-review` sobre `tasks.md`** para validar la cobertura ejecutable real (no a-priori).
- **Riesgo identificado**: la cobertura a-priori subestima oportunidades (200+ skills no exploradas una por una) y simultáneamente sobreestima la cobertura "automática" (skills requieren operador instruido para activar la combinación correcta).

### SD-3 — claude-mem como memoria persistente cross-sesión

**Status**: ✅ **ACCEPT con DEUDA upstream**

- **Qué adoptamos**: claude-mem v13.2.0 (sucesor funcional de Engram bloqueado por SAC).
- **Restricción operativa**: requiere parche local (`autoUpdate: false`) hasta que upstream resuelva manifest mismatch (`.agents/` vs `.claude-plugin/marketplace.json`).
- **Cobertura A* directa**: 0 — claude-mem es infraestructura del agente, no ejecutor de reglas del producto.
- **Valor**: continuidad de sesión + acumulación de hallazgos cross-sesión (LECCIÓN 16 prevención + DEUDAS tracking).

### SD-4 — Superpowers como capa de productividad

**Status**: 🟡 **DEFERRED** (no descartado; reactivar si emerge necesidad)

- **Solapamiento ~80-90%** con ECC en TDD, debugging, plan, execute-plan, code-review.
- **Valor único marginal**: `superpowers:brainstorming` (Socrático estructurado), `superpowers:writing-skills`, `superpowers:dispatching-parallel-agents`.
- **Decisión operativa**: mantener instalado (parche manual ya aplicado, T1.6 confirmó carga), pero NO documentar en la cadena de adopción wholesale. Si en uso emerge gap que sólo Superpowers llena, promover a ACCEPT en ADR posterior.

### SD-5 — Skills sigma propias para gaps del stack (Nivel 3 Framework)

**Status**: ✅ **ACCEPT diseño**; construcción en Sprint 2 post-ADR-009.

Basado en la evidencia de T1.7, se identifican **8 candidatos** (de los cuales 4-5 son MVP):

**MVP Sprint 2 (4 skills)**:
1. **`sigma:operationalize-constitution`** — sync bidireccional Framework (A1-A25) ↔ `.specify/memory/constitution.md` de proyectos consumidores. Cierra gap H1 + gap de `/speckit-constitution` ante constitution ya operacionalizada.
2. **`sigma:enforce-constitution-check`** — post-procesador que valida que cada regla del constitution.md tiene una línea concreta (no placeholder, no vague) en `plan.md`. Cierra gap H1 del Constitution Check delegado.
3. **`sigma:multi-tenant-isolation-checker`** — verifica RLS policies + adversarial tests para A5 (CRÍTICA). Cierra gap A5 Partial.
4. **`sigma:dependency-cycle-detector`** — verifica grafo de imports en hexagonal layouts. Cierra gap A4 None.

**Diferido v1.1 (4 skills opcionales)**:
5. `sigma:circuit-breaker-template` — A19 (gap None confirmado).
6. `sigma:rbac-abac-builder` — A25 (gap Partial confirmado).
7. `sigma:annotate-spec-with-a-rules` — mapping FR/SC ↔ A1-A25 automático.
8. `sigma:clarify-with-a-rules-taxonomy` — taxonomía expandida a 25 categorías.

---

## Decisión consolidada

✅ **ACCEPT PARCIAL** del stack del ecosistema:

| Componente | Status v0.5 | Razón |
|---|---|---|
| Spec Kit (`speckit-*`) | ACCEPT | Orquestador SDD valida estructura/proceso |
| ECC (`ecc:*`) | ACCEPT pendiente /implement | 200+ skills + 6 MCP; cobertura A* preliminar buena |
| claude-mem | ACCEPT con DEUDA upstream | Memoria persistente reemplaza Engram bloqueado |
| Superpowers | DEFERRED | Solapamiento alto con ECC; revisitar si emerge gap único |
| Skills sigma propias | ACCEPT diseño, build Sprint 2 | 4 MVP + 4 v1.1 opcionales |

🔵 **Nivel 2 Framework (A1-A25) sigue siendo única fuente de verdad arquitectónica.** El stack ejecuta donde puede; donde no puede o donde el operador no lo invoca correctamente, el overlay declarativo es la única defensa.

---

## Consecuencias

### Positivas

1. **Aceleración Sprint 2**: el plan original estimaba 10 skills sigma. ADR-009 reduce a 4-5 MVP. Ahorro estimado: **6-10 semanas** de "construir desde cero" a "construir solo lo faltante".
2. **Visión C confirmada**: el Departamento es **curador + calibrador + overlay arquitectónico declarativo**, no constructor de stack completo desde cero.
3. **Defensa en profundidad funcionando**: el sandbox demostró que el overlay declarativo (cuando el operador lo aplica al Constitution Check) sube la cobertura A* del 44% al 76%.
4. **Cross-LLM-ready**: modelo `obra/superpowers` (`.claude-plugin/` + `.codex-plugin/` + `.cursor-plugin/` + `.opencode/`) adoptable cuando empaquetemos. Conexión con ADR-008.

### Negativas

1. **Dependencia de stack externo**: el Framework hereda DEUDA-CLAUDE-MEM-MANIFEST + DEUDA-SUPERPOWERS-FETCH-RACE + versiones rotantes (LECCIÓN 20).
2. **Operador instruido es prerrequisito**: el delta 44%→76% Direct lo aporta el operador del Framework. Sin entrenamiento o sin skills sigma de enforcement, la cobertura cae a a-priori.
3. **Riesgo de divergencia**: si Spec Kit cambia su template (Constitution Check renombrado, taxonomía clarify alterada), las skills sigma post-procesadoras pueden romperse — re-tests obligatorios en cada bump del stack.
4. **Cobertura ejecutable real aún no medida** (este ADR es v0.5 PRELIMINAR; `/speckit-implement` no ejercido).

### Riesgos abiertos para v1.0

- **R1**: T1.9 (comparación `sdd-*` vs `speckit-*`) puede revelar que el alternativo SDD es mejor backbone — promovería de ACCEPT speckit a ACCEPT sdd (o hybrid).
- **R2**: iteración `/speckit-implement` puede revelar fricciones irreconciliables ECC ↔ Spec Kit ↔ claude-mem en flujo real, reduciendo ACCEPT a "Spec Kit + ECC sin chain integration".
- **R3**: las 4 skills sigma MVP pueden encontrar enforcement points que Spec Kit no permite extender — pivotar a soluciones alternativas.

---

## Alternativas consideradas y rechazadas

### Alternativa A — REJECT total y construir desde cero

**Rechazada**: contradice 7° principio (meta-producto recursivo). Sin el stack, el Sprint 2 estaría construyendo lo que ECC ya tiene (200+ skills) por meses sin valor agregado. El delta del Framework (overlay A1-A25 + 4-5 skills sigma) NO se obtiene mejor partiendo de cero.

### Alternativa B — ACCEPT WHOLESALE sin overlay

**Rechazada**: violaría Decisión A. Sin overlay declarativo, el Framework dejaría de ser "harness anti-alucinación senior" y sería "una colección instalada de skills upstream". Sin diferenciador.

### Alternativa C — ACCEPT PARCIAL con TODAS las skills sigma diseñadas (10)

**Rechazada por scope**: las 4 sigma MVP cubren los gaps **CRÍTICOS** (A4, A5, Constitution Check enforcement, constitution sync). Las otras 4 son nice-to-have. Construir las 10 antes de validar las 4 viola el 6° principio (descubrir antes de ejecutar).

### Alternativa D — Esperar T1.9 + `/implement` antes de cualquier ADR

**Rechazada por costo de oportunidad**: la fase de planeación ya da evidencia suficiente para los SD-1, SD-3, SD-4, SD-5. Sólo SD-2 queda pendiente de iteración. Bloquear el ADR completo por SD-2 retrasa Sprint 2 sin valor agregado.

---

## Validación pendiente (PROPOSED v0.5 → ACCEPTED v1.0)

Para promover este ADR de PROPOSED v0.5 a ACCEPTED v1.0:

- [x] **T1.9**: ejecutar el mismo caso (todo+auth Supabase) con `sdd-*` y comparar lado a lado vs `speckit-*`. ✅ COMPLETADO 2026-05-21 PM continuación 2. **Decisión D resuelta**: backbone híbrido (speckit-* default + sdd-* escalation). Evidencia: `projects/sandbox-stack/T1.9-EVIDENCE.md` v0.2 EMPIRICAL.
- [ ] **Iteración 3**: ejecutar `/speckit-implement` o `/ecc:multi-execute` sobre `tasks.md` y medir cobertura ejecutable real de las 11 reglas Direct.
- [ ] **Build de 4 skills sigma MVP** y validar que cierran los gaps identificados (H1, H2, A4, A5).
- [ ] **Reescribir EVALUATION.md v0.5 → v1.0** con evidencia de implementación real.
- [ ] **Re-medir cobertura A* post-implementation** y comparar con la cobertura post-planning de v0.5.

**Si cualquier validation falla** → este ADR baja a REJECTED + redacción de ADR-009-bis con la decisión refinada.

### Addendum T1.9 (2026-05-21 PM continuación 2)

**Decisión D — Backbone SDD resuelto como híbrido**:
- **Default**: speckit-* (velocidad, cost-aware ~30k tokens vs ~140k de sdd-*)
- **Escalation**: sdd-* cuando aplica matriz F1-F10 de T1.9-EVIDENCE.md (multi-domain, DAG explícito, A20 hexagonal crítico, operador no instruido del Framework)
- **Refinamiento**: las 4 sigma MVP (`enforce-constitution-check` en particular) cierran el gap principal de speckit-* (Constitution Check manual), llevando speckit-* a paridad de cobertura A* a fracción del costo

**Nuevas evidencias empíricas (N=1 c/u — 5 lecciones candidatas 24-28)**:
- Convergencia 47 tasks en ambos workflows sobre el mismo caso → case dimension drives task count
- sdd-* genera 2.5x más contenido (2378 vs 928 líneas) pero arranca 3x más lento (45s vs 15s)
- sdd-* tiene capability decomposition emergent vía `domains:` block del config.yaml (sesgo estructural hacia A20)
- Sub-agent `sdd-explore` no tiene tool Write — DEUDA candidata `DEUDA-SDD-EXPLORE-NO-WRITE`
- Skill mandatory rules pueden override instrucciones del orquestador — DEUDA candidata para isolation en sandboxes

**Status**: sigue PROPOSED. Promoción a ACCEPTED requiere iteración 3.

---

## Conexiones

- **ADR-006** (Niveles 1-5 + SOLID): este ADR es el punto donde Nivel 3 (ejecutable) se compone del stack adoptado. Confirma que Nivel 2 (A1-A25) es independiente.
- **ADR-007** (Framework vs proyectos): el sandbox `projects/sandbox-stack/` materializa el patrón "proyecto cliente del Framework". ADR-009 documenta la primera adopción real.
- **ADR-008** (Cross-LLM): modelo `obra/superpowers` validado como patrón canónico cross-LLM. Cuando el Framework empaquete, adoptar el modelo (`.claude-plugin/` + `.codex-plugin/` + ...).
- **ADR-010** (Skill Routing via Foreman): depende de ADR-009. El `sigma:foreman` opera sobre el catálogo definido aquí.
- **LECCIÓN 18** (cross-LLM publishing canónico): citada en SD-3 + en consecuencias positivas.
- **LECCIÓN 19** (método declarativo `extraKnownMarketplaces`): citada como mecanismo de instalación operativo.
- **LECCIÓN 20** (flags rotantes): citada como riesgo R2 + en consecuencias negativas.
- **LECCIÓN 22 candidata** (manual injection point): emerge en este sandbox; documentada en EVALUATION v0.5.
- **LECCIÓN 23 candidata** (matriz a-priori vs ejecutable diverge al alza con operador instruido): emerge en este sandbox; documentada en EVALUATION v0.5.

---

## Implicaciones para Sprint 2

1. **NO construir** todas las 10 skills sigma del plan original. Construir 4 MVP.
2. **Construir primero** `sigma:operationalize-constitution` y `sigma:enforce-constitution-check` — cierran el gap H1 que afecta a TODO proyecto consumidor del Framework.
3. **Diferir** `sigma:circuit-breaker-template`, `sigma:rbac-abac-builder`, `sigma:annotate-*`, `sigma:clarify-with-a-rules-taxonomy` hasta validar las 4 MVP en proyecto productivo.
4. **Documentar el método declarativo `extraKnownMarketplaces`** en `docs/AGENT-INTEGRATION.md` (LECCIÓN 19) — cierra DEUDA-PLUGIN-INSTALL-DOCS.
5. **Documentar Windows setup checklist** (LECCIÓN 20 + DEUDA-WINDOWS-SETUP-CHECKLIST).
6. **Reportar upstream** los issues claude-mem + Superpowers fetch race (DEUDA-CLAUDE-MEM-MANIFEST, DEUDA-SUPERPOWERS-FETCH-RACE).

---

## Decisión final v0.5 PRELIMINAR

✅ Adoptar Spec Kit + ECC + claude-mem como stack base.
🟡 Diferir Superpowers (no descartar).
✅ Construir 4 skills sigma MVP (`operationalize-constitution`, `enforce-constitution-check`, `multi-tenant-isolation-checker`, `dependency-cycle-detector`).
🔵 Mantener Nivel 2 (A1-A25) como única fuente de verdad arquitectónica.
⏳ Promover a v1.0 ACCEPTED tras T1.9 + iteración de `/implement` + build de 4 sigma MVP.

---

**Versión 0.5 PRELIMINAR — 2026-05-21**. Última actualización tras T1.7 (5 skills speckit-* planning ejecutadas) + T1.8 (EVALUATION.md v0.5 refinada) + **T1.9 (2026-05-21 PM continuación 2: comparación empírica sdd-* vs speckit-* completa, Decisión D resuelta como híbrida, anexo T1.9 addendum agregado)**.
