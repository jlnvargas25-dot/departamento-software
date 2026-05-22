# PRD — `sigma:finding-classifier`

**Status**: DRAFT v0.1
**Date**: 2026-05-21 (Sprint 2 sesión 2)
**Owner**: Departamento de Software
**Related**: ADR-011 PROPOSED v0.5 PARTIAL (Phase 2 — Trinidad Correctiva)
**Protocolo**: Paso 1 (Capturar intención) del PROTOCOLO-CONSTRUCCION-CODIGO

---

## 1. Contexto

ADR-011 declaró la **trinidad correctiva** (Tier A mecánico / Tier B sub-agente acotado / Tier C decisión humana) como cura estructural del 4° principio rector ("auto-fix > finding cuando inequívoco"). La trinidad necesita un **front-end determinístico** que decida a qué tier va cada finding antes de aplicar la corrección.

Sin clasificador, los handlers (mechanic, agent, adr-draft) no tienen criterio operativo: cada uno se vería forzado a inspeccionar todos los findings para decidir si le corresponden. El classifier es **el primer componente** de Phase 2 — sin él, el resto no compone.

Sprint 1 produjo evidencia empírica del universo de findings: ~25 issues en 4 rounds de GGA sobre sandbox-stack. El ADR-011 ya hizo un cálculo grueso: ~60% Tier A, ~30% Tier B, ~10% Tier C. Este PRD operacionaliza esa hipótesis con criterios verificables.

---

## 2. Problema que resuelve

**Hoy**: cuando un reviewer (GGA) emite findings, el operador humano decide manualmente cómo abordar cada uno: ¿lo arreglo a mano? ¿le pido al LLM que lo arregle? ¿abro ADR? Esta decisión consume tiempo y es no-determinística entre sesiones (el mismo finding puede ir a flows distintos según humor del operador).

**Tras este PRD**: el classifier mapea cada finding a un tier de forma declarativa, versionada y determinística. El operador (y el resto de la trinidad correctiva) reciben un input estructurado en lugar de un dump de texto.

**Beneficio cuantificable**: M3 del ADR-011 exige Tier A auto-fix ≥90% de findings clasificados como A. Sin classifier, M3 no es medible — no hay forma de saber qué findings "eran" Tier A.

---

## 3. Intención (one-liner)

> "Convertir un dump de findings de cualquier reviewer en una lista estructurada de `(finding, tier)` mediante reglas declarativas, sin LLM, en <100ms."

---

## 4. Scope

### In scope (este PRD)

- **Universo de findings clasificables**: extensible. Sprint inicial cubre GGA v2.8.1 (los ~25 patterns observados en Sprint 1). El diseño deja **slots vacíos** para validadores R01-R15, G1-G33, FG1-FG14 cuando se construyan (Sprint 4+).
- **Output**: cada finding etiquetado con `{tier: A|B|C, rule_id, action_hint}`. `action_hint` es opcional: indica al handler qué herramienta usar (ej. `eslint-fix`, `ts-morph:console-to-logger`, `adr-draft`).
- **Reglas declarativas** en YAML versionable (`sigma-classifier-rules.yaml`).
- **Comportamiento ante regla desconocida**: default conservador → **Tier C** + log estructurado para calibración posterior.
- **Performance target**: clasificación de batch de 50 findings en <100ms (sin LLM, debe ser efectivamente instantáneo).
- **CLI invocable** desde el hook scope-aware actual (composición sobre Phase 1).
- **Implementación**: Python ≥3.10, sin dependencias pesadas (stdlib + `pyyaml`).

### Out of scope (este PRD)

