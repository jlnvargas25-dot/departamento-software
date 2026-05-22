# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico post-T1.6→T2 ejecutados (planning-phase only).
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-22 (post Sprint 2 sesión 2 — Phase 2 ADR-011 PRD-ready, build en Sprint 3)
**Cliente recomendado próxima sesión**: **Claude Code CLI** dentro de `C:\DEPARTAMENTO-SOFTWARE\` (skills speckit-* + ecc:* + claude-mem:* + sdd-* + superpowers:* todos cargados)
**Versión**: 6.3 (post Phase 2 ADR-011 PRD-ready — 6 artefactos planning + audit R01-R15 PASS con 3 warnings tracked; Sprint 3 = build classifier)

---

## ✅ SPRINT 2 SESIÓN 2 CERRADA (2026-05-22)

**Phase 2 ADR-011 (trinidad correctiva) PRD-ready** — Pasos 1-5 del PROTOCOLO-CONSTRUCCION-CODIGO ejecutados sobre el primer componente: `sigma:finding-classifier` (front-end de la trinidad).

**Scope decidido en sesión**: extensible (GGA + slots R/G/FG futuros), no solo GGA. Evita retrabajo Sprint 4+.

Artefactos creados:
- `docs/prd/PRD-sigma-finding-classifier.md` — DRAFT v0.1 (Paso 1)
- `docs/dominio/findings-taxonomy.md` — DRAFT v0.1 (Paso 2 — 27 reglas curadas 15A/7B/5C, distribución 55.6/25.9/18.5%)
- `docs/dominio/sigma-classifier-rules.yaml.draft` — DRAFT v0.1 (Paso 2 — YAML declarativo extensible)
- `docs/arquitectura/ARQUITECTURA-sigma-finding-classifier.md` — DRAFT v0.1 (Paso 3 — Python+pyyaml, A20 hexagonal)
- `docs/stories/STORIES-sigma-finding-classifier.md` — DRAFT v0.1 (Paso 4 — 7 stories S-1..S-7, 10hs total, DAG sin ciclos)
- `auditoria/audit-plan-classifier-2026-05-21.json` — DONE (Paso 5 — R01-R15)

**Audit R01-R15 verdict**: `READY_FOR_BUILD_WITH_DEUDAS_TRACKED` (0 críticos, 3 warnings con acción documentada).

3 warnings tracked (precondición de Sprint 3 build):
1. **R07** — S-8 nuevo (construir fixture `sprint1-iteracion3.json` + medir distribución) antes de promover ADR-011 v1.0.
2. **R08** — anotar `emit_calibration_log()` en S-3 al iniciar build (o crear S-3b sub-tarea).
3. **R10** — construir fixture antes de S-6 (precondición ineludible).

**ADR-011 bumpeado**: PROPOSED v0.5 PARTIAL → **PROPOSED v0.7 PARTIAL** con sección "Phase 2 PRD-ready" anexada + cleanup duplicación "Evidencia empírica Phase 1".

**Lecciones candidatas 35-37**: siguen N=1 (no promovidas). Esperan N=2 al cerrar la próxima corrida empírica.

**Pendientes Sprint 3 (build)**: ~10 hs en 7 stories ÷ 2 sesiones (5 hs cada una). Pasos 6-12 del PROTOCOLO.

**Repo state al cierre**: working tree con 6 archivos nuevos + 2 archivos modificados (ADR-011 y SIGUIENTE-SESION.md). Sin commit pendiente — el usuario decide cuándo commitear.

---

## ✅ SPRINT 2 SESIÓN 1 CERRADA (2026-05-21 PM continuación 5)

**Phase 1 ADR-011 (`sigma:gga-scope-aware`) IMPLEMENTADA vía Plan B** (RULES_FILE swap declarativo en `.gga`, sin parser de output).

Artefactos creados:
- `AGENTS-sandbox.md` — subset relaxed de reglas para scope sandbox
- `.git/hooks/pre-commit` — wrapper scope-aware con backup/swap/restore + trap (vive en `.git/hooks/`, no versionado)
- `docs/SCOPE-AWARENESS.md` — operacional con M1 + reversión + limitaciones
- `decisions/ADR-011-*.md` bumped PROPOSED v0.1 → **PROPOSED v0.5 PARTIAL** con evidencia empírica Phase 1

**M1 CUMPLIDO N=1**: GGA cerró en **1 round** sobre el stash de Sprint 1 (vs 4 rounds baseline). Margen amplio sobre umbral ≤2.

**Commits Sprint 2 sesión 1** (pusheados a origin/main):
- `6c0a71c` feat(framework): Sprint 2 Phase 1 ADR-011 - scope-aware verification
- `fe3ed57` fix(sandbox-stack): GGA round 4 cleanup - 5 archivos (ex-stash@{0})

**Stash@{0} dropped** post-cleanup commiteado.

---

## ⚠️ CAMBIO DE DIRECCIÓN — Sprint 2 redirigido (cont. 4) + Phase 1 cerrada (cont. 5)

Tras análisis del **loop asintótico de GGA observado en Iteración 3** (4 rounds, bypass humano final), el Sprint 2 se redirigió:

- **Antes** (en versión 6.0): build 4 sigma MVP (`operationalize-constitution`, `enforce-constitution-check`, `multi-tenant-isolation-checker`, `dependency-cycle-detector`).
- **Ahora** (versión 6.2): **scope-aware verification ✅ Phase 1 cerrada** (Plan B implementado + M1 N=1 OK), **trinidad correctiva → Sprint 3** (cura estructural — Tier A/B/C).
- **Las 4 sigma MVP originales no se descartan**, pero quedan diferidas a Sprint 4+ hasta validar empíricamente que la capa correctiva + scope-aware resuelven el dolor observado.

**Razón del cambio**: el dolor empírico de Sprint 1 fue *"GGA loop sin auto-fix + sin scope awareness"*, no *"falta de skills sigma para Constitution Check enforcement"*. ADR-011 ataca el problema real observado y **Phase 1 lo confirmó empíricamente con N=1**.

## Próximas opciones Sprint 2 sesión 2

**Opción A — Validación N≥2** (Recommended): aplicar Phase 1 a otro caso (un commit nuevo de sandbox-stack o aplicar a Stallen). Solo entonces promover ADR-011 a v1.0 ACCEPTED con evidencia N≥2.

**Opción B — Arrancar Phase 2 Sprint 3** (trinidad correctiva): `sigma:finding-classifier` + `sigma:auto-fix-mechanic` Tier A. Más caro estructural pero apunta a cierre completo del ciclo.

**Opción C — Aplicar workflow a Stallen** con stack validado + Phase 1 activa. Mayor evidencia de producción.

---

## CONTEXTO RÁPIDO — leer EN ORDEN al arrancar

1. `CLAUDE.md` (constitución global del Framework, ~5 min)
2. `auditoria/sesion-activa.md` — addendum 2026-05-21 PM/continuación 2 (T1.9 EMPIRICAL, ~10 min)
3. Este archivo — plan Sprint 2 actualizado con ADR-011 (~5 min)
4. **`decisions/ADR-011-capa-correctiva-y-scope-aware.md` PROPOSED v0.1** (~10 min) — **NUEVA prioridad Sprint 2**
5. `projects/sandbox-stack/T1.9-EVIDENCE.md` v0.2 EMPIRICAL — matriz F1-F10 + 5 lecciones candidatas (~10 min)
6. `projects/sandbox-stack/EVALUATION.md` v0.5 — matriz speckit-* + 2 lecciones candidatas T1.7 (~10 min, opcional)
7. `projects/sandbox-stack/T1.7-EVIDENCE.md` — findings por skill speckit-* (~10 min, opcional)
8. `decisions/ADR-009-adopcion-stack-ecosistema.md` ACCEPTED v1.0 (~5 min)
9. `decisions/ADR-010-skill-routing-foreman.md` PROPOSED (~5 min, contexto)
10. `projects/sandbox-stack/openspec/changes/todo-management/` (7 artefactos sdd-*, opcional)
11. `projects/sandbox-stack/specs/001-todo-management/` (8 artefactos speckit-*, opcional)
12. (Opcional) `NORTE.md` v0.1 — visión Framework
13. (Opcional) `architecture/PRINCIPIOS-ARQUITECTURA.md` v1.3 — A1-A25

## Pendientes operativos cierre cont. 4

- **`git stash@{0}`** activo: GGA round 4 cleanup deferido a Sprint 2 (5 archivos). Recuperar con `git stash pop` al arrancar Sprint 2.

---

## ESTADO ACTUAL (post 2026-05-21 PM/continuación 3 — Sprint 1 COMPLETO)

### ✅ Sprint 1 cerrado: planning + comparación + implementación validada

- T1.6 ✅ Superpowers 14/14 verificado
- T1.7 ✅ 5 skills speckit-* planning (8 artefactos + 47 tasks)
- T1.8 ✅ EVALUATION.md v0.5 (44%→76% Direct operator-dependent)
- T2 ✅ ADR-009 v0.5 PROPOSED
- T1.9 ✅ EMPIRICAL workflow sdd-* completo (7 artefactos en openspec/, 47 tasks, 5 lecciones)
- **Iteración 3 ✅ EJECUTADA**: 4 sub-agents secuenciales sobre tasks.md. **47/47 tasks marcadas [x]**. **19/25 A-rules ejercitadas empíricamente (76%)**. 75 archivos en sandbox. CI gate con adversarial-gate + integration-rls jobs. T1.10-EVIDENCE.md escrito.
- **ADR-009 ✅ ACCEPTED v1.0**: stack Spec Kit + ECC + claude-mem validado empíricamente. Sigma MVP NO bloqueante para v1.0 (operador-instruido cubre el gap).

### ⏸️ DIFERIDO a próximas sesiones (no bloqueante para v1.0)

- **Build sigma MVP** (4 skills): `operationalize-constitution`, `enforce-constitution-check`, `multi-tenant-isolation-checker`, `dependency-cycle-detector`. Sprint 2.
- **Aplicar workflow operativo a Stallen**: usar el stack validado en proyecto cliente real.
- **EVALUATION.md v0.5 → v1.0**: polish con evidencia post-implement.
- **Smoke tests reales**: requieren `npm ci` + `supabase start` + ejecución manual del checklist en `docs/DEPLOYMENT.md`.
- **DEUDAS nuevas Iteración 3**: DEUDA-ADVERSARIAL-TEST-SHAPE-WRONG (menor), DEUDA-NPM-INSTALL-MANUAL, DEUDA-SUPABASE-LOCAL-MANUAL, DEUDA-SIGMA-MVP-NO-CONSTRUIDAS.

### Repo

- Working tree: con cambios pendientes del cierre 2026-05-21 PM/continuación 3
- Branch: main
- Próximo commit pendiente: en este mismo cierre

---

## DECISIONES TOMADAS EN SESIÓN 2026-05-21 PM/continuación 2

- **T1.9 ejecutado empíricamente**: corrida completa sdd-* sobre el mismo caso que speckit-* en T1.7
- **artifact_store=openspec + execution=automatic** elegido vía AskUserQuestion para T1.9
- **Decisión D resuelta como híbrida**: speckit-* default (cost-aware) + sdd-* escalation por matriz F1-F10
- **Iteración 3 diferida a próxima sesión**: cost-aware (~$25-45 gastado en T1.9). Backbone elegido: speckit-* (consistente con T1.7)
- **ADR-009 sigue PROPOSED**: addendum T1.9 agregado, promoción a ACCEPTED requiere iteración 3

---

## DECISIONES PENDIENTES PARA PRÓXIMA SESIÓN

### Decisión D — SDD backbone (`sdd-*` vs `speckit-*`) — ✅ RESUELTA

Backbone **híbrido** resuelto en T1.9 EMPIRICAL:
- **Default**: speckit-* (velocidad ~15s, cost ~30k tokens)
- **Escalation**: sdd-* cuando aplica matriz F1-F10 de T1.9-EVIDENCE.md (multi-domain, DAG explícito, A20 crítico, operador no instruido)
- **Refinamiento futuro**: las 4 sigma MVP (especialmente `sigma:enforce-constitution-check`) llevan speckit-* a paridad de cobertura A* a fracción del costo

### Decisión B — Visión D (Capa A + Capa B)
- (i) Formalizar ADR-010-bis o ADR-011 ahora
- (ii) Esperar evidencia de iteración 3 + build sigma MVP

**Recomendación**: (ii) — la evidencia preliminar de planning (incluyendo T1.9 EMPIRICAL) valida complementariedad pero no necesariamente separación A/B.

### Decisión C — Stallen
Sigue diferido. Sin cambio.

---

## QUÉ HACER ESTA PRÓXIMA SESIÓN

### PASO T-1 — Verificación commit del cierre 2026-05-21 PM/continuación 2

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git log --oneline -5
# Debería mostrar el commit del cierre PM/continuación 2 2026-05-21 (T1.9 EMPIRICAL)
git status
# Esperado: working tree clean
git pull
```

