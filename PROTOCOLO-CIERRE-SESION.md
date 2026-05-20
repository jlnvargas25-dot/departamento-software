# PROTOCOLO DE CIERRE DE SESIÓN — Departamento de Software (Framework)
# Versión: 1.0 | 2026-05-20
# Checklist obligatorio al cerrar cualquier sesión de trabajo en el Framework

---

## CUÁNDO APLICAR

Al final de cada sesión, ANTES de despedirse. No importa si la sesión fue
corta o larga — el protocolo garantiza que nada se pierde.

**Diferencia con SigmaControl legacy**: este protocolo NO usa `ritual.py`
todavía (DEUDA-RITUAL-FRAMEWORK abierta para futuro Sprint). Se ejecuta
manualmente con el checklist.

---

## FORMA CANÓNICA DE EJECUCIÓN

**Manual con checklist verificado**. Cada paso se ejecuta y se marca como
OK/GAP/N/A explícitamente al final en el audit del paso 8.

Cuando exista `ritual.py` adaptado al Framework (futuro), reemplazará la
ejecución manual. Mientras tanto, **saltar el checklist es violación del
protocolo**.

---

## CHECKLIST DE CIERRE (en orden)

### 1. DOCUMENTAR LO QUE SE HIZO

```
□ Actualizar auditoria/sesion-activa.md con:
  - Qué se hizo (lista concreta por área: arquitectura, decisiones, código, docs)
  - Qué cambió (archivos creados/modificados con paths)
  - Lecciones aprendidas (lecciones N=1 vs N=2+ con criterio claro)
  - Bugs encontrados (incluido bugs de tools MCP como el $$/$BODY$ → edit_file)
  - Audits empíricos ejecutados (1, 2, 3... con cantidad de GAPs detectados)
  - Tests y sus resultados
  - Estado final del repo (commits hoy, working tree limpio sí/no)
  - Notas críticas para próximo Claude
```

### 2. ACTUALIZAR SIGUIENTE SESIÓN

```
□ Escribir SIGUIENTE-SESION.md con:
  - Comando inmediato al abrir (típicamente git pendientes + lecturas obligatorias)
  - Decisiones explícitas pendientes para próxima sesión (A, B, C... con opciones)
  - Resumen ejecutivo paso a paso (T0, T1, T2... con tiempo estimado)
  - Cliente recomendado (Claude Code CLI, Claude Desktop, Claude in Chrome)
  - Riesgos conocidos de la próxima sesión
```

### 3. ACTUALIZAR DOCUMENTOS TOCADOS

```
□ Si se modificó arquitectura (A* reglas o anti-patterns) → bump version
  en architecture/PRINCIPIOS-ARQUITECTURA.md y architecture/ANTI-PATRONES.md
  + actualizar histórico de versiones + mappings (SOLID, Harness Engineering)

□ Si se tomó decisión técnica no obvia → crear decisions/ADR-NNN-titulo.md

□ Si se cambió NORTE/visión estratégica → bump NORTE.md + considerar archivado
  a auditoria/historia-estrategica/ (cuando exista esa carpeta)

□ Si se modificó protocolo → actualizar el .md correspondiente + versión

□ Si se creó documento nuevo en raíz → considerar agregarlo a la tabla
  "DOCUMENTACIÓN CLAVE" de PROTOCOLO-INICIO-CHAT.md
```

### 4. RADAR DE DEUDA NUEVA — OBLIGATORIO

```
□ Preguntarse explícitamente: ¿esta sesión generó deuda o pendientes?

□ Si apareció deuda técnica concreta (bug estructural, módulo inconsistente,
  patrón repetido, regla arquitectónica faltante):
  → agregar a sesion-activa.md sección "Deudas técnicas detectadas"
    con formato:
      DEUDA-<NOMBRE> (NUEVA — esta sesión)
      Status: 🔴 ABIERTA / 🟡 EN PROGRESO / ✅ RESUELTA
      Scope: descripción concreta
      Criticidad: 🔴 Crítica / 🟡 Importante / 🟢 Nice-to-have
      Tiempo estimado: ~N min
      Próxima acción: cuándo se aborda

□ Si aparecieron ideas/preguntas/observaciones sueltas (sin criticidad
  inmediata): → considerar archivo de bitácora (futuro CUADERNO-BITACORA.md
  del Framework cuando exista)

□ Si no apareció nada nuevo: → anotarlo en sesion-activa.md
  ("radar de deuda: limpio")
```

Este paso es innegociable. Una sesión cerrada sin radar es una sesión que
posiblemente dejó deuda silenciosa.

### 5. AUDIT EMPÍRICO RECURSIVO — Práctica nativa del Framework

Lección destilada de la sesión 2026-05-15 (3 audits empíricos sucesivos
detectaron 15 GAPs, hit rate 17/17):

