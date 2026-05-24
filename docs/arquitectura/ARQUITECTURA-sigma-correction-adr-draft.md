# Arquitectura tecnica — `sigma:correction-adr-draft`

**Status**: DRAFT v0.1
**Date**: 2026-05-24 (Sprint 4 sesion 2)
**Related**: PRD-sigma-correction-adr-draft.md, ADR-011 ACCEPTED v1.0

---

## 1. Vision general

El componente mas simple de la trinidad: Python puro que llena templates markdown para findings Tier C. Sin LLM, sin subprocess, sin rollback (no modifica archivos existentes — solo crea nuevos).

```
ClassifiedFinding[] (tier=C)
        │
        ▼
sigma:correction_adr_draft
  1. Lookup template por action_hint
  2. Auto-detect next ADR number
  3. Fill template con finding metadata
  4. Write ADR file
  5. Return DraftResult
        │
        ▼
DraftResult[] (stdout) + ADR files en disco
```

## 2. Modulos

```
framework/sigma/correction_adr_draft/
├── __init__.py
├── models.py           # DraftResult, DraftStatus
├── numbering.py        # auto-detect next ADR number
├── drafter.py          # template filling + file writing
├── cli.py              # stdin/stdout JSON
├── cwe_links.py        # static CWE/OWASP lookup
└── tests/
    ├── __init__.py
    ├── test_models.py
    ├── test_numbering.py
    ├── test_drafter.py
    └── test_cli.py
```

## 3. Decisiones

- **Template inline** (no YAML files): Tier C solo tiene 3 action_hints con templates cortos. Inline en `drafter.py` es mas simple que un loader YAML separado.
- **Sin rollback**: solo crea archivos nuevos, nunca modifica existentes. `unlink()` si algo falla.
- **CWE links estaticos**: dict hardcoded en `cwe_links.py`. 5 entries. No necesita DB ni fetch.

## 4. Stories

| Story | Descripcion | Tests est. |
|-------|-------------|-----------|
| S-1 | models + numbering + cwe_links | ~10 |
| S-2 | drafter (template fill + write) | ~10 |
| S-3 | CLI + idempotency | ~8 |

**Estimacion**: ~4hs, ~28 tests, ~200 LOC prod.
