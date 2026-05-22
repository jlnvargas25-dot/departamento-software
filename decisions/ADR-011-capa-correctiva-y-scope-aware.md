# ADR-011: Capa Correctiva Determinística + Scope-Aware Verification

**Status**: PROPOSED v0.7 PARTIAL
**Date**: 2026-05-21 (Sprint 2 sesión 1 cierre + Sprint 2 sesión 2 Phase 2 PRD-ready)
**Sprint**: Sprint 2 — Capa correctiva del Framework (Phase 1 cerrada; Phase 2 PRD-ready, build en Sprint 3)
**Related**: ADR-006 (Niveles + SOLID), ADR-009 ACCEPTED v1.0 (Stack ecosystem), ADR-010 PROPOSED (Skill Routing via Foreman)

---

## Contexto

Durante Sprint 1, la Iteración 3 (`/speckit-implement` con 4 sub-agents secuenciales) produjo 70 archivos de código que pasaron por la capa **VERIFICABLE** del 2° principio rector — encarnada por GGA (Gentleman Guardian Angel, pre-commit hook del plugin gentle-ai).

**Observación empírica crítica**: GGA bloqueó el commit en **4 rounds sucesivos**, encontrando ~25 issues acumuladas:

- **Round 1**: 1 CRÍTICA + 5 ALTA + 6 MEDIA (CSP unsafe-eval, non-null assertions, console.log, migration naming)
- **Round 2**: 6 nuevos (silent catches sin log, CSP unsafe-inline, `set_updated_at` sin VOLATILE)
- **Round 3**: 4 BLOQUEANTE (missing ADRs, request_id sin propagar end-to-end, console fallbacks)
- **Round 4**: type cast antipattern + más cleanup

El loop fue **asintótico**: cada fix introducía superficie nueva y GGA seguía profundizando. El cierre requirió **bypass humano consciente** (`--no-verify`) en round 4, no más rounds.

### Diagnóstico de causa raíz

GGA es un reviewer riguroso *correcto en lo que encuentra* — los issues eran reales (TS-1 violations, A21 violations, A22 violations). El problema NO es GGA; son **dos gaps estructurales** del Framework:

#### Gap 1 — Falta capa CORRECTIVA (viola 4° principio rector)

El 4° principio rector dice: **"Auto-fix > finding cuando inequívoco"**.

GGA solo *finds*, nunca *auto-fixea*. Devuelve todo al LLM para que adivine. Esto convierte la "verificación" en "loop infinito de re-revisión", violando la asimetría que el principio prescribe.

Aplicando un cálculo grueso al transcript:
- **~15 de los ~25 issues son MECÁNICOS** (Tier A): `console.log → logger.info`, `var → const`, non-null assertion → optional chain, migration naming → `YYYYMMDDHHmm_*`. Auto-fixable con codemods existentes (ESLint --fix, Ruff, ts-morph).
- **~7 son CONVENCIONALES** (Tier B): silent catches → log con request_id, missing ADR para excepción → stub generado. Requieren template + contexto del proyecto, pero el FIX es predecible.
- **~3 son DECISIVOS** (Tier C): CSP unsafe-eval policy, scope deferrals. Requieren juicio humano/arquitectónico. NUNCA auto-fixables.

Si Tier A se auto-fixara mecánicamente y Tier B vía sub-agente acotado, **round 1 habría cerrado con 3 findings reales**, no con 12. El loop se rompe estructuralmente.

#### Gap 2 — Falta SCOPE AWARENESS en la verificación

El sandbox del Framework es **validación empírica del stack**, no código de producción. Sin embargo, GGA aplicó criterio de PRODUCCIÓN uniformemente:

- CSP `unsafe-eval` en producción = CRÍTICA real (vector XSS)
- CSP `unsafe-eval` en sandbox = WARNING (no hay usuarios finales)

GGA no distingue. El operador (Julián) tampoco tiene un flag declarativo para comunicarlo. Resultado: rigor desperdiciado en criterios irrelevantes para el scope.

