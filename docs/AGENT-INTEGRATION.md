# Integración del Departamento con Agentes IA

> **Propósito**: explicar cómo integrar el Departamento de Software con
> diferentes agentes IA. El Departamento es **agent-agnostic by design**
> (ADR-008): sus principios universales sobreviven a cualquier LLM específico.

**Versión**: 1.0 (2026-05-15, post ADR-008)

---

## Filosofía

El Departamento de Software es **arquitectura + filosofía + calibración**, NO
un wrapper de un LLM específico. Cualquier agente IA puede consumir su
gobernanza arquitectónica.

Lo que **NO cambia** según el agente:
- 7 principios rectores
- 15 reglas A1-A15 + 24 anti-patterns
- SOLID + C1-C6
- Sistema de memoria entre sesiones (`.md` cortos)
- Estructura multi-proyecto (`projects/<slug>/`)
- ADRs en `decisions/`

Lo que **SÍ cambia** según el agente:
- Cómo lee el contexto inicial (CLAUDE.md, AGENTS.md, .cursorrules, etc.)
- Dónde viven las skills (`.claude/skills/`, `.cursor/rules/`, `.codex/`, etc.)
- Sintaxis de slash commands específicos
- Cómo se invocan extensions/tools

---

## Entry point universal

Cualquier agente IA que arranque en este repo debería leer en este orden:

1. **`AGENTS.md`** ← reglas universales (contrato cross-LLM)
2. **`architecture/README.md`** ← Niveles 1-5 del Departamento
3. **`auditoria/sesion-activa.md`** ← qué pasó en última sesión
4. **`SIGUIENTE-SESION.md`** ← plan inmediato
5. **Este archivo** ← cómo me integro yo

Cada agente tiene además un **archivo helper específico** (opcional pero útil):
- Claude Code: `CLAUDE.md`
- Cursor: `.cursorrules` (cuando se cree)
- Codex CLI: usa `AGENTS.md` directamente (estándar)
- Gemini CLI: `.gemini/instructions.md` (cuando se cree)

---

## Integración por agente

### Claude Code (Anthropic CLI) — ✅ Primary actual

**Archivos esperados**:
- `CLAUDE.md` (entry point Claude)
- `AGENTS.md` (reglas universales)
- `.claude/skills/` (skills format Anthropic)
- `.claude/agents/` (subagents format Anthropic)
- `.gga` (config Gentleman Guardian Angel)

**Cómo arrancar**:
```powershell
cd C:\DEPARTAMENTO-SOFTWARE
claude  # abre Claude Code CLI
```

Decir al Claude:
> *"Leé CLAUDE.md, AGENTS.md, auditoria/sesion-activa.md y SIGUIENTE-SESION.md.
> Diagnóstico estándar y arrancamos lo que corresponda."*

**Estado**: ✅ Validado en Sprint 1 + Sprint 2.

---

### Cursor — ⏳ Pendiente validación

**Archivos esperados** (cuando se adapte):
- `.cursorrules` (entry point Cursor)
- `AGENTS.md` (reglas universales)
- `.cursor/rules/` (skills format Cursor)

**Adaptación necesaria** (cuando aplique):
1. Crear `.cursorrules` apuntando a `AGENTS.md` + `architecture/README.md`
2. Convertir skills de `.claude/skills/` a `.cursor/rules/` (o mantener ambos)
3. Adaptar subagents si aplica

**Estado**: ⏳ NO validado todavía. Probable en Sprint 4+.

---

### Codex CLI (OpenAI) — ⏳ Pendiente validación

**Archivos esperados**:
- `AGENTS.md` (entry point + reglas — estándar OpenAI usa AGENTS.md directamente)
- `.codex/agents/` (skills/subagents format Codex)

**Adaptación necesaria**:
1. AGENTS.md ya existe y es agent-agnostic ✅
2. Convertir skills de `.claude/skills/` a formato `.codex/` (si aplica)
3. Probar MCP integration (Codex adopta MCP)

**Estado**: ⏳ NO validado. Probable más fácil que Cursor (AGENTS.md ya cumple).

---

### Gemini CLI (Google) — ⏳ Pendiente validación

**Archivos esperados**:
- `.gemini/instructions.md` (entry point Gemini)
- `AGENTS.md` (reglas universales)
- `.gemini/extensions/` (extensions format Gemini)

**Adaptación necesaria**:
1. Crear `.gemini/instructions.md` apuntando a `AGENTS.md`
2. Adaptar skills si aplica
3. Probar MCP integration

**Estado**: ⏳ NO validado. Pendiente.

---

### Antigravity (Google IDE con Gemini 3) — ⏳ Pendiente

Antigravity es el IDE nuevo de Google. Las skills del ecosistema
**sickn33/antigravity-awesome-skills** funcionan nativamente en Antigravity
+ otros agentes.

**Adaptación necesaria**:
- Instalar skills cross-agent: `npx antigravity-awesome-skills --antigravity`
- Configurar entry point según convención Antigravity

**Estado**: ⏳ NO validado.

---

### GPT/ChatGPT web (sin tooling) — ⚠️ Limitado

ChatGPT web **NO tiene filesystem persistente**. Para usarlo con el Departamento:

**Workaround**:
1. Crear un **GPT custom** con `AGENTS.md` + `architecture/PRINCIPIOS-ARQUITECTURA.md` + `architecture/ANTI-PATRONES.md` en su knowledge base
2. Al arrancar sesión, pegar manualmente `auditoria/sesion-activa.md` + `SIGUIENTE-SESION.md`
3. Output del trabajo: copiar manualmente a archivos locales

