# DEPARTAMENTO DE SOFTWARE

**Sistema determinístico de protocolos para construir código con IA del ecosistema cumpliendo estándar comercial robusto y duradero.**

Versión 1.2 — 2026-05-15 (post ADR-007: separación Framework vs Proyectos)

---

## ESTRUCTURA DEL REPOSITORIO

```
C:\DEPARTAMENTO-SOFTWARE\
│
├── FRAMEWORK universal (raíz del repo)
│   ├── CLAUDE.md, AGENTS.md, README.md, *.md       ← Nivel 1: principios
│   ├── architecture/                                ← Nivel 2: A1-A15 + 24 anti-patterns + SOLID + C1-C6
│   │   ├── PRINCIPIOS-SOLID.md
│   │   ├── PRINCIPIOS-ARQUITECTURA.md  (15 reglas A1-A15)
│   │   ├── PATRONES-CARPETAS.md        (6 reglas C1-C6)
│   │   └── ANTI-PATRONES.md            (24 anti-patterns con evidencia)
│   ├── .claude/skills/                              ← Nivel 3: skills universales
│   ├── mcp-servers/                                 ← Nivel 3: validators universales
│   ├── decisions/                                   ← Nivel 5: ADRs DEL FRAMEWORK mismo
│   ├── auditoria/                                   ← Memoria del Framework
│   ├── templates/                                   ← Templates para nuevos proyectos
│   │   └── project-skeleton/
│   ├── PROTOCOLO-*.md                               ← Protocolos universales
│   └── (otros archivos universales)
│
└── projects/                                        ← Cada proyecto en su carpeta ⭐ NUEVO (ADR-007)
    ├── stallen/                                     ← Proyecto principal (Tier 1)
    │   ├── NORTE.md, HORIZONTE.md, DEUDA-TECNICA.md, CUADERNO-BITACORA.md
    │   ├── SIGUIENTE-SESION.md, README.md
    │   ├── domain-captures/                         ← Nivel 4: dominio Stallen
    │   ├── features/                                ← Cada feature en su carpeta
    │   ├── decisions/                               ← Nivel 5: ADRs específicos Stallen
    │   ├── workspace/                               ← Código real Stallen
    │   ├── auditoria/                               ← Memoria Stallen
    │   └── .claude/skills/, .claude/agents/         ← Stallen-specific
    │
    └── (futuros proyectos: sandbox-spec-kit, otros clientes...)
```

Ver `architecture/README.md` para los 5 niveles de reglas.
Ver `decisions/ADR-007-separacion-framework-vs-proyectos.md` para la convención multi-proyecto.
Ver `templates/project-skeleton/README.md` para crear proyecto nuevo.

---

## QUÉ ES ESTO

Tres documentos canónicos que definen cómo funciona un departamento de software apalancando el ecosistema IA existente (Claude Code, Gentle AI, OpenSpec, BMAD, Engram) con una capa propia de enforcement determinístico, captura activa de dominio, polinización cruzada entre subsistemas y memoria institucional.

El sistema **no genera código por sí mismo** — fuerza que el código generado por IA cumpla políticas explícitas que se pueden saltar por descuido pero no por elección consciente.

---

## DOCUMENTOS

### 1. `DEPARTAMENTO-DE-SOFTWARE.md` — Arquitectura
Define **QUÉ** es el departamento.
- 7 principios rectores
- 12 roles especializados
- 5 plataformas del ecosistema adoptadas
- 10 componentes únicos de SigmaControl
- 5 capas técnicas (constitución, captura, orquestación, enforcement, ejecución, memoria)
- 3 tiers de madurez (comercial / durabilidad / vendible público)

### 2. `PROTOCOLO-CONSTRUCCION-CODIGO.md` — Protocolo
Define **CÓMO** se construye código paso a paso.
- 12 pasos secuenciales obligatorios
- 4 capas de enforcement (soft → medium → hard → maximum)
- Cada paso con inputs, outputs, validadores, criterios de "hecho", gates
- Reglas globales (R-0 a R-4)
- Sistema de excepciones con ADR

### 3. `SISTEMA-DE-TRABAJO.md` — Manual operativo
Define **el DÍA-A-DÍA** del departamento.
- 4 estaciones de trabajo (Feature / Bug Fix / Refactor / Spike)
- Workflows completos con timing
- Interacción humano-IA-sistema
- Métricas de calidad
- Onboarding de nuevos miembros
- Evolución del sistema
- Herramientas por tipo de tarea

---

## CÓMO LEER LOS DOCUMENTOS

