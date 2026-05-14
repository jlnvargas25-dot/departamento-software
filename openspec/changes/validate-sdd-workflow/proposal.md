# Proposal — validate-sdd-workflow

**Change**: `validate-sdd-workflow`
**Domain**: `departamento-core`
**Author**: Departamento de Software (meta-validación)
**Date**: 2026-05-14
**Artifact store**: hybrid (engram + filesystem)

---

## 1. Intent

Validar empíricamente, sobre este repo, que el workflow SDD de Gentle AI (skills `sdd-propose`, `sdd-spec`, `sdd-design`, `sdd-tasks`, `sdd-verify`) **se ejecuta de punta a punta sin fricciones estructurales** antes de adoptarlo como pilar operativo del Departamento.

El "feature" no es código de producción: es la **confianza** de que el propio andamiaje SDD respeta:
- los paths convencionales (`openspec/changes/{change-name}/...`),
- las `rules` por phase de `openspec/config.yaml`,
- la persistencia dual (`state.yaml` + Engram con topic keys estables),
- y los 7 principios rectores de la constitución.

## 2. Por qué ahora

El Sprint 1 dejó OpenSpec inicializado con `config.yaml` poblado, pero **ninguna change real ha atravesado el DAG completo todavía**. Si el workflow tiene un defecto estructural (path equivocado, rule mal redactada, state.yaml inconsistente), descubrirlo sobre una feature productiva de Stallen sería caro. Mejor descubrirlo acá, donde el costo de rollback es trivial.

Esto es aplicación directa del **7° principio (meta-producto recursivo)**: el Departamento se somete a su propio protocolo antes de exigírselo a sus consumidores.

## 3. Meta-patrón de origen

**5° principio (polinización cruzada)** + **7° principio (meta-producto recursivo)**.

El meta-patrón es: *"Todo subsistema productivo debe pasar por su propia capa de validación antes de declararse operativo."* Lo aplicamos primero al andamiaje SDD; el resultado de esta change polinizará a las skills propias del Departamento (Sprint 2+) y al onboarding de Stallen como cliente del workflow.

## 4. Scope

### In-scope

- Ejecutar **5 fases** secuencialmente: `propose → spec → design → tasks → verify`.
- Cada fase debe escribir su artifact en el path convencional bajo `openspec/changes/validate-sdd-workflow/`.
- Cada artifact debe respetar las reglas correspondientes de `openspec/config.yaml > rules`.
- Persistir en Engram con topic keys `sdd/validate-sdd-workflow/{phase}` (`capture_prompt: false`).
- Actualizar `state.yaml` después de cada fase: `phases.{phase} = done` + append a `artifacts`.
- `sdd-verify` documenta el **estado del workflow** (qué corrió, qué quedó pendiente), no output de tests de código.

### Out-of-scope

- `sdd-apply`: no se ejecuta. No hay código a implementar.
- `sdd-archive`: no se ejecuta. Esta change NO mergea nada a `openspec/specs/{domain}/spec.md`.
- Modificar archivos fuera de `openspec/changes/validate-sdd-workflow/`.
- Crear ADRs, modificar `config.yaml`, tocar la constitución.
- Validar performance, costo de tokens, o calidad semántica del contenido producido — solo se valida que la **mecánica estructural** del workflow funciona.

## 5. Approach

Ejecución lineal, una skill por fase, en modo `auto`:

1. **propose** (esta fase) — captura intent, scope, approach, criterios de éxito.
2. **spec** — escribe `specs/departamento-core/spec.md` con scenarios Given/When/Then sobre el contrato del propio workflow.
3. **design** — documenta cómo el DAG `propose → spec → design → tasks → verify` se materializa en filesystem + Engram, qué garantías ofrece, y dónde están los puntos de falla.
4. **tasks** — checklist verificable de qué artifacts deben existir, en qué paths, con qué claves Engram, y qué rule de `config.yaml` cubren.
5. **verify** — informe empírico: por cada fase, ¿existe el archivo? ¿existe en Engram? ¿`state.yaml` lo refleja? Reporta CRITICAL / WARNING / SUGGESTION.

### Qué genera Python vs qué ejecuta el LLM (1° principio)