Si push fue exitoso → seguir directo a Iteración 3.

---

### PASO T1.9 — ✅ COMPLETADO 2026-05-21 PM continuación 2

T1.9 ejecutado empíricamente. Decisión D resuelta como híbrida. Ver `projects/sandbox-stack/T1.9-EVIDENCE.md` v0.2 EMPIRICAL.

---

### PASO Iteración 3 — ✅ COMPLETADO 2026-05-21 PM continuación 3

Iteración 3 ejecutada en 4 sub-agents secuenciales. 47/47 tasks marcadas. 19/25 A-rules ejercitadas (76% — matched a-priori). ADR-009 promovido v0.5 PROPOSED → **v1.0 ACCEPTED**. Ver `projects/sandbox-stack/T1.10-EVIDENCE.md`.

---

### Próximas opciones (Sprint 2 o aplicación a Stallen)

**Opción A — Sprint 2: Build sigma MVP (4 skills)**
Construir las 4 skills planeadas en ADR-009. Sin operador instruido del Framework, las skills cierran los gaps que actualmente requieren operador. Tiempo estimado: 2-3 sesiones.

**Opción B — Aplicar workflow a Stallen**
Usar el stack validado (speckit-* + ECC + claude-mem + A1-A25 instruidas) en proyecto cliente real (Stallen SaaS). Mayor evidencia de validez en producción. Tiempo estimado: 1-2 semanas.

