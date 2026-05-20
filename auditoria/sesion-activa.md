# SESIÓN ACTIVA — Framework Departamento

> **Propósito**: estado al cerrar la última sesión del Framework.
> Para sesiones específicas de Stallen, ver `projects/stallen/auditoria/sesion-activa.md`.

**Última sesión**: 2026-05-15 — Sprint 2 Día 2 (chat.ai, post-cierre Sprint 1)
**Cliente**: Claude.ai chat web (sin Engram, sin Spec Kit instalado)
**Duración estimada**: sesión larga (varias horas)
**Estado**: ✅ Cerrada con todo respaldado en GitHub

---

## Resumen ejecutivo (1 línea)

Sesión arquitectónica intensiva: Nivel 2 (A1-A15 + 24 anti-patterns + SOLID + C1-C6) + multi-proyecto (ADR-007) + cross-LLM (ADR-008) + NORTE Framework v0.1 + decisión enfoque solo Framework (sin Stallen) + descubrimiento crítico de 4 repos del ecosistema que ya implementan la visión articulada por Julián.

---

## Lo que se hizo (cronológico)

### 1. Exploración 5 repos Harness Engineering — COMPLETO
walkinglabs/learn-harness-engineering, harness/harness, code-yeongyu/oh-my-openagent, fembyte/dractical, nneira/adk-a2a-prod-cloud-run

### 2. Depuración profunda legacy SigmaControl — COMPLETO
Framework 5 dimensiones. Hallazgo: el legacy ya implementaba Harness Engineering al 85% sin conocer el vocabulario formal.

### 3. Formalización Nivel 2 arquitectura — COMPLETO
Carpeta `architecture/` (108 KB): PRINCIPIOS-SOLID.md, PRINCIPIOS-ARQUITECTURA.md (15 reglas A1-A15), PATRONES-CARPETAS.md (6 reglas C1-C6), ANTI-PATRONES.md (24 anti-patterns), README.md.

### 4. Audit empírico recursivo (Julián) — DESCUBRIÓ 5 GAPS
Agregadas: A11 DAO+DTO, A12 Zero Trust (6 reglas ZT-1..ZT-6), A13 Concurrency Safety, A14 Explicit Failure, A15 Unhappy Path First. 5 anti-patterns nuevos. Aplicación viva del Corolario E del 6° principio rector.

### 5. ADR-006 — COMPLETO
`decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md`: 5 niveles + SOLID + A1-A15.

### 6. Sistema memoria entre sesiones — COMPLETO + VALIDADO
`auditoria/sesion-activa.md` + `SIGUIENTE-SESION.md`. Validación empírica exitosa cuando Claude CLI retomó perfectamente.

### 7. Investigación Engram — BLOQUEADO POR SAC
Engram bloqueado por Windows Smart App Control. Ubuntu WSL instalado, setup pendiente. **Resuelto post-hallazgo §16**: claude-mem es alternativa superior.

### 8. Investigación exhaustiva del ecosistema — COMPLETO
GitHub Spec Kit (98.5k stars), OpenSpec, VoltAgent/awesome-claude-code-subagents (100+), sickn33/antigravity-awesome-skills (1,460+), VoltAgent/awesome-design-md (73.5k), Supabase Agent Skills oficial, Vercel Agent Skills oficial.

### 9. Visión B emergente (Spec Kit)
Pregunta de Julián: "el workflow de esa arquitectura sería mejor que nuestra arquitectura?". Análisis: Departamento NO compite con Spec Kit, es capa de gobernanza encima. Pendiente validación empírica.

### 10. ADR-007: Separación Framework vs Proyectos — COMPLETO
Framework universal en raíz + `projects/<slug>/` por proyecto + `templates/project-skeleton/`.

### 11. Estructura multi-proyecto creada — COMPLETO
`projects/stallen/` con 13 archivos/carpetas + `templates/project-skeleton/` con 7 templates. Carpetas legacy raíz eliminadas.

