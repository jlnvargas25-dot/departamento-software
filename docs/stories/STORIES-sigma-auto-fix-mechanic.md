# Stories ejecutables — `sigma:auto-fix-mechanic`

**Status**: DRAFT v0.1
**Date**: 2026-05-22 (Sprint 3 sesión 3 — Paso 4 del PROTOCOLO-CONSTRUCCION-CODIGO)
**Related**: PRD-sigma-auto-fix-mechanic.md, auto-fix-mechanic-rules.yaml.draft, codemod-toolbox.md, ARQUITECTURA-sigma-auto-fix-mechanic.md
**Protocolo**: Paso 4 (Planificar) del PROTOCOLO-CONSTRUCCION-CODIGO

---

## Resumen del backlog

| Story | Título | Estimación | Sesión | Dependencias |
|-------|--------|-----------|--------|--------------|
| S-1 | Foundation: pyproject + models + loader | M (~2hs) | 4 | — |
| S-2 | Pre-flight check toolbox + Invoker | S (~1.5hs) | 4 | S-1 |
| S-3 | Snapshot + rollback atómico | S (~1hs) | 4 | S-1 |
| S-4 | Verifier dispatcher (5 methods) | M (~2hs) | 4 | S-1 |
| S-5 | Orchestrator + escalation logic | M (~2hs) | 4 | S-2, S-3, S-4 |
| S-6 | Codemods ts-morph (4 scripts custom) | L (~4hs) | 5 | S-1 (para metadata; ejecutables sin core) |
| S-7 | Codemods Python custom (2 scripts) | M (~1.5hs) | 5 | S-1 |
| S-8 | CLI + M3 empirical measurement | M (~2hs) | 5 | S-5, S-6, S-7 |

**Total estimado**: 16 horas → 2 sesiones (~8hs cada una).
- **Sprint 3 sesión 4** (build core): S-1 → S-2 → S-3 → S-4 → S-5 = ~8.5hs
- **Sprint 3 sesión 5** (codemods + integración): S-6 → S-7 → S-8 = ~7.5hs

DAG de dependencias (sin ciclos, verificable):

```
        S-1 (foundation)
        / | | \
      S-2 S-3 S-4 S-6, S-7 (codemods — no dependen del core para correr standalone)
        \ | /
        S-5 (orchestrator)
          |
          S-8 (CLI + M3)
```

---

## S-1 — Foundation: pyproject + models + loader

**Estimación**: M (~2 horas).
**Sesión**: 4 (primera del build).
**Dependencias**: ninguna (primera story).

### Descripción

Setup del package Python `sigma.auto_fix_mechanic` con la estructura mínima ejecutable: pyproject.toml (compatible con el de classifier), `models.py` con dataclasses inmutables (PatchResult, Handler, ToolboxStatus), `loader.py` que carga + valida `auto-fix-mechanic-rules.yaml`.

### Tareas

1. Crear `framework/sigma/auto_fix_mechanic/__init__.py` con public API placeholder.
2. Extender `framework/pyproject.toml` o crear scoped pyproject según patrón del classifier — agregar entry point CLI `sigma-mechanic` (paralelo a `sigma-classify`).
3. Crear `models.py` con dataclasses inmutables:
   - `PatchResult` (output público)
   - `Handler` (interno)
   - `ToolboxStatus` (interno)
   - Enums tipados (FixStatus, VerificationResult).
4. Crear `loader.py` con `load_handlers(yaml_path) → dict[str, Handler]`.
5. Promover `docs/dominio/auto-fix-mechanic-rules.yaml.draft` → `framework/sigma/auto_fix_mechanic/rules.yaml` v0.1.0.
6. Validación schema YAML al cargar (mínimo: `version`, `handlers`, `defaults`, `preflight` presentes; cada handler tiene `tool` + (`invocation` OR `codemod_script`)).

### Acceptance criteria

