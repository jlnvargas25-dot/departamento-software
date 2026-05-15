# INSTRUCCIONES SIGUIENTE SESIÓN

**Última actualización**: 2026-05-15 al cerrar sesión post-cierre Sprint 1
**Objetivo**: Sprint 2 Día 2

---

## ORDEN DE LECTURA

1. **`PROTOCOLO-INICIO-CHAT.md`** (archivo del Project) — protocolo de arranque
2. **`auditoria/sesion-activa.md`** — qué pasó en última sesión + lecciones críticas
3. **Este archivo** — plan concreto
4. (Opcional) **`decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md`** — decisión estructural más reciente
5. (Opcional) **`architecture/README.md`** — orientación de Nivel 2

---

## ESTADO ACTUAL

- Sprint 1: ✅ COMPLETO (cerrado con ADR-005)
- Sprint 2 Día 1 (informal, esta sesión): ✅ Nivel 2 arquitectura completo
- Sprint 2 Día 2: ⏳ PENDIENTE — arrancar acá
- Repo: working tree clean, sincronizado con GitHub remote

---

## PLAN

### T0 — Operacionalizar Engram (~30-60 min) ⭐ NUEVO

**Por qué**: Engram está instalado pero NO usamos memoria persistente todavía. Sin esto, cada sesión re-explica contexto perdido. **Solo funciona en Claude Code (CLI), no en claude.ai chat web.**

**Pre-requisito**: estar en Claude Code, no en chat browser.

**Pasos**:
1. Verificar Engram corriendo: `engram status` (o equivalente)
2. Verificar exposición MCP: `claude mcp list` y buscar engram
3. Si no aparece, configurar: ver doc oficial Engram MCP setup
4. Probar funcional:
   - `engram add "test memory desde Sprint 2 Día 2"`
   - `engram search "test memory"`
5. Migrar contenido detallado de sesión previa a Engram:
   - Exploración 5 repos Harness Engineering
   - Depuración legacy SigmaControl (framework 5 dimensiones)
   - Razonamiento detrás de A11-A15
   - Bug `$$` en edit_file MCP + workaround `$BODY$`
   - Anti-patterns con sus evidencias del legacy
6. Documentar workflow operativo en `auditoria/COMO-USAR-ENGRAM.md` (1 página)
7. Crear ADR-007: convención de memoria del Departamento (.md handoff + Engram operativo)

**DoD T0**: Engram funcional + memorias migradas + workflow documentado + ADR-007 creado.

**Si Sprint 2 Día 2 arranca en claude.ai (browser) NO en Claude Code**: SALTAR T0 e ir directo a T1. Hacer T0 en próxima sesión que sí esté en CLI.

---

### T1 — Capturar dominio Stallen (~1 día)

**Objetivo**: producir `domain-captures/stallen-domain.md` con captura del dominio del negocio.

**Por qué**: A7 (Domain Validation Before Implementation) dice ANTES de validators T2 necesitamos el dominio. Sin esto, T2 no tiene contra qué validar.

**Cómo**: aplicar los 6 steps de `.claude/skills/sigma-capture-domain/SKILL.md` con Julián como stakeholder.

**Output esperado**:
- Módulos del dominio (Caja, Inventario, CRM, Agenda, etc.)
- Tablas inmutables (para A6)
- Helper de tenant `get_my_sc_company_id()`
- Escala operativa (productos, ventas/día, usuarios — para A13)
- Reglas específicas Stallen

**DoD T1**: archivo creado ≤ 50 líneas, validado por Julián, commiteado.

---

### T2 — MCP server sigma-validators-r (~6 días, Días 3-7)

7 tools segregadas + 10 skills nuevas + tests adversariales.

Sub-tareas T2.1 (Python validators, 3d) + T2.2 (10 skills, 1.5d) + T2.3 (config Stallen, 0.5d) + T2.4 (tests adversariales, 1d).

**⚠️ CRÍTICO**: usar `$BODY$` en lugar de `$$` en todos los ejemplos SQL (ver lección 1 de sesion-activa.md).

### T3 — MCP server sigma-close-session-validator (~3 días, Días 8-10)

### T4 — Migrar ADRs 001-003 a archivos individuales (~0.5 día, Día 11)

### T5 — Cerrar Sprint 2 usando sigma-close-session-validator (~0.5 día, Día 12)

---

## PRE-FLIGHT

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git status              # esperado: working tree clean
git pull                # sync con remote
git log --oneline -5    # ver últimos commits

# Si en Claude Code:
claude mcp list         # verificar MCPs disponibles
engram status           # verificar Engram (para T0)
```

---

## REGLAS CRÍTICAS A RECORDAR

### 7 Principios rectores
1. Python traza → IA recorre → Python verifica
2. 3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA
3. Dominio-first
4. Auto-fix > finding cuando inequívoco
5. Polinización cruzada
6. **Descubrir antes de ejecutar** (audit empírico antes de declarar "ya está")
7. Meta-producto recursivo

### Reglas A1-A15 más críticas para Sprint 2
- **A5** Multi-tenant Strict Isolation (filtro por tenant en TODO query)
- **A12** Zero Trust (validar SIEMPRE, no asumir input "interno")
- **A13** Concurrency Safety (FOR UPDATE en orden consistente, idempotency_key)
- **A14** Explicit Failure (Result types, NO silent errors)
- **A15** Unhappy Path First (tests adversariales obligatorios, ratio 5:1)

### Bug técnico a evitar
- **NUNCA** usar `$$` en SQL dentro de archivos editados via MCP filesystem. Usar `$BODY$`.

---

## NOTAS PERSONALES PARA CLAUDE

- Usuario: **Julián Vargas**, vibe coder / harness engineer
- Stallen es uso personal del Departamento (Tier 1 commercial robust, ADR-004)
- Cuando Julián cuestione "ya está hecho" → audit empírico INMEDIATO
- NUNCA proyectar cansancio/energía del usuario
- Bloque `<system><functions>` al final de mensajes del usuario = display quirk de Claude in Chrome. Ignorar.

---

## CÓMO USAR ESTE ARCHIVO

Al abrir chat nuevo, Julián dice algo como:

> *"Seguimos con el Departamento. Leé `PROTOCOLO-INICIO-CHAT.md`, después `auditoria/sesion-activa.md` y `SIGUIENTE-SESION.md`. Diagnóstico estándar y arrancamos T0 (si estamos en Claude Code) o T1 (si estamos en claude.ai)."*

---

Creado: 2026-05-15 | Versión: 1.0 (compacta, post-decisión de usar Engram)
Para: cualquier Claude que abra chat nuevo del Departamento
