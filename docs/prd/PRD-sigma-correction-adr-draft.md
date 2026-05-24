# PRD — `sigma:correction-adr-draft`

**Status**: DRAFT v0.1
**Date**: 2026-05-24 (Sprint 4 sesion 2)
**Owner**: Departamento de Software
**Related**: ADR-011 ACCEPTED v1.0 (Phase 2 — Trinidad Correctiva, Tier C handler)
**Upstream**: `sigma:finding_classifier` v0.1.0, `sigma:correction_agent_bounded` v0.1.0
**Protocolo**: Paso 1 del PROTOCOLO-CONSTRUCCION-CODIGO

---

## 1. Contexto

ADR-011 define Tier C como findings que requieren **decision humana** — NUNCA auto-fix. Son trade-offs arquitectonicos, politicas de seguridad, o decisiones de scope que solo un humano puede resolver.

El `correction-adr-draft` es el **cuarto y ultimo componente** de Phase 2. No fixea nada: genera material estructurado (ADR draft + PR comment) para que el humano decida sin partir de cero.

---

## 2. Problema que resuelve

**Hoy**: findings Tier C (CSP policies, violaciones hexagonales, scope deferrals) llegan como texto libre del reviewer. El operador tiene que crear un ADR desde cero, buscar CWEs, y redactar alternativas. Esto toma 15-30 minutos por finding.

**Tras este PRD**: el componente genera un ADR draft pre-llenado con metadata, alternativas estructuradas, y links a CWE/OWASP cuando aplica. El humano revisa, decide, y commitea. Tiempo estimado: 5 minutos por finding.

---

## 3. Intencion (one-liner)

> "Generar ADR drafts y PR comments estructurados para findings Tier C, bloqueando el commit hasta decision humana explicita."

---

## 4. Scope

### In scope

- **5 rule_ids Tier C** de `rules.yaml` v0.1.0: CSP-UNSAFE-EVAL, CSP-UNSAFE-INLINE, ARCH-HEXAGONAL-VIOLATION, SCOPE-DEFERRAL-DECISION, DEPENDENCY-CYCLE.
- **3 action_hints**: `adr-draft-with-cwe-link`, `flag-for-arch-review`, `flag-for-product-decision`.
- **Output por finding**: ADR draft file + summary JSON.
- **ADR numbering**: auto-detect next ADR number from `adr_directory`.
- **CWE/OWASP links**: lookup table estatica para security-related rules.
- **CLI invocable**: input JSON `ClassifiedFinding[]` (tier=C), output JSON `DraftResult[]` + exit code.
- **NO LLM**: 100% template-based, deterministico.

### Out of scope

- Auto-fix de cualquier tipo.
- PR comment posting (requiere GitHub API — v0.2).
- Blocking del commit (responsabilidad del integrador E2E).

---

## 5. Acceptance criteria

- **AC1**: dado un finding Tier C con action_hint conocido, genera un ADR draft en `adr_directory`.
- **AC2**: el ADR contiene secciones: Context, Decision (PENDING), Alternatives, Consequences, Related.
- **AC3**: para security rules (CSP-*), el ADR incluye link CWE.
- **AC4**: CLI recibe JSON stdin, emite JSON stdout, exit 0 siempre (findings Tier C no "fallan" — se documentan).
- **AC5**: idempotencia — si el ADR ya existe para este finding, retorna NO-OP.
- **AC6**: auto-detect next ADR number scanning `adr_directory`.

---

## 6. Constraints

- **C1**: sin LLM. 100% template + string interpolation.
- **C2**: sin dependencias nuevas fuera de stdlib Python + pyyaml (heredado).
- **C3**: ADR format sigue la convencion del proyecto (`decisions/ADR-NNN-slug.md`).

---

## 7. Metricas

- **MM1**: tiempo de generacion por draft (<1s, es template puro).
- **MM2**: % de findings Tier C que generan draft usable sin edicion manual del operador (target: >80%).
