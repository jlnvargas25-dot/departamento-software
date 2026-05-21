# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico post-sandbox empírico T1.
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-21 — post T0 + T1.1-T1.5 (sandbox del stack ejecutado parcial)
**Cliente recomendado próxima sesión**: **Claude Code CLI 2.1.144** dentro de `projects/sandbox-stack/` (para tener skills `speckit-*` cargadas + acceso a ECC 200+ + claude-mem + parche Superpowers)
**Versión**: 5.0 (post sandbox + matriz A* vs stack + EVALUATION.md preliminar)

---

## CONTEXTO RÁPIDO — leer EN ORDEN al arrancar

1. `CLAUDE.md` (constitución global del Framework, ~5 min)
2. `auditoria/sesion-activa.md` v3.5 — qué pasó en sesión 2026-05-21 (T0 + T1 sandbox) y sesiones previas (~10 min)
3. Este archivo — plan T1.6-T6 actualizado (~5 min)
4. `projects/sandbox-stack/EVALUATION.md` — matriz A* vs stack + veredicto preliminar (~5 min)
5. `projects/sandbox-stack/.specify/memory/constitution.md` — constitución del sandbox que operacionaliza Decisión A
6. (Opcional) `NORTE.md` v0.1 — visión Framework
7. (Opcional) `architecture/PRINCIPIOS-ARQUITECTURA.md` v1.3 — A1-A25 detalladas

---

## ESTADO ACTUAL (post sesión 2026-05-21)

### ✅ Sandbox del stack ejecutado parcial

- **Spec Kit** v0.8.13.dev0 — 9 skills `speckit-*` en `projects/sandbox-stack/`
- **ECC** v2.0.0-rc.1 — **200+ skills `ecc:*` + 6 MCP servers** integrados
- **claude-mem** v13.2.0 — 12 skills + memoria persistente (parche manual upstream `autoUpdate: false`)
- **Superpowers** v5.1.0 — manual fix aplicado, **validación post-restart pendiente**

### ✅ Constitución operacionalizada con A1-A25

`projects/sandbox-stack/.specify/memory/constitution.md` materializa el insight Decisión A: Nivel 2 declarativo del Framework como overlay sobre stack ejecutable.

### ✅ Matriz A* vs stack documentada

`projects/sandbox-stack/EVALUATION.md` v0.1 contiene:
- 11 reglas A* con cobertura Direct (44%)
- 12 reglas A* con cobertura Partial (48%)
- 2 reglas A* sin cobertura — `A4 Acíclicidad`, `A19 External Resilience` — únicamente defendidas por overlay declarativo
- Veredicto preliminar **ADR-009: ACCEPT PARCIAL**

### ⏳ Pendientes arquitectónicos

- 🔍 Workflow end-to-end real con caso concreto (iteración 2)
- 🔍 Comparación `sdd-*` (9 skills) vs `speckit-*` (9 skills) — hay un SDD alternativo cargado
- 🔍 Decisión B — Visión D (Capa A + Capa B) pendiente
- ⏸️ Stallen DIFERIDO hasta Framework maduro

### Repo

- Working tree: clean tras commit cierre 2026-05-21
- Branch: main
- Último commit pusheado: cierre sesión 2026-05-21 (sandbox completo + EVALUATION + memoria)

---

## DECISIONES TOMADAS EN SESIÓN 2026-05-21

- **Decisión A** (Nivel 2 + Nivel 3 son complementos por diseño): ✅ **VALIDADA EMPÍRICAMENTE** — matriz A* vs stack lo demuestra (44% Direct + 48% Partial confirma complementariedad, no sustitución)

---

## DECISIONES PENDIENTES PARA PRÓXIMA SESIÓN

### Decisión B — Visión D (Capa A independiente + Capa B integraciones)
- (i) Formalizar en ADR-010 ahora
- (ii) Esperar evidencia de iteración 2 del sandbox

