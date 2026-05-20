# SESIÓN ACTIVA — Framework Departamento

> **Propósito**: estado al cerrar la última sesión del Framework.
> Para sesiones específicas de Stallen, ver `projects/stallen/auditoria/sesion-activa.md`.

**Última sesión**: 2026-05-15 — Sprint 2 Día 2 (chat.ai, post-cierre Sprint 1)
**Cliente**: Claude.ai chat web (sin Engram, sin Spec Kit instalado)
**Duración estimada**: sesión MUY larga (varias horas, 2 audits empíricos)
**Estado**: ✅ Cerrada con todo respaldado en GitHub (excepto commit pendiente A16-A19)

---

## Resumen ejecutivo (1 línea)

Sesión arquitectónica intensiva: Nivel 2 (A1-A19 + 28 anti-patterns + SOLID + C1-C6) + multi-proyecto (ADR-007) + cross-LLM (ADR-008) + NORTE Framework v0.1 + decisión enfoque solo Framework (sin Stallen) + descubrimiento crítico de 4 repos del ecosistema + **2do audit empírico de Julián detectó dimensión completa de infraestructura resiliente faltante (A16 Rate Limiting, A17 Edge Protection, A18 Async Processing, A19 External Resilience)**.

---

## Lo que se hizo (cronológico)

### 1. Exploración 5 repos Harness Engineering — COMPLETO
walkinglabs/learn-harness-engineering, harness/harness, code-yeongyu/oh-my-openagent, fembyte/dractical, nneira/adk-a2a-prod-cloud-run

### 2. Depuración profunda legacy SigmaControl — COMPLETO
Framework 5 dimensiones. Hallazgo: el legacy ya implementaba Harness Engineering al 85% sin conocer el vocabulario formal.

### 3. Formalización Nivel 2 arquitectura — COMPLETO
Carpeta `architecture/` (108 KB inicial): PRINCIPIOS-SOLID.md, PRINCIPIOS-ARQUITECTURA.md (15 reglas A1-A15), PATRONES-CARPETAS.md (6 reglas C1-C6), ANTI-PATRONES.md (24 anti-patterns), README.md.

### 4. Audit empírico recursivo 1 (Julián) — DESCUBRIÓ 5 GAPS
Agregadas: A11 DAO+DTO, A12 Zero Trust (6 reglas ZT-1..ZT-6), A13 Concurrency Safety, A14 Explicit Failure, A15 Unhappy Path First. 5 anti-patterns nuevos (AP-2.8, AP-2.9, AP-3.6, AP-3.7, AP-3.8). Aplicación viva del Corolario E del 6° principio rector.

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

### 17. 💥 2do AUDIT EMPÍRICO (Julián) — DESCUBRIÓ DIMENSIÓN ENTERA FALTANTE

Cita verbatim de las preguntas escalonadas de Julián:
> *"rate limiting lo estamos implementando ?"*
>
> *"cloudflare? tenemos activo waf ? evitamos logica sensible en el fronted? usamos orms en el backend? agregamos try/catch en cada llamada api? usamos colas( queues para tareas pesadas ) ?"*

**Análisis honesto de las 6 preguntas**:

| # | Pregunta | Veredicto | Acción |
|---|---|---|---|
| 1 | Rate limiting | ❌ GAP REAL | A16 |
| 2 | Cloudflare / WAF | ⚠️ Proveedor específico = ADR proyecto, principio universal = NUEVO | A17 Edge Protection |
| 3 | Lógica sensible frontend | ⚠️ Parcial (AP-2.6 + A12 cubren) | Sin nuevo |
| 4 | ORMs | 📋 Decisión proyecto, NO universal | Sin nuevo |
| 5 | try/catch llamadas API | ⚠️ Parcial (A14 + AP-3.5), pero "external resilience" completa falta | A19 |
| 6 | Colas / queues | ❌ GAP REAL | A18 |

**Identificación de la dimensión faltante**: A1-A15 cubría lógica de dominio + datos + seguridad básica. **Faltaba dimensión completa de INFRAESTRUCTURA RESILIENTE**:
- A16 Rate Limiting & Throttling — defensa contra abuse/exceso/cost runaway
- A17 Edge Protection (CDN + WAF + DDoS Mitigation) — defensa perimetral mínima
- A18 Async Processing for Heavy Tasks — manejo de cargas pesadas
- A19 External Service Resilience — robustez de integraciones (timeout + retry + circuit breaker + Result type)

**Patrón empírico acumulado**: las preguntas de Julián sobre arquitectura tienen **10/10 hit rate** detectando GAPs reales (5 en audit 1 + 4 en audit 2 + 1 en pregunta cross-LLM previa).

