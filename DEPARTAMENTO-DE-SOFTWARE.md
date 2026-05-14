# DEPARTAMENTO DE SOFTWARE — Arquitectura Concreta

**Versión**: 1.0 (2026-05-13)
**Estado**: Diseño fundacional
**Documentos relacionados**:
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` — los pasos determinísticos
- `SISTEMA-DE-TRABAJO.md` — el manual operativo día-a-día

---

## 1. VISIÓN

El **Departamento de Software** es un sistema determinístico que orquesta el ecosistema de IA existente (Claude Code, Codex, Gentle AI, OpenSpec, BMAD, Engram) para que la construcción de software siga un protocolo disciplinado e ineludible.

El sistema no genera código por sí mismo — **fuerza que el código generado por IA cumpla políticas explícitas** que humanos y agentes pueden saltarse por descuido pero no por elección consciente.

### Lo que NO es

- No es un harness que reemplaza a Claude Code o Cursor — los apalanca.
- No es un LLM nuevo — usa los existentes.
- No es vibe coding asistido — es ingeniería disciplinada con IA como ejecutor.
- No es un framework genérico — es metodología con enforcement determinístico.

### Lo que SÍ es

- Un equipo virtual con roles especializados que entregan handoffs estructurados.
- Una memoria institucional que retiene decisiones, dolores y aprendizajes cross-subsistema.
- Una capa de validación multi-nivel que detecta, advierte y auto-corrige.
- Un sistema de captura activa que asegura que el dominio del proyecto esté completo antes de generar código.
- Un conjunto de gates duros (pre-commit, CI/CD) que bloquean código no-conforme antes de producción.

---

## 2. FILOSOFÍA — 7 PRINCIPIOS RECTORES

Estos principios son la constitución del sistema. Toda decisión arquitectónica deriva de ellos.

| # | Principio | Implicación práctica |
|---|---|---|
| 1 | **Python traza el camino → IA lo recorre → Python verifica** | Código determinístico orquesta y valida. La IA produce. Nunca al revés. |
| 2 | **3 capas: preventiva → verificable → correctiva** | Cada output del sistema pasa por las 3 capas. La correctiva auto-arregla cuando puede. |
| 3 | **Dominio-first** | El dominio del negocio se captura activamente antes de cualquier código. No se asume. |
| 4 | **Auto-fix > finding** | Cuando una corrección es determinísticamente inequívoca, se aplica. No se devuelve al LLM para que adivine. |
| 5 | **Polinización cruzada** | Un patrón de dolor descubierto en un subsistema es candidato a propagarse a los demás estructuralmente similares. |
| 6 | **Descubrir antes de ejecutar** | El estado del sistema vivo especifica el scope. Auditoría empírica precede a estimación o diseño. |
| 7 | **Meta-producto recursivo** | Toda entidad productiva merece el mismo ambiente anti-degradación que su supervisor diseñó para sí mismo. Aplica al LLM productivo, al supervisor humano y a los outputs. |

---

## 3. ROLES DEL DEPARTAMENTO

El departamento tiene 12 roles especializados. Cada uno es responsable de fases específicas del workflow. Algunos roles los ejecutan agentes IA (Claude Code, Gentle AI), otros humanos, otros mixtos.

### 3.1 Roles de planificación

| Rol | Responsabilidad | Ejecutor | Inputs | Outputs |
|---|---|---|---|---|
| **Analista de Producto** | Capturar la idea del negocio en términos accionables | Humano + IA | Intenciones del dueño del producto | PRD inicial, lista de capabilities |
| **Captor de Dominio** | Capturar activamente reglas, escala, contexto, workflows | IA con supervisión humana | PRD inicial | ADN del proyecto (5 capas) |
| **Arquitecto** | Diseñar la solución técnica de alto nivel | IA con review humano | ADN + PRD | Diseño arquitectónico, decisiones técnicas |
| **Planificador (Scrum Master)** | Transformar diseño en stories con acceptance criteria | IA | Diseño arquitectónico | Backlog de stories priorizadas |

### 3.2 Roles de construcción

| Rol | Responsabilidad | Ejecutor | Inputs | Outputs |
|---|---|---|---|---|
| **Desarrollador Backend** | Implementar lógica de servidor, SQL, RPCs | IA con validación | Story específica | Código backend + tests |
| **Desarrollador Frontend** | Implementar UI, componentes, integraciones | IA con validación | Story específica | Código frontend + tests |
| **DevOps** | Migraciones, deploys, configuración de infraestructura | IA con review humano | Backend completado | Scripts deploy, configs |

### 3.3 Roles de validación

| Rol | Responsabilidad | Ejecutor | Inputs | Outputs |
|---|---|---|---|---|
| **Auditor de Plan** | Validar planes contra reglas R01-R15 antes de ejecutar | Python determinístico | Plan generado | Findings + auto-fixes aplicados |
| **Auditor de Código** | Validar código generado contra G/FG + SOLID + seguridad | Python + análisis estático | Código generado | Findings + auto-fixes aplicados |
| **Test Architect** | Diseñar y ejecutar tests adversariales obligatorios | IA con templates | Story + código | Test suite adversarial |
| **Auditor de Seguridad** | Validar zero-trust, RLS, auth, secrets | Python + herramientas | Código completo | Findings de seguridad |

### 3.4 Roles transversales

| Rol | Responsabilidad | Ejecutor | Inputs | Outputs |
|---|---|---|---|---|
| **Memoria Institucional** | Capturar decisiones, dolores, polinizaciones | Sistema (Engram + catálogos) | Eventos del departamento | Memoria persistente accesible |

---

## 4. STACK TECNOLÓGICO

El departamento se construye sobre 5 plataformas + 1 capa propia.

### 4.1 Plataformas del ecosistema (no se construyen, se adoptan)

| Plataforma | Función en el departamento | Versión target |
|---|---|---|
| **Claude Code / Codex** | Cliente IA principal. Provee filesystem, bash, git, MCP, sub-agents, memoria de sesión. | Latest |
| **Gentle AI v1.27+** | Stack de skills, gates (delegate_only, fail-closed checksums), 13 agentes especializados, code review GGA. | v1.27.0+ |
| **OpenSpec** | Spec-driven development: estructura por capability, delta markers (ADDED/MODIFIED/REMOVED), three-phase state machine. | Latest |
| **BMAD Method** | Multi-agente con roles, 4 fases (Analysis → Planning → Solutioning → Implementation), scale-adaptive intelligence. | v6+ |
| **Engram** | Memoria persistente agent-agnostic (Go binary + SQLite + FTS5 + MCP + HTTP API + CLI + TUI). | Latest |

### 4.2 Capa propia (IP del Departamento)

| Componente | Función | Estado actual |
|---|---|---|
| **Validadores Backend** (R01-R15, G1-G33) | Validación estructural de planes SQL + RLS + dependencias + colisiones | Implementado en SigmaControl Python |
| **Validadores Frontend** (FG1-FG14) | Validación de componentes React/TSX, imports, types, performance | Implementado en SigmaControl Python |
| **Patcher Determinístico** | Auto-fix sobre planes (R02 referencias, R12 deps, R15 transitivas) | Implementado, 725× más rápido que LLM-feedback |
| **ADN Multi-Capa** | Schema de captura activa: dominio + escala + contexto + workflows + criterios sistémicos | Fase 1 (dominio + modulos_custom) implementada |
| **Capturar ADN** (script) | 3 pasos: cross-reference, modulos_custom, hueco via canal bidireccional | Implementado |
| **Tubería Bidireccional** | `solicitar_dominio()` / `responder_solicitud()` para huecos detectados durante implementación | Implementado |
| **Catálogo Meta-Patrones** | Memoria institucional cross-subsystem de dolores del LLM | Implementado, 7 meta-patrones registrados |
| **Ritual Polinización** | Protocolo de cierre que evalúa si un dolor descubierto se propaga a otros subsistemas | Implementado |
| **Catálogos Canónicos** | erp.yaml, comunes.yaml con módulos pre-definidos | Implementado |
| **7 Principios Rectores** | Constitución del sistema | Documentados |

---

## 5. ARQUITECTURA TÉCNICA

### 5.1 Capas del sistema (de afuera hacia adentro)

```
┌─────────────────────────────────────────────────────────────────┐
│ CAPA 0: CONSTITUCIÓN                                            │
│   - 7 principios rectores (CLAUDE.md / AGENTS.md)               │
│   - Filosofía: dominio-first, auto-fix > finding, polinización  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAPA 1: CAPTURA ACTIVA                                          │
│   - PRD estructurado (formato BMAD)                             │
│   - ADN multi-capa (5 fases: dominio + escala + contexto +      │
│     workflows + proximidad de acción)                            │
│   - capturar_adn.py: cross-reference → modulos_custom → hueco   │
│   - Tubería bidireccional: solicitar_dominio()                  │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAPA 2: ORQUESTACIÓN (workflow)                                 │
│   - 4 fases BMAD (Analysis → Planning → Solutioning → Impl.)    │
│   - OpenSpec workflow (Propose → Apply → Archive)               │
│   - Stories con acceptance criteria explícitos                  │
│   - Skills declarativos con scope metadata (estilo Gentleman)   │
│   - Scale-adaptive: light workflow para bug fixes, full para    │
│     features grandes                                             │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAPA 3: ENFORCEMENT DETERMINÍSTICO (donde está la diferencia)   │
│   - Validadores estructurales (R01-R15)                         │
│   - Auto-fix patcher (R02, R12, R15)                            │
│   - Validadores de código (G1-G33, FG1-FG14)                    │
│   - SOLID structural checks                                      │
│   - Zero-trust security (RLS, auth, secrets)                    │
│   - Detección de errores silenciosos                             │
│   - Tests adversariales obligatorios (no solo happy path)       │
│   - Pre-commit hooks + CI/CD gates duros                        │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAPA 4: EJECUCIÓN (IA del ecosistema)                           │
│   - Claude Code / Codex (cliente principal)                     │
│   - Gentle AI v1.27 (skills + gates + 13 agentes)               │
│   - OpenSpec slash commands                                      │
│   - Engram (memoria persistente)                                 │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────────┐
│ CAPA 5: MEMORIA INSTITUCIONAL                                   │
│   - Engram (memoria persistente sesiones IA)                    │
│   - Catálogo meta-patrones de dolor                              │
│   - Decisiones técnicas con "por qué"                            │
│   - Ritual de polinización cruzada (paso 7.5 de cierre)         │
│   - Retrospectivas formales                                      │
└─────────────────────────────────────────────────────────────────┘
```

### 5.2 Flujo de datos típico (feature nueva)

```
1. Humano formula intención
   ↓