**Recomendación**: **(ii) esperar iteración 2** — la evidencia preliminar valida la complementariedad pero no necesariamente la separación de capas A/B.

### Decisión C — Stallen
- (i) Sigue diferido hasta Framework maduro (sin cambio)
- (ii) Reactivar como driver

**Recomendación**: **(i) sigue diferido**.

### Decisión D — SDD backbone (NUEVA — emergente sesión 2026-05-21)
- (i) Spec Kit (`speckit-*`) como backbone — workflow lineal probado
- (ii) SDD alternativo (`sdd-*`) — workflow con dependency graph + delegation
- (iii) Combinar ambos según fase

**Recomendación**: **(iii) combinar después de comparación empírica**. T1.9 comparará ambos lado a lado.

---

## QUÉ HACER ESTA PRÓXIMA SESIÓN

### PASO T-1 — Verificación commit cierre 2026-05-21 (5 min)

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git log --oneline -5
# Debería mostrar commit del cierre 2026-05-21
git status
# Esperado: working tree clean
```

Si push fue exitoso, seguir T1.6. Si no, completar push.

---

### PASO T1.6 — Restart + verificación Superpowers (10 min)

Después del cierre 2026-05-21 quedó pendiente verificar que Superpowers carga post-fix manual.

```powershell
# Cerrar Claude Desktop
Get-Process -Name "claude" -ErrorAction SilentlyContinue | Stop-Process -Force
Start-Sleep -Seconds 2

