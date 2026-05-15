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
| `PRINCIPIOS-ARQUITECTURA.md` | 15 reglas universales A1-A15 (ownership, contratos, zero trust, concurrency, explicit failure, unhappy path, ...) |
| `PATRONES-CARPETAS.md` | Estructura de directorios + 6 reglas C1-C6 |
| `ANTI-PATRONES.md` | 24 anti-patterns identificados con evidencia empírica |

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

Esta carpeta materializa la subsystem **Instructions** del harness según
la disciplina formal (ver `decisions/ADR-006`). Las otras subsystems:

- **State** → `openspec/`, Engram, git
- **Verification** → `mcp-servers/`, GGA, tests
- **Scope** → `.claude/skills/sigma-capture-domain/`, openspec changes
- **Session Lifecycle** → `PROTOCOLO-CONSTRUCCION-CODIGO.md`, futura `sigma-close-session-validator`

---

Versión: 1.1 | Creado: 2026-05-15 | Última edición: 2026-05-15
Cambios v1.1: ampliado de 10 a 15 reglas A* (DAO/DTO, Zero Trust, Concurrency,
Explicit Failure, Unhappy Path First) y de 19 a 24 anti-patterns tras audit
empírico.