**AC-S1-1**: Importar `from sigma.auto_fix_mechanic import load_handlers` funciona desde el repo root sin error.

**AC-S1-2**: `load_handlers("framework/sigma/auto_fix_mechanic/rules.yaml")` retorna dict con 15 entries (los 15 rule_ids Tier A v0.1.0). Cada Handler tiene `tool` y al menos uno de (`invocation`, `codemod_script`) poblado.

**AC-S1-3**: YAML inválido (campo `version` ausente, handler sin `tool`, etc.) → `load_handlers` raise `InvalidRulesYamlError` con mensaje claro indicando qué falta.

**AC-S1-4**: PatchResult es frozen dataclass — mutación raise `dataclasses.FrozenInstanceError`.

**AC-S1-5**: Tests unitarios para los 4 ACs anteriores + ≥3 casos adversariales (YAML vacío, YAML con tabs en lugar de spaces, YAML con caracteres no-UTF-8).

### Tests planeados

`tests/test_loader.py` (~10 tests).
`tests/test_models.py` (~5 tests, frozen check + serialization).

### Definition of done

- [ ] Public API importable.
- [ ] 15/15 handlers cargados desde YAML productivo.
- [ ] Validación schema funciona (invalid → error claro).
- [ ] Models frozen.
- [ ] Tests pasan (≥15 tests).

---

## S-2 — Pre-flight check toolbox + Invoker

**Estimación**: S (~1.5 horas).
**Sesión**: 4.
**Dependencias**: S-1 (necesita Handler model + load_handlers).

### Descripción

Implementar el pre-flight check (AM9) que verifica disponibilidad de tools externos al boot, y el invoker (subprocess wrapper) que ejecuta tools con timeout, captura stdout/stderr, y maneja exit codes.

### Tareas

1. Crear `preflight.py` con `run_preflight_check(handlers: dict) → ToolboxStatus`:
   - Por cada `preflight.required_tools[]` del YAML, ejecutar `check_command` con timeout 5s.
   - Por cada `preflight.optional_tools[]`, mismo check; si falta → marcar handlers asociados como `optional_tool_unavailable`.
   - Retornar ToolboxStatus con required_tools_ok, missing_required, optional_tools_ok, missing_optional, disabled_handlers.
2. Crear `invoker.py` con `invoke_tool(handler: Handler, file: Path) → InvokeResult`:
   - Sustituir `<file>` en `handler.invocation` por el path real.
   - Ejecutar con `subprocess.run(..., capture_output=True, timeout=30, shell=False)`.
   - Retornar `InvokeResult(exit_code, stdout, stderr, elapsed_ms)`.
   - Caso especial: si tool retorna `noop`-equivalent (eslint exit 0 con "0 problems"), marcar como noop.
3. Manejo de errores: tool no encontrado en PATH → `ToolNotFoundError`. Timeout → `ToolTimeoutError`. Permission denied → `ToolPermissionError`.

### Acceptance criteria

**AC-S2-1**: `run_preflight_check(handlers)` con todos los tools instalados → `ToolboxStatus(required_tools_ok=True, optional_tools_ok=True, ...)`.

**AC-S2-2**: Con `node` faltando del PATH (mock vía PATH manipulation) → `required_tools_ok=False`, `missing_required=["node", ...]`.

**AC-S2-3**: Con `ts-morph` instalado pero ESLint faltando → `required_tools_ok=False`. (Eslint es required, ts-morph es optional.)

**AC-S2-4**: Con ts-morph faltando pero todo lo required OK → `optional_tools_ok=False`, `disabled_handlers` contiene los 4 rule_ids ts-morph.

**AC-S2-5**: `invoke_tool(handler_eslint, file)` ejecuta el comando real y retorna InvokeResult con exit_code y elapsed_ms.

**AC-S2-6**: Tool con timeout 30s excedido → raise `ToolTimeoutError` + el subprocess es killed (no zombie).

