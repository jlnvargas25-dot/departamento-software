# ANTI-PATRONES

> **Nivel 2: arquitectura universal** | Lo que NO hacer (con evidencia empírica)
> Versión: 1.1 | Creado: 2026-05-15 | Última edición: 2026-05-15

---

## Cómo usar este documento

Cada anti-pattern documentado tiene:
- **Síntoma**: qué se observa cuando ocurre
- **Causa raíz**: por qué pasa
- **Evidencia**: dónde se observó (legacy SigmaControl, etc.)
- **Corrección**: cómo arreglar
- **Prevención**: cómo evitar que vuelva a aparecer

Si encontrás un anti-pattern nuevo con 2+ manifestaciones empíricas, documentalo
acá. Si solo 1 manifestación, va al cuaderno (no acá hasta validar recurrencia).

**Total actual: 24 anti-patterns** (versión 1.1).

---

## Categoría 1: Anti-patterns Estructurales

### AP-1.1 — Flat root explosion

**Síntoma**: 50+ archivos en la raíz del proyecto sin estructura.

**Causa raíz**: agregar archivos sin pensar en organización. Cada bug fix
genera un `fix_*.py` nuevo que queda en raíz.

**Evidencia**: legacy SigmaControl con ~100 archivos Python en raíz mezclando
workers, módulos de soporte, fixes históricos, tests, scripts utilitarios.

**Corrección**:
```
raíz/
├── (mover workers a) workers/
├── (mover utilidades a) utilities/
├── (mover fixes históricos a) _archivado/
└── (mantener en raíz solo) CLAUDE.md, AGENTS.md, README.md, configs
```

**Prevención**: regla C1 (la raíz solo contiene entry points). Validación
automática que falla el commit si la raíz tiene >20 archivos no-entry-point.

---

### AP-1.2 — Mixed concerns folder

**Síntoma**: carpeta `utils/` o `helpers/` o `tools/` con 30 archivos de
propósitos completamente distintos.

**Causa raíz**: "no sé dónde ponerlo, lo pongo en utils".

**Evidencia**: legacy SigmaControl con `herramientas/` que mezclaba ritual.py
(operación de cierre crítica), capturar_adn.py (extracción de dominio),
auditoria_imports.py (análisis estático), fix_encoding.py (utilidad one-shot).

**Corrección**: subdividir por dominio funcional:
```
herramientas/
├── session/      ← ritual.py, abrir_sesion/, cerrar_sesion/
├── domain/       ← capturar_adn.py
├── analysis/     ← auditoria_imports.py
└── one-shots/    ← fix_encoding.py (raras, archivable)
```

**Prevención**: cuando se va a agregar archivo nuevo a "utils/", preguntarse
"¿qué subdominio funcional cubre?". Si la respuesta no es clara, considerar
carpeta nueva.

---

### AP-1.3 — Cross-level pollution

**Síntoma**: archivo de Nivel 4 (dominio específico) viviendo en carpeta
de Nivel 2 (universal). O similar.

**Causa raíz**: no entender la separación de niveles.

**Evidencia**:
- legacy SigmaControl: skill `naming-sigmacontrol.md` con nombres de tablas
  específicos viviendo en `skills/` (que debería ser Nivel 3 técnico
  universal). Era Nivel 4 (dominio).

**Corrección**: aplicar reglas C2-C5, mover al nivel correcto:
```
skills/naming-sigmacontrol.md  (Nivel 4 disfrazado de Nivel 3)
    → domain-captures/stallen-domain.md  (Nivel 4 correcto)
    → .claude/skills/sigma-naming-conventions.md  (Nivel 3 universal template)
```

**Prevención**: para cada nuevo archivo, hacer el test del nivel:
- ¿Aplica a cualquier proyecto? → Nivel 1 o 2
- ¿Aplica a cualquier proyecto del mismo stack? → Nivel 3
- ¿Aplica solo a Stallen? → Nivel 4
- ¿Es decisión de momento? → Nivel 5

---

### AP-1.4 — Hidden state

**Síntoma**: configuración crítica en archivos `.hidden` sin documentación.

**Causa raíz**: configuración accidentalmente "oculta" y nadie se acuerda
de ella hasta que rompe algo.

**Evidencia**: comunes en cualquier proyecto. El legacy tenía `.env`, `.env.local`,
`.vercel` sin documentar en raíz.

**Corrección**: cada archivo de config oculto debe tener entrada en `.gitignore`
documentando POR QUÉ está oculto + ejemplo `<archivo>.example` visible.

