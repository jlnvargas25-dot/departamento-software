# Codemod Toolbox — `sigma:auto-fix-mechanic`

**Status**: DRAFT v0.1
**Date**: 2026-05-22 (Sprint 3 sesión 3 — Paso 2 PROTOCOLO dominio)
**Owner**: Departamento de Software
**Related**: PRD-sigma-auto-fix-mechanic.md, auto-fix-mechanic-rules.yaml.draft, classifier/rules.yaml v0.1.0
**Protocolo**: Paso 2 (Capturar dominio activamente) del PROTOCOLO-CONSTRUCCION-CODIGO

---

## Propósito

Catálogo de los **tools externos** que el `sigma:auto-fix-mechanic` invoca via subprocess para aplicar codemods determinísticos. Documenta qué herramienta cubre qué rule_ids, comandos exactos, verificación post-fix, instalación y alternativas consideradas. Es el sustrato empírico de la decisión del **Paso 3** (wholesale ECC vs wrapper sigma propio).

---

## 1. Resumen del toolbox

| Tool | Tipo | Rule_ids cubiertos | Disponibilidad |
|------|------|---------------------|----------------|
| **ESLint --fix** (con plugins) | Codemod genérico stack TS | 8/15 (TS-1, NO-VAR, VAR-TO-CONST, LET-WITHOUT-REASSIGN, UNUSED-IMPORT, IMPORT-ORDER, OBJECT-SHORTHAND, MISSING-SEMI*) | Estándar (npm) |
| **Prettier --write** | Formatter | 2-3/15 (TRAILING-WHITESPACE, MISSING-SEMI*) | Estándar (npm) |
| **ts-morph custom codemods** | AST library para TypeScript | 4/15 (TS-NON-NULL-ASSERTION, A21-OBS-1-CONSOLE-LOG, A21-OBS-1b-DENO-CONSOLE, TYPE-CAST-AS-ANY) | Estándar (npm), scripts custom del Framework |
| **Python custom scripts** | Scripts del Framework | 2/15 (MIGRATION-NAMING, PGSQL-MISSING-VOLATILE) | Custom Framework (`framework/sigma/auto_fix_mechanic/codemods/*.py`) |

\* MISSING-SEMI puede ir por eslint o prettier según config del proyecto target.

**Total cobertura**: 15/15 rule_ids Tier A v0.1.0 (100%) usando 4 tools distintos.

---

## 2. Tools estándar del ecosistema TS (cubren 10-11/15)

### 2.1 ESLint --fix (con plugins)

**Versión recomendada**: ESLint 8.x o 9.x (CommonJS o flat config según proyecto target).

**Plugins requeridos** (en el proyecto target, no en el mechanic):
- Core: incluye prefer-const, no-var, object-shorthand, semi.
- `eslint-plugin-import` — para `import/order`.
- `@typescript-eslint/eslint-plugin` — para reglas TS-1 (familia), no-unused-vars con TS.
- `eslint-plugin-unused-imports` (opcional pero recomendado para UNUSED-IMPORT) — distingue side-effect imports de imports a remover.

**Patrón de invocación canónico**:
```bash
npx eslint --fix --rule '{<rule>: error}' <target-file>
```

**Verificación post-fix**:
```bash
npx eslint --quiet --rule '{<rule>: error}' <target-file>
# Exit 0 = patrón resuelto. Exit ≠ 0 = patrón persiste → mechanic escala a Tier C.
```

**Alternativas consideradas**:
- ❌ **eslint sin --fix**: solo reporta, no aplica. No nos sirve (somos el handler de fix).
- ❌ **biome**: alternativa moderna a eslint+prettier, MAS PERFORMANTE. Considerado pero NO adoptado: el sandbox-stack y proyectos target probablemente usan eslint+prettier (stack del ecosistema). Costo de migración > beneficio. **Evaluar adopción biome en Sprint 5+ si proyectos target lo adoptan masivamente.**
- ❌ **prettier-eslint integration**: combina ambos pero introduce abstracción extra. Preferimos invocar cada tool por separado para trazabilidad (qué tool fixeó qué).

