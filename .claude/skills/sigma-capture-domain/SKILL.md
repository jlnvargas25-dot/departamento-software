---
name: sigma-capture-domain
description: "Captura sistemática del dominio del negocio antes de implementar cualquier feature. Trigger: el usuario menciona arrancar una change/feature/módulo nuevo, o un cambio que toca lógica de negocio no documentada. Aplicación directa del 3° principio rector (dominio-first)."
user-invocable: true
disable-model-invocation: false
license: MIT
metadata:
  author: departamento-software
  version: "1.0"
  date: "2026-05-14"
  principles: ["3rd-domain-first", "6th-discover-before-execute"]
---

# Skill: sigma-capture-domain

## Propósito

Forzar la captura **explícita y verificable** del dominio del negocio ANTES de tocar código. Esta skill existe porque:

- El **3° principio rector** dice "dominio-first": no se implementa sin dominio capturado
- El **6° principio rector** dice "descubrir antes de ejecutar": auditoría empírica precede a estimación
- La experiencia empírica muestra que **80% de los bugs sutiles vienen de asunciones implícitas sobre reglas del negocio**

Sin esta skill, los agentes (humanos o IA) asumen reglas. Las asunciones generan deuda silenciosa. Con esta skill, todo lo que va a producirse tiene un contrato verificable del dominio.

---

## Cuándo invocar esta skill

**SIEMPRE** que vayas a:

- Arrancar una change OpenSpec nueva que toca lógica de negocio
- Migrar un componente legacy (ej: validators de SigmaControl)
- Agregar una entidad o regla nueva al sistema
- Modificar comportamiento existente cuando no hay dominio documentado previo

**NUNCA** invocar para:

- Cambios de infraestructura (CI/CD, observabilidad, deployment)
- Refactors mecánicos sin cambio funcional
- Bug fixes triviales (typos, formato)
- Documentación que no toca lógica

---

## Inputs requeridos

1. **Nombre del dominio/módulo/feature** a capturar (en kebab-case)
   - Ejemplos: `validator-r01`, `feature-soft-delete`, `module-billing`
2. **Contexto del proyecto** (opcional, default: Stallen)
3. **Source disponible** (opcional): código legacy, docs previos, conversación con stakeholder

---

## Output garantizado

Un archivo en `domain-captures/<nombre>-domain.md` con esta estructura **obligatoria**:

```
# Dominio: <nombre>

**Versión**: 1.0
**Capturado**: YYYY-MM-DD
**Proyecto**: <stallen | otro>
**Estado**: borrador | revisado | aprobado
**Captador**: <humano + IA, formato "Julian + Claude (sigma-capture-domain v1.0)">

## 1. Propósito del módulo
[Una frase: para qué existe este módulo en el negocio]

## 2. Entidades
[Lista de entidades del dominio con definición precisa]

## 3. Reglas del negocio
[Reglas explícitas con formato: "DEBE/PUEDE/NUNCA/SIEMPRE + condición"]

## 4. Invariantes
[Condiciones que SIEMPRE deben mantenerse, codificables como asserts]

## 5. Casos edge identificados
[Inputs vacíos, malformados, boundary, race conditions, network failures]

## 6. Glosario
[Términos del dominio con definición canónica]

## 7. Asunciones declaradas
[Lo que vamos a asumir explícitamente, con justificación]

## 8. Lo que NO está en scope
[Reglas/casos deliberadamente fuera de este dominio]

## 9. Preguntas pendientes
[Cosas que NO se pudieron resolver y requieren input adicional]

## 10. Referencias
[Source code legacy, conversaciones, docs externos]
```

---

## Steps detallados (workflow obligatorio)

### Step 1: Verificar precondiciones

Antes de empezar:

- [ ] ¿Existe ya `domain-captures/<nombre>-domain.md`?
  - SÍ → leer primero. Si está en estado "aprobado", preguntar al usuario si quiere actualizar o crear versión nueva.
  - NO → continuar.
- [ ] ¿El usuario aportó source disponible (código, docs, conversación)?
  - SÍ → leer ANTES de hacer preguntas.
  - NO → preguntar al usuario qué fuentes existen.
- [ ] ¿La invocación tiene contexto claro?
  - SÍ → continuar.
  - NO → pedir clarificación: ¿de qué módulo/feature/dominio estamos hablando?

### Step 2: Auditoría empírica (6° principio)

Si hay código legacy o source disponible:

1. Leer el código relevante (no asumir)
2. Identificar entidades en uso
3. Identificar reglas implícitas en código (ej: validaciones, defaults)
4. Identificar dependencias cross-módulo
5. **Reportar al usuario** lo encontrado antes de hacer preguntas

Si NO hay código legacy:

1. Preguntar al usuario sobre el contexto general del módulo
2. Pedir ejemplos concretos de uso esperado
3. Pedir referencia a similares conocidos

### Step 3: Captura guiada por secciones

Hacer preguntas al usuario **una sección a la vez**. No batch. No salto. Orden:

**3.1 Propósito** (siempre primero)
- "En una frase: ¿para qué existe este módulo en el negocio?"
- Si la respuesta es vaga, repreguntar hasta que sea concreta

