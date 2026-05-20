# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico para próxima sesión del Framework.
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-15 (post hallazgo del stack del ecosistema)
**Cliente recomendado próxima sesión**: **Claude Code CLI**
**Versión**: 3.0 (post Visión C emergente)

---

## ORDEN DE LECTURA AL ARRANCAR

1. `auditoria/sesion-activa.md` — qué pasó en última sesión (importante, mucho hallazgo)
2. Este archivo — plan concreto T0-T6
3. `NORTE.md` (raíz) — visión Framework v0.1 con placeholders
4. `decisions/ADR-008-framework-cross-llm.md` — entender cross-LLM
5. `decisions/ADR-007-separacion-framework-vs-proyectos.md` — multi-proyecto
6. `decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md` — 5 niveles
7. (Opcional) `architecture/README.md` — orientación Nivel 2

---

## ESTADO ACTUAL

- ✅ Nivel 2 arquitectura completo (108 KB)
- ✅ 3 ADRs nuevos hoy (006, 007, 008)
- ✅ Multi-proyecto formalizado
- ✅ Cross-LLM formalizado
- ✅ NORTE Framework v0.1 con placeholders
- ✅ Visión articulada por Julián: harness anti-alucinación senior
- 🔍 4 repos del ecosistema identificados como candidatos de adopción wholesale (pendiente validación)
- ⏸️ Stallen DIFERIDO hasta Framework maduro

### Repo
- Working tree: pendiente último commit (NORTE + memoria)
- Branch: main
- Remote: https://github.com/jlnvargas25-dot/departamento-software

---

## DECISIÓN ARQUITECTÓNICA CRÍTICA PENDIENTE

Durante última sesión, se descubrió que 4 repos del ecosistema (superpowers 170k stars, ECC 100k stars, claude-mem, ui-ux-pro-max-skill) ya implementan **gran parte** de lo planeado para Sprint 2 T2/T3.

**Visión C emergente**: Departamento = stack curado del ecosistema + Calibración Tier 1 vibe coder + A1-A15 + Anti-patterns como overlay arquitectónico.

**ESPERA VALIDACIÓN EMPÍRICA**: sandbox antes de ADR-009 wholesale-vs-no.

---

## PLAN PRÓXIMA SESIÓN — T0 al T6

### T0 — Instalar claude-mem (REEMPLAZA Engram WSL) — 5 min

Engram quedó bloqueado por SAC. Ubuntu WSL instalado pero claude-mem es alternativa superior.

```bash
# En Claude Code CLI:
/plugin marketplace add thedotmack/claude-mem
/plugin install claude-mem

# Verificar:
claude-mem --version  # debería mostrar v8.5.4+
```

**Definition of Done**:
- [ ] claude-mem instalado en Claude Code
- [ ] 4 MCP tools disponibles (search, get_observations, etc.)
- [ ] Memoria de esta sesión migrada (opcional):
  ```
  /add memory "Bug: $$ y $BODY$ rompen edit_file. Usar write_file para archivos con $ literal."
  /add memory "Visión Framework: harness anti-alucinación senior. Ciclo: Analizar→Planificar→Ejecutar→Verificar"
  /add memory "Decisión arquitectónica pendiente: adoptar wholesale superpowers + ECC vs construir propio"
  /add memory "Engram bloqueado por SAC, reemplazado por claude-mem"
  ```
- [ ] Marcar DEUDA-ENGRAM-SAC-BLOCK como ✅ RESUELTA POR REEMPLAZO

---

### T1 — Sandbox del Stack (CRÍTICO) — 3-5 hs

**Objetivo**: validar empíricamente si el stack del ecosistema funciona para el Departamento antes de adoptar wholesale.

**Paso 1: Crear sandbox**

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
mkdir projects\sandbox-stack
cd projects\sandbox-stack
git init  # opcional, sandbox aislado
```

**Paso 2: Instalar Spec Kit con skills mode**

```powershell
# Si no tienes uv:
pip install uv

