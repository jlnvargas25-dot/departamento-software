# Templates — Project Skeleton

> **Propósito**: archivos template que se copian al crear proyecto nuevo en
> `projects/<slug>/`. Esto es manual (v1.0) — sin script de automatización
> todavía (esperar 2do proyecto real antes de automatizar).

## Cómo usar

### Crear proyecto nuevo manualmente

```powershell
# 1. Crear carpeta del proyecto
cd C:\DEPARTAMENTO-SOFTWARE
mkdir projects\<slug>
mkdir projects\<slug>\domain-captures
mkdir projects\<slug>\features
mkdir projects\<slug>\decisions
mkdir projects\<slug>\workspace
mkdir projects\<slug>\auditoria
mkdir projects\<slug>\.claude
mkdir projects\<slug>\.claude\skills
mkdir projects\<slug>\.claude\agents

# 2. Copiar templates
copy templates\project-skeleton\NORTE.template.md projects\<slug>\NORTE.md
copy templates\project-skeleton\HORIZONTE.template.md projects\<slug>\HORIZONTE.md
copy templates\project-skeleton\DEUDA-TECNICA.template.md projects\<slug>\DEUDA-TECNICA.md
copy templates\project-skeleton\CUADERNO-BITACORA.template.md projects\<slug>\CUADERNO-BITACORA.md
copy templates\project-skeleton\SIGUIENTE-SESION.template.md projects\<slug>\SIGUIENTE-SESION.md
copy templates\project-skeleton\README.template.md projects\<slug>\README.md
copy templates\project-skeleton\auditoria\sesion-activa.template.md projects\<slug>\auditoria\sesion-activa.md

# 3. Editar manualmente cada archivo reemplazando placeholders:
#    - <PROJECT_SLUG> → nombre del proyecto (ej. "amigo-saas")
#    - <PROJECT_NAME> → nombre humano (ej. "Amigo SaaS")
#    - <TIER> → 0, 1, 2, etc.
#    - <STACK> → tecnologías (ej. "Supabase + Vercel + Next.js")
#    - Otros placeholders marcados con ⚠️

# 4. Commit inicial
git add projects/<slug>
git commit -m "feat(project): inicializar proyecto <slug>"
git push
```

### Crear proyecto sandbox (validación de tools/ecosistema)

Para sandbox (no es proyecto real, es validación):

```powershell
mkdir projects\sandbox-<nombre>
# No necesita todos los archivos, solo lo mínimo:
# - README.md explicando qué validás
# - workspace/ con los experimentos
```

## Templates disponibles

- `NORTE.template.md` — visión del proyecto
- `HORIZONTE.template.md` — hitos 1-3 meses
- `DEUDA-TECNICA.template.md` — bandeja deuda
- `CUADERNO-BITACORA.template.md` — bandeja ideas
- `SIGUIENTE-SESION.template.md` — handoff táctico
- `README.template.md` — overview del proyecto
- `auditoria/sesion-activa.template.md` — memoria operativa

## Automatización futura (Sprint 3+)

Cuando haya evidencia de 2do proyecto real con misma estructura, vale
construir:

```powershell
# Script propuesto (NO existe todavía)
.\scripts\new-project.ps1 -Name <slug> -Tier 1 -Stack supabase-vercel
```

Que automatice los 4 pasos de arriba.

NO se construye preventivamente.