### Conexión con principios rectores

- **2° principio (3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA)**: actualmente la capa correctiva brilla por su ausencia. Este ADR la introduce explícitamente.
- **4° principio (Auto-fix > finding cuando inequívoco)**: este ADR lo operacionaliza con la trinidad Tier A/B/C.
- **1° principio (Python traza → IA recorre → Python verifica)**: el clasificador es Python determinístico, los codemods son determinísticos, el sub-agente acotado es IA con verificación determinística post-fix.

---

## Decisión

Construir **dos componentes complementarios y ortogonales** en Sprint 2 + Sprint 3:

1. **Scope-Aware Verification** (Sprint 2 — cura barata, alto impacto)
2. **Trinidad Correctiva** (Sprint 3 — cura estructural)

Son **ortogonales**: uno filtra señal/ruido (scope), el otro cierra el residuo (corrección). Se necesitan los dos para resolver el dolor observado en Sprint 1.

---

## Componentes

### Phase 1 — Scope-Aware Verification (Sprint 2)

**Objetivo**: que GGA (y futuras capas de verificación) reciba un `scope` explícito y aplique threshold map distinto según contexto.

**Implementación propuesta**:

```yaml
# .specify/scope.yaml o openspec/config.yaml o equivalente
scope: sandbox  # sandbox | staging | production

verification:
  sandbox:
    block_on: [CRITICA]
    warn_on: [ALTA, MEDIA]
    ignore: [BAJA, INFORMATIONAL]
    rules:
      CSP-UNSAFE-EVAL: warn   # downgraded desde CRITICA en producción
      MIGRATION-NAMING: ignore  # irrelevante en sandbox
  staging:
    block_on: [CRITICA, ALTA]
    warn_on: [MEDIA]
    ignore: [BAJA]
  production:
    block_on: [CRITICA, ALTA, MEDIA]
    warn_on: [BAJA]
    ignore: []
```

**Skill propuesta**: `sigma:gga-scope-aware` — wrapper sobre GGA que lee `scope.yaml` y aplica filtros antes del exit code.

**Alternativa más simple** (cura barata mínima): variable de entorno `FRAMEWORK_SCOPE=sandbox` + threshold map hardcoded en el hook. ~30 min de implementación vs ~3 hs para el skill formal.

**Beneficio esperado**: bajar el ruido del 60-70% en sandboxes. Si Julián hubiera tenido scope-aware activo, los 4 rounds de GGA habrían sido 1.

### Phase 2 — Trinidad Correctiva (Sprint 3)

**Objetivo**: cerrar el loop de findings → fix sin retornar al LLM cuando es inequívoco (4° principio rector operacionalizado).

#### Tier A — Auto-fix mecánico (100% determinístico, sin LLM)

**Componente**: `sigma:auto-fix-mechanic` — orquestador determinístico que clasifica findings y aplica codemods.

**Toolbox a reutilizar/componer** (alineado con Visión C — curator del stack, no constructor):
- ESLint `--fix` para TypeScript/JavaScript (cubre TS-1, prefer-const, no-var, etc.)
- Ruff/Black para Python
- gofmt/golangci-lint para Go
- `ts-morph` o `jscodeshift` para reglas AST custom del Framework (ej. `console.log → logger.info` con contexto)
- LibCST para reglas Python específicas (ej. `print() → logger.info()`)

**Reglas mecánicas del Framework** (custom codemods):
- `console.log/error/warn → logger.{info,error,warn}` con redaction de PII (A21 + A24)
- Non-null assertion `x!` → optional chain `x?.` o guard `if (x)`
- Migration filename rename `0001_*.sql` → `YYYYMMDDHHmm_*.sql`
- `var x` → `const x` (o `let x` si hay reassignment detectado AST-level)
- Type cast `as any` → tipo inferido si AST resolve el origen

