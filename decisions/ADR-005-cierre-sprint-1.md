# ADR-005: Cierre oficial del Sprint 1

**Status**: Decidido
**Fecha**: 2026-05-14
**Decisor**: Julián Vargas
**Contexto**: Cierre formal de la primera iteración del Departamento de Software

---

## Contexto

Sprint 1 del Departamento de Software ejecutado durante 2026-05-13/14 con objetivo: instalar el ecosistema commodity (Claude Code + Gentle AI + Engram + GGA + OpenSpec), establecer documentación arquitectónica fundacional, y validar empíricamente que el sistema completo opera sobre el repo.

Este ADR documenta el cierre oficial, los outcomes verificables, las decisiones tomadas durante el sprint, las deudas técnicas anotadas, y el plan para Sprint 2.

---

## Decisión: Sprint 1 declarado CERRADO al 100%

Cierre formal basado en evidencia empírica, no en declaración aspiracional.

### Criterio de cierre

El Sprint 1 se considera cerrado cuando se cumplen TODOS los siguientes (todos verificados a 2026-05-14):

1. ✅ Stack ecosistema instalado y operativo
2. ✅ Documentación arquitectónica completa y commiteada
3. ✅ Validación empírica E2E del workflow ejecutada con veredicto PASS (o PASS-WITH-WARNINGS)
4. ✅ Working tree limpio en main
5. ✅ ADRs principales documentados
6. ✅ Plan para Sprint 2 explícito en docs versionados

---

## Outcomes del Sprint 1

### Días ejecutados

| Día | Objetivo | Resultado |
|---|---|---|
| 1 | CLAUDE.md + workspace + 3 docs fundacionales | ✅ Completo (commit 96458a0, e895d2c) |
| 2 | Validación Claude Code + Agent View | ✅ Completo (Opus 4.7, 1M context, 14 tools Engram) |
| 3 | Stack ecosistema (Go + Engram + GGA + Gentle AI) | ✅ Completo (commit fe23d06) |
| 4 | OpenSpec con rules custom alineadas a 7 principios | ✅ Completo (commit dbd210b, da19adb) |
| 5 | Validación empírica E2E del workflow SDD | ✅ Completo (commit 8bca811, PASS-WITH-WARNINGS) |

### Componentes instalados y validados

| Componente | Versión | Estado |
|---|---|---|
| Claude Code | 2.1.141 | Validado (Agent View, lee CLAUDE.md) |
| Opus 4.7 | con 1M context | Activo |
| Sonnet 4.6 | — | Disponible para sub-agents |
| Go | 1.26.3 | Instalado vía Scoop |
| Scoop | última | Package manager |
| Gentle AI | 1.28.3 | Stack completo sincronizado |
| GGA | v2.8.1 | Pre-commit hook activo |
| Engram | 1.15.11 | 14 MCP tools expuestas |
| OpenSpec | (skills SDD) | Workflow E2E validado |

### Artifacts documentales producidos

```
C:\DEPARTAMENTO-SOFTWARE\
├── CLAUDE.md                                ← Constitución (7 principios)
├── README.md                                ← Visión + dirección estratégica
├── DEPARTAMENTO-DE-SOFTWARE.md              ← Arquitectura completa (10 dimensiones)
├── PROTOCOLO-CONSTRUCCION-CODIGO.md         ← 12 pasos + reglas R-0 a R-6
├── SISTEMA-DE-TRABAJO.md                    ← Manual operativo + plan incidentes
├── AGENTS.md                                ← Reglas para GGA v1.0
├── .gga                                     ← Config del code reviewer
├── decisions/
│   ├── README.md                            ← Convención ADRs
│   ├── ADR-004-calibracion-nivel-comercial.md
│   └── ADR-005-cierre-sprint-1.md           ← Este ADR
├── docs/
│   └── MEMORIA-INTELIGENTE-Y-CIERRE.md      ← ADRs 001-003 + diseño MCP cierre
├── openspec/
│   ├── config.yaml                          ← Rules custom alineadas a 7 principios
│   ├── README.md
│   ├── specs/README.md
│   └── changes/
│       ├── README.md
│       ├── archive/README.md
│       └── validate-sdd-workflow/           ← Validación empírica (6 artifacts)
└── workspace/                               ← Para Sprint 2+
```

