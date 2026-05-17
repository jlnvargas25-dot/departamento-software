# ADR-007: Separación Framework vs Proyectos en el Departamento

**Status**: ACCEPTED
**Date**: 2026-05-15
**Sprint**: Sprint 2 Día 2 — Acción 2.0
**Supersedes**: refina ADR-006 (5 niveles de reglas + SOLID)
**Related**: ADR-001 (foundational stack), ADR-004 (tier commercial), ADR-006 (niveles)

---

## Contexto

Durante Sprint 2 Día 2 (post-cierre Sprint 1), surgió pregunta arquitectónica
de Julián: *"el departamento de software me crea las carpetas organizados
para cada proyecto que se vaya iniciando?"*

Análisis empírico reveló que la estructura actual del Departamento mezcla
**dos cosas distintas**:

1. **Framework universal** (no cambia por proyecto):
   - 7 principios rectores
   - 15 reglas A1-A15
   - 24 anti-patterns
   - SOLID + C1-C6
   - Skills universales (sigma-capture-domain)
   - Protocolos
   - ADRs del Departamento mismo

2. **Artefactos específicos de proyectos** (cambian por proyecto):
   - Visión del proyecto (NORTE)
   - Hitos (HORIZONTE)
   - Captura de dominio
   - Decisiones técnicas específicas
   - Código (workspace)
   - Memoria operativa
   - Skills/agents específicos del proyecto

Hoy todo está en el mismo nivel del repo, lo cual genera 3 problemas:

- **No reusabilidad**: si arranco proyecto nuevo (cliente, sandbox, otro
  uso personal), no hay convención de dónde poner sus archivos sin
  contaminar el framework.
- **No validación empírica del framework**: cuando solo hay un proyecto,
  no se distingue qué reglas son verdaderamente universales vs cuáles son
  específicas. Solo se descubre con 2+ proyectos consumiendo el framework.
- **No sharing**: si en algún momento se quiere compartir el framework
  (open source, comercial, otro equipo), hay que separar manualmente lo
  específico de Stallen.

Esto está alineado con el **patrón que Spec Kit ya resolvió** (Project-Local
Overrides en `.specify/templates/overrides/` + Extensions + Presets):
framework universal + customizaciones por proyecto.

---

## Decisión

Adoptar estructura **Framework vs Proyectos** en el Departamento:

```
C:\DEPARTAMENTO-SOFTWARE\
│
├── FRAMEWORK (universal — raíz del repo)
│   ├── architecture/                  ← A1-A15, anti-patterns, SOLID, C1-C6
│   ├── decisions/                     ← ADRs DEL DEPARTAMENTO mismo
│   ├── .claude/
│   │   ├── skills/                    ← Skills universales
│   │   └── agents/                    ← Subagents universales (cuando se adopten)
│   ├── mcp-servers/                   ← MCP servers del Departamento
│   ├── auditoria/                     ← Memoria del Departamento mismo (cross-proyecto)
│   ├── templates/                     ← Templates para nuevos proyectos
│   │   └── project-skeleton/
│   ├── CLAUDE.md, AGENTS.md           ← Principios universales
│   ├── README.md                      ← Overview del Departamento
│   ├── DEPARTAMENTO-DE-SOFTWARE.md    ← Diseño Nivel 1
│   ├── PROTOCOLO-*.md                 ← Protocolos universales
│   ├── SIGUIENTE-SESION.md            ← Handoff táctico del Framework
│   └── (otros archivos universales)
│
└── projects/                          ← Cada proyecto en su carpeta
    │
    ├── stallen/                       ← Tu proyecto principal
    │   ├── NORTE.md                   ← Visión Stallen
    │   ├── HORIZONTE.md               ← Hitos 1-3 meses Stallen
    │   ├── DEUDA-TECNICA.md           ← Deuda específica Stallen
    │   ├── CUADERNO-BITACORA.md       ← Bandeja ideas Stallen
    │   ├── SIGUIENTE-SESION.md        ← Handoff específico Stallen
    │   ├── README.md                  ← Overview del proyecto Stallen
    │   ├── domain-captures/
    │   │   └── stallen-domain.md
    │   ├── features/                  ← Cada feature en su carpeta
    │   ├── decisions/                 ← ADRs específicos Stallen
    │   ├── workspace/                 ← Código real Stallen
    │   ├── auditoria/
    │   │   ├── sesion-activa.md       ← Estado Stallen al cerrar
    │   │   └── memoria-historial.md
    │   └── .claude/                   ← Skills/agents específicos Stallen
    │       ├── skills/
    │       └── agents/
    │
    ├── sandbox-spec-kit/              ← Validación del ecosistema (Ruta 4 Acción 1)
    │   └── (config Spec Kit + casos de prueba)
    │
    └── (futuros proyectos)
```

