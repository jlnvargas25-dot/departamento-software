# HORIZONTE — Stallen

> **Propósito**: hitos del horizonte activo (1-3 meses). Se lee al arrancar
> cada sesión. Cuando todos los hitos están DONE, se archiva en
> `auditoria/horizontes/` y se reescribe con el próximo horizonte.

**Versión**: 0.1 (placeholder inicial)
**Última actualización**: 2026-05-15
**Estado**: ⚠️ PENDIENTE — vale planificar el primer horizonte de Stallen

---

## Horizonte actual: H-1 "Inicialización Stallen en el Departamento"

**Fecha objetivo**: 2026-05-31 (~2 semanas)

### Hitos

#### H-1.1 — Capturar dominio Stallen
**Estado**: ⏳ TODO
**Owner**: Julián + Claude
**Output esperado**: `projects/stallen/domain-captures/stallen-domain.md`
**Definition of Done**:
- Aplicación de `.claude/skills/sigma-capture-domain/SKILL.md` (6 steps)
- Archivo ≤ 50 líneas (compacto, validado)
- Validado por Julián como stakeholder
- Captura de módulos, invariantes, tablas inmutables, escala operativa

**Sub-tareas**:
- [ ] Aplicar Step 1 (captura dominio en lenguaje natural)
- [ ] Aplicar Step 2 (invariantes del dominio)
- [ ] Aplicar Step 3 (reglas de negocio críticas)
- [ ] Aplicar Step 4 (validación con Julián)
- [ ] Aplicar Step 5 (traducir a invariantes técnicos INV-001, INV-002, ...)
- [ ] Aplicar Step 6 (producir stallen-domain.md)

---

#### H-1.2 — Validar ecosistema (sandbox Spec Kit) [opcional, mover a H-2 si falta tiempo]
**Estado**: ⏳ TODO
**Owner**: Julián + Claude
**Output esperado**: `projects/sandbox-spec-kit/` con resultados validación
**Definition of Done**:
- Spec Kit instalado y probado end-to-end con caso simple
- 4 extensions críticas probadas (Architecture Guard, Red Team, Staff Review, Spec Validate)
- Decisión documentada: adoptar / rechazar / mezclar

**Notas**:
- Va en `projects/sandbox-spec-kit/` (no es Stallen specific)
- Tiempo estimado: 1-2 hs

---

#### H-1.3 — Stallen feature 1 (primer feature real construido con el sistema completo)
**Estado**: ⏳ TODO (depende de H-1.1)
**Owner**: Julián + Claude
**Output esperado**: feature funcional en `projects/stallen/features/feature-001-<nombre>/`
**Definition of Done**:
- Feature elegido (pequeño, validador): ¿login? ¿gestión productos básico? ¿caja simple?
- Aplicado workflow completo del Departamento:
  - Captura dominio (T1) ✓
  - Spec
  - Plan
  - Tasks
  - Implementación
  - Tests adversariales (A15)
  - Code review (GGA)
  - Validación
  - Documentación
- Deploy a staging
- Retrospectiva de qué funcionó y qué falló

**Estimación**: 3-5 días (con todas las dependencias resueltas)

---

#### H-1.4 — Retrospectiva Sprint 2 + decisiones para Sprint 3
**Estado**: ⏳ TODO (después de H-1.3)
**Owner**: Julián + Claude
**Output esperado**: ADR-008 (o más) con decisiones derivadas
**Definition of Done**:
- ¿Adoptamos Spec Kit definitivamente?
- ¿Cuáles fueron las 10 skills T2.2 que SÍ valió construir vs cuáles fueron reemplazadas por ecosistema?
- ¿Cómo escalamos a feature 2, 3, N de Stallen?
- ¿Necesitamos automatización (`departamento new-project`)?

---

## Estado general del horizonte H-1

```
H-1.1 (capturar dominio)     ⏳ TODO  (próximo)
H-1.2 (sandbox Spec Kit)     ⏳ TODO  (opcional/parallel)
H-1.3 (Stallen feature 1)    ⏳ TODO  (depende de H-1.1)
H-1.4 (retrospectiva)        ⏳ TODO  (último)
```

**Próxima acción concreta**: T1 (H-1.1) — capturar dominio Stallen.

---

## Próximo horizonte tentativo: H-2 "Escalado Stallen"

(Para planificar después de cerrar H-1)

Hipótesis de hitos:
- H-2.1 — Stallen features 2-5 (escalar a más features con el sistema)
- H-2.2 — sigma-validators-r MCP server (Sprint 2 T2 original, si no lo cubre Spec Kit)
- H-2.3 — sigma-close-session-validator MCP server (Sprint 2 T3 original)
- H-2.4 — Engram operativo (WSL setup o decisión arquitectónica)
- H-2.5 — Automatización `departamento new-project` (si hay 2do proyecto real)

---

## Historial de horizontes

(Cuando se cierren, mover acá con retrospectiva)

- H-0 (pre-arranque): construir el Framework Departamento → ✅ DONE (Sprint 1 + Sprint 2 Día 1)

---

## Versionado

- v0.1 (2026-05-15) — INICIAL. Primer horizonte H-1 definido para arrancar Stallen.