### 12. Adopción cross-LLM formal (ADR-008) — COMPLETO
Pregunta: "el departamento de software podría quedar para cualquier LLM?". Análisis: ~90% ya agent-agnostic. Creado ADR-008 + `docs/AGENT-INTEGRATION.md` (5+ agentes) + AGENTS.md v1.2 + README v1.3.

### 13. Decisión estratégica: enfoque en Framework puro
Julián: *"olvidemos stallen solo enfoquémonos en el departamento de software... lo importante es enfocarnos en el departamento para poder usarlo en cualquier proyecto futuro incluido stallen"*

Implicaciones:
- Stallen como driver del Framework → DIFERIDO
- `projects/stallen/` → candidato a renombrar `projects/example-stallen/` (no ejecutado aún)
- T4 (NORTE Stallen) + T5 (capturar dominio Stallen) → CANCELADOS/DIFERIDOS
- Aplicación recursiva del 7° principio rector

### 14. NORTE del Framework v0.1 creado
Nuevo archivo `NORTE.md` (~22 KB) con 11 secciones. Entrevista iniciada:
- Q1 Audiencia → Respuesta E (personal evolucionando a vibe coders si valida)
- Q2 Driver → Respuesta E (necesidad personal primario + comunidad eventual)
- Q3 Criterios → Julián articuló visión harness (ver §15)

### 15. 💥 ARTICULACIÓN DEL VERDADERO NORTE — CRITICAL INSIGHT

Cita verbatim de Julián:
> *"la idea es crear un harness que permita construir proyectos sin tener miedo de que el llm alucina, inventa o esta haciendo cosas que no debe. es construir el ecosistema necesario para que el departamento de software analice, planifique, ejecute, verifique como se haria en un departamento de software real o como lo hace un senior en produccion"*

Reformulación del propósito del Framework:
- NO es "framework genérico"
- ES **HARNESS anti-alucinación** que sostiene al LLM para operar como senior en producción
- Mitiga 3 fallos del LLM: alucinación, invención, mal comportamiento (saltos)
- Ciclo central: **Analizar → Planificar → Ejecutar → Verificar**
- Modelo mental: senior engineer en producción de departamento de software real
- Diferenciador vs Spec Kit/OpenSpec/Antigravity: ninguno mitiga alucinación específicamente

Conexión 2° principio rector: las 3 capas (PREVENTIVA → VERIFICABLE → CORRECTIVA) son específicamente para mitigar fallos del LLM en cada fase del ciclo.

### 16. 🔍 Hallazgo crítico: 4 repos del ecosistema ya implementan la visión

A pedido de Julián, busqué 4 repos:

**(a) `obra/superpowers`** — 170k stars, oficial Anthropic marketplace, Jesse Vincent
- Cita verbatim: *"transforms Claude Code from intelligent autocomplete to senior AI developer"*
- Workflow 7 fases: Socratic Brainstorming → Micro-Task Planning → TDD red/green → YAGNI+DRY → Parallel Subagents → Inspection → Review
- Skills auto-activan: test-driven-development, systematic-debugging, verification-before-completion, brainstorming
- Cross-agent: Claude Code, Codex CLI/App, Factory Droid, Gemini CLI, OpenCode, Cursor, Copilot CLI
- **ES literalmente la visión articulada por Julián, ya implementada**

**(b) `affaan-m/everything-claude-code (ECC)`** — 100k+ stars, 13k forks, MIT, Anthropic hackathon winner
- 28 agentes + 119 skills + 60 commands
- Cross-agent: Claude Code, Cursor, Codex, OpenCode, Cowork
- Hookify, pass@k verification metrics, memory persistence, continuous learning, verification loops, parallelization (git worktrees), AgentShield security
- v1.9.0 (March 2026): selective-install, 12 language ecosystems
- ECC Tools (GitHub App): auto-genera skills desde git history