## Convención: qué va dónde

| Tipo de archivo | Framework raíz | projects/`<slug>`/ |
|---|---|---|
| Principios filosóficos (Nivel 1) | ✅ | — |
| Reglas A1-A15 (Nivel 2) | ✅ | — |
| Anti-patterns universales | ✅ | — |
| Skills universales (sigma-capture-domain) | ✅ | — |
| Skills específicos del proyecto (multitenancy Stallen) | — | ✅ `.claude/skills/` |
| Subagents universales | ✅ | — |
| Subagents específicos del proyecto | — | ✅ `.claude/agents/` |
| ADRs del Departamento mismo | ✅ `decisions/` | — |
| ADRs específicos del proyecto | — | ✅ `decisions/` |
| Captura de dominio del proyecto | — | ✅ `domain-captures/` |
| Código del proyecto | — | ✅ `workspace/` |
| Features del proyecto | — | ✅ `features/` |
| Visión del proyecto (NORTE) | — | ✅ |
| Hitos del proyecto (HORIZONTE) | — | ✅ |
| Deuda técnica del proyecto | — | ✅ |
| Cuaderno bitácora del proyecto | — | ✅ |
| Memoria al cerrar sesión del Framework | ✅ `auditoria/sesion-activa.md` | — |
| Memoria al cerrar sesión del Proyecto | — | ✅ `auditoria/sesion-activa.md` |
| Protocolos universales (INICIO, CIERRE) | ✅ | — |
| Templates para nuevo proyecto | ✅ `templates/project-skeleton/` | — |

---

## Cómo se crea un proyecto nuevo

**Manual (v1.0 — actual)**:

```powershell
# 1. Crear carpeta del proyecto
mkdir projects/<slug>

# 2. Copiar templates
xcopy /E /I templates/project-skeleton projects/<slug>

# 3. Renombrar templates removiendo .template
# (manual o con script)

# 4. Llenar NORTE.md con visión del proyecto

# 5. Editar SIGUIENTE-SESION.md con primer paso

# 6. Commit inicial
git add projects/<slug>
git commit -m "feat(project): inicializar proyecto <slug>"
```

**Automatizado (v2.0 — futuro Sprint 3+)**:

Script `departamento new-project --name=<slug> --tier=<N>` que:
- Crea estructura desde `templates/project-skeleton/`
- Pre-llena NORTE con datos básicos
- Configura git
- Hace commit inicial

NO se construye todavía. Esperar evidencia con 2do proyecto real.

---

## Cómo se sincroniza Framework con Proyectos

**Framework es source of truth**. Proyectos consumen el framework via referencia
(NO copia).

Cuando un proyecto necesita override:
- Documentar en `projects/<slug>/decisions/ADR-XXX-override-de-<regla>.md`
- Justificar por qué la regla universal no aplica
- Mantener tracking del divergence

Si el override se vuelve común en múltiples proyectos:
- Promover a reglas universales del Framework (Nivel 2)
- O crear sub-regla del Framework para ese caso

**Para versionado del Framework**: usar tags semánticos (v1.0.0, v1.1.0).
Cuando el Framework actualiza, los proyectos eligen cuándo upgradar
mediante referencia al tag específico.

(Implementación de versionado en Sprint 3+, no urgente.)

---

## Conexión con Spec Kit (si se adopta)

Si en Sprint 3 se adopta GitHub Spec Kit (pendiente validación empírica):

```
Framework architecture/PRINCIPIOS-ARQUITECTURA.md
   ↓ se condensa en
projects/<slug>/.specify/memory/constitution.md (input Spec Kit)
   ↓ guía a
/speckit.specify, /speckit.plan, /speckit.tasks, /speckit.implement
en el contexto de projects/<slug>/
```

Cada proyecto tiene su propio `.specify/` con constitution heredada del
Framework + overrides específicos.

---

## Migración de archivos existentes (hoy)

| Archivo actual | Mover a | Razón |
|---|---|---|
| `domain-captures/` | `projects/stallen/domain-captures/` | Capturas serán de Stallen |
| `workspace/` | `projects/stallen/workspace/` | Código será de Stallen |
| `auditoria/sesion-activa.md` actual | Mantener en framework `auditoria/` | Esta sesión es del Departamento mismo (construir el framework) |
| `SIGUIENTE-SESION.md` actual | Mantener en framework | Plan próxima sesión del Departamento |
| (futuro) `auditoria/sesion-activa.md` Stallen | `projects/stallen/auditoria/sesion-activa.md` | Cuando empecemos T1 |

**Importante**: ningún archivo del Framework universal (`architecture/`,
`decisions/`, `.claude/skills/`, `mcp-servers/`, CLAUDE.md, AGENTS.md,
README.md, PROTOCOLO-*.md, DEPARTAMENTO-DE-SOFTWARE.md) se mueve.
Quedan en raíz.