**Rule_ids cubiertos** (8):
- TS-1 (familia: prefer-const, no-var, no-unused-vars, etc.)
- NO-VAR (rule: `no-var`)
- VAR-TO-CONST (rule: `prefer-const`)
- LET-WITHOUT-REASSIGN (rule: `prefer-const`, alias funcional de VAR-TO-CONST)
- UNUSED-IMPORT (rule: `@typescript-eslint/no-unused-vars` + `unused-imports/no-unused-imports`)
- IMPORT-ORDER (rule: `import/order`)
- OBJECT-SHORTHAND (rule: `object-shorthand`)
- MISSING-SEMI* (rule: `semi`) — solo si proyecto NO usa prettier para semis.

### 2.2 Prettier --write

**Versión recomendada**: Prettier 3.x (con respeto al `.prettierrc` del proyecto target).

**Patrón de invocación**:
```bash
npx prettier --write <target-file>
```

**Verificación post-fix**:
```bash
npx prettier --check <target-file>
# Exit 0 = formato correcto. Exit ≠ 0 = patrón persiste → escalación.
```

**Configuración respetada**:
- `.prettierrc`, `.prettierrc.json`, `prettier.config.js` del proyecto target.
- Si proyecto usa `semi: false`, prettier NO fuerza semis (NO-OP en MISSING-SEMI).
- Si proyecto usa `trailingComma: "all"`, prettier respeta esa config.

**Alternativas consideradas**:
- ❌ **dprint**: rust-based, más rápido. Mismo argumento que biome: costo migración > beneficio en Sprint 3.
- ❌ **eslint con prettier-plugin**: combina pero introduce duplicación de tooling. Preferimos invocar prettier directo.

**Rule_ids cubiertos** (2-3):
- TRAILING-WHITESPACE (prettier strip automático)
- MISSING-SEMI* (si proyecto usa prettier para semis)

### 2.3 ts-morph (AST library para TypeScript)

**Versión recomendada**: ts-morph 22.x o superior.

**Naturaleza**: NO es un CLI, es una librería Node.js para manipular AST de TypeScript programáticamente. Los codemods custom del Framework son scripts TypeScript/JavaScript que usan ts-morph.

**Patrón de invocación**:
```bash
node framework/sigma/auto_fix_mechanic/codemods/<codemod-name>.js <target-file>
```

Cada codemod script:
1. Carga el archivo target en un `Project` de ts-morph.
2. Aplica transformación AST específica.
3. Guarda el archivo modificado.
4. Retorna exit code 0 si aplicó, 1 si pattern no encontrado, 2 si error.

**Verificación post-fix**:
```bash
node framework/sigma/auto_fix_mechanic/codemods/<codemod-name>.js --verify <target-file>
# Mismo script en modo verify: cuenta ocurrencias del pattern AST esperado.
# Exit 0 = pattern eliminado (verificación pasada).
```

**Alternativas consideradas**:
- ❌ **jscodeshift**: similar a ts-morph pero más popular en ecosystem React. Considerado. **Rechazado** porque ts-morph tiene tipos TS first-class (mejor DX para nuestros codemods que tocan tipos como `as any`).
- ❌ **babel-plugin custom**: nivel demasiado bajo, demasiado código boilerplate.
- ❌ **regex puro**: NO sirve para codemods que requieren context AST (ej. console-to-logger requiere saber si hay import del logger).

**Rule_ids cubiertos** (4):
- TS-NON-NULL-ASSERTION (codemod: `non_null_to_optional.ts`)
- A21-OBS-1-CONSOLE-LOG (codemod: `console_to_logger.ts`)
- A21-OBS-1b-DENO-CONSOLE (codemod: `console_to_json_structured.ts`)
- TYPE-CAST-AS-ANY (codemod: `infer_type_from_context.ts`)

### 2.4 Python custom scripts

**Versión**: Python 3.10+ stdlib (mismo stack que el classifier, sin deps adicionales).

