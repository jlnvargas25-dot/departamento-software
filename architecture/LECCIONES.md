# LECCIONES — Registry formal del Framework Departamento

> **Propósito**: índice canónico de **lecciones N=2+** del Framework. Lecciones
> N=1 viven en `auditoria/sesion-activa.md` como candidatas; cuando alcanzan
> N=2 confirmaciones empíricas se promueven acá.

---

## Criterios de promoción (workflow de evidencia)

```
N=1 candidata     →  auditoria/sesion-activa.md (addendum sesión)
N=2 confirmada    →  architecture/LECCIONES.md (este archivo, formal)
N=3+ estructural  →  architecture/PRINCIPIOS-ARQUITECTURA.md (regla A26+) ó
                      architecture/ANTI-PATRONES.md (AP-3.NN+)
```

### Definiciones

- **N=1 candidata**: patrón observado UNA vez. Documentado en sesión activa
  como hipótesis viable. NO se promueve a Framework formal hasta segundo evento.
- **N=2 formal**: patrón confirmado en DOS eventos empíricos distintos (commits,
  sprints, proyectos). Se promueve a este archivo como **LECCIÓN formal**.
  El sistema puede asumirla operacionalmente y referenciarla desde otros docs.
- **N=3+ estructural**: patrón confirmado en 3+ eventos, donde 2+ son
  proyectos/contextos distintos. Califica para integración al Nivel 2
  (PRINCIPIOS-ARQUITECTURA si establece regla universal, ANTI-PATRONES si
  identifica error universal a evitar).

### Distinción con A-rules y anti-patterns

| Artefacto | Origen | Granularidad | Inmutabilidad |
|-----------|--------|--------------|---------------|
| **Lección** (este archivo) | Observación empírica N=2 sobre proceso/herramienta | Específica al contexto operativo | Puede evolucionar con más evidencia |
| **Regla A* universal** (PRINCIPIOS-ARQUITECTURA) | Patrón estructural N=3+ proyectos | Universal cross-proyecto | Inmutabilidad relativa (raramente cambia) |
| **Anti-pattern** (ANTI-PATRONES) | Error recurrente N=3+ con evidencia | Universal cross-proyecto | Inmutabilidad relativa |

Una lección puede **graduar** a regla A* o anti-pattern cuando alcanza N=3+
estructural. La graduación se documenta en ADR del Nivel 5 que justifique el
ascenso al Nivel 2.

---

## Registry de lecciones N=2+

### LECCIÓN 38 — PROTOCOLO + audit Paso 5 elimina loop GGA asintótico (2026-05-22)

**Enunciado**: *Código que sigue PROTOCOLO-CONSTRUCCION-CODIGO (pasos 1-5
estrictos) + audit Paso 5 (R01-R15) sobre el plan PASA GGA en 1 round, sin
bypass humano. En contraposición a 4 rounds + bypass humano (`--no-verify`)
cuando se construye sin auditar el plan previamente.*

**Estado**: ✅ **N=5 CONFIRMADA** (promovida a LECCIÓN formal 2026-05-22 con N=2; N=3 ses 4; N=4 ses 5; N=5 ses 6).

**Evidencia empírica**:

| Evento | Commit/Sprint | GGA rounds | Bypass | PROTOCOLO+audit Paso 5 previo |
|--------|---------------|-----------|--------|-------------------------------|
| Sprint 1 Iteración 3 (baseline contraejemplo) | varios | 4 + asintotizó | ✅ `--no-verify` | ❌ No |
| Sprint 3 sesión 1 — N=1 | `06493bc` (S-1..S-3 classifier) | 1 | ❌ Ninguno | ✅ Sí |
| Sprint 3 sesión 2 — N=2 | `2322e4a` (S-4..S-8 classifier) | 1 | ❌ Ninguno | ✅ Sí |
| Sprint 3 sesión 4 — N=3 | `3701463` (S-1..S-5 mechanic core, 90 tests) | 1 | ❌ Ninguno | ✅ Sí |
| Sprint 3 sesión 5 — N=4 | `797772f` (S-6..S-8 mechanic E2E, 181 tests, R08 cerrada) | 1 | ❌ Ninguno | ✅ Sí |
| Sprint 3 sesión 6 — N=5 | `d35c3f0` (Audit Paso 7+8 PASS + polish 3 advisories, 194 tests) | 1 | ❌ Ninguno | ✅ Sí (audit consolidado) |
| Sprint 4 sesión 1 — **CONTRAEJEMPLO** | `05148e1` (correction-agent-bounded, LLM dep) | 5 + scope bypass | ✅ `FRAMEWORK_SCOPE=sandbox` | ✅ Sí | 

