# SISTEMA DE TRABAJO — Manual Operativo del Departamento

**Versión**: 1.0 (2026-05-13)
**Estado**: Manual fundacional
**Documentos relacionados**:
- `DEPARTAMENTO-DE-SOFTWARE.md` — arquitectura completa
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` — protocolo determinístico

---

## PROPÓSITO

Este manual define cómo se trabaja día-a-día en el Departamento de Software. Mientras la arquitectura describe QUÉ es el sistema y el protocolo describe los PASOS obligatorios, este manual responde el CÓMO operativo concreto.

Audiencia: el operador humano (vos), agentes IA que ejecutan tareas, y eventualmente nuevos miembros del departamento.

---

## 1. ESTACIONES DE TRABAJO

El departamento opera con 4 estaciones de trabajo (workflows reconocibles). Cada estación tiene su propio entrypoint, herramientas y criterios de cierre.

| Estación | Cuándo se usa | Duración típica | Entrypoint |
|---|---|---|---|
| **Estación Feature** | Funcionalidad nueva | 3-15 días | `/sigma:new-feature` |
| **Estación Bug Fix** | Corregir error en producción | 1-3 días | `/sigma:fix-bug` |
| **Estación Refactor** | Mejorar código existente sin cambiar funcionalidad | 2-7 días | `/sigma:refactor` |
| **Estación Spike** | Investigación técnica (sin compromiso de producción) | 1-2 días | `/sigma:spike` |

Cada estación aplica el protocolo de construcción con scale-adaptive: features grandes usan workflow full (12 pasos), bug fixes pueden usar workflow light (skip diseño arquitectónico, ir directo a fix + tests).

---

## 2. WORKFLOW: ESTACIÓN FEATURE COMPLETA

### Día 0 — Iniciar feature

**Quién**: Operador humano (vos) + Analista de Producto (agente IA)

**Acciones**:
1. Crear branch:
   ```bash
   git checkout -b feature/YYYY-MM-DD-nombre-descriptivo
   ```
2. Crear directorio de la feature:
   ```bash
   mkdir -p openspec/changes/YYYY-MM-DD-nombre-descriptivo
   ```
3. Invocar skill de inicio:
   ```
   /sigma:new-feature nombre-descriptivo
   ```
4. El skill prompts por información inicial:
   - ¿Qué problema resuelve?
   - ¿Quién es el usuario afectado?
   - ¿Cómo se medirá el éxito?
   - ¿Qué está OUT of scope?

**Output**: `prd.md` inicial generado, listo para review.

### Día 1 — Capturar dominio

**Quién**: Captor de Dominio (agente IA con supervisión humana)

**Acciones**:
1. Invocar skill de captura:
   ```
   /sigma:capture-domain
   ```
2. El sistema analiza el PRD y consulta `adn-proyecto.json` para identificar:
   - Qué módulos canónicos toca la feature
   - Qué reglas de dominio aplican
   - Qué reglas nuevas se necesitan
3. Para reglas nuevas, ejecuta clasificación 3 pasos automáticamente
4. Si hay huecos reales, el sistema **dispara solicitudes via tubería bidireccional**:
   ```
   ⚠️ SOLICITUD SOL-20260513-093045-123456: regla_DOM-X
      "Necesito tablas que toca la función Y. Opciones detectadas: [A, B, C]"
      ¿Cuál es la respuesta?
   ```
5. Vos respondés via comando:
   ```
   /sigma:respond-solicitud SOL-20260513-093045-123456 "tabla_origen: A, tabla_destino: B"
   ```
6. El sistema actualiza `adn-proyecto.json` con delta marker

**Output**: ADN actualizado con completitud ≥ 95%, `adn-delta.md` documentado.

### Día 2 — Arquitectura

**Quién**: Arquitecto (agente IA con review humano)

**Acciones**:
1. Invocar skill:
   ```
   /sigma:design-architecture
   ```
2. El agente propone diseño basado en PRD + ADN + decisiones técnicas previas
3. Vos reviews el design.md:
   - ¿Los componentes están bien identificados?
   - ¿Las dependencias son las correctas?
   - ¿Hay riesgos no identificados?
4. Si hay decisión técnica no obvia, el agente crea ADR automáticamente
5. Iterar hasta que diseño esté sólido

**Output**: `design.md` validado + ADRs si aplica.

### Día 3 — Planificación

**Quién**: Planificador (Scrum Master agente)

**Acciones**:
1. Invocar skill:
   ```
   /sigma:plan-stories
   ```
2. El agente descompone diseño en stories ejecutables:
   - Cada story tiene acceptance criteria en formato Given/When/Then
   - Cada story tiene estimación de complejidad
   - Stories priorizadas por dependencias
3. Vos reviews el backlog:
   - ¿Las stories son del tamaño correcto?
   - ¿Acceptance criteria son verificables?
   - ¿Falta alguna story?
4. Audit del plan (validadores R01-R15) automático

**Output**: `stories.md` + `tasks.md` + `audit-plan.json` con 0 críticos.

### Días 4-N — Construir

**Quién**: Desarrolladores Backend/Frontend (agentes IA)

**Por cada story** (en orden de dependencias):

1. Seleccionar story:
   ```
   /sigma:work-story STORY-XX
   ```
2. El agente implementa código respetando design.md y acceptance criteria
3. Tests unitarios generados automáticamente
4. Validadores corren en pre-commit:
   - Si linters fallan → no se hace commit
   - Si type check falla → no se hace commit
5. Commit:
   ```bash
   git commit -m "feat(STORY-XX): descripción concisa"
   ```
6. Validadores G/FG corren post-commit (Capa 3)
7. Si auditoría tiene críticos → fix antes de avanzar

**Output**: Código con tests, commits identificables por story.

### Día N+1 — Auditar código

**Quién**: Auditor de Código (Python determinístico)

**Acciones**:
1. Invocar audit completo:
   ```
   /sigma:audit-code
   ```
2. El sistema corre TODOS los validadores:
   - G1-G33 backend
   - FG1-FG14 frontend
   - SOLID structural
   - Zero-trust security
   - Errores silenciosos
3. Auto-fix donde aplique (patcher determinístico)
4. Reporte con findings ordenados por severidad
5. Para críticos sin auto-fix → escalación al humano

**Output**: `audit-code.json` con 0 críticos finales.

### Día N+2 — Tests adversariales

**Quién**: Test Architect (agente IA)

**Acciones**:
1. Invocar:
   ```
   /sigma:adversarial-tests
   ```
2. El agente genera tests adversariales para cada función nueva:
   - Inputs vacíos, None, strings vacíos, listas vacías
   - Boundary conditions
   - Network failures
   - Concurrent access
   - DB failures
3. Verifica coverage ≥ 80%
4. Ejecuta tests en paralelo + secuencial (detectar race conditions)

**Output**: Tests adversariales agregados, coverage validado.

### Día N+3 — Seguridad

**Quién**: Auditor de Seguridad

**Acciones**:
1. Invocar:
   ```
   /sigma:security-audit
   ```
2. Corre suite completa:
   - bandit, semgrep, gitleaks, snyk, trivy
   - RLS validation
   - Config schemas validation
   - Migrations idempotency
3. 0 críticos → green light para deploy

**Output**: `security-audit.json` clean.

### Día N+4 — Deploy

**Quién**: DevOps + revisión humana

**Acciones**:
1. CI/CD pipeline corre todo el suite
2. Si green → deploy autorizado
3. Comando de deploy:
   ```
   /sigma:deploy
   ```
4. Smoke tests post-deploy automáticos
5. Si fallan → rollback automático
6. Verificación 24h con dashboard

**Output**: Feature en producción + log de deploy.

### Día N+5 — Cierre

**Quién**: Memoria Institucional (sistema)

**Acciones**:
1. Invocar cierre:
   ```
   /sigma:close-session
   ```
2. El sistema ejecuta los 9 pasos del protocolo de cierre:
   - Documentar lo hecho
   - Actualizar SIGUIENTE-SESION
   - Verificar docs tocados
   - Actualizar índice
   - Memoria Engram
   - Verificar consistencia
   - Radar de deuda
   - Radar de polinización
   - Git commit + push
3. Retrospectiva opcional cada N features

**Output**: Sesión formalmente cerrada, memoria actualizada, git al día.

---

## 3. WORKFLOW: ESTACIÓN BUG FIX (light)

Para bugs simples, scale-adaptive aplica workflow reducido:

1. **Reproducir bug** (escribir test que falla):
   ```
   /sigma:reproduce-bug
   ```
2. **Análisis de root cause**:
   ```
   /sigma:root-cause
   ```
   - Lee logs, código relevante
   - Identifica causa raíz
3. **Fix**:
   ```
   /sigma:fix-bug STORY-XX
   ```
4. **Auditar código** (paso 7 del protocolo):
   ```
   /sigma:audit-code
   ```
5. **Tests adversariales del bug** (no solo el test del bug):
   - ¿Qué otras condiciones podrían triggerar el mismo patrón?
   - Generar tests para todos
6. **Polinización OBLIGATORIA**:
   - ¿Este bug pertenece a meta-patrón conocido?
   - Si sí → agregar manifestación
   - Si no → crear meta-patrón nuevo
   - **Si bug ocurrió ≥ 3 veces conceptualmente** → crear regla preventiva
7. **Deploy** (skip diseño/planificación):
   ```
   /sigma:deploy --hotfix
   ```
8. **Cierre**:
   ```
   /sigma:close-session
   ```

**Tiempo típico**: 1-3 días (vs 5-15 días feature completa).

---

## 4. WORKFLOW: CODE REVIEW (cuando hay equipo)

Si en el futuro hay equipo humano:

### Para el autor del PR

Antes de crear PR:
1. Local: corrió `/sigma:audit-code` con 0 críticos
2. Local: tests pasan (incl. adversariales)
3. Local: smoke tests
4. CI green en branch propia
5. PR description usa template que referencia:
   - Story implementada
   - Acceptance criteria cumplidos
   - Findings de auto-fix aplicados
   - Tests adversariales agregados

### Para el reviewer

Antes de aprobar:
1. CI green (no override)
2. Validadores Departamento green
3. Coverage adversarial cumplido
4. Lectura de código: ¿claridad, mantenibilidad, no over-engineering?
5. Si dudas → comentarios concretos con sugerencias
6. **Polinización**: ¿este código sugiere patrón aplicable a otras partes?

### Reglas de merge

- 1 approval mínimo (cuando hay equipo)
- CI green obligatorio (no override)
- Branch up-to-date con master
- No "rubber stamp" approvals (reviewer debe responder ≥ 1 comentario o validar lectura)

---

## 5. SESIÓN DE TRABAJO DIARIA

### Inicio de sesión (cada vez que retomás trabajo)

1. **Verificar contexto** (lo hace el sistema):
   ```
   /sigma:resume
   ```
   El sistema lee:
   - `auditoria/sesion-activa.md` (qué se hizo última vez)
   - `SIGUIENTE-SESION.md` (qué hacer ahora)
   - Estado de feature en progreso
   - Deudas técnicas activas
2. **Pre-flight check**:
   ```bash
   # Validadores baseline
   python -m sigma_validators.preflight
   # Tests baseline
   pytest tests/baseline/
   # Git status
   git status
   ```
3. Si pre-flight green → continuar trabajo
4. Si falla → diagnosticar antes de avanzar

### Durante la sesión

- **Cada 1-2 horas**: commit local con mensaje descriptivo
- **Cada vez que se completa una story**: commit + push
- **Cada vez que se detecta dolor estructural**: anotar en `CUADERNO-BITACORA.md`
- **Cada vez que aparece duda de dominio**: usar tubería bidireccional
- **NUNCA**: trabajar sin acceptance criteria explícitos
- **NUNCA**: avanzar a próximo paso del protocolo sin gate verde

### Cierre de sesión

Antes de cerrar la terminal:
```
/sigma:close-session
```

El comando ejecuta el protocolo de cierre completo (9 pasos). NO se cierra a mano.

---

## 6. INTERACCIÓN HUMANO-IA

### Cuándo decide el humano

| Decisión | Por qué humano |
|---|---|
| ¿Qué feature construir próximo? | Estratégica, requiere contexto de negocio |
| ¿Cuál es el problema real? | Captura de intención subjetiva |
| ¿Cuál es el criterio de éxito? | Conocimiento del usuario final |
| ¿Esta decisión técnica vale la pena? | Trade-off costo/beneficio largo plazo |
| ¿Aceptar este riesgo identificado? | Tolerancia al riesgo del negocio |
| ¿Deploy a producción ahora? | Timing de negocio |
| ¿Aprobar bypass de gate con ADR? | Responsabilidad final |

### Cuándo decide la IA

| Decisión | Por qué IA |
|---|---|
| Implementar story con acceptance criteria claros | Mecánica |
| Generar tests adversariales por categoría | Patrón sistemático |
| Aplicar auto-fix donde regla es inequívoca | Determinístico |
| Identificar dependencias entre módulos | Análisis estructural |
| Detectar code smells | Reglas explícitas |
| Sugerir refactor por SOLID violation | Reglas explícitas |

### Cuándo decide el sistema (Python determinístico)

| Decisión | Por qué sistema |
|---|---|
| ¿Plan válido contra R01-R15? | Reglas codificadas |
| ¿Código válido contra G/FG? | Validadores deterministas |
| ¿Auto-fix aplicable? | Match contra patrón conocido |
| ¿Gate de capa 3/4 pasa? | Validadores objetivos |
| ¿Smoke tests post-deploy verdes? | Tests determinísticos |

### Cómo escalar

- IA → Humano: cuando hay ambigüedad de criterio
- Sistema → Humano: cuando hay finding crítico sin auto-fix
- Sistema → IA: cuando hay finding con auto-fix
- Humano → Sistema: cuando se aprueba ADR de excepción

---

## 7. MÉTRICAS DE CALIDAD

### Dashboard continuo (actualizado por sistema)

#### Por feature
- Tiempo desde paso 1 hasta paso 12
- Findings críticos detectados (cuántos auto-fixed vs escalados)
- Coverage de tests adversariales
- Cantidad de iteraciones del paso 5 (audit plan) y paso 7 (audit code)
- ADRs creados durante la feature

#### Por sprint/semana
- # de features completadas
- # de bugs en producción
- # de bypasses de gate (con ADR)
- # de bypasses sin ADR (target: 0)
- # de polinizaciones formales validadas

#### Trimestral
- Tasa de defectos por 1000 líneas de código en producción
- Tiempo promedio bug fix
- Deuda técnica acumulada vs resuelta
- Evolución de catálogo meta-patrones (# nuevos descubiertos vs validados)

### Alertas automáticas

- 🔴 Bypass de gate sin ADR → notificación inmediata
- 🟡 Coverage adversarial baja en feature reciente
- 🟡 Mismo patrón de bug repetido → candidato a regla preventiva
- 🔴 Vulnerabilidad de seguridad en producción → P0 inmediato

---

## 8. ONBOARDING DE NUEVOS MIEMBROS

### Para un humano nuevo (o vos mismo en 6 meses)

**Semana 1 — Comprensión**:
1. Leer `DEPARTAMENTO-DE-SOFTWARE.md` (arquitectura)
2. Leer `PROTOCOLO-CONSTRUCCION-CODIGO.md` (protocolo)
3. Leer este documento (`SISTEMA-DE-TRABAJO.md`)
4. Revisar 3 ADRs de decisiones importantes (`decisions/`)
5. Revisar catálogo meta-patrones para entender dolores conocidos

**Semana 2 — Observación**:
1. Hacer pair-programming con instancia previa o feature ya completa
2. Leer una feature completa de inicio a fin (sus stories, audit reports, ADRs)
3. Entender el flujo de la tubería bidireccional con ejemplos reales

**Semana 3 — Primer feature simple**:
1. Tomar bug fix simple
2. Seguir protocolo light completo (todos los pasos, sin saltar)
3. Tener checkpoint con vos al final de cada paso
4. Hacer retrospectiva al final

**Semana 4+ — Autonomía gradual**:
- Features chicas independientes
- Code review de PRs de otros (cuando hay equipo)
- Contribuir a evolución del catálogo meta-patrones

### Para una nueva instancia de Claude Code / agente IA

El agente lee al inicio:
1. `CLAUDE.md` / `AGENTS.md` (constitución + dispatcher de skills)
2. `adn-proyecto.json` (contexto del proyecto activo)
3. `auditoria/sesion-activa.md` (estado actual)
4. `SIGUIENTE-SESION.md` (próximo objetivo)

El agente NO necesita leer todo el ecosistema cada vez. El sistema de skills hace que el contexto sea on-demand: cuando se invoca `/sigma:work-story X`, el skill carga el contexto necesario.

---

## 9. EVOLUCIÓN DEL SISTEMA

### Quién puede proponer cambios

- Cualquier miembro del departamento (humano o IA) puede proponer cambio al protocolo o sistema
- Las propuestas vienen vía ADR formal

### Proceso de cambio

1. **Identificar problema o oportunidad**:
   - "El paso 7 produce falsos positivos en categoría X"
   - "El gate de capa 3 es bypassado constantemente — necesita revisión"
   - "Apareció patrón de dolor nuevo que merece regla"

2. **Crear ADR de propuesta**:
   ```
   decisions/ADR-NNNN-cambio-propuesto.md
   ```
   Secciones:
   - Contexto: qué problema/oportunidad
   - Decisión propuesta: qué cambiar
   - Alternativas consideradas
   - Consecuencias esperadas
   - Estado: Proposed | Accepted | Rejected | Superseded

3. **Revisión**:
   - Si afecta protocolo → requiere aprobación humana (vos)
   - Si afecta skills → puede ser aceptado por agente con humanidad informada
   - Si afecta validadores → requiere tests adversariales que demuestren

4. **Implementación**:
   - Actualizar documentos afectados
   - Migrar features en progreso si aplica
   - Comunicar al departamento

5. **Validación empírica**:
   - Aplicar en próximas N features
   - Medir si el cambio resolvió el problema
   - Si no → revisar o revertir

### Frecuencia de revisión

- **Por feature**: ¿el protocolo se aplicó completo? (en cierre paso 12)
- **Por sprint**: revisión rápida del dashboard de métricas
- **Por trimestre**: revisión completa del protocolo y arquitectura
- **Cuando aparece dolor nuevo**: revisión ad-hoc del meta-patrón

### Lo que NUNCA se cambia sin discusión profunda

- Los 7 principios rectores (constitución)
- La filosofía determinística (Python orquesta + LLM ejecuta + Python verifica)
- El requirement de polinización en cierre
- Los gates de capa 3/4 (sin ellos, el sistema deja de ser determinístico)

---

## 10. HERRAMIENTAS POR TIPO DE TAREA

### Para iniciar trabajo
- `/sigma:new-feature` — feature nueva
- `/sigma:fix-bug` — bug fix
- `/sigma:refactor` — refactor sin cambio funcional
- `/sigma:spike` — investigación técnica
- `/sigma:resume` — retomar trabajo en progreso

### Para capturar
- `/sigma:capture-domain` — captura activa de dominio (3 pasos)
- `/sigma:respond-solicitud SOL-XXX` — responder solicitud de tubería
- `/sigma:capture-decision` — registrar decisión técnica (ADR)

### Para diseñar y planificar
- `/sigma:design-architecture` — diseño arquitectónico
- `/sigma:plan-stories` — descomposición en stories
- `/sigma:create-prd` — PRD estructurado

### Para construir
- `/sigma:work-story STORY-XX` — implementar story específica
- `/sigma:add-tests` — agregar tests específicos
- `/sigma:refactor-function` — refactor de función puntual

### Para auditar
- `/sigma:audit-plan` — R01-R15 sobre plan
- `/sigma:audit-code` — G/FG + SOLID + zero-trust
- `/sigma:adversarial-tests` — generar tests adversariales
- `/sigma:security-audit` — auditoría de seguridad

### Para deploy
- `/sigma:pre-deploy-check` — verificación pre-deploy
- `/sigma:deploy` — deploy con red de seguridad
- `/sigma:rollback` — rollback automático
- `/sigma:smoke-tests` — smoke tests post-deploy

### Para cerrar
- `/sigma:close-session` — protocolo de cierre 9 pasos
- `/sigma:polinizacion-radar` — radar explícito de polinización
- `/sigma:retrospective` — retrospectiva formal

### Para mantenimiento
- `/sigma:dashboard` — métricas de calidad
- `/sigma:debt-tracker` — estado de deuda técnica
- `/sigma:metapatterns-review` — revisión catálogo meta-patrones
- `/sigma:health-check` — health check del sistema

---

## 11. CHECKLIST DIARIO PARA EL OPERADOR

### Mañana (inicio de día de trabajo)
- [ ] `/sigma:resume` para retomar contexto
- [ ] Revisar `SIGUIENTE-SESION.md` para objetivo del día
- [ ] Pre-flight check con validadores baseline
- [ ] Definir qué se va a completar HOY (1-3 stories máximo)

### Durante el día
- [ ] Commit cada 1-2h con mensaje descriptivo
- [ ] Push cuando se completa una story
- [ ] Anotar dolores estructurales en bitácora
- [ ] Usar tubería bidireccional para huecos de dominio

### Tarde (fin de día de trabajo)
- [ ] `/sigma:close-session` ejecutado
- [ ] Git push exitoso confirmado
- [ ] `SIGUIENTE-SESION.md` apunta a objetivo concreto para mañana
- [ ] Memoria Engram actualizada con aprendizajes del día

---

## 12. SITUACIONES ESPECIALES

### Si encontrás un bug crítico en producción

1. Crear branch `hotfix/YYYY-MM-DD-descripcion`
2. Aplicar workflow Estación Bug Fix (light)
3. Skip diseño arquitectónico solo si root cause es trivial
4. Tests adversariales OBLIGATORIOS (no skip)
5. Polinización OBLIGATORIA (bug crítico es meta-patrón candidato)
6. Deploy con `--hotfix` flag (smoke tests más estrictos)

### Si un gate de capa 3/4 falla y no podés resolverlo

1. NO bypass sin ADR
2. Crear ADR de excepción:
   - ¿Cuál es la razón estructural?
   - ¿Qué tarea derivada para volver al protocolo?
   - ¿Aprobación humana explícita?
3. Solo entonces, bypass temporal con ADR registrado
4. Tarea derivada queda en backlog priorizada

### Si descubrís que el protocolo tiene un problema

1. NO ignorarlo y seguir
2. Documentar el problema en `CUADERNO-BITACORA.md`
3. Si afecta calidad → crear ADR de propuesta de cambio
4. Continuar trabajo con protocolo actual hasta que la propuesta se evalúe

### Si hay desacuerdo entre humano y agente IA

1. El humano tiene última palabra en decisiones de negocio/estrategia
2. La IA tiene mejor data en decisiones técnicas mecánicas (¿cuál algoritmo es más rápido?)
3. Si desacuerdo persiste, escalar a evidencia:
   - "Demostremos empíricamente con benchmarks"
   - "Probemos ambas opciones en branches separados"
4. Documentar el aprendizaje en bitácora

### Si el sistema se rompe

1. Stop work
2. `/sigma:health-check` para diagnóstico
3. Si afecta producción → rollback inmediato
4. Investigar root cause antes de cualquier fix
5. Post-mortem documentado en `decisions/`

### Plan de respuesta a incidentes (formal)

Clasificación por severidad:

| Nivel | Descripción | Tiempo de respuesta | Acción |
|---|---|---|---|
| **P0** | Sistema caído o pérdida de datos | Inmediato (< 15 min) | Rollback + war room + comunicación |
| **P1** | Feature crítica afectada (auth, pagos) | < 1 hora | Fix o rollback parcial + monitoreo |
| **P2** | Degradación menor, workaround disponible | < 24 horas | Fix planificado + workaround comunicado |
| **P3** | Cosmético o nice-to-have | Próximo sprint | Backlog priorizado |

Procedimiento por incidente (cualquier severidad ≥ P2):

1. **Detección**: alerta automática (Sentry, health check, monitoring) o reporte de usuario
2. **Triage** (máximo 5 min): clasificar severidad, asignar responsable (si solo vos, vos sos)
3. **Comunicación inicial**: si afecta usuarios, notificar (incluso si es "investigando")
4. **Mitigación**: detener el sangrado antes de fix definitivo (rollback, feature flag off, throttling)
5. **Root cause analysis**: encontrar la causa real, no solo el síntoma
6. **Fix verificado**: aplicar fix + tests adversariales que prevengan recurrencia
7. **Postmortem** (obligatorio para P0/P1): doc en `decisions/POSTMORTEM-YYYY-MM-DD-titulo.md`
8. **Acciones preventivas**: agregar deuda técnica o regla nueva al catálogo de meta-patrones

Template de postmortem (formato mínimo):

```markdown
# Postmortem: [título descriptivo]

