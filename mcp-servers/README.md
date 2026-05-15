# mcp-servers/

> **Nivel 3: validators y tools automatizados** | MCP servers del Departamento

Esta carpeta contiene los MCP (Model Context Protocol) servers construidos
por el Departamento. Son **validators y tools agnósticos de proyecto** que
Claude Code (u otro agente) consume para automatizar verificación,
validación, y operaciones recurrentes.

## Filosofía

Los MCP servers acá implementan la **subsystem Verification** del harness
según Harness Engineering. Materializan las reglas universales de
arquitectura (Nivel 2) y técnicas universales (Nivel 3) como código
ejecutable.

**Principio clave (DIP)**: cada MCP server es agnóstico de cliente.
Recibe configuración desde `domain-captures/` (Nivel 4) en runtime.
NUNCA hardcodea nombres de tablas, helpers, o detalles específicos
de un cliente.

## Servers planeados

### sigma-validators-r/ (Sprint 2 T2)

Validators SQL universales destilados de las 170+ reglas del legacy
SigmaControl. Tools segregadas según ISP:

```
validate_sql_invariants(sql, rollback, config)
validate_sql_performance(sql)
validate_sql_security(sql, config)
validate_sql_concurrency(sql)
validate_sql_adversarial(sql, config)
validate_sql_scale(sql, escala_operativa)
split_sql(sql)
```

Origen: `modo/programacion/reglas/` del legacy (~140 KB de código probado).
Destilación documentada en ADR-006.

### sigma-close-session-validator/ (Sprint 2 T3)

Validator de cierre de sesión. Verifica que al cerrar una sesión:
- El estado quedó consistente
- Los handoffs están completos
- No hay deuda silenciosa
- El próximo agente puede retomar sin contexto perdido

Origen: `herramientas/ritual.py` del legacy + Lecture 12 de Harness Engineering
("Why every session must leave a clean state").

## Estructura de cada server

Cada MCP server sigue esta estructura:

```
mcp-servers/<server-name>/
├── README.md                  ← Descripción + tools expuestas
├── SCHEMA.md                  ← JSON schema de cada tool (input/output)
├── pyproject.toml             ← Dependencias (si Python)
├── package.json               ← Dependencias (si TypeScript)
├── src/
│   ├── server.py              ← Entry point del MCP server
│   ├── tools/                 ← Implementación de cada tool
│   │   ├── tool_X.py
│   │   └── tool_Y.py
│   └── config/                ← Tipos/schemas de configuración
│       └── domain_config.py
└── tests/
    ├── test_tool_X.py
    └── adversarial/            ← Tests adversariales (stress)
        └── attack_patterns.py
```

## Cómo se consume un server

Desde Claude Code, los MCP servers se configuran en `.mcp.json` o equivalente:

```json
{
  "mcpServers": {
    "sigma-validators-r": {
      "command": "python",
      "args": ["mcp-servers/sigma-validators-r/src/server.py"],
      "env": {
        "DOMAIN_CONFIG_PATH": "domain-captures/stallen-domain.md"
      }
    }
  }
}
```

El server lee `DOMAIN_CONFIG_PATH` en startup y carga la configuración.
Las tools usan esa config en runtime.

## Reglas para crear/modificar un server (C4)

Aplicar regla C4 de `architecture/PATRONES-CARPETAS.md`:

```
NO permitido en mcp-servers/:
  ❌ Hardcoded "inventory_movements_sc" u otros nombres de Stallen
  ❌ Decisiones de momento específicas (van a ADRs)
  ❌ Documentación general del Departamento (va a docs/)

SI permitido en mcp-servers/:
  ✅ Código Python/TypeScript de cada server
  ✅ Tests con datos sintéticos (no Stallen real)
  ✅ Schemas de tools
  ✅ Tipos/interfaces de configuración
```

## SOLID compliance check

Antes de hacer commit de un MCP server nuevo, verificar:

- [ ] **SRP**: el server tiene UNA categoría de responsabilidad clara
- [ ] **OCP**: agregar tool nueva NO requiere modificar tools existentes
- [ ] **LSP**: todas las tools retornan estructuras consistentes
- [ ] **ISP**: tools segregadas (no una "do_everything" monolítica)
- [ ] **DIP**: configuración recibida en runtime, NO hardcoded

## Anti-patterns conocidos a evitar

Ver `architecture/ANTI-PATRONES.md`, especialmente:

- **AP-2.1 God Validator** — un validator monolítico que valida todo
- **AP-2.2 Hardcoded Domain** — strings de Stallen en código universal
- **AP-2.3 Inconsistent Returns** — tools con tipos de return distintos

## Estado actual

```
✅ Estructura definida (este README)
⬜ sigma-validators-r/ — Sprint 2 T2
⬜ sigma-close-session-validator/ — Sprint 2 T3
```

## Roadmap

```
Sprint 2 D3-D7:  sigma-validators-r/ implementación
Sprint 2 D8-D10: sigma-close-session-validator/ implementación
Sprint 3:        CI/CD para validar los servers automáticamente
Sprint 4:        Observabilidad de los servers (métricas por tool)
Sprint 5:        Release process formal para versiones de servers
```

---

Versión: 1.0 | Creado: 2026-05-15
Referencias: ADR-006, architecture/PRINCIPIOS-ARQUITECTURA.md, architecture/PATRONES-CARPETAS.md
