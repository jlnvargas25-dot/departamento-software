# PROTOCOLO DE CONSTRUCCIÓN DE CÓDIGO — Sistema Determinístico

**Versión**: 1.0 (2026-05-13)
**Estado**: Protocolo fundacional
**Documentos relacionados**:
- `DEPARTAMENTO-DE-SOFTWARE.md` — arquitectura completa
- `SISTEMA-DE-TRABAJO.md` — manual operativo

---

## PROPÓSITO

Este protocolo define los pasos determinísticos obligatorios que se siguen para construir código en el Departamento de Software. Cada paso tiene gates de enforcement que impiden avanzar sin cumplir criterios objetivos.

**Filosofía**: Claude Code (o cualquier agente IA) puede saltarse pasos por descuido pero no por elección. El protocolo es ineludible por diseño, no por disciplina personal.

---

## REGLAS GLOBALES

### Regla R-0: Secuencia obligatoria

Los pasos se ejecutan en orden estricto. No se puede saltar un paso. Cada paso requiere artefactos producidos por el anterior.

### Regla R-1: Gates de enforcement por capa

Cada paso tiene gates aplicados en 4 capas:

| Capa | Tipo | Severidad | Ejemplo |
|---|---|---|---|
| 1 | Skill declarativo | Soft | Skill marca "captura activa requerida" pero agente puede ignorar |
| 2 | Tool gate | Medio | Próximo paso requiere artefacto del anterior; sin artefacto → falla |
| 3 | Pre-commit hook | Duro | Git no permite commit si validadores fallan |
| 4 | CI/CD gate | Máximo | PR no se mergea si tests/validators fallan |

**Cada protocolo declara explícitamente qué gate aplica en qué capa.**

### Regla R-2: Auditoría empírica antes de declarar "hecho"

Ningún paso se considera completado solo porque el agente lo declara. Cada paso tiene criterios objetivos verificables por herramienta determinística.

### Regla R-3: Excepciones documentadas

Cualquier excepción al protocolo (skip de paso, bypass de gate) requiere:
1. Razón estructural documentada
2. Aprobación humana explícita
3. Registro en `decisions/` con ADR (Architectural Decision Record)
4. Tarea derivada para volver al protocolo en próxima iteración

Sin estos 4 elementos, la excepción no se acepta.

### Regla R-4: Polinización obligatoria al cierre

Todo cierre de feature/sesión incluye radar de polinización (paso 7.5 del protocolo de cierre): ¿este dolor descubierto puede propagarse a otro subsistema?

---

## PASOS DEL PROTOCOLO

### PASO 1: CAPTURAR INTENCIÓN

**Objetivo**: Convertir la idea del dueño del producto en PRD estructurado.

**Responsable**: Analista de Producto (humano + IA)

**Inputs requeridos**:
- Conversación con dueño del producto (no asume nada)
- Acceso a `openspec/specs/` (estado actual del sistema)

**Tareas**:
1. Identificar problema o oportunidad concreta
2. Validar que el problema no esté ya resuelto (revisar specs existentes)
3. Capturar criterios de éxito medibles (no "que funcione bien")
4. Identificar usuarios afectados y casos de uso
5. Identificar restricciones (presupuesto, tiempo, dependencias)

**Outputs producidos**:
- `openspec/changes/YYYY-MM-DD-feature-X/prd.md` con secciones:
  - Problema
  - Solución propuesta de alto nivel
  - Criterios de éxito medibles
  - Casos de uso
  - Restricciones
  - Out of scope (qué NO incluye)

**Gates de enforcement**:
- **Capa 1**: Skill `capturar-intencion` requiere todas las secciones del PRD pobladas
- **Capa 2**: Próximo paso (capturar dominio) requiere `prd.md` válido contra schema
- **Capa 3**: Pre-commit valida formato de PRD si está incluido en commit
- **Capa 4**: CI valida que todo `openspec/changes/*/prd.md` esté presente

**Criterios de "hecho"**:
- [ ] Las 6 secciones del PRD están pobladas
- [ ] Criterios de éxito son medibles (no genéricos)
- [ ] "Out of scope" está explícito (al menos 1 ítem)
- [ ] Casos de uso son ≥ 2 concretos

