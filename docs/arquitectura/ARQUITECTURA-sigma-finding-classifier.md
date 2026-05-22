# Arquitectura técnica — `sigma:finding-classifier`

**Status**: DRAFT v0.1
**Date**: 2026-05-21 (Sprint 2 sesión 2 — Paso 3 del PROTOCOLO-CONSTRUCCION-CODIGO)
**Related**: PRD-sigma-finding-classifier.md, findings-taxonomy.md, ADR-011 PROPOSED v0.5 PARTIAL, architecture/PRINCIPIOS-ARQUITECTURA.md (A1-A25)
**Principios rectores aplicables**: 1° (Python verifica), 2° (3 capas), A20 (Hexagonal)

---

## 1. Visión general

El classifier es un **componente Python determinístico** que se inserta como **front-end de la capa correctiva** del Framework. Toma findings normalizados de cualquier reviewer y los etiqueta con tier (A/B/C) según reglas declarativas.

```
                ┌─────────────────────────────────────────────────────────┐
                │                  CAPA VERIFICABLE                       │
                │  ┌──────┐    ┌──────┐    ┌────────┐                     │
                │  │ GGA  │    │ R/G/ │    │ Otros  │  ← reviewers       │
                │  │      │    │  FG  │    │        │     emiten findings │
                │  └──┬───┘    └──┬───┘    └────┬───┘                     │
                └─────┼───────────┼─────────────┼───────────────────────-─┘
                      │           │             │
                      │   stdout / formato específico
                      │           │             │
                      ▼           ▼             ▼
                ┌─────────────────────────────────────────────────────────┐
                │              ADAPTER / NORMALIZER                        │
                │   (provider-specific → Finding[] estándar)               │
                │   Responsabilidad del integrador (hook o pipeline)       │
                └────────────────────────┬────────────────────────────────┘
                                         │
                                Finding[] (JSON / stdin)
                                         ▼
                ┌─────────────────────────────────────────────────────────┐
                │            sigma:finding-classifier (ESTE PRD)          │
                │   - Python ≥3.10 puro                                   │
                │   - Carga sigma-classifier-rules.yaml                   │
                │   - Aplica mapeo determinístico rule_id → tier          │
                │   - Default conservador (tier C) para rules unknown     │
                │   - Output JSON: ClassifiedFinding[]                    │
                └────────────────────────┬────────────────────────────────┘
                                         │
                              ClassifiedFinding[] (stdout)
                                         ▼
                ┌─────────────────────────────────────────────────────────┐
                │                CAPA CORRECTIVA (TRINIDAD)               │
                │   ┌───────────┐  ┌───────────┐  ┌────────────────┐      │
                │   │  Tier A   │  │  Tier B   │  │    Tier C      │      │
                │   │ mechanic  │  │   agent   │  │   adr-draft    │      │
                │   │ (codemod) │  │  bounded  │  │ (block + ADR)  │      │
                │   └───────────┘  └───────────┘  └────────────────┘      │
                └─────────────────────────────────────────────────────────┘
```

---

## 2. Composición con Phase 1 (scope-aware)

Phase 1 (`sigma:gga-scope-aware`) ya existe — `pre-commit` hook que hace swap de `RULES_FILE` entre `AGENTS.md` (prod) y `AGENTS-sandbox.md` (sandbox) según `FRAMEWORK_SCOPE`.

**Ortogonalidad** (LECCIÓN 37 candidata): Phase 1 filtra **qué severidad emite GGA**; el classifier decide **cómo tratar lo que sí emite**. Son secuenciales:

```
pre-commit hook
  ├─ Phase 1: scope-aware swap (.gga RULES_FILE)
  ├─ gga run                              (capa verifiable filtrada por scope)
  │    output: text → JSON via normalizer
  ├─ Phase 2: sigma:finding-classifier    ← ESTE COMPONENTE
  │    input: Finding[]
  │    output: ClassifiedFinding[]
  └─ Phase 2: handlers Tier A/B/C dispatch (no en este PRD)
```

**Implicación**: el classifier NO necesita conocer el scope. Recibe ya filtrado lo que pasó Phase 1. Esto preserva A20 (boundaries hexagonales).

---

## 3. Modelo de datos

### 3.1. Tipos públicos (contrato externo)