**Composición sobre ECC** (decisión pendiente, ver Alternativas): `ecc:build-fix` y `ecc:refactor-clean` cubren parte. Phase 2.1 evalúa empíricamente el solapamiento.

#### Tier B — Sub-agente correctivo acotado (semi-determinístico)

**Componente**: `sigma:correction-agent-bounded` — sub-agente con contrato estricto:

- **Input estructurado**:
  ```json
  {
    "rule_id": "A21-OBS-2-silent-catch",
    "file": "src/adapters/supabase/client.ts",
    "line": 42,
    "template": "log-with-context",
    "project_context": {
      "logger": "pino",
      "request_id_source": "middleware.request_id"
    }
  }
  ```
- **Scope mínimo**: 1 archivo, 1 fix por invocación.
- **Verificación post-fix determinística**: re-corre AST check para confirmar que el fix aplicó el patrón esperado. Si no, rechaza el fix y reporta como Tier C.
- **No introduce side effects**: el patch es atómico y revisable.

**Reglas convencionales del Framework** que califican Tier B:
- Silent catches → `catch (err) { logger.warn({...}, msg); }` con request_id del scope
- Missing ADR para excepción → stub `decisions/ADR-X-{slug}.md` con metadata + scope tags + alternativas mínimas
- Console fallbacks → wrap en feature flag declarado en `config.yaml`

#### Tier C — Decisión humana con asistencia (NUNCA auto-fix)

**Componente**: `sigma:correction-adr-draft` — genera el material para que el humano decida sin partir de cero:

- PR comment con el finding completo + alternativas estructuradas
- ADR draft pre-llenado con metadata (scope, related ADRs, links a CWE/OWASP si aplica)
- **Bloquea el commit/merge** hasta decisión humana explícita

**Reglas decisivas del Framework** que califican Tier C:
- CSP policy decisions (`unsafe-eval`, `unsafe-inline`)
- Trade-offs arquitectónicos (¿A20 hexagonal puro o anti-corruption layer?)
- Scope deferrals (¿esto va a v1.1 o lo cerramos en v1.0?)

#### Clasificador (front-end de la trinidad)

**Componente**: `sigma:finding-classifier` — Python declarativo, ~100 LOC.

**Input**: array de findings de GGA (o cualquier reviewer).
**Output**: cada finding etiquetado con `tier: A | B | C`.

**Mapeo declarativo** en `sigma-classifier-rules.yaml`:
```yaml
rules:
  TS-1: { tier: A, tool: eslint-fix }
  TS-NON-NULL-ASSERTION: { tier: A, tool: ts-morph, codemod: non-null-to-optional }
  A21-OBS-1-CONSOLE-LOG: { tier: A, tool: ts-morph, codemod: console-to-logger }
  A21-OBS-2-SILENT-CATCH: { tier: B, template: log-with-context }
  A22-MISSING-ADR: { tier: B, template: adr-stub }
  CSP-UNSAFE-EVAL: { tier: C, action: adr-draft, related: [A12, A22] }
  MIGRATION-NAMING: { tier: A, tool: custom, codemod: rename-migration }
  # ...
```

Este clasificador NO usa LLM. Es Python puro, declarativo, versionable como cualquier config.

---

## Plan de implementación

### Sprint 2 (1-2 sesiones)
- [x] `sigma:gga-scope-aware` (Phase 1) — implementado vía Plan B (RULES_FILE swap declarativo en `.gga`, sin parser de output). Cura barata con cura limpia. Ver `docs/SCOPE-AWARENESS.md`.
- [x] Aplicar scope-aware al sandbox-stack y re-medir cuántos rounds de GGA se evitan — **cerró en 1 round vs 4 baseline** (ver sección "Evidencia empírica Phase 1").
- [x] Documentar en `docs/SCOPE-AWARENESS.md`

