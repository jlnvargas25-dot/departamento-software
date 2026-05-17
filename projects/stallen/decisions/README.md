# Decisiones Stallen — ADRs específicos

ADRs específicos del proyecto Stallen.

## Diferencia con ADRs del Framework

- **Framework `decisions/`**: ADRs del Departamento mismo (cómo funciona el framework universal)
- **Este directorio**: ADRs específicos de Stallen (decisiones técnicas, overrides locales, decisiones de dominio)

## Convención

Formato `ADR-NNN-<titulo-corto>.md`. Numeración independiente del Framework
(empezar en ADR-001 para Stallen).

Sugeridos para arrancar (cuando los hagamos):
- ADR-001 — Stack Supabase + Vercel + Next.js (formalizar decisión)
- ADR-002 — Multitenancy RLS con `get_my_sc_company_id()` helper
- ADR-003 — Inmutabilidad de tablas críticas (mapeo A6 a tablas Stallen)
- ADR-004 — Convención de naming (en español, snake_case, etc.)

## Estado actual

Vacío — primeros ADRs pendientes cuando arranque T1+ con dominio capturado.
