# Proyecto Stallen — README

Este es el proyecto principal del Departamento de Software de Julián Vargas.
Es uso personal del Departamento aplicado a Stallen (empresa real en producción).

## Identificación

- **Proyecto**: Stallen
- **Owner**: Julián Vargas
- **Tier**: 1 — Commercial Robust (ver ADR-004 del Framework)
- **Stack**: Supabase + Vercel (Next.js)
- **Tipo**: ERP/sistema empresarial real en producción
- **Estado**: Sprint 2 Día 2 — preparando captura de dominio (T1)

## Estructura del proyecto

```
projects/stallen/
├── NORTE.md              # Visión del proyecto
├── HORIZONTE.md          # Hitos 1-3 meses
├── DEUDA-TECNICA.md      # Bandeja deuda
├── CUADERNO-BITACORA.md  # Bandeja ideas/observaciones
├── SIGUIENTE-SESION.md   # Plan próxima sesión
├── README.md             # Este archivo
├── domain-captures/      # Captura del dominio (output sigma-capture-domain)
├── features/             # Cada feature en su carpeta
├── decisions/            # ADRs específicos Stallen
├── workspace/            # Código real Stallen
├── auditoria/            # Memoria operativa Stallen
│   ├── sesion-activa.md
│   └── memoria-historial.md
└── .claude/              # Skills/agents específicos Stallen
    ├── skills/
    └── agents/
```

## Relación con el Framework

Stallen **consume** el Framework universal del Departamento:

- Reglas A1-A15 → aplican a todo código Stallen
- Anti-patterns → no se violan en Stallen
- SOLID + C1-C6 → estructuran el código
- Skills universales (sigma-capture-domain) → aplicables
- Protocolos → cierran sesiones Stallen

Stallen puede tener **overrides locales** cuando justificado en
`projects/stallen/decisions/ADR-XXX-override.md`.

## Cómo trabajar en Stallen

### Al abrir sesión nueva

1. Leer `NORTE.md` (~1 vez al mes) — visión del proyecto
2. Leer `HORIZONTE.md` — hitos actuales
3. Leer `SIGUIENTE-SESION.md` — plan inmediato
4. Leer `auditoria/sesion-activa.md` — estado al cerrar última sesión
5. (Si tocás código) Leer Framework `architecture/` para refrescar A1-A15

### Al cerrar sesión

Aplicar `PROTOCOLO-CIERRE-DEPARTAMENTO.md` del Framework (cuando exista),
actualizando los archivos en `projects/stallen/`:
- `auditoria/sesion-activa.md` (qué se hizo)
- `SIGUIENTE-SESION.md` (qué viene)
- `DEUDA-TECNICA.md` (si hay deuda nueva)
- `CUADERNO-BITACORA.md` (si hay ideas)

## Notas para Claude

- **Julián es vibe coder** (no programador profesional)
- **Tier 1 commercial robust** — defensas arquitectónicas estrictas
- **Stallen en producción real** — calidad importa
- **Aplicar audit empírico** cuando algo se declare "completo"
- **No proyectar cansancio del usuario** — anti-paternalismo

---

Creado: 2026-05-15 (Sprint 2 Día 2, Acción 2.0)
Por: ADR-007 (Separación Framework vs Proyectos)