2. Analista de Producto + IA → PRD estructurado
   ↓
3. Captor de Dominio → ADN actualizado (cross-ref / módulos custom / huecos via tubería)
   ↓ [GATE: ADN completitud ≥ 95%]
4. Arquitecto → Diseño técnico
   ↓
5. Planificador → Backlog de stories con acceptance criteria
   ↓ [GATE: stories tienen criteria explícitos]
6. Auditor de Plan → R01-R15 + patcher determinístico
   ↓ [GATE: 0 críticos]
7. Desarrolladores Backend/Frontend → Código + tests
   ↓
8. Auditor de Código → G1-G33 + FG1-FG14 + SOLID + zero-trust
   ↓ [GATE: 0 críticos, auto-fix aplicado donde corresponda]
9. Test Architect → Tests adversariales obligatorios
   ↓ [GATE: cobertura adversarial ≥ N categorías edge cases]
10. Auditor de Seguridad → Validación final
    ↓ [GATE: pre-commit hooks pasan]
11. DevOps → Deploy
    ↓ [GATE: CI/CD pasa + smoke tests post-deploy verdes]
12. Memoria Institucional → Capturar aprendizajes + radar polinización
```

### 5.3 Estructura de archivos del proyecto

```
proyecto/
├── AGENTS.md / CLAUDE.md                 # Constitución + dispatcher de skills
├── adn-proyecto.json                     # ADN multi-capa (5 fases)
├── openspec/                             # Estructura OpenSpec
│   ├── specs/                            # Por capability (no por fase)
│   │   ├── auth-tenancy/
│   │   ├── inventory/
│   │   └── ...
│   ├── changes/                          # Cada feature/bug en su folder
│   │   ├── YYYY-MM-DD-feature-X/
│   │   │   ├── proposal.md
│   │   │   ├── prd.md
│   │   │   ├── design.md
│   │   │   ├── stories.md                # Stories con acceptance criteria
│   │   │   ├── tasks.md
│   │   │   └── spec-deltas.md            # ADDED/MODIFIED/REMOVED
│   │   └── ...
│   └── archive/                          # Cambios completados
├── catalogos/                            # Catálogos canónicos
│   ├── modulos/
│   │   ├── erp.yaml
│   │   └── comunes.yaml
│   └── SCHEMA.md
├── meta-patrones/                        # Memoria institucional
│   ├── catalogo-dolor.md
│   └── polinizaciones-formales.md
├── .claude/skills/                       # Skills declarativos
│   ├── capturar-dominio/SKILL.md
│   ├── planificar-feature/SKILL.md
│   ├── auditar-plan/SKILL.md
│   ├── construir-codigo/SKILL.md
│   ├── auditar-codigo/SKILL.md
│   ├── tests-adversariales/SKILL.md
│   ├── validar-seguridad/SKILL.md
│   ├── deploy-seguro/SKILL.md
│   └── cerrar-sesion/SKILL.md
├── mcp-servers/                          # Tools determinísticos
│   ├── sigma-plan-validator/             # R01-R15
│   ├── sigma-code-validator/             # G1-G33 + FG1-FG14
│   ├── sigma-auto-fix/                   # Patcher
│   ├── sigma-domain-channel/             # Tubería bidireccional
│   ├── sigma-adversarial-tester/         # Tests obligatorios
│   ├── sigma-solid-checker/              # SOLID estructural
│   ├── sigma-security-auditor/           # Zero-trust
│   └── engram-memory/                    # Memoria persistente
├── decisions/                            # ADRs con "por qué"
│   └── ADR-NNNN-titulo.md
└── .git/hooks/                           # Enforcement duro
    ├── pre-commit                        # Validadores aplicados
    └── pre-push                          # Tests + security
