# Arquitectura técnica — `sigma:auto-fix-mechanic`

**Status**: DRAFT v0.1
**Date**: 2026-05-22 (Sprint 3 sesión 3 — Paso 3 del PROTOCOLO-CONSTRUCCION-CODIGO)
**Related**: PRD-sigma-auto-fix-mechanic.md, auto-fix-mechanic-rules.yaml.draft, codemod-toolbox.md, ADR-011 PROPOSED v0.9 PARTIAL, ARQUITECTURA-sigma-finding-classifier.md (referencia de patrón), architecture/PRINCIPIOS-ARQUITECTURA.md (A1-A25)
**Principios rectores aplicables**: 1° (Python verifica), 2° (3 capas — capa correctiva), 4° (Auto-fix > finding cuando inequívoco), A20 (Hexagonal)

---

## 1. Visión general

El mechanic es un **orquestador Python determinístico** que toma findings clasificados como Tier A por el classifier, invoca codemods externos según `auto-fix-mechanic-rules.yaml`, verifica post-fix con re-check determinístico, y emite patch atómico con resultado verificable. Si la verificación falla, hace rollback atómico del archivo y escala a Tier C — NUNCA silencia el error.

```
                ┌─────────────────────────────────────────────────────────┐
                │            CAPA VERIFICABLE (Phase 1+upstream)          │
                │  GGA con scope-aware → Finding[] text                   │
                └────────────────────────┬────────────────────────────────┘
                                         │ (normalizer adapter)
                                         ▼
                ┌─────────────────────────────────────────────────────────┐
                │      sigma:finding_classifier (✅ operativo v0.1.0)      │
                │      output: ClassifiedFinding[] con tier + action_hint  │
                └────────────────────────┬────────────────────────────────┘
                                         │
                          filter by tier == "A"
                                         │
                                         ▼
                ┌─────────────────────────────────────────────────────────┐
                │       sigma:auto_fix_mechanic (ESTE PRD)                │
                │   - Python 3.10+ orquestador                            │
                │   - Carga auto-fix-mechanic-rules.yaml                  │
                │   - Pre-flight check toolbox (eslint, prettier, etc.)   │
                │   - Por cada Finding Tier A:                            │
                │     1. Lookup handler → tool + invocation               │
                │     2. Snapshot file pre-fix (para rollback)            │
                │     3. Invoke tool via subprocess                       │
                │     4. Verify post-fix (re-check pattern)               │
                │     5. Si verify FAIL → rollback + escalate to Tier C   │
                │     6. Si verify OK → mark applied                      │
                │   - Output JSON: PatchResult[]                          │
                └────────────────────────┬────────────────────────────────┘
                                         │
                              PatchResult[] (stdout)
                                         ▼
                ┌─────────────────────────────────────────────────────────┐
                │           Downstream: Tier B / Tier C handlers          │
                │   Reciben escalaciones (verification_failed,            │
                │     rollback_due_to_regression, handler_not_implemented)│
                └─────────────────────────────────────────────────────────┘
```

---

## 2. DECISIÓN ARQUITECTÓNICA CLAVE — Wrapper sigma propio (NO wholesale ECC)

**Decisión**: construir el mechanic como **wrapper Python sigma propio** que orquesta tools externos directos (ESLint, Prettier, ts-morph scripts, Python scripts custom). **NO** componer wholesale sobre ECC `build-fix` ni `refactor-clean`.

**Trade-off central**: composición lateral con ECC permitida (operador puede invocar ECC por su cuenta para casos fuera del scope del classifier), pero ECC NO es backend del Tier A del mechanic.

### 2.1 Evidencia que soporta la decisión

Documentada en detalle en `docs/dominio/codemod-toolbox.md` sección 3. Resumen:

| Criterio | ECC build-fix + refactor-clean | Wrapper sigma propio (ESLint + Prettier + ts-morph + Python custom) |
|----------|--------------------------------|------------------------------------------------------------------------|
| Cobertura directa de los 15 rule_ids Tier A | **0/15** (parcial 3/15 si rule causa build error) | **15/15** |
| Determinístico (sin LLM en path de fix) | ❌ ECC build-fix es sub-agent LLM | ✅ Todos los tools son determinísticos |
| Idempotencia garantizada (AM7) | ❌ LLM reasoning puede variar | ✅ Mismo input → mismo output |
| Verificación post-fix automatizable | ❌ Sub-agent retorna texto, no AST check | ✅ Cada tool soporta re-run en modo check |
| Conoce rule_ids específicos del Framework | ❌ No (A21-OBS-1, MIGRATION-NAMING, etc. son del Framework) | ✅ Mapeo declarativo en YAML |
| Granularidad apropiada | ❌ Nivel "fix build error", no rule-by-rule | ✅ 1 rule_id → 1 handler → 1 tool |
| Visión C respetada (curator > constructor) | 🟡 reutiliza ECC pero ECC no cubre el dominio | ✅ compone sobre stack TS estándar + minimal custom |
| Constraint C1 PRD (sin LLM en path) | ❌ Viola | ✅ Cumple |

### 2.2 Alternativas rechazadas

#### Alternativa A — Wholesale ECC `build-fix` como backend del Tier A
**Rechazada porque**: 0/15 cobertura directa de rule_ids Framework. Usa LLM (viola C1). No determinístico (viola AM7). ECC build-fix está diseñado para "fix this build error" no para "apply codemod X to rule_id Y". Granularidad incorrecta.

#### Alternativa B — Wholesale ECC `refactor-clean` para UNUSED-IMPORT + delegación parcial
**Rechazada porque**: solo 1/15 cobertura parcial (UNUSED-IMPORT como dead code). Costo de wiring + verificación post-fix custom > beneficio. Eslint con `unused-imports` plugin es más directo y determinístico.

#### Alternativa C — Construir codemods desde cero en Python sin tools externos
**Rechazada porque**: viola Visión C. ESLint y Prettier cubren 10/15 rule_ids con cero código del Framework. Reinventarlos sería over-engineering masivo y peor calidad que tools maduros del ecosystem TS.

#### Alternativa D — Sub-agent LLM acotado para Tier A (en lugar de codemods determinísticos)
**Rechazada porque**: viola 4° principio rector ("auto-fix > finding cuando inequívoco"). Si es inequívoco, codemod determinístico funciona. Si requiere reasoning, es Tier B (sub-agente acotado) por definición. Confundir Tier A con LLM borra la distinción del ADR-011.

#### Alternativa E — Esperar a Sprint 5+ para construir auto-fix-mechanic
**Rechazada porque**: bloquea promoción ADR-011 a v1.0 ACCEPTED indefinidamente. M3 no es medible sin mechanic. La trinidad no compone sin Tier A funcional. Decidido en BLOQUE 2 sesión 3 que el costo de 1-2 sesiones de build es proporcionado al valor de cerrar la trinidad mínima.

### 2.3 Consecuencias de la decisión

**Positivas**:
- Cumple los 7 principios rectores sin tensión (1° determinístico, 2° materializa correctiva, 4° operacionaliza auto-fix, etc.).
- Mantiene boundary chico (A20 hexagonal): mechanic no depende de ECC ni de ningún sub-agent.
- Cobertura 15/15 desde día 1 (AM1 cumplible directamente).
- Idempotencia trivial (AM7).
- Verificación post-fix por re-run del mismo tool en modo check.

**Negativas / Costos**:
- 4 codemods ts-morph custom (~50-80 LOC c/u) + 2 scripts Python custom (~30-50 LOC c/u) = ~250-450 LOC de codemod code propio del Framework.
- Mantenimiento: si rule_id cambia de patrón (ej. tsconfig nuevo), codemod custom debe actualizarse.
- Dependencia runtime: el environment del operador (o CI) debe tener Node + ESLint + Prettier + ts-morph + Python. Mitigado por pre-flight check (AM9).

**Riesgos** (cubiertos en sección 13):
- Codemod custom con bug → AM3 rollback + escalación a C.
- Tool externo cambia comportamiento → smoke test al boot detecta.

### 2.4 ECC sigue siendo útil — composición lateral

Esta decisión NO descarta ECC. ECC `build-fix` y `refactor-clean` siguen siendo útiles para:

- **Build errors fuera del scope del classifier**: el operador invoca ECC directamente cuando aparece un error que NO es Tier A (ej. error de compilación por dependency cycle no clasificado). Composición lateral, NO wholesale por el mechanic.
- **Dead code consolidation**: ECC `refactor-clean` puede correr periódicamente como tarea separada (no en el path del commit).

El mechanic y ECC quedan como **herramientas complementarias** del operador, no acopladas.

---

## 3. Composición upstream con el classifier

El mechanic consume directamente la salida del classifier (✅ operativo v0.1.0).

```
classifier output (stdout JSON):
  ClassifiedFinding[] = [{
    finding: {rule_id, file, line, severity, message, source, raw?},
    tier: "A" | "B" | "C",
    action_hint: "eslint-fix" | "console-to-logger" | ...,
    matched_rule: bool
  }, ...]

  |
  v

mechanic input (stdin JSON):
  filter: tier == "A"
  for each Finding A:
    handler = handlers_yaml[finding.rule_id]
    if handler is None:
      emit PatchResult{fix_status: "escalated_to_c", reason: "handler_not_implemented"}
      continue
    snapshot file (for rollback)
    invoke handler.tool with handler.invocation on finding.file
    verify(handler.verification, finding.file)
    if verify OK:
      emit PatchResult{fix_status: "applied", patch_summary, verification: "passed"}
    elif verify FAIL:
      rollback file
      emit PatchResult{fix_status: "rolled_back", verification: "failed", rollback_reason}

mechanic output (stdout JSON):
  PatchResult[]
```

**Beneficio del acoplamiento débil**: el mechanic NO conoce GGA ni a otros reviewers. Solo conoce el formato `ClassifiedFinding`. Si en Sprint 4+ aparece otro classifier (ej. `sigma:finding_classifier_v2` con ML), el mechanic sigue funcionando sin cambios. A20 hexagonal preservado.

---

## 4. Modelo de datos

### 4.1 Tipos públicos (contrato externo)

```python
from dataclasses import dataclass, field
from typing import Literal, Optional
from enum import Enum

FixStatus = Literal[
    "applied",                    # Fix aplicado y verificado
    "rolled_back",                # Fix se intentó pero verification falló → rollback + escalation
    "escalated_to_c",             # Handler no existe O optional tool unavailable → escalation directa
    "noop_already_clean",         # Idempotencia: patrón no estaba presente al arrancar (segundo run)
]

VerificationResult = Literal["passed", "failed", "not_attempted"]

@dataclass(frozen=True)
class PatchResult:
    """Output del mechanic, uno por finding procesado."""
    rule_id: str
    file: str
    line: int
    action_hint: str
    fix_status: FixStatus
    verification: VerificationResult
    patch_summary: Optional[str] = None    # Diff hash o resumen breve
    rollback_reason: Optional[str] = None  # Si fix_status == "rolled_back"
    escalation_reason: Optional[str] = None  # Si fix_status == "escalated_to_c"
    tool_used: Optional[str] = None         # ej. "eslint", "ts-morph:console_to_logger"
    elapsed_ms: int = 0
```

### 4.2 Tipos internos (privados)

```python
@dataclass(frozen=True)
class Handler:
    """Una entrada del auto-fix-mechanic-rules.yaml."""
    rule_id: str
    tool: Literal["eslint", "prettier", "ts-morph-custom", "python-custom-script"]
    invocation: Optional[str] = None      # CLI invocation template (eslint, prettier)
    codemod_script: Optional[str] = None  # Path a script (ts-morph, python)
    pattern_target: str = ""
    transformation: str = ""
    verification: dict = field(default_factory=dict)
    rollback_strategy: str = "file-level-revert"
    notes: Optional[str] = None
    optional_tool_unavailable: bool = False  # Set at boot if pre-flight check failed

@dataclass(frozen=True)
class ToolboxStatus:
    """Resultado del pre-flight check."""
    required_tools_ok: bool
    missing_required: list[str]
    optional_tools_ok: bool
    missing_optional: list[str]
    disabled_handlers: list[str]  # rule_ids whose optional tool is missing
```

### 4.3 Esquema YAML (resumen, completo en auto-fix-mechanic-rules.yaml.draft)