```
□ Si el usuario hizo preguntas arquitectónicas en cadena durante la sesión:
  - ¿Hubo 2+ audits incrementales?
  - ¿Su intuición arquitectónica tuvo hit rate alto (>80%)?
  - SI ambos SÍ → recomendar audit empírico COMPLETO antes de seguir
    incremental

□ Si esta sesión generó reglas arquitectónicas nuevas (A* o anti-patterns):
  - ¿Existe ya un meta-patrón que las cubre?
  - ¿Vale agregar nueva manifestación al meta-patrón existente?
  - Si NO existe meta-patrón → documentar en sesion-activa.md como
    candidato (espera N=2 antes de promover formalmente)

□ Si esta sesión validó empíricamente un patrón conjeturado previamente:
  - Actualizar status del meta-patrón (HIPOTESIS → VALIDADA)
  - Documentar evidencia empírica concreta

□ Si no aplica: anotar en sesion-activa.md "radar polinización: limpio"
```

Aplicación recursiva del 6° principio rector al meta-trabajo: descubrir
scope completo antes de ejecutar.

### 6. VERIFICAR CONSISTENCIA

```
□ ¿SIGUIENTE-SESION.md es coherente con sesion-activa.md?
□ ¿Los archivos modificados en disco coinciden con lo declarado?
   (verificación empírica con list_directory + read_text_file sobre
   archivos clave — aplicación del 6° principio rector al cierre)

□ ¿Hay archivos .md obsoletos en raíz que valdría archivar?

□ ¿Mojibake detectado en archivos editados con write_file?
   (caracteres ��� donde debería haber → ñ ó é etc. — re-leer head + tail
   de archivos críticos editados en esta sesión)
```

### 7. COMMIT + PUSH — ÚLTIMA LÍNEA DE DEFENSA

```
□ Verificar estado git:
    cd C:\DEPARTAMENTO-SOFTWARE
    git status

□ Si hay cambios sin commitear:
    git add -A          # -A incluye deletions + untracked desde la raíz
    git status          # verificación pre-commit
    git commit -m "tipo(scope): descripción concisa

Cambios detallados:
- ...
- ...

Audits empíricos: N (cantidad ejecutada esta sesión)
GAPs detectados: M
Deudas nuevas: K (lista)
Decisiones pendientes próxima sesión: A, B, C"

    git push

□ Segundo git status (red de seguridad post-push):
    git status
    # Esperado: "nothing to commit, working tree clean"

□ Verificar que push terminó OK:
    - "Everything up-to-date" → ya estaba al día (OK)
    - "X objects written" → subido bien (OK)
    - Error → resolver antes de cerrar
```

**Por qué git add -A en vez de git add .**:
- `git add .` agrega cambios del directorio actual hacia abajo; podés
  perder silenciosamente cambios en directorios hermanos
- `git add -A` agrega TODO el repo desde la raíz
- Lección destilada de SigmaControl legacy (DEUDA 1.10 cerrada 2026-04-22)

**Hook GGA (Gentleman Guardian Angel)** corre automáticamente:
- Solo revisa código (*.py, *.sql, *.ts, etc.), NO markdown
- Si NO hay código modificado → dice "No matching files staged" (OK)
- Cambios estructurales a architecture/ NO tienen review automático
  (DEUDA-A21-OBSERVABILITY incluye sub-meta para mejorar esto)

### 8. AUDIT FINAL DEL CIERRE

```
□ Enumerar los 7 pasos anteriores y marcar cada uno como OK / GAP / N/A:

    Paso 1   sesion-activa.md actualizado           → OK / GAP
    Paso 2   SIGUIENTE-SESION.md actualizado        → OK / GAP
    Paso 3   docs tocados (arch, ADRs, NORTE)       → OK / GAP / N/A
    Paso 4   radar de deuda nueva                   → OK / GAP
    Paso 5   audit empírico recursivo               → OK / GAP / N/A
    Paso 6   verificación consistencia              → OK / GAP
    Paso 7   commit + push                          → OK / GAP

□ Si hay al menos 1 GAP:
   OPCIÓN A → arreglar el gap en esta misma sesión antes de declarar cerrada
   OPCIÓN B → re-declarar como diferido explícito en sesion-activa.md
              con razón estructural
  NO OPCIÓN: declarar cerrada con gaps silenciosos

□ Anotar el resultado en sesion-activa.md sección "Audit de cierre":
    "audit paso 8: 7 OK, 0 gaps"
    o "audit paso 8: 6 OK, 1 gap diferido a próxima sesión — razón X"
```

---

## REGLAS

1. **NUNCA** cerrar sin actualizar sesion-activa.md
2. **NUNCA** cerrar sin escribir SIGUIENTE-SESION.md
3. **NUNCA** cerrar sin ejecutar el radar de deuda (paso 4)
4. **NUNCA** cerrar sin hacer git push (paso 7)
5. **NUNCA** cerrar sin ejecutar el audit final (paso 8)
6. **SIEMPRE** actualizar los documentos que se tocaron
7. **SIEMPRE** verificar consistencia disco vs declarado (6° principio rector)
8. **NUNCA** declarar audit empírico recursivo "completo" sin haberlo verificado contra el catálogo de dimensiones arquitectónicas
9. **SIEMPRE** preferir audit COMPLETO sobre audit incremental cuando hay 2+ hits previos en la misma dimensión
10. El protocolo toma 10-20 minutos manual — esa inversión ahorra 30+ minutos en la siguiente sesión y protege contra pérdida total