**Boundary condition (L42)**: L38 holds for 100% deterministic Python code but NOT for components with LLM SDK dependencies. See L42 below.

**Importancia para el Framework**: primera lección que cierra empíricamente
el ciclo **PREVENTIVA → VERIFICABLE** (2° principio rector). Demuestra que la
capa preventiva (auditar el plan con R01-R15 antes de construir) reduce
estructuralmente el costo de la capa verifiable (GGA + reviewers adversariales).

**Operacionalización**:
- El PROTOCOLO-CONSTRUCCION-CODIGO debe ejecutarse estrictamente (pasos 1-5
  obligatorios antes de Paso 6 build).
- Audit Paso 5 (R01-R15) sobre el plan completo (PRD + dominio + arquitectura
  + stories) NO ES OPCIONAL — saltearlo invalida la evidencia de L38.
- Para nuevas construcciones: validar pre-flight que auditoría del plan está
  hecha. Si falta, ejecutar antes de iniciar Paso 6.

**Cross-references**:
- `decisions/ADR-011-capa-correctiva-y-scope-aware.md` v1.0 ACCEPTED (sección
  "Phase 2 BUILD + AUDITS completos") — evidencia consolidada classifier + mechanic.
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` pasos 1-5 — el procedimiento que L38
  valida empíricamente.
- `auditoria/audit-code-classifier-2026-05-22.json` — audit Paso 7 sobre
  código que pasó GGA en 1 round (consistente con L38).
- LECCIÓN 35 candidata (N=1): inversa estructural — *"reviewer adversarial sin
  auto-fix + sin scope-awareness asintotiza al infinito"*. L38 confirma que el
  bypass humano del baseline NO era necesario si el plan estaba auditado.

**Próxima validación esperada**: N≥1 sobre proyecto DISTINTO al Framework
Departamento (ej. Stallen). L38 actualmente tiene N=3 sobre commits del MISMO
proyecto — esto valida la lección en el contexto operativo del Framework pero
NO califica para graduación a regla A26 universal según `architecture/README.md`
("aparece un nuevo patrón estructural validado por 3+ proyectos"). Para
A26 universal: replicar workflow PROTOCOLO + audit Paso 5 en Stallen (o tercer
proyecto) y verificar mismo comportamiento (GGA 1 round). Si se cumple,
graduar a A26 con ADR de promoción.

**Nota interpretativa N=3 (2026-05-24)**: el resultado consistente sobre
3 componentes del Framework (classifier S-1..S-3, classifier S-4..S-8,
mechanic S-1..S-5) con scopes y stacks distintos (loader + classify + CLI +
fixture-based testing vs orchestrator + snapshot + subprocess wrapper +
verifier dispatcher) sugiere robustez del patrón cross-component dentro del
proyecto. La validación cross-proyecto sigue siendo el siguiente hito formal.

**Falsabilidad**: L38 quedaría refutada si un futuro código que pasa PROTOCOLO
+ audit Paso 5 estricto NO pasa GGA en 1 round. En ese caso bajar a candidata
N=1 nuevamente y revisar covariantes (cambios en GGA, en reviewer, en el
caso de prueba).

---

## Lecciones N=1 vigentes (candidatas, esperando N=2)

Las siguientes lecciones están documentadas en `auditoria/sesion-activa.md` y
ADRs cross-referenciados como candidatas N=1. Cuando alcancen N=2 se promueven
a este archivo.

| ID | Enunciado breve | Origen | ADR/sesión referenciada |
|----|-----------------|--------|--------------------------|
| L35 | reviewer adversarial sin auto-fix + sin scope-awareness asintotiza al infinito | Sprint 2 sesión 1 cierre | ADR-011 §Conexiones |
| L36 | calibración de scope antes que capa correctiva — scope es cura barata, correctiva es cura cara | Sprint 2 sesión 1 cierre | ADR-011 §Conexiones |
| L37 | scope awareness y capa correctiva son ortogonales y complementarias — el orden importa | Sprint 2 sesión 1 cierre | ADR-011 §Conexiones |
| L42 | LLM-dependent components require scope-aware bypass; GGA review surface exceeds convergence for novel SDK integrations | Sprint 4 sesión 1 (5 rounds + scope bypass) | ADR-011 v1.1, L38 boundary |
| L41 | commit-per-session en builds multi-story produce history limpio y permite GGA verify por sesión | Sprint 3 ses 4-6 | Radar polinización Sprint 3 |
| L40 | cross-reference testing evita duplicación adversarial sin perder cobertura | Sprint 3 ses 6 | Radar polinización Sprint 3 |
| L39 | audit manual que consolida evidencia GGA previo reduce esfuerzo y mejora trazabilidad | Sprint 3 ses 6 | Radar polinización Sprint 3 |
| L34 | convenciones del operador instruidas en el prompt del sub-agent son sticky, no requieren skill structural inicialmente | Sprint 1 Iteración 3 cierre | ADR-009 |
| L33 | sub-agent scope ideal <15 files modificados | Sprint 1 Iteración 3 cierre | ADR-009 |
| L32 | Server Actions vs REST en App Router crea fricción adversarial | Sprint 1 Iteración 3 cierre | ADR-009 |
| L31 | A-rule coverage real matchea cobertura a-priori instruida | Sprint 1 Iteración 3 cierre | ADR-009 |
| L30 | sub-agent token budget proyectable (~75-100k por sub-agent fresh, multi-file 30-50 tool uses) | Sprint 1 Iteración 3 cierre | ADR-009 |
| L29 | cost hook quirúrgicamente desactivable vía ECC_CONTEXT_MONITOR_COST_WARNINGS=0 | Sprint 1 Iteración 3 cierre | ADR-009 |
| L24-L28 | sdd-* vs speckit-* comparación empírica (convergencia 47 tasks, speed vs depth, sub-agent tools mismatch, skill override orchestrator, capability decomposition) | T1.9 EMPIRICAL | ADR-009 T1.9 addendum |
| L22-L23 | Manual injection point Constitution Check; matriz a-priori vs ejecutable diverge AL ALZA con operador instruido | T1.7 + T1.8 | ADR-009 |
| L16-L21 | Cascada aceptación instances, edit_file array no atómico, cross-LLM publishing canónico, extraKnownMarketplaces, flags rotan rápido, matriz a-priori vs ejecutable | Sesiones 2026-05-20/21 | ADR-009, sesion-activa addendums |

Lecciones L1-L15 son históricas del meta-producto SigmaControl legacy; viven
en `C:\Users\Windows 11\sigmacontrol-camino-1\` (proyecto pausado). Reaparecerán
acá si se promueven al Framework.

---

## Cómo agregar una lección nueva a este archivo

1. Verificar que cumple N=2 documentado en `auditoria/sesion-activa.md` con
   dos eventos empíricos distintos y trazables (commits, sprints, fixtures).
2. Agregar entry siguiendo el formato de L38 más arriba:
   - Enunciado claro y falsable
   - Estado y fecha de promoción
   - Tabla de evidencia empírica (mínimo N=2 eventos)
   - Importancia para el Framework
   - Operacionalización (cómo aplica)
   - Cross-references a ADRs / archivos relacionados
   - Próxima validación esperada (N=3 condition)
   - Falsabilidad
3. Si la lección refuta o supersede a otra lección/regla, documentarlo.
4. Cross-reference desde el ADR del cierre de sesión que motiva la promoción.
5. Mover la lección de "N=1 candidatas" en sesion-activa a "promovidas a
   LECCIONES.md" con la fecha del cierre.

---

Creado: 2026-05-22 (Sprint 3 sesión 3 BLOQUE 1.2 — primera promoción formal con L38)
Versión: 1.0
Próxima revisión: cuando una segunda lección alcance N=2 o cuando L38 alcance N=3 para graduar a A26.
