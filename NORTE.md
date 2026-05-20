# NORTE — Departamento de Software (Framework)

> **Propósito**: visión del Framework como producto independiente. Se lee
> ~1 vez al mes o al arrancar un hito grande del framework mismo. NO se lee
> en cada sesión.
>
> Este NORTE es del **Framework Departamento** (universal, agnóstico de
> cualquier proyecto). Para NORTEs específicos de proyectos que consumen
> el framework, ver `projects/<slug>/NORTE.md`.

**Versión**: 0.1 (draft inicial con placeholders)
**Última actualización**: 2026-05-15
**Estado**: ⚠️ PENDIENTE COMPLETAR — varios placeholders necesitan decisión de Julián

---

## Qué es el Departamento de Software

El Departamento de Software es un **framework de gobernanza arquitectónica
para construir software con agentes IA** cumpliendo estándar comercial
robusto y duradero.

NO es:
- Un tool IDE
- Un wrapper de un LLM específico
- Un workflow rígido
- Un producto SaaS

SÍ es:
- **Conjunto de protocolos** versionados en markdown
- **Capa de gobernanza** que cualquier agente IA puede consumir
- **Calibración específica** para construcción de software con IA
- **Framework reusable** entre proyectos

### Composición técnica (5 niveles — ADR-006)

```
Nivel 1: Filosofía — 7 principios rectores
Nivel 2: Arquitectura — 15 reglas A1-A15 + 24 anti-patterns + SOLID + C1-C6
Nivel 3: Tooling — skills, subagents, MCP servers
Nivel 4: Dominio — capturado por proyecto consumidor
Nivel 5: Decisiones — ADRs específicos
```

### Estructura física (ADR-007)

```
Framework universal (raíz del repo)
└── projects/<slug>/  ← cada proyecto que consume el framework
```

### Característica fundamental (ADR-008)

**Agent-agnostic**: funciona con Claude Code, Cursor, Codex CLI, Gemini CLI,
Antigravity, GPT/ChatGPT, y otros agentes IA emergentes. El framework
sobrevive a cualquier cambio de proveedor LLM.

---

## Por qué existe el Departamento

### Problema que resuelve

Los **vibe coders** (no programadores profesionales, pero que construyen
software real con IA del ecosistema) enfrentan tensión sistémica:

1. **Productividad IA atractiva**: la IA permite construir mucho rápido
2. **Calidad/coherencia/escala vulnerables**: sin defensas arquitectónicas, el código IA-generated:
   - Acumula deuda técnica silenciosa
   - Viola invariantes del dominio
   - Genera bugs estructurales (multi-tenancy leaks, race conditions, etc.)
   - Pierde coherencia entre features
   - Se vuelve inmantenible al crecer

El Departamento resuelve esto con **3 capas de defensa**:
- **PREVENTIVA**: principios + reglas + anti-patterns documentados
- **VERIFICABLE**: skills + validators + tests adversariales
- **CORRECTIVA**: auto-fix cuando determinístico, finding sino

### Diferenciador vs alternativas

| Alternativa | Qué hace bien | Qué le falta |
|---|---|---|
| **GitHub Spec Kit** | Workflow SDD oficial, 30+ integraciones | Sin gobernanza arquitectónica específica para vibe coders |
| **OpenSpec** | SDD lightweight | Mismo gap + comunidad menor |
| **Antigravity Awesome Skills** | 1,460+ skills cross-agent | Sin filosofía operativa unificada |
| **VoltAgent Subagents** | 100+ especialistas | Sin capa de gobernanza arquitectónica |
| **Awesome Design.md** | Sistemas de diseño | Solo capa visual, no arquitectónica |
| **Construir desde cero** | Customización total | Costo de tiempo + sin validación |

**El Departamento es la capa que falta**: gobernanza arquitectónica universal
que orquesta el ecosistema y se calibra para vibe coders Tier 1.

### Estado de la industria (2026)

- **Spec Kit lanzado** (Sept 2025) — 98.5k stars en 8 meses, evolución rápida
- **Antigravity (Google) lanzada** — IDE con Gemini 3, ecosystem cross-agent
- **MCP estandarizado** — Anthropic, Cursor, Codex, Gemini lo adoptan
- **AGENTS.md emergente** — estándar cross-LLM para reglas
- **awesome-design-md** — DESIGN.md de Google Stitch popularizado

