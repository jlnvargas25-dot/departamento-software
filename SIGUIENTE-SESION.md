# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico post-Sprint 3 sesión 3 (BLOQUE 1 sync completado + BLOQUE 2 pasos 1-5 de `sigma:auto-fix-mechanic`).
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-24 (Sprint 3 sesión 5 cerrada — auto-fix-mechanic build end-to-end completo, 181 tests PASS, R08 cerrada)
**Cliente recomendado próxima sesión**: **Claude Code CLI** dentro de `C:\DEPARTAMENTO-SOFTWARE\` (skills speckit-* + ecc:* + claude-mem:* + sdd-* + superpowers:* todos cargados)
**Versión**: 7.2 (post Sprint 3 sesión 5 — mechanic end-to-end operativo; audits Paso 7+8 en sesión 6)

---

## ✅ SPRINT 3 SESIÓN 5 CERRADA (2026-05-24)

**`sigma:auto_fix_mechanic` BUILD END-TO-END COMPLETO** — pasos 6 del PROTOCOLO ejecutado sobre la segunda mitad del plan auditado. Trinidad correctiva ya tiene 2/3 componentes operativos. Codemods custom funcionales con smoke tests; audits Paso 7+8 diferidos a sesión 6.

### Stories completadas

| Story | Descripción | Tests | LOC prod |
|-------|-------------|-------|----------|
| S-6.1 | Codemod `non_null_to_optional.js` (ts-morph, contextual PropertyAccess/ElementAccess) | smoke | ~110 |
| S-6.2 | Codemod `console_to_logger.js` (ts-morph, console.* → logger.*, inject import) | smoke | ~110 |
| S-6.3 | Codemod `console_to_json_structured.js` Deno (Edge Functions scope, `serializeErr` helper inline → **R08 CERRADA**) | smoke | ~170 |
| S-6.4 | Codemod `infer_type_from_context.js` (conservador, type checker inference, escalation if unresolvable) | smoke | ~80 |
| S-7 | Codemods Python: `rename_migration_timestamp.py` (git log priority, DRY-RUN, rollback log) + `add_volatile_marker.py` (regex SQL, idempotente) | smoke | ~250 |
| S-8 | CLI `sigma-mechanic` (stdin/stdout, --metrics MM1-MM5) + 9 tests CLI + 3 M3 empirical + 3 idempotency + 3 extensibility | 18 | ~150 |

### Métricas finales sesión 5

- **181 tests PASS en 5.4s** (73 classifier + 90 mechanic S-1..S-5 sesión 4 + 18 mechanic S-8 sesión 5)
- ~870 LOC adicionales (~150 Python CLI + ~720 codemods) → total mechanic ~1600 LOC prod + ~1100 tests
- 6 codemods funcionales validados via smoke tests manuales (ts-morph 22.0.0 + Python stdlib)
- Toolbox completo: 8 eslint + 2 prettier + 4 ts-morph + 2 python = 16 tools cubriendo 15 rule_ids Tier A
- **R08 audit Paso 5 CERRADA**: `serializeErr()` helper inline en `console_to_json_structured.js`

### Smoke tests manuales ejecutados (validación funcional)

- `non_null_to_optional` sobre `non_null.ts`: applied=4 remaining=1 (1 standalone `user!.email!` escala correctamente)
- `console_to_logger` sobre `console_logger.ts`: applied=4 remaining=0, import injectado `@/lib/logger`
- `console_to_json_structured` sobre `supabase/functions/.../index.ts`: applied=3 remaining=0, `serializeErr` helper presente, error case con `msg + err` separados correctamente
- `infer_type_from_context` sobre `type_cast.ts`: applied=2 (literal shape + ApiResponse), escalated=1 (`value as any` con value:unknown)
- `add_volatile_marker` sobre `missing_volatile.sql`: applied=2, control STABLE preservado, verify exit 0
- `rename_migration_timestamp` sobre `0001_initial.sql`: DRY-RUN print mapping, apply renombra, verify exit 0

### Decisiones de implementación tomadas

- **ts-morph 22.0.0 instalado local en `codemods/`** (no global). `node_modules/` + `package-lock.json` gitignored.
- **Apply-mode siempre exit 0**: si un codemod escala parcialmente, no causa rollback inmediato; verify-mode posterior detecta residuo y orchestrator decide. Alineado con patrón S-5 (atomicidad delegada a orchestrator via FileSnapshot).
- **Scope guard por path heurística**: `console_to_logger` skip si file está en `supabase/functions/`; `console_to_json_structured` skip si file NO está en `supabase/functions/`. Ortogonal y declarativo.
- **`infer_type_from_context` conservador**: skip si tipo inferido es `any`/`unknown`/`never` o >120 chars (legibilidad + brittleness).
- **`serializeErr` inline** (no en file compartido): mantiene atomicidad por-file (cada codemod auto-contenido).
- **M3 sandbox threshold ≥0.5** (vs ≥0.9 producción): tests usan handlers stub Python en lugar de stack TS real; M3 real >90% se medirá en E2E con stack instalado.

### Deudas tracking

- **R08** ✅ CERRADA en S-6.3.
- **DEUDA-CODEMODS-NO-PYTEST-AUTOMATED** *(NUEVA, menor)*: smoke tests de codemods son manuales (Bash). Para integración CI, agregar `test_codemods_smoke.py` con `pytest.mark.skipif` cuando Node falta. Diferida a sesión 6 audit.
- **DEUDA-M3-REAL-NOT-MEASURED**: M3 real (>90% sobre stack TS) requiere environment con ESLint/Prettier/ts-morph reales aplicables sobre proyecto target. Diferida a integración Stallen o sandbox-stack iteration 4.

### Próxima sesión (Sprint 3 sesión 6)

**Audit Paso 7 + Paso 8 + M3 real opcional**:
- Audit Paso 7 (G1-G33 + FG1-FG14 + SOLID + zero-trust) sobre los 16 archivos del mechanic
- Audit Paso 8 (15 categorías adversariales documentadas en arquitectura sec 9.1)
- Si Paso 7 + 8 PASS sin críticos: ADR-011 candidato a **promover v0.9 PARTIAL → v1.0 ACCEPTED** (al menos para classifier + mechanic, dejando Tier B/C para v1.1)
- (Opcional) M3 real sobre sandbox-stack si environment lo permite

**Validación L38 N=4**: si commit final sesión 5 + commits sesión 6 pasan GGA en 1 round, L38 acumula evidencia adicional intra-proyecto.

---

## ✅ SPRINT 3 SESIÓN 4 CERRADA (2026-05-24)

**`sigma:auto_fix_mechanic` S-1..S-5 core OPERATIVO** — pasos 6 del PROTOCOLO ejecutado sobre la mitad core del plan auditado en sesión 3. Build completo + commit + push pusheado a origin/main.

### Stories completadas

| Story | Descripción | Tests | LOC prod |
|-------|-------------|-------|----------|
| S-1 | Foundation: pyproject + models + loader + 8 fixtures (R10 cerrada) | 30 | ~150 |
| S-2 | Pre-flight check toolbox (AM9) + Invoker (subprocess wrapper) | 18 | ~130 |
| S-3 | Snapshot + rollback atómico (R-5 reversibilidad) + threading.Lock intra-process | 14 | ~110 |
| S-4 | Verifier dispatcher 5 methods (re-run-eslint, prettier-check, ast-check, filename-regex, regex-grep) | 17 | ~160 |
| S-5 | Orchestrator + escalation logic (4 casos del flow + AM7 idempotencia) | 11 | ~180 |

**Métricas finales sesión 4**:
- **90 tests mechanic PASS en 3.4s** (suite total 163: 73 classifier sin regresión + 90 mechanic)
- ~730 LOC producción + ~1100 LOC tests (ratio 1.5:1)
- 8 fixture files target con cobertura 15/15 rule_ids Tier A

### Precondiciones audit cerradas durante el build

- **R04 — filelock**: ✅ Cerrada via stdlib `threading.Lock` intra-process (cero dep externa, consistente con classifier). Cross-process (fcntl/msvcrt) diferido a Sprint 5+ si surge necesidad real.
- **R08 — `serializeErr()` helper**: ⏳ Pospuesto a S-6 sesión 5 (codemod ts-morph `console_to_json_structured.ts` aún no construido).
- **R10 — fixture target files**: ✅ Cerrada con 8 archivos sintéticos en `framework/sigma/auto_fix_mechanic/tests/fixtures/target_files/` cubriendo los 15 rule_ids.

### Decisiones de implementación tomadas

- **Lock cross-platform**: `threading.Lock` + dict global por path absoluto (intra-process suficiente para Sprint 3). Documentado en `snapshot.py` como diferimiento explícito.
- **shlex.split**: `posix=True` (no `posix=False`) — Windows-compat con paths quotados (`"C:\Users\Windows 11\..."`); previene `[WinError 5]` por quotes literales en args.
- **Reemplazo `<file>` POST-split**: paths con espacios en `tmp_path` (pytest) quedan como single arg sin necesidad de quote escaping.
- **Verification timeout default 15s** (vs invocación 30s) — verify es más liviano (re-run del tool en modo check).
- **Logging estructurado a stderr**: `[mechanic] event=<x> rule_id=<y> file=<z>:<n> reason=<r>` por finding — parseable, sin acoplar a logger framework específico.

### Próxima sesión (Sprint 3 sesión 5)

**S-6..S-8 + audits**:
- S-6: 4 codemods ts-morph custom (non_null_to_optional, console_to_logger, console_to_json_structured con `serializeErr()` helper [R08 cerrada], infer_type_from_context) — ~4hs
- S-7: 2 codemods Python custom (rename_migration_timestamp, add_volatile_marker) — ~1.5hs
- S-8: CLI `sigma-mechanic` + M3 empirical measurement sobre fixture sprint1-iteracion3 — ~2hs
- Audit Paso 7 (G1-G33 + FG1-FG14 + SOLID + zero-trust)
- Audit Paso 8 (tests adversariales obligatorios — categorías 1-15 sección 9.1 arquitectura)

**Validación L38 N=3**: si commit final sesión 5 pasa GGA en 1 round sin bypass → L38 alcanza N=3 estructural → puede graduar a regla A26 universal en `architecture/PRINCIPIOS-ARQUITECTURA.md`.

**Si M3 ≥90% medido en S-8** → ADR-011 candidato a promover de PROPOSED v0.9 PARTIAL a ACCEPTED v1.0.

---

## ✅ SPRINT 3 SESIÓN 3 CERRADA (2026-05-22)

### BLOQUE 1 — Sincronización post sesiones 1+2

1. **ADR-011 bumped**: PROPOSED v0.7 PARTIAL → **PROPOSED v0.9 PARTIAL**
   - Header actualizado con fecha 2026-05-22 y Sprint 3 sesiones 1+2 cerradas
   - Sección "Phase 2 BUILD ejecutado" anexada con evidencia detallada:
     - 73 tests PASS en 0.32s, MC1=96.2%, 8 stories S-1..S-8 completas
     - Paso 7 audit PASS (0 críticos) + Paso 8 adversariales PASS
     - M2 empírico cumplido (A=57.7/B=26.9/C=15.4 dentro banda AC2 ±15pp)
     - 3 deudas precondición resueltas (R07, R08, R10)
   - Bump rationale table v0.5 → v0.7 → v0.9 anexada
   - Sección "Pendiente para promoción a ACCEPTED" actualizada con marcadores parciales
   - Sigue PARTIAL porque falta Tier A (`auto-fix-mechanic`) operativo

2. **LECCIÓN 38 promovida a formal del Framework** (N=2 confirmada)
   - Enunciado: *"código que sigue PROTOCOLO + audit Paso 5 previa pasa GGA en 1 round (vs 4 rounds + bypass sin auditar)"*
   - Evidencia N=2: commits `06493bc` (Sprint 3 sesión 1) + `2322e4a` (Sprint 3 sesión 2)
   - Contraejemplo baseline: Sprint 1 Iteración 3 (4 rounds + `--no-verify`)
   - Cross-referenced en ADR-011 sección Conexiones y header

3. **`architecture/LECCIONES.md` CREADO** — registry formal de lecciones N=2+
   - Workflow formal: N=1 candidata (sesion-activa) → N=2 formal (LECCIONES.md) → N=3+ estructural (regla A26+ o anti-pattern AP-3.NN+)
   - L38 como primera entry formal
   - Inventario de L1-L37 candidatas N=1 vigentes
   - Resuelve gap arquitectónico: hasta hoy las lecciones promovidas vivían distribuidas en ADRs sin índice canónico

4. **`architecture/README.md` v1.2 → v1.3** — incorpora `LECCIONES.md` en tabla de contenido + sección "Inmutabilidad relativa" actualizada con workflow de promoción

### BLOQUE 2 — sigma:auto-fix-mechanic Tier A (Pasos 1-5 PROTOCOLO) ✅ COMPLETO

Pasos 1-5 ejecutados con plan apto para entrar a build (Sprint 3 sesión 4+). Artefactos producidos:

| Paso | Artefacto | Status |
|------|-----------|--------|
| 1 | `docs/prd/PRD-sigma-auto-fix-mechanic.md` | DRAFT v0.1 — 15 secciones, 9 ACs (AM1-AM9), 10 constraints, M3 + MM1-MM5 metrics |
| 2 | `docs/dominio/auto-fix-mechanic-rules.yaml.draft` | DRAFT v0.1 — 15/15 handlers para rule_ids Tier A v0.1.0 del classifier |
| 2 | `docs/dominio/codemod-toolbox.md` | DRAFT v0.1 — catálogo 4 tools + evidencia ECC vs wrapper (sec 3) |
| 3 | `docs/arquitectura/ARQUITECTURA-sigma-auto-fix-mechanic.md` | DRAFT v0.1 — 15 secciones con decisión clave resuelta + 5 alternativas rechazadas |
| 4 | `docs/stories/STORIES-sigma-auto-fix-mechanic.md` | DRAFT v0.1 — 8 stories (S-1..S-8), 16hs en 2 sesiones, DAG sin ciclos |
| 5 | `auditoria/audit-plan-auto-fix-mechanic-2026-05-22.json` | DONE — 0 críticos, 3 warnings tracked, veredicto `READY_FOR_BUILD_WITH_DEUDAS_TRACKED` |

**Decisión arquitectónica clave RESUELTA (Paso 3)**: **wrapper sigma propio** (NO wholesale ECC).
- Evidencia: ECC `build-fix` + `refactor-clean` tienen 0/15 cobertura directa de los 15 rule_ids Tier A; usan LLM (viola C1 PRD); no determinísticos (viola AM7 idempotencia). Ver `codemod-toolbox.md` sec 3 y `ARQUITECTURA` sec 2.
- Toolbox: 4 tools cubren 15/15 — ESLint (8 rule_ids), Prettier (2-3), ts-morph custom (4), Python custom (2).
- ECC sigue útil como composición lateral (operador puede invocarlo para casos fuera del classifier), no como backend wholesale del mechanic.
- 5 alternativas rechazadas explícitas en ARQUITECTURA sec 2.2.

**3 precondiciones audit Paso 5 a cerrar antes de S-1 build** (Sprint 3 sesión 4):
1. **R04** — `filelock` nueva dep externa: confirmar install vs fallback stdlib (fcntl/msvcrt). Acción en S-3.
2. **R08** — helper `serializeErr()` implícito en codemod `console_to_json_structured.ts`: anotar en S-6 al iniciar build.
3. **R10** — fixture files target (.ts/.sql con patrones): agregar al DoD de S-1 (~15 archivos sintéticos pequeños por rule_id Tier A).

**Métricas estimadas del build próximo**:
- ~600-800 LOC Python prod
- ~250-450 LOC codemods custom (4 ts-morph + 2 Python)
- ~115 tests proyectados (ratio ~2:1 vs prod)
- 2 sesiones de build: sesión 4 (S-1..S-5 core, ~8.5hs) + sesión 5 (S-6..S-8 codemods + integración, ~7.5hs)

**Observación L38 N=3 esperada**: si el build sigue PROTOCOLO + este audit, expectativa GGA passes 1 round = N=3 que graduaría L38 a regla A26 universal en `PRINCIPIOS-ARQUITECTURA.md`.

---

## ✅ SPRINT 3 SESIÓN 2 CERRADA (2026-05-22 — commit `2322e4a`)

**`sigma:finding_classifier` BUILD COMPLETO** — pasos 6-12 PROTOCOLO ejecutados sobre stories S-4..S-8.

Métricas finales:
- **73 tests PASS en 0.32s** (49 al cerrar sesión 1 → 73 al cerrar sesión 2)
- **MC1 = 96.2%** cobertura
- **294 LOC producción + 739 LOC tests** (ratio 2.5:1)
- **Paso 7 audit PASS** — 0 críticos en G1-G33 + FG1-FG14 + SOLID + zero-trust (`auditoria/audit-code-classifier-2026-05-22.json`)
- **Paso 8 adversariales PASS** — 11 tests adversariales + tests remaining
- **M2 empírico medido**: A=57.7% / B=26.9% / C=15.4% sobre fixture R10 (dentro banda AC2 ±15pp) — `auditoria/m2-empirical-distribution-2026-05-22.json`
- **GGA pre-commit hook PASS en 1 round** (sin bypass humano)

Stories completadas sesión 2:
- S-4: CLI `sigma-classify` (stdin/stdout/exit codes)
- S-5: `--audit` flag (tier→count summary)
- S-6: Performance validation sobre fixture R10
- S-7: Extensibility (slots R/G/FG futuros)
- S-8: M2 empirical distribution measurement

---

## ✅ SPRINT 3 SESIÓN 1 CERRADA (2026-05-22 — commit `06493bc`)

**`sigma:finding_classifier` STORIES S-1..S-3 + PRECONDICIONES**

- Precondiciones audit cerradas: R10/R07/R08 (fixture sprint1-iteracion3.json + S-8 + emit_calibration_log())
- S-1: YAML loader + schema validation (PyYAML 6.0.3) — 15 tests
- S-2: `classify()` deterministic algorithm — 11 tests
- S-3: `emit_calibration_log()` con JSON aggregation + deduplicación — 13 tests
- **36 tests PASS en 0.09s**
- Python package infrastructure: `pyproject.toml` + `framework/sigma/finding_classifier/` (15 archivos)
- GGA PASS en 1 round (N=1 de L38 candidata original)

---

## ✅ SPRINT 2 SESIÓN 2 CERRADA (2026-05-21)

**Phase 2 ADR-011 PRD-ready** — Pasos 1-5 PROTOCOLO sobre `sigma:finding_classifier` (artefactos en `docs/prd/`, `docs/dominio/`, `docs/arquitectura/`, `docs/stories/`, `auditoria/audit-plan-classifier-2026-05-21.json`). Veredicto: `READY_FOR_BUILD_WITH_DEUDAS_TRACKED` (3 warnings cerradas en Sprint 3 sesión 1).

ADR-011 bumpeado v0.5 → v0.7 PARTIAL con sección "Phase 2 PRD-ready".

---

## ✅ SPRINT 2 SESIÓN 1 CERRADA (2026-05-21 PM)

**Phase 1 ADR-011 (`sigma:gga-scope-aware`) IMPLEMENTADA** vía Plan B (RULES_FILE swap declarativo en `.gga`).

M1 CUMPLIDO N=1: GGA cerró en 1 round vs 4 baseline.

Commits Sprint 2 sesión 1: `6c0a71c` + `fe3ed57` (pusheados a origin/main).

---

## ESTADO ACTUAL (post Sprint 3 sesión 3 — 2026-05-22)

### Trinidad correctiva (ADR-011 Phase 2)

| Componente | Status | Sprint |
|------------|--------|--------|
| **`sigma:finding_classifier` (front-end)** | ✅ DONE — operativo, 73 tests PASS, audit Paso 7+8 PASS, M2 medido | Sprint 3 sesiones 1+2 |
| **`sigma:auto-fix-mechanic` (Tier A)** | 🟡 PRD-ready o BUILD-ready según cierre BLOQUE 2 de esta sesión | Sprint 3 sesión 3 (planning) → 4-5 (build) |
| **`sigma:correction-agent-bounded` (Tier B)** | ⏳ pendiente | Sprint 4 |
| **`sigma:correction-adr-draft` (Tier C)** | ⏳ pendiente | Sprint 4 |
| **Integración E2E** (GGA → classifier → tier handler → patch/PR) | ⏳ pendiente | Sprint 4-5 |

### Repo

- **Branch**: main
- **HEAD esperado al cierre sesión 3**: nuevo commit con BLOQUE 1 (ADR-011 v0.9 + LECCIONES.md + architecture/README v1.3 + SIGUIENTE-SESION v7.0) + BLOQUE 2 (artefactos planning auto-fix-mechanic)
- **Working tree esperado**: clean post commit

---

## DECISIONES TOMADAS EN SESIÓN 2026-05-22 (Sprint 3 sesión 3)

- **ADR-011 v0.9 PARTIAL** — bump con evidencia BUILD ejecutado + M2 medido + L38 N=2.
- **L38 promovida** — primera lección N=2 formal del Framework.
- **`architecture/LECCIONES.md` creado** — registry canónico de lecciones N=2+ (resuelve gap arquitectónico).
- **Decisión arquitectónica BLOQUE 2 Paso 3**: [PENDIENTE DOCUMENTAR al cerrar sesión] componer wholesale sobre ECC `build-fix` + `refactor-clean` vs construir wrapper sigma propio que invoca codemods directos.

---

## QUÉ HACER EN LA PRÓXIMA SESIÓN (Sprint 3 sesión 4)

### PASO T-1 — Verificación commit del cierre 2026-05-22 pusheado

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git log --oneline -5
# Debería mostrar commit Sprint 3 sesión 3 (BLOQUE 1 sync + BLOQUE 2 planning)
git status
# Esperado: working tree clean
git pull
```