**Naturaleza**: scripts Python para casos donde el rule_id NO mapea naturalmente a herramientas del ecosystem TS:
- Operaciones a nivel sistema de archivos (rename).
- Operaciones sobre SQL (no es JavaScript/TypeScript).

**Patrón de invocación**:
```bash
python framework/sigma/auto_fix_mechanic/codemods/<script-name>.py <target>
```

**Alternativas consideradas**:
- ❌ **shell scripts (bash)**: portabilidad cross-platform (Windows del operador). Python es portátil.
- ❌ **Node.js para SQL**: agregar Node a casos no-TS introduce dependency cross-stack.
- ❌ **pgsql-parser** (Postgres CLI): no instalado por default. Python regex sobre `.sql` es suficiente para PGSQL-MISSING-VOLATILE (patrón simple).

**Rule_ids cubiertos** (2):
- MIGRATION-NAMING (script: `rename_migration_timestamp.py`)
- PGSQL-MISSING-VOLATILE (script: `add_volatile_marker.py`)

---

## 3. Evidencia para Paso 3 — wholesale ECC vs wrapper sigma propio

Esta sección documenta la evidencia empírica que el **Paso 3 (Arquitectura)** usará para resolver el fork pendiente.

### 3.1 Catálogo de ECC build-fix y refactor-clean

**ECC `build-fix`** (per agent description): *"Detect the project build system and incrementally fix build/type errors with minimal safe changes."*

- **Scope**: build/type errors genéricos del compilador/build system.
- **Granularidad**: NO conoce rule_ids específicos del Framework.
- **Mecanismo**: probablemente invoca tsc, build CLI del framework, y aplica fixes mínimos. Usa LLM en el path (sub-agent ECC).

**ECC `refactor-clean`** (per agent description): *"Dead code cleanup and consolidation specialist. Use PROACTIVELY for removing unused code, duplicates, and refactoring."*

- **Scope**: dead code, duplicación, refactoring estructural.
- **Granularidad**: alto nivel (no rule-by-rule específico).
- **Mecanismo**: corre knip/depcheck/ts-prune para identificar dead code. NO codemods rule_id específicos.

### 3.2 Mapeo evidencia: cobertura ECC vs los 15 rule_ids Tier A

| Rule_id Tier A | ECC build-fix lo cubre? | ECC refactor-clean lo cubre? | Sustituto en stack TS estándar |
|----------------|--------------------------|------------------------------|------------------------------|
| TS-1 | 🟡 parcial (si build error) | ❌ No | ✅ ESLint --fix |
| TS-NON-NULL-ASSERTION | ❌ No (no es build error) | ❌ No | ✅ ts-morph custom |
| A21-OBS-1-CONSOLE-LOG | ❌ No (Framework-specific) | ❌ No | ✅ ts-morph custom |
| A21-OBS-1b-DENO-CONSOLE | ❌ No (Framework-specific) | ❌ No | ✅ ts-morph custom |
| NO-VAR | ❌ No (no build error) | ❌ No | ✅ ESLint --fix |
| VAR-TO-CONST | ❌ No | ❌ No | ✅ ESLint --fix |
| MIGRATION-NAMING | ❌ No (filename pattern) | ❌ No | ✅ Python custom |
| TYPE-CAST-AS-ANY | 🟡 parcial (a veces causa error) | ❌ No | ✅ ts-morph custom |
| PGSQL-MISSING-VOLATILE | ❌ No (SQL fuera del scope build TS) | ❌ No | ✅ Python custom |
| LET-WITHOUT-REASSIGN | ❌ No | ❌ No | ✅ ESLint --fix |
| UNUSED-IMPORT | ❌ No (warning, no error) | 🟡 parcial (dead code) | ✅ ESLint --fix |
| TRAILING-WHITESPACE | ❌ No | ❌ No | ✅ Prettier |
| MISSING-SEMI | ❌ No | ❌ No | ✅ Prettier/ESLint |
| IMPORT-ORDER | ❌ No | ❌ No | ✅ ESLint --fix |
| OBJECT-SHORTHAND | ❌ No | ❌ No | ✅ ESLint --fix |