---

## FORMATO DE sesion-activa.md

```markdown
# SESIÓN ACTIVA — Framework Departamento

**Última sesión**: YYYY-MM-DD — [resumen 1 línea]
**Cliente**: [Claude Code CLI / Claude Desktop / Claude in Chrome]
**Duración estimada**: [corta / media / larga / muy larga]
**Estado**: ✅ Cerrada [con/sin gaps]

---

## Resumen ejecutivo (1 línea)
[qué pasó en una oración]

## Lo que se hizo (cronológico)
### 1. [Tarea/área]
[detalle]

### 2. ...

## Lecciones críticas
### LECCIÓN N — [título]
[detalle + cuándo aplicarla]

## Deudas técnicas detectadas
### DEUDA-NOMBRE
**Status**: 🔴 ABIERTA / 🟡 EN PROGRESO / ✅ RESUELTA
**Scope**: ...
**Criticidad**: 🔴 Crítica / 🟡 Importante
**Próxima acción**: ...

## Audit empírico de la sesión (si aplica)
[catálogo de GAPs detectados, hit rate, etc.]

## Estado del repo al cerrar
```
Branch: main
Working tree: clean / con cambios pendientes
Total commits hoy: N
Remote: sincronizado hasta <hash>
```

## Próximo paso — PRIORIDAD CLARA
### 1. Comando inmediato (al abrir próxima sesión):
[comando concreto PowerShell o bash]

### 2. Decisiones pendientes para próxima sesión
[A, B, C... con opciones]

### 3. Roadmap actualizado próxima sesión
[T0, T1, T2... con tiempo estimado]

## Notas críticas para próximo Claude
[lista de gotchas, paths, anti-paternalismo, etc.]

---

Versión: N.M (descripción del cambio)
Estado: ✅ CERRADA
Próxima sesión: cliente recomendado [X]
```

---

## FORMATO DE SIGUIENTE-SESION.md

```markdown
# INSTRUCCIONES SIGUIENTE SESIÓN — Framework

## CONTEXTO RÁPIDO
Leer EN ORDEN al arrancar:
1. CLAUDE.md (constitución, ~5 min)
2. auditoria/sesion-activa.md (último cierre, ~5 min)
3. Este archivo (plan inmediato, ~3 min)
4. [Documentos específicos según tarea]

## ESTADO ACTUAL
- Sprint: [N]
- Nivel 2 arquitectura: [M reglas + K deudas]
- Decisiones pendientes: [A, B, C]

## QUÉ HACER ESTA SESIÓN
### PASO 1 — Comando inmediato
[concreto con powershell o bash]

### PASO 2 — [Tarea principal]
[detalle]

### PASO 3 — ...

## PRE-FLIGHT
[comandos de verificación que validan el estado al arrancar]

## RIESGOS DE LA PRÓXIMA SESIÓN
[lista honesta de cosas que pueden fallar]

## ARCHIVOS CLAVE A TOCAR EN LA PRÓXIMA SESIÓN
[lista paths con razón]
```

---

## DEUDA CONOCIDA SOBRE ESTE PROTOCOLO

### DEUDA-RITUAL-FRAMEWORK
**Status**: 🟡 ABIERTA
**Scope**: SigmaControl legacy tiene `ritual.py inicio` y `ritual.py cierre`
con audit mecánico automático. El Framework todavía ejecuta el checklist
manualmente. Vale portar/adaptar `ritual.py` cuando el Framework esté
maduro (post-Sprint 5+).
**Criticidad**: 🟡 Importante (no bloqueante en Sprint 2-3)
**Tiempo estimado**: ~4-6 hs portar + adaptar
**Próxima acción**: post-sandbox del stack ecosistema (T1+) cuando se
decida si claude-mem/superpowers/ECC cubren parte de esto

### DEUDA-AUDIT-FORMALIZADO-NIVEL-2
**Status**: 🔴 ABIERTA — CRÍTICA (audit empírico 3 detectó 6 GAPs documentados)
**Scope**: Implementar A20-A25 + 6 anti-patterns asociados (ver
auditoria/sesion-activa.md §18 catálogo completo)
**Criticidad**: 🔴 Crítica (paradigma + observability + secrets + data lifecycle)
**Tiempo estimado**: ~3 horas total
**Próxima acción**: decisión A en próxima sesión (¿antes/después/híbrido sandbox?)

---

Creado: 2026-05-20
Versión: 1.0 inicial — protocolo adaptado al Framework, separado de SigmaControl legacy.
Lección N=31+ del sub-meta-patrón #13.x integrada como paso 1 + 6 del checklist.
Audit empírico recursivo formalizado como paso 5 nativo del Framework.
Principio rector aplicado: descubrir antes de declarar — incluso al cerrar.