### PASO Sprint 3 sesión 4 — `sigma:auto-fix-mechanic` BUILD pasos 6-12

Aplicar PROTOCOLO-CONSTRUCCION-CODIGO pasos 6-12 al plan auditado en sesión 3:

- **Paso 6**: Construir código (~10-15hs estimado, según decisión Paso 3 wholesale ECC vs wrapper sigma)
- **Paso 7**: Audit código (G1-G33 + FG1-FG14 + SOLID + zero-trust)
- **Paso 8**: Tests adversariales
- **Paso 9**: Validación seguridad y configuración
- **Paso 10**: Deploy seguro (skill registrado en sigma namespace)
- **Paso 11**: Verificación post-deploy
- **Paso 12**: Cierre + polinización

**Validación de L38 N=3 implícita**: si este build pasa GGA en 1 round, L38 alcanza N=3 estructural y puede graduar a regla A26 universal en `PRINCIPIOS-ARQUITECTURA.md`. Si NO pasa, L38 vuelve a observación contextual sin promoción a A*.

### PASO Sprint 3 sesión 5 — M3 validación empírica + ADR-011 v0.9 → v1.0 ACCEPTED candidato

- Aplicar `auto-fix-mechanic` a un commit real con findings GGA reales
- Validar M3 ≥90% Tier A auto-fix
- Si M3 PASS + M1 N≥2 acumulado: ADR-011 promovido a ACCEPTED v1.0 (al menos para el subset classifier + auto-fix-mechanic)

