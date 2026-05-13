# DEPARTAMENTO DE SOFTWARE

**Sistema determinístico de protocolos para construir código con IA del ecosistema cumpliendo estándar comercial robusto y duradero.**

Versión 1.0 — 2026-05-13

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

### Lo que falta construir (Roadmap)

| Sprint | Duración | Objetivo |
|---|---|---|
| 1 | 2 semanas | Stack ecosistema instalado |
| 2 | 2 semanas | MCP servers + skills migrados |
| 3-4 | 4 semanas | Tier 1 completo (SOLID + zero-trust + CI/CD + tests adversariales) |
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

## CONTACTO Y EVOLUCIÓN

Este sistema es vivo. Evoluciona con evidencia empírica.

- Cambios al protocolo → ADR formal en `decisions/`
- Patrones de dolor nuevos → catálogo meta-patrones
- Métricas de calidad → dashboard continuo

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
*Próxima revisión: tras Sprint 1 validado empíricamente*