```python
from dataclasses import dataclass
from typing import Literal, Optional

Tier = Literal["A", "B", "C"]

@dataclass(frozen=True)
class Finding:
    """Input al classifier — formato normalizado provider-agnóstico."""
    rule_id: str              # ej. "TS-1", "CSP-UNSAFE-EVAL"
    file: str                 # ruta relativa al repo root
    line: int                 # 1-indexed
    severity: str             # informacional (BLOQUEANTE|CRITICA|ALTA|MEDIA|BAJA)
    message: str              # descripción humana del finding
    source: str               # reviewer name (ej. "GGA")
    raw: Optional[dict] = None  # payload original del reviewer (opcional, para auditoría)

@dataclass(frozen=True)
class ClassifiedFinding:
    """Output del classifier — extiende Finding con etiqueta de tier."""
    finding: Finding
    tier: Tier
    action_hint: Optional[str]  # ej. "eslint-fix", None si tier C sin hint
    matched_rule: bool          # True si rule_id estaba en el YAML; False = default
```

### 3.2. Tipos internos (privados)

```python
@dataclass(frozen=True)
class RuleConfig:
    """Una entrada del YAML curado."""
    tier: Tier
    source: str
    severity: str
    action_hint: Optional[str]
    description: Optional[str]

@dataclass(frozen=True)
class Defaults:
    """Política ante rule_id desconocido."""
    unknown_rule_tier: Tier        # "C" por convención (C3 del PRD)
    unknown_rule_action_hint: str

@dataclass(frozen=True)
class ClassifierRules:
    """Estructura completa del YAML cargado."""
    version: str
    rules: dict[str, RuleConfig]   # O(1) lookup
    defaults: Defaults
```

---

## 4. Interfaces (boundaries hexagonales)

Aplicando A20 (Hexagonal): el classifier tiene **un solo puerto de entrada** y **un solo puerto de salida**. Ambos son JSON estructurado.

### 4.1. Puerto de entrada — `stdin` o `--input <path>`

JSON array con shape `Finding[]`. Ejemplo (1 finding sintético):

```json
[
  {
    "rule_id": "TS-1",
    "file": "src/app/actions/auth.ts",
    "line": 42,
    "severity": "ALTA",
    "message": "Prefer const over let",
    "source": "GGA"
  }
]
```

### 4.2. Puerto de salida — `stdout`

JSON array con shape `ClassifiedFinding[]`. Ejemplo del mismo finding clasificado:

```json
[
  {
    "finding": {
      "rule_id": "TS-1",
      "file": "src/app/actions/auth.ts",
      "line": 42,
      "severity": "ALTA",
      "message": "Prefer const over let",
      "source": "GGA"
    },
    "tier": "A",
    "action_hint": "eslint-fix",
    "matched_rule": true
  }
]
```

### 4.3. Side channel — `stderr`

- Log estructurado (1 línea JSON) cuando rule_id no matchea (AC3 PRD).
- Tabla resumen `tier → count` cuando se invoca con flag `--audit` (AC7 PRD).

### 4.4. Exit codes

| Exit code | Significado |
|-----------|-------------|
| 0 | Clasificación completa (incluso si todo fue a default Tier C) |
| 1 | Error fatal: YAML inválido, input no parseable, schema mismatch |
| 2 | Reservado para futuro (ej. `--strict` mode con unknown_rule = error) |

---

## 5. Algoritmo de clasificación

```python
def classify(findings: list[Finding], rules: ClassifierRules) -> list[ClassifiedFinding]:
    """Determinístico: mismo input → mismo output (MC2 del PRD)."""
    out: list[ClassifiedFinding] = []
    unknown_rule_ids: set[str] = set()

    for f in findings:
        rule = rules.rules.get(f.rule_id)
        if rule is not None:
            out.append(ClassifiedFinding(
                finding=f,
                tier=rule.tier,
                action_hint=rule.action_hint,
                matched_rule=True,
            ))
        else:
            unknown_rule_ids.add(f.rule_id)
            out.append(ClassifiedFinding(
                finding=f,
                tier=rules.defaults.unknown_rule_tier,
                action_hint=rules.defaults.unknown_rule_action_hint,
                matched_rule=False,
            ))

    if unknown_rule_ids:
        emit_calibration_log(unknown_rule_ids)  # → stderr structured JSON

    return out
```

**Propiedades**:
- O(N) sobre cantidad de findings.
- O(1) lookup por finding (dict).
- Idempotente (C6 del PRD).
- Sin side effects sobre el filesystem (C4 del PRD).
- Sin LLM (C1 del PRD).

---

## 6. Estructura de archivos del componente

```
framework/sigma/finding-classifier/        ← Sprint 3 build location (canónico)
├── __init__.py
├── cli.py                                  ← argparse, stdin/stdout, exit codes
├── classifier.py                           ← algoritmo (función pura classify)
├── models.py                               ← dataclasses Finding, ClassifiedFinding, RuleConfig
├── loader.py                               ← parsing YAML → ClassifierRules + validación schema
├── rules.yaml                              ← copia productiva del YAML (curada)
├── README.md                               ← invocación CLI + ejemplos
└── tests/
    ├── test_classifier.py                  ← AC1, AC2, AC3, AC5, AC6
    ├── test_loader.py                      ← YAML inválido, schema mismatch
    ├── test_cli.py                         ← exit codes, --audit flag
    ├── fixtures/
    │   ├── sprint1-iteracion3.json         ← input AC1 (catálogo Sprint 1 normalizado)
    │   └── expected-classified.json        ← output esperado
    └── bench/
        └── bench_50_findings.py            ← AC4 performance benchmark
```