### PASOS PARALELOS DIFERIDOS (no bloqueantes Sprint 3)

- **Sprint 4**: `sigma:correction-agent-bounded` Tier B + `sigma:correction-adr-draft` Tier C + integración E2E
- **Sprint 5+**: aplicar workflow a Stallen para alcanzar M1 N≥3 + M2 N≥3 fixtures distintos
- **Diferidos a Sprint 4+**: las 4 sigma MVP originales (`operationalize-constitution`, `enforce-constitution-check`, `multi-tenant-isolation-checker`, `dependency-cycle-detector`)

---

## CONTEXTO RÁPIDO — leer EN ORDEN al arrancar próxima sesión

1. `CLAUDE.md` (constitución, ~5 min)
2. `auditoria/sesion-activa.md` — addendum Sprint 3 sesión 3 (~10 min)
3. Este archivo — plan Sprint 3 sesión 4 (~5 min)
4. `decisions/ADR-011-capa-correctiva-y-scope-aware.md` **PROPOSED v0.9 PARTIAL** — sección "Phase 2 BUILD ejecutado" + bump rationale (~10 min)
5. `architecture/LECCIONES.md` v1.0 — L38 + workflow promoción (~5 min)
6. `docs/prd/PRD-sigma-auto-fix-mechanic.md` (~5 min)
7. `docs/arquitectura/ARQUITECTURA-sigma-auto-fix-mechanic.md` — decisión Paso 3 resuelta (~10 min)
8. `docs/stories/STORIES-sigma-auto-fix-mechanic.md` (~5 min)
9. `auditoria/audit-plan-auto-fix-mechanic-2026-05-22.json` (~3 min)
10. (Opcional) `framework/sigma/finding_classifier/` — código del classifier como referencia de estilo