**Si falla**: No se puede avanzar. Volver a conversar con dueño hasta tener PRD completo.

---

### PASO 2: CAPTURAR DOMINIO ACTIVAMENTE

**Objetivo**: Asegurar que el ADN del proyecto está completo para esta feature.

**Responsable**: Captor de Dominio (IA con supervisión humana)

**Inputs requeridos**:
- `prd.md` del paso 1
- `adn-proyecto.json` actual del proyecto
- Catálogos canónicos (`catalogos/modulos/erp.yaml`, `comunes.yaml`)

**Tareas**:
1. Identificar qué módulos canónicos toca la feature (auth, inventory, etc.)
2. Identificar reglas de dominio aplicables (existentes + nuevas)
3. Para cada regla nueva, ejecutar clasificación 3 pasos:
   - Paso 2a: Cross-reference con vecinas que declaren misma función
   - Paso 2b: Match contra modulos_custom por palabras_clave (score)
   - Paso 2c: Si no hay match → disparar `solicitar_dominio()` (tubería bidireccional)
4. Si hay huecos reales, esperar respuesta humana via tubería
5. Actualizar `adn-proyecto.json` con delta marker (ADDED/MODIFIED)
6. Verificar completitud efectiva ≥ 95%

**Outputs producidos**:
- `adn-proyecto.json` actualizado
- `openspec/changes/YYYY-MM-DD-feature-X/adn-delta.md` con cambios al ADN
- Solicitudes de tubería resueltas (`auditoria/solicitudes-dominio/SOL-*.json`)

**Gates de enforcement**:
- **Capa 1**: Skill `capturar-dominio` requiere completitud verificada
- **Capa 2**: Próximo paso (arquitectura) requiere ADN completitud ≥ 95%
- **Capa 3**: Pre-commit verifica que `adn-proyecto.json` no tiene huecos críticos
- **Capa 4**: CI corre `capturar_adn.py --verify` y rechaza si encuentra huecos

**Criterios de "hecho"**:
- [ ] Completitud efectiva ≥ 95%
- [ ] Todas las solicitudes de tubería tienen respuesta
- [ ] Modulos_custom necesarios están declarados
- [ ] ADN-delta documenta los cambios con marcadores

**Si falla**: No se puede avanzar. Capturar las reglas faltantes con dueño del producto.

---

### PASO 3: DISEÑAR ARQUITECTURA TÉCNICA

**Objetivo**: Producir diseño de alto nivel de la solución.

**Responsable**: Arquitecto (IA con review humano)

**Inputs requeridos**:
- `prd.md`
- `adn-proyecto.json` actualizado
- Decisiones arquitectónicas previas (`decisions/`)
- Patrones aplicables (`meta-patrones/`)

**Tareas**:
1. Identificar arquitectura aplicable (cliente-servidor, eventos, batch, etc.)
2. Identificar componentes nuevos vs modificación de existentes
3. Identificar dependencias entre componentes
4. Identificar puntos de extensibilidad
5. Identificar riesgos técnicos y mitigaciones
6. Si hay decisión técnica no obvia, crear ADR

**Outputs producidos**:
- `openspec/changes/YYYY-MM-DD-feature-X/design.md` con:
  - Diagrama de componentes
  - Flujo de datos
  - Decisiones técnicas y alternativas consideradas
  - Riesgos y mitigaciones
- `decisions/ADR-NNNN-titulo.md` si hay decisión no obvia

**Gates de enforcement**:
- **Capa 1**: Skill `disenar-arquitectura` requiere todas las secciones
- **Capa 2**: Próximo paso (planificar) requiere `design.md` válido
- **Capa 3**: Pre-commit valida formato y completitud
- **Capa 4**: CI valida que cada feature tiene `design.md`

**Criterios de "hecho"**:
- [ ] Diagrama de componentes presente
- [ ] Decisiones técnicas con alternativas (no solo "elegí X")
- [ ] Al menos 2 riesgos identificados con mitigaciones
- [ ] ADR creado si la decisión es no-obvia

**Si falla**: Revisar con humano antes de avanzar. Diseño débil propaga problemas downstream.

---

### PASO 4: PLANIFICAR (BACKLOG DE STORIES)