**Opción C — Polish + evangelización**
EVALUATION.md v0.5 → v1.0 con evidencia post-implement. Workflow operativo `docs/WORKFLOW-OPERATIVO.md` v1.0. Cross-LLM publishing setup (canonical `obra/superpowers` model). Tiempo estimado: 1-2 sesiones.

---

### PASO Iteración 3 — `/speckit-implement` o `/ecc:multi-execute` sobre tasks.md — 2-3 hs

Ejecutar implementación real sobre las 47 tareas de `specs/001-todo-management/tasks.md`. Objetivo: medir cobertura ejecutable real de las 11 reglas Direct (vs cobertura a-priori).

**Métricas a capturar**:
- Cuántas tasks se ejecutaron sin intervención manual
- Cuántas requirieron corrección
- Cuántas reglas A* fueron verificablemente ejecutadas (vs solo declaradas en plan)
- Costo total tokens
- Fricciones específicas entre Spec Kit + ECC + claude-mem en flujo real

**Output**: `projects/sandbox-stack/T1.10-EVIDENCE.md` (implementation phase).

---

### PASO T1.11 — Refinamiento ADR-009 v0.5 → v1.0 — 60 min

Tras T1.9 + iteración 3:

- Actualizar matriz A* vs stack v0.5 → v1.0 con evidencia post-implement
- Resolver Decisión D en ADR-009
- Cambiar status de PROPOSED a ACCEPTED (si validación pasa) o REJECTED (si falla)
- Anexar evidencia ejecutable como apéndice