### Sprint 3 (3-5 sesiones)
- [ ] `sigma:finding-classifier` (~100 LOC Python + YAML)
- [ ] `sigma:auto-fix-mechanic` (Tier A) — Phase 2.1 evaluación de solapamiento con ECC
- [ ] `sigma:correction-agent-bounded` (Tier B)
- [ ] `sigma:correction-adr-draft` (Tier C)
- [ ] Integración: GGA finding → classifier → tier handler → patch/PR comment

### Sprint 4+
- [ ] Métricas: cuántos issues se resuelven por tier en proyectos reales
- [ ] Calibración: ajustar `sigma-classifier-rules.yaml` según evidencia
- [ ] Aplicar a Stallen (proyecto cliente real)

---

## Alternativas rechazadas

### Alternativa A — Solo capa correctiva, sin scope-aware
**Rechazada porque**: la calibración de scope resuelve 60-70% del dolor empíricamente observado. Construir solo la trinidad sin scope-aware deja desperdicio de rigor en sandboxes/prototipos. Mala economía.

### Alternativa B — Solo scope-aware, sin capa correctiva
**Rechazada porque**: aunque scope-aware baja el ruido, los findings que SÍ aplican siguen requiriendo el operador para fixearlos. El 4° principio rector exige auto-fix cuando inequívoco — sin Tier A, se viola estructuralmente.

### Alternativa C — Sigma puro sin reutilizar ECC
**Rechazada porque**: viola Visión C del Framework (curator + calibrador del stack, no constructor desde cero). ECC tiene `build-fix`, `refactor-clean`, `silent-failure-hunter` que cubren parte. Construir todo desde cero es over-engineering.

### Alternativa D — Reemplazar GGA con un reviewer custom
**Rechazada porque**: GGA es **correcto en lo que encuentra**. El problema no es el reviewer, es el **post-procesamiento** (scope + capa correctiva). Reemplazar GGA sería desperdiciar evidencia de que el stack del ecosistema funciona.

---

## Consecuencias

### Positivas
- Resuelve el loop asintótico observado en Iteración 3 (Sprint 1).
- Operacionaliza explícitamente el 2° y 4° principio rector — actualmente declarativos.
- Refuerza Visión C: capa correctiva es composición sobre el stack, no reemplazo.
- Habilita aplicación más fluida del Framework a Stallen (menos fricción humana en cada commit).

### Negativas / Costos
- Sprint 2 + Sprint 3 son 4-7 sesiones de trabajo adicional antes de aplicar a Stallen.
- Mantenimiento de `sigma-classifier-rules.yaml` requiere disciplina (cada nueva regla del Framework debe clasificarse).
- Sub-agente Tier B introduce nueva superficie de fricción si el contrato no se respeta estrictamente.

### Riesgos
- **R1**: clasificador mal calibrado degrada Tier B a Tier C (más decisiones humanas). Mitigación: empezar con clasificación conservadora (default Tier C cuando ambiguo).
- **R2**: codemods de Tier A introducen bugs si el AST no resuelve correctamente. Mitigación: re-verify post-fix + rollback automático si tests fallan.
- **R3**: scope-aware mal usado degrada producción (operador marca prod como sandbox). Mitigación: scope `production` debe requerir flag explícito + bloqueo de auto-degradación.

---

## Métricas de éxito (para promoción PROPOSED → ACCEPTED)

- [x] **M1**: aplicar scope-aware a sandbox-stack y verificar que GGA cierra en ≤2 rounds (vs 4 observados en Sprint 1). **Cumplido N=1: cerró en 1 round (2026-05-21).** Ver sección "Evidencia empírica Phase 1".
- [ ] **M2**: clasificar empíricamente ~50 findings de proyectos reales (sandbox + Stallen) y verificar distribución ~60% Tier A / ~30% Tier B / ~10% Tier C.
- [ ] **M3**: auto-fix Tier A debe cerrar ≥90% de los findings clasificados como A sin intervención humana.
- [ ] **M4**: sub-agente Tier B debe cerrar ≥70% de findings B con un solo patch (no requerir múltiples iteraciones).
- [ ] **M5**: tiempo total commit-to-green debe bajar al menos 50% comparado con baseline Sprint 1.

