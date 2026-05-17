# Proyecto <PROJECT_NAME> — README

## Identificación

- **Proyecto**: <PROJECT_NAME>
- **Slug**: <PROJECT_SLUG>
- **Owner**: <OWNER>
- **Tier**: <TIER>
- **Stack**: <STACK>
- **Estado**: <ESTADO>

## Estructura

```
projects/<PROJECT_SLUG>/
├── NORTE.md
├── HORIZONTE.md
├── DEUDA-TECNICA.md
├── CUADERNO-BITACORA.md
├── SIGUIENTE-SESION.md
├── README.md (este)
├── domain-captures/
├── features/
├── decisions/
├── workspace/
├── auditoria/
└── .claude/
```

## Relación con el Framework

Este proyecto consume el Framework universal del Departamento.
Reglas A1-A15, anti-patterns, SOLID + C1-C6 aplican aquí.

Overrides locales en `decisions/ADR-XXX-override.md`.

## Cómo trabajar

### Al abrir sesión

1. `NORTE.md` (~1x mes)
2. `HORIZONTE.md`
3. `SIGUIENTE-SESION.md`
4. `auditoria/sesion-activa.md`
5. Framework `architecture/` si tocás código

### Al cerrar sesión

Aplicar `PROTOCOLO-CIERRE-DEPARTAMENTO.md` del Framework.

---

Creado: <YYYY-MM-DD>