**Prevención**: regla "no hay configuración no-documentada".

---

## Categoría 2: Anti-patterns Arquitectónicos

### AP-2.1 — God Validator

**Síntoma**: un único validador que valida TODO: SQL, frontend, contratos,
deploy, estado, escala, naming, seguridad.

**Causa raíz**: ahorrar tipeo (un solo archivo) sin pensar mantenimiento.

**Evidencia**: típico anti-pattern. El legacy lo evitó separando en
`reglas_16_19.py`, `reglas_20_22.py`, etc.

**Violaciones SOLID**:
- **SRP**: un archivo con N responsabilidades
- **ISP**: consumidores cargan validaciones que no necesitan

**Corrección**: separar en validators específicos:
```
SqlValidator (antes monolítico)
    → SqlInvariantsValidator
    → SqlPerformanceValidator
    → SqlSecurityValidator
    → SqlConcurrencyValidator
    → SqlScaleValidator
```

**Prevención**: para cualquier validator nuevo, preguntar "¿qué responsabilidad
NUEVA agrega?". Si no es nueva, va en el existente. Si es nueva, crear archivo
separado.

---

### AP-2.2 — Hardcoded Domain

**Síntoma**: nombres de tablas, helpers, sufijos del cliente metidos como
strings literales en código universal.

**Ejemplo del legacy**:
```python
# INCORRECTO (visto en versión inicial):
HELPER_FUNCTION = "get_my_sc_company_id()"  # Stallen-specific
INMUTABLES = {"inventory_movements_sc", "customer_interactions_sc"}  # Stallen
```

**Causa raíz**: empezar con un solo cliente y no pensar en multi-proyecto.

**Violaciones SOLID**:
- **DIP**: dependencia de implementación concreta, no abstracción
- **OCP**: tomar cliente nuevo requiere modificar código universal

**Corrección**: extraer a config:
```python
# CORRECTO:
class SqlValidator:
    def __init__(self, config: DomainConfig):
        self.helper_company_id = config.helper_company_id
        self.inmutables = config.inmutables
        # ...
```

Y la config viene de `domain-captures/<cliente>.md`.

**Prevención**: regla "ningún string que sea nombre de cliente/tabla específica
en código universal". Validable con grep: si aparece "stallen", "_sc", o
nombre de cliente conocido en código de Niveles 1-3, alert.

---

### AP-2.3 — Inconsistent Returns

**Síntoma**: funciones/tools que retornan distintos tipos según caso de uso.

**Ejemplos**:
```python
def validar(x):
    if x.tipo == "sql":
        return True  # bool
    elif x.tipo == "json":
        return {"ok": True, "errors": []}  # dict
    else:
        return ["error1", "error2"]  # list
```

**Violaciones SOLID**:
- **LSP**: consumidores no pueden tratar el return uniformemente
- **SRP**: la función hace cosas distintas según input

**Evidencia**: común en código sin schemas explícitos.

**Corrección**: contrato uniforme:
```python
# El legacy aplicaba esto en core/contratos.py:
def verificar_X(...) -> tuple[bool, list[str]]:
    """Retorna (ok, violaciones)."""
    ...
```

**Prevención**: declarar tipo de return explícito (type hints, schema).
Para MCP tools, schema JSON oficial. Para skills, frontmatter estandarizado.

---

### AP-2.4 — Monolithic Skill

**Síntoma**: skill markdown con 8 secciones sin relación entre sí.

**Ejemplo**: skill que cubre "cómo escribir SQL + cómo hacer handoff + cómo
cerrar sesión + cómo debuggear errores + cómo escalar a humano".

**Violaciones SOLID**:
- **SRP**: skill con N propósitos
- **ISP**: consumidor que solo necesita "cómo escribir SQL" carga todo

**Evidencia**: típico cuando se empieza a documentar sin estructura.

**Corrección**: una skill por concepto:
```
skill-sql-everything.md (monolítica)
    → sigma-sql-production-rules.md
    → sigma-session-handoff.md
    → sigma-detect-failures.md
    → sigma-stop-conditions.md
```

**Prevención**: el título de la skill debe responder UNA pregunta única.
Si la respuesta tiene "y también..." → vale separar.

---

### AP-2.5 — Module Ownership Violation

**Síntoma**: módulo A modifica tablas de módulo B directamente.

