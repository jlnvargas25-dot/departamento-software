# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico post-T1.6→T2 ejecutados (planning-phase only).
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-21 PM continuación 2 — post T1.9 EMPIRICAL (workflow sdd-* completo + comparación side-by-side + Decisión D resuelta + ADR-009 actualizado)
**Cliente recomendado próxima sesión**: **Claude Code CLI** dentro de `projects/sandbox-stack/` (skills speckit-* + ecc:* + claude-mem:* + sdd-* + superpowers:* todos cargados)
**Versión**: 5.2 (post T1.9 EMPIRICAL + Decisión D resuelta híbrida)

---

## CONTEXTO RÁPIDO — leer EN ORDEN al arrancar

1. `CLAUDE.md` (constitución global del Framework, ~5 min)
2. `auditoria/sesion-activa.md` — addendum 2026-05-21 PM/continuación 2 (T1.9 EMPIRICAL, ~10 min)
3. Este archivo — plan iteración 3 + decisiones pendientes actualizadas (~5 min)
4. `projects/sandbox-stack/T1.9-EVIDENCE.md` v0.2 EMPIRICAL — matriz F1-F10 + 5 lecciones candidatas (~10 min)
5. `projects/sandbox-stack/EVALUATION.md` v0.5 — matriz speckit-* + 2 lecciones candidatas T1.7 (~10 min, opcional)
6. `projects/sandbox-stack/T1.7-EVIDENCE.md` — findings por skill speckit-* (~10 min, opcional)
7. `decisions/ADR-009-adopcion-stack-ecosistema.md` v0.5 PROPOSED + addendum T1.9 (~5 min)
8. `projects/sandbox-stack/openspec/changes/todo-management/` (7 artefactos sdd-*, opcional para foco arquitectónico)
9. `projects/sandbox-stack/specs/001-todo-management/` (8 artefactos speckit-*, opcional)
10. (Opcional) `NORTE.md` v0.1 — visión Framework
11. (Opcional) `architecture/PRINCIPIOS-ARQUITECTURA.md` v1.3 — A1-A25

---

## ESTADO ACTUAL (post 2026-05-21 PM/continuación 2)

### ✅ Planning-phase sandbox completo + comparación empírica

- T1.6 ✅ Superpowers 14/14 verificado post-restart (DEUDA-SUPERPOWERS-FETCH-RACE cerrada)
- T1.7 ✅ 5 skills speckit-* planning ejecutadas (8 artefactos en `specs/001-todo-management/` + 47 tasks)
- T1.8 ✅ `EVALUATION.md` v0.5 PRELIMINAR con matriz refinada (44%→76% Direct con caveat operator-dependent)
- T2 ✅ `ADR-009-adopcion-stack-ecosistema.md` v0.5 PROPOSED
- **T1.9 ✅ EMPIRICAL** workflow sdd-* completo sobre el mismo caso (7 artefactos en `openspec/changes/todo-management/` + 47 tasks). **Decisión D resuelta**: backbone híbrido. Convergencia 47 tasks. 5 lecciones candidatas (24-28).

### ⏸️ DIFERIDO a próxima sesión

- **Iteración 3**: `/speckit-implement` o `/ecc:multi-execute` sobre `specs/001-todo-management/tasks.md` (47 tareas). **Backbone**: speckit-* (default híbrido por cost-aware, ver T1.9-EVIDENCE.md Sección 6)
- **Build sigma MVP**: 4 skills (`operationalize-constitution`, `enforce-constitution-check`, `multi-tenant-isolation-checker`, `dependency-cycle-detector`)
- **Promoción ADR-009 v0.5 → v1.0 ACCEPTED**: condicionada a iteración 3 + sigma MVP
- **DEUDAS nuevas T1.9**: DEUDA-SDD-EXPLORE-NO-WRITE (menor), DEUDA-SUB-AGENT-OVERRIDE-OPERATOR (menor)

### Repo

- Working tree: con cambios pendientes del cierre 2026-05-21 PM/continuación 2
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