El ecosistema es **rico pero fragmentado**. El Departamento aporta cohesión.

---

## Para quién es el Departamento

⚠️ **PLACEHOLDER — Julián decide audiencia primaria**

Opciones tentativas (elegir una o combinar):

### Opción A: Personal multi-proyecto

- Solo Julián Vargas
- Aplicado a Stallen (cuando reaparezca) + proyectos personales futuros
- No se comparte públicamente
- Sin presión de UX para terceros

### Opción B: Vibe coders Tier 1 generalizado

- Personas como Julián: no programadores profesionales pero construyen software comercial
- Eventualmente compartible (open source, blog posts, tutoriales)
- Requiere documentación amplia para onboarding

### Opción C: Profesionales individuales

- Programadores que usan IA pero necesitan defensas arquitectónicas
- Mercado más amplio pero más competitivo

### Opción D: Equipos pequeños (2-10 personas)

- Para equipos pequeños construyendo SaaS
- Requiere features de colaboración no contempladas

### Opción E: Combinación

Por defecto **Personal multi-proyecto** ahora, **Vibe coders Tier 1** eventualmente
(si el framework prueba ser útil con Stallen + otros proyectos personales).

---

## Stack tecnológico del framework

### Lo que el framework provee

- **Documentación**: markdown como formato canónico
- **Versionado**: git + GitHub
- **Tooling agnóstico**: MCP filesystem (estándar cross-agent)
- **Code review**: GGA (provider configurable: claude, openai, gemini)
- **Memoria entre sesiones**: `.md` cortos (`auditoria/`, `SIGUIENTE-SESION.md`)
- **Estructura**: convenciones de carpetas (ADR-007)
- **Workflow operativo**: ⚠️ pendiente decisión (Spec Kit / OpenSpec / propio)
- **Memoria persistente avanzada**: ⚠️ Engram (bloqueado por SAC, en WSL)

### Lo que el proyecto consumidor aporta

- Su stack tecnológico específico (ej: Supabase + Vercel para Stallen)
- Su dominio capturado
- Sus decisiones técnicas específicas (en `projects/<slug>/decisions/`)
- Su código en `projects/<slug>/workspace/`

---

## Stakeholders

- **Owner**: Julián Vargas
- **Audiencia primaria**: ⚠️ PLACEHOLDER (ver "Para quién" arriba)
- **Contribuidores futuros**: ⚠️ PLACEHOLDER (¿open source eventualmente?)
- **Validators**: ⚠️ PLACEHOLDER (¿otros vibe coders revisarían el framework?)

---

## Tier de calibración del framework

⚠️ **PLACEHOLDER — Julián decide**

El framework heredó **Tier 1 commercial robust** del ADR-004 (calibrado para
Stallen). Pero si Stallen ya no es el driver principal, vale re-evaluar:

### Opción A: Mantener Tier 1 commercial robust (default)

- Apropiado para SaaS comerciales reales
- Defensas arquitectónicas estrictas
- Aplica a Stallen futuro + otros proyectos comerciales

### Opción B: Tier 2 (más laxo)

- Para proyectos personales/experimentales sin presión comercial
- Defensas más relajadas
- Más rápido para iterar

### Opción C: Multi-tier (framework soporta múltiples calibraciones)

- Tier 0: prototipo desechable
- Tier 1: producción comercial robust (default actual)
- Tier 2: experimentación seria
- El proyecto consumidor elige su tier en `projects/<slug>/decisions/`

### Recomendación tentativa

**Opción C** (multi-tier). Razones:
- Framework reusable debería soportar diferentes contextos
- Tier 1 sigue siendo el default
- Otros tiers se agregan cuando aparezca el caso

Pero decisión es de Julián.

---

## Criterios de éxito del framework

⚠️ **PLACEHOLDER — Julián decide cuándo el framework "está listo"**

Sin Stallen como métrica concreta ("feature 1 sale bien"), necesitamos
criterios objetivos del framework como producto.

Opciones a combinar:

### Criterio técnico (cuándo está "completo")

- [ ] Framework permite construir un caso simple end-to-end con calidad Tier 1
- [ ] 5 niveles formalizados y operativos (✅ logrado en Sprint 2 Día 1-2)
- [ ] Multi-proyecto funcional (✅ logrado en Sprint 2 Día 2)
- [ ] Cross-LLM validado empíricamente con ≥2 agentes (⏳ Sprint 3+)
- [ ] Workflow operativo documentado (Nivel 0 — ⏳ pendiente decisión Spec Kit)
- [ ] Sistema memoria entre sesiones validado (✅ logrado)
- [ ] Protocolos inicio/cierre adaptados (⏳ pendiente)

