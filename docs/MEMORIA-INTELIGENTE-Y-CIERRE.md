# MEMORIA INTELIGENTE Y OPTIMIZACIÓN DEL PROTOCOLO DE CIERRE

> Documento de arquitectura: cómo Engram + MCP server especializado transforman el protocolo de cierre de sesión de un proceso pesado (15-30k tokens, 10-20 min) a uno eficiente (3-7k tokens, 5-10 min) sin sacrificar disciplina.

**Estado**: Decisión arquitectónica formalizada
**Construcción**: Sprint 2
**Referencias**: `DEPARTAMENTO-DE-SOFTWARE.md` secciones 4-6, `SISTEMA-DE-TRABAJO.md` sección Protocolo de Cierre

---

## 1. PROBLEMA DIAGNOSTICADO

El protocolo de cierre actual (12 pasos extendidos con 7.5, 7.6, 8.5, 12) es disciplinado pero costoso en recursos. Identificadas 5 ineficiencias específicas:

### 1.1 Re-lectura completa de archivos en cada paso

Para el paso 7.5 (radar polinización), Claude debe cargar:
- `CATALOGO-METAPATRONES-DOLOR.md` completo (~5-10k tokens)
- `sesion-activa.md` actual (~2-3k tokens)
- Posiblemente `DEUDA-TECNICA.md` (~3-5k tokens)
- Posiblemente `CUADERNO-BITACORA.md`

Solo para responder "¿este patrón ya existe?" se cargan 10-20k tokens en context window.

### 1.2 Re-cálculo de estado en cada paso

No hay estado intermedio del cierre persistido. El paso 12 (audit final) debe reconstruir mentalmente qué se hizo en cada paso anterior. Costo cognitivo y de tokens alto, propenso a error humano.

### 1.3 Búsqueda secuencial vs indexada

Para verificar existencia de meta-patrón, lectura linear del catálogo. Si hoy hay 7 patrones, en 6 meses puede haber 30+. La lectura escala mal.

### 1.4 Auditoría manual del propio protocolo

El paso 12 enumera pasos uno por uno verificando cumplimiento. Es trabajo intelectual que puede programarse.

### 1.5 Sin deduplicación automática

Si en sesión A documentás patrón X como "deps transitivas SQL" y en sesión B describís lo mismo como "dependencias indirectas backend", hoy no hay detección automática de equivalencia semántica.

### Costo total actual por cierre (estimado)

| Recurso | Valor |
|---|---|
| Tokens consumidos | 15-30k |
| Tiempo | 10-20 min |
| Costo monetario (Opus) | $0.40-0.80 |
| Esfuerzo cognitivo Claude | Alto (mucha re-lectura) |

---

## 2. SOLUCIÓN: 6 PATRONES DE OPTIMIZACIÓN CON MEMORIA INTELIGENTE

### Patrón 1: Búsqueda instantánea vs lectura completa

**ANTES (paso 7.5 radar polinización)**:
- Claude lee CATALOGO-METAPATRONES-DOLOR.md (5-10k tokens)
- Lee sesion-activa.md (2-3k tokens)
- Compara mentalmente "este patrón vs los N del catálogo"
- Decide si existe match

Costo: ~10k tokens.

**DESPUÉS (con Engram)**:
- Claude llama `mem_search "deps transitivas SQL backend"`
- Engram retorna en ms: 1-3 candidatos con relevance score
- Si match: agregar nueva manifestación al patrón existente
- Si no match: crear meta-patrón nuevo

Costo: ~500 tokens. **Ahorro: 95%.**

### Patrón 2: Estado intermedio persistente del cierre

Crear "session-close-state" en Engram al iniciar cierre:

```json
{
  "session_id": "2026-05-13-001",
  "started_at": "2026-05-13T23:30:00-05:00",
  "steps": {
    "1_documentar": {"status": "done", "artifact": "sesion-activa.md", "ts": "..."},
    "2_siguiente": {"status": "done", "artifact": "SIGUIENTE-SESION.md"},
    "3_docs": {"status": "done", "artifacts": ["doc1.md", "doc2.md"]},
    "4_indices": {"status": "done"},
    "5_memoria_claude": {"status": "done"},
    "6_consistencia": {"status": "done"},
    "7_deuda": {"status": "done", "items_added": 3},
    "7_5_polinizacion": {"status": "pending"},
    "7_6_audit_empirico": {"status": "pending"},
    "8_contador_periodica": {"status": "pending"},
    "8_5_cleanup": {"status": "pending"},
    "9_git_backup": {"status": "pending"},
    "10_reflexion": {"status": "pending"},
    "11_archivar_norte": {"status": "n/a"},
    "12_audit_final": {"status": "pending"}
  }
}
```

Cada paso actualiza el state via tool call. Audit final (paso 12) **lee el state, no re-evalúa**. Costo del paso 12: ~100 tokens vs ~3k actualmente.

### Patrón 3: Deduplicación automática

Engram automáticamente escanea observaciones similares usando FTS5 al guardar. Si encuentra candidatos sobre threshold, marca `judgment_required: true`.

Aplicado al cierre:
- Documentás patrón "deps transitivas SQL"
- Engram detecta que ya existe "dependencias indirectas backend"
- Te pregunta: "¿es el mismo o es nuevo?"
- Imposible duplicar accidentalmente meta-patrones

### Patrón 4: Auditoría programática vs manual

El paso 12 hoy es manual (Claude enumera y verifica). Después: el MCP server `sigma-close-session-validator` ejecuta verificación automática:

```python
# Retorna en ms
{
  "ok": false,
  "completed": 11,
  "gaps": ["paso_7_5_polinizacion"],
  "diferred": [],
  "summary": "11 OK, 1 GAP - radar polinización no documentado",
  "next_action": "ejecutar mem_search + categorizar antes de finalizar"
}
```

Claude lee el resultado y decide qué hacer. **No re-evalúa los 12 pasos uno por uno.**

### Patrón 5: Pre-compute de polinización candidata

Engram con metadata estructurada por meta-patrón:

```json
{
  "id": "meta_pattern_07",
  "name": "Deps transitivas no declaradas",
  "manifestations": ["P1 G11A", "P0 R15"],
  "coverage": {
    "P1": true,
    "P0": true,
    "frontend": false,
    "domain": false,
    "audit": false
  },
  "polinization_history": [
    {"date": "2026-03-15", "from": "P1", "to": "P0", "result": "applied"}
  ]
}
```

Cuando descubrís nueva manifestación, sistema **sugiere automáticamente** las polinizaciones candidatas:
- "Este patrón en frontend NO está cubierto → evaluar polinización"
- "Este patrón en audit NO está cubierto → evaluar polinización"

No hay que pensarlo cada vez.

### Patrón 6: Compactación con TTL implícito

Engram tiene topic upserts, soft-deletes, exact deduplication.

Aplicado al cierre:
- `sesion-activa.md` no crece sin control: upsert por `session_id`
- Entries viejos se "envejecen" en ranking FTS5 (relevance score baja)
- Lo viejo no contamina lo nuevo
- Soft-delete con archivado para auditoría histórica

---

## 3. DISEÑO: MCP SERVER `sigma-close-session-validator`

### Tools que expone

