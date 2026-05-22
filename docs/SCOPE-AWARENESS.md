# Scope-Aware Verification — Operacional

**Versión**: 1.0 (2026-05-21)
**Phase 1 de**: `decisions/ADR-011-capa-correctiva-y-scope-aware.md`
**Status**: PROPOSED (pendiente validación M1)

---

## Qué es

Mecanismo declarativo para que GGA (el code reviewer pre-commit) aplique **distinto threshold de severidad** según el scope del código que está revisando.

Resuelve el dolor empírico de Sprint 1: GGA bloqueó la Iteración 3 en 4 rounds porque aplicaba criterio de PRODUCCIÓN a un sandbox de validación empírica. Findings reales pero irrelevantes para el scope ahogaron las señales que sí importaban.

---

## Cómo se activa

Variable de entorno `FRAMEWORK_SCOPE`. Tres valores reconocidos:

| Valor       | Archivo de reglas      | Cuándo usar                                    |
|-------------|------------------------|------------------------------------------------|
| `sandbox`   | `AGENTS-sandbox.md`    | Validación empírica del Framework, prototipos. |
| `staging`   | `AGENTS.md` (default)  | Pre-producción.                                |
| `production`| `AGENTS.md` (default)  | Código que llega a usuarios reales.            |

Si `FRAMEWORK_SCOPE` no está definido, default es `production` (fail-safe — el rigor pleno se aplica por omisión, nunca al revés).

### Activación temporal (una sesión)

```bash
# Linux / Mac / Git Bash en Windows:
export FRAMEWORK_SCOPE=sandbox
git commit -m "feat(sandbox): cambio"

# PowerShell:
$env:FRAMEWORK_SCOPE = "sandbox"
git commit -m "feat(sandbox): cambio"
```

### Activación persistente (proyecto)

Para un sandbox dedicado (ej. `projects/sandbox-stack/`), agregar al `.envrc` o equivalente:

```bash
export FRAMEWORK_SCOPE=sandbox
```

Esto requiere `direnv` o equivalente para auto-cargar al entrar al directorio.

---

## Qué se relaja en `sandbox`

Reglas que **bajan a WARN** (no bloquean) en sandbox vs production:

- `console.log/error/warn` en TypeScript / `print()` en Python
- Migration naming estricto (`YYYYMMDDHHmm_*.sql`)
- Non-null assertions `x!`
- Type casts `as any` con justificación inline
- CSP `unsafe-eval` / `unsafe-inline`
- CORS wildcard `*`
- Cobertura de tests mínima (≥ 50% sandbox vs ≥ 70% prod)
- ADRs obligatorios para cada excepción
- Funciones > 50 líneas / Clases > 300 líneas
- `request_id` propagado end-to-end

## Qué SIGUE BLOQUEANTE incluso en `sandbox`

Reglas que NO cambian (no hay scope que las relaje):

- Secrets hardcoded (API keys, tokens, passwords)
- SQL injection (string interpolation en queries)
- RLS deshabilitada en tablas con datos
- `SECURITY DEFINER` sin `search_path` explícito
- TypeScript `strict: false` o `// @ts-ignore` sin razón
- Imports circulares
- Hard delete de datos de negocio
- `TIMESTAMPTZ` faltante en DB
- Conventional Commits malformados
- WIP commits directos en `main`

---

## Cómo funciona técnicamente

El hook `.git/hooks/pre-commit` lee `FRAMEWORK_SCOPE`, mapea a `AGENTS-{scope}.md`, hace un **swap temporal** del campo `RULES_FILE` en `.gga`, ejecuta `gga run`, y **restaura `.gga`** (con `trap` para garantizar restore incluso si gga crashea).

`.gga` queda versionado siempre apuntando a `AGENTS.md` (default production). El swap es ephemeral por commit.

---

## Métrica de éxito (M1 del ADR-011)

**Hipótesis**: con `FRAMEWORK_SCOPE=sandbox` activo, GGA cierra el sandbox-stack en **≤ 2 rounds** (vs 4 observados en Iteración 3 sin scope-aware).

**Validación pendiente**:
1. Re-correr GGA sobre `stash@{0}` (GGA round 4 cleanup deferido).
2. Contar rounds hasta exit code 0.
3. Si ≤ 2 → M1 cumplido → ADR-011 puede avanzar a ACCEPTED tras Phase 2 (Tier A).
4. Si > 2 → revisar qué reglas siguen ladrando y calibrar `AGENTS-sandbox.md`.

---

## Limitaciones conocidas

- **Hook git no se versiona**: `.git/hooks/pre-commit` es local. Cada operador del Framework debe instalarlo en su clon. Trade-off aceptado para Phase 1 (cura barata).
- **Swap de `.gga` es file-level**: si dos commits corren en paralelo (raro en pre-commit), el segundo podría ver el `.gga` modificado. Para Sprint 2 no es problema (un dev local). Phase 2 puede mover a wrapping puro sin tocar archivo.
- **No parametriza por subdirectorio**: el scope aplica al commit entero. Si el commit toca sandbox + producción, gana production (más seguro). Future work si aparece el caso.
- **Granularidad WARN/BLOQUEANTE**: depende de cómo GGA interprete las anotaciones en `AGENTS-sandbox.md`. Si el modelo no respeta el downgrade, hay que iterar el prompting del archivo.

---

## Reversión

Para desactivar scope-awareness (volver al hook original):

```bash
# El hook original era trivial:
cat > .git/hooks/pre-commit << 'EOF'
#!/usr/bin/env bash
# ======== GGA START ========
gga run || exit 1
# ======== GGA END ========
EOF
chmod +x .git/hooks/pre-commit
```

---

## Referencias

- `decisions/ADR-011-capa-correctiva-y-scope-aware.md` — Decisión de arquitectura.
- `AGENTS.md` — Reglas production (default).
- `AGENTS-sandbox.md` — Subset relaxed para sandbox.
- `.gga` — Configuración GGA (versionada, apunta a production por default).
- `.git/hooks/pre-commit` — Hook wrapper scope-aware (local, NO versionado).
