# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico post-Sprint 3 COMPLETO.
> Stallen DIFERIDO hasta que el Framework esté maduro.

**Última actualización**: 2026-05-24 (Sprint 3 sesión 7 — Paso 12 cierre formal + ADR-011 ACCEPTED v1.0)
**Cliente recomendado próxima sesión**: **Claude Code CLI** dentro de `C:\DEPARTAMENTO-SOFTWARE\` (skills speckit-* + ecc:* + claude-mem:* + sdd-* + superpowers:* todos cargados)
**Versión**: 8.0 (Sprint 3 COMPLETO — classifier + mechanic operativos + auditados; ADR-011 v1.0 ACCEPTED)

---

## ✅ SPRINT 3 COMPLETO (2026-05-24)

### Paso 12 PROTOCOLO — Cierre formal

**Scope completado**: Phase 2 ADR-011 parcial — 2 de 4 componentes de la trinidad correctiva operativos y auditados.

| Componente | Status | Tests | LOC prod | Sesiones |
|------------|--------|-------|----------|----------|
| `sigma:finding_classifier` (front-end) | ✅ OPERATIVO | 73 PASS | 294 | Sprint 3 ses 1-2 |
| `sigma:auto_fix_mechanic` (Tier A) | ✅ OPERATIVO | 194 PASS (incl. 73 classifier) | ~1600 + ~720 codemods | Sprint 3 ses 3-6 |
| `sigma:correction_agent_bounded` (Tier B) | ⏳ diferido Sprint 4 | — | — | — |
| `sigma:correction_adr_draft` (Tier C) | ⏳ diferido Sprint 4 | — | — | — |

**Métricas consolidadas Sprint 3**:
- **194 tests PASS + 1 skip en 5.69s** (baseline final)
- **~1894 LOC producción + ~1839 LOC tests** (classifier + mechanic combinados)
- **7 sesiones** (2 classifier build + 1 mechanic planning + 2 mechanic build + 1 audits + 1 cierre)
- **L38 N=5**: 5 commits consecutivos pasaron GGA en 1 round sin bypass
- **ADR-011**: PROPOSED v0.1 → v0.5 → v0.7 → v0.9 → **ACCEPTED v1.0**

### Commits Sprint 3

| Sesión | Commit | Contenido |
|--------|--------|-----------|
| 1 | `06493bc` | classifier S-1..S-3 (36 tests) |
| 2 | `2322e4a` | classifier S-4..S-8 (73 tests) + audit Paso 7+8 |
| 3 | `3049039` | ADR-011 v0.9 + L38 formal + LECCIONES.md + mechanic planning |
| 3 | `e142933` | SIGUIENTE-SESION v7.0 refresh |
| 4 | `3701463` | mechanic S-1..S-5 core (163 tests) |
| 4 | `f8f78e6` | L38 N=2→N=3 |
| 5 | `797772f` | mechanic S-6+S-7+S-8 E2E (181 tests) |
| 5 | `bf67805` | L38 N=3→N=4 |
| 6 | `d35c3f0` | Audit Paso 7+8 PASS + polish 3 advisories (194 tests) |
| 6 | `e82f1da` | L38 N=4→N=5 |
| 7 | (pendiente) | ADR-011 v1.0 ACCEPTED + Paso 12 cierre |

### Pasos del PROTOCOLO ejecutados sobre auto-fix-mechanic

| Paso | Status | Sesión |
|------|--------|--------|
| 1 — PRD | ✅ | 3 |
| 2 — Dominio | ✅ | 3 |
| 3 — Arquitectura | ✅ (wrapper sigma propio, NO wholesale ECC) | 3 |
| 4 — Stories | ✅ S-1..S-8 | 3 |
| 5 — Audit plan | ✅ READY_FOR_BUILD_WITH_DEUDAS_TRACKED | 3 |
| 6 — Build código | ✅ | 4-5 |
| 7 — Audit código | ✅ PASS (17 gates PASS, 0 críticos) | 6 |
| 8 — Tests adversariales | ✅ PASS (15/15 categorías) | 6 |
| 9 — Validación seguridad | ✅ parcial (zero-trust en Paso 7) | 6 |
| 10 — Deploy | N/A (sigma skill, no app) | — |
| 11 — Verificación post-deploy | N/A | — |
| 12 — Cierre + polinización | ✅ **ESTA SESIÓN** | 7 |

---

## 🔄 RADAR DE POLINIZACIÓN — Sprint 3 (R-4 obligatorio)

> 5° principio rector: *"Un patrón de dolor descubierto en un subsistema es candidato a propagarse a los demás estructuralmente similares."*

### Patrones candidatos a propagación

| # | Patrón descubierto | Origen | Candidato a propagarse a | Acción |
|---|-------------------|--------|--------------------------|--------|
| P1 | **PROTOCOLO + audit Paso 5 → GGA 1 round** (L38 N=5) | classifier + mechanic builds | Tier B/C builds, Stallen, cualquier futuro módulo sigma | Ya operacionalizado. Cross-proyecto pendiente. |
| P2 | **Wrapper sigma propio > wholesale ECC para tareas determinísticas** | mechanic Paso 3 decisión | Futuros componentes 100% determinísticos del Framework | Documentado en ARQUITECTURA mechanic. ECC sigue útil para tareas con LLM. |
| P3 | **Audit Paso 7 consolida evidencia GGA automática + agrega dimensiones manuales** | mechanic sesión 6 | Todos los futuros audits de código del Framework | Patrón reduce trabajo + mejora trazabilidad. Documentar en PROTOCOLO. |
| P4 | **Cross-reference testing para categorías adversariales ya cubiertas** | mechanic sesión 6 (10/15 cross-refs) | Cualquier test_adversarial.py futuro | Evita duplicación sin perder trazabilidad. |
| P5 | **M3 sandbox con stub handlers + threshold reducido (≥0.5 vs ≥0.9)** | mechanic S-8 | Futuras métricas empíricas medidas sin stack real | Patrón "medir lo que se puede ahora, real diferido a integración". |
| P6 | **Commit-per-session** (no per-story ni per-block) | Precedente Sprint 3 ses 4-6 | Cualquier build multi-sesión | Mantiene git history limpio + GGA verificable por sesión. |

### Patrones NO propagables (contexto-específicos)

| Patrón | Razón de no-propagación |
|--------|------------------------|
| ts-morph local en codemods/ (sin tocar deps Python) | Específico a codemods JS; otros módulos son Python puro |
| `threading.Lock` intra-process (no cross-process) | Decisión scoped a Sprint 3; cross-process si surge necesidad real en Sprint 5+ |
| `shlex.split(posix=True)` para Windows-compat | Workaround Windows paths; no aplica a otros OS |

### Lecciones operativas Sprint 3 (candidatas N=1)

| ID | Enunciado | Evidencia |
|----|-----------|-----------|
| L39 | Audit manual que consolida evidencia de GGA automático previo reduce esfuerzo y mejora trazabilidad | Sprint 3 ses 6 — audit Paso 7 reusó 2 GGA reviews y cerró en <30 min |
| L40 | Cross-reference testing (sanity import + docstring pointer) evita duplicación adversarial sin perder cobertura | Sprint 3 ses 6 — 10/15 categorías via cross-ref, 5 nuevas |
| L41 | Commit-per-session en builds multi-story produce history limpio y permite GGA verify por sesión | Sprint 3 ses 4-6 — 3 commits, 3 GGA passes, 0 conflictos |

---

## ESTADO ACTUAL (post Sprint 3 — 2026-05-24)

### Trinidad correctiva (ADR-011 ACCEPTED v1.0)

| Componente | Status | Sprint |
|------------|--------|--------|
| `sigma:finding_classifier` (front-end) | ✅ DONE — 73 tests, audit PASS | Sprint 3 ses 1-2 |
| `sigma:auto_fix_mechanic` (Tier A) | ✅ DONE — 194 tests, audit Paso 7+8 PASS | Sprint 3 ses 3-6 |
| `sigma:correction_agent_bounded` (Tier B) | ⏳ pendiente | Sprint 4 |
| `sigma:correction_adr_draft` (Tier C) | ⏳ pendiente | Sprint 4 |
| Integración E2E (GGA → classifier → handler → patch) | ⏳ pendiente | Sprint 4 |

### Repo

- **Branch**: main
- **HEAD al cierre Sprint 3**: commit sesión 7 (este commit)
- **Working tree esperado**: clean post commit

---

## QUÉ HACER EN LA PRÓXIMA SESIÓN (Sprint 4 sesión 1)

### Decisión de dirección (preguntar al operador)

Sprint 4 tiene dos caminos posibles:

**(a) Continuar trinidad correctiva** — construir Tier B (`correction-agent-bounded`) + Tier C (`correction-adr-draft`) + integración E2E. Cerraría ADR-011 v1.1 FULL.

**(b) Pivotar a validación cross-proyecto** — aplicar workflow PROTOCOLO + audit sobre Stallen (o tercer proyecto) para validar L38 cross-proyecto y aspirar a regla A26 universal.

**(c) Híbrido** — un sprint corto de Tier B (2 sesiones) + aplicar a Stallen para medir M3 real + M1 cross-proyecto.

**Recomendación**: (c) — Tier B es el componente más valioso pendiente (semi-determinístico con LLM acotado); Stallen da evidencia cross-proyecto para L38 y M3 real.

### PASO T-1 — Verificación commit cierre Sprint 3

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git log --oneline -5
git status
# Tests baseline
cd framework
python -m pytest sigma/ -q
# Esperado: 194 passed, 1 skipped
```