**Ubicación durante este PRD (Sprint 2 sesión 2)**: solo `docs/dominio/sigma-classifier-rules.yaml.draft` existe. El resto se crea en Sprint 3 build.

---

## 7. Invocación CLI

```bash
# Caso happy path (stdin/stdout):
gga run --json | python -m sigma.finding-classifier > classified.json

# Con archivo:
python -m sigma.finding-classifier --input findings.json --output classified.json

# Audit mode (tier counts a stderr):
python -m sigma.finding-classifier --audit < findings.json > classified.json

# Custom rules path:
python -m sigma.finding-classifier --rules /path/to/custom-rules.yaml < findings.json

# Strict mode (futuro, exit 2 si hay unknown rules):
python -m sigma.finding-classifier --strict < findings.json
```

---

## 8. Integración con `.git/hooks/pre-commit`

El hook scope-aware actual (creado en Phase 1) se extiende:

```bash
#!/usr/bin/env bash
set -euo pipefail

# === Phase 1: scope-aware (YA EXISTE) ===
SCOPE="${FRAMEWORK_SCOPE:-production}"
# ... swap .gga RULES_FILE según scope, trap restore ...
GGA_OUTPUT=$(gga run --json 2>&1) || GGA_EXIT=$?
GGA_EXIT="${GGA_EXIT:-0}"

# === Phase 2: classifier (NUEVO en Sprint 3) ===
if [ "$GGA_EXIT" -ne 0 ]; then
  echo "$GGA_OUTPUT" \
    | python -m sigma.finding-classifier --audit \
    > .gga-classified.json \
    2> .gga-unknown-rules.log

  # Sprint 3: dispatch a handlers Tier A/B/C
  # Por ahora (PRD scope), solo reportar:
  echo "Findings clasificados → .gga-classified.json"
  echo "Reglas desconocidas → .gga-unknown-rules.log (para curación)"
  exit 1  # bloqueo del commit hasta Sprint 3 cuando los handlers cierren el loop
fi

exit 0
```

**Decisión**: la integración con el hook se construye en Sprint 3 junto con los handlers. Este PRD solo diseña el contrato y la interfaz CLI.

---

## 9. Carga y validación del YAML

```python
def load_rules(path: Path) -> ClassifierRules:
    """Carga YAML + valida schema. Falla rápido si YAML mal formado."""
    with path.open() as fh:
        raw = yaml.safe_load(fh)

    # Validación mínima:
    if "version" not in raw or "rules" not in raw or "defaults" not in raw:
        raise SchemaError("YAML missing required top-level keys: version, rules, defaults")

    rules: dict[str, RuleConfig] = {}
    for rule_id, cfg in raw["rules"].items():
        if cfg["tier"] not in ("A", "B", "C"):
            raise SchemaError(f"Rule {rule_id} has invalid tier: {cfg['tier']}")
        rules[rule_id] = RuleConfig(
            tier=cfg["tier"],
            source=cfg["source"],
            severity=cfg.get("severity", "UNKNOWN"),
            action_hint=cfg.get("action_hint"),
            description=cfg.get("description"),
        )

    defaults_raw = raw["defaults"]
    if defaults_raw["unknown_rule_tier"] not in ("A", "B", "C"):
        raise SchemaError("defaults.unknown_rule_tier must be A|B|C")

    return ClassifierRules(
        version=raw["version"],
        rules=rules,
        defaults=Defaults(
            unknown_rule_tier=defaults_raw["unknown_rule_tier"],
            unknown_rule_action_hint=defaults_raw.get("unknown_rule_action_hint", ""),
        ),
    )
```

**Política**: validación temprana. Si el YAML está mal formado, `exit 1` inmediato — no se procesan findings con reglas inconsistentes.

---

## 10. Estructura de tests (Paso 8 del protocolo, planificada acá)

Tests adversariales obligatorios alineados con AC del PRD:

| Test | AC cubierto | Tipo |
|------|-------------|------|
| `test_known_rules_match_correctly` | AC1 | Happy path determinismo |
| `test_unknown_rule_defaults_to_tier_C` | AC3 | Edge case + log structured |
| `test_yaml_invalid_exits_1` | RC1 mitigation | Adversarial |
| `test_idempotency_same_input_same_output` | MC2 | Property-based (pytest hypothesis) |
| `test_distribution_within_acceptable_range` | AC2 | Empirical (fixture Sprint 1) |
| `test_performance_50_findings_under_100ms` | AC4 | Benchmark |
| `test_extensibility_new_rule_no_python_change` | AC5 | Integration |
| `test_output_json_schema_valid` | AC6 | Schema validation |
| `test_audit_flag_emits_summary_to_stderr` | AC7 | Functional |
| `test_classifier_does_not_mutate_filesystem` | C4 | Property |
| `test_classifier_does_not_call_network` | C1 (sin LLM) | Adversarial (mock fail si hay request) |

---

## 11. Decisiones de diseño tomadas

| Decisión | Alternativa rechazada | Justificación |
|----------|----------------------|---------------|
| `dict[rule_id, RuleConfig]` para lookup | Lista lineal con regex matching | O(1) vs O(N). RC4 mitigation. |
| Adapter normalizer fuera del classifier | Classifier acopla a formato GGA | A20 hexagonal — el classifier no sabe quién emitió el finding. |
| YAML como source declarativo | TOML / JSON / Python dict hardcoded | YAML legible humano + comentarios + curación humana viable (Visión C). |
| stdin/stdout como protocolo IPC | Llamada HTTP / función Python directa | Composabilidad UNIX. Permite usarlo con cualquier reviewer presente y futuro. |
| Default Tier C ante unknown | Default Tier A | RC2 mitigation: false positives de auto-fix son catastróficos; falsos negativos de auto-fix solo regresan al humano. |
| Exit code 0 incluso con unknown rules | Exit code 1 por unknown rule | El classifier no es gate; los handlers downstream deciden bloqueo. C4 separación de responsabilidades. |
| Output JSON estructurado | Texto formateado humano | Composabilidad con handlers downstream. Humano lee `--audit` summary. |
| Hot-reload del YAML deshabilitado | Watch + reload | Determinismo por corrida. Cambios pasan por git review. |

---

## 12. Riesgos arquitectónicos identificados

| ID | Riesgo | Mitigación arquitectónica |
|----|--------|---------------------------|
| RA1 | El normalizer GGA-output → Finding[] vive fuera del classifier; si rompe, classifier no se entera. | Output del normalizer se valida con JSON Schema antes de pasarse al classifier. Fallo en normalizer = exit 1 explícito. |
| RA2 | Acoplamiento implícito al schema YAML — cambios al schema rompen YAMLs antiguos. | `version` semver en el YAML + validación de versión soportada en `load_rules`. Bumps de schema requieren migration script. |
| RA3 | Tests sin fixtures reales → AC2 (distribución) no medible. | Fixture obligatorio `sprint1-iteracion3.json` poblado con catálogo curado (`findings-taxonomy.md` sección 3) antes de cualquier merge. |
| RA4 | Performance degrada si se invoca por archivo individual en vez de batch. | Diseño batch-first: API toma `list[Finding]`. CLI consume stdin completo, no streaming line-by-line. |
| RA5 | Composición con handlers Sprint 3 puede revelar que ClassifiedFinding necesita campos extras (ej. `confidence`). | Los handlers son consumers — el contrato se extiende con backward-compat (campos nuevos opcionales). Schema versionado mitiga. |

---

## 13. Próximo paso (Paso 4 del protocolo)

Con arquitectura definida, Paso 4 = **Stories con acceptance criteria ejecutables**.

Cada story debe ser:
- Pequeña (≤4 hs de build).
- Verificable independientemente.
- Con Given/When/Then explícito.
- Vinculada a uno o más AC del PRD.

Output: `docs/stories/STORIES-sigma-finding-classifier.md`.

---

## 14. Conexión con principios rectores

| Principio | Cómo la arquitectura lo encarna |
|-----------|--------------------------------|
| **1°** (Python verifica) | Classifier es Python puro determinístico. Cero IA en el path. |
| **2°** (3 capas) | Componente posicionado explícitamente entre verifiable y correctiva. |
| **3°** (Dominio-first) | YAML curado desde dominio (findings-taxonomy.md), no inventado. |
| **4°** (Auto-fix > finding) | Habilita el flag estructural — sin classifier, no hay decisión de "qué es inequívoco". |
| **5°** (Polinización) | Boundary hexagonal (`source` en `Finding`) permite que GGA, R/G/FG y futuros reviewers compartan classifier. |
| **6°** (Descubrir antes de ejecutar) | Fixture `sprint1-iteracion3.json` es la captura empírica del dominio real. |
| **A20** (Hexagonal) | 1 puerto entrada (stdin/argv) + 1 salida (stdout). Sin acceso directo a filesystem ni network. |
| **A12** (Zero trust) | Validación de YAML schema al cargar; validación de Finding[] al recibir input. |
| **A21** (Observability) | `--audit` mode + structured logging a stderr. Trazable. |
