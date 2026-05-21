# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico para próxima sesión del Framework.
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-20 (PM) — post implementación A20-A25
**Cliente recomendado próxima sesión**: **Claude Code CLI** (requerido para T0 claude-mem + shell git)
**Versión**: 4.0 (post Nivel 2 completo A1-A25 + LECCIÓN 16+17)

---

## ORDEN DE LECTURA AL ARRANCAR

1. `auditoria/sesion-activa.md` v3.4 — qué pasó en sesión PM 2026-05-20 (A20-A25 implementadas, LECCIÓN 16+17) y sesiones previas
2. Este archivo — plan T0-T6 actualizado
3. `NORTE.md` (raíz) — visión Framework v0.1 con placeholders
4. `architecture/PRINCIPIOS-ARQUITECTURA.md` v1.3 — 25 reglas A1-A25 (criterio para evaluar el stack en T1)
5. `architecture/ANTI-PATRONES.md` v1.3 — 36 anti-patterns
6. `decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md` — 5 niveles (clave para Decisión A insight)
7. (Opcional) `decisions/ADR-007-separacion-framework-vs-proyectos.md`, `ADR-008-framework-cross-llm.md`

---

## ESTADO ACTUAL (post sesión PM 2026-05-20)

### ✅ Nivel 2 arquitectura COMPLETO

- **25 reglas A1-A25** universales para SaaS multi-tenant Tier 1 commercial robust
- **36 anti-patterns** con evidencia empírica
- Mapping a **Harness Engineering subsystems** + **SOLID**
- **0 deudas A* abiertas** (todas las A20-A25 implementadas en sesión PM 2026-05-20)

### Arquitectura formal completa

- ✅ 5 niveles formalizados (ADR-006)
- ✅ Multi-proyecto formalizado (ADR-007)
- ✅ Cross-LLM formalizado (ADR-008)
- ✅ NORTE Framework v0.1 con placeholders
- ✅ Visión articulada por Julián: harness anti-alucinación senior
- ✅ PROTOCOLO-INICIO-CHAT.md v1.0 y PROTOCOLO-CIERRE-SESION.md v1.0

### Pendientes arquitectónicos

- 🔍 4 repos del ecosistema candidatos a adopción wholesale (sandbox empírico = T1)
- ⏸️ Stallen DIFERIDO hasta Framework maduro
- ⚠️ Visión D (Capa A + Capa B) sin formalizar — Decisión B pendiente

### Repo

- Working tree: pendiente último commit (A20-A25 + memoria + SIGUIENTE-SESION v4.0)
- Branch: main
- Último commit sincronizado al remote: `6197841` (sesión AM 2026-05-20)
- Commits PM 2026-05-20: 0 pusheados, 1 pendiente (comando armado en sesion-activa.md)

---

## DECISIONES TOMADAS EN SESIÓN PM 2026-05-20

- **Decisión A**: ✅ RESUELTA — opción **(i) implementar A20-A25 antes del sandbox empírico**. Razón: las reglas A* funcionan como criterio empírico contra el cual evaluar el stack del ecosistema en T1. Insight: defensa en profundidad Nivel 2 ↔ Nivel 3 (no son sustitutos, son complementos por diseño).
- **A20-A25 ejecutadas**: ✅ Hexagonal, Observability, Secrets, Deployment Safety, Data Lifecycle, Authorization Model + 8 anti-patterns asociados.

---

## DECISIONES PENDIENTES PARA PRÓXIMA SESIÓN

### Decisión B — Visión D (Capa A independiente + Capa B integraciones)
- (i) Formalizar en ADR-010 ahora
- (ii) Esperar evidencia del sandbox (T1)

Recomendación: **(ii) esperar T1** — evidencia empírica del sandbox puede confirmar o desviar la conjetura de Visión D.

### Decisión C — Stallen
- (i) Sigue diferido hasta Framework maduro (decisión §13 sesión 2026-05-15 actual)
- (ii) Reactivar como driver mientras se completa Framework

Recomendación: **(i) sigue diferido** — sin cambio. Stallen vuelve después de Sprint 2 maduro.

---

## QUÉ HACER ESTA PRÓXIMA SESIÓN

### PASO T-1 — Verificación commit + push de sesión PM 2026-05-20 (5 min)