---

## Decisión sobre el archivo `auditoria/sesion-activa.md` del Framework

Pregunta: ¿la memoria del Framework debe estar en raíz `auditoria/` o
debe haber separación?

**Decisión**: SÍ hay separación.

- `auditoria/sesion-activa.md` en raíz = sesiones del Framework mismo
  (Sprint 1 cerrado, Sprint 2 construyendo arquitectura, etc.)
- `projects/<slug>/auditoria/sesion-activa.md` = sesiones del proyecto
  (T1 capturar dominio Stallen, T2 sigma-validators-r, etc.)

Razón: muchas sesiones tocarán ambos (cambios al Framework + cambios al
proyecto). En esos casos, escribir SÍ en ambos archivos para mantener
audit trail separado.

Si una sesión solo toca uno: actualizar solo ese.

---

## Implicaciones

### Sobre Sprint 2 (en curso)

- **Acción 2.0**: crear estructura `projects/stallen/` + `templates/project-skeleton/` (~1.5 hs)
- **Acción 1 (sandbox Spec Kit)**: va a `projects/sandbox-spec-kit/`
- **Acción 2 (replicar legacy adaptado)**: NORTE/HORIZONTE/DEUDA/CUADERNO van a `projects/stallen/`
- **T1 (capturar dominio Stallen)**: output en `projects/stallen/domain-captures/stallen-domain.md`

### Sobre futuros proyectos

- Sandbox para validar tools nuevas → `projects/sandbox-<nombre>/`
- Si eventual cliente nuevo → `projects/<cliente>/`
- Si el Departamento se vuelve reusable (open source, comercial) → separar
  `projects/` del repo público

### Sobre reusabilidad del Framework

Eventualmente el Framework podría ser un repo separado o submodule. Hoy
no, pero la estructura lo permite.

---

## Riesgos identificados

1. **Sobre-engineering**: posible si nunca aparece 2do proyecto. Mitigación:
   trade-off aceptado, costo de migración futura es mayor.

2. **Confusion sobre dónde va cada cosa**: posible al principio. Mitigación:
   tabla de convención explícita arriba + templates.

3. **Duplicación entre auditoria/ Framework y projects/*/auditoria/**:
   posible si las sesiones tocan ambos. Mitigación: dos archivos
   diferenciados con audit trail separado.

4. **Versionado del Framework no resuelto**: hoy no se versiona explícitamente.
   Mitigación: Sprint 3+ para tags semánticos cuando haya 2do proyecto.

---

## Alternativas consideradas y rechazadas

### Alternativa 1: Mantener estructura plana

Rechazada porque:
- No escala a múltiples proyectos
- Confunde framework con proyecto
- Genera re-trabajo cuando aparece 2do proyecto

### Alternativa 2: Framework y proyectos en repos separados

Rechazada por ahora porque:
- Más complejidad (submodules, versionado cross-repo)
- No hay 2do proyecto todavía que justifique
- Trade-off de simplicidad: 1 repo, 2 niveles internos

Considerar en Sprint 4+ si hay evidencia de necesidad.

### Alternativa 3: Convención por prefijo (sin carpetas)

Ej: `stallen-NORTE.md`, `stallen-domain-captures/`, etc.

Rechazada porque:
- Genera ruido en raíz del repo
- Más difícil de gitignorear por proyecto
- Convención de carpetas es más estándar (Spec Kit lo confirma)

---

## Acciones derivadas

1. ✅ ADR-007 escrito (este archivo)
2. ⏳ Crear estructura `projects/stallen/` (próxima acción)
3. ⏳ Crear `templates/project-skeleton/`
4. ⏳ Migrar `domain-captures/` y `workspace/` actuales
5. ⏳ Actualizar referencias en CLAUDE.md, AGENTS.md, README.md
6. ⏳ Commit + push
7. ⏳ Después: Ruta 4 (sandbox Spec Kit + Acción 2 legacy adaptado + T1)

---

## Métricas de éxito

- 2do proyecto (sandbox-spec-kit) se crea siguiendo la convención sin
  fricción (Sprint 2 Día 2 o 3)
- T1 (capturar dominio Stallen) produce artefacto correctamente ubicado
  en `projects/stallen/domain-captures/`
- 0 archivos del Framework se contaminan con Stallen-specific content
- Cuando aparezca 3er proyecto (Sprint 4+), la convención se aplica sin
  modificar el ADR-007

---

## Historial

- v1.0 (2026-05-15) — ACCEPTED. Decidido en Sprint 2 Día 2 tras pregunta
  de Julián sobre multi-proyecto. Justificación: aplicación 6° principio
  rector (descubrir antes de ejecutar) + 7° principio rector (meta-producto
  recursivo: el Framework merece SU PROPIA arquitectura limpia).
