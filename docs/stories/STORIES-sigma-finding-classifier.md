# Stories — `sigma:finding-classifier`

**Status**: DRAFT v0.1
**Date**: 2026-05-21 (Sprint 2 sesión 2 — Paso 4 del PROTOCOLO-CONSTRUCCION-CODIGO)
**Related**: PRD-sigma-finding-classifier.md, ARQUITECTURA-sigma-finding-classifier.md, findings-taxonomy.md
**Sprint de build estimado**: Sprint 3 (3-5 stories construibles)

---

## Convención

Cada story sigue el formato:

```
S-N — <Título imperativo corto>
- AC vinculado:   <ACs del PRD>
- Estimación:     <hrs>
- Bloquea:        <stories que la requieren>
- Bloqueado por:  <stories prerequisito>

Given <contexto>
When <acción>
Then <resultado verificable>

Adversariales:
- <test edge case 1>
- <test edge case 2>
```

Las stories están ordenadas por dependencia (S-1 primero, S-7 última).

---

## S-1 — Cargar y validar `sigma-classifier-rules.yaml`

- **AC vinculado**: AC5 (extensibilidad), AC6 (output estructurado)
- **Estimación**: 2 hs
- **Bloquea**: S-2, S-3, S-4, S-5, S-6, S-7
- **Bloqueado por**: ninguna

**Given** un archivo YAML con shape `{version, rules, defaults}` (ej. `docs/dominio/sigma-classifier-rules.yaml.draft`)
**When** se invoca `load_rules(path)`
**Then** retorna `ClassifierRules` con `rules: dict[rule_id, RuleConfig]` poblado y `defaults` correctamente parseado.

**Given** un YAML sin la clave `rules` top-level
**When** se invoca `load_rules`
**Then** lanza `SchemaError("YAML missing required top-level keys")` y exit 1 si se llama via CLI.

**Given** un YAML con `rules.SOMETHING.tier = "X"` (tier inválido)
**When** se invoca `load_rules`
**Then** lanza `SchemaError` con mensaje específico apuntando al rule_id ofensor.

**Adversariales**:
- YAML vacío → exit 1, mensaje claro.
- YAML con BOM UTF-8 → debe cargar correctamente (no fallar por encoding).
- YAML con tabs en lugar de spaces → exit 1, mensaje del parser yaml.

---

## S-2 — Clasificar un finding cuyo `rule_id` está en el YAML

- **AC vinculado**: AC1, AC6
- **Estimación**: 2 hs
- **Bloquea**: S-4, S-5, S-7
- **Bloqueado por**: S-1

**Given** un `Finding{rule_id="TS-1", ...}` y `ClassifierRules` con `TS-1 → tier=A, action_hint="eslint-fix"`
**When** se invoca `classify([finding], rules)`
**Then** retorna `[ClassifiedFinding(finding, tier="A", action_hint="eslint-fix", matched_rule=True)]`.

**Given** un batch de 5 findings con rule_ids todos presentes en el YAML
**When** se clasifica
**Then** retorna 5 `ClassifiedFinding` con `matched_rule=True` cada uno, y los tiers coinciden con el YAML.

**Adversariales**:
- `rule_id` con whitespace al final → NO matchea (strict equality, no trimming silencioso). Documentado en S-1 como invariante.
- `rule_id` case-sensitive (TS-1 ≠ ts-1) — verificado por test explícito.
- Finding con campos faltantes (sin `severity`) → S-1 schema validation lo rechaza antes de classify.

---

## S-3 — Default conservador ante `rule_id` desconocido

- **AC vinculado**: AC3 (default Tier C + log)
- **Estimación**: 1.5 hs
- **Bloquea**: S-4, S-7
- **Bloqueado por**: S-1
- **Componentes construidos**: `classify()` extendido con default branch + `emit_calibration_log()` (declarado en ARQUITECTURA sección 5; anotado explícitamente acá tras audit R08 del Paso 5).

**Given** un `Finding{rule_id="UNKNOWN-RULE-XYZ", ...}` y `ClassifierRules` sin esa entrada
**When** se invoca `classify`
**Then** retorna `ClassifiedFinding(finding, tier="C", action_hint="unknown-rule-log-for-calibration", matched_rule=False)`.

**Given** el mismo finding y un classifier invocado vía CLI
**When** se invoca con stdin/stdout
**Then** stderr contiene línea JSON: `{"event":"unknown_rule","rule_id":"UNKNOWN-RULE-XYZ","file":"<path>","line":<n>}` y exit code es 0 (no es error fatal).

**Given** un batch con `N` findings cuyo `rule_id` repite (mismo unknown N veces) y otros con unknown distintos
**When** se invoca `classify` (que delega a `emit_calibration_log(unknown_rule_ids: set[str])`)
**Then** `emit_calibration_log` emite a stderr **una línea JSON por rule_id único** (dedup vía set), con el conteo agregado por rule_id si se invoca con `--audit`.

