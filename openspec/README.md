# OpenSpec — Spec-Driven Development del Departamento

Este directorio contiene las **specs** (requirements + scenarios) y **changes** (features en construcción) del proyecto, siguiendo la convención OpenSpec de Gentle AI.

## Filosofía

OpenSpec aplica el **3° principio rector** (dominio-first) y el **6° principio rector** (descubrir antes de ejecutar):

- **No hay código sin spec aprobada**
- **Las specs capturan dominio del negocio, no implementación**
- **Las changes son atómicas y reversibles**
- **Los deltas se mergean a source of truth al archivar**

## Estructura

```
openspec/
├── config.yaml              ← Config + rules por phase (alineadas a 7 principios)
├── README.md                ← Este archivo
├── specs/                   ← Source of truth (specs aprobados, mergeados)
│   └── {domain}/
│       └── spec.md
└── changes/                 ← Changes activos
    ├── archive/             ← Changes completados (YYYY-MM-DD-{name}/)
    └── {change-name}/       ← Change en construcción
        ├── state.yaml       ← DAG state del workflow
        ├── exploration.md   ← (opcional) Auditoría empírica inicial
        ├── proposal.md      ← Propuesta de qué hacer
        ├── specs/{domain}/spec.md  ← Delta specs (lo que se agrega/modifica)
        ├── design.md        ← Arquitectura técnica de la solución
        ├── tasks.md         ← Checklist DAG de tareas verificables
        └── verify-report.md ← Evidencia empírica de que se cumplieron specs
```

## Domains iniciales

Ver `config.yaml` sección `domains` para la lista actual. Resumen:

| Domain | Qué cubre |
|---|---|
| `departamento-core` | Constitución, protocolos, sistema de trabajo |
| `mcp-servers` | Validadores, patcher, capturar-adn, close-session-validator |
| `skills-sigma` | Skills propias (capture-domain, adversarial-tests, etc.) |
| `integration` | Integración con Stallen y futuros proyectos |
| `observability` | Logging, métricas, health checks |
| `quality-gates` | CI/CD, staging, release process |

Los domains pueden evolucionar. Agregar uno nuevo requiere actualizar `config.yaml`.

## Workflow estándar (DAG)

```
exploration (opcional)
   ↓
proposal
   ↓
specs (delta)
   ↓
design
   ↓
tasks
   ↓
apply (iterativo, marca [x])
   ↓
verify (evidencia empírica)
   ↓
archive (merge a source of truth)
```

Cada phase tiene una **skill SDD** asociada en Gentle AI:
- `sdd-explore` → exploration.md
- `sdd-propose` → proposal.md
- `sdd-spec` → specs/{domain}/spec.md (delta)
- `sdd-design` → design.md
- `sdd-tasks` → tasks.md
- `sdd-apply` → marca [x] en tasks.md
- `sdd-verify` → verify-report.md
- `sdd-archive` → mueve a archive/ + mergea deltas

## Reglas duras

1. **Toda change empieza con `proposal.md`** — sin proposal aprobada, no se escriben specs.
2. **Las specs delta se aplican sobre specs/main**, no sobre nada — siempre leer la spec actual primero.
3. **`tasks.md` es un DAG explícito** — orden por dependencia, no por preferencia.
4. **`verify-report.md` debe tener evidencia empírica** — output de tests, screenshots, mediciones. NO "lo probé y funciona".
5. **Al archivar, los deltas se MERGEAN a `specs/{domain}/spec.md`** — el source of truth se mantiene actualizado.

## Cómo arrancar una change nueva

```
1. Identificar el domain afectado (ver config.yaml)
2. Decidir si es NUEVA capability o MODIFICACIÓN
3. Crear branch: feature/{change-name}
4. Invocar sdd-propose para escribir proposal.md
5. Iterar: spec → design → tasks → apply → verify → archive
6. Merge a main solo después de verify-report.md con evidencia
```

## Integración con el resto del Departamento

- **Engram** (memory MCP): guarda decisions del proceso. Búsqueda rápida de "¿esta spec ya existe?"
- **GGA** (code reviewer): valida que el código generado cumple las reglas de AGENTS.md
- **MCP servers propios** (Sprint 2+): validan que el código cumple las specs Sigma

## Referencias

- Convención canónica: `~/.claude/skills/_shared/openspec-convention.md`
- Skill SDD: `~/.claude/skills/sdd-spec/SKILL.md`
- Constitución del proyecto: `../CLAUDE.md`
- Reglas globales de código: `../AGENTS.md`
- ADR-004 (calibración nivel comercial): `../decisions/ADR-004-calibracion-nivel-comercial.md`
