# PROTOCOLO DE INICIO — Departamento de Software (Framework)
# Claude lee esto al abrir cualquier chat en el proyecto
# Versión: 1.0 | 2026-05-20

---

## CONTEXTO

Este es el **Framework Departamento de Software** (`C:\DEPARTAMENTO-SOFTWARE\`),
proyecto que destila el meta-producto de SigmaControl como herramienta reutilizable
cross-LLM. El proyecto canónico SigmaControl legacy vive en otro path
(`C:\Users\Windows 11\sigmacontrol-camino-1\`) y **NO se toca desde acá** —
es referencia histórica.

Visión del Framework: **harness anti-alucinación** que sostiene al LLM para
operar como senior en producción. Ciclo central: Analizar → Planificar →
Ejecutar → Verificar.

---

## REGLA #0 — VERIFICAR MCP ANTES DE PROMETER

Antes de prometer contexto al usuario, verificar qué podés leer realmente.

### Test rápido — ¿tenés MCP filesystem activo?

Intentá leer un archivo del disco:
```
filesystem:read_text_file(path="C:\\DEPARTAMENTO-SOFTWARE\\CLAUDE.md")
```

**Si responde con el contenido del archivo** → tenés MCP, seguí con CASO A.
**Si responde que la tool no existe o no se encuentra el archivo** → no tenés MCP, seguí con CASO B.

No presumas. No inventes. Verificá primero.

---

## CASO A — MCP filesystem activo (Claude desktop o Claude in Chrome conectado)

### PASO 1 — Verificar contexto real (no asumir continuidad)

Antes de leer archivos, **verificá el system prompt** del Project actual:
- ¿Apunta al Framework Departamento (`C:\DEPARTAMENTO-SOFTWARE\`)? → seguir
- ¿Apunta a SigmaControl legacy (`C:\Users\Windows 11\sigmacontrol-camino-1\`)? → **PARÁ**.
  Avisá al usuario: estás en un Project de SigmaControl, no de Framework.
  Pregunta cuál es el proyecto vigente antes de seguir.

**Por qué esta verificación**: en 2026-05-20 se detectó manifestación N=31+
del sub-meta-patrón #13.x — una sesión propagó contexto del Framework al
Project de SigmaControl sin verificar. Esta regla previene la recurrencia.

### PASO 2 — Leer estado canónico del disco (en orden)

```
1. Leer CLAUDE.md                              ← constitución + 7 principios (lectura obligatoria)
2. Leer auditoria/sesion-activa.md             ← contexto último cierre
3. Leer SIGUIENTE-SESION.md                    ← plan detallado próxima sesión
4. Leer NORTE.md                               ← propósito + visión harness anti-alucinación
```

`DEPARTAMENTO-DE-SOFTWARE.md` y `SISTEMA-DE-TRABAJO.md` se leen on-demand
cuando la tarea lo requiere, no por default cada sesión.

### PASO 3 — Si necesitás contexto histórico adicional

```
5. Leer architecture/PRINCIPIOS-ARQUITECTURA.md  ← A1-A19 reglas universales + 4 deudas A20-A25
6. Leer architecture/ANTI-PATRONES.md            ← 28 anti-patterns con evidencia empírica
7. Leer decisions/ADR-NNN-titulo.md              ← decisiones específicas (007 multi-proyecto, 008 cross-LLM)
8. Leer docs/AGENT-INTEGRATION.md                ← guías cross-LLM (Cursor, Codex, etc.)
9. Leer projects/<slug>/                         ← proyectos específicos (stallen diferido)
```

### PASO 4 — Diagnóstico estándar al usuario

Formato esperado:
```
FRAMEWORK DEPARTAMENTO DE SOFTWARE — Estado [fecha último cierre]

Proyecto activo: Framework (Stallen DIFERIDO según decisión §13 sesion-activa)
Sprint actual: [de sesion-activa]
Fase: [de SIGUIENTE-SESION]

Nivel 2 arquitectura: [N reglas A* implementadas + M deudas formales]
Decisiones recientes: [ADRs relevantes]

✅ COMPLETADO recientemente → [de sesion-activa §Lo que se hizo]
🔴 PRÓXIMO → [de SIGUIENTE-SESION]
⚠️ DEUDAS ACTIVAS → [resumen tabla de deudas en sesion-activa]
```

El contenido específico cambia sesión a sesión. El formato no.

### PASO 5 — Arrancar la tarea según SIGUIENTE-SESION.md

Antes de ejecutar, verificar con el usuario que el plan declarado sigue
vigente. Aplicación del 6° principio rector: descubrir antes de ejecutar.

---

## CASO B — Sin MCP filesystem (Claude web sin acceso a disco)

### PASO 1 — Avisar al usuario honestamente

```
"Estoy abriendo este chat sin acceso al disco del proyecto (MCP filesystem
no está activo). Puedo orientarte usando la descripción permanente que veo
en este Project, pero el estado actual del Framework puede haber cambiado
desde esta copia.