```yaml
version: "0.1.0"
metadata: { ... }
handlers:
  TS-1:
    tool: eslint
    invocation: "npx eslint --fix --rule '{prefer-const: error, ...}' <file>"
    pattern_target: "..."
    verification:
      method: re-run-eslint
      command: "..."
      expected_exit_code: 0
    rollback_strategy: file-level-revert
  # ... 14 more handlers
defaults:
  missing_handler_action: escalate_to_tier_c
preflight:
  required_tools: [...]
  optional_tools: [...]
```

---

## 5. Componentes principales

```
framework/sigma/auto_fix_mechanic/
├── __init__.py                 # Public API: run_mechanic(findings) → PatchResult[]
├── pyproject.toml              # Python package metadata (compatible con classifier setup)
├── models.py                   # Dataclasses (PatchResult, Handler, ToolboxStatus)
├── loader.py                   # Load + validate auto-fix-mechanic-rules.yaml
├── preflight.py                # Pre-flight check del toolbox (AM9)
├── orchestrator.py             # Main loop: per finding → snapshot → invoke → verify → emit
├── snapshot.py                 # File snapshot + restore para rollback atómico (R-5)
├── verifier.py                 # Dispatch por verification.method (re-run-eslint, ast-check, etc.)
├── invoker.py                  # subprocess wrapper con timeout + capture + error handling
├── cli.py                      # CLI entry point (stdin findings, stdout PatchResult[])
├── codemods/
│   ├── README.md               # Docs de los codemods custom (Framework-specific)
│   ├── non_null_to_optional.ts          # ts-morph custom
│   ├── console_to_logger.ts             # ts-morph custom
│   ├── console_to_json_structured.ts    # ts-morph custom
│   ├── infer_type_from_context.ts       # ts-morph custom
│   ├── rename_migration_timestamp.py    # Python custom
│   └── add_volatile_marker.py           # Python custom
├── rules.yaml                  # Productive (copia de auto-fix-mechanic-rules.yaml.draft promoted)
└── tests/
    ├── __init__.py
    ├── test_loader.py
    ├── test_orchestrator.py
    ├── test_snapshot.py
    ├── test_verifier.py
    ├── test_invoker.py
    ├── test_cli.py
    ├── test_idempotency.py            # AM7
    ├── test_rollback.py               # AM3
    ├── test_preflight.py              # AM9
    ├── test_extensibility.py          # AM5
    ├── test_m3_empirical.py           # AM8 (fixture-based)
    ├── test_adversarial.py            # Paso 8 PROTOCOLO
    └── fixtures/
        ├── tier_a_findings_sample.json     # Input fixture
        └── target_files/                   # .ts/.sql files con patrones a fixear
```

**Conteo aproximado**:
- Production Python: ~600-800 LOC (orquestador + verifier + invoker + snapshot + loader + preflight + cli + models)
- Codemods custom (.ts + .py): ~250-450 LOC
- Tests: ~1200-1500 LOC (ratio ~2:1 vs prod, similar al classifier 2.5:1)

---

## 6. Flujo de ejecución detallado

### 6.1 Boot

```python
def main(argv: list[str]) -> int:
    # 1. Parse args + load stdin
    args = parse_args(argv)
    findings_json = sys.stdin.read()
    findings = parse_classified_findings(findings_json)

    # 2. Load YAML + validate
    handlers = load_handlers(args.rules_path or default_rules_path())

    # 3. Pre-flight check toolbox (AM9)
    toolbox_status = run_preflight_check(handlers)
    if not toolbox_status.required_tools_ok:
        print_required_missing_error(toolbox_status.missing_required)
        return 1
    if not toolbox_status.optional_tools_ok:
        # Disable handlers whose tool is missing
        for rule_id in toolbox_status.disabled_handlers:
            handlers[rule_id].optional_tool_unavailable = True

    # 4. Filter findings to tier A
    tier_a_findings = [f for f in findings if f.tier == "A"]

    # 5. Run orchestrator
    results: list[PatchResult] = []
    for finding in tier_a_findings:
        result = process_finding(finding, handlers)
        results.append(result)

    # 6. Emit output
    print(json.dumps([asdict(r) for r in results], indent=2))
    return 0
```

### 6.2 Por finding (process_finding)