**AC-S2-7**: Tests adversariales: file path con espacios, file path con unicode, comando con shell metacharacters (validar que `shell=False` previene injection).

### Tests planeados

`tests/test_preflight.py` (~6 tests, varios mock de PATH).
`tests/test_invoker.py` (~8 tests, incluyendo timeout + permission denied).

### Definition of done

- [ ] Pre-flight check funcional con required + optional separados.
- [ ] Invoker con timeout + clean exit handling.
- [ ] Sin shell injection (shell=False enforced).
- [ ] Tests pasan (≥14 tests).

---

## S-3 — Snapshot + rollback atómico

**Estimación**: S (~1 hora).
**Sesión**: 4.
**Dependencias**: S-1.

### Descripción

Implementar `FileSnapshot` context manager (sección 6.3 de arquitectura): snapshot in-memory de bytes + mtime al entrar, restore() para rollback, unchanged() para detectar noop, diff_summary() para hash del cambio.

### Tareas

1. Crear `snapshot.py` con clase `FileSnapshot`:
   - `__init__(path)`: capturar `original_content = path.read_bytes()`, `original_mtime = path.stat().st_mtime`.
   - `restore()`: `path.write_bytes(self.original_content)` (idempotente).
   - `unchanged()`: comparar bytes actuales vs originales.
   - `diff_summary()`: hashes SHA256 truncados pre/post.
   - `__enter__` / `__exit__`: si excepción no controlada, rollback automático.
2. Manejo de archivos grandes: si `path.stat().st_size > 100MB` → raise `FileTooLargeForSnapshotError` (test adversarial 11 de arquitectura).
3. Lock por archivo (`filelock` library) para prevenir race conditions (R-5 + RM5 PRD).

### Acceptance criteria

**AC-S3-1**: `with FileSnapshot(p) as snap: p.write_bytes(b"modified"); snap.restore()` → el archivo vuelve al contenido original.

**AC-S3-2**: `snap.unchanged()` retorna True si no hubo cambios; False si bytes cambiaron.

**AC-S3-3**: `snap.diff_summary()` retorna string con formato `"sha256:<8chars> → sha256:<8chars>"`.

**AC-S3-4**: Si dentro del `with` se lanza excepción no controlada → al salir del context, archivo está restaurado.

**AC-S3-5**: Archivo >100MB → `FileTooLargeForSnapshotError` al construir.

**AC-S3-6**: Dos `FileSnapshot(p)` concurrentes → segunda espera por lock o falla con timeout claro.

**AC-S3-7**: `restore()` llamado dos veces → segunda invocación es no-op (no double-write).

### Tests planeados

`tests/test_snapshot.py` (~10 tests, incluyendo concurrent + large file mock).

### Definition of done

- [ ] FileSnapshot con bytes preservation.
- [ ] Rollback automático en excepción.
- [ ] Lock por archivo funcional.
- [ ] Test de archivo grande (mock).
- [ ] Tests pasan (≥10 tests).

---

## S-4 — Verifier dispatcher (5 methods)

**Estimación**: M (~2 horas).
**Sesión**: 4.
**Dependencias**: S-1, S-2 (necesita Invoker para algunos methods).

### Descripción

Implementar el dispatcher de verificación post-fix. Cada handler especifica un `verification.method`; el verifier lo invoca y retorna `VerifyResult(passed, detail)`.

### Tareas

1. Crear `verifier.py` con `run_verification(spec: dict, file: Path) → VerifyResult`:
   - Dispatcher por `spec.method`: `re-run-eslint`, `re-run-prettier-check`, `ast-check`, `filename-regex`, `regex-grep`.
2. Implementar los 5 methods:
   - `re-run-eslint(spec, file)`: invocar eslint con `--quiet --rule`; exit 0 → passed.
   - `re-run-prettier-check(spec, file)`: invocar prettier --check; exit 0 → passed.
   - `ast-check(spec, file)`: invocar el codemod script en modo `--verify`; exit 0 → passed.
   - `filename-regex(spec, file)`: glob directory + check regex match en filenames.
   - `regex-grep(spec, file)`: leer file content + re.findall; assertion según `spec.assertion`.
