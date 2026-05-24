# PRD — `sigma:auto-fix-mechanic`

**Status**: DRAFT v0.1
**Date**: 2026-05-22 (Sprint 3 sesión 3)
**Owner**: Departamento de Software
**Related**: ADR-011 PROPOSED v0.9 PARTIAL (Phase 2 — Trinidad Correctiva, Tier A handler)
**Upstream**: `sigma:finding_classifier` v0.1.0 ✅ operativo (73 tests PASS, audit Paso 7+8 PASS, M2 cumplido)
**Protocolo**: Paso 1 (Capturar intención) del PROTOCOLO-CONSTRUCCION-CODIGO

---

## 1. Contexto

ADR-011 declaró la **trinidad correctiva** (Tier A mecánico / Tier B sub-agente acotado / Tier C decisión humana). Sprint 3 sesiones 1+2 construyeron el front-end determinístico (`finding_classifier`) que clasifica findings en Tier A/B/C según `rules.yaml` v0.1.0 (15 reglas Tier A curadas con `action_hint` específico).

El classifier **etiqueta pero no fixea**. M3 del ADR-011 exige que ≥90% de findings clasificados como Tier A reciban fix sin intervención humana — sin un handler que efectivamente aplique los codemods, M3 no es medible y la trinidad correctiva no compone.

`sigma:auto-fix-mechanic` es el **segundo componente de Phase 2**. Es el handler de Tier A: toma findings clasificados, invoca codemods determinísticos según `action_hint`, verifica que el fix preservó semántica, y emite patch atómico verificable. Si algo falla en la verificación, rollback atómico + escalar a Tier C como rechazo, NO silenciar.

Esto operacionaliza el **4° principio rector** (auto-fix > finding cuando inequívoco) y cierra empíricamente el ciclo PREVENTIVA → VERIFICABLE → **CORRECTIVA** del 2° principio rector.

---

## 2. Problema que resuelve

**Hoy**: el classifier etiqueta findings como `tier: A` con `action_hint` (ej. `eslint-fix`, `console-to-logger`, `rename-migration-timestamp`), pero el operador (Julián) sigue aplicando los fixes manualmente uno por uno. Esto es:

- **Lento**: cada round de GGA del Sprint 1 generó ~15 issues Tier A. Aplicarlas manualmente toma 20-30 minutos.
- **No-determinístico**: el mismo finding puede recibir fix levemente distinto entre sesiones (humor del operador, contexto).
- **Riesgoso**: el operador puede aplicar mal el fix (typo, semántica rota) y los tests downstream solo lo detectan después.

**Tras este PRD**: el mechanic aplica codemods determinísticos por rule_id, verifica post-fix con AST/lint/tests focalizados, y entrega patch atómico. El operador queda libre para enfocarse en Tier B (sub-agente) y Tier C (decisión humana real).

**Beneficio cuantificable**: M3 ADR-011 (Tier A auto-fix ≥90%) habilitado. Tiempo commit-to-green proyectado baja del baseline Sprint 1 (~30 min para 15 findings A) a <2 min (M5 ADR-011).

---

## 3. Intención (one-liner)

> "Aplicar codemods determinísticos (sin LLM) a findings clasificados como Tier A, verificar el fix preservó semántica, y entregar patch atómico verificable — o rollback + escalación a Tier C si el fix no es seguro."

---

## 4. Scope

### In scope (este PRD)

- **Universo de findings fixables**: los **15 rule_ids Tier A** curados en `framework/sigma/finding_classifier/rules.yaml` v0.1.0:
  - TS-1, TS-NON-NULL-ASSERTION, A21-OBS-1-CONSOLE-LOG, A21-OBS-1b-DENO-CONSOLE, NO-VAR, VAR-TO-CONST, MIGRATION-NAMING, TYPE-CAST-AS-ANY, PGSQL-MISSING-VOLATILE, LET-WITHOUT-REASSIGN, UNUSED-IMPORT, TRAILING-WHITESPACE, MISSING-SEMI, IMPORT-ORDER, OBJECT-SHORTHAND.
- **Diseño extensible**: slot vacío para Tier A futuros (R/G/FG cuando aparezcan en Sprint 4+).
- **Output por finding procesado**: `{rule_id, file, action_hint, fix_status: applied | rolled_back | escalated_to_c, patch_summary, verification: passed | failed}`.
- **Verificación post-fix determinística**: por cada fix aplicado, re-correr AST-check del rule_id sobre el archivo modificado para confirmar que el patrón target ya no aparece. Si el patrón sigue, rollback + escalación a C.
- **Rollback atómico**: si verificación falla o si test focalizado se rompe, revertir el cambio del archivo a su estado pre-fix.
- **Idempotencia**: aplicar el mechanic dos veces sobre el mismo finding = segundo run NO-OP (el patrón ya no está).
- **CLI invocable**: input JSON `Finding[]` (output del classifier), output JSON `PatchResult[]` + exit code.
- **Implementación**: Python 3.10+ orquestador + subprocess para invocar tools externos. Sin Node, sin npm install runtime.

