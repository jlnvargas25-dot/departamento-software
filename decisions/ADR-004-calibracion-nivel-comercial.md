# ADR-004: Calibración del Nivel Comercial del Departamento

**Status**: Decidido
**Fecha**: 2026-05-13
**Decisor**: Julián Vargas
**Contexto**: Sesión fundacional Sprint 1, conversación estratégica sobre cobertura de la arquitectura para uso comercial

---

## Contexto

Durante el Sprint 1, surgieron 3 preguntas clave que requirieron decisión explícita:

1. ¿Es producto vendible o uso personal?
2. ¿Qué nivel de "comercial" apunta Stallen?
3. ¿Qué tan completa debe estar la arquitectura?

Sin esta decisión documentada, hay riesgo de over-engineering (construir para Nivel 3 cuando Stallen es Nivel 2) o under-engineering (quedarse en Nivel 1 cuando ya hay clientes pagando).

---

## Decisión

### Naturaleza del Departamento

**Decisión**: El Departamento de Software es para **USO PERSONAL** (Julián), aplicado a proyectos comerciales reales. NO es producto vendible.

**Implicación**: salen del scope:
- Packaging como framework público
- Build in public / comunidad / partnerships
- Naming, licencia, distribución
- Documentación pública navegable
- Templates exportables

### Niveles de comercial definidos

**Nivel 1 — Comercial personal** (1 cliente, dev único, sin SLA formal):
- Stallen con 1 cliente (Wendy) en su estado actual
- Downtime aceptable de horas
- Sin contratos legales pesados

**Nivel 2 — Comercial profesional** (3-10 clientes, ingreso medio, dev único o pequeño equipo):
- Stallen con varios clientes pagando
- Downtime aceptable de minutos
- Algunas obligaciones contractuales

**Nivel 3 — Comercial empresarial** (clientes empresariales, SLAs, compliance):
- SaaS con clientes empresariales
- Compliance (GDPR, posibly SOC 2)
- Equipo de 2-5 devs
- Downtime con costo significativo

### Apuesta para Stallen

**Hoy**: Nivel 1
**12 meses**: Nivel 2
**24+ meses**: posiblemente Nivel 3 si el mercado lo justifica (no obligado)

**Implicación**: la arquitectura del Departamento se construye para llegar a Nivel 2 sólido en 12 semanas. Nivel 3 se evalúa cuando llegue el momento, no se construye preventivamente.

---

## Cobertura actual vs target

### Lo que YA está construido (cubre Nivel 1 al 80%)

- ✅ Constitución (CLAUDE.md con 7 principios)
- ✅ Protocolo construcción (12 pasos + 6 reglas globales R-0 a R-6)
- ✅ Sistema de trabajo operativo
- ✅ Memoria inteligente (Engram con 14 tools MCP)
- ✅ Code reviewer (GGA v2.8.1)
- ✅ Reglas de calidad (AGENTS.md v1.0)
- ✅ 10 dimensiones de calidad documentadas (DEPARTAMENTO-DE-SOFTWARE.md §8)
- ✅ Plan respuesta a incidentes (SISTEMA-DE-TRABAJO.md)
- ✅ Workflow trimestral backups
- ✅ Manejo de costos APIs externas
- ✅ Diseño MCP server sigma-close-session-validator

### Lo que falta para Nivel 2 (priorizado)

**Tier crítico** (sin esto NO es Nivel 2 real):

1. **CI/CD obligatorio** — GitHub Actions con gates de linters, tests, types, security scan, migrations dry-run. Branch protection en `main`. Sprint 3.

2. **Staging environment real** — Réplica de Stallen en proyecto Supabase separado. Pipeline PR → staging → manual approval → prod. Smoke tests post-deploy. Sprint 3-4.

3. **Tests adversariales sistemáticos** — Skill `/sigma:adversarial-tests` que genere automáticamente tests de inputs vacíos/malformados/edge/race conditions. Librerías property-based testing (Hypothesis, fast-check). Sprint 4.

4. **Observabilidad real** — Sentry + logging estructurado (structlog) + health checks + dashboard básico (Grafana Cloud free tier) + alertas configuradas. Sprint 4.

5. **Backups con restore probado** — Ritual trimestral ya documentado, falta ejecución y validación. Sprint 5 (primer ciclo).

**Tier alto** (importante para Nivel 2 maduro):