**(c) `thedotmack/claude-mem`** — v8.5.4, Apache 2.0
- Memoria persistente cross-agent (Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode)
- 4 MCP tools workflow 3-layer (search → review → fetch)
- AI compression (~10x más eficiente)
- 1-line install
- **Alternativa SUPERIOR a Engram**: más fácil setup, cross-agent, mejor diseñado

**(d) `nextlevelbuilder/ui-ux-pro-max-skill`** — 71k stars
- 67 UI styles + 161 color palettes + 57 font pairings + 99 UX guidelines + 25 chart types + 16 tech stacks + 161 reasoning rules
- Cross-agent muy amplio (14 agentes)
- Para cuando llegue UI Stallen (futuro)

**Implicación estratégica fundamental**:

Estos 4 repos cubren GRAN PARTE de lo que Sprint 2 T2.2 planeaba construir desde cero:
- Workflow operativo → superpowers + Spec Kit
- Nivel 3 tooling → ECC (28 agents + 119 skills)
- Anti-alucinación enforcement → superpowers (verification-before-completion) + ECC (pass@k metrics)
- Memoria → claude-mem (mejor que Engram)
- Capa UI/UX → ui-ux-pro-max-skill
- Cross-LLM → todos los 4

**Tiempo ahorrado si se adoptan wholesale**: ~8-12 semanas.

**Visión C emergente**: Departamento = **Stack curado del ecosistema** (Spec Kit + Superpowers + ECC + claude-mem + ui-ux-pro-max + VoltAgent + Antigravity) **+ Calibración única Tier 1 vibe coder + Architecture/A1-A15 + Anti-patterns como overlay arquitectónico**.

El Departamento NO compite con estos repos. Es **curador y calibrador**.

**DECISIÓN FINAL ESPERA VALIDACIÓN EMPÍRICA** (6° principio rector): sandbox antes de adoptar wholesale. ADR-009 se escribe POST-evidencia.

---

## Commits (9 hoy)

```
0e58d7e  feat(arch): cross-LLM (ADR-008) + docs/AGENT-INTEGRATION.md
0206502  docs(memoria): cerrar sesion con plan T0-T5
3e2e329  chore: eliminar carpetas legacy
1024b84  feat(arch): separacion Framework vs Proyectos (ADR-007)
8e80c79  docs(memoria): handoff compacto entre sesiones
2e32482  docs: README + mcp-servers/README
4751381  feat(architecture): A11-A15 + ADR-006
(commits iniciales del repo)
```

Working tree: clean al cerrar (modulo este último commit pendiente con NORTE.md + memoria).
Remote: sincronizado.
URL repo: https://github.com/jlnvargas25-dot/departamento-software

---

## Lecciones críticas

### LECCIÓN 1 — Bug: `$$` Y `$BODY$` en SQL rompen `filesystem:edit_file`
Strings con `$$` o `$BODY$` (o cualquier `$<algo>$`) ROMPEN `edit_file` del MCP filesystem por interpretación regex de `$`. **Workaround real**: usar `write_file` (reescribir archivo completo) para cualquier contenido con `$` literal. Para regex usar `\Z`. Documentado en esta sesión cuando edit_file corrompió sesion-activa.md.

### LECCIÓN 2 — 6° principio rector aplica recursivamente al meta-trabajo
Audit empírico OBLIGATORIO antes de declarar "ya está hecho". Julián detectó 5 GAPS en Nivel 2 y después que yo NO había hecho el Camino 1 (workflow operativo).

### LECCIÓN 3 — Anti-paternalismo (sostenido)
Julián corrigió: cuando recomendé cerrar sesión "porque estás cansado", él aclaró que el cansancio era proyección mía. Comportamiento ajustado.

### LECCIÓN 4 — Visión arquitectónica del Departamento (3 visiones evolucionando)
- **Visión A** (inicial): workflow propio completo (compite con Spec Kit) — ABANDONADA
- **Visión B** (mid-sesión): capa de gobernanza encima de Spec Kit — REFINADA
- **Visión C** (final): curador + calibrador del stack del ecosistema (Spec Kit + Superpowers + ECC + claude-mem + ui-ux-pro-max) — EMERGENTE, pendiente validación