**Objetivo**: Transformar diseño en stories ejecutables con acceptance criteria.

**Responsable**: Planificador (IA, agente Scrum Master)

**Inputs requeridos**:
- `design.md`
- `adn-proyecto.json`
- Catálogos canónicos

**Tareas**:
1. Descomponer la solución en stories de tamaño ejecutable (1-3 días de trabajo IA-asistido)
2. Para cada story, capturar:
   - Título y descripción
   - Acceptance criteria explícitos (en formato Given/When/Then o equivalente)
   - Dependencias con otras stories
   - Estimación de complejidad (S/M/L)
3. Priorizar stories según dependencias y valor de negocio
4. Identificar si aplica scale-adaptive: ¿es bug fix simple? → workflow light. ¿Es feature grande? → workflow full.

**Outputs producidos**:
- `openspec/changes/YYYY-MM-DD-feature-X/stories.md` con backlog priorizado
- `openspec/changes/YYYY-MM-DD-feature-X/tasks.md` con plan de ejecución secuencial

**Gates de enforcement**:
- **Capa 1**: Skill `planificar-stories` requiere acceptance criteria en cada story
- **Capa 2**: Próximo paso (auditar plan) requiere `stories.md` y `tasks.md`
- **Capa 3**: Pre-commit verifica formato de stories
- **Capa 4**: CI valida que cada feature tiene stories priorizadas

**Criterios de "hecho"**:
- [ ] Cada story tiene acceptance criteria explícitos (mínimo 3 por story)
- [ ] Cada story tiene estimación de complejidad
- [ ] Dependencias entre stories están declaradas
- [ ] Plan de ejecución es secuencial (no asume paralelismo no validado)

**Si falla**: Acceptance criteria vagos → reescribir hasta que sean verificables objetivamente.

---

### PASO 5: AUDITAR PLAN (validadores R01-R15)

**Objetivo**: Validar coherencia estructural del plan antes de generar código.

**Responsable**: Auditor de Plan (Python determinístico)

**Inputs requeridos**:
- `stories.md`
- `tasks.md`
- `adn-proyecto.json`
- Plan generado para backend (si aplica)

**Tareas**:
1. Ejecutar `sigma-plan-validator` (MCP server) sobre el plan
2. Aplicar R01-R15:
   - R01: ancestros válidos
   - R02: referencias coherentes
   - R03: detectar ciclos
   - R04: deps fuera de scope
   - R05: naming conventions
   - R06: colisiones de tablas
   - R07: plan vs grafo consistency
   - R08: funciones declaradas pero no creadas
   - R09: aislamiento de scope (warning)
   - R10: stubs necesarios
   - R11: tamaño de thread
   - R12: cobertura de dominio
   - R13: cobertura de módulos
   - R15: deps transitivas
3. Si hay findings críticos, ejecutar `sigma-auto-fix` (patcher)
4. Si auto-fix no cubre todos, escalar a humano

**Outputs producidos**:
- Reporte de findings: `openspec/changes/YYYY-MM-DD-feature-X/audit-plan.json`
- Plan modificado con auto-fixes aplicados (si corresponde)

**Gates de enforcement**:
- **Capa 1**: Skill `auditar-plan` invoca validadores automáticamente
- **Capa 2**: Próximo paso (construir) requiere 0 críticos en audit-plan
- **Capa 3**: Pre-commit corre validadores y rechaza commit si hay críticos
- **Capa 4**: CI corre validadores en pipeline; rechaza PR si hay críticos

**Criterios de "hecho"**:
- [ ] 0 findings críticos (todos resueltos por auto-fix o ajuste humano)
- [ ] Warnings documentados o aceptados explícitamente
- [ ] Auto-fixes aplicados están registrados con razón

**Si falla**: NO avanzar. Plan con findings críticos genera código defectuoso garantizado.

---

### PASO 6: CONSTRUIR CÓDIGO (Backend / Frontend)

**Objetivo**: Generar código que implementa las stories.

**Responsable**: Desarrolladores Backend/Frontend (IA — Claude Code, Cursor, etc.)

**Inputs requeridos**:
- `stories.md` con acceptance criteria
- `design.md` para contexto arquitectónico
- `adn-proyecto.json` para reglas del dominio
- Catálogos canónicos
- `audit-plan.json` con 0 críticos

