# ADR-008: Departamento como Framework Cross-LLM

**Status**: ACCEPTED
**Date**: 2026-05-15
**Sprint**: Sprint 2 Día 2 — Acción cross-LLM
**Related**: ADR-001 (foundational stack), ADR-006 (niveles), ADR-007 (Framework vs Proyectos)

---

## Contexto

Durante Sprint 2 Día 2, surgió pregunta arquitectónica de Julián:

> *"el departamento de software podría quedar para cualquier LLM?"*

Análisis empírico reveló que el Departamento ya es **~90% agent-agnostic** y solo
**~10% específico de Claude/Anthropic**:

### Componentes 100% agent-agnostic

- **Nivel 1** (Filosofía): 7 principios rectores universales
- **Nivel 2** (Arquitectura): A1-A15 + 24 anti-patterns + SOLID + C1-C6
- **Nivel 4** (Dominio): captura de negocio, no de LLM
- **Nivel 5** (Decisiones): ADRs en markdown universal
- **Sistema memoria entre sesiones**: `.md` cortos (cualquier filesystem)
- **Multi-proyecto** (ADR-007): convención agnóstica
- **Templates** (`templates/project-skeleton/`): markdown plano

### Componentes parcialmente Claude-specific (~10%)

- **`.claude/skills/SKILL.md`** formato — Claude Code convention
- **`.claude/agents/`** (subagents) — Claude Code convention
- **`CLAUDE.md`** filename — Claude convention
- **`.gga`** config (`Provider: claude` configurable a openai, gemini)

### Hallazgo del ecosistema

El ecosistema externo **YA es cross-agent por diseño**:

- **GitHub Spec Kit**: 30+ integraciones (Claude Code, Cursor, Codex, Copilot, Gemini CLI, Windsurf, Antigravity, Kiro, OpenCode, Forge...)
- **Antigravity Awesome Skills**: 1,460+ skills multi-agent
- **VoltAgent subagents**: portables a múltiples agentes
- **awesome-design-md**: markdown plano, cualquier LLM lo procesa
- **MCP**: estándar abierto adoptado por Claude, Cursor, Codex, Gemini
- **AGENTS.md**: estándar emergente cross-LLM

---

## Decisión

**Adoptar formalmente al Departamento como framework cross-LLM.**

El Departamento NO debe casarse con ningún agente IA específico. Su valor está
en:

1. **Arquitectura universal** (A1-A15, anti-patterns, SOLID)
2. **Filosofía operativa** (7 principios rectores)
3. **Calibración específica** (vibe coder, Tier 1 commercial robust)
4. **Gobernanza arquitectónica** que alimenta a cualquier agente IA

No en:
- Tooling específico de un agente
- Sintaxis de slash commands de un agente
- Formato de skills/agents de un agente

---

## Implicaciones técnicas

### 1. AGENTS.md como estándar primario (no CLAUDE.md)

`AGENTS.md` ya existe y es agent-agnostic. Es el archivo que cualquier agente IA
debería leer al arrancar.

**CLAUDE.md no se elimina** — se mantiene como compatibilidad con la convención
de Anthropic. Pero su rol pasa a ser:
- **AGENTS.md**: contrato cross-LLM, reglas universales
- **CLAUDE.md**: helper de inicio + complemento Claude-specific

### 2. Documento `docs/AGENT-INTEGRATION.md` (NUEVO)

Documenta cómo integrar el Departamento con cada agente IA conocido:

- Claude Code (Anthropic CLI)
- Cursor (con `.cursor/rules/`)
- Codex CLI (OpenAI)
- Gemini CLI (Google)
- Antigravity (Google IDE con Gemini 3)
- Kiro, OpenCode, Windsurf
- GPT/ChatGPT web (sin filesystem)
- Otros emergentes

### 3. Skills cross-agent compatible

Las skills del Departamento (hoy en `.claude/skills/`) deberían:

- **Funcionalmente**: ser cross-agent (sin asumir Claude-specific syntax)
- **Estructuralmente**: mantenerse en `.claude/skills/` para compatibilidad
  con Claude Code (no romper lo que funciona)
- **Documentalmente**: declarar en su frontmatter qué agentes soportan

Para nuevas skills:
- Preferir formato Antigravity Awesome Skills (cross-agent nativo)
- O Spec Kit skills (cross-agent oficial)

### 4. Spec Kit como workflow primary (pendiente validación)

Spec Kit ya soporta 30+ agentes. Si se adopta (decisión pendiente T1-T2):
- Workflow Constitution → Specify → Plan → Tasks → Implement = cross-LLM nativo
- Las skills mode instalan en formato de cada agente automáticamente
- Resuelve ~60% del cross-LLM "para free"

### 5. Templates cross-agent

`templates/project-skeleton/` debe usar:
- Referencias a "agente IA" en vez de "Claude" donde aplique
- Mencionar AGENTS.md como entry point
- Documentar equivalencias por agente en README

### 6. README raíz actualizado

Mencionar explícitamente:
- "Departamento como framework agent-agnostic"
- Referencia a `docs/AGENT-INTEGRATION.md`
- Hipótesis de que Stallen (uso actual) podría migrarse a otro agente sin re-arquitectar

---

## Componentes que sobreviven a cualquier LLM

Aunque el LLM cambie, estos componentes **NO cambian**:

| Componente | Por qué sobrevive |
|---|---|
| 7 principios rectores | Filosofía, no técnica |
| A1-A15 reglas arquitectónicas | Universales para SaaS multi-tenant |
| 24 anti-patterns | Universales |
| SOLID + C1-C6 | Estándar industria |
| `architecture/` completo | Markdown universal |
| Domain captures (cuando existan) | Negocio, no LLM |
| ADRs en `decisions/` | Markdown universal |
| Sistema memoria `.md` | Filesystem universal |
| Estructura `projects/<slug>/` | Convención universal |
| Templates skeleton | Markdown universal |
| Git workflow | Universal |
| Conventional commits | Universal |
| GGA pre-commit hook | Multi-provider |