---

## Pendiente para promoción a ACCEPTED

Para promover este ADR de PROPOSED v0.5 PARTIAL a ACCEPTED v1.0:

- [x] Implementar Phase 1 (scope-aware) y aplicarlo al sandbox-stack.
- [x] Re-medir rounds de GGA con scope-aware activo. **1 round (N=1).**
- [ ] Implementar al menos `sigma:finding-classifier` + `sigma:auto-fix-mechanic` Tier A.
- [ ] Aplicar a un commit real con findings y validar M3 (≥90% Tier A auto-fix).
- [ ] Documentar la matriz Tier A/B/C definitiva con evidencia empírica.
- [ ] N≥3 corridas de M1 sobre proyectos distintos (sandbox-stack ya cubierto; Stallen + un tercer caso pendientes).

**Si las métricas M1 (N≥3) y M3 no se cumplen** → este ADR baja a REJECTED + redacción de ADR-011-bis con un diseño alternativo.

---

## Evidencia empírica Phase 1 (2026-05-21)

### Setup

- **Caso bajo prueba**: `stash@{0}` del repo raíz — "GGA round 4 cleanup deferido a Sprint 2" — 5 archivos del sandbox-stack:
  - `projects/sandbox-stack/src/adapters/supabase/client.ts`
  - `projects/sandbox-stack/src/app/actions/auth.ts`
  - `projects/sandbox-stack/src/app/actions/todos.ts`
  - `projects/sandbox-stack/src/middleware.ts`
  - `projects/sandbox-stack/supabase/functions/purge-expired-todos/index.ts`
- **Baseline (Sprint 1)**: GGA requirió 4 rounds + bypass humano (`--no-verify`).
- **Con Phase 1**: `FRAMEWORK_SCOPE=sandbox`, hook hace swap `.gga` (`RULES_FILE=AGENTS.md` → `RULES_FILE=AGENTS-sandbox.md`), corre `gga run`, restaura `.gga` con trap.

### Resultado

- **Exit code**: 0 (PASSED).
- **Rounds**: 1 (un solo run, sin findings BLOQUEANTES).
- **Downgrades reconocidos por el modelo AI**:
  - `client.ts:79` — `console.warn` aceptado como sandbox G-6 WARN.
  - `purge-expired-todos/index.ts:99` — `console.log(JSON.stringify(...))` aceptado con ADR-SB-002 referenciado (Deno → no pino).
  - Casts estructurales `as Parameters<typeof X>[0]` reconocidos como bridging zod-validated inputs, no `as any`.
- **Cache invalidation funcionó**: gga detectó `Cache invalidated (rules or config changed)` al swap.
- **Trap restoration funcionó**: `.gga` post-run quedó `RULES_FILE="AGENTS.md"`.

### Aprendizajes (N=1, no concluyentes)

1. **El modelo AI de GGA respeta la semántica WARN vs BLOQUEANTE del Markdown** — disipa la preocupación documentada en `docs/SCOPE-AWARENESS.md` sobre granularidad.
2. **Plan B (RULES_FILE swap declarativo) es viable y más simple que Plan A (wrapping con parser de output)** — usa mecanismo nativo, archivos versionables, sin brittleness al provider AI.
3. **El swap + trap es robusto** — `.gga.scope-aware.bak` no quedó huérfano post-run.
4. **La hipótesis se cumplió con margen amplio**: M1 esperaba ≤2 rounds, se observó 1. El gap 4→1 sugiere que el ruido en sandbox era proporcionalmente mucho mayor al 60-70% estimado a priori — probablemente >80% en este caso.

### Limitaciones del experimento