**Tareas**:
1. Para cada story (en orden de dependencias):
   - Implementar código siguiendo design.md
   - Generar tests unitarios cumpliendo acceptance criteria
   - NO implementar solo happy path (ver paso 8)
   - Aplicar SOLID en estructura (paso 7 valida)
   - Aplicar zero-trust en accesos a datos
2. Commit por story (no acumular)

**Outputs producidos**:
- Código fuente (backend SQL/Python, frontend TSX/React)
- Tests unitarios por story
- Migrations idempotentes si aplica

**Gates de enforcement**:
- **Capa 1**: Skill `construir-codigo` referencia stories y acceptance criteria
- **Capa 2**: Próximo paso (auditar código) requiere commits individuales por story
- **Capa 3**: Pre-commit corre linters básicos (ruff, eslint, prettier)
- **Capa 4**: CI corre suite completa de validadores

**Criterios de "hecho"**:
- [ ] Cada story tiene commit identificable
- [ ] Tests unitarios pasan
- [ ] Linters básicos pasan
- [ ] Cada acceptance criterion tiene al menos 1 test asociado

**Si falla**: Tests rojos → no se puede mergear. Linters fallan → no se puede commitear.

---

### PASO 7: AUDITAR CÓDIGO (G1-G33 + FG1-FG14 + SOLID + Zero-Trust)

**Objetivo**: Validar que el código generado cumple estándares estructurales y de seguridad.

**Responsable**: Auditor de Código (Python determinístico + análisis estático)

**Inputs requeridos**:
- Código generado en paso 6
- ADN del proyecto

**Tareas**:
1. **Backend SQL/Python**:
   - Ejecutar `sigma-code-validator` (G1-G33)
   - Verificar timestamps inyectados (G1)
   - Verificar SECURITY DEFINER con search_path (G2)
   - Verificar parameterized queries (G15)
   - Verificar campos obligatorios (G7-G8)
2. **Frontend TSX/React**:
   - Ejecutar validadores FG1-FG14
   - Verificar imports correctos
   - Verificar types estrictos
   - Verificar componentes accesibles
3. **SOLID estructural** (`sigma-solid-checker`):
   - Single Responsibility: funciones ≤ 50 líneas, clases ≤ 300 líneas
   - Open/Closed: detectar modificación de clases base donde aplicaría extensión
   - Liskov: verificar contratos en docstrings + tests de override
   - Interface Segregation: clases con > 7 métodos públicos → review
   - Dependency Inversion: imports concretos donde debería haber abstracción
4. **Zero-Trust** (`sigma-security-auditor`):
   - Endpoints sin auth decorator → reject
   - SECURITY DEFINER sin search_path → reject
   - Secrets en código → reject (gitleaks + truffleHog)
   - Input validation con schemas obligatoria
   - Output sanitization
5. **Detección errores silenciosos**:
   - `except: pass` sin re-raise → reject
   - Promises sin `.catch()` → reject (ESLint `no-floating-promises`)
   - Funciones sin return explícito en path de error → reject (mypy --strict)
6. **Si hay findings críticos**, intentar auto-fix; si no se puede, escalar a humano.

**Outputs producidos**:
- Reporte de findings: `openspec/changes/YYYY-MM-DD-feature-X/audit-code.json`
- Código modificado con auto-fixes aplicados

**Gates de enforcement**:
- **Capa 1**: Skill `auditar-codigo` invoca validadores
- **Capa 2**: Próximo paso (tests adversariales) requiere 0 críticos
- **Capa 3**: Pre-commit corre validadores; rechaza si hay críticos
- **Capa 4**: CI corre validadores; rechaza PR si hay críticos

**Criterios de "hecho"**:
- [ ] 0 findings críticos en validadores G/FG
- [ ] 0 violaciones SOLID estructurales
- [ ] 0 issues de zero-trust
- [ ] 0 errores silenciosos detectados
- [ ] Auto-fixes registrados con razón

**Si falla**: NO avanzar. Código que falla auditoría tiene defectos garantizados.

---

### PASO 8: TESTS ADVERSARIALES OBLIGATORIOS