**Ejemplo del legacy** (cita verbatim de skill-deteccion-fallas):
```sql
-- Caja hizo en una migración:
ALTER TABLE customers ADD COLUMN limite_credito NUMERIC;
-- customers es propiedad de CRM
```

**Causa raíz**: necesidad legítima (Caja quiere saber límite) mal resuelta
(modificación directa en vez de via interface).

**Violaciones**:
- **A1 Module Ownership** (Nivel 2 universal)
- **A2 Encapsulación** (Nivel 2 universal)

**Corrección**:
- CRM expone `get_limite_credito(customer_id) → NUMERIC` (RPC)
- O CRM publica evento `limite_credito_actualizado` y Caja consume

**Prevención**: validator que detecta `ALTER TABLE X` cuando X no pertenece
al módulo declarado del thread. El legacy tenía esto como regla G21
("Builder inventa entidades fuera del scope del plan").

---

### AP-2.6 — Direct Table Access from Frontend

**Síntoma**: frontend hace `supabase.from('products').select()` directo.

**Causa raíz**: parece "simple" en MVP, después no se refactorea.

**Violaciones**:
- **A2 Encapsulación**: tablas son detalles de implementación, no interface

**Evidencia**: legacy SigmaControl frontend tenía 14 componentes que
accedían tablas directamente. Cuando el modelo de datos cambió, 14 componentes
se rompieron a la vez.

**Corrección**: TODOS los accesos al backend pasan por RPCs:
```typescript
// INCORRECTO:
const { data } = await supabase.from('products').select('*');

// CORRECTO:
const { data } = await supabase.rpc('get_inventario');
```

**Prevención**: linter que detecta `.from()` en código frontend. Solo `.rpc()`
permitido.

---

### AP-2.7 — Cross-Tenant Function Parameter

**Síntoma**: función pública recibe `p_company_id UUID` como parámetro
externo.

**Ejemplo del legacy**:
```sql
CREATE FUNCTION evaluar_alertas_todas_empresas(p_company_id UUID)
-- Cualquier usuario puede pedir alertas de cualquier empresa
```

**Causa raíz**: parecía "más flexible" recibir tenant como param.

**Violaciones**:
- **A5 Multi-tenant Strict Isolation** (Nivel 2 universal)
- **A12 Zero Trust** — viola ZT-1 (tenant del JWT, no del param)
- **Crítico de seguridad**: cross-tenant data leak

**Corrección**:
```sql
CREATE FUNCTION evaluar_alertas_crm()
-- Solo opera sobre la empresa del usuario autenticado
DECLARE
    v_company_id UUID := get_my_sc_company_id();
BEGIN
    -- ...
END;
```

**Prevención**: validator detecta automáticamente funciones públicas con
`p_company_id` o `p_tenant_id` como parámetro. Falla el commit.

---

### AP-2.8 — Raw Table Response

**Síntoma**: API/RPC retorna filas crudas de tabla como respuesta sin
filtrar/transformar.

**Ejemplos**:
```
INCORRECTO en SQL:
  CREATE FUNCTION get_productos()
  RETURNS SETOF products_sc   -- retorna la tabla entera con TODOS los campos
  AS ... ;

Esto expone columnas internas como:
  - created_by_user_id (interno)
  - cost_internal (sensible)
  - deleted_at (soft-delete flag)
  - notes_internal (admin only)
```

```typescript
// INCORRECTO en frontend:
const { data } = await supabase.from('products_sc').select('*');
// data tiene TODOS los campos de la tabla
```

**Causa raíz**: más fácil retornar la tabla que diseñar DTO. "Después lo arreglamos".

**Violaciones**:
- **A11 DAO + DTO** — expone schema interno
- **A2 Encapsulación de tablas** — tabla es interface

**Por qué importa**:
- Acoplamiento frágil: cambiar nombre de columna rompe TODO consumer
- Filtración de información sensible (audit fields, cost, internal notes)
- Imposible versionar API sin migrar schema
- 14 consumers se rompieron simultáneamente en el legacy cuando cambió schema

**Corrección**:
```
CORRECTO: declarar columnas específicas en RETURNS TABLE

  CREATE FUNCTION get_productos_para_venta()
  RETURNS TABLE (
      id UUID,
      nombre TEXT,
      precio NUMERIC,
      stock_actual NUMERIC
  ) AS ...
      RETURN QUERY
      SELECT p.id, p.name AS nombre, p.precio_venta AS precio, p.stock_actual
      FROM products_sc p
      WHERE p.company_id = get_my_sc_company_id()
        AND p.deleted_at IS NULL;
  ...
```