**Adversariales**:
- Múltiples findings con el mismo unknown rule_id → log se emite UNA sola vez (deduplicado) con el conteo agregado.
- 100 findings unknown distintos → exit 0, 100 líneas de log a stderr (cap razonable, sin truncar).
- `emit_calibration_log` invocada con `set()` vacío → no emite nada (no-op silencioso).

---

## S-4 — CLI: stdin/stdout/exit codes

- **AC vinculado**: AC6 (output estructurado parseable)
- **Estimación**: 2 hs
- **Bloquea**: S-6, S-7
- **Bloqueado por**: S-1, S-2, S-3

**Given** un JSON array válido de findings vía stdin
**When** se invoca `python -m sigma.finding-classifier < findings.json`
**Then** stdout contiene JSON válido (`ClassifiedFinding[]`) parseable con `json.loads`, exit code 0.

**Given** stdin con JSON inválido (texto plano, no JSON)
**When** se invoca el CLI
**Then** exit code 1, stderr contiene mensaje claro indicando posición del error de parsing.

**Given** flag `--input findings.json`
**When** se invoca sin stdin
**Then** lee del archivo en lugar de stdin, mismo output a stdout.

**Adversariales**:
- stdin vacío → exit 1 con mensaje "no findings provided".
- Array JSON vacío `[]` → exit 0, stdout `[]` (válido).
- `--input` apuntando a archivo inexistente → exit 1.

---

## S-5 — Flag `--audit`: resumen tier→count a stderr

- **AC vinculado**: AC7
- **Estimación**: 1 h
- **Bloquea**: S-7
- **Bloqueado por**: S-2, S-3

**Given** un batch de 27 findings (15 A, 7 B, 5 C, esperado catálogo Sprint 1)
**When** se invoca con flag `--audit`
**Then** stdout sigue conteniendo JSON normal; stderr adicionalmente contiene tabla resumen:
```
tier_A: 15
tier_B: 7
tier_C: 5
unknown_rules: 0
```

**Given** el mismo batch sin flag `--audit`
**When** se invoca
**Then** stderr no contiene la tabla (silenciosa por defecto, solo unknown_rules log si aplica).

**Adversariales**:
- `--audit` con stdin vacío → exit 1 (heredado de S-4), no se emite tabla.
- `--audit` con todos unknown → tabla muestra `tier_C: <N>` y `unknown_rules: <N>`.

---

## S-6 — Performance: 50 findings en <100ms

- **AC vinculado**: AC4
- **Estimación**: 0.5 h (es benchmark, no implementación nueva)
- **Bloquea**: S-7
- **Bloqueado por**: S-4

**Given** un fixture de 50 findings sintéticos cargado de archivo
**When** se mide wall-clock de `time python -m sigma.finding-classifier --input fixture.json > /dev/null`
**Then** total <100ms en máquina de desarrollo estándar (CPU x86_64, Python 3.10+, sin cold start de Python).

**Adversariales**:
- Fixture de 1000 findings → <2s (linear scaling, no degradación cuadrática).
- Fixture de 50 findings con 50 rule_ids únicos → <100ms (no hay caching que esconda problemas).
- Comparar warm vs cold start de Python (warm es el target real, cold solo informacional).

---

## S-7 — Extensibilidad: agregar regla sin tocar Python

- **AC vinculado**: AC5
- **Estimación**: 1 h
- **Bloquea**: ninguna (último)
- **Bloqueado por**: S-1, S-2, S-3, S-4, S-5

**Given** YAML inicial con N reglas y un finding cuyo `rule_id="R-NEW-RULE-001"` está unknown
**When** se agrega al YAML la entrada `R-NEW-RULE-001: {tier: A, source: "sigma:plan-auditor", action_hint: "eslint-fix"}` y se re-invoca el CLI sobre el mismo input
**Then** el finding se clasifica como tier A con `matched_rule=True`, sin cambios al código Python.

**Adversariales**:
- Re-correr el CLI sin reiniciar proceso (CLI invocaciones son procesos nuevos, no daemon) → consistencia respetada.
- Agregar regla con tier inválido y re-correr → exit 1 inmediato (S-1 schema validation).
- Quitar una regla del YAML que estaba siendo usada → ese rule_id pasa a unknown → tier C default (S-3 cubierto).

---

## S-8 — Medir distribución empírica del clasificador sobre fixture Sprint 1

- **AC vinculado**: AC2 (distribución 60/30/10 ±15%) + métrica M2 del ADR-011
- **Estimación**: 1 h
- **Bloquea**: promoción ADR-011 v0.7 PARTIAL → v1.0 ACCEPTED
- **Bloqueado por**: S-2, S-3, S-4 (necesita el classifier funcional + CLI)
- **Origen**: cerrar warning R07 del audit Paso 5 (`auditoria/audit-plan-classifier-2026-05-21.json`).