**Objetivo**: Verificar que el código maneja edge cases, no solo happy path.

**Responsable**: Test Architect (IA con templates)

**Inputs requeridos**:
- Código del paso 6
- Acceptance criteria de stories
- Patrones de tests adversariales (`meta-patrones/adversarial-patterns.md`)

**Tareas**:
1. Para cada función nueva o modificada, generar tests adversariales:
   - Inputs vacíos (string vacío, list vacía, None, undefined)
   - Inputs malformados (tipos incorrectos, encoding inválido)
   - Boundary conditions (0, 1, max, max+1)
   - Inputs concurrentes (race conditions cuando aplica)
   - Network failures simulados (timeouts, 500, 401, 403)
   - Database failures (constraint violations, deadlocks)
2. Verificar cobertura de branches ≥ 80%
3. Ejecutar property-based testing donde aplique (hypothesis Python, fast-check TS)
4. Ejecutar mutation testing periódico (mensual)

**Outputs producidos**:
- Tests adversariales agregados al código
- Reporte de cobertura: `openspec/changes/YYYY-MM-DD-feature-X/coverage-report.json`

**Gates de enforcement**:
- **Capa 1**: Skill `tests-adversariales` requiere N categorías de edge cases
- **Capa 2**: Próximo paso (seguridad final) requiere tests adversariales presentes
- **Capa 3**: Pre-commit verifica que tests adversariales existen
- **Capa 4**: CI corre tests + coverage; rechaza si coverage < 80%

**Criterios de "hecho"**:
- [ ] Cada función nueva tiene ≥ 5 categorías de edge cases cubiertos
- [ ] Cobertura de branches ≥ 80%
- [ ] Tests pasan tanto secuenciales como en paralelo (`pytest-xdist`, `jest --runInBand` vs paralelo)
- [ ] Property-based tests existen donde aplica

**Si falla**: Código que solo prueba happy path NO es comercial. Bloqueo absoluto.

---

### PASO 9: VALIDACIÓN DE SEGURIDAD Y CONFIGURACIÓN

**Objetivo**: Verificar zero-trust completo y configuración válida antes de deploy.

**Responsable**: Auditor de Seguridad (Python + herramientas)

**Inputs requeridos**:
- Código completo
- Configuración de producción

**Tareas**:
1. **Auditoría de seguridad**:
   - bandit (Python security issues)
   - semgrep (custom security rules)
   - gitleaks + truffleHog (secrets detection)
   - snyk (dependency vulnerabilities)
   - trivy (container scanning si aplica)
2. **Validación de configuración**:
   - Schemas Pydantic/Zod para todo config
   - Variables de entorno validadas al boot (fail-fast)
   - Configs de prod NO incluyen valores de dev/test
   - Secrets NO en código (todos en env vars o vault)
3. **Validación de RLS (Postgres)**:
   - Todas las tablas con datos sensibles tienen RLS habilitado
   - Todas las funciones SECURITY DEFINER tienen search_path
   - Policies cubren todos los casos (no solo SELECT)
4. **Migrations idempotentes**:
   - DROP IF EXISTS antes de CREATE
   - Validación de re-ejecución segura

**Outputs producidos**:
- Reporte de seguridad: `openspec/changes/YYYY-MM-DD-feature-X/security-audit.json`
- Reporte de configuración: `openspec/changes/YYYY-MM-DD-feature-X/config-audit.json`

**Gates de enforcement**:
- **Capa 1**: Skill `validar-seguridad` invoca todas las herramientas
- **Capa 2**: Próximo paso (deploy) requiere 0 críticos
- **Capa 3**: Pre-push hook corre auditoría de seguridad
- **Capa 4**: CI corre full security pipeline; rechaza si hay críticos

**Criterios de "hecho"**:
- [ ] 0 vulnerabilidades críticas/altas en dependencies
- [ ] 0 secrets en código
- [ ] 0 issues de RLS faltante
- [ ] Schemas de config validados
- [ ] Migrations idempotentes verificadas

**Si falla**: NO se hace deploy. Vulnerabilidad en producción es disqualifier inmediato.

---

### PASO 10: DEPLOY SEGURO

**Objetivo**: Aplicar cambios a producción con red de seguridad.

**Responsable**: DevOps (IA con review humano)