### Out of scope (este PRD)

- **Tier B y Tier C**: PRDs separados (`correction-agent-bounded`, `correction-adr-draft`).
- **Instalación de tools externos**: eslint/prettier/ts-morph deben estar disponibles en el environment. Pre-flight check al boot + error claro si falta. Instalación es responsabilidad del operador (documentado en quickstart del mechanic).
- **Aplicación distribuida**: un solo proceso local. Multi-tenant queueing es Sprint 5+.
- **Multi-archivo en un solo fix**: cada fix toca exactamente 1 archivo. Si un finding "lógico" requiere cambios coordinados en N archivos, va a Tier B (sub-agente acotado).
- **Inferencia de codemods nuevos**: si un rule_id Tier A llega sin handler implementado, escala a Tier C como rechazo + log estructurado. NO improvisa el fix.
- **UI / dashboard**: solo stdout JSON. Dashboards Sprint 5+.
- **LLM en path de fix**: 1° principio rector.
- **Decisión arquitectónica wholesale ECC vs wrapper sigma**: la resuelve Paso 3 con evidencia. Este PRD describe el QUÉ; el CÓMO es del Paso 3.

---

## 5. Usuarios y stakeholders

| Stakeholder | Rol respecto al mechanic |
|-------------|--------------------------|
| **Operador (Julián)** | Invoca el mechanic indirectamente vía pre-commit hook scope-aware. Revisa PatchResult JSON antes de stage. |
| **`sigma:finding_classifier` (upstream)** | Produce el `Finding[]` con `tier: A` que el mechanic consume. |
| **`sigma:correction-agent-bounded` (Tier B downstream)** | Recibe findings que el mechanic NO pudo fixear determinísticamente. |
| **`sigma:correction-adr-draft` (Tier C downstream)** | Recibe findings que mechanic intentó fixear pero verificación falló (escalación por seguridad). |
| **Tools externos (eslint, prettier, ts-morph)** | Invocados via subprocess. El mechanic es orquestador, no implementa codemods desde cero. |
| **Auditor del Framework** | Mide M3 ≥90% y MM1-MM3 periódicamente. Cura `mechanic-handlers.yaml` cuando aparece codemod nuevo. |

---

## 6. Acceptance criteria (formales — verificables empíricamente)

### AM1 — Cobertura determinística sobre catálogo Tier A v0.1.0

**Given** los 15 rule_ids Tier A del `rules.yaml` v0.1.0 del classifier
**When** el mechanic procesa un batch que contenga findings de los 15 rule_ids
**Then** **15/15 rule_ids tienen handler implementado** (no escalan a Tier C por "handler no existe"). Tasa de escalación legítima a Tier C (por verificación fallida) debe ser <10% sobre fixture sprint1-iteracion3.

### AM2 — Verificación post-fix determinística

**Given** un finding fixeado por el mechanic
**When** se re-corre AST-check del rule_id sobre el archivo modificado
**Then** el patrón target ya no aparece. Si el patrón sigue, mechanic rollback + escala a Tier C con razón `verification-failed`.

### AM3 — Rollback automático ante regresión

**Given** un fix aplicado que rompe build/lint/tests focalizados
**When** la verificación post-fix detecta el break
**Then** mechanic revierte el archivo a su estado pre-fix (atómicamente) + emite escalación a Tier C con razón `rollback-due-to-regression`. El working tree queda limpio (no a medio aplicar).

### AM4 — Performance

**Given** un batch de 30 findings Tier A
**When** se invoca el mechanic
**Then** el wall-clock total es <60s (orquestador <5s + tools externos hasta 55s acumulados con paralelismo donde aplique).

### AM5 — Extensibilidad sin reescritura

**Given** un rule_id Tier A nuevo (ej. `R03-NEW-RULE` de validador R01-R15 futuro)
**When** se agrega un handler al registry de codemods (`mechanic-handlers.yaml` o equivalente declarativo del Paso 3)
**Then** el mechanic invoca el codemod correcto sin cambios al core Python.

### AM6 — Output estructurado y parseable