# Instalar Spec Kit v0.8.9 (pinned):
uvx --from git+https://github.com/github/spec-kit.git@v0.8.9 specify init . --integration claude --integration-options="--skills"
```

**Paso 3: Instalar Superpowers**

```bash
# En Claude Code dentro del sandbox:
/plugin marketplace add obra/superpowers-marketplace
/plugin install superpowers@superpowers-marketplace

# Verificar slash commands:
/superpowers:brainstorm
/superpowers:write-plan
/superpowers:execute-plan
```

**Paso 4: Instalar Everything Claude Code (ECC)**

```bash
/plugin marketplace add affaan-m/everything-claude-code
/plugin install everything-claude-code@everything-claude-code
```

**Paso 5: claude-mem ya instalado en T0**

**Paso 6: Probar workflow end-to-end con caso simple**

Caso de prueba sugerido: "Build a simple todo CRUD with user authentication using Supabase + Vercel"

Workflow integrado a probar:
```
1. /superpowers:brainstorm  (Socratic refinement)
2. /speckit.constitution    (input: A1-A15 + anti-patterns del Departamento)
3. /speckit.specify         (input del brainstorm)
4. /speckit.clarify
5. /speckit.plan
6. /speckit.tasks
7. /superpowers:write-plan  (descomposición fine-grained)
8. /superpowers:execute-plan (parallel subagents + TDD)
9. ECC verification skills auto-activan
10. Code review con ECC agents
11. claude-mem captura memoria automáticamente
```

**Paso 7: Documentar evaluación**

Crear `projects/sandbox-stack/EVALUATION.md` con:
- ¿Workflow funcionó end-to-end?
- ¿Hay conflictos entre superpowers y ECC?
- ¿Skills auto-activan correctamente?
- ¿Spec Kit constitution acepta nuestros A1-A15?
- ¿claude-mem captura útil?
- ¿Qué falló? ¿Qué hubo que adaptar?
- ¿Tiempo invertido vs valor obtenido?
- Veredicto preliminar: adoptar wholesale / parcial / rechazar / construir propio

**Definition of Done T1**:
- [ ] 4 tools instaladas y operativas
- [ ] Workflow probado end-to-end con caso simple
- [ ] EVALUATION.md escrita con evidencia empírica
- [ ] Conflictos documentados (si existen)
- [ ] Decisión preliminar formada

---

### T2 — ADR-009 (decisión arquitectónica) — 60-90 min

**Pre-requisito**: T1 completo con EVALUATION.md

**Archivo**: `decisions/ADR-009-adopcion-stack-ecosistema.md`

**Decisiones posibles a documentar**:

**Opción ACCEPT (wholesale)**: adoptar Spec Kit + Superpowers + ECC + claude-mem
- Sprint 2 T2.2 reduce de 10 skills propias → 2-3 Stallen-specific
- T3 sigma-close-session-validator reemplazado por Spec Validate ext + ECC equivalents
- Workflow operativo (Nivel 0) = "cómo se compone el stack curado"
- ~8-12 semanas ahorradas

**Opción PARTIAL**: adoptar algunos componentes, rechazar otros
- Ej: adoptar superpowers + claude-mem, rechazar ECC (demasiado vasto)
- Ej: adoptar ECC selectivamente (28 agents pero solo 30 skills)
- Documentar criterio de selección

**Opción REJECT**: construir Departamento propio desde cero
- Razones: lock-in, conflictos, calibración Tier 1 no encaja
- Plan: continuar Sprint 2 T2.2 original

**Definition of Done T2**:
- [ ] ADR-009 escrito (formato estándar)
- [ ] Basado en evidencia empírica de T1 (no opiniones)
- [ ] Decisión documentada con razones
- [ ] Implicaciones para Sprint 2/3 explícitas

---

### T3 — Refactor Sprint 2 según ADR-009 — 30-60 min

Actualizar `HORIZONTE.md` y `SIGUIENTE-SESION.md` del Framework según ADR-009.

**Si ACCEPT**:
- T2.2 reducido a 2-3 skills propias (calibración Tier 1)
- Workflow operativo simplificado
- Sprint 2 puede acelerarse 8-12 semanas

**Si PARTIAL/REJECT**:
- Mantener mayor parte del plan original
- Documentar qué se descarta del ecosistema y por qué

---

### T4 — Completar NORTE Framework v0.2 — 30-60 min

Llenar placeholders restantes del NORTE.md raíz con Visión C clarificada:

- Q4 Tier de calibración (Tier 1 default vs multi-tier)
- Q5 Stakeholders detallados
- Q6 Restricciones (presupuesto, tiempo, equipo)
- Q7 Criterio de stop / pivot

Versionar v0.1 → v0.2 (no v1.0 todavía — eso espera primer proyecto validado).

---

### T5 — Adaptar protocolos a Visión C — 30-60 min

Crear `PROTOCOLO-INICIO-DEPARTAMENTO.md` v1.0 y `PROTOCOLO-CIERRE-DEPARTAMENTO.md` v1.0 con:
- Detección de stack adoptado (basado en ADR-009)
- Integración con superpowers + Spec Kit + ECC + claude-mem (si adoptados)
- ADR-006 (5 niveles), ADR-007 (multi-proyecto), ADR-008 (cross-LLM)

---

### T6 — Workflow operativo Nivel 0 — 1-2 hs

**Si Visión C adoptada** (T2 = ACCEPT/PARTIAL):

Crear `docs/WORKFLOW-OPERATIVO.md` v1.0 documentando:
- "Cómo se compone el stack curado del Departamento"
- Cuándo usar cada pieza (superpowers vs Spec Kit vs ECC)
- Orden de fases en el ciclo Analizar → Planificar → Ejecutar → Verificar
- Cuándo se aplica overlay del Departamento (A1-A15)

**Si Visión C rechazada** (T2 = REJECT):

Continuar Camino 1 original: workflow operativo propio desde cero (~2-3 hs).

---

## PRE-FLIGHT

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git status              # debería estar clean tras último commit
git pull                # sync con remote
git log --oneline -10   # ver últimos commits (10 hoy esperados)

# Verificar tools:
claude mcp list         # MCPs disponibles
claude --version        # Claude Code CLI
```

