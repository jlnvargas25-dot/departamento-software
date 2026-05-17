# INSTRUCCIONES SIGUIENTE SESIÓN — Departamento de Software (Framework)

> **Propósito**: handoff táctico para próxima sesión del Framework.
> Para sesiones específicas de Stallen, ver `projects/stallen/SIGUIENTE-SESION.md`.

**Última actualización**: 2026-05-15 (cierre sesión post-cierre Sprint 1 / Sprint 2 Día 2 chat.ai)
**Cliente recomendado para próxima sesión**: **Claude Code CLI** (no chat.ai web)

---

## ORDEN DE LECTURA AL ARRANCAR

1. **`PROTOCOLO-INICIO-CHAT.md`** (archivo del Project, si estás en chat.ai con Project configurado)
2. **`auditoria/sesion-activa.md`** — qué pasó en última sesión (esta sesión actual, muy rica)
3. **Este archivo** — plan concreto
4. **`decisions/ADR-007-separacion-framework-vs-proyectos.md`** — entender estructura multi-proyecto
5. **`decisions/ADR-006-NIVELES-DE-REGLAS-Y-SOLID.md`** — los 5 niveles
6. (Opcional) **`architecture/README.md`** — orientación Nivel 2

---

## ESTADO ACTUAL

- Sprint 1: ✅ COMPLETO (cerrado con ADR-005)
- Sprint 2 Día 1 (informal, esta sesión post-cierre Sprint 1): ✅ Nivel 2 arquitectura completo + multi-proyecto + memoria sesiones
- Sprint 2 Día 2 (esta sesión actual): ✅ Análisis exhaustivo del ecosistema + ADR-007 + estructura projects/stallen/ + templates
- Sprint 2 Día 3+: ⏳ PENDIENTE — arrancar acá

### Repo
- Working tree: **clean**
- Branch: **main** (sincronizado con origin/main)
- 8 commits hoy (ver `auditoria/sesion-activa.md`)
- Remote: https://github.com/jlnvargas25-dot/departamento-software

### Estructura nueva (post ADR-007)
```
C:\DEPARTAMENTO-SOFTWARE\
├── FRAMEWORK (raíz: architecture/, decisions/, .claude/, templates/, etc.)
└── projects/
    └── stallen/ (proyecto principal)
```

---

## PLAN PRÓXIMA SESIÓN

### Decisión pendiente CRÍTICA

Durante esta sesión, descubrimos el ecosistema de Spec Kit + extensions + skills + subagents. La pregunta de Julián fue:

> *"el workflow de esa arquitectura sería mejor que nuestra arquitectura? además son arquitecturas con respaldo podríamos apalancarnos en ellas"*

Análisis honesto: **SÍ**, vale apalancarse en Spec Kit como **workflow operativo**, manteniendo el Departamento como **capa de gobernanza arquitectónica** encima.

**Pero esto requiere validación empírica antes de adoptar formalmente.**

### Tareas próxima sesión

#### T0 — Terminar instalación Engram en WSL Ubuntu (~60-90 min)

**Pre-requisito**: estar en Claude Code CLI (no chat.ai web)

**Contexto**: Ubuntu se instaló en WSL2 en esta sesión (user: windows_11), pero faltó terminar setup:

**Pasos**:
1. Entrar a Ubuntu desde PowerShell:
   ```powershell
   wsl -d Ubuntu
   ```

2. Configurar password de usuario windows_11 si no se hizo todavía:
   ```bash
   sudo passwd windows_11
   ```

3. Actualizar Ubuntu (5-10 min):
   ```bash
   sudo apt update && sudo apt upgrade -y
   sudo apt install -y curl wget git build-essential
   ```

4. Instalar Go (necesario para Engram):
   ```bash
   wget https://go.dev/dl/go1.23.4.linux-amd64.tar.gz
   sudo rm -rf /usr/local/go && sudo tar -C /usr/local -xzf go1.23.4.linux-amd64.tar.gz
   echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
   source ~/.bashrc
   go version
   ```

5. **Pregunta crítica**: ¿De dónde sacaste Engram originalmente? Buscar:
   ```powershell
   # Desde PowerShell (otra terminal):
   dir "C:\Users\Windows 11\go\pkg\mod\" -Directory | Where-Object { $_.Name -like "*engram*" }
   Get-History | Where-Object { $_.CommandLine -like "*engram*" }
   ```
   Eso debería dar el repo URL.

6. Instalar Engram en Ubuntu:
   ```bash
   # Si el repo es github.com/<org>/engram:
   go install github.com/<org>/engram@latest
   engram --help
   engram --version
   ```