**Given** un batch procesado
**When** el mechanic termina
**Then** stdout contiene JSON válido con esquema `PatchResult[]` = `[{rule_id, file, action_hint, fix_status: applied|rolled_back|escalated_to_c, patch_summary: <diff hash o resumen>, verification: passed|failed, rollback_reason?: <string>}]`. Exit code 0 si **todo el batch** se procesó (incluso si N fueron escaladas legítimamente); exit code 1 solo en error fatal (input inválido, tool externo NO instalado, IO error).

### AM7 — Idempotencia

**Given** un batch ya procesado por el mechanic (todos los fixes aplicados o escalados)
**When** se invoca el mechanic una segunda vez sobre exactamente el mismo input
**Then** los findings cuyo patrón ya fue fixeado retornan `fix_status: noop-already-clean`. Las escalaciones a C se mantienen idénticas (mismo razonamiento). No hay efectos secundarios adicionales.

### AM8 — Métrica M3 medible (cumple ADR-011)

**Given** una corrida sobre fixture real con N findings Tier A (N≥15)
**When** se calcula `applied / total_tier_a`
**Then** el ratio reporta el M3 empírico. Target ≥90% para promoción ADR-011 v0.9 → v1.0 ACCEPTED.

### AM9 — Pre-flight check de toolbox

**Given** el mechanic arranca
**When** verifica disponibilidad de los tools requeridos (eslint, prettier, ts-morph, etc. según handlers configurados)
**Then** si falta algún tool, falla rápido con mensaje claro indicando qué falta y cómo instalarlo. NO arranca con toolbox incompleto.

---

## 7. Constraints (no negociables)

| ID | Constraint | Origen |
|----|-----------|--------|
| C1 | **Sin LLM en el path de fix**. Determinístico puro. | 1° principio rector + C1 PRD classifier |
| C2 | **Tools externos invocados via subprocess**. No re-implementa codemods desde cero. | Visión C (curator > constructor) |
| C3 | **Fix atómico por finding**: 1 finding → 1 archivo modificado (o 0 si escala). NO multi-archivo en una invocación. | A20 hexagonal — boundary chico |
| C4 | **Verificación post-fix obligatoria**: NO trust en tool externo sin verificar. | Zero trust + 2° principio rector capa correctiva |
| C5 | **Rollback determinístico**: si verificación falla, working tree vuelve a estado pre-fix. | A23 deployment safety (sin estado intermedio) |
| C6 | **Stack: Python 3.10+ stdlib + subprocess**. Sin Node runtime, sin npm install. | A20 hexagonal + C5 del PRD classifier |
| C7 | **Pre-flight check de toolbox al boot**: fail-fast si falta tool. | A22 secrets/config — fail-fast at boot |
| C8 | **Idempotente**: mismo input → mismo output. | A12 zero trust testabilidad |
| C9 | **Registro declarativo de handlers** (`mechanic-handlers.yaml` o equivalente). NO if/else hardcoded por rule_id. | Visión C + Open/Closed SOLID |
| C10 | **Sin side effects fuera de los archivos target**: no toca .git/, no muta config, no escribe en disco fuera del scope del fix. | A20 hexagonal + auditoría |

---

## 8. Métricas de éxito (cómo sabemos si funciona)

### Métricas heredadas de ADR-011

- **M3** (efectividad Tier A): ≥90% de findings clasificados como A reciben fix sin intervención humana. Medible solo cuando el mechanic existe — este PRD habilita la medición.
- **M5** (tiempo commit-to-green): baja al menos 50% vs baseline Sprint 1 (~30 min para 15 findings A → <15 min con mechanic operativo).

### Métricas propias del mechanic

- **MM1** — **Cobertura de handlers**: 15/15 rule_ids Tier A v0.1.0 tienen handler funcional. <100% = build incompleto (gap explícito en stories).
- **MM2** — **Tasa de rollback**: % de fixes que pasan a `fix_status: rolled_back`. Target <10% post-curación. >10% sostenido = handlers mal calibrados; deuda.
- **MM3** — **Tiempo de fix p95 por rule**: <500ms por finding individual (excluyendo IO de tools externos lentos). p95 alto = bottleneck en handler específico.
- **MM4** — **Tasa de escalación legítima a Tier C**: % de fixes que terminan en `escalated_to_c`. Esperado <10% (idealmente convergiendo a 0% post-curación).
- **MM5** — **Estabilidad inter-corrida** (idempotencia): segunda corrida sobre input ya fixeado debe retornar 100% `noop-already-clean`.

---

## 9. Dependencias