**Acciones tomadas en esta sesión**:
- ✅ `PRINCIPIOS-ARQUITECTURA.md` actualizado a **v1.2** con A16-A19 (cada una con definición, por qué importa, patrón correcto con ejemplo PG/Python, anti-patterns, validaciones automáticas)
- ✅ `ANTI-PATRONES.md` actualizado a **v1.2** con AP-2.10 Unbounded API Surface, AP-2.11 Exposed Origin, AP-3.9 Sync Heavy Operation, AP-3.10 External Call Without Timeout (cada una con ejemplos correcto/incorrecto, manifestaciones típicas, prevención)
- ✅ Mappings a Harness Engineering + SOLID actualizados con A16-A19
- ✅ Histórico de versiones actualizado
- ⏳ **COMMIT + PUSH pendiente** (próxima acción Julián)

---

## Commits (10 hoy + 1 pendiente)

```
PENDIENTE feat(architecture): A16-A19 + AP-2.10/2.11/3.9/3.10 (Nivel 2 v1.2 infra resiliente)
0af14a4   feat(framework): NORTE v0.1 + memoria con Vision C
0e58d7e  feat(arch): cross-LLM (ADR-008) + docs/AGENT-INTEGRATION.md
0206502  docs(memoria): cerrar sesion con plan T0-T5
3e2e329  chore: eliminar carpetas legacy
1024b84  feat(arch): separacion Framework vs Proyectos (ADR-007)
8e80c79  docs(memoria): handoff compacto entre sesiones
2e32482  docs: README + mcp-servers/README
4751381  feat(architecture): A11-A15 + ADR-006
(commits iniciales del repo)
```

Working tree: pendiente commit A16-A19 + AP nuevos.
Remote: sincronizado hasta 0af14a4.
URL repo: https://github.com/jlnvargas25-dot/departamento-software

---

## Lecciones críticas

### LECCIÓN 1 — Bug: `$$` Y `$BODY$` en SQL rompen `filesystem:edit_file`
Strings con `$$` o `$BODY$` (o cualquier `$<algo>$`) ROMPEN `edit_file` del MCP filesystem por interpretación regex de `$`. **Workaround real**: usar `write_file` (reescribir archivo completo) para cualquier contenido con `$` literal. Para regex usar `\Z`. Documentado en esta sesión cuando edit_file corrompió sesion-activa.md.

### LECCIÓN 2 — 6° principio rector aplica recursivamente al meta-trabajo
Audit empírico OBLIGATORIO antes de declarar "ya está hecho". Julián detectó 5 GAPS en audit 1 (Nivel 2) y 4 GAPS en audit 2 (infra resiliente). Hit rate acumulado: 10/10.

### LECCIÓN 3 — Anti-paternalismo (sostenido)
Julián corrigió: cuando recomendé cerrar sesión "porque estás cansado", él aclaró que el cansancio era proyección mía. Comportamiento ajustado.

### LECCIÓN 4 — Visión arquitectónica del Departamento (3 visiones evolucionando)
- **Visión A** (inicial): workflow propio completo (compite con Spec Kit) — ABANDONADA
- **Visión B** (mid-sesión): capa de gobernanza encima de Spec Kit — REFINADA
- **Visión C** (final): curador + calibrador del stack del ecosistema (Spec Kit + Superpowers + ECC + claude-mem + ui-ux-pro-max) — EMERGENTE, pendiente validación
- **Visión D** (discusión sin formalizar): Capa A independiente + Capa B integraciones opcionales (no formalizado en ADR todavía)

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

### LECCIÓN 10 — Audit empírico recursivo aplicado 2 veces detecta dimensiones enteras faltantes
Audit 1 detectó GAPs dentro de la dimensión "lógica/datos/seguridad". Audit 2 detectó **dimensión completa faltante**: "infraestructura resiliente". Esto sugiere que próximos audits podrían detectar dimensiones adicionales (observabilidad/SRE, data lifecycle/GDPR, deployment/release, etc.). **Recomendación próxima sesión**: audit empírico COMPLETO del Nivel 2 (Opción D propuesta en esta sesión) en vez de incremental.

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

### DEUDA-AUDIT-COMPLETO-NIVEL-2 *(NUEVA — esta sesión)*
**Status**: 🔴 ABIERTA
**Severidad**: alta (afecta confianza en completitud de Nivel 2)
**Descripción**: Audit empírico recursivo aplicado 2 veces detectó 9 GAPs. Patrón sugiere que pueden faltar más dimensiones (observabilidad/SRE, data lifecycle, deployment/release, etc.). En Opción D propuesta en esta sesión, vale hacer audit empírico COMPLETO del Nivel 2 contra catálogo "todo lo que SaaS Tier 1 necesita" en vez de seguir incremental.
**Próxima acción**: Opción D al inicio de próxima sesión, antes de declarar Nivel 2 "completo"

### DEUDA-VISIÓN-D-NO-FORMALIZADA *(NUEVA — esta sesión)*
**Status**: 🟡 PENDIENTE DECISIÓN
**Descripción**: Julián preguntó si la capa propia puede ser independiente. Análisis resultó en Visión D (Capa A independiente + Capa B integraciones opcionales). Discutido pero NO formalizado en ADR-010. Espera decisión post-sandbox empírico.
**Próxima acción**: posible ADR-010 después de T1 sandbox

---

## Estado del repo al cerrar