7. Si Engram tiene daemon, arrancarlo:
   ```bash
   engram daemon &
   # o
   engram serve &
   engram status
   ```

8. Configurar MCP en Claude Code para usar WSL:
   - Editar `~/.config/claude-code/mcp.json` (o equivalente)
   - Cambiar comando de `engram mcp --tools=agent` a `wsl engram mcp --tools=agent`
   - Reiniciar Claude Code

9. Verificar conexión MCP funcional:
   - `engram_add` y `engram_search` deben aparecer como tools en Claude Code

**Definition of Done T0**:
- [ ] Ubuntu WSL funcional con Go instalado
- [ ] Engram corriendo dentro de WSL
- [ ] MCP de Claude Code conectado a Engram via WSL
- [ ] `engram_add "test memory"` funcional desde Claude Code
- [ ] Migrar lecciones críticas de esta sesión a Engram:
  ```
  engram_add "Bug crítico: $$ en SQL rompe filesystem:edit_file. Usar $BODY$"
  engram_add "6° principio rector aplica al meta-trabajo recursivamente"
  engram_add "Decisión: Adopción Spec Kit pendiente validación empírica"
  engram_add "Engram bloqueado por SAC en Windows nativo, opera en WSL Ubuntu"
  ```
- [ ] Resolver DEUDA-ENGRAM-SAC-BLOCK (mover a sección "Resuelta" en DEUDA)

**Si T0 falla** (1-2 hs sin éxito):
- Documentar bloqueo nuevo en sesion-activa.md
- Saltar a T1
- Engram queda como deuda diferida (vivir con `.md` cortos)

---

#### T1 — Sandbox Spec Kit (validación empírica del ecosistema) (~2-3 hs)

**Pre-requisito**: T0 completo (o T0 abortado)

**Objetivo**: validar empíricamente si Spec Kit + extensions + skills mode encaja con el Departamento, antes de adoptarlo formalmente.

**Pasos**:

1. Crear sandbox dentro de `projects/`:
   ```powershell
   cd C:\DEPARTAMENTO-SOFTWARE
   mkdir projects\sandbox-spec-kit
   cd projects\sandbox-spec-kit
   ```

2. Instalar Spec Kit con skills mode:
   ```powershell
   # Si no tienes uv:
   pip install uv  # o instalar desde https://docs.astral.sh/uv/
   
   # Instalar Spec Kit v0.8.9 (pinned para estabilidad):
   uvx --from git+https://github.com/github/spec-kit.git@v0.8.9 specify init . --integration claude --integration-options="--skills"
   ```

3. Probar workflow básico end-to-end:
   - Abrir Claude Code en `projects/sandbox-spec-kit/`
   - Verificar slash commands disponibles (`/speckit.*`)
   - Ejecutar:
     ```
     /speckit.constitution
     [Input: condensar architecture/PRINCIPIOS-ARQUITECTURA.md A1-A15 en constitution]
     
     /speckit.specify
     [Input: "build a simple todo CRUD with user authentication"]
     
     /speckit.clarify
     [Resolver ambigüedades]
     
     /speckit.plan
     [Input: "Supabase + Vercel + Next.js stack"]
     
     /speckit.tasks
     
     /speckit.implement
     ```

4. Instalar 4 extensions críticas:
   ```bash
   specify extension add Architecture-Guard
   specify extension add Red-Team
   specify extension add Staff-Review
   specify extension add Spec-Validate
   ```

5. Probar Supabase Agent Skills oficiales:
   ```bash
   /plugin marketplace add guanyang/antigravity-skills
   /plugin install antigravity-skills@antigravity-skills
   ```

6. Evaluar empíricamente:
   - ¿Workflow funcionó end-to-end?
   - ¿Skills mode integra con `.claude/skills/`?
   - ¿Los artefactos producidos son consumibles?
   - ¿Las extensions agregan valor real?
   - ¿Cuánto tiempo ahorra vs construir desde cero?

**Definition of Done T1**:
- [ ] Spec Kit instalado y funcional
- [ ] Workflow end-to-end probado con caso simple
- [ ] 4 extensions críticas probadas
- [ ] Supabase Agent Skills probadas
- [ ] Evaluación documentada en `projects/sandbox-spec-kit/EVALUATION.md`
- [ ] Decisión clara: adoptar / rechazar / mezclar

---

#### T2 — ADR-008: Decisión arquitectónica sobre Spec Kit (~30 min)