---

## Componentes que cambian si el LLM cambia

| Componente | Equivalencia por LLM |
|---|---|
| `CLAUDE.md` lectura inicial | `.cursorrules` (Cursor), `AGENTS.md` (Codex), `.gemini/...` (Gemini) |
| `.claude/skills/` | `.cursor/rules/`, `.codex/agents/`, `.gemini/extensions/`, etc. |
| `.claude/agents/` (subagents) | Cursor agents, Codex subagents, etc. |
| Slash commands específicos | Cada agente tiene su sintaxis |

---

## Trade-offs

### Ventajas

1. **Anti lock-in**: el Departamento sobrevive a cualquier cambio de proveedor LLM
2. **Reusabilidad**: framework potencialmente compartible con otros desarrolladores
3. **Validación universal**: si funciona con N LLMs, sus principios son robustos
4. **Alineado con ecosistema**: el ecosistema YA es cross-agent
5. **Costo bajo AHORA** (~5-10 hs adaptación): refactor futuro sería ~30-50 hs

### Desventajas

1. **Trabajo inmediato**: 5-10 hs distribuidas en sesiones próximas
2. **Posible over-engineering** si NUNCA se usa otro LLM
3. **Más decisiones pendientes**: cómo manejar cada componente cross-agent
4. **Curva de aprendizaje** del usuario para entender equivalencias

---

## Plan de implementación

### Acción 1 — Hoy (esta sesión post-pregunta)
- ✅ Este ADR-008
- ✅ Crear `docs/AGENT-INTEGRATION.md` (documentar equivalencias)
- ✅ Ajustes mínimos a AGENTS.md, README.md, templates

### Acción 2 — Próxima sesión (después de T1-T2 Spec Kit)
- Si Spec Kit se adopta:
  - Documentar workflow cross-LLM en `docs/WORKFLOW-OPERATIVO.md` con Spec Kit como base
  - Adaptar skills propias al formato cross-agent oficial
- Si Spec Kit se rechaza:
  - Construir workflow operativo propio agent-agnostic
  - Documentar equivalencias por agente

### Acción 3 — Sprint 3+ (cuando aplique)
- Validar empíricamente: probar el Departamento con OTRO agente IA (no Claude)
- Documentar la experiencia en ADR-009 (próximo)
- Refinar `docs/AGENT-INTEGRATION.md` con evidencia real

---

## Métricas de éxito

- ✅ Cualquier agente IA puede leer `AGENTS.md` + `architecture/` y entender las reglas
- ✅ `docs/AGENT-INTEGRATION.md` documenta cómo arrancar con N agentes
- ✅ Templates skeleton no asumen agente específico
- ⏳ (futuro) Validación empírica: el Departamento funciona end-to-end con un agente NO-Claude

---

## Riesgos identificados

### 1. Drift entre agentes

**Riesgo**: agentes evolucionan distinto, lo que funciona en uno deja de funcionar en otro.

**Mitigación**:
- Documentar versiones específicas testeadas en `docs/AGENT-INTEGRATION.md`
- Periódicamente re-validar con principal agente activo

### 2. Over-engineering preventivo

**Riesgo**: hacer cross-LLM antes de necesitarlo realmente.

**Mitigación**:
- Costo bajo de implementar (5-10 hs)
- Decisión reversible: si no se usa, se descarta sin perder mucho
- Trade-off: 5-10 hs ahora vs 30-50 hs retrofit después

### 3. Lock-in cultural a un agente específico

**Riesgo**: aunque técnicamente cross-LLM, vos solo usás Claude Code y el Departamento converge inadvertidamente a Claude-only.

**Mitigación**:
- Periodicamente probar con otro agente (ej: Cursor) en sandbox
- Si no se valida con otro agente en Sprint 4+, considerar revertir esta decisión

---

## Alternativas consideradas y rechazadas

### Alternativa 1: Mantener Claude-only

**Rechazada porque**:
- Lock-in a Anthropic
- Va contra evolución del ecosistema (Spec Kit, Antigravity skills cross-agent)
- Costo de retrofit futuro mayor que costo de cross-LLM ahora

### Alternativa 2: Re-escribir todo desde cero para multi-agent

**Rechazada porque**:
- Innecesario: el Departamento ya es ~90% agnóstico
- Costo desproporcionado
- Riesgo de over-engineering

### Alternativa 3: Documentar como deuda y diferir

**Rechazada porque (Julián eligió Opción B explícitamente)**:
- Costo bajo de implementar AHORA
- Costo alto de retrofit DESPUÉS
- Decisión arquitectónica que afecta a todo el roadmap

---

## Acciones derivadas

1. ✅ ADR-008 escrito (este archivo)
2. ✅ Crear `docs/AGENT-INTEGRATION.md`
3. ✅ Actualizar AGENTS.md aclarando rol cross-LLM
4. ✅ Actualizar README.md raíz
5. ✅ Actualizar templates skeleton
6. ⏳ (Próxima sesión) Validar Spec Kit que aporta cross-LLM automáticamente
7. ⏳ (Sprint 3+) Probar empíricamente con otro agente IA

---

## Historial

- v1.0 (2026-05-15) — ACCEPTED. Decidido en Sprint 2 Día 2 tras pregunta de Julián
  sobre cross-LLM. Aplicación del 7° principio rector: meta-producto recursivo —
  el Departamento merece ser agnóstico de la herramienta específica que lo usa.