```python
def process_finding(finding: ClassifiedFinding, handlers: dict[str, Handler]) -> PatchResult:
    start_ms = time.monotonic_ns() // 1_000_000
    handler = handlers.get(finding.rule_id)

    # Caso 1: handler no implementado
    if handler is None:
        return PatchResult(
            rule_id=finding.rule_id, file=finding.file, line=finding.line,
            action_hint=finding.action_hint or "",
            fix_status="escalated_to_c",
            verification="not_attempted",
            escalation_reason="handler_not_implemented",
        )

    # Caso 2: optional tool unavailable
    if handler.optional_tool_unavailable:
        return PatchResult(
            rule_id=finding.rule_id, file=finding.file, line=finding.line,
            action_hint=finding.action_hint or "", tool_used=handler.tool,
            fix_status="escalated_to_c",
            verification="not_attempted",
            escalation_reason=f"optional_tool_unavailable:{handler.tool}",
        )

    # Caso 3: snapshot + invoke + verify + (rollback OR commit)
    with file_snapshot(finding.file) as snapshot:
        invoke_result = invoke_tool(handler, finding.file)
        if invoke_result.exit_code != 0 and invoke_result.exit_code != "noop":
            # Tool falló durante invocación (no es failed verification, es tool crash)
            snapshot.restore()  # AM3: rollback atómico
            return PatchResult(
                rule_id=finding.rule_id, file=finding.file, line=finding.line,
                action_hint=finding.action_hint or "", tool_used=handler.tool,
                fix_status="rolled_back",
                verification="failed",
                rollback_reason=f"tool_invocation_failed:{invoke_result.stderr[:200]}",
                elapsed_ms=elapsed(start_ms),
            )

        # Verificar post-fix
        verify_result = run_verification(handler.verification, finding.file)
        if verify_result.passed:
            # AM7 idempotencia: si el fix no cambió nada (porque ya estaba clean), marcar noop
            if snapshot.unchanged():
                return PatchResult(
                    rule_id=finding.rule_id, file=finding.file, line=finding.line,
                    action_hint=finding.action_hint or "", tool_used=handler.tool,
                    fix_status="noop_already_clean",
                    verification="passed",
                    elapsed_ms=elapsed(start_ms),
                )
            return PatchResult(
                rule_id=finding.rule_id, file=finding.file, line=finding.line,
                action_hint=finding.action_hint or "", tool_used=handler.tool,
                fix_status="applied",
                verification="passed",
                patch_summary=snapshot.diff_summary(),
                elapsed_ms=elapsed(start_ms),
            )
        else:
            snapshot.restore()
            return PatchResult(
                rule_id=finding.rule_id, file=finding.file, line=finding.line,
                action_hint=finding.action_hint or "", tool_used=handler.tool,
                fix_status="rolled_back",
                verification="failed",
                rollback_reason=f"post_fix_verification_failed:{verify_result.detail[:200]}",
                elapsed_ms=elapsed(start_ms),
            )
```

### 6.3 Snapshot atómico (R-5 reversibilidad)

```python
class FileSnapshot:
    def __init__(self, path: Path):
        self.path = path
        self.original_content = path.read_bytes()
        self.original_mtime = path.stat().st_mtime
        self._restored = False

    def restore(self) -> None:
        if not self._restored:
            self.path.write_bytes(self.original_content)
            self._restored = True

    def unchanged(self) -> bool:
        return self.path.read_bytes() == self.original_content

    def diff_summary(self) -> str:
        # Hash del diff o conteo simple de líneas cambiadas
        return f"sha256:{hashlib.sha256(self.original_content).hexdigest()[:8]} → sha256:{hashlib.sha256(self.path.read_bytes()).hexdigest()[:8]}"

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        # Si hay excepción no controlada, rollback por seguridad
        if exc_type is not None and not self._restored:
            self.restore()
        return False  # NO suppress exception
```

---

## 7. Estructura de la verificación post-fix

Dispatcher por `verification.method`:

| Method | Implementación | Casos de uso |
|--------|----------------|--------------|
| `re-run-eslint` | `subprocess.run([npx, eslint, --quiet, --rule, ..., file])` y check exit_code | 8 rule_ids ESLint |
| `re-run-prettier-check` | `subprocess.run([npx, prettier, --check, file])` y check exit_code | 2-3 rule_ids Prettier |
| `ast-check` | Invoca el codemod script en modo `--verify`; cuenta pattern AST | 4 rule_ids ts-morph |
| `filename-regex` | Glob + regex match sobre filenames del directory | 1 rule_id (MIGRATION-NAMING) |
| `regex-grep` | `re.findall(pattern, file_content)` + assertion | 1 rule_id (PGSQL-MISSING-VOLATILE) |

Cada método retorna `VerifyResult(passed: bool, detail: str)`.

---

## 8. Composición downstream — escalation a Tier B/C

Cuando el mechanic emite `fix_status: rolled_back` o `escalated_to_c`, el integrator (hook scope-aware) toma esos PatchResults y los pasa al handler downstream apropiado:

```
mechanic stdout: PatchResult[]
                       │
                       ▼
┌──────────────────────────────────────────────────────────────┐
│       integrator (pre-commit hook o pipeline)                 │
│  - PatchResults con fix_status="applied" → git add + report   │
│  - PatchResults con fix_status="rolled_back" → forward to     │
│    sigma:correction-agent-bounded (Tier B, Sprint 4)          │
│  - PatchResults con fix_status="escalated_to_c" → forward to  │
│    sigma:correction-adr-draft (Tier C, Sprint 4)              │
└──────────────────────────────────────────────────────────────┘
```

**Importante**: el mechanic NO conoce los handlers Tier B/C. Solo emite resultado estructurado. Los handlers downstream son responsabilidad de Sprint 4. Este Sprint 3 sesión 4 (build del mechanic) entrega CLI invocable + tests que validan que el output es correcto para que Sprint 4 pueda consumirlo sin cambios.

---

## 9. Tests planeados

| Categoría | Tests | Cobertura AC |
|-----------|-------|--------------|
| Loader / models | test_loader.py (~10 tests) | C2, C9 |
| Pre-flight check | test_preflight.py (~6 tests) | AM9 |
| Orchestrator | test_orchestrator.py (~15 tests) | AM1, AM6 |
| Snapshot/rollback | test_snapshot.py (~10 tests) | AM3, C5, R-5 |
| Verifier | test_verifier.py (~12 tests) | AM2 |
| Invoker | test_invoker.py (~8 tests) | C2 (subprocess wrapper) |
| CLI | test_cli.py (~10 tests) | AM6, AM8 |
| Idempotencia | test_idempotency.py (~5 tests) | AM7 |
| Extensibilidad | test_extensibility.py (~5 tests) | AM5 |
| M3 empirical (fixture) | test_m3_empirical.py (~3 tests) | AM8 |
| Adversariales | test_adversarial.py (~15 tests) | Paso 8 PROTOCOLO |

**Total proyectado**: ~100 tests. Ratio tests:prod proyectado ~2:1 (consistente con classifier 2.5:1).

### 9.1 Tests adversariales obligatorios (Paso 8 PROTOCOLO)

Categorías mínimas:

1. **Inputs vacíos**: empty findings array → exit 0 + `[]` stdout.
2. **Inputs malformados**: invalid JSON, missing required fields → exit 1 + error claro.
3. **Findings con rule_id desconocido**: handler no existe → `escalated_to_c` sin crash.
4. **Codemod script crash** (mock): exit code != 0 → rollback + escalation.
5. **Verification crash** (mock): verifier lanza excepción → rollback por seguridad + escalation.
6. **File no existe**: handler intenta abrir file inexistente → rollback (snapshot lo previene) + escalation.
7. **File con permisos read-only**: invocación falla → rollback + escalation.
8. **Tool externo NO instalado runtime**: handler invoca eslint no presente → escalation con `tool_unavailable_runtime`.
9. **Race condition**: dos invocaciones paralelas sobre mismo file → segunda espera por lock o falla con clarity.
10. **Patch summary corrupto** (mock hash collision): output JSON sigue siendo válido.
11. **Tamaño masivo**: batch de 1000 findings → no leak de memoria + tiempo razonable.
12. **Verification timeout**: re-run del tool toma >30s → kill + escalation.
13. **Idempotencia adversarial**: invocar el mechanic 3 veces consecutivas → segunda y tercera son `noop_already_clean`.
14. **Rollback durante rollback** (snapshot.restore() falla): error claro + working tree warning.
15. **YAML malformado**: handlers.yaml inválido → exit 1 + linter del YAML.