3. Detail string: capturar stderr/stdout del tool para diagnóstico (cap a 200 chars en PatchResult.rollback_reason).
4. Timeout por verification: 15s default (más corto que invocación porque verify suele ser lighter).

### Acceptance criteria

**AC-S4-1**: `run_verification({"method": "re-run-eslint", "command": "..."}, file)` ejecuta el comando y retorna VerifyResult con passed según exit_code.

**AC-S4-2**: Method desconocido → `UnknownVerificationMethodError` con lista de methods soportados.

**AC-S4-3**: Cada uno de los 5 methods tiene al menos 2 tests (passed + failed case) = 10 tests mínimo.

**AC-S4-4**: Timeout 15s excedido → VerifyResult(passed=False, detail="verification_timeout_exceeded").

**AC-S4-5**: Spec malformado (falta `command` para re-run-eslint) → `InvalidVerificationSpecError` al validar (no en ejecución).

### Tests planeados

`tests/test_verifier.py` (~12 tests, 2+ por method).

### Definition of done

- [ ] 5 methods funcionales.
- [ ] Dispatcher con error claro para method desconocido.
- [ ] Timeout por verify.
- [ ] Tests pasan (≥12 tests).

---

## S-5 — Orchestrator + escalation logic

**Estimación**: M (~2 horas).
**Sesión**: 4 (última del día).
**Dependencias**: S-2 (preflight + invoker), S-3 (snapshot), S-4 (verifier).

### Descripción

El core del mechanic: `process_finding(finding, handlers) → PatchResult`. Implementa la lógica de orquestación de la sección 6.2 de arquitectura: lookup handler → snapshot → invoke → verify → rollback OR commit.

### Tareas

1. Crear `orchestrator.py` con:
   - `process_finding(finding, handlers) → PatchResult` (función principal).
   - `run_batch(findings, handlers) → list[PatchResult]` (wrapper iterativo).
2. Implementar los 4 casos del flow (sección 6.2 arquitectura):
   - Caso 1: handler is None → `escalated_to_c` con `escalation_reason="handler_not_implemented"`.
   - Caso 2: optional tool unavailable → `escalated_to_c` con `escalation_reason="optional_tool_unavailable:<tool>"`.
   - Caso 3a: tool invocation falla (exit_code != 0 con stderr) → rollback + `rolled_back` con `rollback_reason`.
   - Caso 3b: verification falla → rollback + `rolled_back` con razón post-fix.
   - Caso 3c: verification OK + archivo cambió → `applied` con patch_summary.
   - Caso 3d: verification OK + archivo NO cambió → `noop_already_clean` (AM7 idempotencia).
3. Time tracking: cada PatchResult tiene `elapsed_ms` real.
4. Logging estructurado (stderr): un log line por finding procesado con tier/result/elapsed.

### Acceptance criteria

**AC-S5-1**: `process_finding` con handler que aplica fix exitosamente → `PatchResult(fix_status="applied", verification="passed", patch_summary populated)`.

**AC-S5-2**: `process_finding` con rule_id sin handler → `PatchResult(fix_status="escalated_to_c", escalation_reason="handler_not_implemented")`.

**AC-S5-3**: `process_finding` con handler que su tool crashea (mock exit code 1) → `PatchResult(fix_status="rolled_back", verification="failed", rollback_reason contains tool stderr first 200 chars)`. Working tree del archivo limpio (sin cambios).

**AC-S5-4**: `process_finding` con verification mock que retorna failed → rollback + escalation.

**AC-S5-5**: `process_finding` con file ya limpio (segundo run consecutivo, AM7) → `PatchResult(fix_status="noop_already_clean", verification="passed")`.