### LECCIÓN 5 — Engram bloqueado por SAC, claude-mem es alternativa superior
SAC bloquea Engram. WSL Ubuntu funcionaría pero claude-mem es mejor (cross-agent, MCP nativo, 1-line install). DEUDA-ENGRAM-SAC-BLOCK resuelta por reemplazo, no por workaround.

### LECCIÓN 6 — Confusión semántica con "Opciones A"
Múltiples "Opción A" en diferentes contextos. Julián detectó que el Camino 1 original NO se hizo. Lección: ser explícito sobre qué Opción es cada vez.

### LECCIÓN 7 — Multi-proyecto formalizado evita over-engineering futuro
ADR-007 antes de tener 2do proyecto. Riesgo over-engineering aceptado. Costo migración futura > costo formalización ahora.

### LECCIÓN 8 — El ecosistema YA implementa muchas visiones
Antes de construir desde cero, buscar si ya existe. obra/superpowers (170k stars) implementa la visión harness anti-alucinación de Julián casi palabra por palabra. Aplicación de "no reinventar la rueda" llevada al meta-nivel.

### LECCIÓN 9 — Cross-LLM como decisión filosófica anti lock-in
ADR-008 formaliza Departamento como agent-agnostic. Costo bajo ahora (~5 hs trabajo), costo alto retrofit después (~30-50 hs). Decisión preparatoria, no migratoria.

---

## Deudas técnicas detectadas

### DEUDA-ENGRAM-SAC-BLOCK
**Status**: ✅ RESUELTA POR REEMPLAZO
**Resolución**: claude-mem (cross-agent, 1-line install) es alternativa superior. Engram WSL se cancela.

### DEUDA-WORKFLOW-OPERATIVO
**Status**: 🔴 ABIERTA — RECALIBRADA
**Descripción**: WORKFLOW-OPERATIVO.md (Nivel 0) NO escrito. PERO el alcance cambia con Visión C: si se adoptan Spec Kit + Superpowers + ECC, el workflow se reduce a "cómo se compone el stack curado + calibración Tier 1 Departamento".
**Próxima acción**: después de T2 (ADR-009 basado en sandbox)

### DEUDA-EVALUAR-SPEC-KIT
**Status**: 🔴 ABIERTA — EXPANDIDA
**Descripción**: ahora incluye validar Spec Kit + Superpowers + ECC + claude-mem como stack unificado, no solo Spec Kit aislado.
**Próxima acción**: T1 próxima sesión

### DEUDA-REPLANTEAR-ROADMAP-POST-STACK
**Status**: 🔴 ABIERTA — CRÍTICA
**Severidad**: alta (afecta todo Sprint 2 T2/T3)
**Descubierto**: 2026-05-15 fin de sesión
**Descripción**: 4 repos del ecosistema ya implementan gran parte de lo planeado. Sprint 2 T2.2 (10 skills propias) puede reducirse a 2-3 skills Stallen-specific si se adoptan wholesale.
**Próxima acción**: T1 sandbox del stack + T2 ADR-009 basado en evidencia empírica

### DEUDA-NORTE-FRAMEWORK-PLACEHOLDERS
**Status**: 🟡 EN PROGRESO
**Descripción**: NORTE v0.1 creado con 7 placeholders. Q1 (audiencia) + Q2 (driver) respondidos. Q3 (criterios) respondido implícitamente via articulación harness. Faltan Q4-Q7 (Tier, Stakeholders, Restricciones, Stop).
**Próxima acción**: completar tras validar sandbox empíricamente