---

## 10. Performance considerations

### 10.1 Bottlenecks esperados

- **Tools externos (ESLint, Prettier)**: ~200-500ms cada invocación (carga de config + parse). Mitigar: si batch tiene 8 findings ESLint sobre el mismo archivo, invocar ESLint UNA vez con todas las rules. AM4 lo contempla.
- **ts-morph init**: el `Project` de ts-morph carga el TS config. Mitigar: codemod script lo carga una vez per script run.
- **Subprocess fork**: cada invocación tiene overhead ~50ms en Windows. Mitigar: batch por tool donde aplique.

### 10.2 Estrategia de paralelismo

- **Por defecto secuencial**: predictibilidad + simplicidad de rollback. Single-threaded.
- **Paralelismo opcional** (Sprint 5+): `--workers N` flag para invocar handlers en paralelo cuando los findings son sobre archivos distintos. Requiere lock por archivo para safety.

### 10.3 Target AM4 (30 findings en <60s)

Cálculo grueso:
- 8 ESLint findings agrupados: 1 invocación batch (~500ms) + 8 verifications individuales (8 × 200ms = 1.6s) = ~2.1s
- 2 Prettier findings: 1 batch (~300ms) + 2 verify (~400ms) = ~0.7s
- 4 ts-morph findings: 4 scripts (4 × 800ms = 3.2s) + 4 verify (~1.6s) = ~4.8s
- 2 Python custom: 2 scripts (~400ms) + 2 verify (~200ms) = ~0.6s
- 14 idem alguno: noop fast (~50ms × 14 = 0.7s)
- Subtotal: ~9s para 30 findings → 6x bajo el target de 60s. Margen amplio.

---

## 11. Decisiones de diseño con tradeoffs

| Decisión | Alternativa rechazada | Razón |
|----------|----------------------|-------|
| Snapshot in-memory (bytes) | Snapshot a archivo temp en .sigma-mechanic/ | Memory es más rápido + no genera archivos huérfanos. Files grandes (>10MB) son excepcionales en Tier A. |
| Verificación re-run del mismo tool | AST check propio del Framework | Re-run garantiza paridad semántica con la herramienta original. Custom AST check es brittle. |
| Subprocess sync (no async) | asyncio + subprocess.create_subprocess_exec | Simplicidad > performance marginal. Paralelismo via `--workers` en Sprint 5. |
| YAML como single source of truth | Decorators Python por handler | YAML es versionable + readable por non-developers + mismo patrón que classifier (C2). |
| Default missing_handler_action = escalate_to_c | Default missing_handler_action = no-op silent | NUNCA silenciar. Escalación visible para curación (MM4 metric). |
| File-level revert (overwrite bytes) | git stash + git checkout | No depende de git (mechanic puede invocarse sin git context). Más simple. |
| Tools externos via npx | Path absoluto a ejecutables | npx resuelve versión del proyecto target (semver pinned en package.json). Más portable. |
| Codemods custom en `codemods/` adjacent | Repo separado | Mantenimiento conjunto. Versionables con el resto del mechanic. Si crecen >10 codemods, splitear. |

---

## 12. Conexión con clases A* del Framework (architecture/PRINCIPIOS-ARQUITECTURA.md)

| A-rule | Cómo el mechanic la respeta |
|--------|------------------------------|
| **A1 Single Responsibility** | Cada handler es responsable de UN rule_id. Cada script de codemod hace UNA transformación. |
| **A4 Acíclicidad** | Mechanic depende del classifier. Classifier NO depende del mechanic. Sin ciclos. |
| **A12 Zero Trust** | NO confía en el tool externo: verificación post-fix obligatoria (AM2). |
| **A18 Explicit Failure** | Tres modos de failure explícitos: `escalated_to_c`, `rolled_back`, exit code 1. NO silencia. |
| **A20 Hexagonal** | Boundary chico: input `Finding[]`, output `PatchResult[]`. Adapters (subprocess, snapshot) en módulos separados. |
| **A21 Structured Observability** | Output JSON estructurado. Errores con razón clara. Métricas MM1-MM5 emitibles. |
| **A22 Secrets Management** | NO maneja secrets. Pre-flight check para fail-fast on env issues. |
| **A23 Deployment Safety** | Snapshot + rollback atómico = R-5 reversibilidad. NO deja estado parcial. |
| **A24 Data Lifecycle** | Snapshot in-memory ephemeral. NO persiste data sensible. |