```python
# Inicia el cierre, retorna checklist con estado actual
close_start(session_id: str) -> CloseState:
    """
    Crea registro en Engram para esta sesión.
    Retorna checklist de 12 pasos con status inicial pending.
    """

# Marca un paso como ejecutado
close_record_step(
    step_id: str,
    status: Literal["done", "gap", "diferred"],
    artifact_path: str | None = None,
    notes: str | None = None
) -> StepResult:
    """
    Actualiza el state del cierre.
    Si status=gap o diferred, requiere notes explicando.
    """

# Búsqueda de patrón en catálogo (usa Engram internamente)
close_polinization_check(
    pattern_description: str,
    new_manifestation: str
) -> Candidates:
    """
    Llama a Engram mem_search para encontrar meta-patrones similares.
    Retorna candidates con relevance score + coverage matrix.
    Sugiere polinizaciones candidatas no cubiertas.
    """

# Verifica que limpieza declarada coincide con disco (paso 8.5)
close_verify_cleanup() -> CleanupReport:
    """
    Lee del state los archivos declarados como movidos/archivados.
    Verifica con filesystem que están en estado correcto.
    Retorna divergencias si existen.
    """

# Retorna estado actual del cierre
close_audit_status() -> AuditReport:
    """
    Lee state completo del cierre desde Engram.
    Retorna {ok, completed, gaps, diferred, summary}.
    """

# Ejecuta git add -A + commit + push (paso 9)
close_git_backup(commit_message: str) -> GitResult:
    """
    Ejecuta git add -A, commit, push.
    Captura outputs. Retorna éxito o error.
    Si push falla, no marca el paso como done.
    """

# Verifica que todos los pasos están done o diferred con razón
close_finalize() -> FinalReport:
    """
    Verifica que NO hay pasos pending sin justificar.
    Si todo OK: declara cierre formal, archiva state.
    Si hay gaps: rechaza cierre con motivo específico.
    """
```

### Flujo del cierre con esto

```
1. Claude invoca close_start(session_id) → state inicializado en Engram

2. Para cada paso 1-11:
   - Claude hace el trabajo intelectual (escribir docs, decidir, evaluar)
   - Llama close_record_step() con resultado

3. Para paso 7.5: close_polinization_check() automatiza la búsqueda
   - Retorna candidates + coverage gaps
   - Claude decide qué hacer con cada polinización candidata

4. Para paso 8.5: close_verify_cleanup() verifica disco automáticamente
   - Compara declaración del cierre vs estado real del filesystem
   - Reporta divergencias

5. Para paso 9: close_git_backup(message) ejecuta git operations completas

6. Para paso 12: close_audit_status() retorna estado completo
   - Si todo done: paso 12 done
   - Si hay gaps: paso 12 reporta gaps específicos para resolver

7. Si todo OK: close_finalize() declara cierre formal
   - Si NO ok: cierre rechazado, debe resolverse antes de finalizar
```

### Aplicación directa del 2° Principio Rector

**"Capa correctiva: si algo se omite, el sistema lo detecta y corrige."**

Hoy podés cerrar sin polinización si te olvidás. Con MCP server, `close_finalize()` rechaza el cierre si paso 7.5 está pending sin justificación documentada. La disciplina queda enforced por código, no por memoria.

---

## 4. BENEFICIOS CUANTIFICADOS

### Antes / Después

| Métrica | Antes | Después | Mejora |
|---|---|---|---|
| Tokens por cierre | 15-30k | 3-7k | **60-80% menos** |
| Tiempo del cierre | 10-20 min | 5-10 min | **50% menos** |
| Costo monetario por cierre (Opus) | $0.40-0.80 | $0.10-0.20 | **70% menos** |
| Riesgo duplicar meta-patrones | Alto (manual) | ~0 (Engram detecta) | Eliminado |
| Riesgo skip silencioso de paso | Medio | Bajo | Capa correctiva |
| Trazabilidad del cierre | Manual | Automática auditable | Mejorado |
| Onboarding (yo en 6 meses) | Lees logs manualmente | mem_search directo | 10x más rápido |
| Detección polinización candidata | Manual | Sugerida automáticamente | Ahorro cognitivo |

### Retorno de inversión

**Inversión** (Sprint 2): 1-2 días para construir el MCP server.

**Ahorro mensual** (estimando 20 cierres/mes):
- Tokens ahorrados: ~400k tokens/mes
- Tiempo ahorrado: ~3-4 horas/mes
- Costo $ Claude API ahorrado: $5-10/mes (tarifas Opus)