| Si querés... | Leé primero |
|---|---|
| Entender la visión completa | `DEPARTAMENTO-DE-SOFTWARE.md` |
| Saber cómo se construye una feature | `PROTOCOLO-CONSTRUCCION-CODIGO.md` |
| Empezar a trabajar mañana | `SISTEMA-DE-TRABAJO.md` |
| Onboardear gente nueva | Los 3, en orden |
| Decidir si adoptar este sistema | `DEPARTAMENTO-DE-SOFTWARE.md` sección 6 (aportes únicos) |
| Validar que entiendo el protocolo | `PROTOCOLO-CONSTRUCCION-CODIGO.md` sección "Pasos del Protocolo" |

---

## LOS 5 NIVELES DE REGLAS

El Departamento separa explícitamente 5 niveles de reglas para no mezclar
preocupaciones de distinto alcance (formalizado en ADR-006):

| Nivel | Lugar | Cambia | Aplica a |
|---|---|---|---|
| 1 — Principios filosóficos | CLAUDE.md, AGENTS.md | Casi nunca | Todos los proyectos, stacks |
| 2 — Arquitectura universal | `architecture/` | Raramente | Cualquier SaaS multi-tenant |
| 3 — Reglas técnicas universales | `.claude/skills/`, `mcp-servers/` | Con cambios de stack | Mismo stack (Supabase) |
| 4 — Dominio específico | `domain-captures/` | Por cliente nuevo | Cliente específico |
| 5 — Decisiones proyecto/momento | `decisions/` (ADRs) | Por decisión | Proyecto/momento |

**Beneficio clave**: tomar un cliente nuevo NO requiere modificar Niveles 1-3.
Solo agregás Nivel 4 (domain-capture) y Nivel 5 (ADRs específicos).

---

## ESTADO ACTUAL (Mayo 2026)

### Lo que ya está implementado (en SigmaControl Python legacy)
- 7 principios rectores documentados
- Validadores: R01-R15, G1-G33, FG1-FG14
- Patcher determinístico con 47/47 tests
- ADN Fase 1 (dominio + modulos_custom) validada en 2 proyectos reales
- Tubería bidireccional con fix microsegundos
- Catálogo meta-patrones (7 patrones registrados)
- 1 polinización formal validada (G11A → R15)
- Tests adversariales con 4 dominios sintéticos
- Protocolo de cierre disciplinado (9 pasos)

### Lo que está completado (Sprint 1)

- ✅ Stack ecosistema instalado y validado (Claude Code 2.1.141, Gentle AI 1.28.3, GGA, Engram 1.15.11, Go)
- ✅ CLAUDE.md + AGENTS.md v1.1 (32 reglas)
- ✅ 14 commits con disciplina Conventional Commits
- ✅ OpenSpec inicializado con rules alineadas a 7 principios
- ✅ Validación empírica E2E del workflow SDD
- ✅ Skill sigma-capture-domain v1.0
- ✅ ADRs 001-005 + ADR-006 (niveles de reglas + SOLID)
- ✅ Estructura de carpetas según ADR-006 (`architecture/`, `mcp-servers/`)

### Lo que falta construir (Roadmap)

| Sprint | Duración | Objetivo |
|---|---|---|
| 1 | 2 semanas | ✅ Stack ecosistema + fundamentos |
| 2 | 2 semanas | MCP servers (sigma-validators-r + sigma-close-session-validator) + 10 skills nuevas |
| 3-4 | 4 semanas | CI/CD + staging + tests adversariales + observability (alineados Tier 1) |
| 5 | 1 semana | Validación empírica sobre Stallen feature real |
| 6-8 | 6 semanas | Tier 2 (durabilidad: stories, PRDs, ADRs, métricas) |
| 9-12 | 8-12 semanas | Tier 3 (empaquetamiento como producto vendible) |

**Total horizonte para producto vendible público: ~6 meses.**

---

## PRINCIPIOS RECTORES (versión corta)

1. **Python traza el camino → IA lo recorre → Python verifica**
2. **3 capas: preventiva → verificable → correctiva**
3. **Dominio-first: captura activa antes de código**
4. **Auto-fix > finding cuando es inequívoco**
5. **Polinización cruzada entre subsistemas estructuralmente similares**
6. **Descubrir antes de ejecutar: código vivo especifica el scope**
7. **Meta-producto recursivo: toda entidad productiva merece ambiente anti-degradación**

---

## STACK TECNOLÓGICO

**Plataformas del ecosistema (adoptar, no construir)**:
- Claude Code / Codex
- Gentle AI v1.27+
- OpenSpec
- BMAD Method v6+
- Engram (memoria persistente)

