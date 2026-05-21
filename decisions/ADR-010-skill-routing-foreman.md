# ADR-010: Skill Routing via Foreman — Planning-Time Declaration + Runtime Auto-Activation Hybrid

**Status**: PROPOSED (pendiente validación empírica en Sprint 2 post-sandbox)
**Date**: 2026-05-20
**Sprint**: Sprint 2 — post sesión PM 2026-05-20 (post implementación A20-A25 + post T1 sandbox del stack)
**Related**: ADR-006 (Niveles + SOLID), ADR-008 (Cross-LLM), ADR-009 (Adopción del Stack del Ecosistema, en redacción)

---

## Contexto

Tras la decisión ACCEPT PARCIAL del stack del ecosistema en ADR-009 (Spec Kit
+ ECC + claude-mem adoptados wholesale, Superpowers diferido, 4-5 skills
`sigma:*` propias para gaps A4/A5/A19/A25), el Framework Departamento queda
con un catálogo de skills considerable cargado en cada sesión de LLM:

- `ecc:*` — ~119 skills del Everything Claude Code
- `speckit-*` — varias skills de Spec Kit oficial
- `vercel:*` — Vercel Agent Skills
- `sdd-*` — skills SDD (alternativas/overlays sobre Spec Kit, ver
  DEUDA-SDD-VS-SPECKIT-COMPARACION)
- `sigma:*` — skills propias del Framework (4-5 planeadas para gaps específicos)
- Built-ins del LLM (Claude Code u otro)

Esto genera tres problemas concretos identificados en el sandbox de Sprint 2:

1. **Overlap de descriptions**: dos skills con descriptions parecidas (ej.
   `ecc:test-runner` y `speckit-test-validate`) pueden activarse ambas o
   activar la "incorrecta" por matching ambiguo.

2. **Priorización**: cuando dos skills aplican al mismo contexto (ej. una
   `ecc:*` lang-specific + una `sigma:*` universal), no hay regla declarada
   de cuál tiene precedencia.

3. **Disponibilidad cross-LLM**: el mecanismo nativo de auto-activación por
   description difiere entre agents (Claude Code, Codex, Cursor, etc.). Una
   skill bien escrita para Claude puede no auto-activarse en Codex con la
   misma description. Conecta directo con ADR-008 y LECCIÓN 18 (cross-LLM
   publishing model).

**Pregunta arquitectónica fundamental detectada en sesión PM 2026-05-20**
(Julián, hit rate 20/20):

> *"¿cómo sabemos que el LLM va a saber o necesita esa skill? ¿desde
> planeación se hace el SDD con las skills que necesita en ese SDD?"*

La pregunta desplaza el problema del routing del **tiempo de ejecución**
(reactivo, "¿qué skill uso ahora?") al **tiempo de planeación** (proactivo,
"¿qué skills va a necesitar este plan desde el principio?").

---

## Decisión

**Skill routing del Framework es HÍBRIDO: declaración proactiva en
planeación + auto-activación reactiva en runtime + verificación de
compliance al cierre.**

El centro del modelo es un sub-agente especialista, `sigma:foreman`, que es
invocado en **dos momentos** del ciclo del harness:

| Momento | Rol del foreman | Output |
|---|---|---|
| **Planeación** (subroutine de `/speckit.plan`) | Decide proactivamente qué skills van a necesitarse para el feature | Sección "Skill Graph Declarado" del plan, con justificación |
| **Verificación de cierre** | Audita si las skills declaradas se usaron efectivamente, y qué se agregó/omitió | Reporte de compliance del contrato de skills |

El foreman **NO se invoca en cada turno de ejecución**. Durante ejecución,
las skills declaradas se invocan via slash command o auto-activación
nativa; las skills no-declaradas se auto-activan reactivamente como red de
seguridad (mecanismo nativo del LLM).

### División de responsabilidad por tipo de skill

| Tipo de skill | Cuándo se decide | Cómo se invoca | Por qué |
|---|---|---|---|
| **Declaradas** (intencionales, derivadas del spec) | Planeación (foreman ayuda al planificador) | Slash command o invocación explícita en fase | Contrato explícito, auditable |
| **Reactivas** (auto-activan por context match) | Runtime | Mecanismo nativo del LLM | Red de seguridad para casos no previstos en plan |
| **De verificación final** | Cierre de sesión | Foreman audita contra plan | Compliance del contrato |

### Rol del foreman — invocable, no autónomo

`sigma:foreman` es **tool invocable**, no agente autónomo:

- LLM principal (planificador) lo invoca con input estructurado: reglas A*
  aplicables al feature, dominio, fases del feature