**Given** el fixture `framework/sigma/finding-classifier/tests/fixtures/sprint1-iteracion3.json` (poblado con findings reales del transcript Sprint 1 Iteración 3, ver DEUDA-FIXTURE-SPRINT1 cerrada en precondición R10 del Sprint 3)
**When** se invoca el classifier sobre el fixture con `--audit` y se calcula la distribución `tier → count / total`
**Then** se obtienen tres porcentajes (Tier A %, Tier B %, Tier C %) y se verifica que cada uno cae dentro de `[hipótesis ADR-011 ± 15 pp]` — i.e. A ∈ [45-75]%, B ∈ [15-45]%, C ∈ [0-25]%.

**Given** la distribución medida
**When** se compara contra la hipótesis ADR-011 original (60/30/10)
**Then** se documenta el delta empírico vs hipótesis en `auditoria/m2-empirical-distribution-{date}.json` con campos `{tier, observed_pct, hypothesis_pct, delta_pp, within_band: bool}`.

**Given** distribución medida que cae fuera del rango AC2 (±15pp)
**When** se evalúa la promoción del ADR-011 a v1.0
**Then** el ADR-011 NO se promueve a ACCEPTED; se redacta sub-decisión en `decisions/` documentando la divergencia y recalibrando la hipótesis o el clasificador.

**Adversariales**:
- Fixture con <10 findings totales → exit 0 pero el reporte M2 marca `low_sample_warning: true` (no se puede inferir distribución con N pequeño).
- Todos los findings caen a Tier C (unknown rule overflow) → la distribución refleja problema del fixture, no del clasificador; reporte M2 marca `coverage_warning: true` con cobertura MC1 < 95%.
- Re-correr el classifier sobre el mismo fixture en 10 corridas seguidas → distribución idéntica las 10 veces (MC2 estabilidad inter-corrida).

**Notas**:
- Esta story NO bloquea el build de S-1..S-7. Se ejecuta una vez S-4 (CLI) esté operativo.
- El reporte M2 alimenta la promoción del ADR-011 — sin este reporte la promoción queda bloqueada por el propio criterio de aceptación del ADR.

---

## Resumen del backlog

| Story | AC | Estimación | Dep. |
|-------|----|------------|------|
| S-1 Cargar YAML | AC5, AC6 | 2 h | — |
| S-2 Clasificar known | AC1, AC6 | 2 h | S-1 |
| S-3 Default unknown + emit_calibration_log | AC3 | 1.5 h | S-1 |
| S-4 CLI stdin/stdout | AC6 | 2 h | S-1, S-2, S-3 |
| S-5 Flag --audit | AC7 | 1 h | S-2, S-3 |
| S-6 Performance | AC4 | 0.5 h | S-4 |
| S-7 Extensibilidad | AC5 | 1 h | S-1..S-5 |
| S-8 Distribución empírica (M2) | AC2 | 1 h | S-2, S-3, S-4 |
| **Total estimado** | — | **11 h** | — |

**Capacidad de sesión**: 11 hs de build cabe en 2 sesiones de Sprint 3 (~5-6 hs cada una). MC2 (idempotencia) cubierta transversalmente por todas las stories. S-8 cierra el warning R07 del audit Paso 5 y desbloquea la promoción del ADR-011 a v1.0 ACCEPTED.

---

## ACs del PRD vs cobertura por stories

| AC PRD | Stories que lo cubren |
|--------|----------------------|
| AC1 — Clasificación determinística | S-2 |
| AC2 — Distribución 60/30/10 | S-8 (medición empírica post-build sobre fixture real) |
| AC3 — Default conservador | S-3 |
| AC4 — Performance <100ms | S-6 |
| AC5 — Extensibilidad sin reescritura | S-1, S-7 |
| AC6 — Output estructurado | S-2, S-4 |
| AC7 — Audit | S-5 |

**DEUDA-FIXTURE-SPRINT1 cerrada**: fixture `framework/sigma/finding-classifier/tests/fixtures/sprint1-iteracion3.json` poblado como **precondición R10** al iniciar Sprint 3 (con 26 findings reales del transcript Iteración 3 + 1 unknown para AC3). Habilita S-6 (performance), S-7 (extensibilidad) y S-8 (distribución).

---

## Definición de "Done" por story

- ✅ Código mergeado en `framework/sigma/finding-classifier/`
- ✅ Tests pasando (unit + integration relevantes a la story)
- ✅ Tests adversariales pasando
- ✅ Coverage local ≥80% sobre el código nuevo
- ✅ Documentación inline mínima (docstrings tipo función, no narrativa)
- ✅ Sin invocación de LLM ni network ni filesystem mutaciones (verificado por test C1, C4)

## Definición de "Done" del componente completo

- ✅ Las 7 stories en estado Done
- ✅ Fixture `sprint1-iteracion3.json` poblado (DEUDA-FIXTURE-SPRINT1 cerrada)
- ✅ AC2 medido sobre fixture real: distribución dentro de 60/30/10 (±15%)
- ✅ MC1 ≥95% cobertura del YAML sobre fixture
- ✅ MC2 100% estabilidad inter-corrida (10 corridas seguidas, output idéntico)
- ✅ Integración CLI con `gga run --json | ...` validada manualmente al menos 1 vez
- ✅ ADR-011 bumpeado a v0.9 PARTIAL con evidencia M3 medida (cuando exista mechanic)