### Criterio de uso (cuándo está "útil")

- [ ] Aplicado a 1 proyecto real (Stallen feature 1 — diferido)
- [ ] Aplicado a 2+ proyectos sin re-arquitectar
- [ ] Reduce tiempo de arranque de proyecto nuevo a <1 día

### Criterio de reusabilidad (cuándo está "compartible")

- [ ] Otro vibe coder podría arrancar siguiendo solo la documentación
- [ ] Tutorial básico existe
- [ ] FAQ con casos comunes
- [ ] Ejemplo funcional (`projects/example-*`)

### Criterio cross-LLM (cuándo es "agnóstico de verdad")

- [ ] Funciona con Claude Code (✅ actual)
- [ ] Funciona con Cursor (⏳ pendiente validación Sprint 3+)
- [ ] Funciona con Codex CLI (⏳ pendiente)
- [ ] Funciona con al menos un agente más (Gemini, Antigravity, etc.)

### Recomendación tentativa

Combinación de **Criterio técnico** (mínimo viable) + **Criterio de uso**
(1 proyecto real aplicado) como hito de "framework v1.0 estable".

Después: Reusabilidad + Cross-LLM como hitos posteriores.

---

## Decisiones fundamentales (no negociables)

Estas son las decisiones que el framework NO altera sin razón estructural
extremadamente fuerte:

1. **7 principios rectores** (Nivel 1) — filosofía operativa
2. **15 reglas A1-A15 universales** (Nivel 2) — para SaaS multi-tenant
3. **24 anti-patterns documentados** con evidencia empírica
4. **SOLID adaptado + C1-C6** (organización)
5. **Framework agent-agnostic** (ADR-008) — NO casarse con un LLM
6. **5 niveles claros** (ADR-006) — separación de concerns en reglas
7. **Multi-proyecto** (ADR-007) — Framework universal + proyectos consumidores
8. **Audit empírico recursivo** — descubrir antes de ejecutar, en TODO
9. **Anti-paternalismo** — no proyectar sobre el usuario
10. **Markdown como formato canónico** — versionable, agent-agnostic

Cualquier cambio a estas decisiones requiere ADR explícito con razonamiento
empírico (no preferencia estética).

---

## Restricciones

### Tiempo

- ⚠️ PLACEHOLDER — ¿cuánto tiempo/semana se dedica al framework?
- Estimación tentativa: 4-8 hs/semana de Julián

### Presupuesto

- ⚠️ PLACEHOLDER — ¿hay budget para tools del ecosistema?
- Hoy: $0 (todo lo adoptado es free/open source)
- Posibles costos futuros: hosting docs, comercial tools

### Equipo

- Hoy: Julián + IA del ecosistema (Claude, GPT, etc.)
- ⚠️ PLACEHOLDER — ¿se invitará contribuidores eventualmente?

### Compliance / legal

- Framework markdown — sin compliance específico
- Si se vuelve open source: licencia a decidir
- Si se vuelve comercial: términos de uso

### Stack lock-in aceptable

- ✅ Markdown universal
- ✅ Git universal
- ⚠️ MCP estándar emergente (acceptable)
- ⚠️ Spec Kit (si se adopta) — license MIT, código fuente disponible

---

## Driver del framework

⚠️ **PLACEHOLDER — Julián decide qué motiva construir esto**

Opciones (elegir una o combinar):

### Driver A: Necesidad personal (intrínseco)

- Construir Stallen (eventual) + otros proyectos personales bien
- Sin presión externa
- Mantenido mientras Julián tenga proyectos que lo consuman

### Driver B: Contribución a la comunidad (extrínseco)

- Vibe coders necesitan algo así, no existe formalizado
- Eventualmente open source / blog posts
- Mantenido si la comunidad lo encuentra útil

### Driver C: Posible producto comercial (extrínseco económico)

- Vender el framework como SaaS / consultoría / curso
- Requiere validación con clientes reales
- Mantenido si genera revenue

### Driver D: Experimento intelectual (extrínseco intelectual)

- Por construir algo arquitectónicamente bien
- Validación de principios de Harness Engineering en práctica
- Mantenido mientras sea intelectualmente interesante