**Payback**: ~2-3 meses en tiempo + costo. Después, ganancia neta indefinida.

### Beneficios cualitativos no medibles

1. **El protocolo se vuelve gate-able**: hoy podés cerrar sin polinización. Con MCP server, imposible.
2. **Auto-evidencia recursiva**: el sistema captura su propio uso. Podés preguntar "¿qué pasos se difieren más?" y aprendés del protocolo.
3. **Memoria como ground truth**: mem_search te dice cuándo descubriste un meta-patrón, con contexto.
4. **Polinización proactiva**: alerta sobre gaps de cobertura antes de finalizar la sesión.

---

## 5. LO QUE NO CAMBIA

Importante para preservar disciplina:

- **Los 12 pasos siguen siendo 12 pasos**. La automatización es del plumbing, no del razonamiento.
- **El trabajo intelectual sigue siendo humano + Claude**: decidir qué documentar, cómo categorizar, qué polinizaciones implementar.
- **Markdown humano sigue vivo**: `DEUDA-TECNICA.md`, `CUADERNO-BITACORA.md`, los 3 documentos fundacionales siguen siendo markdown leíbles. Engram complementa, no reemplaza.
- **Disciplina enforced, no relajada**: gate-able significa MÁS estricto, no menos.

---

## 6. ARQUITECTURA HÍBRIDA RESULTANTE

| Tipo de contenido | Storage | Por qué |
|---|---|---|
| Memoria operativa LLM (bugs, decisiones, patrones) | **Engram** | Retrieval rápido, conflict detection automático |
| Estado de cierre en progreso | **Engram** | Persistencia + audit programático |
| Catálogo meta-patrones (índice + metadata) | **Engram** | Búsqueda + coverage matrix |
| Catálogo meta-patrones (narrativa completa) | **Markdown** | Lectura humana |
| 3 documentos fundacionales del Departamento | **Markdown** | Constitución, lectura humana |
| CUADERNO-BITACORA (notas en prosa) | **Markdown** | Escritura libre |
| DEUDA-TECNICA (backlog visible) | **Markdown** | Lectura humana, edición frecuente |
| ADRs (decisiones técnicas) | **Híbrido**: índice en Engram, contenido en markdown | Búsqueda + lectura |

**Patrón**: lo que un LLM consulta frecuentemente → Engram. Lo que un humano lee/edita → Markdown.

---

## 7. IMPLICACIÓN PARA EL ROADMAP

Esto cabe naturalmente en **Sprint 2** sin alterar el plan:

| Sprint 2 task original | Refinamiento con este análisis |
|---|---|
| Migrar validadores R/G/FG a MCP | Sin cambio |
| Migrar patcher a MCP | Sin cambio |
| Migrar capturar_adn a skill | Sin cambio |
| Migrar protocolo cierre a skill | **Skill + MCP server `sigma-close-session-validator` con Engram backend** |
| Setup Engram | **Prioridad alta: todo lo demás se beneficia** |

### Pre-requisitos para construcción

1. Engram instalado y configurado (Sprint 1 Días 7-8)
2. MCP integrado con Claude Code (Sprint 1 Día 10)
3. Convención de tipos de memoria definida (`bugfix`, `decision`, `pattern`, `polinization`, `debt`, `incident`, `session_close_state`)
4. Schema del state de cierre formalizado (Sprint 2 Día 1)
5. Tools del MCP server implementados (Sprint 2 Días 2-3)
6. Skill `cerrar-sesion` actualizado para usar el MCP server (Sprint 2 Día 4)
7. Validación empírica: ejecutar 3-5 cierres reales con el sistema nuevo, medir tokens vs anterior (Sprint 2 Día 5)

### Métrica de éxito Sprint 2

