# PATRONES DE CARPETAS

> **Nivel 2: arquitectura universal** | Estructura de directorios + reglas C1-C6
> Versión: 1.0 | Creado: 2026-05-15

---

## Estructura completa del Departamento

```
C:\DEPARTAMENTO-SOFTWARE\
│
├── 📄 CLAUDE.md                       ← Nivel 1: principios filosóficos (system prompt)
├── 📄 AGENTS.md                       ← Nivel 1: instructions root para agentes
├── 📄 README.md                       ← Punto de entrada para humanos
├── 📄 DEPARTAMENTO-DE-SOFTWARE.md     ← Diseño general del sistema
├── 📄 SISTEMA-DE-TRABAJO.md           ← Manual operativo
├── 📄 PROTOCOLO-CONSTRUCCION-CODIGO.md ← Protocolo de construcción
├── 📄 .gga                            ← Config de Gentle AI (GGA pre-commit)
├── 📄 .gitignore
│
├── 📁 architecture/                   ← Nivel 2: arquitectura universal ⭐
│   ├── README.md                     ← Índice de esta carpeta
│   ├── PRINCIPIOS-SOLID.md           ← SOLID adaptado
│   ├── PRINCIPIOS-ARQUITECTURA.md    ← Reglas A1-A10
│   ├── PATRONES-CARPETAS.md          ← Este archivo
│   └── ANTI-PATRONES.md              ← Anti-patterns conocidos
│
├── 📁 .claude/                        ← Configuración Claude Code
│   └── skills/                        ← Nivel 3: skills markdown reusables
│       ├── sigma-capture-domain/      ← Captura de dominio (creado Sprint 2 D1)
│       ├── sigma-sql-production-rules/   ← Sprint 2 T2
│       ├── sigma-multitenancy-bootstrap/ ← Sprint 2 T2
│       ├── sigma-immutable-tables/    ← Sprint 2 T2
│       ├── sigma-no-test-code/        ← Sprint 2 T2
│       ├── sigma-detect-failures/     ← Sprint 2 T2
│       ├── sigma-stop-conditions/     ← Sprint 2 T2
│       ├── sigma-session-handoff/     ← Sprint 2 T3
│       ├── sigma-memory-anti-degradation/ ← Sprint 2 T3
│       └── sigma-cleanup-staff-engineer/  ← Sprint 2/3
│
├── 📁 mcp-servers/                    ← Nivel 3: validators automatizados ⭐
│   ├── README.md
│   ├── sigma-validators-r/            ← Sprint 2 T2 (las 170+ reglas SQL)
│   └── sigma-close-session-validator/ ← Sprint 2 T3
│
├── 📁 domain-captures/                ← Nivel 4: dominio específico
│   ├── README.md
│   └── stallen-domain.md              ← Sprint 2 T1 (cuando capturemos Stallen)
│
├── 📁 decisions/                      ← Nivel 5: ADRs proyecto-momento
│   ├── README.md
│   ├── ADR-004-calibracion-nivel-comercial.md
│   ├── ADR-005-cierre-sprint-1.md
│   └── ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md ← Creado en esta sesión
│
├── 📁 docs/
│   └── MEMORIA-INTELIGENTE-Y-CIERRE.md  ← ADRs 001-003 embebidos
│
├── 📁 openspec/                       ← Changes específicos del proyecto
│   ├── config.yaml
│   ├── README.md
│   ├── specs/
│   └── changes/
│       └── validate-sdd-workflow/     ← Sprint 1 D5
│
├── 📁 workspace/                      ← Código del proyecto activo
│   ├── .gitkeep
│   └── stallen/                       ← Cuando arranque construcción Stallen (Sprint 3+)
│
└── 📁 .git/                           ← Repositorio git
```

---

## Las 6 reglas de organización de carpetas (C1-C6)

### C1 — La raíz solo contiene puntos de entrada