**Prevención**:
- Validator detecta `RETURNS SETOF tabla` → review (marcar como sospechoso)
- Validator detecta `SELECT *` en RPCs → alert
- Linter frontend prohibe `.from()` (solo permite `.rpc()`)

---

### AP-2.9 — Trust Boundary Violation

**Síntoma**: código asume que un input "interno" (del frontend, de otro
módulo, de un servicio confiable) ya está validado/sanitizado.

**Ejemplos**:
```
INCORRECTO en SQL: asume que p_email viene validado

  CREATE FUNCTION registrar_lead(p_email TEXT, p_nombre TEXT)
  RETURNS UUID AS ...
      -- Sin validar p_email -> podría ser inyección, malformado, etc.
      INSERT INTO leads_sc (email, nombre) VALUES (p_email, p_nombre);
      -- ...
```

```python
# INCORRECTO en backend: asume que el frontend ya validó
@app.post("/api/registrar")
def registrar(body: dict):
    db.execute(f"INSERT INTO users (email) VALUES ('{body['email']}')")
    # SQL injection garantizado si frontend tiene bug
```

**Causa raíz**: "si el frontend lo manda, ya está validado". Falsa premisa
de Zero Trust.

**Violaciones**:
- **A12 Zero Trust** — viola ZT-3 (validar siempre, no asumir)
- Crítico: SQL injection, XSS, command injection posibles

**Por qué importa**:
- El frontend puede ser bypasseado (curl, Postman, navegador modificado)
- El frontend puede tener bug que NO valida
- Otro módulo "confiable" puede tener bug
- Defense in depth: validar en CADA capa

**Corrección**:
```
Validar SIEMPRE en cada capa, no asumir:

  CREATE FUNCTION registrar_lead(p_email TEXT, p_nombre TEXT)
  RETURNS UUID AS ...
      -- ZT-3: validar SIEMPRE, no asumir
      IF p_email IS NULL OR LENGTH(p_email) < 5 THEN
          RAISE EXCEPTION 'email invalid';
      END IF;
      IF p_email NOT LIKE '%@%.%' THEN
          RAISE EXCEPTION 'email format invalid';
      END IF;
      IF LENGTH(p_email) > 255 THEN
          RAISE EXCEPTION 'email too long';
      END IF;
      IF p_nombre IS NULL OR LENGTH(TRIM(p_nombre)) = 0 THEN
          RAISE EXCEPTION 'nombre required';
      END IF;
      -- ... ahora sí proceder
      INSERT INTO leads_sc (email, nombre) VALUES (p_email, p_nombre);
  ...
```

**Prevención**:
- Code review obligatorio: toda función pública DEBE validar inputs
- Linter detecta funciones que reciben TEXT/JSONB sin chequear NULL/format
- Tests adversariales obligatorios (A15) cubren inputs malformados

---

## Categoría 3: Anti-patterns de Proceso

### AP-3.1 — Mixing Cleanup with Execution

**Síntoma**: sesión donde se hace limpieza estructural Y construcción nueva
a la vez.

**Causa raíz**: "ya que estoy con el archivo abierto, también arreglo X".

**Evidencia**: legacy SigmaControl documentó esto como regla #5 ("No mezclar
limpieza con ejecución en la misma sesión").

**Por qué importa**:
- Mezclar limpieza con feature work hace que ningún commit sea atómico
- Si la limpieza tiene bug, rompe el feature también
- Si el feature tiene bug, no se sabe si es por el feature o por la limpieza

**Corrección**: separar en commits y/o sesiones distintas:
```
Commit 1: refactor — separar X de Y (cleanup puro)
Commit 2: feat — agregar feature Z (construction puro)
```

**Prevención**: protocol explícito antes de cada sesión: "¿esta sesión es
cleanup o construction? Solo uno."

---

### AP-3.2 — Test Code in Production

**Síntoma**: funciones `smoke_test_*`, `test_*`, `debug_*`, `verify_*` quedan
en código de producción.

**Causa raíz**: LLMs agregan estas funciones para "verificar su trabajo"
sin que se les pida. Quedan ahí si nadie las limpia.

**Evidencia**: extremadamente común. El legacy tenía skill dedicado
(`skill-no-codigo-prueba.md`) y regla Python automática para detectarlo.

**Violaciones**:
- **A10 No Test Code in Production** (Nivel 2 universal)
- **SRP**: artefactos de producción ≠ artefactos de testing