**Inputs requeridos**:
- Código auditado y validado (pasos 7-9 completos)
- CI/CD passing en green
- Backup de producción reciente

**Tareas**:
1. **Pre-deploy checks**:
   - Verificar que todos los gates anteriores pasaron
   - Verificar backup de producción reciente (< 24h)
   - Verificar rollback plan documentado
2. **Deploy en orden**:
   - Migrations primero (idempotentes)
   - Backend después
   - Frontend al final
3. **Smoke tests post-deploy**:
   - Endpoints críticos respondiendo
   - Auth funcionando
   - Tx críticas funcionando
   - Performance baseline OK
4. **Rollback plan listo**:
   - Comando documentado para rollback
   - Backup verificado para restore si necesario

**Outputs producidos**:
- Log de deploy: `openspec/changes/YYYY-MM-DD-feature-X/deploy-log.md`
- Reporte de smoke tests
- Confirmación de rollback plan

**Gates de enforcement**:
- **Capa 1**: Skill `deploy-seguro` requiere todos los pre-checks
- **Capa 2**: Smoke tests deben pasar; si fallan → rollback automático
- **Capa 3**: Pre-push hook requiere CI green
- **Capa 4**: CI/CD pipeline gatea deploy

**Criterios de "hecho"**:
- [ ] CI/CD green
- [ ] Smoke tests post-deploy verdes
- [ ] Performance baseline mantenido o mejorado
- [ ] Rollback plan documentado y testeado
- [ ] Log de deploy registrado

**Si falla**: Rollback inmediato. Investigar causa antes de retry.

---

### PASO 11: VERIFICACIÓN POST-DEPLOY

**Objetivo**: Confirmar que la feature funciona en producción real.

**Responsable**: DevOps + Test Architect

**Inputs requeridos**:
- Sistema en producción con feature deployed
- Métricas de baseline

**Tareas**:
1. Monitor durante 24h post-deploy:
   - Métricas de performance (latencia, throughput)
   - Tasa de errores
   - Logs de aplicación
2. Validar acceptance criteria de stories en producción real
3. Verificar que no hay regresiones en features existentes
4. Si aparecen issues, decidir: fix-forward o rollback

**Outputs producidos**:
- Reporte de verificación 24h
- Métricas de baseline actualizadas
- Tickets si hay issues a corregir

**Gates de enforcement**:
- **Capa 1**: Skill `verificar-post-deploy` requiere 24h de monitoring
- **Capa 2**: Si métricas degradan > 10%, alerta automática
- **Capa 3**: N/A
- **Capa 4**: CI/CD pipeline monitorea métricas continuas

**Criterios de "hecho"**:
- [ ] 24h sin issues críticos
- [ ] Métricas en baseline o mejor
- [ ] Acceptance criteria validados en producción
- [ ] No regresiones detectadas

**Si falla**: Decidir fix-forward o rollback según severidad.

---

### PASO 12: CIERRE Y POLINIZACIÓN

**Objetivo**: Capturar aprendizajes y propagar a otros subsistemas.

**Responsable**: Memoria Institucional (sistema)

**Inputs requeridos**:
- Toda la feature ejecutada
- Logs de pasos 1-11

**Tareas**:
1. **Documentar lo hecho** (`auditoria/sesion-activa.md`):
   - Qué se hizo
   - Qué se aprendió
   - Bugs encontrados y resueltos
2. **Radar de deuda nueva**:
   - ¿Generó deuda técnica esta feature?
   - Si sí → agregar a `DEUDA-TECNICA.md`
3. **Radar de polinización cruzada** (CRÍTICO):
   - ¿Se descubrió patrón de dolor en algún paso?
   - ¿Existe en catálogo meta-patrones?
   - Si NO → agregar nuevo meta-patrón
   - Si SÍ → agregar nueva manifestación
   - Para cada subsistema no cubierto, evaluar si aplica polinización
4. **Actualizar memoria persistente** (Engram):
   - Decisiones técnicas tomadas
   - Patrones útiles descubiertos
5. **Backup git**: commit + push obligatorio
6. **Retrospectiva** (si aplica):
   - ¿Qué funcionó bien?
   - ¿Qué se podría mejorar en próximas features?
   - ¿Qué partes del protocolo merecen evolución?