**Limitaciones**:
- Sin tooling: no puede ejecutar comandos
- Sin filesystem: no puede leer/escribir directamente
- Sin git: vos hacés commits manualmente
- Memoria: depende del contexto window

**Estado**: ⚠️ Funcional para conversaciones arquitectónicas, NO para ejecución.

---

### Claude.ai chat web — ✅ Funcional con limitaciones

Es donde estás escribiendo ahora. Funciona con:
- ✅ MCP filesystem (puede leer/escribir archivos)
- ❌ Sin acceso a Engram (solo Claude Code CLI)
- ❌ Sin slash commands (`/speckit.*` solo en Claude Code)
- ❌ Sin GGA (solo se ejecuta en commits desde CLI)
- ✅ Web search + image search

**Mejor para**:
- Decisiones arquitectónicas
- Análisis de ecosistema
- Documentación profunda

**Peor para**:
- Implementación de código real
- Workflow Spec Kit
- Memory persistente vía Engram

---

## Equivalencias de conceptos por agente

| Concepto Departamento | Claude Code | Cursor | Codex CLI | Gemini CLI |
|---|---|---|---|---|
| Entry point inicio | CLAUDE.md | .cursorrules | AGENTS.md | .gemini/instructions.md |
| Skills (procedurales) | .claude/skills/ | .cursor/rules/ | .codex/agents/ | .gemini/extensions/ |
| Subagents | .claude/agents/ | Cursor Composer agents | Codex subagents | (n/a o equivalente) |
| Slash commands | `/speckit.*` | `/cursor.*` | `/codex.*` | `/gemini.*` |
| MCP tools | ✅ nativo | ✅ adoptando | ✅ adoptando | ✅ adoptando |
| Pre-commit code review | GGA (provider: claude) | GGA (provider: openai) | GGA (provider: openai) | GGA (provider: gemini) |

---

## Cómo migrar de un agente a otro

Si en algún momento decidís cambiar de Claude Code a otro agente, el proceso es:

### Paso 1: NO tocar Niveles 1-2-4-5 del Departamento

Lo siguiente NO cambia:
- `architecture/` completo
- `decisions/` completo
- `projects/<slug>/domain-captures/`
- `auditoria/`
- `templates/project-skeleton/`

### Paso 2: Adaptar Nivel 3 (tooling)

Por cada componente Claude-specific, crear equivalente para el nuevo agente:

```
.claude/skills/ → .new-agent/equivalent/
.claude/agents/ → .new-agent/agents/
CLAUDE.md → .new-agent/instructions.md (o equivalente)
```

### Paso 3: Configurar GGA con nuevo provider

```bash
# Editar .gga config:
Provider: openai  # o gemini, o el que sea
```

### Paso 4: Probar workflow end-to-end

Hacer un feature pequeño con el nuevo agente. Documentar fricciones en
`auditoria/sesion-activa.md` y/o nueva entrada en `CUADERNO-BITACORA.md`.

### Paso 5: Decidir formalmente con ADR

Si la migración fue exitosa, ADR-NNN documenta:
- Cambio de Claude a [nuevo agente]
- Razón
- Configuración nueva
- Aprendizajes

---

## Spec Kit como puente cross-LLM

**GitHub Spec Kit** soporta **30+ integraciones** oficialmente:
Claude Code, Cursor, Codex CLI, Copilot, Gemini CLI, Windsurf, Antigravity,
Kiro, OpenCode, Forge, y más.

Si adoptás Spec Kit como workflow operativo (pendiente decisión T1-T2):

**Beneficio cross-LLM automático**:
- Slash commands `/speckit.*` funcionan en cualquier agente soportado
- Skills mode genera skills en formato del agente activo
- Constitution único alimenta a cualquier agente
- Extensions de Spec Kit funcionan cross-agent

**Esto reduce el trabajo cross-LLM del Departamento en ~60%.**

Decisión sobre adopción Spec Kit: ver ADR-008 (futura validación empírica).

---

## Hipótesis a validar (Sprint 3+)

1. **¿El Departamento funciona end-to-end con Cursor?**
   - Probar: crear feature Stallen pequeño con Cursor en lugar de Claude Code
   - Métricas: ¿qué falló? ¿qué hubo que adaptar? ¿valió la pena?

2. **¿Las skills propias del Departamento son portables?**
   - Probar: ejecutar `sigma-capture-domain` con Cursor
   - Adaptar si necesario

3. **¿La calibración Tier 1 vibe coder funciona con OTROS agentes?**
   - Algunos agentes son más agresivos (Codex), otros más cautos (Claude)
   - ¿La calibración requiere ajustes por agente?

Estas hipótesis se validan empíricamente cuando vos quieras probar otro agente.
No hay urgencia.

---

## Recursos externos cross-LLM

- **Spec Kit (GitHub oficial)**: https://github.com/github/spec-kit (30+ integraciones)
- **Antigravity Awesome Skills**: https://github.com/sickn33/antigravity-awesome-skills (1,460+ skills cross-agent)
- **VoltAgent subagents**: https://github.com/VoltAgent/awesome-claude-code-subagents (portables)
- **MCP servers**: https://github.com/modelcontextprotocol/servers (estándar)
- **AGENTS.md spec**: estándar emergente cross-LLM (varios repos lo usan)

---

## Versionado

- v1.0 (2026-05-15) — INICIAL. Post ADR-008. Documenta integración con 5 agentes
  conocidos. Pendiente validación empírica con otros agentes (Sprint 3+).