- Foreman traduce: reglas A* + dominio → skills concretas + slash commands
  + justificación
- LLM principal integra el output al plan final
- Patrón validado en ecosistema: ECC, Superpowers, claude-mem usan agents
  como tools invocables (LECCIÓN 8)

### Estructura del plan con skill graph declarado

Salida enriquecida de `/speckit.plan` tras la integración:

```markdown
# PLAN — Feature: <nombre>

## Spec resumida
<resumen>

## Reglas A* aplicables (derivadas del spec por foreman)
A<n>, A<m>, A<k>, ...

## Skill Graph Declarado por fase

### Fase 1 — <descripción>
Skills requeridas:
- <skill1> (regla A<n>: <razón>)
- <skill2> (auto-activación esperada en <context>)
- ...

### Fase 2 — <descripción>
Skills requeridas:
- ...

## Verificación de cierre
- [ ] Todas las skills declaradas fueron invocadas (log de foreman)
- [ ] Justificación documentada de skills declaradas omitidas
- [ ] Skills auto-activadas adicionales registradas (transparencia)
```

---

## Razones

### Por qué proactivo en planeación > reactivo en runtime

1. **6° principio rector** (descubrir antes de ejecutar): la planeación es
   donde se descubre el scope, no el runtime. Mover el routing a planeación
   alinea la práctica con el principio.

2. **2° principio rector** (3 capas: preventiva → verificable → correctiva):
   declarar skills en planeación es la **capa preventiva**; las skills
   declaradas son las verificaciones que se aplicarán. Auto-activación
   reactiva en runtime es **red de seguridad**, no la línea principal.

3. **A14 Explicit Failure**: si una skill declarada no está disponible, el
   harness falla explícito con error informativo. Sin declaración previa,
   el LLM "sigue como puede" y la falla es silenciosa.

4. **A15 Unhappy Path First**: en planeación se piensa adversarialmente qué
   puede fallar; las skills declaradas cubren explícitamente los unhappy
   paths conocidos. Runtime improvisado tiende a cubrir solo happy path.

5. **Visión harness senior**: un senior en producción NO improvisa qué
   linter / test framework / security review usar en runtime. Lo declara
   ANTES de empezar a codear. El Framework debe materializar ese patrón
   senior, no el patrón junior reactivo.

### Por qué LLM-principal-usa-foreman > foreman-hace-todo

1. **SOC limpio**: foreman es especialista del catálogo de skills; LLM
   principal entiende el feature. División natural por competencia.

2. **Cross-LLM por diseño**: cualquier LLM principal (Claude/Codex/Cursor)
   puede invocar foreman como subroutine sin que foreman tenga que conocer
   particularidades de cada agent. Conecta con ADR-008 + LECCIÓN 18.

3. **Foreman se mantiene scope acotado**: si foreman parsea spec + decide
   dominio + mapea reglas + elige skills + integra al plan, crece a "senior
   completo" — riesgo de scope creep que ya identificamos. Invocable y
   mínimo es mejor.

4. **Testeable deterministicamente**: dado input estructurado (reglas A* +
   dominio), foreman debería retornar skills predecibles. Testeable con
   A15 adversarial.

5. **Patrón validado en ecosistema**: ECC, superpowers, claude-mem todos
   usan agents como tools invocables, no autónomos. LECCIÓN 8 (no
   reinventar la rueda al meta-nivel).

### Por qué híbrido > solo-proactivo o solo-reactivo

- **Solo proactivo**: pierde la red de seguridad para casos no previstos
  en plan. Imposible anticipar todo en planeación.
- **Solo reactivo**: ya descartado por las razones de arriba (improvisación
  vs disciplina senior).
- **Híbrido**: aprovecha lo mejor de cada modelo. El plan declara skills
  intencionales; las reactivas catch lo que no estaba previsto. Foreman
  audita coherencia al cierre.

---

## Sub-decisiones pendientes (placeholders explícitos)

Las siguientes decisiones de implementación quedan PENDIENTES hasta tener
evidencia empírica del sandbox extendido (sub-T1.5 a definir):

### SD-1 — Formato exacto de la sección "Skill Graph Declarado"

Opciones:
- (a) Markdown estructurado en el plan (legible humano + parseable)
- (b) YAML/JSON separado en `.specify/memory/skill-graph.yaml`
- (c) Frontmatter en el plan + markdown body

**Validación empírica requerida**: cuál integra mejor con `/speckit.plan`
output, qué tooling de Spec Kit ya consume frontmatter vs body.

### SD-2 — Política de fallback granular