**Corrección**:
```sql
-- Eliminar de producción:
-- CREATE FUNCTION smoke_test_products_sc() ...
-- CREATE FUNCTION test_rls_isolation() ...
-- CREATE FUNCTION debug_check_constraints() ...

-- Mover (si se quieren) a:
-- tests/sql/test_products.sql (carpeta separada)
```

**Prevención**: validator automático (legacy lo tenía):
```python
PATRONES_TEST_CODE = [
    r'CREATE.*FUNCTION.*smoke_test',
    r'CREATE.*FUNCTION.*test_\w+',
    r'CREATE.*FUNCTION.*debug_',
    r'CREATE.*FUNCTION.*verify_',
]
```
Auto-elimina o rechaza commit.

---

### AP-3.3 — Infinite Retry without Stop Conditions

**Síntoma**: agente/worker en loop infinito reintentando la misma operación.

**Ejemplo del legacy**:
```
[CONSTRUCTOR] Thread 1 falló 3x — escalando a replanning
[CONSTRUCTOR] Thread 1 falló 4x — escalando a replanning
[CONSTRUCTOR] Thread 1 falló 5x — escalando a replanning
(se repite indefinidamente)
```

**Causa raíz**: lógica de escalamiento mal definida. El worker "escala" pero
no verifica que ESCALÓ realmente antes de reintentar.

**Violaciones**:
- **A9 Stop Conditions Explicit** (Nivel 2 universal)

**Corrección**:
```python
MAX_RETRIES = 3
for intento in range(MAX_RETRIES):
    resultado = ejecutar()
    if resultado.ok:
        return resultado
    if intento == MAX_RETRIES - 1:
        escalar_a_humano(razon=resultado.error)
        raise  # Salir del loop, NO seguir reintentando
```

**Prevención**: code review focused on stop conditions. Todo loop con `while`
o retry debe tener condición de salida explícita y testeada.

---

### AP-3.4 — Aprendizajes Duplicados Acumulados

**Síntoma**: lista de "aprendizajes"/"learnings"/"notas" crece sin parar con
el mismo aprendizaje repetido N veces.

**Ejemplo del legacy** (verbatim):
```json
"aprendizajes": [
  "Thread 1 requirió replanning después de 3 rechazos",
  "Thread 1 requirió replanning después de 3 rechazos",
  "Thread 1 requirió replanning después de 3 rechazos"
]
```
(30+ veces el mismo texto en la lista real)

**Causa raíz**: cada ciclo agrega el aprendizaje sin verificar si ya existe.

**Por qué importa**:
- Lista de aprendizajes crece indefinidamente
- LLM no puede procesar 50+ entradas en prompt
- Aprendizajes más viejos se truncan, se pierden, se repiten

**Corrección**:
```python
# Deduplicar antes de guardar:
aprendizajes_unicos = list(dict.fromkeys(aprendizajes))
estado["aprendizajes"] = aprendizajes_unicos[-20:]  # cap a 20
```

**Prevención**: regla "toda lista de notas debe deduplicarse y capearse".
Sistema de **memoria larga** (skills auto-generados) absorbe los recurrentes.

---

### AP-3.5 — API Call Without Retry

**Síntoma**: llamada a API externa sin manejo de overload/timeout.

**Ejemplo del legacy**:
```
anthropic._exceptions.OverloadedError: Error code: 529
(ocurre en múltiples workers simultáneamente)
```

**Causa raíz**: asumir que la API siempre responde. No prever sobrecarga.

**Violaciones**:
- **A9 Stop Conditions Explicit** (parcial: necesita retry como complemento)

**Corrección**: retry exponencial obligatorio:
```python
def llamar_api_con_retry(payload, max_retries=5):
    for intento in range(max_retries):
        try:
            return llamar_api(payload)
        except OverloadedError:
            espera = (2 ** intento) * 15  # 15s, 30s, 60s, 120s, 240s
            time.sleep(espera)
    raise EscaladoHumano("API no disponible después de 5 retries")
```

**Prevención**: regla "ninguna llamada a API externa sin retry exponencial".
Code review enforced.

---

### AP-3.6 — Silent Exception Swallow

**Síntoma**: bloques `try/except` que capturan excepciones sin loggear ni
propagarlas.

**Ejemplos**:
```python
# El clásico:
try:
    operacion_critica()
except Exception:
    pass  # falla silenciosa

# El "camuflado":
try:
    venta_id = registrar_venta(items)
except:
    return None  # caller no sabe que falló

# El "falso log":
try:
    procesar_pago()
except Exception as e:
    print(e)  # print NO es log estructurado
```