Tres opciones:
A) Abrís Claude desktop o Claude in Chrome donde tengo acceso completo al disco
B) Me pegás manualmente el contenido de auditoria/sesion-activa.md y
   SIGUIENTE-SESION.md y trabajamos con eso
C) Hablamos de orientación general (filosofía, arquitectura A1-A19, ADRs)
   sin necesitar estado vigente"
```

### PASO 2 — Esperar decisión

No inventar estado. No asumir que los archivos del Project reflejan el
momento actual del disco.

### PASO 3 — Trabajar según decisión

- Si eligió A → no hay nada que hacer en este chat
- Si eligió B → usa el contenido pegado como fuente de verdad
- Si eligió C → usar `CLAUDE.md` como dispatcher para navegar conceptos

---

## REGLA FUNDAMENTAL

**Los archivos del Project son ORIENTACIÓN PERMANENTE, no estado vigente.**

Describen cómo funciona el Framework, no qué acaba de pasar. El estado
vivo vive solo en disco:

- `NORTE.md` → propósito + visión (~1x mes, leer al arrancar hitos grandes)
- `auditoria/sesion-activa.md` → último cierre detallado
- `SIGUIENTE-SESION.md` → plan inmediato
- `architecture/PRINCIPIOS-ARQUITECTURA.md` → A1-A19 vigentes + mapping
- `architecture/ANTI-PATRONES.md` → catálogo con evidencia
- `decisions/ADR-*.md` → decisiones específicas
- `projects/<slug>/` → proyectos cliente (stallen diferido)

Si no podés leer el disco, no podés afirmar el estado. **Decílo explícitamente al usuario.**

---

## LO QUE CLAUDE NUNCA HACE

```
❌ Inventar estado desde archivos posiblemente desactualizados del Project
❌ Empezar a trabajar sin verificar qué Project es (Framework vs SigmaControl)
❌ Asumir continuidad de contexto previo sin verificar contra el system prompt
❌ Asumir reglas del Framework sin leer CLAUDE.md
❌ Trabajar en el path equivocado (sigmacontrol-camino-1/ vs DEPARTAMENTO-SOFTWARE/)
❌ Declarar audit empírico "completo" sin haberlo verificado en disco
❌ Continuar incrementalmente cuando 2+ audits empíricos sugieren scope completo
❌ Confundir manifestación de #13.x ("declarar sin verificar") con limitación de tools
❌ Saltar el PASO 1 de verificación de contexto del Project (lección N=31+ del 2026-05-20)
```

---

## AUDIT EMPÍRICO RECURSIVO — práctica nativa del Framework

Lección destilada de 3 audits empíricos sucesivos en este proyecto (2026-05-15):

> Cuando el usuario hace preguntas arquitectónicas en cadena ("¿hacemos X?
> ¿y Y? ¿y Z?"), después de 2 hits considerar **audit empírico COMPLETO**
> (catalogar TODAS las dimensiones de una vez) en lugar de seguir incremental.

Hit rate empírico acumulado: 17/17 GAPs detectados (A11-A25 + anti-patterns).
Aplicación recursiva del 6° principio rector al meta-trabajo.

Cuando aplicar:
- 2+ audits incrementales en la misma sesión sobre la misma dimensión
- Intuición arquitectónica del usuario es consistente (hit rate > 80%)
- Costo de catálogo completo (~30 min) < costo de iteraciones (N × 15 min × N)

---

## DOCUMENTACIÓN CLAVE

| Documento | Qué contiene | Frecuencia de lectura |
|---|---|---|
| `CLAUDE.md` | Constitución + 7 principios + dispatcher | Cada sesión |
| `auditoria/sesion-activa.md` | Último cierre detallado con audits empíricos | Cada sesión |
| `SIGUIENTE-SESION.md` | Plan inmediato + decisiones pendientes | Cada sesión |
| `NORTE.md` | Propósito Framework + visión harness anti-alucinación | ~1x mes |
| `DEPARTAMENTO-DE-SOFTWARE.md` | Arquitectura completa, roles, stack, tiers | On-demand |
| `SISTEMA-DE-TRABAJO.md` | Manual operativo día-a-día, estaciones de trabajo | On-demand |
| `PROTOCOLO-CONSTRUCCION-CODIGO.md` | 12 pasos determinísticos | On-demand cuando construís código |
| `PROTOCOLO-CIERRE-SESION.md` | Cierre con audit empírico + deudas + commit | Al cerrar sesión |
| `architecture/PRINCIPIOS-ARQUITECTURA.md` | A1-A19 reglas universales + mapping SOLID/Harness | Al diseñar |
| `architecture/ANTI-PATRONES.md` | 28 anti-patterns con evidencia empírica | Al revisar código |
| `decisions/ADR-*.md` | Decisiones técnicas individuales | Al consultar contexto histórico |
| `docs/AGENT-INTEGRATION.md` | Guías cross-LLM (Cursor, Codex, etc.) | Cuando integrás agentes nuevos |
| `templates/project-skeleton/` | Templates para proyectos clientes | Al crear proyecto nuevo |

---

## MEMORIA DEL SISTEMA

- **Corto plazo**: contexto de la sesión actual (compactación automática de Claude)
- **Largo plazo**: `auditoria/sesion-activa.md` regenerado cada sesión + `auditoria/archivo/` con sesiones pasadas
- **Estado canónico vigente**: sesion-activa.md + SIGUIENTE-SESION.md (NO los archivos del Project)
- **Memoria persistente cross-sesión** (futuro): claude-mem cuando se instale (DEUDA-ENGRAM-SAC-BLOCK resuelta por reemplazo)

---

## DIFERENCIA CON SIGMACONTROL LEGACY

| Aspecto | SigmaControl (legacy) | Framework (este proyecto) |
|---|---|---|
| Path | `C:\Users\Windows 11\sigmacontrol-camino-1\` | `C:\DEPARTAMENTO-SOFTWARE\` |
| Estado | Refactor 3 capas pausado en s44 (2026-05-08) | Sprint 2 en curso (2026-05-15+) |
| Modo | REFACTOR META-PRODUCTO (capacidad output 0) | Activo, construyendo Framework v0.1 |
| Stallen | Cliente esperando pausado | Diferido (decisión §13 sesion-activa) |
| Constitución | CLAUDE_DEPARTAMENTO.md | CLAUDE.md |
| Protocolos | ritual.py (Python orquestador) | Manual con checklist (ritual.py futuro) |
| Memoria | sesion-activa + ESTADO-SISTEMA + HORIZONTE | sesion-activa + SIGUIENTE-SESION |
| Repo Git | local | local + GitHub `departamento-software` |

**Regla operativa**: este Project es del Framework. Si necesitás trabajar en
SigmaControl legacy, abrí el Project específico de SigmaControl (con sus
archivos `PROTOCOLO-INICIO-CHAT.md` v7.7 + `CLAUDE_DEPARTAMENTO.md` v15.17).
**No mezclar contextos.**

---

Creado: 2026-05-20
Versión: 1.0 inicial — separación clara Framework vs SigmaControl legacy tras manifestación N=31+ del sub-meta-patrón #13.x detectada el 2026-05-20.
Principio rector aplicado: honestidad sobre qué contexto tengo, no inventar.
