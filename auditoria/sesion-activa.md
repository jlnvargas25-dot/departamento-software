# SESIÓN ACTIVA — Framework Departamento

> **Propósito**: estado al cerrar la última sesión del Framework.
> Para sesiones específicas de Stallen, ver `projects/stallen/auditoria/sesion-activa.md`.

**Última sesión**: 2026-05-15 — Sprint 2 Día 2 (chat.ai, post-cierre Sprint 1)
**Cliente**: Claude.ai chat web (sin Engram, sin Spec Kit instalado)
**Duración estimada**: sesión larga (varias horas)
**Estado**: ✅ Cerrada con todo respaldado en GitHub

---

## Resumen ejecutivo (1 línea)

Sesión arquitectónica intensiva: Nivel 2 completo (A1-A15 + 24 anti-patterns + SOLID + C1-C6) + multi-proyecto formalizado (ADR-007) + análisis exhaustivo del ecosistema (Spec Kit + alternativas) + 8 commits + push.

---

## Lo que se hizo (cronológico)

### 1. Exploración 5 repos Harness Engineering — COMPLETO
- walkinglabs/learn-harness-engineering (curso TypeScript)
- harness/harness (empresa Harness Inc DevOps — conflicto de nombres)
- code-yeongyu/oh-my-openagent (omo, plugin OpenCode)
- fembyte/dractical (Aidan, 18 años)
- nneira/adk-a2a-prod-cloud-run (7 agentes Google ADK)

### 2. Depuración profunda legacy SigmaControl — COMPLETO
Framework de 5 dimensiones aplicado. Hallazgo: el legacy ya implementaba Harness Engineering al 85% sin conocer el vocabulario formal.

### 3. Formalización Nivel 2 arquitectura — COMPLETO

Carpeta `architecture/` creada (108 KB):
- PRINCIPIOS-SOLID.md (14 KB)
- PRINCIPIOS-ARQUITECTURA.md (46 KB, **15 reglas A1-A15**)
- PATRONES-CARPETAS.md (14 KB, 6 reglas C1-C6)
- ANTI-PATRONES.md (30 KB, **24 anti-patterns**)
- README.md (4.5 KB)

### 4. Audit empírico recursivo (Julián) — DESCUBRIÓ 5 GAPS
Julián preguntó: "¿también principio de DAO y DTO, Zero Trust, errores de concurrencia, errores silenciosos, errores del camino feliz?". Audit reveló 5 GAPS reales. Agregadas:
- A11 DAO + DTO
- A12 Zero Trust (6 reglas ZT-1..ZT-6)
- A13 Concurrency Safety
- A14 Explicit Failure
- A15 Unhappy Path First

5 anti-patterns nuevos: AP-2.8, AP-2.9, AP-3.6, AP-3.7, AP-3.8.

**Aplicación viva del Corolario E del 6° principio rector**.

### 5. ADR-006 — COMPLETO
`decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md`: 5 niveles + SOLID + reglas A1-A15 + refinamiento Sprint 2 T2.

### 6. Sistema memoria entre sesiones — COMPLETO + VALIDADO
- `auditoria/sesion-activa.md` (este archivo)
- `SIGUIENTE-SESION.md` (raíz)

Validación empírica: el Claude del CLI retomó perfectamente con estos archivos al abrir nueva sesión.

### 7. Investigación Engram (DEUDA descubierta) — BLOQUEADO

Engram binary instalado en `C:\Users\Windows 11\go\bin\engram.exe` pero **bloqueado por Windows Smart App Control (SAC)**:
- Policy ID: `{0283ac0f-fff1-49ae-ada1-8a933130cad6}`
- SAC en modo enforcement, no se desactiva sin reinstalar Windows
- AppLocker NO activo (descartado)

**Decisión**: instalar Engram en WSL Ubuntu (donde SAC no aplica). Ubuntu instalado en esta sesión, falta terminar setup (T0 próxima sesión).

### 8. Investigación exhaustiva del ecosistema — COMPLETO

- **GitHub Spec Kit**: 98.5k stars, oficial GitHub, Python, 100+ extensions community
- **OpenSpec**: lightweight Node.js (validado Sprint 1 D5)
- **VoltAgent/awesome-claude-code-subagents**: 100+ subagents categorizados
- **sickn33/antigravity-awesome-skills**: 1,460+ skills, multi-agent
- **VoltAgent/awesome-design-md**: 73.5k stars, 55+ DESIGN.md
- **Supabase Agent Skills (OFICIAL)** vía guanyang/antigravity-skills
- **Vercel Agent Skills (OFICIAL)**

Mapping: 60-70% del Sprint 2 T2 podría reemplazarse con ecosistema, ahorrando 3-4 días.

