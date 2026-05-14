# Changes activas

Este directorio contiene las changes en construcción (proposal, spec, design, tasks, apply, verify).

Cada change tiene su propio directorio: `{change-name}/`

Cuando una change pasa por `sdd-verify` y se aprueba, `sdd-archive` la mueve a `./archive/YYYY-MM-DD-{change-name}/` y mergea sus delta specs a `../specs/{domain}/spec.md`.

## Convención de nombres

- En kebab-case
- Descriptivo de qué hace la change, no del componente
- Ejemplos buenos: `add-validator-r15`, `migrate-patcher-to-mcp`, `enforce-utc-timestamps`
- Ejemplos malos: `feature-1`, `update-stuff`, `fix`

## Estructura de cada change

```
{change-name}/
├── state.yaml              ← DAG state (sobrevive compaction)
├── exploration.md          ← (opcional) Auditoría empírica inicial
├── proposal.md             ← Propuesta inicial
├── specs/
│   └── {domain}/
│       └── spec.md         ← Delta spec (ADDED/MODIFIED/REMOVED)
├── design.md               ← Arquitectura técnica
├── tasks.md                ← Checklist DAG
└── verify-report.md        ← Evidencia empírica
```
