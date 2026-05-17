# ⚠️ Esta carpeta se MOVIÓ a projects/<slug>/workspace/

A partir de ADR-007 (2026-05-15, Sprint 2 Día 2), el código real vive
dentro de cada proyecto, no en la raíz del Framework.

## Nueva ubicación

- **Stallen**: `projects/stallen/workspace/`
- **Otros proyectos futuros**: `projects/<slug>/workspace/`

## Por qué

El Framework universal (raíz) NO debe tener código específico de proyectos.
Cada proyecto tiene su workspace en su carpeta de proyecto.

Ver `decisions/ADR-007-separacion-framework-vs-proyectos.md` para detalle.

## Acción

Esta carpeta queda vacía y vale **eliminarla manualmente** desde PowerShell:

```powershell
Remove-Item -Path "C:\DEPARTAMENTO-SOFTWARE\workspace" -Recurse
```

Antes de eliminar, verificar que el `.gitkeep` no es relevante.