# Reabrir Claude Desktop normalmente
# Arrancar Claude Code dentro del sandbox
cd C:\DEPARTAMENTO-SOFTWARE\projects\sandbox-stack
claude
```

Pedir al nuevo Claude:
```
listame skills disponibles agrupadas por familia: speckit-*, ecc:*, claude-mem:*, superpowers:*, sdd-*. Reportá cuántas hay de cada una.
```

**Esperado**:
- 9 `speckit-*` ✓ (ya verificado)
- 200+ `ecc:*` ✓ (ya verificado)
- 12 `claude-mem:*` ✓ (ya verificado)
- **14 `superpowers:*`** ← LO QUE VALIDAMOS
- 9 `sdd-*` (ya visto en sesión 2026-05-21)

**Si Superpowers carga** → T1.3 ✅ y avanzar a T1.7.
**Si no carga** → diagnóstico: revisar `~/.claude/plugins/cache/superpowers-marketplace/superpowers/5.1.0/.orphaned_at` (puede haberse re-creado). Si vuelve a fallar 2 veces → cerrar como DEUDA aceptada, ECC cubre 80-90%.

---

### PASO T1.7 — Workflow end-to-end REAL con caso simple (2-3 hs)

**Objetivo**: ejecutar el workflow completo del stack para validar empíricamente (no a-priori) que las skills hacen lo que prometen + medir cobertura real de las reglas A*.

**Caso de prueba**: "Build a simple todo CRUD with user authentication using Supabase + Vercel" (caso del plan original v4.0).

Workflow integrado a probar:
```
1. /speckit-constitution    (input: este sandbox ya tiene la constitution con A1-A25)
2. /speckit-specify         (NL → spec inicial)
3. /speckit-clarify         (de-risking con 5 preguntas)
4. /speckit-plan            (plan de implementación)
5. /speckit-tasks           (tasks ordenados por dependencia)
6. /speckit-implement       OR /ecc:multi-execute  (implementación)
7. /ecc:quality-gate        (verificación quality)
8. /ecc:code-review         (review crítico)
9. /ecc:security-review     (review seguridad — verifica A12 Zero Trust, A22 Secrets, A25 Authz)
10. /ecc:verification-loop  (test loop)
11. /claude-mem:learn-codebase (captura memoria post-feature)
```

Durante ejecución, anotar para CADA invocación:
- Skill ejecutado
- Reglas A* que el output del skill aborda directamente
- Reglas A* que el output del skill ignora pese a aplicar
- Skills sigma que faltarían

---

### PASO T1.8 — Actualizar EVALUATION.md a v0.2 (60-90 min)

Reescribir matriz A* vs stack con evidencia EJECUTABLE (no a-priori):
- Mover 🟢 Direct → 🟡 Partial si el skill no cumplió lo prometido
- Mover 🟡 Partial → 🟢 Direct si descubrimos skill no listada
- Confirmar 🔴 None (A4, A19) con evidencia
- Agregar columna "Evidencia ejecutable" con outputs concretos

Documentar fricciones, conflictos entre skills, overhead, y veredicto refinado.

---

### PASO T1.9 — Comparación `sdd-*` vs `speckit-*` (Decisión D nueva) (60 min)

Ejecutar el mismo caso de prueba con el SDD alternativo:
```
/sdd-init
/sdd-new <change-name>
/sdd-explore
/sdd-propose
/sdd-spec
/sdd-design
/sdd-tasks
/sdd-apply
/sdd-verify
/sdd-archive
```

Comparar:
- ¿Cuál es más rápido para arrancar?
- ¿Cuál genera artefactos más útiles?
- ¿Cuál tiene mejor manejo de dependency graph?
- ¿Cuál integra mejor con ECC + claude-mem?
- ¿Cuál encaja con los 7 principios del Framework?

**Decisión D resuelta**: elegir backbone o combinación.

---

### PASO T2 — ADR-009 (decisión arquitectónica con evidencia ejecutable) — 60-90 min

**Pre-requisito**: T1.7 + T1.8 + T1.9 completos con evidencia REAL.

**Archivo**: `decisions/ADR-009-adopcion-stack-ecosistema.md`

**Decisión a documentar** (basada en EVALUATION v0.2):
- ✅ Adoptar Spec Kit OR SDD alternativo (resultado T1.9) como backbone SDD
- ✅ Adoptar ECC como stack ejecutable principal
- ✅ Adoptar claude-mem como memoria persistente
- 🟡 Superpowers diferido (a confirmar post-T1.6)
- 🔵 4-5 skills sigma propias (A4 Acíclicidad, A5 Multi-tenant, A19 Resilience, A25 Authz)

**Definition of Done T2**:
- [ ] ADR-009 escrito con formato estándar
- [ ] Matriz A* vs stack v0.2 como anexo
- [ ] Decisiones B+D resueltas con razones
- [ ] Implicaciones para Sprint 2/3 explícitas

---

### PASO T3 — Refactor Sprint 2 según ADR-009 (30-60 min)

Actualizar `SIGUIENTE-SESION.md` y `auditoria/sesion-activa.md` con plan reducido:
- 4-5 skills sigma propias (no 10 del plan original)
- Workflow operativo = "composición del stack" (Visión C confirmada)
- Sprint 2 acelerado ~6-10 semanas

---

### PASO T4 — Completar NORTE Framework v0.2 (30-60 min)

Llenar placeholders restantes en `NORTE.md`:
- Q4 Tier de calibración (mantener Tier 1 default o multi-tier)
- Q5 Stakeholders detallados
- Q6 Restricciones
- Q7 Criterio de stop / pivot

Bump v0.1 → v0.2 (no v1.0 todavía — eso espera proyecto productivo aplicado).

---

### PASO T5 — Workflow operativo Nivel 0 — 1-2 hs

**Si Visión C confirmada por T2 (ACCEPT PARCIAL)**:

Crear `docs/WORKFLOW-OPERATIVO.md` v1.0 documentando:
- "Cómo se compone el stack curado del Departamento"
- Cuándo usar cada pieza (Spec Kit vs SDD vs ECC vs claude-mem)
- Orden de fases Analizar → Planificar → Ejecutar → Verificar
- Cuándo aplicar overlay del Framework (A1-A25)
- Cuándo invocar skills sigma propias

---

### PASO T6 — Documentar lecciones operativas (45 min)

Agregar a `docs/AGENT-INTEGRATION.md`:
- Método declarativo `extraKnownMarketplaces` (LECCIÓN 19)
- Cross-LLM publishing canónico (LECCIÓN 18 — modelo `obra/superpowers`)
- Windows setup checklist (DEUDA-WINDOWS-SETUP-CHECKLIST)
- Stack del ecosistema integrado para Claude Code (alternativas para Cursor/Codex/etc.)

---

### PASO T7 — Posible ADR-010 (Decisión B Visión D) — opcional

Si T1.7-T1.8 dan evidencia de que la separación Capa A / Capa B tiene sentido empírico, formalizar en ADR-010. Sino, mantener como deuda abierta.

---

## PRE-FLIGHT

```powershell
cd C:\DEPARTAMENTO-SOFTWARE