---

## DEUDAS TÉCNICAS — estado post Sprint 3

### Deudas RESUELTAS en Sprint 3

- ✅ R07 — AC2 sin story explícita → S-8 classifier
- ✅ R08 — `serializeErr()` helper → S-6.3 mechanic (`console_to_json_structured.js`)
- ✅ R10 — Fixture `sprint1-iteracion3.json` → construido y poblado

### Deudas NUEVAS de Sprint 3

- 🟡 **DEUDA-CODEMODS-NO-PYTEST-AUTOMATED**: smoke tests de codemods son manuales (Bash/Node). Para CI, agregar `test_codemods_smoke.py` con `pytest.mark.skipif`. No bloqueante.
- 🟡 **DEUDA-M3-REAL-NOT-MEASURED**: M3 real (≥90% sobre stack TS) requiere environment con ESLint/Prettier/ts-morph reales. Diferida a integración Stallen.
- 🟡 **DEUDA-ADR-011-V1.1**: Tier B + Tier C + M3 real + M1 cross-proyecto pendientes para ACCEPTED FULL.

### Deudas ABIERTAS heredadas (sin cambio)

- 🟡 DEUDA-ADVERSARIAL-TEST-SHAPE-WRONG (Iteración 3)
- 🟢 DEUDA-NPM-INSTALL-MANUAL (Iteración 3)
- 🟢 DEUDA-SUPABASE-LOCAL-MANUAL (Iteración 3)
- 🟡 DEUDA-SIGMA-MVP-NO-CONSTRUIDAS — diferidas Sprint 4+
- 🟡 DEUDA-CONSTITUTION-CHECK-ENFORCEMENT — diferida
- 🟡 DEUDA-TAXONOMIA-CLARIFY-INCOMPLETA — diferida
- 🟡 DEUDA-FACT-FORCING-GATE-EN-SANDBOX (workaround documentado)
- 🟡 DEUDA-CLAUDE-MEM-MANIFEST (parche local persistente)
- 🟢 DEUDA-PLUGIN-INSTALL-DOCS
- 🟢 DEUDA-WINDOWS-SETUP-CHECKLIST
- 🟢 DEUDA-SDD-EXPLORE-NO-WRITE (menor)
- 🟢 DEUDA-SUB-AGENT-OVERRIDE-OPERATOR (menor)
- 🟡 DEUDA-ADR-010-PROMOTE-TO-ACCEPTED
- 🟡 DEUDA-NORTE-FRAMEWORK-PLACEHOLDERS (Q4-Q7)
- 🟡 DEUDA-WORKFLOW-OPERATIVO
- 🟡 DEUDA-VISIÓN-D-NO-FORMALIZADA
- 🟡 DEUDA-REPLANTEAR-ROADMAP-POST-STACK