Sistema considerado validado cuando:
- 3 cierres consecutivos completos sin intervención manual extra
- Reducción de tokens promedio ≥ 50% vs baseline anterior
- Cero meta-patrones duplicados detectados post-hoc
- 100% de gaps detectados automáticamente por `close_audit_status`

---

## 8. DECISIONES ARQUITECTÓNICAS ASOCIADAS (ADRs)

Estas decisiones se formalizarán en `decisions/` cuando se cree el directorio:

### ADR-001: Adopción de Engram para memoria operativa de agentes

**Status**: Decidido
**Fecha**: 2026-05-13
**Decisión**: Adoptar Engram como sistema de memoria operativa para agentes Claude.
**Justificación**: Búsqueda full-text indexada, retrieval progresivo, conflict detection automático, MCP nativo, agent-agnostic, sin dependencias externas (1 binary Go + SQLite).
**Alternativas consideradas**: Construir sistema propio (descartado: mantenimiento + paridad), vector DB (descartado: ver ADR-002).
**Criterios de revisión**: Re-evaluar si volumen de memoria supera 100k entradas o aparecen casos de uso que requieran matching semántico no resoluble con FTS5 + tags.

### ADR-002: Rechazo de vectorización para memoria institucional

**Status**: Decidido
**Fecha**: 2026-05-13
**Decisión**: NO usar vector databases (Chroma, Pinecone, Weaviate, etc.) para memoria del Departamento.
**Justificación**:
- Filosofía Engram explícita: FTS5 cubre 95% de use cases
- Schema estructurado (tipo, tags, project) elimina necesidad de semantic search
- Costo computacional + monetario de embeddings injustificable para volumen proyectado (~1k-10k entradas en 5 años)
- Privacy: vectores requieren proveedor externo, FTS5 es 100% local
- Determinismo: FTS5 es reproducible, embeddings tienen drift entre versiones de modelo
**Alternativas consideradas**: Chroma, Pinecone, Qdrant, Weaviate.
**Criterios de revisión**: Re-evaluar si:
- Volumen supera 100k entradas heterogéneas
- Aparecen búsquedas semánticas genuinas no resolubles con keywords + tags
- Multi-modal (texto + imágenes + código) se vuelve necesario
- Equipo crece y se requiere búsqueda en lenguaje natural por humanos sin vocabulario técnico

### ADR-003: MCP server `sigma-close-session-validator` para protocolo de cierre

**Status**: Diseñado, pendiente de implementación Sprint 2
**Fecha**: 2026-05-13
**Decisión**: Construir MCP server especializado que automatice plumbing del protocolo de cierre, manteniendo razonamiento humano + Claude en cada paso.
**Justificación**: 60-80% reducción de tokens, 50% reducción de tiempo, eliminación de duplicados accidentales, audit programático del propio protocolo, aplicación directa del 2° principio rector (capa correctiva).
**Alternativas consideradas**: Mantener protocolo manual (descartado: ineficiente y propenso a skip silencioso), skill-only sin MCP (descartado: skills no pueden ejecutar lógica programática compleja como audit del estado).

---

## 9. REFERENCIAS

- `DEPARTAMENTO-DE-SOFTWARE.md` sección 4: Stack tecnológico (Engram en stack)
- `DEPARTAMENTO-DE-SOFTWARE.md` sección 5: Arquitectura técnica (MCP servers)
- `DEPARTAMENTO-DE-SOFTWARE.md` sección 8.2 punto 5: Observabilidad (incluye logs estructurados del MCP server)
- `PROTOCOLO-CONSTRUCCION-CODIGO.md` regla R-3: Disciplina como ley
- `SISTEMA-DE-TRABAJO.md`: Protocolo de cierre actual (12 pasos)
- Engram official: https://github.com/Gentleman-Programming/engram
- Engram DOCS: https://github.com/Gentleman-Programming/engram/blob/main/DOCS.md

---

**Última actualización**: 2026-05-13
**Próxima revisión**: Post-Sprint 2 (validación empírica del MCP server)