**AC-S5-6**: `process_finding` con optional_tool_unavailable=True → `escalated_to_c` sin intentar invocar tool.

**AC-S5-7**: `run_batch([])` → retorna lista vacía sin errores (empty input).

**AC-S5-8**: `elapsed_ms` es coherente (>0 cuando se ejecutó algo; idempotente ronda 0-50ms).

### Tests planeados

`tests/test_orchestrator.py` (~15 tests, incluye los 4 casos + edge cases).

### Definition of done

- [ ] process_finding cubre los 4 casos del flow.
- [ ] Rollback atómico verificado en tests.
- [ ] Idempotencia funcional.
- [ ] Logging estructurado a stderr.
- [ ] Tests pasan (≥15 tests).

---

## S-6 — Codemods ts-morph (4 scripts custom)

**Estimación**: L (~4 horas).
**Sesión**: 5 (primera de la segunda sesión).
**Dependencias**: S-1 (para metadata Handler; los scripts son ejecutables standalone).

### Descripción

Implementar los 4 codemods custom que requieren ts-morph (TypeScript AST library): el orquestador los invoca via subprocess (`node <script>.js <file>` o `node <script>.js --verify <file>`).

### Tareas

1. Setup ts-morph: crear `codemods/package.json` con ts-morph como dev dep (NO se instala globalmente; el proyecto target debe tener ts-morph o se usa npx).
2. Implementar **`non_null_to_optional.ts`**:
   - AST query: `expr.kind === SyntaxKind.NonNullExpression`.
   - Transformación: contextual — si está dentro de PropertyAccessExpression → optional chain (`?.`); si standalone → guard (`if (x) { ... }`).
   - Modo `--verify`: contar NonNullExpression nodes, exit 0 si == 0.
3. Implementar **`console_to_logger.ts`**:
   - AST query: CallExpression con callee=`console.{log,error,warn,info}`.
   - Transformación: reemplazar con `logger.{info,error,warn,info}`. Inject `import { logger } from '@/lib/logger'` si no existe.
   - Manejo de alias `@/lib/logger`: leer tsconfig.json `paths` para resolver. Si no resuelve, fallback a `'./lib/logger'` o escalation.
   - Modo `--verify`: count console.* calls, exit 0 si == 0.
4. Implementar **`console_to_json_structured.ts`**:
   - Solo aplica si file path matches `supabase/functions/**/*.ts`.
   - Transformación: `console.log(msg)` → `console.log(JSON.stringify({ level: "info", msg }))`.
   - Modo `--verify`: check todos los console.log están wrapped con JSON.stringify({level, ...}).
5. Implementar **`infer_type_from_context.ts`**:
   - AST query: `AsExpression` con type = AnyKeyword.
   - Strategy:
     1. RHS es literal → inferir del literal.
     2. RHS es CallExpression con return type explícito → usar return type.
     3. RHS es PropertyAccess → resolver tipo de la property.
     4. Si no resuelve → exit 1 con razón "inference_failed_for_<node>".
   - Modo `--verify`: count `as any` literals, debe ser <= count pre-fix.
6. Cada script tiene logging estructurado a stderr + summary a stdout.

### Acceptance criteria

**AC-S6-1**: `node codemods/non_null_to_optional.js <test_file.ts>` aplica fix; re-run en `--verify` mode exit 0.

**AC-S6-2**: `node codemods/console_to_logger.js <test_file.ts>` inyecta import si falta + reemplaza calls.

**AC-S6-3**: `node codemods/console_to_json_structured.js <supabase/functions/foo/index.ts>` wraps con JSON.stringify; sobre file fuera de supabase/functions/ → no-op + exit 0.

**AC-S6-4**: `node codemods/infer_type_from_context.js <file.ts>` con literal RHS resuelve; con type unresolvable → exit 1 con razón clara.

**AC-S6-5**: Cada codemod tiene fixture file y test de smoke (corre el script real sobre fixture, verifica diff esperado).