---

### PASO T3 — Build 4 sigma MVP — 1-2 sesiones (no esta sesión)

Construir:
1. `sigma:operationalize-constitution`
2. `sigma:enforce-constitution-check`
3. `sigma:multi-tenant-isolation-checker`
4. `sigma:dependency-cycle-detector`

Como skills cross-LLM siguiendo modelo `obra/superpowers` (LECCIÓN 18).

---

### PASO T4 — NORTE Framework v0.2 (placeholders Q4-Q7) — 30-60 min

Llenar:
- Q4 Tier de calibración (mantener Tier 1 default o multi-tier)
- Q5 Stakeholders detallados
- Q6 Restricciones
- Q7 Criterio de stop / pivot

Bump v0.1 → v0.2 (no v1.0 todavía).

---

### PASO T5 — Workflow operativo Nivel 0 — 1-2 hs

Si Visión C confirmada por ADR-009 v1.0 ACCEPTED → crear `docs/WORKFLOW-OPERATIVO.md` v1.0 documentando:
- Composición del stack curado
- Cuándo usar cada pieza
- Orden Analizar → Planificar → Ejecutar → Verificar
- Cuándo aplicar overlay del Framework
- Cuándo invocar skills sigma

---

### PASO T6 — Documentar lecciones operativas — 45 min