- **Aplicación del fix**: el classifier solo *etiqueta*. Los handlers (Tier A `auto-fix-mechanic`, Tier B `correction-agent-bounded`, Tier C `correction-adr-draft`) son PRDs separados.
- **Parser del output GGA**: el classifier consume un formato intermedio normalizado (`Finding[]`). El adapter GGA-output → `Finding[]` es responsabilidad del integrador (hook o pipeline). Esto deja al classifier desacoplado del provider del reviewer.
- **UI / dashboard**: clasificación se reporta vía stdout JSON. Dashboards son Sprint 5+.
- **Aprendizaje automático**: las reglas son curadas humanamente. NO hay ML aquí (1° principio rector).
- **Inferencia de reglas nuevas**: si un finding no matchea, va a Tier C y se loguea. La curación de la regla nueva es responsabilidad humana (revisión periódica de logs).

---

## 5. Usuarios y stakeholders

| Stakeholder | Rol respecto al classifier |
|-------------|----------------------------|
| **Operador (Julián)** | Invoca el classifier indirectamente vía pre-commit hook. Cura `sigma-classifier-rules.yaml` periódicamente. |
| **Tier A `auto-fix-mechanic`** | Consume findings clasificados como `tier: A`. Aplica codemod según `action_hint`. |
| **Tier B `correction-agent-bounded`** | Consume `tier: B`. Recibe template + contexto del proyecto. |
| **Tier C `correction-adr-draft`** | Consume `tier: C`. Bloquea commit, abre PR comment o ADR stub. |
| **Reviewers (GGA, futuros R/G/FG)** | Producen findings; el classifier los normaliza. |
| **Auditor del Framework** | Revisa periódicamente la distribución empírica de tiers contra hipótesis del ADR-011 (60/30/10). |

---

## 6. Acceptance criteria (formales — verificables empíricamente)

### AC1 — Clasificación determinística sobre catálogo GGA conocido

**Given** los ~25 patterns de findings GGA observados en Sprint 1 (transcript Iteración 3)
**When** el classifier procesa un batch que los contenga
**Then** todos los findings reciben tier sin ambigüedad: ≥95% matchean una regla del YAML (≤5% caen a default Tier C por desconocimiento).

### AC2 — Distribución alineada con hipótesis ADR-011 (M2)

**Given** el catálogo GGA Sprint 1 + ≥1 corrida real adicional
**When** se mide la distribución de tiers
**Then** se observa aproximadamente 60% A / 30% B / 10% C (±15% por tier — la hipótesis se valida si está en el rango).

### AC3 — Comportamiento conservador ante regla desconocida

**Given** un finding con `rule_id` no presente en `sigma-classifier-rules.yaml`
**When** el classifier lo procesa
**Then** retorna `{tier: C, rule_id: <id>, action_hint: "unknown-rule-log-for-calibration"}` y emite log estructurado a stderr con el `rule_id` y el `file:line` para curación posterior.

### AC4 — Performance

**Given** un batch de 50 findings
**When** se invoca el classifier
**Then** el wall-clock total es <100ms en máquina de desarrollo estándar (excluyendo I/O del provider GGA).

### AC5 — Extensibilidad sin reescritura

**Given** una regla nueva (ej. `R-NEW-RULE-001` de validador R01-R15 futuro)
**When** se agrega al YAML con `{tier: A|B|C, action_hint: <opcional>}`
**Then** el classifier la respeta en la próxima invocación sin cambios al código Python (solo cambio en YAML).

### AC6 — Output estructurado y parseable

**Given** un batch de findings
**When** el classifier termina
**Then** stdout contiene JSON válido con esquema `Finding[]` extendido con `{tier, action_hint}`. Exit code 0 si todo se clasificó (incluyendo defaults a Tier C); exit code 1 solo en error fatal (YAML inválido, input no parseable).

### AC7 — Trazabilidad / auditoría

**Given** cualquier clasificación
**When** se invoca con `--audit` flag
**Then** además del output JSON normal, emite a stderr una tabla resumen `tier → count` y la lista de rules desconocidas (insumo para curación del YAML).

---

## 7. Constraints (no negociables)