**Causa raíz**: "no sabía qué hacer con el error, lo capturo y sigo". O
Claude generando código defensivo sin instrucción explícita.

**Violaciones**:
- **A14 Explicit Failure** (Nivel 2 universal)

**Por qué importa**:
- Sistema parece funcionar pero datos se corrompen
- Bug se descubre semanas después en producción
- Imposible debuggear: no hay traza
- Pérdida total de confianza del usuario ("a veces funciona, a veces no")

**Corrección**:
```python
import logging
logger = logging.getLogger(__name__)

try:
    venta_id = registrar_venta(items)
except DatabaseError as e:
    # SIEMPRE log con contexto
    logger.exception("DB error en registrar_venta",
                     extra={"items_count": len(items)})
    # Y propagar como error tipado (Result type, ver A14)
    return Err(error=str(e), code="DB_ERROR")
except Exception as e:
    logger.exception("Error inesperado en registrar_venta")
    return Err(error="unexpected", code="INTERNAL",
               details={"type": type(e).__name__})
```

**Prevención**:
- Linter detecta `except: pass` y `except Exception: pass` → alert
- Linter detecta `except` sin `logger.exception()` o equivalente → alert
- Code review obligatorio sobre cualquier try/except

**Aplicación a SQL**:
```
INCORRECTO:
  EXCEPTION WHEN OTHERS THEN
      NULL;   -- silent swallow en plpgsql

CORRECTO:
  EXCEPTION WHEN OTHERS THEN
      INSERT INTO error_log_sc (function_name, error_msg, error_state)
      VALUES ('mi_funcion', SQLERRM, SQLSTATE);
      RAISE;  -- propagar al caller
```

---

### AP-3.7 — Happy Path Only Testing

**Síntoma**: módulo con tests pero solo cubren el flujo cuando todo va bien.
Ratio happy:unhappy = 10:1 o peor.

**Ejemplos típicos**:
```python
# Lo que se ve comúnmente:
def test_crear_usuario():
    user = crear_usuario(email="valido@example.com", nombre="Juan")
    assert user is not None

def test_crear_usuario_otro():
    user = crear_usuario(email="otro@example.com", nombre="Pedro")
    assert user is not None

# 10 más tests todos felices...

# FALTAN:
# - test_crear_usuario_email_vacio
# - test_crear_usuario_email_invalido
# - test_crear_usuario_email_demasiado_largo
# - test_crear_usuario_nombre_null
# - test_crear_usuario_db_caida
# - test_crear_usuario_email_duplicado
# - test_crear_usuario_con_inyeccion_sql
# - test_crear_usuario_quota_excedida
# - test_crear_usuario_de_otra_empresa  (ZT)
# ...
```

**Causa raíz**: el happy path es lo "obvio". Los unhappy paths requieren
pensar adversarialmente, que es menos natural.

**Violaciones**:
- **A15 Unhappy Path First** (Nivel 2 universal)

**Por qué importa**:
- Happy path = 5% del código real, 80% del tiempo de testing si lo hacés mal
- Producción amplifica unhappy paths (1M usuarios = 1M variaciones)
- Tests felices dan falsa confianza ("todo verde, deployemos")
- Bugs aparecen en producción donde los costos son 10-100x mayores

**Corrección**: aplicar workflow de A15:
1. Listar inputs adversariales ANTES de escribir código
2. Escribir tests unhappy ANTES del happy path
3. Mantener ratio mínimo 5:1 unhappy:happy

**Catálogo de inputs adversariales** (referencia rápida):
```
- vacío: "", null, undefined, [], {}
- tamaño extremo: 0, MAX_INT, MAX_TEXT, gigabytes
- tipo incorrecto: number → string, dict → list
- encoding: "ñ", emoji, RTL, NUL byte
- inyecciones: ';DROP TABLE', '<script>', '...eval(...)'
- fechas: 1900, 2099, '0000-00-00', NaN
- decimales: 0.0000001, 1e308, -0.0
- locales: "," vs "." decimal, fechas DD/MM vs MM/DD
- timezones: UTC, +14:00, -12:00, DST transitions
- caracteres especiales: \n \r \t \0
- duplicados: misma key, mismo unique
- concurrencia: 2 ops simultáneas
- auth: token expirado, sin permisos, otro tenant (A12)
```