> La raíz del Departamento contiene **solo** archivos que actúan como puntos
> de entrada o configuración root. NO scripts ejecutables sueltos, NO archivos
> de un proyecto específico.

**Permitido en raíz**:
- `CLAUDE.md` — system prompt para Claude
- `AGENTS.md` — instructions root para agentes
- `README.md` — punto de entrada para humanos
- Documentos de diseño general (DEPARTAMENTO-DE-SOFTWARE.md, SISTEMA-DE-TRABAJO.md, PROTOCOLO-CONSTRUCCION-CODIGO.md)
- Configuración root (`.gga`, `.gitignore`, eventualmente `package.json`, `pyproject.toml`)
- Carpetas funcionales (architecture/, decisions/, etc.)

**NO permitido en raíz**:
- ❌ Scripts Python sueltos (`validate.py`, `helper.py`)
- ❌ Archivos de un proyecto específico (`stallen-something.md`)
- ❌ Outputs temporales (`output.txt`, `debug.log`)
- ❌ Backups manuales (`backup-2026-05-15.zip`)
- ❌ Archivos de test sueltos (`test_temp.py`)

**Por qué**: la raíz es la primera impresión del proyecto. Debe responder en
30 segundos "¿qué es este sistema?" sin ruido.

**Anti-pattern del legacy**: ~100 archivos Python en raíz mezclados con módulos
de soporte, workers, fixes históricos. Imposible entender qué es importante.

---

### C2 — `architecture/` contiene SOLO documentos universales (Nivel 2)

> Esta carpeta contiene **documentos de arquitectura universal**. NUNCA código
> ejecutable, NUNCA configuración de un cliente, NUNCA decisiones de momento.

**Permitido en `architecture/`**:
- Documentos `.md` describiendo principios universales
- Patrones agnósticos de proyecto
- Anti-patterns universales

**NO permitido en `architecture/`**:
- ❌ Archivos `.py`, `.ts`, `.sql` (van a workspace/ o mcp-servers/)
- ❌ Datos de Stallen específicos
- ❌ ADRs de un proyecto (van a decisions/)
- ❌ Skills markdown (van a .claude/skills/)

**Por qué**: separa **principios** de **implementación**. Cambiar un principio
es serio; cambiar una skill es rutina. La separación física refuerza esto.

---

### C3 — `domain-captures/` contiene SOLO configuración de dominio

> Configuración de un cliente/dominio específico. NUNCA lógica de negocio,
> NUNCA código de implementación.

**Permitido en `domain-captures/`**:
- Archivos `.md` describiendo el dominio en lenguaje natural
- Configuración declarativa (tablas inmutables, helpers, escala operativa)
- Invariantes de dominio en formato leíble
- Reglas de negocio específicas del cliente

**NO permitido en `domain-captures/`**:
- ❌ Código Python que IMPLEMENTA la lógica (va a workspace/)
- ❌ Migraciones SQL del cliente (van a workspace/<cliente>/)
- ❌ Reglas técnicas universales (van a `.claude/skills/`)
- ❌ Principios arquitectónicos (van a architecture/)

**Por qué**: el dominio se **declara**, no se **implementa**, en esta carpeta.
Permite reusar el mismo dominio con distintas implementaciones técnicas.

---

### C4 — `mcp-servers/` contiene SOLO validators y tools agnósticos

> Los MCP servers son agnósticos de proyecto. Reciben configuración via
> `domain-captures/`. NUNCA hardcodean nombres de tablas o helpers específicos.

**Permitido en `mcp-servers/`**:
- Código Python/TypeScript de cada server
- Tests del server con datos sintéticos
- README.md de cada server
- Schemas de tools

**NO permitido en `mcp-servers/`**:
- ❌ Hardcoded `"inventory_movements_sc"` u otros nombres de Stallen
- ❌ Decisiones de momento (van a ADRs)
- ❌ Documentación general del Departamento (va a docs/)