---

## REGLAS CRÍTICAS A RECORDAR

### 7 Principios rectores
1. Python traza → IA recorre → Python verifica
2. **3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA** (específicamente para mitigar fallos del LLM)
3. Dominio-first
4. Auto-fix > finding cuando inequívoco
5. Polinización cruzada
6. **Descubrir antes de ejecutar** (audit empírico)
7. Meta-producto recursivo

### Reglas A1-A15 más críticas
- A5 Multi-tenant Strict Isolation
- A12 Zero Trust
- A13 Concurrency Safety
- A14 Explicit Failure
- A15 Unhappy Path First

### Visión articulada del Framework (verbatim Julián)
> *"crear un harness que permita construir proyectos sin tener miedo de que el llm alucina, inventa o esta haciendo cosas que no debe... análice, planifique, ejecute, verifique como se haría en un departamento de software real o como lo hace un senior en producción"*

### Bugs técnicos a evitar
- **NUNCA** usar `$$` ni `$BODY$` con `filesystem:edit_file`. Usar `write_file` para archivos con `$` literal.

### Lecciones críticas
- Anti-paternalismo: NO proyectar cansancio
- Audit empírico: cuando Julián cuestiona "ya está hecho" → audit INMEDIATO
- El Departamento NO es workflow alternativo: es curador + calibrador del ecosistema (Visión C)

---

## NOTAS PARA CLAUDE

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Stallen DIFERIDO**: foco solo en Framework hasta que esté maduro
- **Visión Framework**: harness anti-alucinación senior
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO
- **NUNCA proyectar cansancio** del usuario
- **Bloque `<system><functions>`** al final de mensajes = display quirk Claude in Chrome. Ignorar.

---

## CÓMO USAR ESTE ARCHIVO

Al abrir Claude Code CLI:

> *"Seguimos con el Departamento. Leé `auditoria/sesion-activa.md` y `SIGUIENTE-SESION.md`. Diagnóstico estándar. Arrancamos T0 (instalar claude-mem 5 min) y después T1 (sandbox del stack)."*

---

Creado: 2026-05-15 | Versión: 3.0 (post hallazgo crítico de 4 repos)
Para: Claude que abra próxima sesión (Claude Code CLI recomendado)