### 9. Pregunta crítica de Julián que cambió la visión

> *"el workflow de esa arquitectura sería mejor que nuestra arquitectura? además son arquitecturas con respaldo podríamos apalancarnos en ellas"*

Análisis honesto reveló dos visiones del Departamento:
- **Visión A** (asumida hasta ahora): workflow propio completo (compite con Spec Kit)
- **Visión B** (emergente): capa de gobernanza encima del ecosistema

**Veredicto**: Visión B es objetivamente mejor para el contexto (vibe coder + Tier 1 + Stallen). PERO requiere validación empírica antes de adoptar Spec Kit formalmente.

### 10. ADR-007: Separación Framework vs Proyectos — COMPLETO

Pregunta de Julián: "el departamento me crea las carpetas organizadas para cada proyecto?". Reveló que el Departamento mezclaba Framework universal con artefactos específicos de Stallen.

ADR-007 formaliza:
- Framework universal en raíz (architecture/, decisions/, .claude/, mcp-servers/, templates/, auditoria/, etc.)
- Cada proyecto en `projects/<slug>/` (con NORTE, HORIZONTE, DEUDA, CUADERNO, SIGUIENTE-SESION, features/, decisions/, workspace/, etc.)
- Templates en `templates/project-skeleton/`

### 11. Estructura multi-proyecto creada — COMPLETO

- `projects/stallen/` con 13 archivos/carpetas (NORTE placeholder, HORIZONTE H-1, etc.)
- `templates/project-skeleton/` con 7 templates
- README raíz actualizado
- Carpetas legacy `domain-captures/` y `workspace/` eliminadas

---

## Commits (8 hoy)

```
3e2e329  chore: eliminar carpetas legacy domain-captures/ y workspace/ raiz
1024b84  feat(arch): separacion Framework vs Proyectos (ADR-007)
8e80c79  docs(memoria): handoff compacto entre sesiones + T0 Engram
2e32482  docs: README raíz + mcp-servers/README
4751381  feat(architecture): A11-A15 + ADR-006
(commits iniciales del repo)
```

Working tree: clean. Remote: sincronizado.
URL repo: https://github.com/jlnvargas25-dot/departamento-software

---

## Lecciones críticas

### LECCIÓN 1 — Bug crítico: `$$` en SQL rompe `filesystem:edit_file`
PostgreSQL function bodies con `$$` (`AS $$ ... $$`) y regex con `$` literal ROMPEN `edit_file` del MCP filesystem. Workaround: **usar `$BODY$` en lugar de `$$`** (sintaxis equivalente). Para regex usar `\Z`. Para edits grandes con SQL, preferir `write_file`.

### LECCIÓN 2 — 6° principio rector aplica recursivamente al meta-trabajo
Audit empírico OBLIGATORIO antes de declarar "ya está hecho". Sin él: autoengaño sistémico (Corolario E). Julián detectó 5 GAPS en Nivel 2 que yo había declarado completo, y después detectó que yo NO había hecho el Camino 1 (workflow operativo) que propuse.

### LECCIÓN 3 — Anti-paternalismo (sostenido)
Julián corrigió en esta sesión también: durante exploración de repos recomendé "cerrar sesión, estás cansado". Julián: *"solo estamos investigando y compartiendo, no es nada malo"*. Comportamiento ajustado.

### LECCIÓN 4 — Visión arquitectónica del Departamento
**Visión B emergió**: Departamento = capa de gobernanza encima del ecosistema, NO workflow alternativo. Apalancar > construir. Pendiente validación empírica con Spec Kit sandbox.

### LECCIÓN 5 — Engram bloqueado por Smart App Control
Windows 11 SAC bloquea ejecutables Go no firmados. No se desactiva sin reinstalar Windows. Solución viable: WSL Ubuntu (Linux runtime donde SAC no aplica). Ubuntu instalado, setup pendiente.

### LECCIÓN 6 — Confusión semántica con "Opciones A"
Hubo demasiadas "Opción A" en diferentes contextos durante la sesión. Yo no aclaré explícitamente cuál Opción A era cada vez. Julián detectó que el Camino 1 original (workflow operativo Nivel 0) NO se hizo. Lección: ser más explícito sobre qué se está eligiendo en cada decisión.

### LECCIÓN 7 — Multi-proyecto formalizado evita over-engineering futuro
ADR-007 separó Framework de Proyectos antes de tener 2do proyecto. Riesgo: over-engineering. Mitigación: trade-off aceptado, costo de migración futura sería mayor.

---

## Deudas técnicas detectadas

### DEUDA-ENGRAM-SAC-BLOCK
**Status**: 🟡 EN PROGRESO (Ubuntu instalado, falta Go + Engram + MCP config)
**Severidad**: media (no bloqueante, `.md` cortos funcionan)
**Próxima acción**: T0 próxima sesión