**Por qué**: si tomás un cliente nuevo, NO modificás el MCP server. Solo le
das nueva config via domain-captures/. DIP cumplido.

**Implicación práctica para Sprint 2 T2**: el server `sigma-validators-r` no
puede importar nombres específicos de Stallen. Recibe config de:
```
domain-captures/stallen-domain.md → parseado → DomainConfig object → inyectado
```

---

### C5 — `workspace/` contiene el código real del proyecto activo

> Donde vive el código que el cliente final usa. Separado del harness para
> que reinstalar el harness no toque código real, y refactorear el harness
> no rompa código real.

**Permitido en `workspace/`**:
- Carpetas por cliente: `workspace/stallen/`, `workspace/futuro-cliente/`
- Código Python/TypeScript/Svelte del proyecto
- Migraciones SQL del proyecto
- Tests del proyecto
- Documentación del proyecto

**NO permitido en `workspace/`**:
- ❌ Mezclar workspace con architecture/skills/mcp-servers (anti-pattern grave)
- ❌ Archivos del harness mezclados con código del cliente
- ❌ Configuración del Departamento (va a otras carpetas)

**Por qué**: separación clara entre "el harness" (todo lo demás) y "el código
que el harness produce" (workspace). Permite:
- Tomar otro cliente sin tocar el código de Stallen
- Refactorear el harness sin riesgo de romper código productivo
- Backup del cliente independiente del harness

**Estado actual (Sprint 1)**: workspace/ vacío con `.gitkeep`. Cuando arranque
construcción Stallen (Sprint 3+), creará `workspace/stallen/` con la app real.

---

### C6 — Cada carpeta tiene README.md propio

> Cada carpeta del Departamento (a partir de 2 archivos) DEBE tener un README.md
> que defina:
> 1. Qué Nivel cubre esta carpeta
> 2. Qué va aquí
> 3. Qué NO va aquí
> 4. Anti-patterns específicos de esta carpeta

**Por qué**:
- Onboarding más rápido (cada carpeta es auto-documentada)
- Fricción para violar la regla (alguien que agrega archivo incorrecto lee el README primero)
- Histórico claro de la intención original de la carpeta

**Excepciones**:
- Carpetas con 1 archivo (auto-explicativas)
- `.git/`, `.claude/`, etc. (configuración de tools externos)

**Estado actual**: la mayoría de carpetas ya tienen README. Las que faltan
(`mcp-servers/`) se crean en esta sesión.

---

## Mapping carpetas a SOLID

| Carpeta | SOLID dominante | Justificación |
|---|---|---|
| `architecture/` | **SRP** | UN propósito: documentar Nivel 2 |
| `.claude/skills/` | **SRP** + **ISP** | UNA skill = UN concept; skills focalizadas |
| `mcp-servers/` | **SRP** + **DIP** | UN server = UNA categoría; config inyectada |
| `domain-captures/` | **DIP** + **OCP** | Abstracción del dominio; agregás clientes sin modificar |
| `decisions/` | **SRP** | UN ADR = UNA decisión |
| `workspace/` | **SRP** + **OCP** | Código real separado; agregás clientes sin tocar harness |
| `openspec/` | **SRP** + **OCP** | Changes específicos por proyecto, no mezclados |

---

## Reglas de movimiento de archivos

Cuando un archivo está en la carpeta incorrecta, mover con razón documentada:

### De raíz → otra carpeta

```
"validate.py" en raíz → mcp-servers/sigma-validators-r/validate.py
  Razón: scripts ejecutables NO van en raíz (regla C1)

"stallen-database-schema.md" en raíz → domain-captures/stallen-domain.md
  Razón: dominio específico va en domain-captures (Nivel 4)
```

### De `.claude/skills/` → otra carpeta