**3.2 Entidades**
- "¿Cuáles son las entidades principales? (objetos, conceptos del negocio)"
- Para cada entidad: "Definí esta entidad en 1-2 frases"
- Identificar relaciones entre entidades

**3.3 Reglas del negocio**
- "¿Qué reglas DEBE cumplir el sistema?"
- Formato obligatorio: "DEBE/PUEDE/NUNCA/SIEMPRE + condición concreta"
- Numerar las reglas (BR-1, BR-2, ...)
- Cada regla debe ser verificable (testeable)

**3.4 Invariantes**
- "¿Qué condiciones SIEMPRE deben mantenerse, en todo momento?"
- Las invariantes son más fuertes que las reglas — nunca pueden romperse
- Numerar (INV-1, INV-2, ...)
- Idealmente codificables como asserts

**3.5 Casos edge**
- Para cada entidad/regla, preguntar:
  - "¿Qué pasa si el input está vacío?"
  - "¿Qué pasa si el input es malformado?"
  - "¿Qué pasa en boundary conditions (0, máximo, negativos)?"
  - "¿Qué pasa si hay concurrencia?"
  - "¿Qué pasa si una dependencia externa cae?"
- Numerar (EC-1, EC-2, ...)

**3.6 Glosario**
- "¿Hay términos del dominio que valen aclarar?"
- Captura definición canónica de cada término
- Específicamente: jerga del negocio, abreviaciones, nombres de roles

**3.7 Asunciones declaradas**
- "¿Qué vamos a asumir sin verificar? Justificar cada asunción"
- Es OK asumir cosas, pero explícitamente — no implícitamente

**3.8 Out of scope**
- "¿Qué deliberadamente NO está cubierto por este dominio?"
- Evita scope creep en implementación

**3.9 Preguntas pendientes**
- Anotar todo lo que NO se pudo resolver
- Idealmente con propuesta de cómo resolverlo

### Step 4: Validación cruzada

Antes de declarar la captura como completa:

1. Releer el documento completo con el usuario
2. Preguntar: "¿Falta algo? ¿Algo está mal capturado?"
3. Identificar contradicciones internas (regla X contradice regla Y)
4. Confirmar que cada regla tiene al menos un caso edge identificado

### Step 5: Persistencia

1. Escribir el archivo en `domain-captures/<nombre>-domain.md`
2. Actualizar estado a "borrador" (no auto-aprobar)
3. Guardar referencia en Engram con:
   - `topic_key`: `domain-capture/<nombre>`
   - `type`: `architecture`
   - `project`: `<nombre del proyecto>`
4. Si la captura es para una change OpenSpec en curso, agregarla al `state.yaml` como exploration artifact

### Step 6: Reporte final

Al terminar, reportar al usuario:

```
✅ Dominio capturado: <nombre>
📁 Archivo: domain-captures/<nombre>-domain.md
📊 Resumen:
   - Entidades: N
   - Reglas: M (BR-1 a BR-M)
   - Invariantes: K (INV-1 a INV-K)
   - Casos edge: L (EC-1 a EC-L)
   - Términos glosario: J
   - Asunciones: I
   - Preguntas pendientes: H

🚨 Atención (si aplica):
   - Hay H preguntas pendientes que requieren input adicional
   - Hay <N> reglas sin caso edge identificado

🔍 Próximo paso recomendado:
   - Si esto es para change OpenSpec: usar este dominio en proposal.md
   - Si las preguntas pendientes bloquean implementación: resolver antes de continuar
```

---

## Reglas duras (NUNCA romper)

1. **NUNCA capturar dominio asumiendo**. Si no sabés, preguntá al usuario o investigá código existente.
2. **NUNCA saltar secciones**. Las 10 secciones del output son obligatorias. Si una está vacía, marcarla como "N/A" con razón.
3. **NUNCA auto-aprobar la captura**. El estado inicial es "borrador" — el usuario decide cuándo marcarlo "aprobado".
4. **NUNCA reordenar el workflow**. Las 6 steps van en orden. Saltar = bug.
5. **NUNCA capturar dominio sin persistirlo**. Si no se puede escribir el archivo, hay que fallar ruidoso.

---

## Anti-patrones detectados (lecciones aprendidas)

A medida que esta skill se use en proyectos reales, capturar acá los anti-patrones:

- *(vacío en v1 — se irá poblando empíricamente)*

---

## Referencias

- `CLAUDE.md` — 7 principios rectores (3° dominio-first, 6° descubrir antes ejecutar)
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` — pasos 1-2 del protocolo
- `AGENTS.md` — Regla G-7 (Captura de dominio explícita)
- `openspec/config.yaml` — rules.exploration y rules.proposal
- `decisions/ADR-005-cierre-sprint-1.md` — Sprint 2 plan

---

## Evolución de la skill

- **v1.0** (2026-05-14): MVP pragmático con template guiado. Skills user-invocable.
- **v1.1** (futuro): agregar extracción semi-automática desde código legacy.
- **v2.0** (futuro): integrar con MCP server `sigma-validators` para validar reglas en runtime.