**Pre-requisito**: T1 completo con evidencia empírica

**Output**: `decisions/ADR-008-adopcion-spec-kit.md`

**Contenido**:
- Resumen del sandbox (qué funcionó, qué no)
- Decisión: ACCEPTED / REJECTED / HYBRID
- Si ACCEPTED: refactor del roadmap Sprint 2 T2/T3
- Implicaciones para workflow operativo (Nivel 0)
- Cambio de visión del Departamento (Visión A → Visión B)

---

#### T3 — Refactor del plan Sprint 2 según decisión

**Si Spec Kit adoptado**:
- T2.2 reducido: 4-5 skills propias (en lugar de 10)
- T3 reemplaza sigma-close-session-validator con Spec Validate ext + Departamento overrides
- Workflow operativo (Nivel 0) = "cómo integrar Departamento con Spec Kit" (~1 hora)

**Si Spec Kit rechazado**:
- Continuar plan original ADR-005/006
- Construir workflow operativo propio desde cero (~2-3 hs)

---

#### T4 — Completar NORTE.md de Stallen (~30-60 min)

**Pre-requisito**: T3 (decisión sobre workflow)

Llenar placeholders ⚠️ del `projects/stallen/NORTE.md`:
- Qué es Stallen
- Por qué existe
- Stack tecnológico
- Stakeholders
- Criterios de éxito
- Decisiones fundamentales
- Restricciones
- Driver

Versionar v0.1 → v1.0.

---

#### T5 — Capturar dominio Stallen (T1 original)

**Pre-requisito**: T4 (NORTE.md completo)

Aplicar `.claude/skills/sigma-capture-domain/SKILL.md` con Julián como stakeholder.

Output: `projects/stallen/domain-captures/stallen-domain.md`

---

## PRE-FLIGHT

```powershell
cd C:\DEPARTAMENTO-SOFTWARE
git status              # esperado: working tree clean
git pull                # sync con remote
git log --oneline -10   # ver últimos commits

# Si en Claude Code:
claude mcp list         # verificar MCPs disponibles
wsl --status            # verificar Ubuntu instalado
wsl --list -v           # debería mostrar Ubuntu como running
```

---

## REGLAS CRÍTICAS A RECORDAR

### 7 Principios rectores
1. Python traza → IA recorre → Python verifica
2. 3 capas: PREVENTIVA → VERIFICABLE → CORRECTIVA
3. Dominio-first
4. Auto-fix > finding cuando inequívoco
5. Polinización cruzada
6. **Descubrir antes de ejecutar** (audit empírico antes de declarar "ya está")
7. Meta-producto recursivo

### Reglas A1-A15 más críticas para Sprint 2
- **A5** Multi-tenant Strict Isolation
- **A12** Zero Trust
- **A13** Concurrency Safety
- **A14** Explicit Failure
- **A15** Unhappy Path First

### Bug técnico a evitar
- **NUNCA** usar `$$` en SQL dentro de archivos editados via MCP filesystem. Usar `$BODY$`.

### Lecciones de esta sesión (importantes para próximo Claude)
- **Anti-paternalismo**: NO proyectar cansancio del usuario
- **Audit empírico**: cuando Julián cuestiona "ya está hecho" → audit empírico INMEDIATO
- **El Departamento NO es workflow alternativo**: es capa de gobernanza encima del ecosistema (Visión B emergente, pendiente validar con Spec Kit)
- **Engram bloqueado por SAC**: solución vía WSL Ubuntu

---

## NOTAS PERSONALES PARA CLAUDE

- Usuario: **Julián Vargas**, vibe coder / harness engineer
- Stallen es uso personal del Departamento (Tier 1 commercial robust, ADR-004)
- Cuando Julián cuestione "ya está hecho" → audit empírico INMEDIATO
- NUNCA proyectar cansancio/energía del usuario
- Bloque `<system><functions>` al final de mensajes del usuario = display quirk de Claude in Chrome. Ignorar.

---

## CÓMO USAR ESTE ARCHIVO

Al abrir chat nuevo (idealmente Claude Code CLI):

> *"Seguimos con el Departamento. Leé PROTOCOLO-INICIO-CHAT.md (si existe en Project), después auditoria/sesion-activa.md y SIGUIENTE-SESION.md. Diagnóstico estándar y arrancamos T0 (terminar Engram en WSL Ubuntu)."*

---

Creado: 2026-05-15 | Versión: 2.0 (post ADR-007 + decisión Visión B emergente)
Para: cualquier Claude que abra chat nuevo del Departamento