Opciones:
- (a) Hard-fail si skill declarada no está disponible (A14 explícito)
- (b) Soft-fail con warning logueado + ejecución continúa
- (c) Diferenciado por criticidad de la skill (skills críticas hard-fail,
  importantes soft-fail)

**Validación empírica requerida**: probar las 3 en sandbox y medir
disrupción del flujo del desarrollador.

### SD-3 — Mecanismo de invocación cross-LLM del foreman

Opciones:
- (a) MCP server propio (`sigma-mcp` con tool `foreman_plan_skills`)
- (b) Skill markdown puro invocable por slash command desde cualquier LLM
- (c) Combinación: skill markdown wrapper + MCP server backend para lógica

**Validación empírica requerida**: medir overhead de cada opción y
compatibilidad cross-LLM real.

### SD-4 — Catálogo de skills consumido por foreman

Opciones:
- (a) Foreman lee `CLAUDE.md` (sección DISPATCHER DE SKILLS, hoy vacía) +
  parsea on-the-fly
- (b) Archivo derivado `.claude/skill-catalog.yaml` generado por script
  `generate_skill_catalog.py` desde CLAUDE.md + skills instaladas
- (c) Foreman tiene catálogo embebido en su system prompt (no
  recomendado: difícil mantener)

**Recomendación tentativa**: (b) con generación automática. CLAUDE.md
sigue siendo fuente humana-legible; el yaml es el catálogo derivado que
foreman consume.

### SD-5 — Granularidad del skill graph

Opciones:
- (a) Por fase del plan (granularidad fase, ej. "Phase 1: Schema")
- (b) Por tarea atómica del plan (granularidad task)
- (c) Híbrido: skills universales declaradas a nivel plan + skills
  específicas por task

**Validación empírica requerida**: cuál es más útil al ejecutor.

### SD-6 — Política de invocación del foreman en planeación

Opciones:
- (a) Foreman siempre se invoca durante `/speckit.plan`
- (b) Foreman se invoca solo si el plan tiene cierta complejidad
  (heurística: >N tareas o >M reglas A* aplicables)
- (c) Foreman se invoca on-demand, el LLM principal decide cuándo

**Recomendación tentativa**: (a) siempre, para garantizar consistencia.
Optimización por complejidad puede agregarse después si hay evidencia
de que es costoso.

---

## Tests adversariales obligatorios (A15 aplicado al routing)

Antes de promover este ADR de PROPOSED a ACCEPTED, validar empíricamente:

- **T-Adv-1**: Dos skills con descriptions solapadas en el catálogo. ¿Qué
  decide el foreman? ¿Hay regla de priorización?
- **T-Adv-2**: Plan declara skill que no existe (typo, skill removida,
  marketplace caído). ¿Hard-fail o continúa? ¿Mensaje útil para el
  desarrollador?
- **T-Adv-3**: Spec demasiado vago para derivar reglas A* aplicables.
  ¿Foreman pide clarificación, devuelve set por default, o falla?
- **T-Adv-4**: Catálogo de skills tiene 200+ entradas. ¿Foreman sigue
  decidiendo en tiempo razonable? ¿Context window del foreman explota?
- **T-Adv-5**: Invocación cross-LLM: Claude Code → foreman vs Codex →
  foreman vs Cursor → foreman. ¿Mismos outputs para el mismo input?
  (Determinismo cross-LLM)
- **T-Adv-6**: Skill auto-activada en runtime que NO estaba declarada en
  plan. ¿Foreman al cierre la considera violación, mejora, o neutro?
- **T-Adv-7**: Skill declarada en plan que NO se invocó durante ejecución.
  ¿Foreman al cierre la considera bug, optimización válida, o requiere
  justificación?
- **T-Adv-8**: Plan generado sin invocar foreman (humano lo escribe a
  mano). ¿El sistema lo permite o lo bloquea?

Plan: estos tests se ejecutan en sub-T1.6 del Sprint 2 antes de promover
ADR a ACCEPTED.

---

## Métricas de éxito (placeholders)

Para promover el ADR de PROPOSED a ACCEPTED en Sprint 2 maduro, medir:

- **M-1**: % de features con skill graph declarado en su plan (target: ≥
  90% en Sprint 3+)
- **M-2**: % de skills declaradas que efectivamente se invocaron durante
  ejecución (target: ≥ 85%)
- **M-3**: Frecuencia de falsos positivos de auto-activación reactiva
  (target: ≤ 2 por feature)
- **M-4**: Tiempo medio de invocación de foreman en planeación (target: ≤
  10s)
- **M-5**: Tasa de tests adversariales pasados (target: 8/8 antes de
  promoción)
- **M-6**: Hit rate cross-LLM (mismo input → mismo output en ≥ 3 agents,
  target: ≥ 90%)

