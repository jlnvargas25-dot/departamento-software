# Architecture Decision Records (ADRs)

Este directorio contiene las decisiones arquitectónicas formales del Departamento de Software.

## Qué es un ADR

Un Architecture Decision Record (ADR) documenta una decisión técnica importante: el contexto, las alternativas consideradas, la decisión tomada, y las consecuencias esperadas.

## Cuándo crear un ADR

Crear ADR cuando:
- La decisión afecta arquitectura del sistema
- Hay alternativas reales que se descartaron
- Tu yo del futuro (o un colaborador) podría preguntarse "¿por qué se hizo así?"
- La decisión tiene costo significativo de revertir
- La decisión tiene impacto cross-módulo

NO crear ADR para:
- Decisiones de implementación local (qué nombre dar a una variable)
- Refactors triviales
- Bugfixes

## Formato

Cada ADR sigue esta estructura mínima:

```markdown
# ADR-NNN: Título descriptivo

**Status**: Decidido | Pendiente | Superado | Deprecated
**Fecha**: YYYY-MM-DD
**Decisor**: Nombre

## Contexto
[Qué situación motivó esta decisión]

## Decisión
[Qué se decidió hacer]

## Alternativas consideradas
[Qué se evaluó y por qué se descartó]

## Consecuencias
[Positivas, negativas, mitigaciones]

## Criterios de revisión
[Cuándo re-evaluar esta decisión]

## Referencias
[Links a docs relacionados]
```

## Numeración

Los ADRs son numerados secuencialmente y nunca se renumeran. Si un ADR queda superado, se marca como `Status: Superado por ADR-XXX` y se mantiene en el repo como evidencia histórica.

## Índice de ADRs

### Activos

- **ADR-001**: Adopción de Engram para memoria operativa de agentes
  *(formalizado en `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md` § 8)*

- **ADR-002**: Rechazo de vectorización para memoria institucional
  *(formalizado en `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md` § 8)*

- **ADR-003**: MCP server `sigma-close-session-validator` para protocolo de cierre
  *(formalizado en `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md` § 8)*

- **ADR-004**: Calibración del Nivel Comercial del Departamento
  *([`ADR-004-calibracion-nivel-comercial.md`](ADR-004-calibracion-nivel-comercial.md))*

### Superados

*(ninguno todavía)*

## Convención de nombres

`ADR-NNN-titulo-descriptivo-en-kebab-case.md`

Ejemplo: `ADR-004-calibracion-nivel-comercial.md`

## Migración pendiente

Los ADRs 001, 002, 003 están actualmente documentados dentro de `docs/MEMORIA-INTELIGENTE-Y-CIERRE.md` sección 8. Migración a archivos individuales en este directorio: deuda técnica para Sprint 2 (Tarea: extraer ADRs 001-003 a archivos individuales y dejar referencias cruzadas).