**Prevención**:
- CI cuenta tests por módulo, falla si ratio < 1:2 happy:unhappy
- Code review obligatorio: "¿qué unhappy paths cubre este test suite?"
- Skill futura `sigma-adversarial-testing` automatiza el catálogo

---

### AP-3.8 — Inconsistent FOR UPDATE Order

**Síntoma**: dos funciones diferentes hacen `SELECT ... FOR UPDATE` sobre las
mismas tablas pero en orden distinto. Cuando se ejecutan concurrentemente,
deadlock garantizado.

**Ejemplo del legacy (regla G23)**:
```
Función A:
  CREATE FUNCTION transferir_stock(p_origen UUID, p_destino UUID) ...
      -- Lock en orden: origen, después destino
      PERFORM 1 FROM products_sc WHERE id = p_origen FOR UPDATE;
      PERFORM 1 FROM products_sc WHERE id = p_destino FOR UPDATE;
      -- ...

Función B (en otro módulo):
  CREATE FUNCTION reservar_producto(p_principal UUID, p_secundario UUID) ...
      -- Lock en orden: principal, después secundario
      -- PERO si A llama con origen=X, destino=Y
      -- y B llama con principal=Y, secundario=X (al revés) -> DEADLOCK
      PERFORM 1 FROM products_sc WHERE id = p_principal FOR UPDATE;
      PERFORM 1 FROM products_sc WHERE id = p_secundario FOR UPDATE;
      -- ...
```

**Resultado en producción**:
- Usuario en cajero 1 transfiere stock A→B
- Simultáneamente, usuario en cajero 2 reserva producto B y A
- Función A tiene lock en A, espera lock en B
- Función B tiene lock en B, espera lock en A
- → ambas esperan eternamente, PostgreSQL detecta deadlock y cancela una
- → usuario ve error random sin saber por qué

**Causa raíz**: cada función se diseñó aisladamente, sin coordinar orden de
locks entre funciones que tocan las mismas tablas.

**Violaciones**:
- **A13 Concurrency Safety** (Nivel 2 universal)

**Por qué importa**:
- Deadlocks son intermitentes y difíciles de reproducir
- Aparecen solo bajo carga (testing en dev no los muestra)
- Cancelan transacciones a mitad de ejecución
- Compliance afectado si datos quedan parcialmente persistidos

**Corrección**: **siempre ordenar IDs antes de FOR UPDATE**:
```
CREATE FUNCTION transferir_stock(p_origen UUID, p_destino UUID) ...
    -- CRÍTICO: orden consistente entre TODAS las funciones
    PERFORM 1 FROM products_sc
    WHERE id IN (p_origen, p_destino)
    ORDER BY id   -- orden alfabético/UUID consistente
    FOR UPDATE;
    -- Ahora el resto de la lógica

CREATE FUNCTION reservar_producto(p_principal UUID, p_secundario UUID) ...
    -- MISMO PATRÓN: ORDER BY id antes de FOR UPDATE
    PERFORM 1 FROM products_sc
    WHERE id IN (p_principal, p_secundario)
    ORDER BY id   -- mismo orden que la función A
    FOR UPDATE;
```

**Regla universal**: cuando se locken 2+ filas de la misma tabla, **SIEMPRE**
usar `ORDER BY id` (o columna comparable) antes de FOR UPDATE.

**Prevención**:
- Validator detecta `FOR UPDATE` sin `ORDER BY` previo → review
- Tests adversariales de concurrencia (lanzar 100 ops simultáneas)
- Code review obligatorio sobre cualquier función con `FOR UPDATE`

---

## Categoría 4: Anti-patterns de Documentación

### AP-4.1 — Stale Documentation

**Síntoma**: docs dicen X pero el código hace Y.

**Causa raíz**: cambios al código sin actualizar docs.

**Evidencia**: universal.

**Corrección**: aplicar 6° principio rector (descubrir antes de ejecutar) al
mantenimiento de docs. Antes de declarar "está documentado", verificar que
el doc coincide con realidad.

**Prevención**:
- Tests que validan ejemplos de código en docs
- Validators automáticos (legacy tenía `verificar_runtime.py`)
- Convención: tocar código → actualizar doc en el mismo commit

---

### AP-4.2 — Documentation in Wrong Level

**Síntoma**: regla universal escrita como ADR específico, o decisión específica
escrita como principio universal.

**Ejemplo del legacy**: las "REGLAS QUE NUNCA SE ROMPEN" mezclaban Niveles 2-5:
```
Regla 1 NUNCA tablas directas → Nivel 2 universal ✓
Regla 7 Manufactura NO existe en V2 → Nivel 5 decisión ✗ (en lugar incorrecto)
```

