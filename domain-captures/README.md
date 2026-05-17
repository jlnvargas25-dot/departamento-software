# ⚠️ Esta carpeta se MOVIÓ a projects/<slug>/domain-captures/

A partir de ADR-007 (2026-05-15, Sprint 2 Día 2), las capturas de dominio
viven dentro de cada proyecto, no en la raíz del Framework.

## Nueva ubicación

- **Stallen**: `projects/stallen/domain-captures/`
- **Otros proyectos futuros**: `projects/<slug>/domain-captures/`

## Por qué

El Framework universal (raíz) NO debe tener capturas específicas de proyectos.
Cada proyecto tiene su propia captura en su carpeta de proyecto.

Ver `decisions/ADR-007-separacion-framework-vs-proyectos.md` para detalle.

## Acción

Esta carpeta queda vacía y vale **eliminarla manualmente** desde PowerShell:

```powershell
Remove-Item -Path "C:\DEPARTAMENTO-SOFTWARE\domain-captures" -Recurse
```

Pero quedó este README como recordatorio en caso de que alguien la recree por confusión.