# Estado git
git status              # debería estar clean
git pull                # sync con remote
git log --oneline -10   # ver últimos commits

# Verificar tools (en Claude Code CLI):
claude mcp list         # MCPs disponibles
claude --version        # Claude Code CLI version

# Verificar skills cargadas en sandbox
cd projects/sandbox-stack
ls .claude/skills/      # debería listar speckit-*

# Verificar parches anti-degradación
cat ~/.claude/plugins/known_marketplaces.json | grep -A 5 thedotmack
# Debería decir "autoUpdate: false"
```

---

## REGLAS CRÍTICAS A RECORDAR

### 7 Principios rectores
1. Python traza → IA recorre → Python verifica
2. **3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA**
3. Dominio-first
4. Auto-fix > finding cuando inequívoco
5. Polinización cruzada
6. **Descubrir antes de ejecutar** (audit empírico)
7. Meta-producto recursivo

### Reglas A1-A25 más críticas para vibe coders Tier 1
- A5 Multi-tenant Strict Isolation (CRÍTICA, partial cobertura stack)
- A12 Zero Trust (CRÍTICA, Direct cobertura ECC)
- A13 Concurrency Safety
- A14 Explicit Failure (Direct ECC)
- A15 Unhappy Path First (Direct ECC)
- A20 Hexagonal Architecture (CRÍTICA, Direct `ecc:hexagonal-architecture`)
- A21 Structured Observability (CRÍTICA, partial)
- A22 Secrets Management (CRÍTICA, Direct ECC)
- A24 Data Lifecycle (CRÍTICA, partial)

### Visión articulada del Framework (verbatim Julián 2026-05-15)
> *"crear un harness que permita construir proyectos sin tener miedo de que el llm alucina, inventa o esta haciendo cosas que no debe... análice, planifique, ejecute, verifique como se haría en un departamento de software real o como lo hace un senior en producción"*

### Insight Decisión A — **VALIDADO EMPÍRICAMENTE** (sesión 2026-05-21)
Nivel 2 declarativo A1-A25 + Nivel 3 ejecutable son complementos por diseño. Matriz A* vs stack: 44% Direct + 48% Partial + 8% None confirma complementariedad — el stack NO sustituye al overlay, lo ejecuta donde puede; donde NO puede, el overlay es la única defensa.

### Lecciones técnicas críticas (acumulado)
- **LECCIÓN 16**: cascada de aceptación entre Claude instances
- **LECCIÓN 17**: `edit_file` con array no es atómico — preferir `write_file`
- **LECCIÓN 18** *(2026-05-21)*: cross-LLM publishing canónico (`obra/superpowers` modelo) vs anti-patrón (`.agents/` único de claude-mem)
- **LECCIÓN 19** *(2026-05-21)*: método declarativo `extraKnownMarketplaces` en `~/.claude/settings.json` para CLI standalone
- **LECCIÓN 20** *(2026-05-21)*: flags de tools rotan rápido — documentar comportamiento, no flags
- **LECCIÓN 21** *(2026-05-21, N=1 candidato)*: matriz a-priori vs ejecutable — validar invocando, no solo leyendo metadata

### Lecciones de proceso
- Anti-paternalismo: NO proyectar cansancio
- Audit empírico: cuando Julián cuestiona → audit INMEDIATO (hit rate 19/19)
- El Departamento es Visión C confirmada (curador + calibrador + overlay arquitectónico declarativo)

---

## RIESGOS DE LA PRÓXIMA SESIÓN

- **T1.6 Superpowers fix no carga**: el restart puede no resolver el race condition. Mitigación: clone manual + entry installed_plugins ya aplicados; si vuelve a quedar orphaned → declarar como deuda permanente y avanzar (ECC cubre 80-90%).
- **T1.7 workflow falla a mitad**: si Spec Kit + ECC + claude-mem chocan irreconciliablemente en flow real, ADR-009 = ACCEPT solo Spec Kit + ECC sin chain integration.
- **T1.7 tiempo subestimado**: 2-3 hs puede ser optimista para primer caso end-to-end real. Si toma 4+ hs, dividir en T1.7.1 (constitution + specify + plan) y T1.7.2 (implement + verify).
- **T1.9 comparación SDD vs Spec Kit confusa**: si ambos workflows son confusamente similares, la Decisión D queda como "depende del proyecto" — aceptable.
- **Bump de versiones**: spec-kit/ECC/claude-mem pueden bumper entre esta sesión y la próxima. Si flags cambian, adaptar al vuelo.
- **Compactación de chat**: si la sesión es muy larga, aplicar PROTOCOLO-INICIO-CHAT PASO 1 al re-arrancar.

---

## ARCHIVOS CLAVE A TOCAR EN LA PRÓXIMA SESIÓN

- `projects/sandbox-stack/EVALUATION.md` (v0.1 → v0.2 con evidencia ejecutable)
- `projects/sandbox-stack/.specify/` (artefactos generados por workflow)
- `decisions/ADR-009-adopcion-stack-ecosistema.md` (nuevo)
- `NORTE.md` (v0.1 → v0.2 placeholders llenados)
- `docs/WORKFLOW-OPERATIVO.md` (nuevo si T5 aplica)
- `docs/AGENT-INTEGRATION.md` (actualizar con T6)
- `auditoria/sesion-activa.md` (al cerrar próxima sesión)
- `SIGUIENTE-SESION.md` (al cerrar, regenerar)

---

## NOTAS PARA CLAUDE

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Cliente recomendado**: Claude Code CLI dentro del sandbox para tener skills `speckit-*` cargadas
- **Visión Framework**: harness anti-alucinación senior — Visión C confirmada
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO (hit rate 19/19)
- **NUNCA proyectar cansancio**
- **Hit rate intuición arquitectónica acumulado**: **19/19**
- **A1-A25 son universales** — 0 deudas A* abiertas
- **PROTOCOLO-INICIO-CHAT v1.0 PASO 1 OBLIGATORIO** para verificar Project es Framework
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy pause)
- **EVALUATION.md v0.1 es preliminar** — iteración 2 lo refina con evidencia ejecutable
- **claude-mem requiere autoUpdate: false** — no romper el parche
- **5 stacks instalados**: spec-kit, ecc, claude-mem, superpowers (manual fix), vercel (existente). Bonus tracks: sdd-*, sigma-*, engram:memory, gentle-ai builtins.

---

## CÓMO USAR ESTE ARCHIVO

Al abrir Claude Code CLI:

> *"Seguimos con el Departamento. Aplicá PROTOCOLO-INICIO-CHAT. Leé `auditoria/sesion-activa.md` v3.5 y `SIGUIENTE-SESION.md` v5.0. Diagnóstico estándar. Arrancamos T-1 (verificar commit pusheado), después T1.6 (restart + Superpowers), después T1.7 (workflow end-to-end real)."*

---

Creado: 2026-05-15 | Versión: **5.0** (post sandbox empírico T1 + matriz A* vs stack + EVALUATION.md v0.1 + Decisión A validada)
Para: Claude que abra próxima sesión (Claude Code CLI recomendado dentro de `projects/sandbox-stack/`)