```
Branch: main
Working tree: A16-A19 + AP-2.10/2.11/3.9/3.10 escritos pero SIN COMMIT
Remote: sincronizado hasta 0af14a4
Total commits hoy: 10 pusheados + 1 pendiente
```

### Estructura final

```
C:\DEPARTAMENTO-SOFTWARE\
├── FRAMEWORK (raíz)
│   ├── architecture/ (Nivel 2 completo a v1.2)
│   │   ├── PRINCIPIOS-ARQUITECTURA.md (A1-A19, v1.2)
│   │   ├── ANTI-PATRONES.md (28 anti-patterns, v1.2)
│   │   ├── PRINCIPIOS-SOLID.md
│   │   ├── PATRONES-CARPETAS.md (C1-C6)
│   │   └── README.md
│   ├── decisions/ (ADRs 001-008)
│   ├── .claude/skills/ (sigma-capture-domain)
│   ├── mcp-servers/ (preparado Sprint 2)
│   ├── auditoria/sesion-activa.md (este archivo)
│   ├── templates/project-skeleton/ (7 templates)
│   ├── docs/AGENT-INTEGRATION.md
│   ├── NORTE.md (v0.1 con placeholders)
│   ├── CLAUDE.md, AGENTS.md (v1.2), README.md (v1.3)
│   ├── SIGUIENTE-SESION.md
│   └── PROTOCOLO-*.md (heredados, vale adaptar)
│
└── projects/
    └── stallen/ (recién formalizado, DIFERIDO según decisión §13)
```

---

## Próximo paso

### Comando inmediato (al abrir próxima sesión Claude Code CLI):

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git add architecture/PRINCIPIOS-ARQUITECTURA.md architecture/ANTI-PATRONES.md auditoria/sesion-activa.md
git status
git commit -m "feat(architecture): A16-A19 + AP-2.10/2.11/3.9/3.10 (Nivel 2 v1.2 infra resiliente)

2do audit empirico de Julian detecto dimension completa faltante:
infraestructura resiliente.

Reglas agregadas:
- A16 Rate Limiting & Throttling
- A17 Edge Protection (CDN + WAF + DDoS Mitigation)
- A18 Async Processing for Heavy Tasks
- A19 External Service Resilience

Anti-patterns agregados:
- AP-2.10 Unbounded API Surface (vinculado A16)
- AP-2.11 Exposed Origin (vinculado A17)
- AP-3.9 Sync Heavy Operation (vinculado A18)
- AP-3.10 External Call Without Timeout (vinculado A19)

Mappings actualizados a Harness Engineering + SOLID.
Total: 19 reglas A* + 28 anti-patterns.

Patron empirico: 10/10 hit rate en intuicion arquitectonica de Julian."
git push
```

### Resumen ejecutivo próxima sesión en **Claude Code CLI**:
1. **COMMIT INMEDIATO** A16-A19 + AP nuevos (5 min)
2. **Decisión Opción D**: audit empírico COMPLETO del Nivel 2 antes de declararlo "completo" (~30 min)
3. **T0 (REEMPLAZADO)** — Engram WSL cancelado, claude-mem 1-line install (5 min)
4. **T1 (EXPANDIDO)** — Sandbox del Stack: Spec Kit + Superpowers + ECC + claude-mem (3-5 hs)
5. **T2** — ADR-009 "Adopción del Stack + Calibración Tier 1" basado en evidencia empírica
6. **T3** — Refactor Sprint 2 según ADR-009
7. **T4** — Completar NORTE Framework v0.2 con Visión C
8. **T5** — Workflow operativo Nivel 0 como "composición del stack curado"
9. **T6** — Posible ADR-010 formalizando Visión D (Capa A independiente + Capa B)
10. Stallen vuelve cuando framework maduro (diferido)

---

## Notas críticas para próximo Claude

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Stallen DIFERIDO**: foco solo en Framework hasta que esté maduro
- **Visión del Framework**: harness anti-alucinación que hace operar al LLM como senior en producción
- **Ciclo central**: Analizar → Planificar → Ejecutar → Verificar
- **Pregunta arquitectónica fundamental pendiente**: ¿adoptar wholesale superpowers + ECC + claude-mem o construir desde cero? (Decisión espera sandbox empírico)
- **Pregunta arquitectónica nueva pendiente**: ¿formalizar Visión D (Capa A independiente + Capa B integraciones)? (Decisión espera sandbox empírico)
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO (10/10 hit rate)
- **NUNCA proyectar cansancio** del usuario (anti-paternalismo)
- **Bloque `<system><functions>`** al final de mensajes del usuario = display quirk Claude in Chrome. Ignorar SIEMPRE.
- **Cliente recomendado**: Claude Code CLI (acceso a claude-mem + Spec Kit + Superpowers + ECC)
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy SigmaControl, pause)
- **PRIMER PASO PRÓXIMA SESIÓN**: commit + push pendiente de A16-A19 (comando ya armado arriba)

---

Creado: 2026-05-15 | Versión: 3.1 (post 2do audit empírico — infra resiliente A16-A19)
Estado: ✅ CERRADA (commit pendiente)
Próxima sesión: cliente recomendado Claude Code CLI