```

---

## 6. APORTES ÚNICOS DEL DEPARTAMENTO (vs ecosistema solo)

Lo que SigmaControl aporta y NO existe en ningún framework del ecosistema:

### 6.1 Validadores Backend específicos para Postgres/Supabase

**R01-R15** — validación de planes SQL:
- R01: ancestros válidos para deps funcionales
- R02: referencias coherentes entre threads
- R03: detección de ciclos circulares (directos y transitivos)
- R04: deps fuera de scope
- R05: naming conventions con sufijo `_sc`
- R06: colisiones de tablas entre threads
- R07: plan vs grafo consistency
- R08: funciones declaradas pero no creadas
- R09: aislamiento de scope (warning)
- R10: stubs necesarios para deps externas
- R11: tamaño máximo de thread
- R12: cobertura de dominio (regla de negocio sin thread implementador)
- R13: cobertura de módulos canónicos
- R15: dependencias transitivas (función X toca tabla Y, debe declarar dep transitiva)

**G1-G33** — validación SQL post-procesador:
- G1: timestamps inyectados (created_at, updated_at)
- G2: SECURITY DEFINER con SET search_path = ''
- G7-G8: campos obligatorios (NOT NULL, defaults)
- G11A: referencias coherentes
- G13: ENUMs no duplicados cross-thread
- G15: parameterized queries (no string interpolation)
- G21: detección de entidades inventadas
- G23-G33: reglas G adicionales

### 6.2 Patcher Determinístico (Auto-fix)

`patcher_plan.py` que arregla automáticamente:
- R02: agrega referencias faltantes
- R12: crea thread audit_sc para reglas no implementadas
- R15: agrega deps transitivas faltantes

**Performance medida**:
- 725× más rápido que LLM-feedback
- $0 vs $3 por vuelta de LLM
- Convergencia 100% vs 93% del approach LLM

### 6.3 ADN Multi-Capa

Schema único del proyecto con 5 fases:
1. **Dominio**: reglas de negocio con tablas declaradas
2. **Escala operativa**: sedes, usuarios, tx/día, registros pico, estacionalidad
3. **Contexto**: vocabulario, regulaciones, integraciones, workflows del dueño
4. **Workflows complejos**: multi-paso, dependencias, doble aprobación
5. **Proximidad de acción**: distancia entre decisión y operación real

### 6.4 Polinización Cruzada Formal

- Catálogo de meta-patrones de dolor cross-subsystem
- Ritual de cierre que evalúa propagación (paso 7.5 del protocolo)
- Matriz de cobertura por subsistema (P1/P0/Frontend/Dominio)
- Primera polinización validada: P1 G11A → P0 R15 (convergencia <1s / $0 / 0 intervenciones)

### 6.5 Tubería Bidireccional

`solicitar_dominio()` + `responder_solicitud()`:
- Canal formal worker→humano→worker
- Crea SOL-{timestamp-microsegundos}.json
- Permite que el sistema pause y pregunte por huecos detectados
- Sin esto, asume specs upfront y se rompe en producción

### 6.6 Tests Adversariales con Dominios Sintéticos

`test_adversarial_dominio.py`:
- 4 dominios sintéticos (clínica, restaurante, logística, SaaS)
- 25 reglas cross-dominio
- 16 casos edge unitarios
- 20/20 tests OK validando clasificador sobre dominios radicalmente distintos
- Base para banco de proyectos sintéticos (estrés arquitectónico)

---

## 7. TIERS DE MADUREZ

El departamento se construye en 3 tiers. Cada tier define un nivel de calidad alcanzado.

### Tier 1 — Producción comercial (mínimo viable)

Lo que es necesario para que algo sea considerado "production grade":

- A6: Tests adversariales obligatorios sistematizados
- A7: Verificación SOLID estructural automatizada
- A8: Validación zero-trust completa
- A9: Detección de errores silenciosos
- A11: Detección de concurrencia issues
- C2: CI/CD con gates duros
- C5: Validación de performance crítica
- C6: Smoke tests post-deploy
- F2: Captura de escala operativa (Fase 2 ADN)
- F3: Captura de contexto (Fase 3 ADN)

**Sin Tier 1 completo, el código NO es comercial.**

### Tier 2 — Durabilidad (sobrevive 12+ meses sin pudrirse)

- B1: Estructura por capability (no por fase)
- B3: Delta markers en cambios
- B4: Stories con acceptance criteria explícitos
- B5: PRD estructurado por feature
- B6: Brownfield vs Greenfield workflows diferenciados
- D1: Decisiones técnicas estructuradas con "por qué"
- D4: Retrospectivas formales
- D5: Documentación de "por qué", no solo "qué"
- E4: Métricas de calidad recurrentes
- E5: Tracking automatizado de evolución de deuda

**Sin Tier 2, el código se vuelve cirugía mayor refactorizar en 12 meses.**

### Tier 3 — Producto vendible público

- G2: Templates por tipo de proyecto
- G3: Skills/MCP servers exportables
- G4: Documentación pública de uso
- G5: Banco de proyectos sintéticos validados
- F4: Captura de workflows complejos (Fase 4 ADN)
- F5: Criterios de cruce sistémico — proximidad de acción (Fase 5 ADN)
- D6: Engram-style memory adopción completa

**Sin Tier 3, el departamento sirve para vos pero no es producto distribuible.**

---

## 8. DIMENSIONES ADICIONALES DE CALIDAD

Las 7 dimensiones del departamento (sección 1) son el core, pero hay 10 prácticas adicionales que distinguen código "que funciona" de código de calidad profesional real. Están priorizadas por tier para incorporación gradual.

### 8.1 — Tier 1 (crítico para producción)

**1. Reversibilidad por defecto**

Toda operación destructiva debe ser reversible o explícitamente marcada como no-reversible.

Patrones obligatorios:
- Soft delete sobre hard delete (campo `deleted_at` en vez de DELETE)
- Versionado de datos críticos: tabla de auditoría que guarda cambios
- Rollback automático en deploys: si smoke tests fallan post-deploy → rollback sin intervención
- Snapshots periódicos de bases de datos (no solo backups, snapshots para experimentos)
- Feature flags para activar/desactivar features sin redeploy

**2. Idempotencia en operaciones críticas**

Mismo request ejecutado 2-3 veces debe producir mismo resultado.

Aplica a:
- API endpoints: aceptar `Idempotency-Key` en POST/PUT críticos
- Webhooks: procesamiento idempotente
- Background jobs: tareas async deben poder reintentarse sin efectos duplicados
- Migrations: DROP IF EXISTS antes de CREATE, re-ejecución segura validada
- Triggers de DB: evitar cascadas que multipliquen efectos

**3. Backups verificados con restore probado**

Un backup que no probaste no es backup, es esperanza.

Práctica:
- Backup automático de BD: diario completo + incremental cada hora
- Backups en otra región (no solo el mismo servidor)
- Retención escalonada: últimos 7 días diarios, últimas 4 semanas semanales, últimos 12 meses mensuales
- **Restore test trimestral**: cada 3 meses, restore real a ambiente separado, verificar que funciona
- Documentar RTO (Recovery Time Objective) y RPO (Recovery Point Objective)

**4. Manejo explícito de tiempo y zonas horarias**

Causa de incontables bugs en software real, casi nunca cubierto.

Reglas:
- Almacenar SIEMPRE en UTC en base de datos
- Convertir a timezone del usuario solo en presentación
- Usar tipos con timezone explícito (`TIMESTAMPTZ` en Postgres, NO `TIMESTAMP`)
- Nunca confiar en `now()` del cliente, siempre server-side
- Tests con timezones distintas para detectar bugs (UTC vs Lima vs Bogotá)
- Considerar daylight saving time en cálculos de duración

### 8.2 — Tier 2 (importante para profesionalismo)

**5. Observabilidad (logs, traces, métricas)**

No alcanza con que el código funcione — necesitás saber qué pasa en runtime.

Componentes:
- Logging estructurado: JSON logs con campos consistentes (timestamp, level, request_id, user_id)
- Distributed tracing: OpenTelemetry si hay múltiples servicios
- Métricas de negocio: "transacciones/min", "errores por feature", "latencia p95 por endpoint" (no solo CPU/RAM)
- Health checks: endpoints `/health` y `/ready` que reportan estado real
- Error tracking: Sentry o equivalente para capturar excepciones con stack traces

**6. Separación de ambientes con paridad estricta**

Departamento real opera con al menos 3 ambientes.

Estructura:
- **Development** (local): donde escribís código
- **Staging** (réplica de prod): donde probás antes de prod, datos sintéticos o anonimizados
- **Production**: lo real

Reglas duras:
- Mismo stack tecnológico en los 3 (no SQLite en dev y Postgres en prod)
- Configs distintas via env vars, NUNCA hardcoded
- Migrations corren primero en staging, después en prod
- Acceso a prod restringido
- Datos de prod nunca van a dev (privacy + seguridad)

**7. Gestión de costos y rate limiting defensivo**

Especialmente crítico con APIs externas (Claude API, Supabase, etc.).

Patrones:
- Rate limiting interno: máximo N requests/segundo a APIs externas
- Circuit breakers: si API externa falla repetidamente, dejar de llamarla X minutos
- Caching agresivo de respuestas costosas
- Budget alerts: notificación si gasto mensual va camino de superar presupuesto
- Graceful degradation: si servicio externo cae, la app sigue funcionando con funcionalidad reducida
- Timeouts explícitos: ningún request sin timeout (default 30s, ajustar según caso)

### 8.3 — Tier 3 (mejora continua)

**8. Convenciones explícitas de naming y código**

Mucho se asume y poco se documenta. Vivirá en `docs/CONVENCIONES.md`.

Qué documentar:
- Naming de variables, tablas, funciones, archivos
- Estructura de commits: Conventional Commits (`feat:`, `fix:`, `chore:`)
- Branching: trunk-based, GitHub Flow, etc.
- Comentarios: cuándo agregar, cuándo evitar

**9. Documentación técnica viva (no documentos muertos)**

Distinto a los 3 documentos del Departamento — esto es documentación del código mismo.

Tipos:
- README por módulo importante
- ADRs ya formalizados en `decisions/`
- Diagramas de arquitectura en Mermaid (en markdown, no Visio)
- API documentation auto-generada (OpenAPI/Swagger)
- Changelog visible (`CHANGELOG.md`)
- Runbooks: "¿qué hacer si X falla?"

Regla: si la documentación no se actualiza cuando cambia el código, no sirve. Idealmente auto-generada o forzada por CI.

**10. Plan de respuesta a incidentes**

Detalle operativo en `SISTEMA-DE-TRABAJO.md` sección Situaciones Especiales.

Componentes:
- Incident severity levels: P0 (sistema caído) / P1 (feature crítica afectada) / P2 (degradación menor) / P3 (cosmético)
- Runbook por incidente común
- Postmortem template (cada incidente serio genera doc con root cause + acciones preventivas)
- War room procedure (cómo coordinás, incluso solo, durante incidente en curso)

### 8.4 — Tabla de incorporación al roadmap (recalibrada 2026-05-13)

Esta tabla refleja la decisión del ADR-004 (`decisions/ADR-004-calibracion-nivel-comercial.md`): el Departamento apunta a Nivel 2 comercial profesional en 12 semanas. Tier 3 features (compliance, multi-tenant, DR) NO están en scope salvo trigger explícito documentado.

| Sprint | Tier 1 a agregar | Tier 2 a agregar | Tier 3 a agregar |
|---|---|---|---|
| 2 | Reversibilidad (soft delete, feature flags) + Idempotencia básica | MCP servers propios + Captura de dominio | — |
| 3 | Idempotencia API + Timezones UTC (audit Stallen) | **CI/CD obligatorio** + **Staging environment** | — |
| 4 | — | **Observabilidad real** (Sentry + logs estructurados + dashboard) + **Tests adversariales sistemáticos** | — |
| 5 | Backups con restore probado (primer ciclo) | Validación empírica end-to-end sobre Stallen feature real + **Release process formal** | — |
| 6 | — | Monitoreo de costos APIs (budget alerts) + Tuning observabilidad | — |
| Post-Sprint 6 | — | — | Convenciones, docs viva, plan incidentes formal |

**Total: 10-12 semanas hasta Nivel 2 comercial profesional sólido.**

Las 5 piezas críticas (en negrita) son las que separan "código que funciona" de "código de departamento de software comercial real". Detalle de cada una:

**CI/CD obligatorio** (Sprint 3): GitHub Actions con workflow que corre linters estrictos, type check, tests + coverage threshold, security scan (bandit + trufflehog), SQL migrations dry-run. Branch protection en `main`: no merge sin CI passing. Deploy automático a staging después de merge.

**Staging environment** (Sprint 3-4): Réplica de Stallen en proyecto Supabase separado. Datos sintéticos o anonimizados (NUNCA prod data en staging). Pipeline PR → staging → manual approval → prod. Smoke tests post-deploy automáticos.

**Observabilidad real** (Sprint 4): Sentry para error tracking. Logging estructurado con structlog (Python) o pino (Node) + request_id consistente. Health checks `/health` y `/ready`. Dashboard básico (Grafana Cloud free tier o Better Stack). Alertas configuradas: error rate > X%, latencia p95 > Y ms, budget API externa > Z%.

**Tests adversariales sistemáticos** (Sprint 4): Skill `/sigma:adversarial-tests` que para cada función nueva genere automáticamente tests de inputs vacíos/null/undefined, inputs malformados, boundary conditions, race conditions, network failures simuladas. Librerías: Hypothesis (Python) o fast-check (JS) para property-based testing.

**Release process formal** (Sprint 5): SemVer + CHANGELOG.md automático con conventional-changelog + release tags en git + release notes + rollback documentado por release.

Lectura cruzada: `decisions/ADR-004-calibracion-nivel-comercial.md` para racional completo de por qué estas 5 son críticas para Nivel 2 y NO opcionales.

No agregar todo de una vez. Esfuerzo escalonado, validación empírica de cada dimensión antes de la siguiente.

---

## 9. ESTADO ACTUAL VS VISIÓN COMPLETA

### 9.1 Lo que ya está implementado (en SigmaControl Python original)

- 7 principios rectores documentados
- R01-R15 validadores de plan
- G1-G33 validadores SQL
- FG1-FG14 validadores frontend
- Patcher determinístico con 47/47 tests
- ADN Fase 1 (dominio + modulos_custom) — 100% efectiva en stallen-test y stallen-control
- Tubería bidireccional con fix microsegundos
- Catálogo meta-patrones (7 patrones)
- 1 polinización formal validada (G11A → R15)
- Tests adversariales con 4 dominios sintéticos + 16 unitarios
- Catálogos canónicos (erp.yaml, comunes.yaml)
- Protocolo de cierre disciplinado (9 pasos)
- Protocolo de revisión periódica

### 9.2 Lo que falta construir o migrar

**Migración al ecosistema (semana 1-4)**:
- Setup Claude Code / Codex como cliente principal
- Install Gentle AI v1.27 + Engram
- Adopción OpenSpec workflow
- Migrar validadores a MCP servers
- Migrar patcher a MCP server
- Migrar capturar_adn a skill

**Construcción nueva (semana 5-9)**:
- SOLID structural automatizado (A7)
- Errores silenciosos detection (A9)
- Zero-trust completo (A8)
- Concurrencia checks (A11)
- CI/CD con gates duros (C2)
- Performance critical paths (C5)
- Smoke tests post-deploy (C6)
- Dashboard métricas calidad (E4)
- ADN Fases 2-5 (escala, contexto, workflows, proximidad)

**Empaquetamiento como producto (mes 3-6)**:
- Skills exportables (G3)
- Templates por tipo de proyecto (G2)
- Documentación pública (G4)
- Banco proyectos sintéticos completo (G5)

### 9.3 Roadmap por tiers

| Sprint | Duración | Tier objetivo | Entregable |
|---|---|---|---|
| 1 | 2 semanas | Fundación | Stack instalado + CLAUDE.md + OpenSpec structure |
| 2 | 2 semanas | Migración IP | MCP servers + skills migrados |
| 3 | 2 semanas | Tier 1 parte 1 | SOLID + zero-trust + errores silenciosos automatizados |
| 4 | 2 semanas | Tier 1 parte 2 | CI/CD + performance + smoke tests |
| 5 | 1 semana | Validación | Aplicar a Stallen feature real |
| 6-8 | 6 semanas | Tier 2 | Durabilidad: stories, PRDs, ADRs, métricas |
| 9-12 | 8-12 semanas | Tier 3 | Empaquetamiento como producto vendible |

**Total horizonte**: 6 meses para tier 3 completo. 9 semanas para Tier 1 con migración.

---

## REFERENCIAS

- `PROTOCOLO-CONSTRUCCION-CODIGO.md` — protocolo determinístico paso a paso
- `SISTEMA-DE-TRABAJO.md` — manual operativo día-a-día
- SigmaControl original (legacy): `C:\Users\Windows 11\sigmacontrol\`
- BMAD Method: https://github.com/bmad-code-org/BMAD-METHOD
- OpenSpec: https://github.com/fission-ai/openspec
- Gentle AI: https://github.com/Gentleman-Programming/gentle-ai
- Engram: https://github.com/Gentleman-Programming/engram

---

Versión 1.0 — 2026-05-13
Próxima revisión: tras Sprint 1 completado (Stack instalado + validado empíricamente)