**AC-S6-6**: Mode `--verify` exit codes: 0 si pattern eliminado, 1 si pattern persiste, 2 si script crash (vs error de pattern).

### Tests planeados

`tests/codemods/test_non_null_to_optional.py` (~4 tests, incluye subprocess invoke).
`tests/codemods/test_console_to_logger.py` (~6 tests, incluye alias resolution).
`tests/codemods/test_console_to_json_structured.py` (~4 tests).
`tests/codemods/test_infer_type_from_context.py` (~5 tests, incluye inference failure path).
Total: ~19 tests.

### Definition of done

- [ ] 4 scripts ts-morph funcionales + `--verify` mode.
- [ ] Fixtures + tests de smoke.
- [ ] Conservador: si pattern ambiguo → escalation (no forzar).
- [ ] Tests pasan (≥19 tests).

---

## S-7 — Codemods Python custom (2 scripts)

**Estimación**: M (~1.5 horas).
**Sesión**: 5.
**Dependencias**: S-1.

### Descripción

Implementar los 2 codemods custom en Python: `rename_migration_timestamp.py` (filesystem) y `add_volatile_marker.py` (SQL regex).

### Tareas

1. Implementar **`rename_migration_timestamp.py`**:
   - Detectar files matching `supabase/migrations/0\d{3}_*.sql`.
   - Para cada uno:
     - Extraer timestamp source: mtime (Posix) OR git log primer commit OR UTC actual.
     - Renombrar `0001_initial.sql` → `202605221130_initial.sql` (formato `YYYYMMDDHHmm_<slug>.sql`).
   - DRY-RUN mode obligatorio (`--dry-run`): solo printa mapping, NO renombra.
   - Mantener mapping log en `.sigma-mechanic/migration-renames.log` (para rollback manual si necesario).
   - Modo `--verify`: check todos los files en `supabase/migrations/` matchean regex `^\d{12}_[a-z0-9_-]+\.sql$`.
2. Implementar **`add_volatile_marker.py`**:
   - Regex pattern: `CREATE FUNCTION ... AS $$ ... $$ LANGUAGE plpgsql\s*$` (sin VOLATILE/STABLE/IMMUTABLE).
   - Agregar `VOLATILE` al final.
   - Idempotente: si ya tiene marker, no-op.
   - Modo `--verify`: assertion every CREATE FUNCTION matches `LANGUAGE plpgsql\s+(VOLATILE|STABLE|IMMUTABLE)`.
3. Cada script: argparse con `--verify` + `--dry-run` (donde aplique) + `<file>` positional.

### Acceptance criteria

**AC-S7-1**: `python codemods/rename_migration_timestamp.py supabase/migrations/0001_initial.sql --dry-run` printa mapping sin renombrar.

**AC-S7-2**: Sin `--dry-run`, renombra + escribe log. Re-correr es no-op (file ya tiene timestamp format).

**AC-S7-3**: `python codemods/add_volatile_marker.py file.sql` agrega `VOLATILE` a CREATE FUNCTION sin marker. Idempotente.

**AC-S7-4**: Mode `--verify` para ambos scripts retorna exit 0 si patrón resuelto, 1 si persiste.

**AC-S7-5**: Edge case rename_migration: file ya con formato timestamp `(\d{12})_*.sql` → no-op.

**AC-S7-6**: Edge case add_volatile: function ya con STABLE → respetar, no convertir a VOLATILE.

### Tests planeados

`tests/codemods/test_rename_migration.py` (~6 tests).
`tests/codemods/test_add_volatile.py` (~6 tests).
Total: ~12 tests.

### Definition of done

- [ ] 2 scripts Python funcionales + `--verify` mode.
- [ ] DRY-RUN mode en rename_migration (R-5 reversibilidad).
- [ ] Idempotentes.
- [ ] Edge cases cubiertos (file ya con marker, file con STABLE/IMMUTABLE).
- [ ] Tests pasan (≥12 tests).