6. **MCP servers propios** — Migrar IP de SigmaControl: validadores R/G/FG, patcher determinístico, capturar_adn como skill, sigma-close-session-validator. Sprint 2.

7. **Captura activa de dominio** — Skill `/sigma:capture-domain` que sistemáticamente extraiga reglas del negocio antes de implementar. Sprint 2.

8. **Release process formal** — SemVer + CHANGELOG.md automático (conventional-changelog) + release tags + release notes + rollback documentado. Sprint 5.

### Lo que NO está en scope (para Nivel 1-2)

- Compliance GDPR / SOC 2 (Nivel 3 only)
- Multi-tenant aislamiento estricto (Nivel 3)
- DR (Disaster Recovery) regional (Nivel 3)
- Soporte 24/7 con SLA documentado (Nivel 3)
- Auditoría externa de seguridad (Nivel 3)
- Onboarding sistematizado para devs nuevos (Nivel 3)

---

## Roadmap recalibrado para llegar a Nivel 2

| Sprint | Duración | Objetivo | Output verificable |
|---|---|---|---|
| 1 (actual) | 2 sem | Setup ecosistema | ✅ Stack instalado, validado, commiteado |
| 2 | 2 sem | IP único migrado como MCP servers + skills | Validadores R/G/FG funcionando + sigma-close-session-validator |
| 3 | 2 sem | CI/CD + Staging environment | GitHub Actions bloqueando + staging Stallen separado |
| 4 | 2 sem | Tests adversariales + Observabilidad | Sentry + dashboard + skill generador de tests |
| 5 | 1-2 sem | Validación empírica + Release process | Feature real de Stallen pasando el sistema completo + release v1.0 |
| 6 | 1 sem | Backups verificados + monitoring de costos | Restore test trimestral ejecutado + budget alerts configurados |

**Total estimado: 10-12 semanas para Nivel 2 sólido.**

---

## Criterios de revisión de esta decisión

Re-evaluar este ADR si:

1. **Stallen crece más rápido de lo esperado** (5+ clientes en menos de 6 meses) → considerar acelerar elementos de Nivel 3
2. **Aparece cliente empresarial con compliance requirements** → evaluar costo/beneficio de Nivel 3
3. **Cambia el modelo de negocio** (ej: pivoteo a SaaS multi-tenant) → re-arquitecturar
4. **Stallen tiene incidente serio que un Tier 3 hubiera prevenido** → considerar adopción anticipada

---

## Alternativas consideradas

### Alternativa A: Producto vendible desde el inicio

**Descartada porque**:
- Julián no tiene interés actual en venderlo
- Construir para market reduce velocidad de validación empírica
- Open core requiere overhead que no aporta a Stallen

### Alternativa B: Solo arquitectura mínima (Nivel 1 indefinido)

**Descartada porque**:
- Stallen ya tiene 1 cliente real → no es proyecto experimental
- Costo de errores serios > costo de construir Nivel 2
- Sin staging + CI/CD, riesgo de afectar cliente es alto

### Alternativa C: Construir Nivel 3 preventivamente

**Descartada porque**:
- Compliance + multi-tenant son trabajo significativo sin payoff inmediato
- YAGNI: construir features que no sabemos si vamos a necesitar
- Costo de oportunidad: ese tiempo invertido en Stallen real produce más valor

---

## Consecuencias

### Positivas

- Plan claro y acotado: 12 semanas con destino concreto
- Disciplina enforced pero no excesiva
- Tu yo del futuro tiene roadmap explícito
- Decisiones técnicas justificadas por nivel apuntado

### Negativas

- Si Stallen escala a Nivel 3 rápido, hay refactor pendiente
- Tier 3 features no están construidas (compliance, multi-tenant)
- Decisión revisable, no inmutable

### Mitigaciones

- Re-evaluar este ADR cada 3 meses
- Capturar fricciones reales en CUADERNO-BITACORA cuando aparezcan
- Trigger explícito documentado arriba para escalar a Nivel 3

---

## Referencias

- `CLAUDE.md` — Constitución
- `DEPARTAMENTO-DE-SOFTWARE.md` § 8 — 10 dimensiones de calidad
- `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md` — ADRs 001, 002, 003
- Conversación de Sprint 1 sesión 2026-05-13 que motivó este ADR

---

**Próxima revisión**: 2026-08-13 (3 meses) o cuando dispare criterio de revisión.