### Recomendación tentativa

**Driver A** (necesidad personal) como primario inicial. Si el framework
prueba ser útil a Julián, considerar **Driver B/C** después con evidencia
empírica.

---

## Criterio de stop / pivot

¿Cuándo el framework dejaría de tener sentido?

⚠️ **PLACEHOLDER — Julián decide**

Opciones tentativas:

### Stop A: Framework muy complejo de mantener

Si construir/mantener el framework toma más tiempo del que ahorra → stop.

### Stop B: Ecosistema absorbe la función del framework

Si Spec Kit + extensions + Supabase Agent Skills cubren TODO lo que el
framework hace → considerar adoptar wholesale y eliminar el framework
propio.

### Stop C: Julián deja de hacer proyectos personales

Si no hay proyectos consumiendo el framework, no tiene sentido seguir.

### Stop D: Framework no genera valor empírico

Si después de aplicar el framework a 2-3 proyectos, NO mejora la calidad/
velocidad/coherencia comparado con NO usarlo → considerar pivot o stop.

### Pivot escenarios

- **Pivot 1**: si Spec Kit absorbe ~80% del valor → renombrar el framework
  como "Spec Kit + opiniones arquitectónicas de Julián"
- **Pivot 2**: si emerge mejor approach (cualquiera) → considerar abandonar
  por algo superior
- **Pivot 3**: si Stallen + futuros proyectos NO necesitan framework formal
  → reducir framework a "documento de buenas prácticas"

---

## Estado actual del framework (al cerrar 2026-05-15)

### Completado

- ✅ Nivel 1 (Filosofía) — 7 principios rectores formalizados
- ✅ Nivel 2 (Arquitectura) — A1-A15 + 24 anti-patterns + SOLID + C1-C6
- ✅ Nivel 5 (Decisiones) — ADRs 001-008 documentados
- ✅ Sistema memoria entre sesiones — `.md` cortos validados empíricamente
- ✅ Multi-proyecto formalizado — ADR-007
- ✅ Cross-LLM formalizado — ADR-008 + `docs/AGENT-INTEGRATION.md`
- ✅ Templates para nuevos proyectos — `templates/project-skeleton/`

### En progreso / próximas sesiones

- ⏳ Nivel 3 (Tooling) — skills + subagents + MCP servers (Sprint 2 T2 original, en re-evaluación)
- ⏳ Engram operativo en WSL Ubuntu (T0 próxima sesión)
- ⏳ Sandbox Spec Kit validación empírica (T1 próxima sesión)
- ⏳ Decisión adopción Spec Kit (T2 → ADR-009)
- ⏳ Workflow operativo Nivel 0 (depende de T2)
- ⏳ Protocolos adaptados (INICIO + CIERRE del Departamento)

### Diferido (vuelve después)

- ⏸️ Stallen como proyecto consumidor — diferido hasta que el framework esté maduro
- ⏸️ `projects/stallen/` → renombrar a `projects/example-stallen/` (caso de uso hipotético)

### Pendiente decisión de Julián

- ⚠️ Audiencia primaria (Para quién)
- ⚠️ Tier de calibración (Tier 1 / multi-tier)
- ⚠️ Criterios de éxito específicos
- ⚠️ Driver (personal / comunitario / comercial / intelectual)
- ⚠️ Criterio de stop / pivot

---

## Acciones pendientes para completar este NORTE

- [ ] Julián completa los placeholders ⚠️ (en entrevista o asincrónico)
- [ ] Versionar v0.1 → v1.0 cuando completo
- [ ] Archivar versiones anteriores en `auditoria/historia-estrategica/` cuando haya pivots

---

## Versionado

- **v0.1** (2026-05-15) — INICIAL draft con placeholders. Post decisión de Julián
  de enfocar solo en el framework (apartar Stallen temporalmente).
- **v1.0** (futuro) — Versión completa tras llenar placeholders.
- **v2.0+** (futuro) — Si hay pivots estratégicos (driver cambia, audiencia cambia, etc.)

---

## Notas para próximo Claude

- Este NORTE es del **Framework Departamento**, NO de un proyecto específico
- Cualquier decisión del framework debe alinearse con este NORTE
- Si una decisión NO se alinea → o se justifica desviarse (con ADR), o se revisa el NORTE
- Aplicación del 7° principio rector: el framework merece su propio NORTE