---

## S-8 — CLI + M3 empirical measurement

**Estimación**: M (~2 horas).
**Sesión**: 5 (última).
**Dependencias**: S-5 (orchestrator), S-6 + S-7 (codemods invocables).

### Descripción

CLI entry point `sigma-mechanic` que lee findings de stdin, procesa, emite PatchResult[] a stdout. Además: medición empírica M3 sobre fixture sprint1-iteracion3.json filtrado a Tier A (AM8).

### Tareas

1. Implementar `cli.py` con `main(argv) → int`:
   - Parse args: `--rules-path`, `--verify-only` (corre solo verify sin invocar), `--metrics` (emite MM1-MM5 a stderr).
   - Lectura stdin JSON, parse a ClassifiedFinding[].
   - Pre-flight check.
   - Filter tier == "A".
   - Run orchestrator.
   - Emit JSON a stdout, exit code 0 o 1 según fatal error.
2. Entry point `sigma-mechanic` en pyproject.toml.
3. Implementar `test_m3_empirical.py`:
   - Fixture: filtrar findings Tier A de `sprint1-iteracion3.json` (~15 findings).
   - Setup: copiar fixture files a `tmp_path` (no modificar repo real).
   - Run mechanic batch.
   - Medir M3 = `applied / total_tier_a`.
   - Assertion: M3 ≥ 0.5 (no exigir 90% en sandbox de tests; el target real es producción).
   - Reportar a stderr con tabla `rule_id → fix_status` para auditoría manual.
4. Output structured con MM1-MM5 cuando `--metrics`.

### Acceptance criteria

**AC-S8-1**: `echo '[]' | sigma-mechanic` → stdout `[]`, exit 0.

**AC-S8-2**: `echo '<valid_finding>' | sigma-mechanic` → stdout PatchResult[] con 1 entry, exit 0.

**AC-S8-3**: `echo 'invalid_json' | sigma-mechanic` → stderr error claro, exit 1.

**AC-S8-4**: Test M3 empirical corre sobre fixture filtrado, calcula M3, falla si <0.5 (para CI gate; real target ≥0.9 en producción).

**AC-S8-5**: `sigma-mechanic --metrics` emite a stderr tabla con MM1 (cobertura), MM2 (tasa rollback), MM3 (tiempo p95), MM4 (escalación legítima), MM5 (idempotencia stability).

**AC-S8-6**: Test idempotencia (AM7): corre mechanic dos veces consecutivas → segundo run todos `noop_already_clean`.

**AC-S8-7**: Test extensibilidad (AM5): handler ficticio en YAML para rule_id `MOCK-RULE-001` → mechanic invoca el comando mock sin tocar core.

### Tests planeados

`tests/test_cli.py` (~10 tests, incluye stdin parsing + exit codes).
`tests/test_m3_empirical.py` (~3 tests, fixture-based).
`tests/test_idempotency.py` (~5 tests).
`tests/test_extensibility.py` (~5 tests).
Total: ~23 tests.

### Definition of done

- [ ] CLI invocable con stdin/stdout/exit codes correctos.
- [ ] M3 medido empíricamente sobre fixture real.
- [ ] Metrics MM1-MM5 emitibles.
- [ ] Idempotencia + extensibilidad verificadas.
- [ ] Tests pasan (≥23 tests).

---

## ACs del PRD vs cobertura de stories

