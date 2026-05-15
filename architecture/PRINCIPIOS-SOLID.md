# PRINCIPIOS SOLID — Adaptados al Departamento de Software

> **Nivel 2: arquitectura universal** | SOLID adaptado a contexto multi-stack
> Versión: 1.0 | Creado: 2026-05-15

---

## Por qué SOLID acá (y no solo OOP)

SOLID nació en 2000 (Robert C. Martin) para diseño orientado a objetos. Pero los
5 principios son **patrones de organización** que trascienden OOP. Aplican a:

- Diseño de módulos de software (OOP original)
- Diseño de servicios (microservicios, MCP servers)
- Diseño de skills/agents (harness engineering)
- Diseño de documentación (estructura de archivos)
- Diseño de schemas de datos (DB, JSON, APIs)
- Diseño de procesos (workflows, protocols)

El Departamento aplica SOLID a **todos estos niveles simultáneamente**, no solo
al código Python. Esta es la traducción explícita.

---

## S — Single Responsibility Principle

**Definición clásica**: una clase tiene una sola razón para cambiar.

**Adaptado al Departamento**: cada artefacto del sistema tiene UNA responsabilidad
clara. Si cambian dos razones distintas, vale separar en dos artefactos.

### Aplicación por tipo de artefacto

```
Cada MCP server         → UNA categoría de validación
Cada skill markdown     → UN concept/dominio cubierto
Cada módulo SQL         → UN dominio de negocio
Cada Python validator   → UN tipo de regla específica
Cada ADR                → UNA decisión técnica específica
Cada archivo en raíz    → UN propósito (entry point, root config)
Cada domain-capture     → UN cliente/dominio
```

### Violaciones conocidas (a evitar)

```
❌ MCP server "validate_everything(sql)" monolítico
   → Mejor: validate_invariants, validate_performance, validate_security separados

❌ Skill markdown "sigma-do-anything.md"
   → Mejor: skill por concept específico

❌ CLAUDE.md mezclando principios + workers + decisiones
   → Mejor: CLAUDE.md solo principios, decisiones en ADRs

❌ Archivo Python con función "construir_validar_deployar_documentar()"
   → Mejor: 4 funciones, una responsabilidad cada una
```

### Cómo verificar SRP

Pregunta al artefacto: **"¿Por qué cambiarías este archivo en el futuro?"**

- Si la respuesta tiene UNA razón clara → SRP cumplido
- Si la respuesta tiene 2+ razones independientes → vale separar

### Test concreto para skills

Un skill cumple SRP si su título responde una pregunta única:
- ✅ `sigma-immutable-tables` → "¿Cómo manejo tablas inmutables?"
- ✅ `sigma-multitenancy-bootstrap` → "¿Cómo arranco RLS multi-tenant?"
- ❌ `sigma-sql-everything` → "¿Cómo hago todo lo de SQL?" (demasiado amplio)

---

## O — Open/Closed Principle

**Definición clásica**: abierto a extensión, cerrado a modificación.

**Adaptado al Departamento**: el sistema debe permitir agregar capacidades nuevas
sin tocar las existentes. Cada nivel de regla es "cerrado a modificación" desde
los niveles inferiores.

### Aplicación por tipo de extensión

```
Nuevos validators       → AGREGAR al MCP server (NO modificar existentes)
Nuevos dominios         → AGREGAR a domain-captures/ (NO tocar core)
Nuevas skills           → AGREGAR a .claude/skills/ (NO editar existentes)
Nuevos clientes         → AGREGAR config Nivel 4 (NO reescribir Niveles 1-3)
Nuevas reglas SQL       → AGREGAR al archivo Python apropiado (NO romper otras)
```

### Por qué Niveles 1-3 son agnósticos de proyecto

Esta es la consecuencia directa de OCP en el Departamento:

```
Niveles 1-3 son CERRADOS a modificación por proyecto.
Niveles 4-5 son ABIERTOS a extensión por proyecto.

Si necesitás cambiar Nivel 1-3 para un proyecto específico:
→ Significa que la regla NO era universal (clasificación incorrecta)
→ Re-evaluar nivel correcto
→ Solo modificar Nivel 1-3 si descubriste algo verdaderamente universal
```

### Violaciones conocidas (a evitar)

```
❌ Editar architecture/PRINCIPIOS-ARQUITECTURA.md "porque Stallen necesita X"
   → Stallen-specific va en domain-captures/

❌ Hardcodear "stallen-sc" en código del MCP server
   → El nombre del cliente se INYECTA via config

❌ Modificar skill sigma-immutable-tables porque Stallen tiene 3 tablas inmutables
   → Las 3 tablas se DECLARAN en stallen-domain.md, no en la skill

❌ Romper backward compatibility de una skill existente
   → Mejor: skill nueva con suffix v2
```

### Cómo verificar OCP

Pregunta al artefacto: **"¿Para tomar el siguiente cliente, necesito MODIFICAR
este archivo o solo agregar configuración?"**

- Si solo agregás config → OCP cumplido
- Si necesitás editar archivo de Nivel 1-3 → OCP violado, re-evaluar

---

## L — Liskov Substitution Principle

**Definición clásica**: subtipos deben ser sustituibles por sus tipos base sin
romper el programa.

**Adaptado al Departamento**: cualquier implementación que respeta un contrato/schema
es sustituible por otra que respete el mismo contrato.

### Aplicación por tipo de contrato

```
Cualquier RPC con contrato (p_X UUID) RETURNS Y → sustituible
Cualquier MCP tool con schema declarado         → sustituible
Cualquier skill con formato sigma-*.md           → sustituible
Cualquier domain-capture que cumpla SCHEMA.md   → sustituible
Cualquier validator que retorne (ok: bool, violaciones: list) → sustituible
```

### Implicación crítica: SCHEMAs explícitos

Para que LSP funcione, **cada categoría de artefacto necesita schema explícito**:

- Skills → schema en `.claude/skills/SCHEMA.md` (define frontmatter, secciones obligatorias)
- MCP tools → schema JSON oficial (input + output)
- Domain captures → schema en `domain-captures/SCHEMA.md` (campos obligatorios)
- Validators Python → contrato común `(ok: bool, violaciones: list[str])`

Sin schema explícito, no hay LSP posible.

### Ejemplo de LSP cumplido (del legacy SigmaControl)

```python
# Todos los validators del legacy retornan la misma firma:
def verificar_handoff(handoff) -> (bool, list[str]):
def verificar_resultado_ejecutar(resultado, sql) -> (bool, list[str]):
def verificar_resultado_deploy(resultado) -> (bool, list[str]):
def verificar_grafo(grafo) -> (bool, list[str]):
def verificar_estado(estado) -> (bool, list[str]):

# Esto permite función genérica que las consuma:
def verificar_todos(**kwargs) -> dict:
    # Trabaja con cualquier validador que cumpla el contrato
    ...
```

### Violaciones conocidas (a evitar)

```
❌ MCP tool que a veces retorna string, a veces dict
   → Inconsistencia rompe LSP

❌ Skill que a veces tiene frontmatter, a veces no
   → Tools que parsean skills no pueden tratarlas igual

❌ Validator Python con firma distinta a otros validators
   → Imposible consumirlos uniformemente
```

### Cómo verificar LSP

Pregunta al artefacto: **"Si reemplazo este artefacto por otro de su misma
categoría, ¿el resto del sistema sigue funcionando?"**

- Si sí → LSP cumplido
- Si no → re-evaluar si el schema/contrato está bien definido

---

## I — Interface Segregation Principle

**Definición clásica**: las interfaces deben ser específicas, no monolíticas.
Clientes no deberían depender de métodos que no usan.

**Adaptado al Departamento**: cada artefacto expone interfaces focalizadas, no
contratos amplios. Consumidores eligen qué consumir, no se obligan a todo.