---

## DEUDAS TÉCNICAS — estado tras Sprint 3 sesión 3

### Deudas RESUELTAS esta sesión

- **DEUDA-SIGUIENTE-SESION-STALE**: ✅ refresh v6.3 → v7.0 con estado real del disco.
- **DEUDA-REGISTRY-LECCIONES**: ✅ `architecture/LECCIONES.md` creado.

### Deudas precondición Sprint 3 (de audit Paso 5 v0.7) — RESUELTAS en sesión 1+2

- **R07** ✅ S-8 creada con fixture R10 + medición M2 dentro banda AC2 ±15pp.
- **R08** ✅ `emit_calibration_log()` implementada con coverage 100%.
- **R10** ✅ Fixture `sprint1-iteracion3.json` construido y poblado.

### Deudas ABIERTAS sin cambio

- **DEUDA-ADVERSARIAL-TEST-SHAPE-WRONG** (Iteración 3) 🟡
- **DEUDA-NPM-INSTALL-MANUAL** (Iteración 3) 🟢
- **DEUDA-SUPABASE-LOCAL-MANUAL** (Iteración 3) 🟢
- **DEUDA-SIGMA-MVP-NO-CONSTRUIDAS** — diferidas Sprint 4+
- **DEUDA-CONSTITUTION-CHECK-ENFORCEMENT** — diferida
- **DEUDA-TAXONOMIA-CLARIFY-INCOMPLETA** — diferida
- **DEUDA-FACT-FORCING-GATE-EN-SANDBOX** (workaround documentado)
- **DEUDA-CLAUDE-MEM-MANIFEST** (parche local persistente)
- **DEUDA-PLUGIN-INSTALL-DOCS**
- **DEUDA-WINDOWS-SETUP-CHECKLIST**
- **DEUDA-SDD-EXPLORE-NO-WRITE** (menor)
- **DEUDA-SUB-AGENT-OVERRIDE-OPERATOR** (menor)
- **DEUDA-ADR-010-PROMOTE-TO-ACCEPTED**
- **DEUDA-NORTE-FRAMEWORK-PLACEHOLDERS** (Q4-Q7)
- **DEUDA-WORKFLOW-OPERATIVO**
- **DEUDA-VISIÓN-D-NO-FORMALIZADA**
- **DEUDA-REPLANTEAR-ROADMAP-POST-STACK**