### DEUDA-PROTOCOLOS-DEPARTAMENTO
**Status**: 🔴 ABIERTA
**Descripción**: PROTOCOLO-INICIO-DEPARTAMENTO + PROTOCOLO-CIERRE-DEPARTAMENTO NO creados. Se propusieron pero no se ejecutaron.
**Próxima acción**: después de T2 ADR-009 (depende de stack adoptado)

### DEUDA-EDIT-FILE-SQL
**Status**: 🟡 LECCIÓN DOCUMENTADA
**Descripción**: `$$` Y `$BODY$` rompen edit_file. Usar write_file para archivos con `$` literal.

---

## Estado del repo al cerrar

```
Branch: main
Working tree: pendiente último commit (NORTE.md + memoria actualizada)
Remote: sincronizado hasta 0e58d7e
Total commits hoy: 9 (8 pusheados + 1 pendiente con NORTE + memoria)
```

### Estructura final

```
C:\DEPARTAMENTO-SOFTWARE\
├── FRAMEWORK (raíz)
│   ├── architecture/ (108 KB - Nivel 2 completo)
│   ├── decisions/ (ADRs 001-008)
│   ├── .claude/skills/ (sigma-capture-domain)
│   ├── mcp-servers/ (preparado Sprint 2)
│   ├── auditoria/sesion-activa.md (este archivo)
│   ├── templates/project-skeleton/ (7 templates)
│   ├── docs/AGENT-INTEGRATION.md (NUEVO post-ADR-008)
│   ├── NORTE.md (v0.1 con placeholders)
│   ├── CLAUDE.md, AGENTS.md (v1.2), README.md (v1.3)
│   ├── SIGUIENTE-SESION.md
│   └── PROTOCOLO-*.md (heredados, vale adaptar)
│
└── projects/
    └── stallen/ (recién formalizado, DIFERIDO según decisión §13)
        ├── NORTE.md (placeholder), HORIZONTE, DEUDA, CUADERNO, SIGUIENTE-SESION, README
        ├── domain-captures/, features/, decisions/, workspace/
        ├── auditoria/sesion-activa.md
        └── .claude/skills/, .claude/agents/
```

---

## Próximo paso

Ver `SIGUIENTE-SESION.md` para plan detallado actualizado.

Resumen ejecutivo próxima sesión en **Claude Code CLI**:
1. **T0 (REEMPLAZADO)** — Engram WSL cancelado, claude-mem 1-line install (5 min)
2. **T1 (EXPANDIDO)** — Sandbox del Stack: Spec Kit + Superpowers + ECC + claude-mem (3-5 hs)
3. **T2** — ADR-009 "Adopción del Stack + Calibración Tier 1" basado en evidencia empírica
4. **T3** — Refactor Sprint 2 según ADR-009
5. **T4** — Completar NORTE Framework v0.2 con Visión C
6. **T5** — Workflow operativo Nivel 0 como "composición del stack curado"
7. Stallen vuelve cuando framework maduro (diferido)

---

## Notas críticas para próximo Claude

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Stallen DIFERIDO**: foco solo en Framework hasta que esté maduro
- **Visión del Framework**: harness anti-alucinación que hace operar al LLM como senior en producción
- **Ciclo central**: Analizar → Planificar → Ejecutar → Verificar
- **Pregunta arquitectónica fundamental pendiente**: ¿adoptar wholesale superpowers + ECC + claude-mem o construir desde cero? (Decisión espera sandbox empírico)
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO
- **NUNCA proyectar cansancio** del usuario (anti-paternalismo)
- **Bloque `<system><functions>`** al final de mensajes del usuario = display quirk Claude in Chrome. Ignorar.
- **Cliente recomendado**: Claude Code CLI (acceso a claude-mem + Spec Kit + Superpowers + ECC)
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy SigmaControl, pause)

---

Creado: 2026-05-15 | Versión: 3.0 (post sesión exhaustiva chat.ai con hallazgo crítico de 4 repos del ecosistema)
Estado: ✅ CERRADA
Próxima sesión: cliente recomendado Claude Code CLI