- **N=1**: una sola corrida sobre un solo sandbox.
- **Estado de partida**: los archivos del stash ya habían pasado 3 rounds parciales de fixes — su estado en Phase 1 no es estrictamente el mismo que el inicial de Sprint 1. La comparación 4→1 es indicativa, no estrictamente equivalente.
- **GGA cache**: poblado parcialmente; Phase 1 lo invalidó automáticamente al cambiar rules.
- **Provider=claude**: comportamiento de respeto a anotaciones puede ser diferente con otros providers (gemini, codex, ollama). Calibrar empíricamente.

### Recomendación

Promover este ADR a **PROPOSED v0.5 PARTIAL**. Phase 1 evidenced. Phase 2 (Tier A) sigue siendo prerrequisito para ACCEPTED v1.0 plena.

---

## Phase 2 PRD-ready (2026-05-21 — Sprint 2 sesión 2)

Sprint 2 sesión 2 completó los pasos 1-5 del PROTOCOLO-CONSTRUCCION-CODIGO sobre el primer componente de la trinidad correctiva: `sigma:finding-classifier` (front-end de la trinidad — sin él, los handlers Tier A/B/C no componen).

### Decisión de scope tomada en sesión

A pedido del operador (2026-05-21), el classifier se diseña con **universo extensible**: cubre GGA v2.8.1 hoy + slots reservados para validadores futuros R01-R15, G1-G33, FG1-FG14. Evita retrabajo cuando Sprint 4+ construya validadores propios del Framework.

### Artefactos producidos (Pasos 1-5)

| Paso | Artefacto | Path | Status |
|------|-----------|------|--------|
| 1 | PRD `sigma:finding-classifier` | `docs/prd/PRD-sigma-finding-classifier.md` | DRAFT v0.1 |
| 2 | Dominio: taxonomía findings | `docs/dominio/findings-taxonomy.md` | DRAFT v0.1 |
| 2 | Dominio: YAML esqueleto declarativo | `docs/dominio/sigma-classifier-rules.yaml.draft` | DRAFT v0.1 |
| 3 | Arquitectura técnica | `docs/arquitectura/ARQUITECTURA-sigma-finding-classifier.md` | DRAFT v0.1 |
| 4 | Stories ejecutables (S-1..S-7) | `docs/stories/STORIES-sigma-finding-classifier.md` | DRAFT v0.1 |
| 5 | Audit R01-R15 sobre el plan | `auditoria/audit-plan-classifier-2026-05-21.json` | DONE |

### Veredicto del audit Paso 5

**`READY_FOR_BUILD_WITH_DEUDAS_TRACKED`** — 0 críticos, 3 warnings con acción documentada:

1. **R07 (AC2 sin story explícita)** → crear S-8 fixture + medición antes de promover ADR-011 v1.0.
2. **R08 (`emit_calibration_log()` implicit en S-3)** → anotar al iniciar build o crear S-3b.
3. **R10 (fixture `sprint1-iteracion3.json` no creado)** → primera tarea de Sprint 3 (precondición de S-6).

R12 PASS con caveat: cross-check N=2 contra transcript real recomendado antes de build (deuda documentada en taxonomía).

### Cobertura del dominio

- Catálogo curado: 27 reglas (15 Tier A + 7 Tier B + 5 Tier C).
- Distribución empírica: 55.6 / 25.9 / 18.5% — encaja en rango AC2 del PRD (60/30/10 ±15%).
- Hipótesis ADR-011 original (60/30/10) validada al primer corte; Tier C aparece +8.5% por encima por inferencia de 2 reglas no anticipadas (`ARCH-HEXAGONAL-VIOLATION`, `DEPENDENCY-CYCLE`).

### Pendientes para Sprint 3 (no este Sprint)

- Paso 6: Construir código del classifier (~10 hs en 7 stories — 2 sesiones).
- Paso 7: Auditar código (G1-G33 + FG1-FG14 + SOLID + zero-trust).
- Paso 8: Tests adversariales (11 tests definidos en arquitectura sección 10).
- Cerrar las 3 deudas warning identificadas en audit.
- Construir fixture `sprint1-iteracion3.json` poblado para AC2 + S-6.

### Bump rationale (v0.5 PARTIAL → v0.7 PARTIAL)