---

## REGLAS CRÍTICAS A RECORDAR (Sprint 4+)

### 7 Principios rectores (sin cambio)
1. Python traza → IA recorre → Python verifica
2. **3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA** ← L38 N=5 confirma empíricamente
3. Dominio-first
4. **Auto-fix > finding cuando inequívoco** ← `auto-fix-mechanic` OPERACIONALIZA
5. **Polinización cruzada** ← radar Sprint 3 ejecutado (6 patrones propagables)
6. **Descubrir antes de ejecutar** (audit empírico)
7. Meta-producto recursivo

### Lecciones formales (architecture/LECCIONES.md)
- **L38 N=5**: PROTOCOLO + audit Paso 5 elimina loop GGA asintótico. Cross-proyecto pendiente para A26.

### Lecciones candidatas N=1 nuevas (Sprint 3)
- **L39**: audit manual que consolida evidencia GGA previo reduce esfuerzo
- **L40**: cross-reference testing evita duplicación adversarial
- **L41**: commit-per-session en builds multi-story produce history limpio

---

## NOTAS PARA CLAUDE

- **Usuario**: Julián Vargas, vibe coder / harness engineer
- **Cliente recomendado**: Claude Code CLI dentro de `C:\DEPARTAMENTO-SOFTWARE\`
- **Cuando Julián cuestione "ya está hecho"** → audit empírico INMEDIATO
- **NUNCA proyectar cansancio**
- **PROTOCOLO-INICIO-CHAT v1.0 PASO 1 OBLIGATORIO** para verificar Project es Framework
- **2 directorios a NO confundir**: `C:\DEPARTAMENTO-SOFTWARE\` (activo) vs `C:\Users\Windows 11\sigmacontrol-camino-1\` (legacy pause)
- **L38 ya es FORMAL N=5** — no usarla como "candidata" en docs nuevos
- **L35-L37 SIGUEN candidatas N=1** — no promoverlas sin segundo evento empírico
- **ADR-011 es ACCEPTED v1.0** — scope: classifier + mechanic. Tier B/C → v1.1
- **Trinidad correctiva**: classifier ✅, mechanic ✅, Tier B ⏳, Tier C ⏳
- **claude-mem requiere `autoUpdate: false`** — no romper el parche local

---

Creado: 2026-05-15 | Versión: **8.0** (Sprint 3 COMPLETO — Paso 12 cierre formal + ADR-011 ACCEPTED v1.0 + radar polinización)
Para: Claude que abra próxima sesión (Sprint 4 sesión 1)