**Conteo de cobertura ECC**: 0/15 cobertura directa. 3/15 cobertura parcial (TS-1, TYPE-CAST-AS-ANY, UNUSED-IMPORT) — y solo si esos rule_ids causan build error o son detectados como dead code, lo cual NO es garantizado.

**Conteo de cobertura tools estándar TS + Python custom**: 15/15 cobertura directa con verificación post-fix determinística.

### 3.3 Conclusión empírica para Paso 3

La evidencia sugiere fuertemente que **ECC `build-fix` y `refactor-clean` NO son adecuados como backend wholesale del Tier A** porque:

1. **No conocen los rule_ids del Framework**: A21-OBS-1-CONSOLE-LOG, MIGRATION-NAMING, PGSQL-MISSING-VOLATILE son específicos del Framework y NO mapean a errores de compilación genéricos.
2. **Usan LLM en el path**: viola C1 del PRD (sin LLM en path de fix). ECC build-fix es sub-agent con razonamiento, no codemod determinístico.
3. **No determinísticos**: dos invocaciones de ECC sobre el mismo input pueden dar fixes distintos (sub-agent reasoning). Esto rompe AM7 (idempotencia) del PRD.
4. **Granularidad incorrecta**: ECC opera a nivel "fix this build error", no "apply this specific codemod for this specific rule_id".

**Recomendación para Paso 3** (a confirmar empíricamente):
- **Construir wrapper sigma propio** que orquesta los 4 tools (ESLint, Prettier, ts-morph custom, Python custom) según `auto-fix-mechanic-rules.yaml`.
- **ECC sigue siendo útil** para casos fuera del scope del classifier (build errors no clasificados como Tier A): el operador puede invocar ECC directamente cuando necesite, NO via el mechanic. Composición lateral, no wholesale.
- **Visión C respetada**: el mechanic compone sobre tools del stack (eslint, prettier, ts-morph) — no construye desde cero. Solo construye los 2 scripts Python custom + los 4 codemods ts-morph custom que son necesariamente del Framework (rule_ids del Framework).

Esta recomendación se formaliza en el documento de Arquitectura del Paso 3 con su rationale completo + alternativas rechazadas explícitas.

---

## 4. Decisiones de mapeo tomadas en este Paso 2

| Decisión | Resolución | Justificación |
|----------|------------|---------------|
| ¿Usar eslint --fix o reinventar codemods en Python? | **eslint --fix donde aplique** | Visión C: composición sobre stack. Eslint cubre 8/15 sin código del Framework. |
| ¿MISSING-SEMI por eslint o prettier? | **Prettier por default, eslint fallback** | Respeta `.prettierrc` local del proyecto target. Si proyecto NO tiene prettier, eslint con `semi: error`. |
| ¿ts-morph o jscodeshift para codemods custom? | **ts-morph** | Mejor soporte de tipos TS first-class. DX superior para nuestros 4 codemods (especialmente TYPE-CAST-AS-ANY). |
| ¿Bash o Python para MIGRATION-NAMING? | **Python** | Portabilidad Windows. Mismo stack que classifier. |
| ¿pgsql-parser CLI o regex Python para PGSQL-MISSING-VOLATILE? | **Regex Python** | Patrón simple (CREATE FUNCTION ... LANGUAGE plpgsql sin VOLATILE/STABLE/IMMUTABLE marker). No requiere parser SQL completo. Sin deps adicionales. |
| ¿Default VOLATILE/STABLE/IMMUTABLE para PGSQL? | **VOLATILE** | Postgres default + más seguro (suboptimal perf pero correcto semánticamente). Operador puede sobreescribir post-fix. |
| ¿Manejar side-effect imports en UNUSED-IMPORT? | **Usar eslint-plugin-unused-imports** | El plugin distingue side-effects (`import "./styles.css"`) de imports a remover. Plugin es más seguro que rule core. |
| ¿Cobertura wholesale ECC build-fix viable? | **NO viable** (evidencia sección 3.2) | 0/15 directa, 3/15 parcial. ECC usa LLM, no determinístico. Recomendación Paso 3: wrapper sigma propio. |

