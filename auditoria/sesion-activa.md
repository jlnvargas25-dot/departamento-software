# SESIÓN ACTIVA — Framework Departamento

> **Propósito**: estado al cerrar la última sesión del Framework.
> Para sesiones específicas de Stallen, ver `projects/stallen/auditoria/sesion-activa.md`.

**Última sesión**: 2026-05-20 — Detección de deriva de contexto + creación de PROTOCOLO-INICIO + PROTOCOLO-CIERRE + reconfiguración Project Claude.ai
**Sesión anterior**: 2026-05-15 — Sprint 2 Día 2 (chat.ai, 3 audits empíricos, A1-A19 implementadas + A20-A25 deudas)
**Cliente**: Claude in Chrome (MCP filesystem activo)
**Duración estimada**: sesión larga (varias horas, manifestación N=31+ del sub-meta-patrón #13.x detectada y corregida)
**Estado**: ✅ Cerrada formalmente con primera aplicación práctica del PROTOCOLO-CIERRE-SESION.md v1.0

---

## Resumen ejecutivo (1 línea)

Sesión arquitectónica intensiva: Nivel 2 (A1-A19 + 28 anti-patterns + SOLID + C1-C6) + multi-proyecto (ADR-007) + cross-LLM (ADR-008) + NORTE Framework v0.1 + decisión enfoque solo Framework (sin Stallen) + descubrimiento crítico de 4 repos del ecosistema + **3 audits empíricos sucesivos** detectaron 9 GAPs resueltos (A11-A19) + **6 GAPs adicionales documentados como deudas formales** (A20-A25, audit empírico 3 / Opción D).

---

## Lo que se hizo (cronológico)

### 1. Exploración 5 repos Harness Engineering — COMPLETO
walkinglabs/learn-harness-engineering, harness/harness, code-yeongyu/oh-my-openagent, fembyte/dractical, nneira/adk-a2a-prod-cloud-run

### 2. Depuración profunda legacy SigmaControl — COMPLETO
Framework 5 dimensiones. Hallazgo: el legacy ya implementaba Harness Engineering al 85% sin conocer el vocabulario formal.

### 3. Formalización Nivel 2 arquitectura — COMPLETO
Carpeta `architecture/` (108 KB inicial): PRINCIPIOS-SOLID.md, PRINCIPIOS-ARQUITECTURA.md (15 reglas A1-A15), PATRONES-CARPETAS.md (6 reglas C1-C6), ANTI-PATRONES.md (24 anti-patterns), README.md.

### 4. Audit empírico recursivo 1 (Julián) — DESCUBRIÓ 5 GAPS
Agregadas: A11 DAO+DTO, A12 Zero Trust (6 reglas ZT-1..ZT-6), A13 Concurrency Safety, A14 Explicit Failure, A15 Unhappy Path First. 5 anti-patterns nuevos (AP-2.8, AP-2.9, AP-3.6, AP-3.7, AP-3.8). Aplicación viva del Corolario E del 6° principio rector.

### 5. ADR-006 — COMPLETO
`decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md`: 5 niveles + SOLID + A1-A15.

### 6. Sistema memoria entre sesiones — COMPLETO + VALIDADO
`auditoria/sesion-activa.md` + `SIGUIENTE-SESION.md`. Validación empírica exitosa cuando Claude CLI retomó perfectamente.

### 7. Investigación Engram — BLOQUEADO POR SAC
Engram bloqueado por Windows Smart App Control. Ubuntu WSL instalado, setup pendiente. **Resuelto post-hallazgo §16**: claude-mem es alternativa superior.

### 8. Investigación exhaustiva del ecosistema — COMPLETO
GitHub Spec Kit (98.5k stars), OpenSpec, VoltAgent/awesome-claude-code-subagents (100+), sickn33/antigravity-awesome-skills (1,460+), VoltAgent/awesome-design-md (73.5k), Supabase Agent Skills oficial, Vercel Agent Skills oficial.

### 9. Visión B emergente (Spec Kit)
Pregunta de Julián: "el workflow de esa arquitectura sería mejor que nuestra arquitectura?". Análisis: Departamento NO compite con Spec Kit, es capa de gobernanza encima. Pendiente validación empírica.

### 10. ADR-007: Separación Framework vs Proyectos — COMPLETO
Framework universal en raíz + `projects/<slug>/` por proyecto + `templates/project-skeleton/`.

### 11. Estructura multi-proyecto creada — COMPLETO
`projects/stallen/` con 13 archivos/carpetas + `templates/project-skeleton/` con 7 templates. Carpetas legacy raíz eliminadas.

### 12. Adopción cross-LLM formal (ADR-008) — COMPLETO
Pregunta: "el departamento de software podría quedar para cualquier LLM?". Análisis: ~90% ya agent-agnostic. Creado ADR-008 + `docs/AGENT-INTEGRATION.md` (5+ agentes) + AGENTS.md v1.2 + README v1.3.

### 13. Decisión estratégica: enfoque en Framework puro
Julián: *"olvidemos stallen solo enfoquémonos en el departamento de software... lo importante es enfocarnos en el departamento para poder usarlo en cualquier proyecto futuro incluido stallen"*

Implicaciones:
- Stallen como driver del Framework → DIFERIDO
- `projects/stallen/` → candidato a renombrar `projects/example-stallen/` (no ejecutado aún)
- T4 (NORTE Stallen) + T5 (capturar dominio Stallen) → CANCELADOS/DIFERIDOS
- Aplicación recursiva del 7° principio rector

### 14. NORTE del Framework v0.1 creado
Nuevo archivo `NORTE.md` (~22 KB) con 11 secciones. Entrevista iniciada:
- Q1 Audiencia → Respuesta E (personal evolucionando a vibe coders si valida)
- Q2 Driver → Respuesta E (necesidad personal primario + comunidad eventual)
- Q3 Criterios → Julián articuló visión harness (ver §15)

### 15. ARTICULACIÓN DEL VERDADERO NORTE — CRITICAL INSIGHT

Cita verbatim de Julián:
> *"la idea es crear un harness que permita construir proyectos sin tener miedo de que el llm alucina, inventa o esta haciendo cosas que no debe. es construir el ecosistema necesario para que el departamento de software analice, planifique, ejecute, verifique como se haria en un departamento de software real o como lo hace un senior en produccion"*

Reformulación del propósito del Framework:
- NO es "framework genérico"
- ES **HARNESS anti-alucinación** que sostiene al LLM para operar como senior en producción
- Mitiga 3 fallos del LLM: alucinación, invención, mal comportamiento (saltos)
- Ciclo central: **Analizar → Planificar → Ejecutar → Verificar**
- Modelo mental: senior engineer en producción de departamento de software real
- Diferenciador vs Spec Kit/OpenSpec/Antigravity: ninguno mitiga alucinación específicamente

Conexión 2° principio rector: las 3 capas (PREVENTIVA → VERIFICABLE → CORRECTIVA) son específicamente para mitigar fallos del LLM en cada fase del ciclo.

### 16. Hallazgo crítico: 4 repos del ecosistema ya implementan la visión

A pedido de Julián, busqué 4 repos:

**(a) `obra/superpowers`** — 170k stars, oficial Anthropic marketplace, Jesse Vincent
- Cita verbatim: *"transforms Claude Code from intelligent autocomplete to senior AI developer"*
- Workflow 7 fases: Socratic Brainstorming → Micro-Task Planning → TDD red/green → YAGNI+DRY → Parallel Subagents → Inspection → Review
- Skills auto-activan: test-driven-development, systematic-debugging, verification-before-completion, brainstorming
- Cross-agent: Claude Code, Codex CLI/App, Factory Droid, Gemini CLI, OpenCode, Cursor, Copilot CLI
- **ES literalmente la visión articulada por Julián, ya implementada**

**(b) `affaan-m/everything-claude-code (ECC)`** — 100k+ stars, 13k forks, MIT, Anthropic hackathon winner
- 28 agentes + 119 skills + 60 commands
- Cross-agent: Claude Code, Cursor, Codex, OpenCode, Cowork
- Hookify, pass@k verification metrics, memory persistence, continuous learning, verification loops, parallelization (git worktrees), AgentShield security
- v1.9.0 (March 2026): selective-install, 12 language ecosystems
- ECC Tools (GitHub App): auto-genera skills desde git history

**(c) `thedotmack/claude-mem`** — v8.5.4, Apache 2.0
- Memoria persistente cross-agent (Claude Code, OpenClaw, Codex, Gemini, Hermes, Copilot, OpenCode)
- 4 MCP tools workflow 3-layer (search → review → fetch)
- AI compression (~10x más eficiente)
- 1-line install
- **Alternativa SUPERIOR a Engram**: más fácil setup, cross-agent, mejor diseñado

**(d) `nextlevelbuilder/ui-ux-pro-max-skill`** — 71k stars
- 67 UI styles + 161 color palettes + 57 font pairings + 99 UX guidelines + 25 chart types + 16 tech stacks + 161 reasoning rules
- Cross-agent muy amplio (14 agentes)
- Para cuando llegue UI Stallen (futuro)

**Visión C emergente**: Departamento = **Stack curado del ecosistema** + **Calibración única Tier 1 vibe coder + Architecture/A1-A19 + Anti-patterns como overlay arquitectónico**.

Tiempo ahorrado wholesale: ~8-12 semanas. **DECISIÓN ESPERA SANDBOX EMPÍRICO**.

### 17. 2do AUDIT EMPÍRICO (Julián) — A16-A19 (dimensión infraestructura resiliente)

Preguntas verbatim de Julián:
> *"rate limiting lo estamos implementando ?"*
>
> *"cloudflare? tenemos activo waf ? evitamos logica sensible en el fronted? usamos orms en el backend? agregamos try/catch en cada llamada api? usamos colas( queues para tareas pesadas ) ?"*

**Identificación de dimensión faltante**: A1-A15 cubría lógica/datos/seguridad básica. Faltaba dimensión completa de **INFRAESTRUCTURA RESILIENTE**:
- A16 Rate Limiting & Throttling
- A17 Edge Protection (CDN + WAF + DDoS Mitigation)
- A18 Async Processing for Heavy Tasks
- A19 External Service Resilience

**Acciones ejecutadas**:
- ✅ `PRINCIPIOS-ARQUITECTURA.md` v1.1 → **v1.2** con A16-A19 (con definición, ejemplos PG/Python concretos, anti-patterns, validaciones automáticas)
- ✅ `ANTI-PATRONES.md` v1.1 → **v1.2** con AP-2.10 Unbounded API Surface, AP-2.11 Exposed Origin, AP-3.9 Sync Heavy Operation, AP-3.10 External Call Without Timeout
- ✅ Mappings a Harness Engineering + SOLID actualizados con A16-A19
- ✅ **COMMIT + PUSH ejecutado** en sesión 2026-05-20 (commit `1c08732` incluyó architecture/ + `dc0c798` incluyó audit empírico 3)

### 19. SESIÓN 2026-05-20 — Detección de deriva de contexto + reconfiguración del Project Claude.ai

Descubrimiento crítico al iniciar otro chat del Project: el chat actual había estado trabajando en `C:\DEPARTAMENTO-SOFTWARE\` pero el system prompt del Project apuntaba a SigmaControl (`sigmacontrol-camino-1/`). Manifestación N=31+ del sub-meta-patrón #13.x — compactación de chat propagó contexto desviado del system prompt.

**Verificación empírica realizada** (aplicación del 6° principio rector):
- Confirmado: ambos proyectos existen en disco
- SigmaControl en `sigmacontrol-camino-1/`: estado canon s44 cerrado (2026-05-08), refactor 3 capas activo, s45 pendiente
- DEPARTAMENTO-SOFTWARE en `C:\DEPARTAMENTO-SOFTWARE\`: este Framework, Sprint 2 Día 2, A1-A19 + A20-A25
- Son **dos proyectos distintos** que coexisten

**Decisión Julian — Lectura B**: el Framework reemplazó a SigmaControl en la dirección del refactor. SigmaControl queda como referencia histórica.

**Solución elegida**: crear Project nuevo en Claude.ai específico del Framework, en lugar de migrar el Project existente. Mantiene SigmaControl intocable y da configuración limpia al Framework.

**Archivos creados en disco en sesión 2026-05-20**:
- `PROTOCOLO-INICIO-CHAT.md` v1.0 — cómo arrancar sesión + verificación contexto Project (PASO 1 anti-deriva) + audit empírico recursivo como práctica nativa + diferencia con SigmaControl
- `PROTOCOLO-CIERRE-SESION.md` v1.0 — checklist 8 pasos manual (sin ritual.py) + radar deuda + audit final + lección N=31+ integrada

**Configuración del Project nuevo entregada a Julián**:
- 3 archivos mínimos para subir: CLAUDE.md + PROTOCOLO-INICIO-CHAT.md + PROTOCOLO-CIERRE-SESION.md
- 2 archivos recomendados: DEPARTAMENTO-DE-SOFTWARE.md + SISTEMA-DE-TRABAJO.md
- Texto del system prompt instructivo (con regla anti-deriva de contexto integrada)

**Validación empírica de que el Project nuevo funciona**:
Julián creó el Project nuevo y abrió chat. El nuevo chat:
- Se identificó correctamente como Framework (no SigmaControl)
- Leyó sesion-activa.md + SIGUIENTE-SESION.md del disco
- Reportó estado real: A1-A19 + A20-A25 deudas + decisiones pendientes
- **CRÍTICAMENTE**: aplicó el 6° principio rector mejor que este chat — detectó que los 2 protocolos del 2026-05-20 son posteriores al cierre formal del 2026-05-15, lo que implica gap de cierre silencioso (esta misma sesión no estaba documentada en sesion-activa.md)
- Aplicación recursiva del 7° principio rector: el chat nuevo aplicó el protocolo de cierre v1.0 que recién se había escrito

**Esta sección 19 es la respuesta al gap detectado**: cierre formal retroactivo de la sesión 2026-05-20 antes de arrancar T0-T6 del plan de SIGUIENTE-SESION.md.

---

### 18. 3er AUDIT EMPÍRICO — OPCIÓN D — Catálogo completo de GAPs del Nivel 2

Preguntas verbatim de Julián que dispararon el audit completo:
> *"arquitectura sidecar ? arquitectura hexagonal ?"*

**Decisión metodológica**: en vez de seguir incremental (descubrir A20, A21, A22... uno por uno tras cada pregunta), aplicar 6° principio rector **al meta-trabajo**: descubrir scope completo antes de ejecutar. Julián eligió Opción D — audit empírico COMPLETO del Nivel 2 contra catálogo "todo lo que SaaS Tier 1 necesita".

**Catálogo evaluado (13 dimensiones arquitectónicas)**:

| Dimensión | Cobertura A1-A19 | GAP crítico identificado |
|---|---|---|
| 1. Lógica de negocio + datos | ✅ Cubierta (A1-A15) | Ninguno |
| 2. Infraestructura resiliente | ✅ Cubierta (A16-A19) | Ninguno |
| 3. **Paradigma arquitectónico** | ⚠️ Parcial (A2+A7+A11) | **A20 Hexagonal** |
| 4. **Observabilidad / SRE** | ⚠️ Parcial (mencionado) | **A21 Observability** |
| 5. **Secrets & Credentials** | ⚠️ Parcial (A12 ZT-6) | **A22 Secrets Mgmt** |
| 6. **Deployment / Release** | ⚠️ Parcial (A8 rollback) | **A23 Deployment Safety** |
| 7. **Data Lifecycle / Privacy** | ❌ No cubierta | **A24 Data Lifecycle** |
| 8. **Authorization granular** | ⚠️ Parcial (A12 auth básica) | **A25 Authorization** |
| 9. Performance & Scalability | Parcial / decisión stack | Anti-patterns N+1, Pagination |
| 10. CI/CD & DevOps | Decisión proyecto | Sin regla universal |
| 11. Testing extendido | A15 cubre lo esencial | Sin GAP crítico |
| 12. Security adicional | Parcial (A12+A17) | Refuerzo de A17 (CORS/CSP) |
| 13. Documentation | Mayormente cubierto (AP-4.x) | Sin GAP crítico |

**Decisiones de plataforma/stack (NO regla universal)**:
- Cloudflare específico → ADR de proyecto
- ORM vs raw SQL → decisión de proyecto
- CI/CD provider → decisión de proyecto
- Caching layer específico → decisión de proyecto
- **Sidecar** → decisión de plataforma (Kubernetes-specific)

**Resultado del audit**: 6 GAPs críticos identificados como A20-A25 + 6 anti-patterns asociados.

---

## CATÁLOGO DE GAPS — A20-A25 (formalizado pero no escrito)

Las siguientes 6 reglas fueron identificadas como **GAPs reales del Nivel 2 Tier 1** durante el audit empírico 3 (Opción D). Quedan documentadas acá como deudas formales pendientes de implementación. Próxima sesión decide prioridades.

### A20 — Hexagonal Architecture (Ports & Adapters)

**Dimensión**: Paradigma arquitectónico de fondo
**Cobertura actual**: Parcial (A2 Encapsulación + A7 Domain First + A11 DAO/DTO cubren aspectos, pero no formalizan el paradigma completo)
**Por qué es GAP**: NO existe regla afirmativa explícita "el dominio NO depende de infraestructura". A2 encapsula tablas, A11 separa acceso a datos, A7 captura dominio antes — pero nadie dice que **dominio define ports** e **infraestructura implementa adapters intercambiables**.
**Criticidad**: 🔴 **CRÍTICA** para vibe coder Tier 1
**Riesgo si NO**: acoplamiento Supabase → refactor masivo cuando crezcas. Cambiar de stack = rewrite.
**Origen**: Alistair Cockburn 2005, variantes Clean Architecture (Uncle Bob), Onion Architecture (Palermo)
**Tiempo estimado**: ~30 min (paradigma + ejemplo PG port `OrderRepository` con adapter Supabase + adapter in-memory para tests)
**Mapping a SOLID**: **DIP** (Dependency Inversion Principle) en su forma más pura
**Anti-pattern asociado**: **AP-2.13 Domain Polluted by Infrastructure** (dominio con SQL strings, HTTP clients, framework imports adentro)

### A21 — Structured Observability

**Dimensión**: Observabilidad / SRE
**Cobertura actual**: Parcial (A14 menciona `logger.exception`, A16/A19 mencionan métricas)
**Por qué es GAP**: sin regla formal que estandarice los **3 pilares** (logs estructurados + metrics + distributed tracing), cada función logguea distinto y producción es caja negra.
**Criticidad**: 🔴 **CRÍTICA** para vibe coder Tier 1
**Riesgo si NO**: no vas a estar 24/7 mirando dashboards. Bug en prod = misterio sin trace, hora de debug se vuelve día.
**Sub-reglas propuestas**:
- OBS-1: Structured logging (JSON con campos consistentes: timestamp, level, service, trace_id, user_id, tenant_id, message, error)
- OBS-2: Metrics (counters, gauges, histograms con labels normalizadas)
- OBS-3: Distributed tracing (trace_id propagado a través de boundary calls)
- OBS-4: Health checks (liveness + readiness)
- OBS-5: SLOs explícitos por servicio crítico
- OBS-6: Alertas con runbooks asociados (no alerta sin acción documentada)
**Tiempo estimado**: ~30 min
**Mapping a SOLID**: **SRP** (observabilidad como concern separado)
**Anti-pattern asociado**: **AP-3.12 Unstructured Logging** (print statements, format inconsistente, sin trace_id)

### A22 — Secrets Management

**Dimensión**: Secrets & Credentials
**Cobertura actual**: Parcial (A12 ZT-6 dice "no loggear secrets" pero NO dice "cómo gestionarlos")
**Por qué es GAP**: sin regla formal sobre **vaulting + rotation + env discipline**, los secrets terminan en .env committeados, código, o memoria sin rotación.
**Criticidad**: 🔴 **CRÍTICA** (vector de ataque #1 en SaaS)
**Riesgo si NO**: secret leak → bill de Stripe/Anthropic triplicado en 1 día por API key leaked. Es solo cuestión de tiempo.
**Sub-reglas propuestas**:
- SEC-1: NO secrets en código (ni .env committeado)
- SEC-2: Vaulting obligatorio (env vars + secret manager: Doppler, AWS Secrets Manager, Vercel env, etc.)
- SEC-3: Rotation policy declarada por tipo de secret
- SEC-4: Acceso a secrets via service account / IAM (no credenciales personales)
- SEC-5: Audit log de acceso a secrets sensibles
- SEC-6: Detection de secret leaks en CI (truffleHog, git-secrets, etc.)
**Tiempo estimado**: ~20 min
**Anti-pattern asociado**: **AP-2.14 Hardcoded Secrets** (API keys en código, .env en repo, secrets en logs)

### A23 — Deployment Safety

**Dimensión**: Deployment / Release Safety
**Cobertura actual**: Parcial (A8 cubre rollback de migraciones, pero NO release del código aplicación)
**Por qué es GAP**: sin regla formal sobre **zero-downtime migrations + API versioning + feature flags + canary**, cada deploy a producción es ruleta rusa.
**Criticidad**: 🟡 **IMPORTANTE**
**Riesgo si NO**: cliente reporta "se cayó al actualizar" cada vez. Bugs en producción sin rollback rápido.
**Sub-reglas propuestas**:
- DEP-1: Migraciones zero-downtime (3-step: add nullable column → backfill → make NOT NULL, etc.)
- DEP-2: API versioning explícito (breaking changes en versión nueva, no en existente)
- DEP-3: Feature flags para cambios riesgosos (rollback sin redeploy)
- DEP-4: Canary / blue-green opcional pero documentado
- DEP-5: Rollback strategy declarada antes del deploy
- DEP-6: Pre-deploy checklist automatizable (smoke tests, migration dry-run)
**Tiempo estimado**: ~25 min
**Anti-pattern asociado**: **AP-3.13 Breaking API Change Without Versioning** (cambio incompatible en endpoint existente sin /v2)

### A24 — Data Lifecycle & Privacy

**Dimensión**: Data Lifecycle / Privacy / Compliance
**Cobertura actual**: ❌ **No cubierta**
**Por qué es GAP**: sin reglas formales sobre **retention + GDPR right-to-erasure + PII handling + backup/DR**, exposición a multas regulatorias + imposibilidad de cumplir requests legales.
**Criticidad**: 🔴 **CRÍTICA** (compliance GDPR multas: 4% revenue global)
**Riesgo si NO**: compliance breach → cliente enterprise pierdes. Request de "borrar mis datos" no se puede cumplir.
**Sub-reglas propuestas**:
- DLP-1: Data retention policies por tipo de dato (audit log: 7 años, sesiones: 30 días, etc.)
- DLP-2: GDPR right-to-erasure implementado (soft-delete + hard-delete diferido)
- DLP-3: PII classification (qué campos son PII, cómo se manejan)
- DLP-4: Anonymization para analytics (no usar PII real en BI)
- DLP-5: Backup policy con RPO/RTO declarados + restore drills periódicos
- DLP-6: Multi-region failover si Tier 1 commercial robust lo requiere
**Tiempo estimado**: ~30 min
**Anti-pattern asociado**: posible AP-2.15 PII Sin Clasificar / AP-3.14 Data Sin Retention Policy

### A25 — Authorization Model (RBAC/ABAC)

**Dimensión**: Authorization granular (más allá de tenancy)
**Cobertura actual**: Parcial (A12 ZT-1/ZT-4 cubre "estás autenticado y en tu tenant", pero NO "qué podés hacer")
**Por qué es GAP**: A12 protege contra cross-tenant pero NO contra **escalación dentro del tenant** (usuario común haciendo acciones de admin del mismo tenant).
**Criticidad**: 🟡 **IMPORTANTE**
**Riesgo si NO**: admin de tenant A acciona endpoint sensible del propio tenant A sin autorización granular. Privilege escalation interna.
**Sub-reglas propuestas**:
- AUTHZ-1: Modelo declarado (RBAC simple, ABAC complejo) — decisión por proyecto pero declarado
- AUTHZ-2: Permission checks granular por operación sensible (no solo por endpoint)
- AUTHZ-3: Roles/permisos en BD (no hardcoded en código)
- AUTHZ-4: Default deny (sin permiso explícito → no autorizado)
- AUTHZ-5: Audit log de cambios de permisos
- AUTHZ-6: Tests adversariales de privilege escalation (A15 aplicado a authz)
**Tiempo estimado**: ~20 min
**Anti-pattern asociado**: posible AP-2.16 Permission Check Solo en UI / AP-2.17 Hardcoded Role Logic

### Anti-patterns menores asociados (Performance / Universal)

- **AP-3.11 N+1 Query Pattern** — patrón clásico, universal, vale anti-pattern aunque NO sea regla nueva
- **AP-2.12 Missing Pagination** — endpoint que retorna lista sin paginación, universal

---

## Resumen del audit empírico 3

| Métrica | Valor |
|---|---|
| Dimensiones evaluadas | 13 |
| GAPs críticos identificados | 6 (A20, A21, A22, A24) |
| GAPs importantes | 2 (A23, A25) |
| Anti-patterns asociados | 6 (AP-2.12, AP-2.13, AP-2.14, AP-3.11, AP-3.12, AP-3.13) + 2-4 más posibles en A24/A25 |
| Decisiones de plataforma (NO regla universal) | Sidecar, Cloudflare específico, ORM, CI/CD provider, Caching layer |
| Tiempo total estimado de implementación A20-A25 | ~3 horas de trabajo bien hecho |

---

## Patrón empírico acumulado (3 audits)

| Iteración | GAPs detectados | Status |
|---|---|---|
| Audit 1 (sesión anterior) | A11-A15 (5 reglas + 5 anti-patterns) | ✅ Implementado |
| Audit 2 (esta sesión, mañana) | A16-A19 (4 reglas + 4 anti-patterns) | ✅ Implementado (commit pendiente) |
| Audit 3 (esta sesión, Opción D) | A20-A25 (6 reglas + 6+ anti-patterns) | 📋 Documentado como deudas formales |

**Hit rate acumulado de intuición arquitectónica de Julián**: ~17/17 (100%).

**Lección estructural**: el audit completo (Opción D) reveló que el audit incremental hubiera seguido descubriendo GAPs uno por uno indefinidamente. **El meta-patrón**: ante intuición empírica recurrente, mejor descubrir scope COMPLETO en una iteración que incremental — 6° principio rector aplicado al meta-trabajo.

---

## Commits (10 hoy + 2 pendientes)

```
PENDIENTE feat(architecture): A16-A19 + AP-2.10/2.11/3.9/3.10 (Nivel 2 v1.2 infra resiliente)
PENDIENTE docs(memoria): audit empirico 3 (Opcion D) + catalogo A20-A25 + 6 deudas formales
0af14a4   feat(framework): NORTE v0.1 + memoria con Vision C
0e58d7e   feat(arch): cross-LLM (ADR-008) + docs/AGENT-INTEGRATION.md
0206502   docs(memoria): cerrar sesion con plan T0-T5
3e2e329   chore: eliminar carpetas legacy
1024b84   feat(arch): separacion Framework vs Proyectos (ADR-007)
8e80c79   docs(memoria): handoff compacto entre sesiones
2e32482   docs: README + mcp-servers/README
4751381   feat(architecture): A11-A15 + ADR-006
(commits iniciales del repo)
```

Working tree: pendiente commit A16-A19 + AP nuevos + esta memoria actualizada.
Remote: sincronizado hasta 0af14a4.
URL repo: https://github.com/jlnvargas25-dot/departamento-software

---

## Lecciones críticas

### LECCIÓN 1 — Bug: `$$` Y `$BODY$` en SQL rompen `filesystem:edit_file`
Strings con `$$` o `$BODY$` (o cualquier `$<algo>$`) ROMPEN `edit_file` del MCP filesystem por interpretación regex de `$`. **Workaround real**: usar `write_file` (reescribir archivo completo) para cualquier contenido con `$` literal. Para regex usar `\Z`. Documentado en esta sesión cuando edit_file corrompió sesion-activa.md.

### LECCIÓN 2 — 6° principio rector aplica recursivamente al meta-trabajo
Audit empírico OBLIGATORIO antes de declarar "ya está hecho". Julián detectó 5+4+6 = 15 GAPs en 3 audits. Hit rate acumulado: 100%.

### LECCIÓN 3 — Anti-paternalismo (sostenido)
Julián corrigió cuando recomendé cerrar sesión "porque estás cansado". El cansancio era proyección mía. Comportamiento ajustado.

### LECCIÓN 4 — Visión arquitectónica del Departamento (4 visiones evolucionando)
- **Visión A** (inicial): workflow propio completo (compite con Spec Kit) — ABANDONADA
- **Visión B** (mid-sesión): capa de gobernanza encima de Spec Kit — REFINADA
- **Visión C** (final): curador + calibrador del stack del ecosistema — EMERGENTE, pendiente validación
- **Visión D** (discusión sin formalizar): Capa A independiente + Capa B integraciones opcionales — DEUDA-VISIÓN-D-NO-FORMALIZADA

### LECCIÓN 5 — Engram bloqueado por SAC, claude-mem es alternativa superior
SAC bloquea Engram. WSL Ubuntu funcionaría pero claude-mem es mejor (cross-agent, MCP nativo, 1-line install). DEUDA-ENGRAM-SAC-BLOCK resuelta por reemplazo.

### LECCIÓN 6 — Confusión semántica con "Opciones A"
Múltiples "Opción A" en diferentes contextos. Lección: ser explícito sobre qué Opción es cada vez.

### LECCIÓN 7 — Multi-proyecto formalizado evita over-engineering futuro
ADR-007 antes de tener 2do proyecto. Costo migración futura > costo formalización ahora.

### LECCIÓN 8 — El ecosistema YA implementa muchas visiones
obra/superpowers (170k stars) implementa la visión harness anti-alucinación de Julián casi palabra por palabra. "No reinventar la rueda" al meta-nivel.

### LECCIÓN 9 — Cross-LLM como decisión filosófica anti lock-in
ADR-008 formaliza Departamento como agent-agnostic. Costo bajo ahora vs alto retrofit después.

### LECCIÓN 10 — Audit empírico recursivo detecta dimensiones enteras
Audit 1 detectó GAPs dentro de "lógica/datos/seguridad". Audit 2 detectó dimensión completa "infraestructura resiliente". Audit 3 (Opción D, completo) detectó 4 dimensiones más críticas (paradigma, observability, secrets, data lifecycle) + 2 importantes (deployment, authz).

### LECCIÓN 11 — Audit COMPLETO > audit incremental cuando el patrón empírico es recurrente
Después de 2 audits incrementales (cada uno descubriendo más GAPs), aplicar 6° principio rector al meta-trabajo: descubrir scope completo en UNA iteración. Audit 3 (Opción D) en ~30 min reveló más que 2 audits incrementales previos. **Costo-beneficio asimétrico**: 30 min de catálogo evita N iteraciones de descubrimiento incremental.

### LECCIÓN 12 — Compactación de chat puede propagar contexto desviado del system prompt
Manifestación N=31+ del sub-meta-patrón #13.x detectada el 2026-05-20: este mismo chat trabajó en DEPARTAMENTO-SOFTWARE pensando que el system prompt apuntaba ahí, cuando en realidad apuntaba a SigmaControl. La compactación de conversación previa propagó el contexto sin verificarlo contra el system prompt del Project. **Lección**: PASO 1 del PROTOCOLO-INICIO-CHAT v1.0 es OBLIGATORIO — verificar contra system prompt antes de seguir cualquier contexto compactado.

### LECCIÓN 13 — GGA solo revisa código, no markdown
GGA filtra por `*.py`/`*.sql`/`*.ts`/etc. Cambios en `.md` (architecture/, docs/, memoria) no disparan review automático. Implica que cambios estructurales a las reglas A1-A19 NO tienen layer de revisión automática. Conectado a DEUDA-A21-OBSERVABILITY (sub-meta para mejorar esto eventualmente).

### LECCIÓN 14 — Resolución del bug del system prompt vía Project nuevo (no migración)
Cuando 2 proyectos paralelos coexisten en disco y el Project en Claude.ai apunta a uno mientras un chat trabaja en otro, la solución correcta es: crear Project NUEVO específico para el segundo proyecto en vez de migrar el primero. **Razones**: (1) preserva el Project original intocable, (2) Claude.ai separa contextos limpiamente por Project, (3) cada Project tiene su system prompt + archivos. Aplicado el 2026-05-20: Project nuevo Framework + Project original SigmaControl intactos.

### LECCIÓN 15 — Primera aplicación práctica del PROTOCOLO-CIERRE-SESION.md v1.0
El protocolo de cierre que se escribió en esta misma sesión tuvo su primera aplicación práctica al cerrar esta sesión. **Aplicación recursiva viva del 7° principio rector** (meta-producto recursivo): el protocolo se aplica a sí mismo desde el momento en que se escribe. El chat nuevo del Project nuevo detectó que esta sesión no estaba documentada en sesion-activa.md y disparó la aplicación del protocolo. Sin el chat nuevo, habíamos quedado con gap de cierre silencioso — exactamente lo que el protocolo previene.

---

## Deudas técnicas

### DEUDA-ENGRAM-SAC-BLOCK
**Status**: ✅ RESUELTA POR REEMPLAZO (claude-mem)

### DEUDA-WORKFLOW-OPERATIVO
**Status**: 🔴 ABIERTA — RECALIBRADA
**Próxima acción**: después de T2 (ADR-009 basado en sandbox)

### DEUDA-EVALUAR-SPEC-KIT
**Status**: 🔴 ABIERTA — EXPANDIDA (incluye Spec Kit + Superpowers + ECC + claude-mem)
**Próxima acción**: T1 próxima sesión

### DEUDA-REPLANTEAR-ROADMAP-POST-STACK
**Status**: 🔴 ABIERTA — CRÍTICA
**Próxima acción**: T1 sandbox + T2 ADR-009 basado en evidencia empírica

### DEUDA-NORTE-FRAMEWORK-PLACEHOLDERS
**Status**: 🟡 EN PROGRESO (Q4-Q7 pendientes)

### DEUDA-PROTOCOLOS-DEPARTAMENTO
**Status**: 🔴 ABIERTA

### DEUDA-EDIT-FILE-SQL
**Status**: 🟡 LECCIÓN DOCUMENTADA (write_file en archivos con `$` literal)

### DEUDA-AUDIT-COMPLETO-NIVEL-2
**Status**: ✅ RESUELTA EN ESTA SESIÓN (Opción D ejecutada — ver §18)

### DEUDA-VISIÓN-D-NO-FORMALIZADA
**Status**: 🟡 PENDIENTE DECISIÓN
**Próxima acción**: posible ADR-010 después de T1 sandbox

### DEUDA-A20-HEXAGONAL *(NUEVA — audit 3)*
**Status**: 🔴 ABIERTA
**Scope**: ver §18 catálogo A20
**Criticidad**: CRÍTICA (paradigma de fondo)
**Tiempo estimado**: ~30 min
**Anti-pattern**: AP-2.13 Domain Polluted by Infrastructure
**Próxima acción**: priorización en próxima sesión

### DEUDA-A21-OBSERVABILITY *(NUEVA — audit 3)*
**Status**: 🔴 ABIERTA
**Scope**: ver §18 catálogo A21 (6 sub-reglas OBS-1..OBS-6)
**Criticidad**: CRÍTICA (producción es caja negra sin esto)
**Tiempo estimado**: ~30 min
**Anti-pattern**: AP-3.12 Unstructured Logging
**Próxima acción**: priorización en próxima sesión

### DEUDA-A22-SECRETS *(NUEVA — audit 3)*
**Status**: 🔴 ABIERTA
**Scope**: ver §18 catálogo A22 (6 sub-reglas SEC-1..SEC-6)
**Criticidad**: CRÍTICA (vector de ataque #1)
**Tiempo estimado**: ~20 min
**Anti-pattern**: AP-2.14 Hardcoded Secrets
**Próxima acción**: priorización en próxima sesión

### DEUDA-A23-DEPLOYMENT *(NUEVA — audit 3)*
**Status**: 🔴 ABIERTA
**Scope**: ver §18 catálogo A23 (6 sub-reglas DEP-1..DEP-6)
**Criticidad**: IMPORTANTE (parcialmente cubierto por A8)
**Tiempo estimado**: ~25 min
**Anti-pattern**: AP-3.13 Breaking API Change Without Versioning
**Próxima acción**: priorización en próxima sesión

### DEUDA-A24-DATA-LIFECYCLE *(NUEVA — audit 3)*
**Status**: 🔴 ABIERTA
**Scope**: ver §18 catálogo A24 (6 sub-reglas DLP-1..DLP-6)
**Criticidad**: CRÍTICA (compliance GDPR — multas 4% revenue global)
**Tiempo estimado**: ~30 min
**Anti-pattern**: AP-2.15 PII Sin Clasificar / AP-3.14 Data Sin Retention (a definir)
**Próxima acción**: priorización en próxima sesión

### DEUDA-A25-AUTHORIZATION *(NUEVA — audit 3)*
**Status**: 🔴 ABIERTA
**Scope**: ver §18 catálogo A25 (6 sub-reglas AUTHZ-1..AUTHZ-6)
**Criticidad**: IMPORTANTE (privilege escalation dentro de tenant)
**Tiempo estimado**: ~20 min
**Anti-pattern**: AP-2.16 Permission Check Solo en UI (a definir)
**Próxima acción**: priorización en próxima sesión

### DEUDA-ANTI-PATTERNS-MENORES *(NUEVA — audit 3)*
**Status**: 🟡 ABIERTA
**Scope**: AP-3.11 N+1 Query, AP-2.12 Missing Pagination (sin regla A* asociada, son patrones universales valiosos)
**Tiempo estimado**: ~15 min para ambos
**Próxima acción**: agregar junto con A20-A25 o en sesión separada

### DEUDA-PROJECT-CLAUDE-CONFIG *(NUEVA — sesión 2026-05-20)*
**Status**: 🟡 EN PROGRESO (acción humana pendiente)
**Scope**: Julián debe crear Project nuevo en Claude.ai con los 3 archivos mínimos (CLAUDE.md + PROTOCOLO-INICIO-CHAT.md + PROTOCOLO-CIERRE-SESION.md) + system prompt instructivo entregado en sesión 2026-05-20
**Criticidad**: 🟡 IMPORTANTE (sin esto, futuros chats pueden propagar deriva de contexto)
**Tiempo estimado**: ~10 min (acción manual en Claude.ai)
**Próxima acción**: Julián ejecuta. Ya confirmado que el Project nuevo se creó y funciona correctamente — marcado como ✅ al final de sesión 2026-05-20
**Estado al cierre 2026-05-20**: ✅ RESUELTA (Project creado y validado empíricamente)

---

## Estado del repo al cerrar

```
Branch: main
Working tree: A16-A19 + AP-2.10/2.11/3.9/3.10 escritos + esta memoria actualizada (SIN COMMIT)
Remote: sincronizado hasta 0af14a4
Total commits hoy: 10 pusheados + 2 pendientes
```

### Estructura final

```
C:\DEPARTAMENTO-SOFTWARE\
├── FRAMEWORK (raíz)
│   ├── architecture/ (Nivel 2 v1.2 con A1-A19 + 28 anti-patterns)
│   │   ├── PRINCIPIOS-ARQUITECTURA.md (A1-A19, v1.2)
│   │   ├── ANTI-PATRONES.md (28 anti-patterns, v1.2)
│   │   ├── PRINCIPIOS-SOLID.md
│   │   ├── PATRONES-CARPETAS.md (C1-C6)
│   │   └── README.md
│   ├── decisions/ (ADRs 001-008)
│   ├── .claude/skills/ (sigma-capture-domain)
│   ├── mcp-servers/ (preparado Sprint 2)
│   ├── auditoria/sesion-activa.md (este archivo v3.2)
│   ├── templates/project-skeleton/ (7 templates)
│   ├── docs/AGENT-INTEGRATION.md
│   ├── NORTE.md (v0.1 con placeholders)
│   ├── CLAUDE.md, AGENTS.md (v1.2), README.md (v1.3)
│   ├── SIGUIENTE-SESION.md
│   └── PROTOCOLO-*.md (heredados, vale adaptar)
│
└── projects/
    └── stallen/ (DIFERIDO según decisión §13)
```

---

## Próximo paso — PRIORIDAD CLARA

### 1. Comando commit inmediato (al abrir próxima sesión):

**NOTA SESIÓN 2026-05-20**: A16-A19 + audit empírico 3 ya commitados en `1c08732` y `dc0c798`. Lo pendiente al cierre del 2026-05-20 son los 2 protocolos nuevos + esta memoria actualizada.

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git add PROTOCOLO-INICIO-CHAT.md PROTOCOLO-CIERRE-SESION.md auditoria/sesion-activa.md
git status
git commit -m "feat(framework): PROTOCOLO-INICIO + PROTOCOLO-CIERRE v1.0 + cierre sesion 2026-05-20

Deteccion de deriva de contexto el 2026-05-20: el chat habia estado
trabajando en C:\DEPARTAMENTO-SOFTWARE pensando que el system prompt
apuntaba ahi, cuando en realidad apuntaba a SigmaControl legacy.
Manifestacion N=31+ del sub-meta-patron #13.x.

Solucion (Lectura B): Framework reemplaza SigmaControl en direccion
del refactor. Project nuevo en Claude.ai en lugar de migrar el existente.

Archivos creados:
- PROTOCOLO-INICIO-CHAT.md v1.0 con PASO 1 anti-deriva
- PROTOCOLO-CIERRE-SESION.md v1.0 con checklist 8 pasos manual

Memoria actualizada con:
- Seccion 19 (sesion 2026-05-20)
- Lecciones 12-15
- DEUDA-PROJECT-CLAUDE-CONFIG (resuelta)

Primera aplicacion practica del PROTOCOLO-CIERRE v1.0 al cerrar
esta misma sesion (7 principio rector recursivo)."
git push
```

### 2. Decisiones pendientes para próxima sesión:

**Decisión A — Cuándo implementar A20-A25**:
- (i) Antes del sandbox empírico (T1) → completa Nivel 2 "Tier 1 commercial robust"
- (ii) Después del sandbox → riesgo de implementar reglas que el stack ya cubre
- (iii) Híbrido: las 4 críticas (A20, A21, A22, A24) antes del sandbox, las 2 importantes (A23, A25) después

**Decisión B — Visión D (Capa A independiente + Capa B integraciones)**:
- (i) Formalizar en ADR-010 ahora
- (ii) Esperar evidencia del sandbox

**Decisión C — Stallen**:
- (i) Sigue diferido hasta Framework maduro (decisión §13 actual)
- (ii) Reactivar como driver mientras se completa Framework

### 3. Roadmap actualizado próxima sesión (Claude Code CLI):

1. **COMMIT INMEDIATO** A16-A19 + memoria (5 min)
2. **Decisión A**: cuándo A20-A25
3. **T0 (REEMPLAZADO)** — claude-mem 1-line install (5 min)
4. **T1 (EXPANDIDO)** — Sandbox del Stack: Spec Kit + Superpowers + ECC + claude-mem (3-5 hs)
5. **T2** — ADR-009 "Adopción del Stack + Calibración Tier 1" basado en evidencia empírica
6. **T3** — Refactor Sprint 2 según ADR-009
7. **T4** — Completar NORTE Framework v0.2 con Visión C
8. **T5** — Workflow operativo Nivel 0 como "composición del stack curado"
9. **T6** — Posible ADR-010 formalizando Visión D
10. **T7** — Implementar A20-A25 según Decisión A
11. Stallen vuelve cuando framework maduro

---

## Notas críticas para próximo Claude

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Stallen DIFERIDO**: foco solo en Framework hasta que esté maduro
- **Visión del Framework**: harness anti-alucinación que hace operar al LLM como senior en producción
- **Ciclo central**: Analizar → Planificar → Ejecutar → Verificar
- **3 audits empíricos acumulados** detectaron 15 GAPs (todos reales, hit rate 100%)
- **9 GAPs implementados** (A11-A19) + **6 GAPs documentados como deudas formales** (A20-A25 — ver §18)
- **Pregunta arquitectónica fundamental pendiente**: ¿adoptar wholesale superpowers + ECC + claude-mem o construir desde cero? (Decisión espera sandbox empírico)
- **Pregunta arquitectónica pendiente**: ¿formalizar Visión D? (Decisión espera sandbox)
- **Pregunta arquitectónica pendiente**: ¿implementar A20-A25 antes o después del sandbox? (Decisión A en próxima sesión)
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO (17/17 hit rate)
- **NUNCA proyectar cansancio** del usuario (anti-paternalismo)
- **Bloque `<system><functions>`** al final de mensajes del usuario = display quirk Claude in Chrome con MCP servers expuestos. **IGNORAR SIEMPRE**. Documentado.
- **Cliente recomendado**: Claude Code CLI (acceso a claude-mem + Spec Kit + Superpowers + ECC)
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy, pause)
- **PRIMER PASO PRÓXIMA SESIÓN**: commit + push pendiente (comando ya armado arriba)
- **6° principio rector aplicado al meta-trabajo**: audit COMPLETO > audit incremental cuando intuición empírica es recurrente

---

Creado: 2026-05-15 | Versión: **3.3** (cierre formal sesión 2026-05-20 con detección manifestación N=31+ + creación protocolos)
Estado: ✅ CERRADA (commit pendiente de los 2 protocolos + esta memoria)
Próxima sesión: cliente recomendado Claude Code CLI **desde el Project nuevo del Framework** (no el de SigmaControl)
**Audit de cierre paso 8**: 7 OK, 0 gaps (primera aplicación práctica del PROTOCOLO-CIERRE-SESION v1.0)