```
"skill-de-stallen.md" → domain-captures/stallen-domain.md
  Razón: si solo aplica a Stallen, NO es Nivel 3 (es Nivel 4)

"skill-principios-solid.md" → architecture/PRINCIPIOS-SOLID.md
  Razón: si es universal y conceptual, es Nivel 2 (no Nivel 3)
```

### De `decisions/` → otra carpeta

```
"ADR-arquitectura-X.md" con regla universal → architecture/<archivo>.md
  Razón: si la decisión es estructural universal, promover a Nivel 2
  (Pero mantener el ADR como histórico de "cuándo se decidió")
```

---

## Cuándo crear una carpeta nueva

Crear carpeta nueva solo cuando:
1. **Aparece un Nivel nuevo** (raro: estos 5 son estables)
2. **Aparece un tipo de artefacto nuevo** que no encaja en ninguna existente
3. **Hay 3+ archivos** del mismo tipo en una carpeta existente (justifica subdivisión)

Antes de crear carpeta nueva:
- ¿Encaja en alguna existente?
- ¿Puede ser subcarpeta de una existente?
- ¿Es realmente diferente de las demás?

Carpetas nuevas válidas a futuro:
- `tools/` — si aparecen tools auxiliares no-MCP (CLI scripts, etc.)
- `monitoring/` — Sprint 4 cuando agregue observability
- `templates/` — Sprint 3+ cuando crezcan templates reusables

---

## Anti-patterns de organización (referencia)

Identificados en el legacy o en proyectos comunes:

### "Flat root explosion"
~100 archivos Python en la raíz sin carpetas. Imposible navegar.
**Cura**: aplicar C1 retroactivamente, mover archivos a carpetas funcionales.

### "Mixed concerns folder"
Carpeta `utils/` con 30 archivos de propósitos completamente distintos.
**Cura**: subdividir por dominio funcional, no por tipo de archivo.

### "Cross-level pollution"
Archivo de Nivel 4 (dominio Stallen) viviendo en `architecture/` (Nivel 2).
**Cura**: aplicar las reglas C2-C5, mover al nivel correcto.

### "Hidden state"
Configuración crítica en archivos `.hidden` sin documentación.
**Cura**: configuración visible con README explicando por qué está allí.

Ver `ANTI-PATRONES.md` para catálogo completo.

---

## Validación automática propuesta

Es posible (y deseable) validar estas reglas automáticamente:

```python
# pseudo-código de validator
def validar_estructura_carpetas(root):
    violaciones = []

    # C1: raíz solo con entry points
    for archivo in listdir(root):
        if es_archivo(archivo) and not es_entry_point(archivo):
            violaciones.append(f"C1: {archivo} no es entry point")

    # C2: architecture/ sin .py/.ts
    for archivo in listdir(root/"architecture"):
        if archivo.endswith((".py", ".ts", ".sql")):
            violaciones.append(f"C2: code file in architecture/: {archivo}")

    # C6: cada carpeta tiene README
    for carpeta in subcarpetas(root):
        if num_archivos(carpeta) >= 2 and not (carpeta/"README.md").exists():
            violaciones.append(f"C6: {carpeta} sin README.md")

    return violaciones
```

Esta validación puede ser parte de `mcp-servers/sigma-validators-r/` como
herramienta `validate_repo_structure()`.

---

## Cómo este documento se mantiene

**Cambios válidos**:
- Aparece nuevo Nivel (muy raro)
- Aparece patrón estructural validado por 2+ proyectos
- Se descubre carpeta universalmente útil que falta

**Cambios INVÁLIDOS**:
- "Mi proyecto Stallen necesita una carpeta especial" → Nivel 4/5
- "Voy a reordenar todo porque me gusta más así" → requiere ADR
- "Esta regla es muy estricta" → re-evaluar caso específico, no relajar regla

---

Versión: 1.0 | Creado: 2026-05-15
Origen: aplicación de SOLID + 5 niveles de reglas + análisis legacy SigmaControl