Fecha: YYYY-MM-DD
Severidad: P0 / P1
Duración: HH:MM (desde detección hasta resolución)
Impacto: [usuarios/datos/funcionalidad afectada]

## Timeline
- HH:MM detección del problema
- HH:MM acción de mitigación X
- HH:MM ...
- HH:MM resolución confirmada

## Root cause
[Causa real, no síntoma]

## Lo que funcionó
- [Detección rápida por X]
- [Rollback funcionó sin issues]

## Lo que NO funcionó
- [Tardamos N min en detectar porque Y]
- [Faltaba alerta sobre Z]

## Acciones preventivas
- [ ] Tarea concreta 1
- [ ] Tarea concreta 2
```

Lectura adicional: `DEPARTAMENTO-DE-SOFTWARE.md` sección 8.3 punto 10.

### Workflow: verificación trimestral de backups

Cada 3 meses, ejecutar el siguiente ritual (1-2 horas):

1. Levantar ambiente de staging temporal o aislado
2. Tomar el último backup completo de prod
3. Restaurar en el ambiente aislado
4. Verificar:
   - [ ] Restore completa sin errores
   - [ ] Datos críticos presentes y consistentes
   - [ ] App funciona conectada al restore
   - [ ] Tiempo total de restore (RTO) dentro del objetivo
   - [ ] Pérdida máxima de datos (RPO) calculada
5. Documentar resultado en `decisions/RESTORE-TEST-YYYY-MM-DD.md`
6. Si hubo issues → deuda técnica nueva en `DEUDA-TECNICA.md`

Referencia: `DEPARTAMENTO-DE-SOFTWARE.md` sección 8.1 punto 3.

### Manejo de costos de APIs externas (Claude API, Supabase, etc.)

Monitoreo permanente:

- Budget alert configurado al 50% / 75% / 90% del presupuesto mensual
- Rate limiting interno en endpoints que llaman APIs externas
- Circuit breaker para servicios externos críticos
- Cache agresivo de respuestas costosas
- Timeouts explícitos en TODO request (default 30s, ajustar según caso)
- Graceful degradation si servicio externo cae

Si gasto mensual supera proyección en ≥ 30%:

1. Audit inmediato de uso (qué endpoints generaron picos)
2. Identificar causa: feature nueva, bug, abuso, escalamiento natural
3. Decisión: optimizar / rate limit más estricto / aumentar presupuesto / pausar feature
4. Documentar en `decisions/COST-INCIDENT-YYYY-MM-DD.md`

Referencia: `DEPARTAMENTO-DE-SOFTWARE.md` sección 8.2 punto 7.

---

## REFERENCIAS

- `DEPARTAMENTO-DE-SOFTWARE.md` — arquitectura completa
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` — protocolo determinístico
- Catálogo meta-patrones de dolor (`meta-patrones/`)
- ADRs (`decisions/`)
- 7 principios rectores

---

Versión 1.0 — 2026-05-13
Próxima revisión: tras Sprint 1 (validación empírica sobre Stallen feature real)