| Capa | Quién | Qué |
|---|---|---|
| Orquestación | Python (Claude Code dispatcher + Engram MCP) | Invoca skills en orden, persiste `state.yaml`, escribe a Engram con topic keys estables |
| Producción de contenido | LLM (skills SDD) | Redacta proposal, spec, design, tasks, verify-report |
| Verificación | Python (sdd-verify lee filesystem + Engram) | Comprueba existencia de artifacts y consistencia de `state.yaml` |

El LLM nunca decide *si* una fase está done — eso lo dictamina `state.yaml` + verificación de path. El LLM solo produce el contenido cuando se le pide.

## 6. 3 capas afectadas (2° principio)

- **Preventiva**: `openspec/config.yaml > rules.proposal` (y rules.{spec,design,tasks,verify}) impone qué debe contener cada artifact antes de declararlo válido. Esta proposal ya cumple las 5 rules de `rules.proposal`.
- **Verificable**: `state.yaml` + presencia de archivos en paths convencionales + topic keys en Engram. `sdd-verify` chequea esto empíricamente.
- **Correctiva**: Si una fase falla, la skill correspondiente puede re-ejecutarse contra el mismo `change-name` (idempotente sobre filesystem, upsert sobre Engram vía `topic_key`). No hay auto-fix más allá de re-correr — y eso está bien para una meta-validación.

## 7. Success criterion (empírico, no aspiracional)

La change se considera exitosa si y solo si, al terminar `sdd-verify`:

1. Existen exactamente estos archivos:
   - `openspec/changes/validate-sdd-workflow/proposal.md`
   - `openspec/changes/validate-sdd-workflow/specs/departamento-core/spec.md`
   - `openspec/changes/validate-sdd-workflow/design.md`
   - `openspec/changes/validate-sdd-workflow/tasks.md`
   - `openspec/changes/validate-sdd-workflow/verify-report.md`
2. Existen 5 observations en Engram con topic keys `sdd/validate-sdd-workflow/{proposal,spec,design,tasks,verify-report}`, todas con `project: departamento-software`.
3. `state.yaml` tiene `phases.{proposal,spec,design,tasks,verify} = done` y `artifacts` lista los 5 paths.
4. `verify-report.md` reporta **0 findings CRITICAL** sobre el contrato estructural del workflow.

Cualquier desviación (path equivocado, rule no cumplida, topic key inconsistente, `state.yaml` desincronizado) se documenta en `verify-report.md` como CRITICAL y dispara una entrada en el radar de polinización para Sprint 2.

## 8. Rollback plan

Trivial. Esta change **no escribe nada fuera de `openspec/changes/validate-sdd-workflow/`** y **no se archiva** (no merge a `openspec/specs/`).

Pasos de rollback:

1. `rm -rf openspec/changes/validate-sdd-workflow/` (o equivalente PowerShell: `Remove-Item -Recurse -Force`).
2. Opcional: borrar las 5 observations de Engram con `mem_delete` filtrando por `topic_key` prefix `sdd/validate-sdd-workflow/`. No es estrictamente necesario — quedan como traza histórica del experimento.
3. No hay branches a revertir, ni migrations, ni deploys. El working tree vuelve al estado previo al inicio de la change con un único comando.

No hay impacto sobre `openspec/specs/`, `openspec/config.yaml`, la constitución, ni ningún otro consumidor.

## 9. Risks y open questions

- **Riesgo bajo**: si una skill SDD escribe en un path que no coincide con `~/.claude/skills/_shared/openspec-convention.md`, lo detectamos acá sin daño.
- **Open question**: ¿`sdd-verify` sobre un workflow meta (sin código) produce un informe semánticamente útil, o degrada a checklist mecánico? Lo evaluamos al leer el verify-report.
- **Asunción**: Engram MCP está disponible y el `topic_key` upsert funciona. Si Engram falla, la mitad "hybrid" del artifact store degrada a "openspec puro" — la change sigue siendo válida, pero pierde la prueba de persistencia cross-session.

## 10. Next phase

`sdd-spec` — escribir `specs/departamento-core/spec.md` con scenarios Given/When/Then que codifiquen el contrato estructural del workflow (paths esperados, topic keys, transiciones de `state.yaml`). `sdd-spec` y `sdd-design` pueden correr en paralelo según el DAG.
