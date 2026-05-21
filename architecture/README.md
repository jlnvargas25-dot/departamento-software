# architecture/

> Reglas de arquitectura universal del Departamento de Software (Nivel 2)

Esta carpeta contiene **reglas universales de arquitectura** que aplican a cualquier
proyecto SaaS multi-tenant construido dentro del Departamento. Son agnósticas de:
- Cliente específico (Stallen, futuros proyectos)
- Stack técnico específico de implementación
- Decisiones de scope momentáneas

## Los 5 niveles de reglas

El Departamento separa explícitamente **5 niveles de reglas** para no mezclar
preocupaciones de distinto alcance. Esta carpeta cubre **Nivel 2** únicamente.

```
NIVEL 1 — Principios filosóficos        → CLAUDE.md, AGENTS.md (raíz)
NIVEL 2 — Arquitectura universal        → architecture/ (esta carpeta)
NIVEL 3 — Reglas técnicas universales   → .claude/skills/, mcp-servers/
NIVEL 4 — Dominio específico            → domain-captures/
NIVEL 5 — Decisiones proyecto/momento   → decisions/ (ADRs)
```

| Nivel | Cambia con | Aplica a |
|---|---|---|
| 1 | Casi nunca (madurez filosófica) | Todos los proyectos, todos los stacks |
| 2 | Raramente (cuando aparece nuevo patrón estructural) | Todos los proyectos SaaS multi-tenant |
| 3 | Con cambios de stack (Supabase → otra DB) | Todos los proyectos del mismo stack |
| 4 | Con cada cliente nuevo | El cliente específico |
| 5 | Con cada decisión técnica concreta | El proyecto/momento específico |

## Contenido de esta carpeta

| Archivo | Contenido |
|---|---|
| `PRINCIPIOS-SOLID.md` | SOLID adaptado al contexto del Departamento (no solo OOP) |
| `PRINCIPIOS-ARQUITECTURA.md` | 25 reglas universales A1-A25 (ownership, contratos, zero trust, concurrency, explicit failure, unhappy path, rate limiting, edge protection, async, external resilience, hexagonal, observability, secrets, deployment, data lifecycle, authorization) |
| `PATRONES-CARPETAS.md` | Estructura de directorios + 6 reglas C1-C6 |
| `ANTI-PATRONES.md` | 36 anti-patterns identificados con evidencia empírica |

## Cómo usar esta carpeta

**Al diseñar un nuevo componente del Departamento**:
1. Leer `PRINCIPIOS-SOLID.md` para validar diseño
2. Leer `PRINCIPIOS-ARQUITECTURA.md` para validar fit arquitectónico
3. Leer `ANTI-PATRONES.md` para validar que no estás cometiendo errores conocidos
4. Ubicar el componente en la carpeta correcta según `PATRONES-CARPETAS.md`

**Al onboarding de un colaborador nuevo**:
- Estos 4 documentos son la base teórica
- Cubren TODO lo agnóstico de proyecto/cliente
- Niveles 4-5 los aprende por proyecto

**Al evaluar una regla nueva propuesta**:
- ¿Es agnóstica de cliente? ¿De stack? → Nivel 2 (aquí)
- ¿Aplica solo a Supabase/PostgreSQL? → Nivel 3 (skills/mcp-servers)
- ¿Es específica de Stallen? → Nivel 4 (domain-captures)
- ¿Es decisión de momento? → Nivel 5 (decisions)

## Origen de las reglas en esta carpeta

Muchas reglas fueron **destiladas del legacy SigmaControl** (proyecto anterior
en `C:\Users\Windows 11\sigmacontrol-camino-1\`) donde estaban mezcladas con
código del meta-sistema. La depuración aplicó el framework de 5 dimensiones
(coherencia, dominio, escala, contexto, evidencia) para separar:

- Lo que es **universal** (vino acá, Nivel 2)
- Lo que es **técnico del stack** (fue a `.claude/skills/`, Nivel 3)
- Lo que es **del dominio Stallen** (fue a `domain-captures/`, Nivel 4)
- Lo que es **decisión del proyecto** (fue a `decisions/`, Nivel 5)

Ver `decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md` para la decisión formal.

## Inmutabilidad relativa

Estos documentos son **relativamente inmutables**: cambian raramente, y cada
cambio debe documentarse con razón explícita. Cambios típicos válidos:

- Aparece un nuevo patrón estructural validado por 3+ proyectos
- Se descubre un anti-pattern nuevo con evidencia empírica
- Se formaliza vocabulario industrial (ej: Harness Engineering)

Cambios típicos INVÁLIDOS (NO modificar Nivel 2 por estas razones):
- "Stallen necesita X específico" → Va en Nivel 4
- "Supabase requiere Y" → Va en Nivel 3
- "Decidí cambiar el approach" → Va en ADR Nivel 5

## Relación con Harness Engineering

Esta carpeta materializa principalmente la subsystem **Instructions** del
harness según la disciplina formal (ver `decisions/ADR-006`), aunque varias
reglas tocan también **Scope**, **Verification** y **Session Lifecycle**.
Mapping detallado de cada regla A* a subsystem en `PRINCIPIOS-ARQUITECTURA.md`
sección "Mapping a Harness Engineering Subsystems".

Las otras subsystems materializadas en otras carpetas del Departamento:

- **State** → `openspec/`, claude-mem (futuro), git
- **Verification** → `mcp-servers/`, GGA, tests adversariales
- **Scope** → `.claude/skills/sigma-capture-domain/`, openspec changes, A12+A16+A17+A22
- **Session Lifecycle** → `PROTOCOLO-CONSTRUCCION-CODIGO.md`, A18+A23+A24, futura `sigma-close-session-validator`

---

Versión: 1.2 | Creado: 2026-05-15 | Última edición: 2026-05-20
Cambios v1.2 (2026-05-20): ampliado de 19 a 25 reglas A* tras 3er audit
empírico (Opción D — catálogo completo Nivel 2). Nuevas reglas A20-A25
cubren dimensiones de paradigma arquitectónico (Hexagonal), observabilidad
estructurada, secrets management, deployment safety, data lifecycle &
privacy, y authorization model. Y de 28 a 36 anti-patterns. Mapping
actualizado a SOLID y Harness Engineering Subsystems.

Cambios v1.1 (2026-05-15): ampliado de 10 a 15 reglas A* (DAO/DTO, Zero
Trust, Concurrency, Explicit Failure, Unhappy Path First) + de 19 a 24
anti-patterns. v1.2 inicial: de 15 a 19 reglas A* (Rate Limiting, Edge
Protection, Async Processing, External Resilience) + de 24 a 28 anti-patterns.
Ambos hitos consolidados acá en v1.2 final del README.