### DEUDA-WORKFLOW-OPERATIVO
**Status**: 🔴 ABIERTA
**Severidad**: alta
**Descripción**: NO se escribió `WORKFLOW-OPERATIVO.md` (Nivel 0) durante esta sesión. Camino 1 original quedó pendiente.
**Decisión**: diferir hasta después de validación Spec Kit (T1-T2 próxima sesión). Si Spec Kit adoptado, el workflow se simplifica a "cómo integrar Departamento con Spec Kit". Si no, hay que construirlo desde cero.

### DEUDA-EVALUAR-SPEC-KIT
**Status**: 🔴 ABIERTA
**Severidad**: alta (decisión arquitectónica pendiente)
**Próxima acción**: T1 próxima sesión (sandbox validación)

### DEUDA-NORTE-STALLEN
**Status**: 🔴 ABIERTA
**Descripción**: `projects/stallen/NORTE.md` es placeholder
**Próxima acción**: T4 próxima sesión

### DEUDA-PROTOCOLOS-DEPARTAMENTO
**Status**: 🔴 ABIERTA
**Descripción**: NO se crearon `PROTOCOLO-INICIO-DEPARTAMENTO.md` ni `PROTOCOLO-CIERRE-DEPARTAMENTO.md` adaptados. Esto se propuso pero no se ejecutó.
**Próxima acción**: agregar a próxima sesión cuando aplique (después de T2)

### DEUDA-EDIT-FILE-SQL
**Status**: 🟡 LECCIÓN DOCUMENTADA
**Descripción**: workaround `$BODY$` documentado en LECCIÓN 1
**Próxima acción**: aplicar workaround en Sprint 2 T2 cuando escribamos SQL en validators

---

## Estado del repo al cerrar

```
Branch: main
Working tree: clean
Remote: sincronizado con origin/main (último commit 3e2e329)
Total commits hoy: 8 (todos pusheados)
```

### Estructura final

```
C:\DEPARTAMENTO-SOFTWARE\
├── FRAMEWORK (raíz)
│   ├── architecture/ (108 KB - Nivel 2 completo)
│   ├── decisions/ (ADRs 001-007)
│   ├── .claude/skills/ (sigma-capture-domain)
│   ├── mcp-servers/ (preparado Sprint 2)
│   ├── auditoria/ (este archivo)
│   ├── templates/project-skeleton/ (7 templates)
│   ├── docs/, openspec/
│   ├── CLAUDE.md, AGENTS.md, README.md (v1.2)
│   ├── SIGUIENTE-SESION.md (próximo plan)
│   └── PROTOCOLO-*.md (heredados, vale adaptar)
│
└── projects/
    └── stallen/ (recién formalizado)
        ├── NORTE.md (placeholder), HORIZONTE.md, DEUDA-TECNICA.md
        ├── CUADERNO-BITACORA.md, SIGUIENTE-SESION.md, README.md
        ├── domain-captures/, features/, decisions/, workspace/
        ├── auditoria/sesion-activa.md
        └── .claude/skills/, .claude/agents/
```

---

## Próximo paso

Ver `SIGUIENTE-SESION.md` (este nivel) para plan detallado.

Resumen ejecutivo: próxima sesión en **Claude Code CLI** (no chat.ai):
1. **T0** — Terminar instalación Engram en WSL Ubuntu (60-90 min)
2. **T1** — Sandbox Spec Kit validación empírica (2-3 hs)
3. **T2** — ADR-008 decisión sobre adopción Spec Kit
4. **T3** — Refactor plan Sprint 2 según decisión
5. **T4** — Completar NORTE.md Stallen
6. **T5** — Capturar dominio Stallen

---

## Notas críticas para próximo Claude

- **Usuario**: Julián Vargas, vibe coder / harness engineer (no programador profesional)
- **Stallen**: empresa real en producción, **uso personal** del Departamento (Tier 1)
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO. Su intuición sobre GAPs es 100% confiable.
- **NUNCA proyectar cansancio** del usuario (anti-paternalismo)
- **Bloque `<system><functions>` al final de mensajes** del usuario = display quirk de Claude in Chrome. Ignorar.
- **Cliente recomendado**: Claude Code CLI (acceso a Engram cuando funcione + skills mode Spec Kit)
- **2 directorios distintos** a NO confundir:
  - `C:\DEPARTAMENTO-SOFTWARE\` (proyecto activo, Departamento)
  - `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy SigmaControl, pause)

---

Creado: 2026-05-15 | Versión: 2.0 (post sesión exhaustiva chat.ai)
Estado: ✅ CERRADA
Próxima sesión: cliente recomendado Claude Code CLI