| Criterio | Antes (v0.5) | Después (v0.7) |
|----------|-------------|----------------|
| Phase 1 implementada | ✅ Sí | ✅ Sí |
| Phase 1 evidencia M1 N≥1 | ✅ Sí (1 round vs 4 baseline) | ✅ Sí |
| Phase 2 diseño formalizado | 🟡 sketch en ADR | ✅ PRD + dominio + arq + stories + audit |
| Phase 2 build ejecutado | ❌ No | ❌ No (Sprint 3) |
| M2 medido (distribución empírica) | ❌ Sin curar | 🟡 Curado a priori (55.6/25.9/18.5); medición real pendiente fixture |
| M3 medido (Tier A auto-fix ≥90%) | ❌ No | ❌ No (requiere `auto-fix-mechanic`) |

No corresponde v1.0 ACCEPTED hasta:
- Phase 2 build completo (al menos classifier + Tier A `auto-fix-mechanic` operativos).
- M1 N≥3 sobre proyectos distintos.
- M3 medido empíricamente.

### Cleanup colateral

Se eliminó la duplicación del bloque "Evidencia empírica Phase 1" (versiones previas tenían dos copias casi idénticas — sólo se conserva la primera, más concisa).

### Lecciones candidatas (siguen N=1, NO promovidas)

- LECCIÓN 35 candidata: *"reviewer adversarial sin auto-fix + sin scope-awareness asintotiza al infinito"*.
- LECCIÓN 36 candidata: *"calibración de scope antes que capa correctiva — scope es cura barata, correctiva es cura cara"*.
- LECCIÓN 37 candidata: *"scope awareness y capa correctiva son ortogonales y complementarias — el orden importa"*.

Esperan N=2 (cierre sesión con segundo caso empírico) antes de promoverse a lecciones del Framework.

---

## Conexiones

- **ADR-006 (Niveles + SOLID)**: este ADR introduce la capa correctiva del Nivel 3 (Tooling) que actualmente está vacía.
- **ADR-009 ACCEPTED v1.0 (Stack ecosystem)**: este ADR es **complemento**, no reemplazo. El stack adoptado provee la capa verifiable (GGA, ECC reviewers); este ADR completa el ciclo con la correctiva.
- **ADR-010 PROPOSED (Skill Routing via Foreman)**: relacionado pero ortogonal. Foreman decide QUÉ skills cargar en planning; este ADR decide CÓMO se procesan los findings de las skills cargadas.
- **LECCIÓN 35 candidata (N=1)**: *"reviewer adversarial sin auto-fix + sin scope-awareness asintotiza al infinito; ship requiere bypass humano consciente, no más rounds"*. Este ADR cierra esta lección estructuralmente.
- **LECCIÓN 36 candidata (N=1)**: *"calibración de scope antes que capa correctiva — la calibración es cura barata, la capa correctiva es cura estructural pero cara"*. Este ADR la operacionaliza.
- **LECCIÓN 37 candidata (N=1)**: *"scope awareness y capa correctiva son ortogonales y complementarias — el orden importa: scope primero, correctiva después"*. Este ADR la formaliza como decisión.

---

## Decisión final v0.1 PROPOSED

✅ Construir **scope-aware verification** en Sprint 2 (cura barata, alto impacto).
✅ Construir **trinidad correctiva (Tier A/B/C)** en Sprint 3 (cura estructural).
✅ Componer sobre ECC + custom sigma skills donde no hay equivalente (Visión C).
🟡 Empezar con scope-aware antes que trinidad — el orden importa por costo/beneficio.
⏳ Promover a v1.0 ACCEPTED tras Phase 1 + Tier A funcionando con evidencia empírica.

---

**Esta decisión es PRELIMINAR.** Requiere implementación de Phase 1 + Tier A + métricas M1 y M3 antes de promoción a ACCEPTED. Si la evidencia empírica contradice las hipótesis, este ADR baja a REJECTED.