### Métricas del Sprint 1

**Documentación**:
- ~3,500 líneas de documentación arquitectónica versionada
- 11 commits en main, working tree limpio
- 5 ADRs formalizados (004 + 005 archivos individuales; 001-003 embebidos en docs/)

**Validación empírica (Día 5)**:
- 226.5k tokens consumidos en validación E2E
- 22m 12s wall clock
- 106 tool calls
- Veredicto: **PASS-WITH-WARNINGS** (0 CRITICAL, 2 WARNING, 3 SUGGESTION)
- 13/13 tasks empíricas PASS

**Costo monetario aproximado**:
- Sprint 1 completo: ~$3-5 USD en uso de API
- Plan Pro $20/mes: cubrió todo holgadamente

---

## Decisiones arquitectónicas tomadas durante el Sprint 1

### ADR-001 (formalizado en docs/MEMORIA-INTELIGENTE-Y-CIERRE.md)
Adopción de Engram para memoria operativa de agentes.

### ADR-002 (formalizado en docs/MEMORIA-INTELIGENTE-Y-CIERRE.md)
Rechazo de vectorización (vector DBs) para memoria institucional. FTS5 alcanza.

### ADR-003 (formalizado en docs/MEMORIA-INTELIGENTE-Y-CIERRE.md)
Diseño del MCP server `sigma-close-session-validator` para optimizar protocolo de cierre 60-80%.

### ADR-004 (decisions/ADR-004-calibracion-nivel-comercial.md)
Calibración a Nivel 2 comercial profesional en 12 semanas. NO producto vendible. NO Nivel 3 preventivo.

### Decisiones implícitas (no formalizadas como ADR pero efectivas):

- **D-IMPLICIT-1**: Apalancarse en ecosistema (Gentle AI + Engram + GGA + OpenSpec) en vez de construir framework propio
- **D-IMPLICIT-2**: NO instalar OpenSpec CLI standalone (fission-ai). Usar skills SDD de Gentle AI con la misma convención
- **D-IMPLICIT-3**: NO implementar BMAD Method. Solapamiento del 80% con stack actual, costo de migración alto, no hay dolor empírico que lo justifique. Revisitable post-Sprint 5
- **D-IMPLICIT-4**: artifact_store en OpenSpec configurado como `hybrid` (Engram + filesystem) para aprovechar búsqueda FTS5 + lectura humana
- **D-IMPLICIT-5**: Coordinación entre agentes Claude requiere protocolo explícito (lección del Día 4 con sesión paralela)

---

## Deudas técnicas anotadas

### Tier crítico (Sprint 2 Día 1)