| AC PRD | Cubierto por story(es) |
|--------|------------------------|
| AM1 — Cobertura 15/15 | S-1 (YAML 15 entries) + S-5 (process_finding) + S-6+S-7 (codemods) + S-8 (M3 measurement) |
| AM2 — Verificación post-fix | S-4 (verifier) + S-5 (lookup en orchestrator) |
| AM3 — Rollback automático | S-3 (snapshot) + S-5 (rollback en flow case 3a/3b) |
| AM4 — Performance <60s batch 30 | S-5 (batch loop) + S-8 (perf test fixture) |
| AM5 — Extensibilidad | S-1 (YAML declarativo) + S-8 (test_extensibility.py) |
| AM6 — Output JSON estructurado | S-1 (models) + S-8 (CLI emit) |
| AM7 — Idempotencia | S-3 (unchanged()) + S-5 (caso 3d noop) + S-8 (test_idempotency) |
| AM8 — M3 medible | S-8 (test_m3_empirical) |
| AM9 — Pre-flight check | S-2 (preflight.py) |

**Cobertura total**: 9/9 ACs del PRD tienen al menos una story que los implementa. Sin gaps.

---

## Plan de ejecución secuencial

**Sprint 3 sesión 4** (~8.5 hs):
1. S-1 Foundation (2hs) → 14:00-16:00
2. S-2 Pre-flight + Invoker (1.5hs) → 16:00-17:30
3. S-3 Snapshot (1hs) → 17:30-18:30
4. S-4 Verifier (2hs) → 18:30-20:30
5. S-5 Orchestrator (2hs) → 20:30-22:30
6. Commit + push parcial: "feat(framework): auto-fix-mechanic S-1..S-5 (core, ~60 tests)"

**Sprint 3 sesión 5** (~7.5 hs):
1. S-6 Codemods ts-morph (4hs) → 14:00-18:00
2. S-7 Codemods Python (1.5hs) → 18:00-19:30
3. S-8 CLI + M3 (2hs) → 19:30-21:30
4. Audit Paso 7 (G1-G33 + FG1-FG14 + SOLID + zero-trust) + Audit Paso 8 (adversariales) (1-2hs adicional o sesión 6)
5. Commit + push final: "feat(framework): auto-fix-mechanic S-6..S-8 + Paso 7 audit + Paso 8 adv (~115 tests, M3 medido)"

---

## Riesgos del plan

| Riesgo | Mitigación |
|--------|-----------|
| S-6 (ts-morph custom) toma más de 4hs | Dividir en S-6a (2 codemods simples: non_null + console_to_logger) y S-6b (2 codemods complejos: console_to_json + infer_type). Permite parar Sprint 3 sesión 5 con S-6a + S-7 + S-8 stub. |
| ts-morph requiere config TS específico del proyecto target | Codemods deben aceptar `tsconfig.json` path como arg. Test fallback: si no hay tsconfig → escalation. |
| Lock por archivo (filelock) requiere lib externa no instalada | Fallback a `fcntl` (Posix) / `msvcrt` (Windows) stdlib. Si tampoco disponible, lock no-op + warning (degradación graceful). |
| M3 empirical <0.5 sobre fixture (test S-8 falla) | Reportar gaps + iterar handlers o re-clasificar rule_id en classifier. NO bajar threshold del test artificialmente. |
| Pre-flight check rechaza el environment del operador | Mensaje claro + quickstart con install steps. Operador puede correr en sandbox con npm install local. |

---

## Lecciones candidatas a observar durante el build

- **L39 candidata (esperaría N=1 al cerrar sesión 4 o 5)**: *"snapshot in-memory + rollback atómico es overkill para batches pequeños; vale la pena solo cuando batch >5 findings"*. Observable: medir tiempo extra de snapshot vs no-snapshot en S-3 tests.
- **L40 candidata (esperaría N=1)**: *"verificación post-fix con re-run del mismo tool detecta 90%+ de regresiones; el 10% restante requiere test focalizado"*. Observable: tasa de regresión detectada por re-run vs por tests adicionales.

Ambas se documentarían en `architecture/LECCIONES.md` o `auditoria/sesion-activa.md` según N.

---

**Próximo paso (Paso 5 del protocolo)**: auditar este plan completo (PRD + dominio + arquitectura + stories) con validadores R01-R15. Output: `auditoria/audit-plan-auto-fix-mechanic-2026-05-22.json`.