**Corrección**: re-clasificar por nivel (proceso descrito en `PRINCIPIOS-ARQUITECTURA.md`).

**Prevención**: cada nueva regla pasa por el test de nivel antes de ubicarse:
```
1. ¿Aplica a CUALQUIER proyecto SaaS multi-tenant? → Nivel 2
2. ¿Aplica solo al stack actual (Supabase)? → Nivel 3
3. ¿Aplica solo a Stallen? → Nivel 4
4. ¿Es decisión de momento? → Nivel 5
```

---

### AP-4.3 — Implicit Decisions

**Síntoma**: el código hace X pero NO hay ADR explicando por qué.

**Causa raíz**: decisión tomada "obvia" en el momento, sin documentar.

**Evidencia**: futuro yo (o nuevo dev) lee el código y se pregunta "¿por qué
está así?". Sin ADR, riesgo de revertir la decisión "por parecer mejor".

**Corrección**: documentar la decisión retroactivamente en ADR (mejor tarde
que nunca).

**Prevención**: regla "decisión técnica no obvia → ADR antes del commit".
Para vibe coders: ADRs cortos están OK. No necesitan ser tesis. 5-10 líneas
es suficiente.

---

## Catálogo abreviado (referencia rápida)

```
ESTRUCTURALES:
  AP-1.1 Flat root explosion
  AP-1.2 Mixed concerns folder
  AP-1.3 Cross-level pollution
  AP-1.4 Hidden state

ARQUITECTÓNICOS:
  AP-2.1 God Validator
  AP-2.2 Hardcoded Domain
  AP-2.3 Inconsistent Returns
  AP-2.4 Monolithic Skill
  AP-2.5 Module Ownership Violation
  AP-2.6 Direct Table Access from Frontend
  AP-2.7 Cross-Tenant Function Parameter
  AP-2.8 Raw Table Response                  ← nuevo v1.1 (A11)
  AP-2.9 Trust Boundary Violation            ← nuevo v1.1 (A12)

PROCESO:
  AP-3.1 Mixing Cleanup with Execution
  AP-3.2 Test Code in Production
  AP-3.3 Infinite Retry without Stop Conditions
  AP-3.4 Aprendizajes Duplicados Acumulados
  AP-3.5 API Call Without Retry
  AP-3.6 Silent Exception Swallow            ← nuevo v1.1 (A14)
  AP-3.7 Happy Path Only Testing             ← nuevo v1.1 (A15)
  AP-3.8 Inconsistent FOR UPDATE Order       ← nuevo v1.1 (A13)

DOCUMENTACIÓN:
  AP-4.1 Stale Documentation
  AP-4.2 Documentation in Wrong Level
  AP-4.3 Implicit Decisions
```

---

## Cómo este documento se mantiene

**Agregar un anti-pattern nuevo**:
- Necesita 2+ manifestaciones empíricas
- Necesita causa raíz identificada
- Necesita corrección y prevención documentadas
- Si solo 1 manifestación → va al cuaderno, no acá

**Modificar un anti-pattern existente**:
- Agregar nueva evidencia (nueva manifestación, nuevo proyecto)
- Refinar la corrección con experiencia
- Mejorar prevención si se descubre mejor approach

**Eliminar un anti-pattern**:
- Casi nunca. Solo si el anti-pattern era falso (clasificación incorrecta).
- Mantener registro histórico de por qué se eliminó.

---

## Histórico de versiones

- **1.0** (2026-05-15): 19 anti-patterns (AP-1.1..AP-4.3)
- **1.1** (2026-05-15): Audit empírico de Julián detectó GAPS. Agregados:
  - AP-2.8 Raw Table Response (vinculado a A11 DAO+DTO)
  - AP-2.9 Trust Boundary Violation (vinculado a A12 Zero Trust)
  - AP-3.6 Silent Exception Swallow (vinculado a A14 Explicit Failure)
  - AP-3.7 Happy Path Only Testing (vinculado a A15 Unhappy Path First)
  - AP-3.8 Inconsistent FOR UPDATE Order (vinculado a A13 Concurrency Safety)

  Total: 24 anti-patterns.

---

Versión: 1.1 | Creado: 2026-05-15 | Última edición: 2026-05-15 (post audit empírico)
Origen: análisis legacy SigmaControl + síntesis de patrones SOLID/Harness Engineering