- **DEUDA-DIA3-01**: Hook `UserPromptSubmit` de Gentle AI falla por path con espacios (`C:\Users\Windows 11\`). Mensaje "non-blocking" pero indica config rota. Investigar y resolver.
- **DEUDA-DIA3-02**: `.gga` FILE_PATTERNS hardcoded a `*.ts,*.tsx,*.js,*.jsx`. Para Stallen (Python+SQL) hay que ajustar antes de empezar a generar código.
- **DEUDA-AGENTS-1**: AGENTS.md v1.0 tiene reglas mínimas. Ampliar con reglas específicas Python/SQL/Supabase antes del primer commit de código real.

### Tier alto (Sprint 2-3)

- **DEUDA-ADR-MIGRACION**: ADRs 001-003 viven embebidos en `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md`. Migrar a archivos individuales en `decisions/` para consistencia con ADR-004 y ADR-005.
- **DEUDA-VERIFY-1**: REQ-WF-008 (idempotencia del workflow SDD) no se ejercitó en el Día 5. Sub-change `test-sdd-idempotency` que corra dos veces la misma phase.
- **DEUDA-VERIFY-2**: Paralelismo de spec+design no ejercitado. Requiere lock protocol para state.yaml antes de habilitar.

### Tier medio (Sprint 2-4)

- **DEUDA-AF-1 a AF-4**: 4 auto-fix candidates documentados en `validate-sdd-workflow/design.md` para MCP server `sdd-reconcile` (aplicación del 4° principio).
- **DEUDA-SDD-VERIFY-COSTO**: `sdd-verify` consumió 38% de tokens del workflow (87k). Considerar caching de file reads para validaciones recurrentes.

### Tier bajo (post-Sprint 5)

- **DEUDA-COMMIT-MULTILINEA**: commits con `git commit -m "..."` multilinea en PowerShell tienen riesgo de generar archivos basura. Documentar workaround o usar `git commit -F`.
- **DEUDA-COORDINACION-AGENTES**: meta-patrón "coordinación entre agentes Claude operando concurrentemente" candidato a catálogo cuando arranque.

---

## Plan Sprint 2 — Construcción de MCP servers propios

### Objetivo del Sprint 2

Migrar la IP única de SigmaControl (validadores R/G/FG, patcher, capturar_adn) al ecosistema actual como **MCP servers propios + skills**. Validar empíricamente que la migración mantiene la disciplina del sistema original.

### Duración estimada: 2 semanas

### Pre-requisitos antes de empezar

1. Resolver deudas Tier crítico (DEUDA-DIA3-01, DEUDA-DIA3-02, DEUDA-AGENTS-1)
2. Ajustar `.gga` para Python+SQL
3. Ampliar `AGENTS.md` con reglas específicas Stallen
4. Crear branch protection en main (opcional pero recomendado)

### Backlog Sprint 2

**Tarea 1 — Captura de dominio del Departamento** (Sprint 2 Día 1-2)
- Crear skill `sigma:capture-domain` (3° principio: dominio-first)
- Aplicarla al propio Departamento como primera validación
- Persistir dominio capturado en `decisions/ADR-006-dominio-departamento.md`

**Tarea 2 — Primer MCP server: sigma-validators-r-mvp** (Sprint 2 Día 3-7)
- Crear change OpenSpec: `add-validator-r-mvp`
- Migrar 1-3 validators R del SigmaControl original (R01, R02, R03)
- Construir MCP server con tools `validate_r01`, `validate_r02`, `validate_r03`
- Tests adversariales para cada validator (Hypothesis)
- Validar end-to-end con feature dummy de Stallen

**Tarea 3 — MCP server sigma-close-session-validator** (Sprint 2 Día 8-10)
- Implementar según diseño en `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md` § 3
- 7 tools: close_start, close_record_step, close_polinization_check, close_verify_cleanup, close_audit_status, close_git_backup, close_finalize
- Validar empíricamente con cierre real al final del Sprint 2

**Tarea 4 — Migración ADRs 001-003** (Sprint 2 Día 11)
- Extraer ADRs 001, 002, 003 de `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md` a archivos individuales en `decisions/`
- Actualizar README de decisions/ con índice completo

**Tarea 5 — Cierre Sprint 2** (Sprint 2 Día 12)
- Aplicar el nuevo MCP server `sigma-close-session-validator` para cerrar este sprint
- Validar empíricamente el ahorro de tokens (objetivo: 60-80% menos vs cierre manual)

### Métricas de éxito Sprint 2

- 3-5 validators R migrados y operativos como MCP tools
- Skill `sigma:capture-domain` funcional y aplicada al menos una vez
- MCP server `sigma-close-session-validator` operativo
- Tokens del próximo cierre ≤ 7k (vs ~15-30k estimado manual)
- Cero meta-patrones duplicados detectados
- 100% de gaps detectados por `close_audit_status`

### Riesgos identificados Sprint 2

- **Riesgo alto**: construcción de primer MCP server toma más tiempo que estimado (typing, MCP protocol, testing). Mitigación: empezar con MVP simple (1 validator), no toda la suite
- **Riesgo medio**: validators R del SigmaControl original asumen contexto que no está documentado. Mitigación: aplicar `sigma:capture-domain` antes de migrar
- **Riesgo bajo**: el `.gga` con FILE_PATTERNS de Python rechaza commits que no deberían. Mitigación: ajustar gradualmente, monitorear falsos positivos

---

## Alternativas consideradas durante Sprint 1

### Alternativa A: Construir framework propio desde cero
**Descartada**: tiempo de construcción >>> tiempo de aprovechar ecosistema. Riesgo de reinventar lo que Gentle AI/Engram resolvieron mejor.

### Alternativa B: Implementar BMAD Method
**Descartada**: solapamiento del 80% con stack actual. Vocabulario distinto para mismo problema. Costo de migración alto sin beneficio empírico claro. Revisitable post-Sprint 5 si aparece dolor concreto.

### Alternativa C: Vector DB para memoria
**Descartada**: FTS5 alcanza para volumen proyectado (<10k entries en 5 años). Vectorización es over-engineering para uso personal. (Ver ADR-002)

### Alternativa D: Producto vendible desde el inicio
**Descartada**: no es el interés actual. Genera overhead (packaging, comunidad, naming) sin aportar a Stallen. (Ver ADR-004)

---

## Consecuencias del cierre

### Positivas

- Stack ecosistema instalado y validado empíricamente — base sólida para Sprint 2+
- Documentación arquitectónica completa — onboarding (incluido yo del futuro) en horas, no días
- Decisiones técnicas trazables — ADRs explican el "por qué" de cada elección
- Plan Sprint 2 explícito — no hay ambigüedad sobre próximos pasos
- Validación empírica del workflow — confianza estructural antes de generar código real
- Costo controlado — Sprint completo bajo $5 USD

### Negativas

- Deudas técnicas pendientes (Tier crítico bloquea código de Stallen real)
- ADRs 001-003 embebidos en docs/ en lugar de archivos individuales (inconsistencia)
- Hook UserPromptSubmit roto degrada UX de Claude Code (non-blocking pero molesto)
- Sprint 2 depende fuertemente de Sprint 1 (sin MCP servers, no hay enforcement determinístico real)

### Mitigaciones

- Tier crítico de deudas atacable en 1-2 horas al inicio de Sprint 2
- Migración de ADRs es trabajo mecánico (1 hora máximo)
- Hook UserPromptSubmit es deuda menor, no bloquea trabajo real
- Plan Sprint 2 con MVPs (1-3 validators, no todos) reduce riesgo

---

## Criterios de revisión

Este ADR queda como **histórico inmutable** una vez aplicado. No se revisita.

Para Sprint 2 se creará un ADR análogo (ADR-006 o numeración consecutiva) que documente outcomes y plan Sprint 3.

---

## Reflexión meta

**Lo que funcionó**:
- Apalancarse en ecosistema (decisión correcta validada empíricamente)
- Documentar decisiones como ADRs en tiempo real
- Validación empírica end-to-end antes de declarar el sprint cerrado
- 7° principio aplicado al propio Sprint (meta-validation del workflow con el workflow)

**Lo que no funcionó tan bien**:
- Coordinación entre agentes Claude (sesión paralela del Día 4)
- Commits multilinea en PowerShell (archivo basura del Día 4)
- Algunas decisiones críticas embebidas en docs/ en lugar de ADRs individuales

**Aprendizajes para Sprint 2**:
- Explicitar coordinación cuando hay múltiples agentes operando sobre el mismo filesystem
- Usar `git commit -F mensaje.txt` o editor para mensajes multilinea complejos
- Cualquier decisión arquitectónica nueva → ADR individual desde el inicio
- Aplicar `sigma:capture-domain` (cuando exista) ANTES de migrar componentes

---

## Referencias

- Constitución: `../CLAUDE.md`
- Roadmap detallado: `ADR-004-calibracion-nivel-comercial.md`
- Memoria + cierre: `../docs/MEMORIA-INTELIGENTE-Y-CIERRE.md`
- Arquitectura completa: `../DEPARTAMENTO-DE-SOFTWARE.md`
- Workflow validation: `../openspec/changes/validate-sdd-workflow/`
- 11 commits del Sprint 1: `git log --oneline` (rango e895d2c → 8bca811)

---

**Sprint 1 declarado CERRADO al 100% — 2026-05-14**
**Próximo sprint**: Sprint 2 — Construcción de MCP servers propios
**Próxima revisión periódica del sistema completo**: post-Sprint 5 (validación Nivel 2 comercial)