---

## Conexiones con el resto del Framework

- **ADR-006** (Niveles + SOLID): foreman + skill graph operan al límite
  entre Nivel 3 (skills técnicas) y Nivel 5 (decisiones específicas).
  Foreman es Nivel 3 universal; el skill graph declarado es Nivel 5
  específico del proyecto/feature.
- **ADR-008** (Cross-LLM): este ADR materializa "cómo se hace cross-LLM
  el routing de skills" — depende crucialmente de que foreman sea
  invocable desde cualquier agent. Sub-decisión SD-3 lo formaliza.
- **ADR-009** (Adopción del Stack — en redacción): este ADR depende de
  que el stack del ecosistema esté adoptado. Skill graph integra Spec Kit
  (planificador) + ECC + claude-mem + sigma propias.
- **LECCIÓN 16** (cascada de aceptación entre instances): el foreman
  como árbitro reduce el riesgo de cascada — su decisión es la
  referencia, no la opinión de otra instancia.
- **LECCIÓN 17** (edit_file no atómico + falsa atribución): no aplica
  directo, pero refuerza el patrón "verificar empíricamente antes de
  declarar" — el foreman al cierre verifica empíricamente uso, no asume.
- **LECCIÓN 18** (cross-LLM publishing model): `sigma:foreman` debe
  publicarse con multi-plugin manifest (`.claude-plugin/` +
  `.codex-plugin/` + `.cursor-plugin/`) como `obra/superpowers`.
- **LECCIÓN 19** (`extraKnownMarketplaces`): el catálogo que consume
  foreman incluye marketplaces declarados ahí. Vale formalizar en SD-4.
- **LECCIÓN 20** (flags del ecosistema rotan rápido): documentar el
  comportamiento del foreman, no comprometer flags exactos de Spec Kit
  u otros tools que pueden cambiar entre versiones.

---

## Implementación inicial propuesta

Una vez promovido a ACCEPTED tras validación empírica:

### Paso 1 — Esqueleto del foreman
`projects/<slug>/.claude/agents/sigma-foreman.md` (o equivalente
cross-LLM):

```yaml
---
name: sigma:foreman
description: Skill router del Framework Departamento de Software. Decide
  qué skills se declaran en planeación y verifica su uso al cierre.
input:
  - phase: "planning" | "verification"
  - context_planning?: { spec, rules_aplicables, domain }
  - context_verification?: { plan_skills_declared, runtime_log }
output:
  - planning: { skills_to_declare, justification, rules_to_apply }
  - verification: { compliance_report, missing, added, neutral }
---
```

### Paso 2 — Generación del catálogo
Script `tools/generate_skill_catalog.py` que produce
`.claude/skill-catalog.yaml` desde:
- CLAUDE.md (sección DISPATCHER)
- Skills instaladas en marketplaces declarados
- Mapping A* → skill (de `architecture/PRINCIPIOS-ARQUITECTURA.md`)

### Paso 3 — Integración con `/speckit.plan`
Skill `sigma:foreman-plan-integration.md` que se auto-activa al ejecutar
`/speckit.plan` y agrega la sección "Skill Graph Declarado" al output.

### Paso 4 — Integración con cierre de sesión
Extensión del `PROTOCOLO-CIERRE-SESION.md` con paso 5b: "Foreman audit:
verificar uso de skills declaradas". Output va al sesion-activa.md.

### Paso 5 — Tests adversariales
Implementar T-Adv-1 a T-Adv-8 en `tests/foreman/`.

### Paso 6 — Publicación cross-LLM
Multi-plugin manifest según LECCIÓN 18, para que `sigma:foreman` sea
invocable desde Claude Code, Codex, Cursor.

---

## Historial

- **2026-05-20 (PM)**: ADR creado como PROPOSED tras discusión arquitectónica
  con Julián en sesión PM 2026-05-20. Hit rate de intuición arquitectónica
  acumulado al crear este ADR: 20/20.
  - Pregunta clave de Julián que disparó la decisión: "*¿desde planeación se
    hace el SDD con las skills que necesita en ese SDD?*"
  - Respuesta del Framework: sí, y se materializa via foreman como tool
    invocable.
  - Sub-decisiones SD-1 a SD-6 quedan pendientes de validación empírica
    en sandbox.

---

**Status**: PROPOSED
**Próxima acción**: validar empíricamente en Sprint 2 (sub-T1.5 a T1.7) y
promover a ACCEPTED tras T-Adv-1 a T-Adv-8 pasados + métricas iniciales OK.
**Autor**: discusión Julián + Claude (chat web sesión PM 2026-05-20 post-cierre formal)