---

## 13. Riesgos estructurales (extensión del PRD sección 10)

| Riesgo arquitectónico | Severidad | Mitigación |
|------------------------|-----------|------------|
| Snapshot in-memory falla para archivos muy grandes (>100MB) | Baja | Pre-check tamaño antes de snapshot; si >X MB → escalation con razón "file_too_large_for_safe_snapshot". |
| Subprocess deadlock por stdin/stdout buffer lleno | Media | Usar `subprocess.run(..., capture_output=True, timeout=30)` con explicit timeout. Test adversarial 12. |
| Codemod ts-morph custom crashea por TS config malformado | Media | Codemod debe validar `tsconfig.json` exista; si no, escalation con razón. Test adversarial 6. |
| YAML schema drift (nuevo campo no manejado) | Baja | Validación con `pydantic` o `dataclasses-json` al load. Test test_loader.py. |
| Race condition entre dos invocaciones del mechanic | Media | Lock por archivo (`filelock` library). Documentar en quickstart. |
| Tool externo (eslint) actualiza y cambia formato de output | Media | Smoke test del toolbox al boot (sin modificar archivos reales). Detect drift early. |
| Python 3.13+ rompe alguna API que usamos | Baja | Pin Python 3.10-3.13 en pyproject.toml. CI matrix. |

---

## 14. Conexión con principios rectores

| Principio | Cómo la arquitectura del mechanic lo encarna |
|-----------|----------------------------------------------|
| **1° (Python verifica)** | Mechanic Python puro. Tools externos también determinísticos. Verificación post-fix obligatoria. Cero LLM en el path. |
| **2° (3 capas)** | **MATERIALIZA la capa CORRECTIVA**. Sin esta arquitectura, la trinidad no compone — classifier solo etiqueta, no fixea. |
| **3° (Dominio-first)** | Toda la arquitectura referencia el dominio capturado en Paso 2 (auto-fix-mechanic-rules.yaml + codemod-toolbox.md). NO especulación sobre rule_ids. |
| **4° (Auto-fix > finding cuando inequívoco)** | **OPERACIONALIZA el principio**. Inequívoco = Tier A clasificado + handler verificable. Si verificación falla, escala (NO fuerza). |
| **5° (Polinización cruzada)** | Patrón snapshot + verify + rollback es replicable al Tier B handler (Sprint 4) con sub-agente LLM en lugar de codemod. Patrón estructural propagable. |
| **6° (Descubrir antes de ejecutar)** | Pre-flight check toolbox + verify post-fix. Sección 2 de este doc documenta evidencia ECC vs wrapper sigma antes de decidir. NO asume. |
| **7° (Meta-producto recursivo)** | Los codemods custom del Framework son auto-aplicables si GGA encuentra esos patterns en código sigma. El mechanic se aplica a sí mismo. |

---

## 15. Próximo paso (Paso 4 del protocolo)

Descomponer en stories ejecutables S-1..S-n con acceptance criteria explícitos, dependencias declaradas, estimación de complejidad. Output: `docs/stories/STORIES-sigma-auto-fix-mechanic.md`.

Patrón a seguir (precedente classifier): 7-8 stories totalizando 10-15hs, distribuidas en 1-2 sesiones de build (Sprint 3 sesiones 4-5).

---

**Esta arquitectura es prerrequisito de**: Paso 4 (stories), Paso 5 (audit R01-R15), Paso 6+ (build Sprint 3 sesión 4+).
**Esta arquitectura supersede**: la frase "Phase 2.1 evalúa empíricamente" del ADR-011 (la evaluación se resolvió acá con la evidencia del Paso 2).