| ID | Constraint | Origen |
|----|-----------|--------|
| C1 | **Sin LLM en el path de clasificación**. Determinístico puro. | 1° principio rector (Python verifica) |
| C2 | **Reglas declarativas** (YAML). No hardcoded en Python. | Visión C (curator > constructor) |
| C3 | **Default conservador** ante desconocimiento: Tier C, nunca Tier A. | R1 del ADR-011 (clasificador mal calibrado ≠ catástrofe) |
| C4 | **Sin side effects**: el classifier no muta archivos. Solo lee + emite output. | Separación de responsabilidades (mechanic muta, classifier etiqueta) |
| C5 | **Stack: Python ≥3.10, stdlib + pyyaml**. Sin dependencias pesadas. | A20 hexagonal (mantener boundary chico) |
| C6 | **Idempotente**: mismo input → mismo output, sin estado entre corridas. | A12 zero trust testabilidad |
| C7 | **Versionable**: `sigma-classifier-rules.yaml` es código, va a git, tiene historial. | A21 observability + auditoría |

---

## 8. Métricas de éxito (cómo sabemos si funciona)

### Métricas heredadas de ADR-011

- **M2** (cobertura distribución): ~50 findings reales clasificados con distribución 60/30/10 (±15%).
- **M3** (efectividad Tier A): de los findings que el classifier mandó a Tier A, ≥90% son efectivamente auto-fixables por `auto-fix-mechanic` sin intervención humana. (M3 se mide cuando el mechanic exista — este PRD habilita la medición.)

### Métricas propias del classifier

- **MC1** — **Cobertura del YAML**: ≥95% de findings reales matchean una regla curada. Tasa de "unknown → default Tier C" debe ser <5% post-calibración (≤2 ciclos de curación humana).
- **MC2** — **Estabilidad inter-corrida**: dado el mismo batch de findings, el classifier produce el mismo output en 100% de corridas (test de regresión obligatorio).
- **MC3** — **Tiempo de curación**: cuando aparece un finding desconocido, agregar la regla al YAML toma <5 minutos (insumo: log estructurado de AC3).

---

## 9. Dependencias

- **Upstream**: Phase 1 (`sigma:gga-scope-aware`) ya implementada — el classifier compone sobre el hook scope-aware existente.
- **Downstream (consumers, no construidos aún)**:
  - `sigma:auto-fix-mechanic` (Tier A handler) — Sprint 3
  - `sigma:correction-agent-bounded` (Tier B handler) — Sprint 3
  - `sigma:correction-adr-draft` (Tier C handler) — Sprint 3
- **Externa**: ninguna runtime; calibración manual del YAML requiere acceso al transcript de Iteración 3 (ya capturado en ADR-011 líneas 14-21).

---

## 10. Riesgos y mitigaciones

| ID | Riesgo | Probabilidad | Impacto | Mitigación |
|----|--------|-------------|---------|------------|
| RC1 | YAML mal calibrado clasifica findings A como C (over-conservador). Pérdida de auto-fix automático. | Media | Bajo | Default Tier C es **seguro** (regresa al humano). MC1 bajo se detecta empíricamente y se cura. |
| RC2 | YAML mal calibrado clasifica findings C como A (under-conservador). Auto-fix rompe semántica. | Baja | Alto | C3 hardcoded: la **regla por defecto es C**. Para clasificar como A se requiere entrada explícita curada en YAML. RC2 solo aparece si humano marca mal una regla. |
| RC3 | Output GGA cambia formato entre versiones (rompe parser). | Media | Medio | Out of scope (parser es responsabilidad del integrador). PRD del integrador debe absorber esto. |
| RC4 | Performance degrada con catálogos grandes (>1000 reglas). | Baja | Bajo | Diseño con `dict[rule_id, RuleConfig]` O(1) lookup. Benchmark obligatorio en AC4. |
| RC5 | Reglas ambiguas (un finding podría ser A o B según contexto). | Media | Medio | Phase 1: defaults conservadores (A→B→C). Phase 2 del classifier puede introducir condicionales `if file_path matches X then tier B`. NO en este PRD. |

---

## 11. Non-goals explícitos