**Outputs producidos**:
- `auditoria/sesion-activa.md` actualizado
- Meta-patrones actualizados
- Memoria persistente con nuevos aprendizajes
- Git commit + push

**Gates de enforcement**:
- **Capa 1**: Skill `cerrar-sesion` corre los 9 pasos del protocolo de cierre
- **Capa 2**: N/A
- **Capa 3**: Pre-push hook verifica que ritual de cierre está completo
- **Capa 4**: N/A

**Criterios de "hecho"**:
- [ ] 9 pasos del protocolo de cierre completados
- [ ] Radar de polinización ejecutado explícitamente (no skip)
- [ ] Git push exitoso
- [ ] Memoria persistente actualizada
- [ ] Retrospectiva documentada (cada N sesiones)

**Si falla**: Cierre sin polinización es deuda institucional. NO se acepta.

---

## ENFORCEMENT MULTI-CAPA

### Resumen de gates por capa

| Capa | Mecanismo | Cuándo aplica | Quién lo aplica |
|---|---|---|---|
| 1 — Soft | Skills declarativos | Durante ejecución del agente IA | Agente IA leyendo SKILL.md |
| 2 — Medium | Tool gates (output requerido) | Entre pasos del protocolo | Sistema de orquestación |
| 3 — Hard | Pre-commit/pre-push hooks | En cada git commit/push | Git hooks locales |
| 4 — Maximum | CI/CD pipelines | En cada PR/merge | GitHub Actions / CI service |

### Lo que NO se puede saltar (ineludible)

Pasos con gate de Capa 3 o 4:
- Paso 2: Captura de dominio (CI valida completitud)
- Paso 5: Auditoría de plan (pre-commit + CI)
- Paso 7: Auditoría de código (pre-commit + CI)
- Paso 8: Tests adversariales (CI rechaza si coverage bajo)
- Paso 9: Seguridad (pre-push + CI)
- Paso 10: CI/CD green (pipeline gate)
- Paso 12: Backup git (pre-push verifica ritual)

### Excepciones permitidas

Solo con ADR documentado:
- Skip de paso por razón estructural justificada
- Bypass de gate con aprobación humana explícita
- Workaround temporal con tarea derivada para volver al protocolo

**Sin ADR → la excepción no se acepta y el código no llega a producción.**

---

## AUDITORÍA DEL PROTOCOLO

### Métricas continuas

Dashboard de calidad del departamento (actualizado automáticamente):

- **% de features que cumplen protocolo completo** (target: 100%)
- **# de excepciones registradas (con ADR)** por trimestre
- **# de gates bypassed sin ADR** (target: 0; alerta inmediata si > 0)
- **Tiempo promedio por feature** desde paso 1 hasta paso 12
- **# de bugs en producción atribuibles a skip de paso** (target: 0)
- **Coverage promedio de tests adversariales**
- **# de polinizaciones formales validadas** acumulado

### Revisión periódica

Cada 5 features completadas o 1 mes (lo que ocurra primero):
1. Revisar métricas del dashboard
2. Identificar pasos que se saltan frecuentemente
3. Decidir si el paso debe mejorarse o el gate debe endurecerse
4. Actualizar este documento si corresponde
5. Comunicar cambios al departamento

### Evolución del protocolo

Este protocolo es vivo. Evoluciona con evidencia empírica:
- Si un gate produce falsos positivos repetidos → ajustarlo
- Si un paso se vuelve cuello de botella → optimizarlo (no eliminarlo)
- Si aparece un patrón de dolor nuevo → agregar paso o gate
- Si una herramienta del ecosistema mejora → adoptarla

Cada cambio al protocolo requiere ADR.

---

## REFERENCIAS

- `DEPARTAMENTO-DE-SOFTWARE.md` — arquitectura completa
- `SISTEMA-DE-TRABAJO.md` — manual operativo día-a-día
- 7 principios rectores (sección 2 de arquitectura)
- Catálogo meta-patrones de dolor
- ADRs en `decisions/`

---

Versión 1.0 — 2026-05-13
Próxima revisión: tras Sprint 1 (validación empírica del protocolo sobre Stallen feature real)
