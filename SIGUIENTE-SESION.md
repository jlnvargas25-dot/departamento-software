# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico post-Sprint 3 sesión 3 (BLOQUE 1 sync completado + BLOQUE 2 pasos 1-5 de `sigma:auto-fix-mechanic`).
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-22 (Sprint 3 sesión 3 cerrada — ADR-011 v0.9 PARTIAL, L38 formal N=2, auto-fix-mechanic PRD-ready o build-ready según Bloque 2)
**Cliente recomendado próxima sesión**: **Claude Code CLI** dentro de `C:\DEPARTAMENTO-SOFTWARE\` (skills speckit-* + ecc:* + claude-mem:* + sdd-* + superpowers:* todos cargados)
**Versión**: 7.0 (post Sprint 3 sesión 3 — sync + segundo componente trinidad correctiva planeado)

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

### BLOQUE 2 — sigma:auto-fix-mechanic Tier A (Pasos 1-5 PROTOCOLO)

> **Status BLOQUE 2 al cierre**: [completar al finalizar sesión 3 — reflejar pasos efectivamente ejecutados, decisión arquitectónica del fork ECC wholesale vs wrapper sigma, ubicación de artefactos producidos]

Artefactos esperados (pendiente confirmar al cierre real):
- `docs/prd/PRD-sigma-auto-fix-mechanic.md` (Paso 1)
- `docs/dominio/auto-fix-mechanic-rules.yaml.draft` + `docs/dominio/codemod-toolbox.md` (Paso 2)
- `docs/arquitectura/ARQUITECTURA-sigma-auto-fix-mechanic.md` (Paso 3) — con decisión wholesale ECC vs wrapper sigma resuelta
- `docs/stories/STORIES-sigma-auto-fix-mechanic.md` (Paso 4)
- `auditoria/audit-plan-auto-fix-mechanic-2026-05-22.json` (Paso 5)

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