**Capa propia (IP del Departamento)**:
- Validadores backend (R01-R15, G1-G33) específicos Postgres/Supabase
- Validadores frontend (FG1-FG14) específicos React/TSX
- Patcher determinístico (auto-fix con 725× mejor performance que LLM-feedback)
- ADN multi-capa (5 fases de captura)
- Tubería bidireccional
- Catálogo meta-patrones + ritual polinización
- 7 principios rectores formalizados

---

## NAVEGAR EL REPOSITORIO

**Para entender la visión completa**:
1. `CLAUDE.md` — principios filosóficos
2. `architecture/README.md` — niveles de reglas
3. `DEPARTAMENTO-DE-SOFTWARE.md` — arquitectura general

**Para entender cómo trabajar día-a-día**:
1. `SISTEMA-DE-TRABAJO.md` — manual operativo
2. `PROTOCOLO-CONSTRUCCION-CODIGO.md` — protocolo de construcción
3. `architecture/PRINCIPIOS-SOLID.md` — SOLID adaptado
4. `architecture/ANTI-PATRONES.md` — qué NO hacer

**Para entender decisiones específicas**:
- `decisions/` — ADRs por orden cronológico
- ADR-006 — niveles de reglas y SOLID (más reciente y estructurante)

**Para empezar Sprint 2**:
- `decisions/ADR-005-cierre-sprint-1.md` — plan original Sprint 2
- `decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md` — refinamiento del plan
- `mcp-servers/README.md` — guía para crear los MCP servers nuevos

---

## CONTACTO Y EVOLUCIÓN

Este sistema es vivo. Evoluciona con evidencia empírica.

- Cambios al protocolo → ADR formal en `decisions/`
- Patrones de dolor nuevos → catálogo meta-patrones
- Métricas de calidad → dashboard continuo
- Cambios a `architecture/` (Nivel 2) → requieren ADR con evidencia empírica 2+ proyectos

---

## DIRECCIÓN ESTRATÉGICA: HACIA UN FRAMEWORK

Este sistema está diseñado para eventualmente convertirse en **framework público** (en la categoría de BMAD Method, OpenSpec, Gentle AI) cuando esté validado empíricamente sobre proyecto productivo real (Stallen).

**Tipo de framework objetivo**: Híbrido (metodología + tools instalables).
**Posicionamiento tentativo**: Especialización backend disciplinado con enforcement determinístico — complemento al ecosistema, no competidor frontal.
**Licencia tentativa**: Open core (gratis básico + premium pago para validadores específicos y soporte).

### Roadmap de transición a framework

| Fase | Duración | Output |
|---|---|---|
| Pre-framework | Hoy | 3 docs fundacionales + commit local (este estado) |
| Sprint 1-5 | 9 semanas | Stack instalado + IP único migrado + Tier 1 validado sobre Stallen |
| Sprint 6-8 | 6 semanas | Tier 2: durabilidad (stories, PRDs, ADRs, métricas) |
| Pre-launch | 4 semanas | Packaging v0.1: naming definitivo, estructura repo, docs públicas, ejemplos |
| Launch privado | 2 semanas | Repo público early-access + 3-5 beta testers |
| Launch público | Variable | Anuncio público + comunidad + contenido |

**Total horizonte: ~6 meses hasta framework v0.1 lanzado.**

### Decisiones estratégicas a definir antes de Sprint 9

- **Naming definitivo** del framework (tentativos: sigma-protocol, departamento, disciplined-ai)
- **Posicionamiento final** vs ecosistema (complemento especializado vs alternativa)
- **Licencia** elegida (MIT / Apache 2.0 / Open core / Comercial cerrado)
- **Estructura del repo público** y modelo de distribución (npm, pip, GitHub releases)

### Principio rector hasta Sprint 8

**Validación primero, packaging después.** Hasta tener Tier 1 + Tier 2 completos con evidencia empírica sobre Stallen, el foco NO es framework público. Anti-patrón a evitar: empaquetar antes de validar (causa muerte por falta de tracción, ver casos similares).

---

## NEXT STEPS

Si estás empezando ahora:

1. **Leer los 3 documentos en orden** (~2 horas total)
2. **Validar la visión**: ¿Es esto lo que querés construir?
3. **Sprint 1**: Instalar el stack del ecosistema
4. **Sprint 2**: Migrar primer componente único (validadores R01-R15 como MCP server)
5. **Sprint 5**: Validación empírica sobre feature real (Stallen)

Si ya tenés SigmaControl Python legacy funcionando:
- Mantener legacy en producción para Stallen actual
- Construir Departamento en paralelo
- Migrar progresivamente cuando cada componente esté validado en Departamento

---

*Versión 1.0 fundacional — 2026-05-13*
*Versión 1.1 — 2026-05-15 (post ADR-006: niveles de reglas + SOLID)*
*Próxima revisión: tras Sprint 2 validado empíricamente*