---

## 5. Próximas precondiciones para Sprint 3 sesión 4 (build)

Antes de arrancar el build del mechanic (Paso 6):

1. **Confirmar tools instalados en environment de desarrollo**:
   - `npx eslint --version` y `npx prettier --version` accesibles.
   - `ts-morph` instalado en proyecto target o en environment del mechanic.
   - Python 3.10+ accesible.
2. **Definir contrato de los 4 codemods ts-morph custom** (en Paso 3 arquitectura):
   - `non_null_to_optional.ts` — input/output, verificación, fallback.
   - `console_to_logger.ts` — handling de import inject, alias resolution.
   - `console_to_json_structured.ts` — scope solo `supabase/functions/`.
   - `infer_type_from_context.ts` — strategy de inference, fallback a Tier C.
3. **Definir contrato de los 2 scripts Python custom**:
   - `rename_migration_timestamp.py` — DRY-RUN mode + mapping log para rollback.
   - `add_volatile_marker.py` — patrón regex + idempotencia.
4. **Resolver Paso 3 fork wholesale ECC vs wrapper sigma**: documentar en `docs/arquitectura/ARQUITECTURA-sigma-auto-fix-mechanic.md` con alternativas rechazadas + evidencia sección 3 de este doc.

---

## 6. Out of scope (documentar para evitar drift)

- ❌ Codemods para validadores R/G/FG futuros (Sprint 4+ cuando esos validadores existan).
- ❌ Codemods para Tier B o Tier C rule_ids (otros componentes de la trinidad).
- ❌ Migración del stack a biome/dprint (Sprint 5+ si la comunidad adopta masivamente).
- ❌ UI dashboard de tasa de fix por rule_id (Sprint 5+).
- ❌ Instalación automática de tools (eslint, prettier, ts-morph) — responsabilidad del operador, documentado en pre-flight check.

---

## 7. Relación con principios rectores

| Principio | Cómo el dominio del toolbox lo encarna |
|-----------|----------------------------------------|
| **1° (Python verifica)** | Mechanic es Python; tools externos invocados via subprocess. Verificación post-fix determinística (re-run del tool o AST check). |
| **2° (3 capas)** | Tools son la **superficie ejecutiva** de la capa CORRECTIVA. La capa preventiva (PROTOCOLO) y verificable (GGA/classifier) ya existen — el toolbox completa el ciclo. |
| **3° (Dominio-first)** | Este documento ES el dominio del mechanic. Sin él, el build del Paso 6 sería especulativo. |
| **4° (Auto-fix > finding cuando inequívoco)** | Cada handler del YAML mapea rule_id (clasificado como inequívoco por classifier) a codemod (también determinístico). Doble certeza. |
| **5° (Polinización cruzada)** | El toolbox de eslint+prettier+ts-morph+Python custom se polinizará al siguiente componente (correction-agent-bounded Tier B) con sub-agente LLM en lugar de codemod determinístico. Mismo patrón estructural. |
| **6° (Descubrir antes de ejecutar)** | Pre-flight check verifica disponibilidad de tools al boot. Sección 3.2 documenta evidencia ECC vs wrapper sigma antes de decidir en Paso 3. |
| **7° (Meta-producto recursivo)** | Los codemods custom del Framework (`framework/sigma/auto_fix_mechanic/codemods/`) son artefactos del propio Framework — auto-aplicables si GGA encuentra esos patterns en código sigma. |

---

**Próximo paso (Paso 3 del protocolo)**: Diseñar arquitectura técnica del `sigma:auto-fix-mechanic` incorporando la decisión wholesale ECC vs wrapper sigma con la evidencia de la sección 3 de este documento. Output: `docs/arquitectura/ARQUITECTURA-sigma-auto-fix-mechanic.md`.