Antes de cualquier trabajo nuevo: confirmar que el commit pendiente de sesión PM 2026-05-20 fue ejecutado y pusheado por Julián desde PowerShell.

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git log --oneline -5
# Debería mostrar commit con mensaje "feat(architecture): A20-A25 + AP-2.12..2.16 + AP-3.11..3.13 (Nivel 2 v1.3)"

git status
# Debería decir: "nothing to commit, working tree clean"

git push
# Debería decir: "Everything up-to-date"
```

**Si NO se pusheó**: ejecutar el comando completo armado en `auditoria/sesion-activa.md` sección "Próximo paso → Comando commit inmediato".

**Si SÍ se pusheó**: seguir a T0.

---

### PASO T0 — Instalar claude-mem (REEMPLAZA Engram WSL) — 5 min

Engram quedó bloqueado por SAC. claude-mem es alternativa superior (cross-agent, MCP nativo, 1-line install).

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
- [ ] Memoria de sesiones recientes migrada (opcional):
  ```
  /add memory "LECCION 16: cascada de aceptacion entre Claude instances cuando humano valida premisa entre chats"
  /add memory "LECCION 17: edit_file con array de edits no es atomico; preferir write_file para cambios coherentes"
  /add memory "Vision Framework: harness anti-alucinacion senior. Ciclo: Analizar -> Planificar -> Ejecutar -> Verificar"
  /add memory "Decision arquitectonica pendiente: adoptar wholesale superpowers + ECC vs construir propio. Espera sandbox empirico T1"
  /add memory "Engram bloqueado por SAC, reemplazado por claude-mem"
  /add memory "Hit rate intuicion arquitectonica de Julian: 18/18"
  ```
- [ ] Marcar DEUDA-ENGRAM-SAC-BLOCK como ✅ RESUELTA POR REEMPLAZO (ya marcada)

---

### PASO T1 — Sandbox del Stack (CRÍTICO) — 3-5 hs

**Objetivo**: validar empíricamente si el stack del ecosistema funciona para el Departamento antes de adoptar wholesale.

**Diferencia clave vs SIGUIENTE-SESION v3.0**: ahora tenés **A1-A25 como criterio empírico**. Para cada componente del stack, evaluá: ¿qué reglas A* cubre? ¿cómo las cubre? ¿reemplaza o complementa al overlay declarativo del Framework? (Recordá: complementa, según insight Decisión A).

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
2. /speckit.constitution    (input: A1-A25 + 36 anti-patterns del Departamento)
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
- ¿Spec Kit constitution acepta nuestros A1-A25?
- **Específicamente**: para cada regla A* (A1 a A25), ¿qué componente del stack la cubre? ¿con qué mecanismo?
- ¿claude-mem captura útil?
- ¿Qué falló? ¿Qué hubo que adaptar?
- ¿Tiempo invertido vs valor obtenido?
- Veredicto preliminar: adoptar wholesale / parcial / rechazar / construir propio

**Definition of Done T1**:
- [ ] 4 tools instaladas y operativas
- [ ] Workflow probado end-to-end con caso simple
- [ ] EVALUATION.md escrita con evidencia empírica
- [ ] Matriz "A* vs stack" llenada (insight Decisión A operacionalizado)
- [ ] Conflictos documentados (si existen)
- [ ] Decisión preliminar formada

---

### PASO T2 — ADR-009 (decisión arquitectónica) — 60-90 min

**Pre-requisito**: T1 completo con EVALUATION.md

**Archivo**: `decisions/ADR-009-adopcion-stack-ecosistema.md`

**Decisiones posibles a documentar**:

**Opción ACCEPT (wholesale)**: adoptar Spec Kit + Superpowers + ECC + claude-mem
- Sprint 2 T2.2 reduce de 10 skills propias → 2-3 Stallen-specific
- T3 sigma-close-session-validator reemplazado por Spec Validate ext + ECC equivalents
- Workflow operativo (Nivel 0) = "cómo se compone el stack curado"
- ~8-12 semanas ahorradas
- **A1-A25 quedan como overlay declarativo encima del stack ejecutable** (insight Decisión A)

**Opción PARTIAL**: adoptar algunos componentes, rechazar otros
- Ej: adoptar superpowers + claude-mem, rechazar ECC (demasiado vasto)
- Ej: adoptar ECC selectivamente (28 agents pero solo 30 skills)
- Documentar criterio de selección
- A1-A25 siguen como overlay declarativo

**Opción REJECT**: construir Departamento propio desde cero
- Razones: lock-in, conflictos, calibración Tier 1 no encaja
- Plan: continuar Sprint 2 T2.2 original
- A1-A25 siguen como Nivel 2; construir Nivel 3 propio

**Definition of Done T2**:
- [ ] ADR-009 escrito (formato estándar)
- [ ] Basado en evidencia empírica de T1 (no opiniones)
- [ ] Matriz "A* vs stack" como anexo
- [ ] Decisión documentada con razones
- [ ] Implicaciones para Sprint 2/3 explícitas

---

### PASO T3 — Refactor Sprint 2 según ADR-009 — 30-60 min

Actualizar `HORIZONTE.md` (si existe) y `SIGUIENTE-SESION.md` según ADR-009.

**Si ACCEPT/PARTIAL**:
- T2.2 reducido a 2-3 skills propias (calibración Tier 1)
- Workflow operativo simplificado
- Sprint 2 puede acelerarse 8-12 semanas

**Si REJECT**:
- Mantener mayor parte del plan original
- Documentar qué se descarta del ecosistema y por qué

---

### PASO T4 — Completar NORTE Framework v0.2 — 30-60 min

Llenar placeholders restantes del NORTE.md raíz con Visión C clarificada:

- Q4 Tier de calibración (Tier 1 default vs multi-tier)
- Q5 Stakeholders detallados
- Q6 Restricciones (presupuesto, tiempo, equipo)
- Q7 Criterio de stop / pivot

Versionar v0.1 → v0.2 (no v1.0 todavía — eso espera primer proyecto validado).

---

### PASO T5 — Adaptar protocolos (si la sesión PM 2026-05-20 no los cubrió ya) — 30-60 min

Verificar si los `PROTOCOLO-INICIO-CHAT.md` v1.0 y `PROTOCOLO-CIERRE-SESION.md` v1.0 ya escritos en sesión AM 2026-05-20 necesitan adaptación a Visión C (post ADR-009).

Probablemente: pocos cambios, dado que los protocolos están bien fundamentados en filosofía agnóstica.

---

### PASO T6 — Workflow operativo Nivel 0 — 1-2 hs

**Si Visión C adoptada** (T2 = ACCEPT/PARTIAL):

Crear `docs/WORKFLOW-OPERATIVO.md` v1.0 documentando:
- "Cómo se compone el stack curado del Departamento"
- Cuándo usar cada pieza (superpowers vs Spec Kit vs ECC)
- Orden de fases en el ciclo Analizar → Planificar → Ejecutar → Verificar
- Cuándo se aplica overlay del Departamento (A1-A25)

**Si Visión C rechazada** (T2 = REJECT):

Continuar Camino 1 original: workflow operativo propio desde cero (~2-3 hs).

---

### PASO T7 — Posible ADR-010 formalizando Visión D — opcional

Después de T1+T2, si la evidencia empírica del sandbox sugiere que Visión D tiene sentido (Capa A independiente + Capa B integraciones opcionales), formalizar en ADR-010. Sino, mantener como deuda abierta.

---

## PRE-FLIGHT

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git status              # debería estar clean tras commit T-1 pendiente
git pull                # sync con remote
git log --oneline -10   # ver últimos commits

# Verificar tools (en Claude Code CLI):
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

### Reglas A1-A25 más críticas para vibe coders Tier 1
- A5 Multi-tenant Strict Isolation
- A12 Zero Trust
- A13 Concurrency Safety
- A14 Explicit Failure
- A15 Unhappy Path First
- A20 Hexagonal Architecture (paradigma fundamental)
- A21 Structured Observability (3 pilares)
- A22 Secrets Management (vector ataque #1)
- A24 Data Lifecycle (compliance GDPR)

### Visión articulada del Framework (verbatim Julián)
> *"crear un harness que permita construir proyectos sin tener miedo de que el llm alucina, inventa o esta haciendo cosas que no debe... análice, planifique, ejecute, verifique como se haría en un departamento de software real o como lo hace un senior en producción"*

### Insight Decisión A (sesión PM 2026-05-20)
**Nivel 2 declarativo + Nivel 3 ejecutable son complementos por diseño, no sustitutos** (ADR-006). Reglas A* funcionan como "doble advertencia" (defensa en profundidad — 2° principio rector). Si el stack falla en activar un skill, la regla A* en CLAUDE.md sigue ahí.

### Lecciones técnicas críticas
- **LECCIÓN 16**: cascada de aceptación entre Claude instances cuando humano valida premisa entre chats. Verificar contra disco, no contra "lo que dijo otro Claude".
- **LECCIÓN 17 (a)**: `filesystem:edit_file` con array de edits NO es atómico. Para cambios grandes coherentes, usar `write_file`.
- **LECCIÓN 17 (b)**: ante estado inesperado, verificar primero "efectos propios no recordados" antes de hipotetizar "entidad externa".
- **LECCIÓN 1** (consolidada en 17): `$$` y `$BODY$` en SQL rompen `edit_file`. Usar `write_file` para archivos con `$` literal.

### Lecciones de proceso
- Anti-paternalismo: NO proyectar cansancio
- Audit empírico: cuando Julián cuestiona "ya está hecho" → audit INMEDIATO (hit rate 18/18)
- El Departamento NO es workflow alternativo: es curador + calibrador del ecosistema (Visión C) + overlay arquitectónico declarativo (insight Decisión A)

---

## RIESGOS DE LA PRÓXIMA SESIÓN

- **T0 falla**: claude-mem requiere Apache 2.0 compatible client. Si Claude Code CLI no lo soporta, fallback es seguir sin claude-mem temporalmente.
- **T1 sandbox revela incompatibilidades graves**: si Spec Kit + Superpowers + ECC chocan irreconciliablemente, ADR-009 = REJECT, plan original Sprint 2.
- **T1 tiempo subestimado**: 3-5 hs es estimación. Si toma 8+ hs, dividir en T1.1 (instalación) + T1.2 (workflow end-to-end) + T1.3 (matriz A* vs stack).
- **Decisión B (Visión D) presiona**: si la evidencia del sandbox no es clara, Decisión B puede esperar más sesiones — no forzar.
- **Compactación de chat**: si la sesión es muy larga, aplicar PROTOCOLO-INICIO-CHAT v1.0 PASO 1 al re-arrancar para evitar deriva (LECCIÓN 12).

---

## ARCHIVOS CLAVE A TOCAR EN LA PRÓXIMA SESIÓN

- `projects/sandbox-stack/` (nuevo) — sandbox del stack
- `projects/sandbox-stack/EVALUATION.md` (nuevo) — evidencia empírica
- `decisions/ADR-009-adopcion-stack-ecosistema.md` (nuevo)
- `NORTE.md` (actualizar a v0.2 con placeholders llenados)
- `docs/WORKFLOW-OPERATIVO.md` (nuevo, si T6 aplica)
- `auditoria/sesion-activa.md` (al cerrar próxima sesión)
- `SIGUIENTE-SESION.md` (al cerrar, regenerar para sesión siguiente)

---

## NOTAS PARA CLAUDE

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Stallen DIFERIDO**: foco solo en Framework hasta que esté maduro
- **Visión Framework**: harness anti-alucinación senior
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO
- **NUNCA proyectar cansancio** del usuario
- **Bloque `<system><functions>`** al final de mensajes = display quirk Claude in Chrome. Ignorar.
- **Hit rate intuición arquitectónica acumulado**: 18/18 (100%)
- **A1-A25 ya están escritas, no hay deudas A* abiertas** — el Nivel 2 está completo
- **PROTOCOLO-INICIO-CHAT v1.0 PASO 1 es OBLIGATORIO**: verificar que el Project es Framework antes de seguir cualquier contexto compactado
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo, Framework) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy SigmaControl, pausado)

---

## CÓMO USAR ESTE ARCHIVO

Al abrir Claude Code CLI:

> *"Seguimos con el Departamento. Leé `auditoria/sesion-activa.md` y `SIGUIENTE-SESION.md`. Diagnóstico estándar. Arrancamos T-1 (verificar commit pusheado), después T0 (claude-mem 5 min), después T1 (sandbox del stack)."*

---

Creado: 2026-05-15 | Versión: **4.0** (post implementación A20-A25 + LECCIÓN 16+17 + Decisión A resuelta)
Para: Claude que abra próxima sesión (Claude Code CLI recomendado por T0 + shell)