### Aplicación por tipo de artefacto

```
MCP server → expone tools específicas
   ✅ validate_sql_invariants(sql)
   ✅ validate_sql_performance(sql)
   ✅ validate_sql_security(sql)
   ❌ validate(sql, type="invariants") monolítico

Skill → cubre un scope acotado
   ✅ sigma-immutable-tables (qué es, RLS correcta, checklist)
   ❌ sigma-sql-everything (cubre 10 temas distintos)

Domain capture → focalizada en UN dominio
   ✅ stallen-domain.md
   ✅ cliente-x-domain.md
   ❌ all-clients-domain.md mezclando todos

Python module → función por responsabilidad
   ✅ verificar_handoff, verificar_grafo, verificar_estado (separados)
   ❌ verificar_todo(handoff, grafo, estado) monolítico
```

### Por qué importa para vibe coders / harness engineers

Como **harness engineer** que pide a Claude Code que escriba código, querés:
- Validar UN aspecto a la vez (más debugging-friendly)
- Componer validaciones según necesites
- No pagar costo de validar lo que no es relevante

Una tool monolítica `validate(sql)` que hace TODO obliga a:
- Ejecutar validaciones irrelevantes
- Parsear output complejo para encontrar lo relevante
- No poder pedir solo "X validation"

Tools segregadas permiten:
- "Solo validá security, el resto ya lo verifiqué manualmente"
- "Pedile a Claude que ejecute validate_performance + validate_concurrency"
- Output específico, no soup de findings mixtos

### Violaciones conocidas (a evitar)

```
❌ MCP server con UNA tool "do_everything(input)"
❌ Skill markdown con 8 secciones sin relación entre sí
❌ Función Python con 12 parámetros opcionales y mil branches
❌ ADR que cubre 5 decisiones distintas
```

### Cómo verificar ISP

Pregunta al artefacto: **"¿Un consumidor que solo necesita X tendría que cargar
también Y, Z, W?"**

- Si no → ISP cumplido
- Si sí → segregar interface

---

## D — Dependency Inversion Principle

**Definición clásica**: depender de abstracciones, no de implementaciones
concretas. Los módulos de alto nivel no deberían depender de los de bajo nivel.

**Adaptado al Departamento**: el harness depende de **configuración abstracta**,
no de **valores específicos del proyecto**.

### Aplicación por tipo de dependencia

```
domain-captures depende de SCHEMA → abstracción, NO implementación específica
Reglas SQL dependen de configuración (ADN) → NO hardcoded values
Harness depende de configuración del proyecto → NO del proyecto específico
MCP server depende de domain-captures/ → NO de "Stallen"
.claude/skills depende de project context → NO de Stallen hardcoded
```

### Ejemplo claro del legacy (reglas_escala.py)

El legacy ya aplicaba DIP en reglas de escala:

```python
# INCORRECTO (hardcoded, viola DIP):
TABLAS_UNBOUNDED = {
    "audit_log_sc", "inventory_movements_sc", "sales_sc"
}  # Stallen específico, no portable

# CORRECTO (DIP cumplido):
# Sufijos universales en el código
SUFIJOS_UNBOUNDED = ("_log", "_movements", "_entries", "_history", "_audit")

# Adicionales específicas del cliente, en el ADN del proyecto
# stallen-domain.md declara: tablas_unbounded_adicionales: ["sales_sc"]
```

El código (Nivel 3) define la **abstracción** (sufijos universales).
El cliente (Nivel 4) declara la **especificación** (su tabla extra).

Si tomás otro cliente, NO tocás código. Solo cambiás Nivel 4.

### Implicación para Sprint 2 T2

El MCP server `sigma-validators-r` debe seguir DIP estrictamente:

```python
# CORRECTO:
class SqlValidator:
    def __init__(self, config: DomainConfig):
        self.tablas_inmutables = config.tablas_inmutables
        self.helper_company_id = config.helper_company_id
        self.escala_operativa = config.escala_operativa
        # ... etc

    def validate_invariants(self, sql, rollback):
        # Usa self.tablas_inmutables, NO valores hardcoded
        ...

# INCORRECTO:
def validate_sql(sql):
    INMUTABLES = {"inventory_movements", "customer_interactions"}  # Stallen-specific
    # ... usa INMUTABLES hardcoded
```

### Violaciones conocidas (a evitar)

```
❌ Hardcodear nombres de tablas Stallen en código del MCP server
❌ Tests que solo pasan si stallen-domain.md existe
❌ Skills que mencionan tablas específicas como ejemplos definitivos
❌ ADRs que asumen contexto Stallen sin declararlo explícitamente
```

### Cómo verificar DIP

Pregunta al artefacto: **"¿Este código/documento funciona para CUALQUIER cliente
que cumpla el contrato, o solo para Stallen?"**

- Si funciona para cualquiera → DIP cumplido
- Si depende de Stallen → re-evaluar dónde va lo Stallen-specific

---

## Cómo SOLID se materializa en la estructura de carpetas

Esta no es coincidencia — la separación de carpetas REFLEJA SOLID:

| Carpeta | SOLID que justifica |
|---|---|
| `architecture/` (esta carpeta, Nivel 2) | **SRP**: separa arquitectura de implementación. **OCP**: no se modifica per-proyecto |
| `.claude/skills/` (Nivel 3) | **SRP**: una skill = un scope. **ISP**: skills focalizadas |
| `mcp-servers/` (Nivel 3) | **SRP**: cada server = una responsabilidad. **ISP**: tools focalizadas. **DIP**: config-driven |
| `domain-captures/` (Nivel 4) | **DIP**: abstracción del dominio. **OCP**: agregás clientes sin modificar reglas |
| `decisions/` (Nivel 5) | **SRP**: un ADR = una decisión. Inmutabilidad histórica |
| `workspace/` (Proyecto activo) | **SRP**: separa código real del harness |

Ver `PATRONES-CARPETAS.md` para detalle completo.

---

## Anti-patterns SOLID conocidos

Catálogo de violaciones SOLID identificadas en el legacy o en otros sistemas:

### 1. "God Validator" (anti-SRP, anti-ISP)
Un único validador que valida todo: SQL, frontend, contratos, deploy, estado.
**Corrección**: separar en validators específicos.

### 2. "Hardcoded Domain" (anti-OCP, anti-DIP)
Nombres de tablas, helpers, sufijos del cliente metidos en código universal.
**Corrección**: extraer a domain-captures/ con schema.

### 3. "Inconsistent Returns" (anti-LSP)
Validators/tools que retornan distintos tipos según caso.
**Corrección**: contrato uniforme `(ok, violaciones)`.

### 4. "Monolithic Skill" (anti-SRP)
Skill markdown con 8 secciones sin relación: cómo escribir SQL + cómo hacer
handoff + cómo cerrar sesión.
**Corrección**: una skill por concepto.

### 5. "Cross-Level Pollution" (anti-OCP)
Reglas de Nivel 4 (dominio) escritas como si fueran Nivel 2 (universal).
**Corrección**: clasificación correcta de nivel.

---

## Cómo este documento se mantiene

**Cambios válidos a este archivo**:
- Aparece patrón nuevo de SOLID adaptado al contexto del Departamento
- Se descubre nueva clase de violación con evidencia empírica
- Se formaliza vocabulario industrial relevante (ej: GRASP, Clean Architecture)

**Cambios INVÁLIDOS**:
- "Stallen necesita Y" → no, va en Nivel 4
- "Mi proyecto actual requiere Z" → no, va en Nivel 5 (ADR)
- "Encontré una mejor manera, voy a sobrescribir" → no, propone v2 con razón

---

Versión: 1.0 | Creado: 2026-05-15
Basado en: legacy SigmaControl `core/contratos.py`, `reglas_escala.py`, observaciones de validación adversarial