- ❌ NO clasifica severidad (CRÍTICA/ALTA/MEDIA). El reviewer ya lo hace; el classifier solo decide **tier de tratamiento**.
- ❌ NO aplica fixes. Solo etiqueta.
- ❌ NO usa LLM ni heurísticas estadísticas. Reglas curadas humanamente.
- ❌ NO genera reglas nuevas automáticamente. Si una regla falta, va a Tier C y se loguea — humano cura.
- ❌ NO integra con CI/CD en este PRD. Solo CLI local. CI integration es Sprint 3.

---

## 12. Conexión con principios rectores

| Principio | Cómo el classifier lo encarna |
|-----------|------------------------------|
| **1° (Python traza → IA recorre → Python verifica)** | Classifier es Python puro determinístico. Cero IA en el path. |
| **2° (3 capas)** | Classifier es el **front-end de la capa correctiva**. Sin él, capa correctiva no se materializa. |
| **3° (Dominio-first)** | Paso 2 de este protocolo captura activamente el dominio de findings antes del diseño técnico. |
| **4° (Auto-fix > finding cuando inequívoco)** | Operacionaliza el "cuando inequívoco" — el classifier es quien decide qué es inequívoco (Tier A). |
| **5° (Polinización cruzada)** | Diseño extensible: GGA hoy, R/G/FG mañana, cualquier reviewer futuro. |
| **6° (Descubrir antes de ejecutar)** | El YAML se cura por **observación empírica** del transcript de Iteración 3, no por especulación. |
| **7° (Meta-producto recursivo)** | El classifier es Framework, pero su YAML es el mismo mecanismo que se aplicaría a clasificar findings del propio Framework. |

---

## 13. Plan de validación (cómo verificaremos cada AC en Sprint 3)

| AC | Validación |
|----|------------|
| AC1 | Corrida sobre transcript de Iteración 3 (input fixture). Esperado: ≥24/25 patterns matcheados. |
| AC2 | Corrida sobre catálogo Sprint 1 + N=2 corrida adicional sobre commit nuevo de sandbox-stack o Stallen. |
| AC3 | Test unitario: input con `rule_id: UNKNOWN-RULE-XYZ` → output `tier: C` + log a stderr. |
| AC4 | Benchmark con `time` sobre fixture de 50 findings. |
| AC5 | Test integración: agregar regla nueva al YAML, re-correr sin modificar Python, verificar nuevo output. |
| AC6 | Validación de schema con `jsonschema` sobre output. |
| AC7 | Test funcional: invocar con `--audit`, verificar stderr contiene tabla `tier → count`. |

---

## 14. Resoluciones de scope tomadas en este PRD

| Pregunta | Resolución | Justificación |
|----------|------------|---------------|
| ¿Solo GGA o universo extensible? | **Extensible (GGA + slots futuros R/G/FG)** | Decisión del operador 2026-05-21 (Sprint 2 sesión 2). Evita retrabajo cuando Sprint 4+ construya validadores propios. |
| ¿LLM en clasificación? | **NO** | 1° principio rector + C1. |
| ¿Default ante desconocido? | **Tier C** | R1 ADR-011 + RC2 mitigation. Conservador = seguro. |
| ¿Input format? | **`Finding[]` normalizado** | Desacopla classifier del provider del reviewer. |
| ¿Output format? | **JSON estructurado a stdout** | Composabilidad con cualquier handler downstream. |
| ¿Stack? | **Python ≥3.10 + pyyaml** | Mínima superficie de dependencias. C5. |

---

## 15. Siguiente paso (Paso 2 del protocolo)

Capturar **activamente el dominio**: el universo de findings reales observados en Sprint 1, taxonomizado, con slots vacíos para R/G/FG futuros. Output: `sigma-classifier-rules.yaml` (esqueleto) + tabla de mapeos.

---

**Este PRD es prerrequisito de**: `sigma:finding-classifier` build (Sprint 3).
**Este PRD bloquea**: Paso 2 (dominio), Paso 3 (arquitectura), Paso 4 (stories), Paso 5 (audit + bump ADR-011).