- **Upstream (en disco, ✅ operativo)**: `framework/sigma/finding_classifier/` v0.1.0 con `rules.yaml` curado y `cli.py` que produce `Finding[]` con `tier` + `action_hint` por finding.
- **Upstream (concepts)**: ADR-011 PROPOSED v0.9 PARTIAL declara Tier A handler como obligatorio para v1.0 ACCEPTED.
- **Downstream (consumers, no construidos aún)**:
  - `sigma:correction-agent-bounded` (Tier B) — Sprint 4. Recibe findings que mechanic NO pudo fixear (handler no existe O verification-failed O rollback).
  - `sigma:correction-adr-draft` (Tier C) — Sprint 4. Recibe findings que escalaron desde mechanic.
- **Externa runtime**: tools externos según `mechanic-handlers.yaml`:
  - **ESLint** (`npx eslint --fix`) — para TS-1, NO-VAR, VAR-TO-CONST, LET-WITHOUT-REASSIGN, UNUSED-IMPORT, IMPORT-ORDER, OBJECT-SHORTHAND
  - **Prettier** (`npx prettier --write`) — para TRAILING-WHITESPACE, MISSING-SEMI
  - **ts-morph custom codemods** — para A21-OBS-1-CONSOLE-LOG, A21-OBS-1b-DENO-CONSOLE, TS-NON-NULL-ASSERTION, TYPE-CAST-AS-ANY
  - **Custom Python script** — para MIGRATION-NAMING (rename `0001_*.sql` → `YYYYMMDDHHmm_*.sql`)
  - **SQL AST/regex tool** — para PGSQL-MISSING-VOLATILE (add `VOLATILE` marker)
- **Decisión Paso 3 pendiente**: el mapeo handler → tool concreto y el orquestador (wholesale ECC vs wrapper sigma) lo resuelve Paso 3 con evidencia empírica del solapamiento real entre ECC `build-fix` / `refactor-clean` y los 15 rule_ids Tier A.

---

## 10. Riesgos y mitigaciones

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|----|--------|-------------|---------|------------|
| RM1 | Tool externo se rompe upstream (eslint cambia formato de output) | Media | Medio | Pre-flight check + smoke test del toolbox al boot. Failure aislada por handler (un handler roto no tira el mechanic). |
| RM2 | Fix aplicado pasa verificación AST pero rompe tests downstream | Media | Alto | AM3 rollback automático + escalación a Tier C. C5 garantiza working tree limpio. |
| RM3 | Codemod custom (ts-morph) introduce bug semántico (ej. console-to-logger mal contextualizado) | Media | Alto | AM2 verifica AST post-fix; AM3 verifica tests focalizados. Doble red. |
| RM4 | Tools externos NO instalados → mechanic falla en runtime | Alta | Bajo | AM9 pre-flight check fail-fast con mensaje claro. Documentación quickstart con install steps. |
| RM5 | Race condition: dos invocaciones tocan mismo archivo | Baja | Medio | Lock por archivo (filelock) + serialización dentro de un mismo batch. Single-process es default. |
| RM6 | M3 <90% al medir → ADR-011 NO promueve a v1.0 ACCEPTED | Media | Alto | Iterar handlers (curar mechanic-handlers.yaml) + reportar gaps reales. NO bajar threshold artificialmente. |
| RM7 | Dependencia de ECC `build-fix` resulta inadecuada (decisión Paso 3 wholesale falla en evidencia) | Media | Bajo | Paso 3 evalúa empíricamente; si wholesale falla, wrapper sigma propio. Trade-off documentado. |
| RM8 | Algún rule_id Tier A queda sin handler viable (codemod inexistente para el patrón) | Baja | Medio | Re-clasificar ese rule_id como Tier B en `classifier/rules.yaml`. NO forzar fix que no existe. Trazabilidad de re-clasificaciones en LECCIONES.md. |

---

## 11. Non-goals explícitos

- ❌ NO clasifica findings. Eso es del classifier (upstream).
- ❌ NO infere codemods nuevos. Si falta handler para un rule_id Tier A, escala a Tier C con razón clara.
- ❌ NO usa LLM en path de fix. 1° principio rector.
- ❌ NO toca archivos fuera del scope del finding. C10.
- ❌ NO acumula state entre invocaciones. C8 idempotente.
- ❌ NO maneja Tier B ni Tier C. Otros PRDs.
- ❌ NO instala tools externos automáticamente. Documenta pre-requisitos; falla rápido si faltan.
- ❌ NO genera código nuevo (que no sea un fix mecánico). Si requiere generación creativa, escala a Tier B.

---

## 12. Conexión con principios rectores