Agregar a `docs/AGENT-INTEGRATION.md`:
- Método declarativo `extraKnownMarketplaces` (LECCIÓN 19)
- Cross-LLM publishing canónico modelo `obra/superpowers` (LECCIÓN 18)
- Windows setup checklist (DEUDA-WINDOWS-SETUP-CHECKLIST)
- Desactivación de Fact-Forcing Gate en sandbox via settings.local.json (DEUDA-FACT-FORCING-GATE-EN-SANDBOX, workaround)

---

## PRE-FLIGHT

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git status              # working tree esperado: clean post cierre 2026-05-21 PM/continuación
git pull
git log --oneline -10

cd projects/sandbox-stack
ls .claude/skills/      # speckit-*
ls .specify/            # workflow Spec Kit
ls specs/001-todo-management/  # 8 artefactos (spec, checklists, plan, research, data-model, contracts, quickstart, tasks)
```

---

## REGLAS CRÍTICAS A RECORDAR

### 7 Principios rectores
1. Python traza → IA recorre → Python verifica
2. **3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA**
3. Dominio-first
4. Auto-fix > finding cuando inequívoco
5. Polinización cruzada
6. **Descubrir antes de ejecutar** (audit empírico)
7. Meta-producto recursivo

### Reglas A1-A25 más críticas (sin cambio)
- A5 Multi-tenant Strict Isolation (CRÍTICA, Direct post-T1.7)
- A12 Zero Trust (CRÍTICA, Direct)
- A20 Hexagonal Architecture (CRÍTICA, Direct)
- A21 Structured Observability (CRÍTICA, Partial — traces deferido v2)
- A22 Secrets Management (CRÍTICA, Direct)
- A24 Data Lifecycle (CRÍTICA, Direct post-T1.7)

### Insight Decisión A — VALIDADO 2 NIVELES
- Sesión 2026-05-21 (matriz a-priori): 44% Direct + 48% Partial confirmó complementariedad
- Sesión 2026-05-21 PM/continuación (matriz ejecutable): 76% Direct con operador instruido del Framework → el delta es operator-dependent, lo que justifica empíricamente el Framework

### Lecciones técnicas críticas (acumulado)
- LECCIÓN 16: cascada de aceptación entre Claude instances
- LECCIÓN 17: edit_file con array no es atómico — preferir write_file
- LECCIÓN 18: cross-LLM publishing canónico (`obra/superpowers` modelo)
- LECCIÓN 19: método declarativo `extraKnownMarketplaces` en ~/.claude/settings.json
- LECCIÓN 20: flags de tools rotan rápido — documentar comportamiento, no flags
- LECCIÓN 21 (N=1): matriz a-priori vs ejecutable — validar invocando
- LECCIÓN 22 candidata (N=1, 2026-05-21 PM): manual injection point del Constitution Check
- LECCIÓN 23 candidata (N=1, 2026-05-21 PM): matriz a-priori vs ejecutable diverge AL ALZA con operador instruido

### Lecciones de proceso
- Anti-paternalismo: NO proyectar cansancio
- Audit empírico: cuando Julián cuestiona → audit INMEDIATO (hit rate 20/20)
- El Departamento es Visión C confirmada (curador + calibrador + overlay arquitectónico declarativo)
- Fact-Forcing Gate desactivable en sandbox via settings.local.json (precedente capturado)

---

## RIESGOS DE LA PRÓXIMA SESIÓN

- **T1.9 confusión sdd-* vs speckit-***: si ambos workflows son confusamente similares, Decisión D queda como "depende del proyecto" — aceptable.
- **Iteración 3 cuesta más de lo estimado**: si `/implement` toma 4+ hs, dividir en sub-T1.10.1 (US2 auth) y T1.10.2 (US1 todos).
- **ADR-009 promoción puede REJECT**: si la iteración 3 revela fricciones irreconciliables Spec Kit↔ECC↔claude-mem, ADR-009 baja a REJECTED y se redacta ADR-009-bis.
- **Build sigma MVP puede revelar puntos no extensibles**: si Spec Kit no permite hook post-procesador, las sigma skills necesitan otra arquitectura.
- **Compactación de chat**: si la sesión es larga, aplicar PROTOCOLO-INICIO-CHAT PASO 1 al re-arrancar.

---

## ARCHIVOS CLAVE A TOCAR EN LA PRÓXIMA SESIÓN

- `projects/sandbox-stack/T1.9-EVIDENCE.md` (nuevo)
- `projects/sandbox-stack/T1.10-EVIDENCE.md` (nuevo — implementation)
- `projects/sandbox-stack/EVALUATION.md` (v0.5 → v1.0)
- `decisions/ADR-009-adopcion-stack-ecosistema.md` (v0.5 → v1.0 ACCEPTED o REJECTED)
- `NORTE.md` (v0.1 → v0.2 placeholders)
- `docs/WORKFLOW-OPERATIVO.md` (nuevo si T5 aplica)
- `docs/AGENT-INTEGRATION.md` (actualizar con T6)
- `auditoria/sesion-activa.md` (al cerrar próxima sesión)
- `SIGUIENTE-SESION.md` (al cerrar, regenerar)
- Posibles 4 nuevos dirs `sigma:*` skills (cross-LLM publishing)

---

## NOTAS PARA CLAUDE

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Cliente recomendado**: Claude Code CLI dentro de `projects/sandbox-stack/`
- **Visión Framework**: harness anti-alucinación senior — Visión C confirmada empíricamente
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO (hit rate 20/20)
- **NUNCA proyectar cansancio**
- **A1-A25 universales** — 0 deudas A* abiertas
- **PROTOCOLO-INICIO-CHAT v1.0 PASO 1 OBLIGATORIO** para verificar Project es Framework
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy pause)
- **EVALUATION.md v0.5 es preliminar** — iteración 3 lo refina con evidencia de implement
- **claude-mem requiere autoUpdate: false** — no romper el parche
- **Fact-Forcing Gate desactivado** en `projects/sandbox-stack/.claude/settings.local.json` para esta workspace. Si trabajás en otro path, el gate sigue activo.
- **8 stacks cargados**: spec-kit, ecc (200+), claude-mem (12), superpowers (14), sdd-* (9 — para T1.9), vercel:*, sigma-mem (futuro), gentle-ai builtins.

---

## CÓMO USAR ESTE ARCHIVO

Al abrir Claude Code CLI:

> *"Seguimos con el Departamento. Aplicá PROTOCOLO-INICIO-CHAT. Leé sesion-activa.md (addendum 2026-05-21 PM/continuación) y SIGUIENTE-SESION.md v5.1. Diagnóstico estándar. Arrancamos T-1 (verificar commit pusheado), después T1.9 (comparación sdd-* vs speckit-*), después iteración 3 (/implement) si hay tiempo."*

---

Creado: 2026-05-15 | Versión: **5.1** (post planning-phase del workflow real + 2 lecciones candidatas + ADR-009 v0.5 PROPOSED)
Para: Claude que abra próxima sesión (Claude Code CLI recomendado dentro de `projects/sandbox-stack/`)