---

## PRE-FLIGHT próxima sesión

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git status              # working tree esperado: clean post cierre sesión 3
git pull
git log --oneline -10

# Verificar trinidad correctiva al día
ls framework/sigma/             # deberían aparecer: finding_classifier/ + auto-fix-mechanic/ (si BLOQUE 2 build arrancó) o solo finding_classifier/ (si solo planning)
cat decisions/ADR-011-*.md | head -10  # confirmar v0.9 PARTIAL en header
cat architecture/LECCIONES.md | head -30  # confirmar L38 formal + workflow

# Tests del classifier siguen verdes
cd framework
python -m pytest sigma/finding_classifier/tests/ -q
# Esperado: 73 passed in <1s
```

---

## REGLAS CRÍTICAS A RECORDAR (Sprint 3 sesión 4+)

### 7 Principios rectores (sin cambio)
1. Python traza → IA recorre → Python verifica
2. **3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA** ← L38 confirma empíricamente
3. Dominio-first
4. **Auto-fix > finding cuando inequívoco** ← `auto-fix-mechanic` operacionaliza
5. Polinización cruzada
6. **Descubrir antes de ejecutar** (audit empírico)
7. Meta-producto recursivo

### Lecciones N=2+ formales (architecture/LECCIONES.md)
- **L38**: PROTOCOLO + audit Paso 5 elimina loop GGA asintótico (N=2, primera promoción formal)

### Lecciones N=1 vigentes (sesion-activa.md)
- L35, L36, L37 (capa correctiva + scope-awareness — esperan N=2)
- L29-L34 (Iteración 3 — cost hook, token budget, A-rule coverage, etc.)
- L24-L28 (sdd-* vs speckit-* — T1.9 EMPIRICAL)
- L22-L23 (planning a-priori vs ejecutable)
- L16-L21 (sesiones 2026-05-20/21)

### Insight Decisión A — VALIDADO 2 NIVELES (sin cambio)

### Lecciones técnicas sticky
- LECCIÓN 17: `edit_file` con array no atómico — preferir `write_file` (válido en Sprint 3 también)
- LECCIÓN 18: cross-LLM publishing canónico (`obra/superpowers` modelo)
- LECCIÓN 19: `extraKnownMarketplaces` en `~/.claude/settings.json`

---

## RIESGOS DE LA PRÓXIMA SESIÓN (Sprint 3 sesión 4)

- **Fork ECC wholesale vs wrapper sigma**: si la decisión Paso 3 fue wholesale, validar empíricamente que ECC `build-fix` cubre los rule_ids Tier A del classifier. Si gap >50%, considerar wrapper sigma híbrido.
- **L38 N=3 puede fallar**: si el build de `auto-fix-mechanic` NO pasa GGA en 1 round, L38 NO promueve a A26 — queda en N=2 formal solamente. Acción: investigar causa raíz, NO bypass.
- **M3 puede medirse <90%**: si Tier A auto-fix tiene <90% de éxito, ADR-011 NO sube a v1.0 ACCEPTED. Bajar a REJECTED o iterar con auto-fix-mechanic v0.2.
- **Build estimado 10-15hs**: dividir en sub-sesiones por phase si es necesario (precedente del classifier: S-1..S-3 sesión 1, S-4..S-8 sesión 2).

---

## ARCHIVOS CLAVE A TOCAR EN LA PRÓXIMA SESIÓN

- `framework/sigma/auto-fix-mechanic/` (nuevo package)
- `framework/sigma/auto-fix-mechanic/tests/` (test suite)
- `auditoria/audit-code-auto-fix-mechanic-YYYY-MM-DD.json` (Paso 7)
- `auditoria/m3-empirical-tier-a-success-YYYY-MM-DD.json` (M3 medición)
- `decisions/ADR-011-capa-correctiva-y-scope-aware.md` (eventual v0.9 → v1.0 candidato)
- `architecture/LECCIONES.md` (eventual L38 → A26 graduation o L39+ nueva)
- `auditoria/sesion-activa.md` (cierre próxima sesión)
- `SIGUIENTE-SESION.md` (regenerar al cierre v7.0 → v7.1)

---

## NOTAS PARA CLAUDE

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Cliente recomendado**: Claude Code CLI dentro de `C:\DEPARTAMENTO-SOFTWARE\`
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO (hit rate 20/20)
- **NUNCA proyectar cansancio**
- **PROTOCOLO-INICIO-CHAT v1.0 PASO 1 OBLIGATORIO** para verificar Project es Framework
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy pause)
- **L38 ya es FORMAL** — no usarla como "candidata" en docs nuevos
- **L35-L37 SIGUEN candidatas N=1** — no promoverlas sin segundo evento empírico
- **Trinidad correctiva**: classifier ✅ operativo, auto-fix-mechanic 🟡 en construcción, los otros dos ⏳ Sprint 4
- **claude-mem requiere `autoUpdate: false`** — no romper el parche local

---

## CÓMO USAR ESTE ARCHIVO

Al abrir Claude Code CLI:

> *"Seguimos Framework Departamento. HEAD esperado: [commit Sprint 3 sesión 3]. Aplicá PROTOCOLO-INICIO-CHAT. Estado: Sprint 3 sesión 4. Trinidad correctiva: classifier ✅, auto-fix-mechanic 🟡 (BUILD pasos 6-12 esta sesión). Arrancamos T-1 + Paso 6 build auto-fix-mechanic siguiendo plan auditado en sesión 3."*

---

Creado: 2026-05-15 | Versión: **7.0** (post Sprint 3 sesión 3 — sync ADR-011 v0.9 + L38 formal N=2 + LECCIONES.md nuevo + auto-fix-mechanic planning)
Para: Claude que abra próxima sesión (Sprint 3 sesión 4 — BUILD auto-fix-mechanic)