| Principio | Cómo el mechanic lo encarna |
|-----------|------------------------------|
| **1° (Python traza → IA recorre → Python verifica)** | Mechanic es Python puro determinístico. Cero IA en el path. Tools externos también determinísticos (eslint, prettier). |
| **2° (3 capas)** | **Materializa explícitamente la capa CORRECTIVA**. Sin mechanic, capa correctiva sigue siendo declarativa (ADR) pero no operativa. |
| **3° (Dominio-first)** | Paso 2 de este protocolo captura activamente el mapeo rule_id → codemod tool antes del diseño técnico. |
| **4° (Auto-fix > finding cuando inequívoco)** | **Operacionaliza el principio**. Inequívoco = Tier A clasificado + handler verificable. Si verificación falla, escala a humano (no fuerza). |
| **5° (Polinización cruzada)** | Patrón del classifier (handler declarativo en YAML + Python orquestador) se replica acá. Lección de extensibilidad propagada. |
| **6° (Descubrir antes de ejecutar)** | Pre-flight check de toolbox al boot. Verificación post-fix antes de aceptar. NO asume. |
| **7° (Meta-producto recursivo)** | El mechanic es Framework, pero su `mechanic-handlers.yaml` puede aplicar a findings del propio Framework cuando GGA revise código sigma. |

---

## 13. Plan de validación (cómo verificaremos cada AC en Sprint 3 sesión 4+)

| AC | Validación |
|----|------------|
| AM1 | Corrida sobre fixture sprint1-iteracion3.json filtrado a findings Tier A. Esperado: 15/15 handlers invocados sin escalar por "handler no existe". |
| AM2 | Test unitario por handler: aplicar fix → re-correr AST-check del rule_id → patrón no debe aparecer. |
| AM3 | Test integración: mock de codemod buggy (rompe sintaxis) → verificar rollback atómico + escalación a C. |
| AM4 | Benchmark con `time` sobre fixture 30 findings A. |
| AM5 | Test extensibilidad: agregar handler ficticio para rule_id nuevo en YAML, verificar invocación sin tocar core. |
| AM6 | Validación de schema con `jsonschema` sobre output `PatchResult[]`. |
| AM7 | Test idempotencia: dos corridas consecutivas sobre mismo input, segunda retorna `noop-already-clean` para los applied. |
| AM8 | Medición M3 sobre fixture real. Reportar % real, comparar contra ≥90%. |
| AM9 | Test pre-flight: quitar tool del PATH temporalmente, verificar fail-fast con mensaje claro. |

---

## 14. Resoluciones de scope tomadas en este PRD

| Pregunta | Resolución | Justificación |
|----------|------------|---------------|
| ¿Universo cubierto inicialmente? | **15 rule_ids Tier A v0.1.0 del classifier** | Cierra empíricamente lo que el classifier ya etiqueta hoy. Extensibilidad declarativa para futuros R/G/FG. |
| ¿LLM en path de fix? | **NO** | 1° principio + C1. |
| ¿Comportamiento ante handler faltante? | **Escala a Tier C** (NO improvisa) | Conservador. RM8 contempla re-clasificación si el patrón es estructuralmente no-fixable. |
| ¿Verificación post-fix? | **Obligatoria + Rollback si falla** | 4° principio "cuando inequívoco" requiere certeza, no esperanza. |
| ¿Multi-archivo en un fix? | **NO** (escala a Tier B) | C3 atomicidad + A20 boundary chico. |
| ¿Instalación de tools externos? | **Out of scope** (operador responsable, pre-flight check fail-fast) | Visión C: composición sobre stack ya instalado. |
| ¿Stack? | **Python 3.10+ stdlib + subprocess** | Mismo patrón que classifier. C6. |
| ¿Decisión wholesale ECC vs wrapper sigma? | **Diferida a Paso 3** | El PRD describe QUÉ, no CÓMO. Paso 3 evalúa empíricamente con evidencia. |

---

## 15. Siguiente paso (Paso 2 del protocolo)

Capturar **activamente el dominio**: mapeo rule_id → codemod tool por cada uno de los 15 rule_ids Tier A, con tool externo concreto identificado (eslint plugin específico, ts-morph custom script, etc.) y verificación post-fix definida.

Output Paso 2:
- `docs/dominio/auto-fix-mechanic-rules.yaml.draft` — registro declarativo `rule_id → handler`
- `docs/dominio/codemod-toolbox.md` — catálogo de tools externos requeridos + comandos + verificación

---

**Este PRD es prerrequisito de**: `sigma:auto-fix-mechanic` build (Sprint 3 sesión 4+).
**Este PRD bloquea**: Paso 2 (dominio), Paso 3 (arquitectura + decisión wholesale ECC vs wrapper sigma), Paso 4 (stories), Paso 5 (audit + bump ADR-011 v0.9 → v1.0 candidato).
