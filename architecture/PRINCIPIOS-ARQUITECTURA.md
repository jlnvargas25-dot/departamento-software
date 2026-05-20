# PRINCIPIOS DE ARQUITECTURA UNIVERSAL

> **Nivel 2: arquitectura universal** | Reglas para cualquier SaaS multi-tenant
> Versión: 1.2 | Creado: 2026-05-15 | Última edición: 2026-05-15 (post audit empírico 2)

---

## Alcance

Estas reglas aplican a cualquier proyecto SaaS multi-tenant construido dentro
del Departamento. Son **agnósticas de cliente** y **agnósticas de stack
tecnológico específico**. Una violación de cualquier regla acá es una violación
arquitectónica que debe documentarse y corregirse.

**No incluye**:
- Reglas específicas de Supabase/PostgreSQL → ver `.claude/skills/`
- Reglas específicas de Stallen → ver `domain-captures/stallen-domain.md`
- Decisiones específicas del proyecto/momento → ver `decisions/`

**Nota de sintaxis**: los ejemplos PostgreSQL usan delimitador `$BODY$` en lugar
de `$$` para evitar conflictos de parsing en herramientas de edición. Ambos
son sintaxis válida y equivalente en PostgreSQL.

---

## A1 — Module Ownership (Propiedad de datos por módulo)

> **Cada módulo de dominio es DUEÑO de sus datos. Solo él puede escribir en
> sus tablas. Los demás módulos consumen vía interface explícita.**

### Definición

Un módulo (Inventario, CRM, Caja, etc.) tiene un conjunto de tablas que **posee
exclusivamente**:
- Solo ese módulo hace INSERT/UPDATE/DELETE en sus tablas
- Otros módulos LEEN solo a través de funciones/RPCs públicas del dueño
- Los datos críticos NUNCA son compartidos en ownership

### Por qué importa

Sin ownership claro, en producción tenés:
- Bug en módulo A modifica datos del módulo B → debugging imposible
- Cambios de schema de B rompen A silenciosamente
- Responsabilidad difusa cuando algo falla
- Imposible refactorear un módulo sin tocar todos los demás

### Patrón correcto

```
Módulo Inventario es dueño de:
  - products_sc
  - inventory_movements (inmutable)
  - stock_alerts

Solo Inventario puede:
  - INSERT INTO products_sc
  - INSERT INTO inventory_movements
  - INSERT/UPDATE/DELETE INTO stock_alerts

Otros módulos:
  - Caja consume Inventario via: Inventario.registrar_salida(p_product_id, p_cantidad)
  - Reportes consume Inventario via: Inventario.get_inventario() (read-only RPC)
  - NUNCA: Caja hace INSERT INTO inventory_movements directamente
```

### Anti-patrón conocido (del legacy)

Caja hacía `ALTER TABLE customers ADD COLUMN limite_credito` cuando customers
era propiedad de CRM. Resultado: 6 módulos contaminados, refactor caro.

### Cómo verificar

Antes de hacer commit:
```
□ ¿Esta migración modifica solo tablas del módulo declarado?
□ ¿Los INSERTs son solo en tablas propias?
□ ¿Las consultas a otras tablas usan RPCs públicas del dueño?
```

---

## A2 — Encapsulación de tablas (NUNCA tabla directa, SIEMPRE interface)

> **Las tablas son detalles de implementación. La interface pública de un módulo
> son sus RPCs/eventos, NO sus tablas.**

### Definición

Una tabla NO es la interface de un módulo. Es su implementación. La interface
debe ser explícita:
- **Lectura**: RPCs con `SECURITY DEFINER` que retornan datos filtrados
- **Escritura**: RPCs públicas que reciben parámetros tipados
- **Eventos**: publicación al bus de integración con payload tipado

### Por qué importa

Sin encapsulación:
- Cambiar nombre de columna rompe TODO consumer
- Imposible agregar validación centralizada
- RLS se aplica a queries directas pero NO a la lógica de negocio
- Multi-tenant requiere filtros repetidos en cada query

### Patrón correcto

```sql
-- INCORRECTO (acceso directo a tabla):
SELECT * FROM products_sc WHERE company_id = (...)

-- CORRECTO (via RPC encapsulada):
SELECT * FROM get_inventario();  -- la RPC ya hace el filtro multi-tenant
```

### Implicación: RPCs con SECURITY DEFINER

Toda RPC pública:
- Tiene `SECURITY DEFINER` (corre con privilegios del owner, no del caller)
- Tiene `SET search_path = public` (no contamina con paths externos)
- Filtra multi-tenant internamente (`get_my_*_company_id()`)
- Valida inputs ANTES de la operación

### Anti-patrón conocido (del legacy)

Frontend hacía `supabase.from('products').select()` directamente. Cuando el
modelo de datos cambió, rompió 14 componentes a la vez. La solución fue mover
todo a RPCs encapsuladas.

---

## A3 — Inter-Module Contracts (Contratos explícitos entre módulos)

> **Las dependencias entre módulos son contratos formales: firma exacta,
> pre/post-condiciones, errores documentados.**

### Definición

Cuando módulo A depende de módulo B, NO depende de "B existe". Depende de
**una interface contractual específica**:

```
Contrato: Caja → Inventario

FUNCIÓN: registrar_salida(
    p_product_id UUID,        -- producto a egresar
    p_cantidad NUMERIC,       -- cantidad a egresar
    p_referencia TEXT,        -- venta_id u otro contexto
    p_notas TEXT              -- nota opcional
) → BOOLEAN

PRECONDICIÓN:    stock_actual >= p_cantidad
POSTCONDICIÓN:   stock reducido en p_cantidad
                 fila nueva en inventory_movements
ERROR SI:        stock insuficiente → RAISE 'stock insuficiente'
INMUTABILIDAD:   inventory_movements no se modifica, solo se inserta

Thread que CREA esta interface:   Thread N (Inventario)
Thread que CONSUME esta interface: Thread M (Caja)
```

### Por qué importa

Sin contratos formales:
- Bugs por firma incompatible (Caja llama con 4 params, función tiene 3)
- Imposible cambiar implementación de B sin coordinar manualmente con A
- Imposible auto-validar
- Sin auditabilidad de quién depende de qué

### Patrón correcto

Cada proyecto tiene un archivo `contratos-entre-modulos.md` que lista todos
los contratos vigentes. Antes de cada commit:
- Si modificás interface pública → actualizás el contrato + notificás consumers
- Si rompés contrato → es breaking change, requiere versión nueva

### Validación automática

Es posible (y deseable) validar contratos automáticamente:
- Parser SQL extrae firmas reales del código
- Compara con contratos declarados
- Detecta drift entre implementación y contrato
- Falla el build si hay discrepancia

El legacy implementó esto en `core/contratos.py` con 5 contratos:
- `verificar_handoff` (output de construir)
- `verificar_resultado_ejecutar` (output de ejecución SQL)
- `verificar_resultado_deploy` (output de deploy)
- `verificar_grafo` (grafo de dependencias)
- `verificar_estado` (estado del pipeline)

---

## A4 — Acíclicidad de Dependencias (Sin ciclos en el grafo)

> **El grafo de dependencias entre módulos DEBE ser acíclico. Cualquier ciclo
> es bug de diseño que se resuelve con bus de eventos.**

### Definición

```
CORRECTO (acíclico):
  Inventario → (sin dependencias)
  CRM        → (sin dependencias)
  Caja       → Inventario, CRM
  Reportes   → Caja, Inventario, CRM

INCORRECTO (cíclico):
  A → B → C → A    (ciclo de 3)
  A → B → A        (ciclo directo)
```

### Por qué importa

Ciclos en dependencias generan:
- Imposibilidad de construir incrementalmente (todo debe coexistir)
- Cambios en cascada impredecibles
- Tests imposibles de aislar
- Refactoring atascado

### Cómo romper ciclos

Cuando aparece un ciclo, la solución NO es eliminar una dependencia. Es
**convertir la dependencia bidireccional en eventos asincrónicos**:

```
INCORRECTO (ciclo):
  Caja → CRM (registrar_interaccion)
  CRM  → Caja (notificar_descuento_loyalty)

CORRECTO (bus de eventos):
  Caja publica evento "venta_registrada"
    CRM consume: registra interacción
  CRM publica evento "descuento_disponible"
    Caja consume: aplica en próxima venta
  → Acoplamiento bajo, sin ciclo directo
```

### Validación automática

Es posible (y deseable) validar acíclicidad:
- Construir grafo de dependencias declaradas
- Aplicar topological sort
- Si falla → reportar el ciclo exacto
- Fallar el build hasta resolverlo

El legacy implementó esto en `core/contratos.py`:
```python
def verificar_grafo(grafo):
    # ... detecta ciclos directos A→B→A
    for tid, info in threads.items():
        for dep in info.get("dependencias", []):
            dep_info = threads.get(dep, {})
            if tid in dep_info.get("dependencias", []):
                v.append(f"ciclo directo: Thread {tid} ↔ Thread {dep}")
```

---

## A5 — Multi-tenant Strict Isolation (Aislamiento estricto entre tenants)

> **En sistemas multi-tenant, TODA tabla de dominio tiene campo de tenant, TODO
> query lo filtra. Sin excepciones.**

### Definición

Cuando un sistema atiende múltiples clientes/empresas/organizaciones:
- Cada tabla de dominio tiene `tenant_id` (o equivalente: `company_id`, `org_id`)
- El campo es NOT NULL siempre
- Todo SELECT filtra por tenant (idealmente via RLS automático)
- Todo INSERT setea el tenant explícitamente
- NUNCA hay funciones "across tenants" salvo administrativas privilegiadas

### Por qué importa

Una falla de aislamiento es **breach de seguridad/privacidad crítico**:
- Cliente A ve datos de Cliente B
- Compliance violation (GDPR, HIPAA, etc.)
- Pérdida total de confianza
- Posible responsabilidad legal

### Patrón correcto (Supabase con RLS)

```sql
-- 1. Toda tabla tiene company_id NOT NULL
CREATE TABLE products_sc (
    id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id  UUID NOT NULL REFERENCES companies_sc(id),
    name        TEXT NOT NULL
);

-- 2. RLS activado en toda tabla de dominio
ALTER TABLE products_sc ENABLE ROW LEVEL SECURITY;

-- 3. 4 policies por tabla (SELECT, INSERT, UPDATE, DELETE)
CREATE POLICY "products_select" ON products_sc
    FOR SELECT USING (company_id = (SELECT get_my_sc_company_id()));

CREATE POLICY "products_insert" ON products_sc
    FOR INSERT WITH CHECK (company_id = (SELECT get_my_sc_company_id()));

-- 4. RPCs SIEMPRE filtran multi-tenant internamente
CREATE FUNCTION get_inventario() RETURNS SETOF products_sc
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
BEGIN
    RETURN QUERY
    SELECT * FROM products_sc
    WHERE company_id = get_my_sc_company_id()
    LIMIT 50;
END;
$BODY$;
```

### Anti-patrón conocido (del legacy)

Función `evaluar_alertas_todas_empresas(p_company_id UUID)` que recibía
`company_id` como **parámetro externo**. Resultado: cualquier usuario podía
pedir alertas de cualquier empresa. **Falla crítica de seguridad**.

Solución: la función NO recibe `company_id`. Lo obtiene internamente con
`get_my_sc_company_id()` que lee del JWT auth.

### Implicación para validación

El MCP server `sigma-validators-r` debe DETECTAR esta clase de violación:
- Función con parámetro `p_company_id UUID` → alert
- Función pública sin `get_my_*_company_id()` interno → alert
- Tabla creada sin `company_id NOT NULL` → alert
- Tabla sin RLS habilitado → alert
- Tabla con RLS pero sin las 4 policies → alert

---

## A6 — Immutability for Audit (Eventos inmutables para auditabilidad)

> **Ciertas tablas son INMUTABLES por compliance: historial de movimientos,
> interacciones, transacciones. NUNCA UPDATE ni DELETE en ellas.**

### Definición

Tablas que registran eventos históricos NUNCA pueden modificarse después de
insertarse:
- Movimientos de inventario
- Interacciones con clientes
- Transacciones financieras
- Audit logs
- Records de compliance

Para "corregir" un evento incorrecto, se registra un **nuevo evento de ajuste**,
no se edita el original.

### Por qué importa

Sin inmutabilidad:
- Compliance violado (audit trail no confiable)
- Imposible reconstruir historial real
- Disputas legales sin evidencia
- Bug que sobrescribe datos históricos sin posibilidad de recuperación

### Patrón correcto

```sql
-- Solo políticas SELECT e INSERT, NUNCA UPDATE/DELETE
CREATE POLICY "inv_mov_select" ON inventory_movements
    FOR SELECT USING (company_id = get_my_sc_company_id());

CREATE POLICY "inv_mov_insert" ON inventory_movements
    FOR INSERT WITH CHECK (company_id = get_my_sc_company_id());

-- NUNCA crear estas para tablas inmutables:
-- CREATE POLICY "..." ON inventory_movements FOR UPDATE ...
-- CREATE POLICY "..." ON inventory_movements FOR DELETE ...
```

### Cómo declarar tablas inmutables

Cada cliente declara sus tablas inmutables en su `domain-capture`:

```yaml
# stallen-domain.md
inmutables:
  - inventory_movements
  - customer_interactions
  - sales_transactions
```

El validator universal lee esta config y enforces:
- Si una migración crea política UPDATE/DELETE para tabla inmutable → alert
- Si una migración crea trigger AFTER UPDATE en tabla inmutable → alert

---

## A7 — Domain Validation Before Implementation

> **Captura y valida el dominio ANTES de implementar técnicamente. El código
> implementa lo que el dominio dice, no al revés.**

### Definición

Antes de escribir SQL/código:
1. Capturar el dominio en lenguaje de negocio
2. Validar con stakeholder (humano que conoce el dominio)
3. Documentar invariantes del dominio
4. SOLO después: implementar

### Por qué importa

Sin captura previa:
- Código implementa modelo mental incorrecto
- Bugs aparecen como "comportamiento inesperado"
- Refactor doloroso cuando el modelo real diverge del código

### Patrón correcto

```
Capa 1 — DOMINIO (lenguaje de negocio):
  "Una cita SIEMPRE tiene un servicio asociado."
  "Un servicio puede tener variantes (corte adulto, corte niño)."
  "El precio de una variante puede sobrescribir el precio del servicio base."
  "Una cita cancelada antes de 24h libera el horario."
  → Stakeholder valida cada afirmación: sí/no

Capa 2 — INVARIANTES (reglas técnicas):
  → INV-001: cita.servicio_id NOT NULL FK to services_sc
  → INV-002: variante.precio_override NULL o > 0
  → INV-003: trigger libera horario si cita.cancelada_at < cita.inicio - 24h

Capa 3 — IMPLEMENTACIÓN:
  → SQL que materializa los invariantes
```

### Implementación del Departamento

Esta regla se materializa via el skill `sigma-capture-domain`:
- Steps 1-3: captura del dominio en lenguaje natural
- Step 4: validación con stakeholder
- Step 5: traducción a invariantes técnicos
- Step 6: produce `domain-captures/<cliente>-domain.md`

---

## A8 — Idempotency or Explicit Rollback

> **Toda operación que modifica estado DEBE ser idempotente O tener rollback
> explícito. NUNCA mutación irreversible sin plan de reverso.**

### Definición

Operaciones de mutación tienen 2 garantías mínimas posibles:

**Opción 1: Idempotente**
- Ejecutar 2 veces produce el mismo resultado que 1 vez
- Ejemplo: `UPDATE x SET status='active' WHERE id=Y` (siempre llega a active)

**Opción 2: Con rollback explícito**
- Operación NO es idempotente
- Pero existe operación inversa documentada
- Ejemplo: migración SQL viene con DROPs para revertir todo

NUNCA aceptar: operación que muta estado, no es idempotente, y no tiene reverso.

### Por qué importa

Sin esta regla:
- Re-ejecutar un script accidentalmente corrompe datos
- Imposible recuperarse de errores de deploy
- Falla en producción = pánico sin opciones

### Patrón correcto (migraciones SQL)

```sql
-- ESTRUCTURA OBLIGATORIA DE MIGRACIÓN:

-- PARTE 1: Forward (la migración)
CREATE TABLE products_sc (...);
CREATE FUNCTION registrar_entrada(...);
CREATE TRIGGER ...;

-- PARTE 2: Rollback explícito (orden inverso)
DROP TRIGGER IF EXISTS ...;
DROP FUNCTION IF EXISTS registrar_entrada(...);
DROP TABLE IF EXISTS products_sc;
```

El validator universal verifica:
- Toda tabla creada tiene su `DROP IF EXISTS` en el rollback
- Toda función creada tiene su `DROP IF EXISTS` en el rollback
- Todo trigger creado tiene su `DROP IF EXISTS` en el rollback
- Orden del rollback es inverso al forward

### Anti-patrón conocido (del legacy)

Migración 17 de SigmaControl creó tabla `sessions_sc` sin rollback. Cuando
Supabase Auth resolvió el caso de uso, hubo que mantener `sessions_sc` aunque
estaba vacía y no se usaba — borrarla requería migración manual fuera de banda.

---

## A9 — Stop Conditions Explicit (Condiciones de parada explícitas)

> **Todo proceso autónomo tiene límites explícitos: qué resuelve solo, qué
> escala a humano. Sin línea clara, el sistema entra en loops infinitos.**

### Definición

Cualquier agente/worker/skill que ejecuta autónomamente debe declarar:

**Límite 1: Reintentos**
- Cuántas veces reintenta una operación antes de escalar
- Típico: 3 intentos con backoff exponencial

**Límite 2: Profundidad de recursión**
- Cuántos niveles de delegación permite
- Típico: 2-3 niveles, después escala

**Límite 3: Tiempo total**
- Cuánto tiempo máximo en una tarea
- Típico: timeout explícito que mata el proceso

**Límite 4: Confidence threshold**
- Si el agente no está seguro, ESCALA en vez de inventar
- "No sé" es respuesta válida

### Por qué importa

Sin condiciones de parada:
- Agentes en loops infinitos quemando tokens
- Decisiones tomadas "porque parecía correcto" en vez de "porque lo verifiqué"
- Costos explosivos sin valor entregado
- Imposibilidad de saber cuándo intervenir manualmente

### Patrón correcto (del legacy)

```python
# Para todo worker:
RETRY_LIMIT = 3
BACKOFF_SECONDS = [15, 30, 60]  # exponencial

# Para llamadas a API:
def llamar_api_con_retry(payload):
    for intento in range(RETRY_LIMIT):
        try:
            return llamar_api(payload)
        except OverloadedError:
            if intento < RETRY_LIMIT - 1:
                time.sleep(BACKOFF_SECONDS[intento])
                continue
            else:
                escalar_a_humano(f"API no responde después de {RETRY_LIMIT} reintentos")
                raise

# Para construcción de threads:
if thread_fallido_count >= 3:
    fase = "p0_replanning"
    escalar_a_humano("Thread no puede completarse, requiere replan")
```

### Implementación del Departamento

Esta regla se materializa via:
- Skills explícitas (`sigma-stop-conditions`)
- Retry logic en MCP servers
- ADRs que documentan thresholds específicos

---

## A10 — No Test Code in Production Artifacts

> **El código de producción NO contiene funciones de prueba/smoke/debug.
> Estas viven separadas en suite de tests.**

### Definición

Los LLMs tienen tendencia a "verificar su trabajo" agregando funciones de
prueba inline:

```sql
-- LLM agrega sin pedírselo:
CREATE FUNCTION smoke_test_products_sc() ...
CREATE FUNCTION verify_rls_isolation() ...
CREATE FUNCTION debug_check_constraints() ...
```

Estas funciones:
- Quedan en producción consumiendo espacio
- Pueden tener permisos relajados que comprometen seguridad
- Confunden a otros desarrolladores
- Aumentan superficie de ataque

### Patrón correcto

```sql
-- Migración de producción contiene SOLO:
-- - Objetos del dominio (tablas, funciones reales, RPCs)
-- - Datos semilla reales (no de prueba)
-- - Rollback

-- NO contiene:
-- - CREATE FUNCTION smoke_test_*, test_*, debug_*, verify_*
-- - INSERT con datos ficticios
-- - SELECT * FROM tabla; sin propósito
```

### Detección automática

Patrones a detectar:
```python
PATRONES_TEST_CODE = [
    r'CREATE.*FUNCTION.*smoke_test',
    r'CREATE.*FUNCTION.*test_\w+',
    r'CREATE.*FUNCTION.*\w+_test\b',
    r'CREATE.*FUNCTION.*prueba_',
    r'CREATE.*FUNCTION.*debug_',
    r'CREATE.*FUNCTION.*verify_',
    r'CREATE.*FUNCTION.*verificar_',
]
```

Si el validator detecta → eliminar automáticamente o rechazar el commit.

### Aplica a cualquier stack

```python
# NO en módulo Python de producción:
def test_conexion_bd():
    pass

# NO en código TypeScript de producción:
function smoke_test_auth() {}
```

---

## A11 — DAO + DTO (Patrones de acceso a datos)

> **Las tablas son detalles internos. La interface pública del sistema son DAOs
> (Data Access Objects) que retornan DTOs (Data Transfer Objects). NUNCA
> exponés filas crudas como respuesta API.**

### Definición

Dos patrones clásicos (Gang of Four / industria) trabajando juntos:

**DAO (Data Access Object)**:
- Encapsula el acceso a datos
- Oculta la estructura de tablas
- En Supabase = RPC `SECURITY DEFINER` que filtra, valida, y retorna

**DTO (Data Transfer Object)**:
- Objeto/estructura usada para transferir datos entre capas
- NO es la entidad de dominio
- NO es la fila cruda de la tabla
- Tiene SOLO los campos que el consumidor necesita

Juntos: el DAO retorna DTOs, no filas.

### Por qué importa

Sin DAO + DTO:
- API expone schema interno (acoplamiento frágil)
- Cambiar nombre de columna rompe consumidores
- Filtración de información (columnas internas, soft-delete flags, audit trail)
- Imposible versionar la API sin migrar BD
- Frontend depende de estructura física, no contrato lógico

### Patrón correcto

```sql
-- DAO: RPC con SECURITY DEFINER
CREATE OR REPLACE FUNCTION get_productos_para_venta()
RETURNS TABLE (
    id UUID,
    nombre TEXT,
    precio NUMERIC,
    stock_actual NUMERIC,
    categoria TEXT
)
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_company_id UUID := get_my_sc_company_id();
BEGIN
    RETURN QUERY
    SELECT
        p.id,                         -- DTO field
        p.name AS nombre,             -- DTO field (renombrado)
        p.precio_venta AS precio,     -- DTO field (renombrado por dominio)
        p.stock_actual,               -- DTO field
        c.nombre AS categoria         -- DTO field (join)
        -- NO retorna campos internos:
        -- p.created_by_user_id   ← interno
        -- p.deleted_at           ← soft-delete flag
        -- p.notes_internal       ← campo de admin
        -- p.cost_internal        ← información sensible
    FROM products_sc p
    LEFT JOIN categories_sc c ON c.id = p.category_id
    WHERE p.company_id = v_company_id
      AND p.deleted_at IS NULL
      AND p.stock_actual > 0
      AND p.activo = true
    ORDER BY p.name
    LIMIT 100;
END;
$BODY$;
```

### Anti-pattern conocido (del legacy)

Frontend hacía `supabase.from('products_sc').select('*')`:
- Expuso campos internos `created_by_user_id`, `cost_internal`, `notes_internal`
- Cuando schema cambió, 14 componentes se rompieron simultáneamente
- Imposible refactorear backend sin coordinar 14 frontends

Ver AP-2.6 en `ANTI-PATRONES.md` para detalle.

### Cómo verificar

Validaciones automáticas posibles:
```python
# 1. Frontend NO usa .from()
linter_rule_FE_1 = "forbid: supabase.from(...)"
linter_rule_FE_2 = "only allow: supabase.rpc(...)"

# 2. RPCs NO usan SELECT * (excepto en SETOF tabla declarado)
validator_rule = "forbid in SQL: SELECT * FROM tabla as DTO response"

# 3. RPCs declaran columnas en RETURNS TABLE
validator_rule = "prefer: RETURNS TABLE (...) over RETURNS SETOF tabla"
```

### Variaciones aceptables

No todo necesita DTO complejo. Para casos simples:
- DTO = subset directo de columnas → OK
- DTO = JSON con shape específica → OK para casos complejos
- DTO = view tipada → OK si se respeta el contrato

Lo importante: el caller NUNCA recibe la fila cruda como contract.

---

## A12 — Zero Trust (Never trust, always verify)

> **Asumí que CADA request es potencialmente malicioso. Validá en cada hop,
> no solo en perímetro. No confíes en autenticación previa, en input "del
> frontend", o en parámetros recibidos.**

### Definición

Zero Trust es framework de seguridad formalizado (NIST 800-207, BeyondCorp
Google 2014, modelo de Forrester). Principio central: **"Never trust, always
verify"**.

Contrasta con modelo perimeter-based tradicional:
- INCORRECTO: "Una vez dentro del perímetro, todo es seguro"
- CORRECTO: "Cada operación se autentica + autoriza + valida + audita"

### Aplicaciones a SaaS multi-tenant

**6 reglas concretas de Zero Trust**:

```
ZT-1: El tenant se lee del JWT, NUNCA del parámetro
ZT-2: Defense in depth: RLS + función filter + auth check (no uno solo)
ZT-3: Input validation aunque venga del "frontend autorizado"
ZT-4: Authorization explícita por operación (no implícita por sesión)
ZT-5: Audit log de operaciones sensibles
ZT-6: Logs NO contienen secretos (passwords, tokens, PII innecesaria)
```

### Patrón correcto

```sql
CREATE OR REPLACE FUNCTION cambiar_password(p_new_password TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    -- ZT-1: tenant y user del JWT, NUNCA de parámetros
    v_company_id UUID := get_my_sc_company_id();
    v_user_id UUID := auth.uid();
BEGIN
    -- ZT-3: validar input aunque "vino del frontend"
    IF p_new_password IS NULL OR LENGTH(p_new_password) < 8 THEN
        RAISE EXCEPTION 'password too short';
    END IF;
    -- regex que detecta password "solo letras" (demasiado débil)
    IF p_new_password ~ E'^[a-zA-Z]+\\Z' THEN
        RAISE EXCEPTION 'password too weak (only letters)';
    END IF;

    -- ZT-4: autorización explícita (no asumir que la sesión basta)
    IF NOT EXISTS (
        SELECT 1 FROM users_sc
        WHERE id = v_user_id
          AND company_id = v_company_id
          AND deleted_at IS NULL
          AND activo = true
    ) THEN
        RAISE EXCEPTION 'unauthorized: user inactive or wrong tenant';
    END IF;

    -- ZT-5: audit log de operación sensible
    INSERT INTO audit_log_sc (
        user_id, action, company_id, occurred_at, ip_address
    ) VALUES (
        v_user_id,
        'password_changed',
        v_company_id,
        now(),
        current_setting('request.headers', true)::json->>'x-real-ip'
    );

    -- ZT-6: NO loggear el password en plaintext
    -- (el log dice "password_changed", no "changed to: secretXYZ")

    -- Operación real (vía Supabase Auth admin API)
    PERFORM auth.update_user_password(v_user_id, p_new_password);

    RETURN true;
END;
$BODY$;
```

### Anti-patterns conocidos

**AP-2.7** (ya documentado): `evaluar_alertas_todas_empresas(p_company_id UUID)`
donde cualquier usuario puede pedir alertas de cualquier empresa.

**Nuevo: AP-2.9 Trust Boundary Violation** (ver `ANTI-PATRONES.md`):
Asumir que un input "interno" (del frontend, de otro módulo) ya está
validado/sanitizado. **Defense in depth: validar SIEMPRE.**

### Por qué Zero Trust importa más para vibe coders

Como **harness engineer** (no programador profesional), no podés revisar
cada línea de código que Claude genera. Zero Trust como **default arquitectónico**
es tu defensa:

- Si el código generado se equivoca en validación específica → otras capas protegen
- Defense in depth significa que un error no es catastrófico
- Audit log permite detectar problemas post-hoc

Sin Zero Trust: un solo error en código generado = breach.
Con Zero Trust: necesita N errores simultáneos para fallar.

### Cómo verificar

Validaciones automáticas (parte del MCP server `sigma-validators-r`):
```
- Detectar: función pública con p_company_id, p_user_id, p_tenant_id como param
- Detectar: tabla de dominio sin RLS
- Detectar: tabla con RLS pero sin las 4 policies
- Detectar: operación crítica sin entry en audit_log_sc
- Detectar: logs que pueden contener tokens/passwords
```

---

## A13 — Concurrency Safety

> **Diseñá para concurrencia desde el inicio. Race conditions, deadlocks,
> y stale reads NO son edge cases — son comportamiento esperado en
> sistemas multi-usuario. Plan explícito para cada uno.**

### Definición

Los sistemas multi-usuario (cualquier SaaS) están sujetos a operaciones
concurrentes. Errores clásicos:

**1. Race Condition**: Dos operaciones simultáneas modifican el mismo recurso.
```
User A lee stock = 10
User B lee stock = 10
User A vende 8, escribe stock = 2
User B vende 8, escribe stock = 2  (debería ser -6, sobrevendida)
```

**2. Deadlock**: Locks en orden inconsistente.
```
Txn1: lock A, intenta lock B
Txn2: lock B, intenta lock A
→ ambas esperan eternamente
```

**3. Lost Update**: B sobrescribe cambios de A sin verlos.
```
A lee version 1, modifica nombre
B lee version 1, modifica email
A escribe (perdió email de B implícitamente)
```

**4. Phantom Read**: Query repetida ve filas distintas.
```
Txn1 lee "productos con stock > 5" → 10 productos
Txn2 inserta producto con stock 10
Txn1 lee de nuevo → 11 productos (fantasma)
```

**5. Stale Read**: Dato leído ya está obsoleto al usarlo.
```
Lee precio = $100 → cliente confirma compra
Mientras tanto, admin cambió precio a $120
Cobro = $100 (precio incorrecto)
```

### Por qué importa

Sin manejo explícito:
- Inventarios se sobre-venden
- Datos se corrompen silenciosamente
- Sistemas se quedan bloqueados (deadlocks)
- Auditoría inconsistente
- Compliance breached

### Patrón correcto (técnicas combinadas)

**Técnica 1: FOR UPDATE en orden CONSISTENTE**

```sql
CREATE OR REPLACE FUNCTION transferir_stock(
    p_origen UUID,
    p_destino UUID,
    p_cantidad NUMERIC
) RETURNS BOOLEAN
LANGUAGE plpgsql
AS $BODY$
BEGIN
    -- CRÍTICO: ordenar IDs antes de FOR UPDATE
    -- Si origen=A y destino=B, lock en orden A→B siempre
    -- (no "primero origen luego destino" que puede ser B→A)
    PERFORM 1 FROM products_sc
    WHERE id IN (p_origen, p_destino)
    ORDER BY id  -- ← orden consistente entre TODAS las funciones
    FOR UPDATE;

    -- Resto de la operación...
    RETURN true;
END;
$BODY$;
```

**Técnica 2: Optimistic locking con version**

```sql
CREATE TABLE entities_sc (
    id UUID PRIMARY KEY,
    company_id UUID NOT NULL,
    name TEXT NOT NULL,
    version BIGINT NOT NULL DEFAULT 1,
    updated_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION update_entity(
    p_id UUID,
    p_name TEXT,
    p_expected_version BIGINT
) RETURNS BOOLEAN
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_affected INT;
BEGIN
    UPDATE entities_sc
    SET name = p_name,
        version = version + 1,
        updated_at = now()
    WHERE id = p_id
      AND company_id = get_my_sc_company_id()
      AND version = p_expected_version;  -- falla si otra txn modificó

    GET DIAGNOSTICS v_affected = ROW_COUNT;
    IF v_affected = 0 THEN
        RAISE EXCEPTION 'version mismatch: another transaction modified this entity';
    END IF;

    RETURN true;
END;
$BODY$;
```

**Técnica 3: Idempotencia con idempotency_key**

```sql
CREATE TABLE ventas_sc (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    idempotency_key UUID UNIQUE NOT NULL,  -- ← clave única del cliente
    company_id UUID NOT NULL,
    total NUMERIC NOT NULL,
    created_at TIMESTAMPTZ DEFAULT now()
);

CREATE OR REPLACE FUNCTION crear_venta(
    p_idempotency_key UUID,
    p_items JSONB
) RETURNS UUID
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_existing_id UUID;
BEGIN
    -- Si la key ya existe → retornar la venta existente
    -- (cliente puede retry sin crear duplicada)
    SELECT id INTO v_existing_id
    FROM ventas_sc
    WHERE idempotency_key = p_idempotency_key
      AND company_id = get_my_sc_company_id();

    IF FOUND THEN
        RETURN v_existing_id;
    END IF;

    -- Crear nueva venta...
    INSERT INTO ventas_sc (idempotency_key, company_id, total)
    VALUES (p_idempotency_key, get_my_sc_company_id(), 0)
    RETURNING id INTO v_existing_id;

    RETURN v_existing_id;
END;
$BODY$;
```

### Anti-patterns conocidos

**Del legacy (regla G23)**:
> "G23: Dos funciones que hacen FOR UPDATE sobre las MISMAS tablas en
> ORDEN DISTINTO → deadlock garantizado si corren concurrentemente."

El validator del legacy ya detectaba esto. Vale destilarlo como AP-3.8.

**Otros anti-patterns**:
```
- UPDATE sin WHERE version = X (lost update inevitable)
- Read-then-write sin SELECT FOR UPDATE
- Operaciones "críticas" sin idempotency_key (retry causa duplicados)
- INSERT-or-UPDATE sin ON CONFLICT (race condition)
```

### Cómo verificar

Validaciones automáticas:
```
- Detectar UPDATE con WHERE id = X sin version → alert
- Detectar FOR UPDATE sin ORDER BY → review
- Detectar INSERT en tabla sensible sin idempotency_key → review
- Detectar funciones que modifican stock/balance sin FOR UPDATE → alert
- Detectar transacciones largas (> 5 segundos) → review
```

---

## A14 — Explicit Failure (Anti Silent Errors)

> **Toda operación reporta éxito o falla EXPLÍCITAMENTE. Nunca falsy/truthy
> ambiguo. Excepciones siempre loggean + se propagan o se manejan, nunca
> se swallowean.**

### Definición

Un "error silencioso" es cuando algo falla pero el sistema no lo reporta:
- Función retorna `True` aunque falló internamente
- `try/except` que swallow exception sin loggear
- Operación que falla pero retorna `[]` (vacío) en vez de error
- HTTP 200 con body `{"error": "..."}` (debería ser 4xx/5xx)
- Validation que detecta violación pero no actúa
- Logs `WARN` para errores críticos

### Por qué importa

Errores silenciosos son **el peor tipo de bug**:
- Sistema parece funcionar normalmente
- Datos se corrompen progresivamente
- Bug se descubre semanas después en producción
- Imposible debuggear retroactivamente (no hay traza)
- Pérdida de confianza del usuario ("a veces funciona, a veces no")

### Patrón correcto (Python)

```python
# CORRECTO: Result type discriminado (Python 3.10+)
from typing import Literal, Union, Generic, TypeVar
from dataclasses import dataclass
import logging

logger = logging.getLogger(__name__)
T = TypeVar('T')

@dataclass
class Ok(Generic[T]):
    kind: Literal["ok"] = "ok"
    value: T = None

@dataclass
class Err:
    kind: Literal["err"] = "err"
    error: str = ""
    code: str = "UNKNOWN"
    details: dict = None

Result = Union[Ok[T], Err]

def registrar_venta(items: list, customer_id: str) -> Result[str]:
    """
    Retorna Ok(venta_id) o Err(error, code, details).
    NUNCA retorna None ambiguo.
    """
    try:
        if not items:
            return Err(error="items vacio", code="INVALID_INPUT")
        if not customer_id:
            return Err(error="customer_id faltante", code="INVALID_INPUT")

        venta_id = ejecutar_db(items, customer_id)
        return Ok(value=venta_id)

    except DatabaseError as e:
        # SIEMPRE log antes de propagar/transformar
        logger.exception(
            "DB error en registrar_venta",
            extra={"customer_id": customer_id, "items_count": len(items)}
        )
        return Err(
            error="DB error",
            code="DB_ERROR",
            details={"original": str(e)}
        )
    except Exception as e:
        # NUNCA swallow sin log
        logger.exception("Error inesperado en registrar_venta")
        return Err(
            error="unexpected error",
            code="INTERNAL",
            details={"type": type(e).__name__}
        )

# CONSUMER (match/case Python 3.10+):
result = registrar_venta(items, customer_id)
match result:
    case Ok(value=venta_id):
        print(f"Venta creada: {venta_id}")
    case Err(code="INVALID_INPUT", error=msg):
        # manejar input invalido (HTTP 400)
        return http_400(msg)
    case Err(code="DB_ERROR"):
        # error infraestructura (HTTP 500 + alerta)
        alertar_ops()
        return http_503()
    case Err(error=msg):
        return http_500(msg)
```

### Patrón correcto (PostgreSQL)

```sql
CREATE OR REPLACE FUNCTION registrar_venta(p_items JSONB)
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_venta_id UUID;
BEGIN
    -- lógica de la operación
    INSERT INTO ventas_sc (company_id, total)
    VALUES (get_my_sc_company_id(), 0)
    RETURNING id INTO v_venta_id;

    RETURN jsonb_build_object(
        'ok', true,
        'venta_id', v_venta_id
    );
EXCEPTION
    WHEN OTHERS THEN
        -- LOG antes de transformar
        INSERT INTO error_log_sc (
            function_name, error_msg, error_state, company_id
        ) VALUES (
            'registrar_venta', SQLERRM, SQLSTATE, get_my_sc_company_id()
        );

        -- Retorno explícito de error (no silencioso)
        RETURN jsonb_build_object(
            'ok', false,
            'error', SQLERRM,
            'code', SQLSTATE
        );
END;
$BODY$;
```

### Anti-patterns conocidos

**El legacy ya detectaba algunos** (verbatim de `core/contratos.py`):
```python
# Si el resultado contiene status ERROR, no puede ser éxito
if isinstance(data, dict) and data.get("status") == "ERROR" and exito:
    v.append("resultado contiene {status:ERROR} pero exito=True — error silencioso")
```

Ver AP-3.6 en `ANTI-PATRONES.md` para catálogo completo.

### Cómo verificar

Validaciones automáticas:
```
- Detectar: try/except: pass (silent swallow) → alert
- Detectar: except sin logging.exception() o equivalente → alert
- Detectar: función que retorna None en error path sin diferenciarlo → review
- Detectar: HTTP handler que devuelve 200 con error en body → alert
- Detectar: logger.warning() para excepciones (debería ser error) → review
```

### Para vibe coders

Claude tiende a generar código con `try/except: pass` silenciosos cuando
no sabe qué hacer con un error. Validation automática que detecta esto
es **defensa crítica** porque vos no podés revisar línea por línea.

---

## A15 — Unhappy Path First (Anti Happy Path Bias)

> **Diseñá errores ANTES del flujo feliz. El happy path es el caso fácil;
> los unhappy paths son donde el sistema realmente prueba su robustez.
> Tests adversariales son obligatorios, no opcionales.**

### Definición

El **happy path bias** es la tendencia natural a diseñar/testear solo el
flujo cuando todo va bien. Resultado: el código rompe en producción cuando
algo falla porque nadie pensó en ese path.

**Unhappy paths típicos no cubiertos**:
- Inputs vacíos, gigantescos, malformados
- Tipos incorrectos (string donde se espera number)
- Inyecciones (SQL, XSS, command injection)
- UTF-8 raros, emojis, caracteres RTL
- Fechas extremas (1900, 2099, fechas negativas)
- Quotas excedidos
- Network failures, timeouts, DNS resolution
- DB caída, queue lleno, disk lleno
- Auth expirada, sin permisos
- Race conditions (ver A13)
- Datos parcialmente persistidos (operación falla a la mitad)

### Por qué importa

- Happy path = 5% del código real, 80% del tiempo de desarrollo si lo hacés mal
- Unhappy paths = 80% del código real, sin tests = todas las fallas en producción
- Producción amplifica unhappy paths (1M usuarios = 1M variaciones de input)
- Confianza del usuario se pierde más rápido por bugs raros que por features faltantes

### Patrón correcto

**Workflow**:

```
1. ANTES de escribir código, listar inputs que pueden romperlo:

   Catálogo de inputs adversariales:
   - vacío: "", null, undefined
   - tamaño extremo: 0, MAX_INT, MAX_TEXT
   - tipo incorrecto: number→string, etc
   - encoding: "ñ", emoji, RTL, NUL byte
   - inyecciones: ';DROP TABLE', '<script>'
   - fechas: 1900, 2099, '0000-00-00'
   - decimales: 0.0000001, 1e308
   - locales: "," vs "." decimal
   - timezones: UTC, +14:00, -12:00

2. Para cada input adversarial, decidir respuesta explícita:

   Input             →  Respuesta esperada
   ""                →  Err("empty", 400)
   null              →  Err("null", 400)
   very_long_text    →  Err("too long", 400)
   ';DROP TABLE'     →  Err("invalid", 400)
   1e308             →  Err("out of range")

3. Tests adversariales obligatorios:
   - Test del happy path: 1 test
   - Tests de cada unhappy path: N tests
   - Razón mínima esperada: 1 happy : 5 unhappy

4. SOLO después: implementar happy path
```

### Ejemplo concreto (registro de venta)

```python
# tests/test_registrar_venta.py

# UNHAPPY PATHS PRIMERO (escribir y fallar antes del happy path):

def test_items_vacio_retorna_error():
    result = registrar_venta(items=[], customer_id="abc")
    assert isinstance(result, Err)
    assert result.code == "INVALID_INPUT"

def test_customer_id_null_retorna_error():
    result = registrar_venta(items=[{"id": "x", "cant": 1}], customer_id=None)
    assert isinstance(result, Err)
    assert result.code == "INVALID_INPUT"

def test_item_con_cantidad_negativa_retorna_error():
    result = registrar_venta(items=[{"id": "x", "cant": -5}], customer_id="abc")
    assert isinstance(result, Err)

def test_item_con_id_inexistente_retorna_error():
    result = registrar_venta(items=[{"id": "NO-EXISTE", "cant": 1}], customer_id="abc")
    assert isinstance(result, Err)
    assert result.code == "PRODUCT_NOT_FOUND"

def test_stock_insuficiente_retorna_error():
    # setup: stock = 5
    result = registrar_venta(items=[{"id": "x", "cant": 10}], customer_id="abc")
    assert isinstance(result, Err)
    assert result.code == "STOCK_INSUFFICIENT"

def test_customer_no_pertenece_a_company_retorna_error():
    # ZT: customer de otra empresa
    result = registrar_venta(items=[{"id": "x", "cant": 1}], customer_id="OTRA_EMPRESA")
    assert isinstance(result, Err)
    assert result.code == "UNAUTHORIZED"

def test_db_caida_retorna_error_no_crashea():
    # Mock DB down
    result = registrar_venta(items=[{"id": "x", "cant": 1}], customer_id="abc")
    assert isinstance(result, Err)
    assert result.code == "DB_ERROR"

def test_idempotency_key_repetida_no_duplica():
    # Crear venta
    r1 = registrar_venta(items=[{"id": "x", "cant": 1}], customer_id="abc", idempotency_key="KEY1")
    # Retry con misma key
    r2 = registrar_venta(items=[{"id": "x", "cant": 1}], customer_id="abc", idempotency_key="KEY1")
    assert isinstance(r1, Ok) and isinstance(r2, Ok)
    assert r1.value == r2.value  # mismo venta_id

# HAPPY PATH AL FINAL (1 test):
def test_venta_valida_se_registra():
    result = registrar_venta(items=[{"id": "x", "cant": 2}], customer_id="abc")
    assert isinstance(result, Ok)
    assert result.value is not None
```

8 tests de unhappy path, 1 de happy path. Ratio ~8:1.

### Anti-pattern conocido (del legacy adversarial)

El legacy SigmaControl LO HACÍA pero NO lo formalizó (cita verbatim de
reglas_23_33.py):

> "Origen: adversarial testing (2026-04-17). El red team ejecutó 20 ataques
> contra el pipeline y encontró 11 patrones tóxicos que no tenían regla
> dedicada. Estas reglas son preventivas: nacieron de SIMULACIÓN, no de
> producción."

Esta práctica vale formalizar como regla universal A15.

### Cómo verificar

Validaciones automáticas:
```
- Detectar: módulo con tests pero ratio happy:unhappy > 1:2 → review
- Detectar: función pública sin test de inputs vacíos → review
- Detectar: función pública sin test de tipos incorrectos → review
- Tests adversariales obligatorios en CI (Sprint 4)
```

Un módulo se considera "production-ready" cuando:
- Tiene al menos 5 tests de unhappy paths por cada happy path
- Cubre todos los inputs adversariales del catálogo aplicables
- Pasa todos sin crashes (degrada gracefully)

### Para vibe coders

Claude tiende a generar happy path code primero (porque es lo "obvio").
Si NO le pedís explícitamente unhappy paths, no los genera. Tu workflow
debe forzar el orden:

1. Le pedís a Claude: "listame 10 inputs adversariales para esta función"
2. Le pedís: "escribe los tests adversariales primero"
3. Después: "implementá el happy path que los pase"

Este orden está documentado en la skill `sigma-capture-domain` y vale
reforzarlo en una skill futura `sigma-adversarial-testing`.

---

## A16 — Rate Limiting & Throttling

> **Todo endpoint público o caro DEBE tener rate limiting por tenant + usuario.
> El sistema NUNCA confía en que el cliente se autorregule. Defensa contra
> abuse, runaway costs, y noisy neighbors.**

### Definición

**Rate Limiting**: limitar la frecuencia de operaciones (requests/segundo, jobs/minuto).
**Throttling**: limitar la concurrencia (operaciones simultáneas).
**Quota**: límite total por período (de modelo de negocio, no de defensa).

Las tres son distintas y se aplican en combinación:
- Rate limit: 100 req/min por usuario, 1000 req/min por tenant
- Throttling: máximo 10 jobs concurrentes por tenant
- Quota: 100k requests/mes incluidos en plan Pro

### Dimensiones de rate limiting

```
DIMENSIÓN          PROPÓSITO                       EJEMPLO
─────────────────  ──────────────────────────────  ──────────────────
por tenant         protege contra tenant abusivo   1000 req/min/company
por usuario        protege contra usuario rogue    100 req/min/user
por endpoint       protege endpoints costosos      10 req/min en /api/heavy
por API key        protege integraciones externas  100 req/min/key
por IP             protege contra DDoS básico      100 req/min/IP (en edge)
```

Aplicar **TODAS** las relevantes, no una sola.

### Por qué importa

Sin rate limiting:
- **Un tenant en loop infinito** → DoS para los demás tenants (noisy neighbor)
- **Usuario crea bot scraper** → costos cloud/DB explotan
- **API key leaked en GitHub** → tu bill de Stripe/Twilio/Anthropic explota antes de detectarlo
- **Endpoint costoso sin protección** → 1 atacante = DB CPU 100%
- **Sin observabilidad** → imposible detectar abuse hasta que duele

Para Tier 1 commercial robust, rate limiting es **infraestructura mínima**,
equivalente arquitectónico a tener backup de DB.

### Patrón correcto

**Capa 1: Edge (CDN/WAF)** — defensa perimetral (ver A17):
- Rate limit por IP (anti-DDoS volumétrico)
- Bot detection / management
- Geographic restrictions si aplica

**Capa 2: API Gateway** — defensa de aplicación:
- Rate limit por API key
- Rate limit por IP (afinado)

**Capa 3: Aplicación** — defensa de negocio:
- Rate limit por tenant
- Rate limit por usuario
- Rate limit por endpoint costoso
- Concurrency throttling

**Implementación PostgreSQL/Supabase**:

```sql
-- Tabla de tracking (con TTL via partition o cleanup job)
CREATE TABLE rate_limit_buckets (
    bucket_key TEXT NOT NULL,        -- "tenant:UUID" o "user:UUID:endpoint:X"
    window_start TIMESTAMPTZ NOT NULL,
    count INTEGER NOT NULL DEFAULT 1,
    PRIMARY KEY (bucket_key, window_start)
);

-- Cleanup automático de buckets viejos
CREATE INDEX idx_rate_limit_cleanup ON rate_limit_buckets(window_start);

-- Función con sliding window
CREATE OR REPLACE FUNCTION check_rate_limit(
    p_bucket_key TEXT,
    p_max_per_minute INTEGER
) RETURNS BOOLEAN
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_window_start TIMESTAMPTZ := date_trunc('minute', now());
    v_current_count INTEGER;
BEGIN
    -- Incrementar contador (atomic con UPSERT)
    INSERT INTO rate_limit_buckets (bucket_key, window_start, count)
    VALUES (p_bucket_key, v_window_start, 1)
    ON CONFLICT (bucket_key, window_start)
    DO UPDATE SET count = rate_limit_buckets.count + 1
    RETURNING count INTO v_current_count;

    -- Verificar límite
    IF v_current_count > p_max_per_minute THEN
        -- ZT-5: audit log de rate limit hits para observabilidad
        INSERT INTO rate_limit_events (bucket_key, count, limit_value, occurred_at)
        VALUES (p_bucket_key, v_current_count, p_max_per_minute, now());
        RETURN FALSE;  -- bloqueado
    END IF;

    RETURN TRUE;  -- permitido
END;
$BODY$;

-- Uso en función crítica
CREATE OR REPLACE FUNCTION enviar_email_masivo(p_destinatarios JSONB)
RETURNS JSONB
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_company_id UUID := get_my_sc_company_id();
    v_user_id UUID := auth.uid();
BEGIN
    -- Rate limit por tenant (10 emails masivos/min por empresa)
    IF NOT check_rate_limit('tenant:' || v_company_id || ':bulk_email', 10) THEN
        RETURN jsonb_build_object(
            'ok', false,
            'error', 'rate limit exceeded for tenant',
            'code', 'RATE_LIMITED',
            'retry_after_seconds', 60
        );
    END IF;

    -- Rate limit por usuario (5 por min)
    IF NOT check_rate_limit('user:' || v_user_id || ':bulk_email', 5) THEN
        RETURN jsonb_build_object(
            'ok', false,
            'error', 'rate limit exceeded for user',
            'code', 'RATE_LIMITED',
            'retry_after_seconds', 60
        );
    END IF;

    -- ... operación real ...
    RETURN jsonb_build_object('ok', true);
END;
$BODY$;
```

### Backpressure (qué hacer cuando se alcanza el límite)

Opciones por orden de preferencia:

1. **HTTP 429 Too Many Requests** con `Retry-After: <seconds>` header
2. **Queue + procesamiento diferido** (si la operación tolera asincronía — ver A18)
3. **Degraded mode** (servir resultado cacheado/parcial)
4. **Cancelar request** (último recurso)

NUNCA: bloquear silenciosamente sin informar al cliente.

### Observabilidad obligatoria

```
Métricas mínimas a exponer:
- rate_limit.requests_total (counter, por bucket dimension)
- rate_limit.requests_blocked (counter, por bucket dimension)
- rate_limit.utilization (gauge: current_count / max_count)
- rate_limit.breach_rate (rate: breaches per minute)

Alertas mínimas:
- breach_rate > 100/min → atacante potencial
- utilization > 80% sostenido → considerar ajustar límite
- mismo bucket bloqueado >50 veces/min → escalation
```

### Por qué importa más para vibe coders

Como harness engineer, NO vas a poder reaccionar rápido a un abuse en
producción:
- No vas a estar 24/7 mirando dashboards
- Tu costo cloud puede triplicarse en una hora sin que lo notes
- Un solo atacante puede arruinar tu día (y tu mes)

Rate limiting como **default arquitectónico** es defensa pasiva: el sistema
se protege solo, vos te enterás post-hoc por la métrica.

### Anti-pattern conocido

Ver **AP-2.10 Unbounded API Surface** en `ANTI-PATRONES.md`.

### Cómo verificar

Validaciones automáticas:
```
- Detectar: endpoint público sin check_rate_limit() → alert
- Detectar: función costosa (con bucle, JOIN N tablas, llamada externa) sin rate limit → review
- Detectar: API endpoint que no documenta su rate limit en OpenAPI → review
- Métricas: alerta si rate_limit.breach_rate > 10/min sostenido
```

---

## A17 — Edge Protection (CDN + WAF + DDoS Mitigation)

> **Sistema público Tier 1 DEBE tener edge protection: CDN para cachear estático,
> WAF para filtrar ataques conocidos, DDoS mitigation para sobrevivir floods.
> NO es opcional para producción comercial.**

### Definición

**Edge Protection** = capa de defensa antes de que el tráfico llegue a tu
aplicación. Tres componentes:

1. **CDN (Content Delivery Network)**: cachea assets estáticos, sirve desde
   edge cerca del usuario. Reduce latencia + carga del origin.

2. **WAF (Web Application Firewall)**: filtra requests maliciosos en edge.
   Detecta SQL injection, XSS, RCE, path traversal, etc. ANTES de que lleguen
   a tu app.

3. **DDoS Mitigation**: absorbe floods volumétricos (capa 3-4) y aplicativos
   (capa 7). Sin esto, un script kiddie con $5 puede tirar tu app.

### Por qué importa

Sin edge protection:
- **SQL injection en input no esperado** → BD comprometida (aunque tengas A12)
- **XSS en frontend** → robo de sesiones
- **DDoS de $5** → app inaccesible mientras dure el ataque
- **Bots scrapean APIs** → costos + degradación
- **Latencia alta global** → pierdes usuarios geográficamente distantes
- **Origin sobrecargado** → cae fácilmente bajo cualquier spike

Para Tier 1, edge protection es **infraestructura mínima**, como tener HTTPS.

### Implementaciones válidas

| Proveedor | Tipo | Notas |
|---|---|---|
| **Cloudflare** | CDN + WAF + DDoS + Bot mgmt | Free tier suficiente para arrancar. Muy popular. |
| **AWS CloudFront + WAF + Shield** | CDN + WAF + DDoS | Integración con AWS. Shield Standard incluido. |
| **Fastly** | CDN + WAF | Edge compute potente. Precio premium. |
| **Bunny.net** | CDN + WAF | Económico. Más simple que los anteriores. |
| **Akamai** | CDN + WAF + DDoS | Enterprise. Muy caro pero muy capaz. |
| **Vercel** | CDN integrado + DDoS | Si ya usás Vercel para hosting, viene incluido. |

La **decisión específica de proveedor va en ADR del proyecto**. La regla
universal es: TENER edge protection, no qué proveedor.

### Configuración mínima requerida

**Para CDN**:
```
- Cachear assets estáticos (JS, CSS, imágenes) con max-age largo
- Cachear responses API GET cuando aplique (con vary headers correctos)
- TLS termination en edge (HTTPS obligatorio)
- HTTP/2 o HTTP/3
```

**Para WAF**:
```
- Reglas OWASP Core Rule Set habilitadas (SQL injection, XSS, etc.)
- Reglas custom para endpoints sensibles
- Block + log de matches (no solo log)
- Geographic restrictions si aplica (ej: bloquear países donde no operás)
```

**Para DDoS Mitigation**:
```
- Always-on (no on-demand)
- Capa 3-4: protección volumétrica automática
- Capa 7: rate limiting por IP en edge (complementa A16)
- Challenge mode (CAPTCHA/JavaScript) para tráfico sospechoso
```

### Por qué importa más para vibe coders

Como harness engineer en Tier 1:
- NO podés diagnosticar/mitigar un ataque DDoS en producción
- NO querés que tu primera lección de seguridad sea un incidente real
- Cloudflare free tier (5 minutos de setup) te da el 80% de defensa

Edge protection es la inversión con MEJOR ROI de seguridad:
- Costo: $0 a $20/mes para arrancar
- Beneficio: mitigación de 90%+ de ataques automatizados

### Anti-pattern conocido

Ver **AP-2.11 Exposed Origin** en `ANTI-PATRONES.md`.

### Cómo verificar

Validaciones (semi-manuales, infrastructure-as-code-friendly):
```
- ¿El dominio público resuelve a IP de CDN, no a tu origin directo?
- ¿WAF tiene reglas OWASP CRS habilitadas?
- ¿DDoS mitigation activa (no solo "available")?
- ¿TLS termination en edge con TLS 1.3?
- ¿Origin no es directamente accesible vía IP pública?
- ¿Rate limit en edge por IP configurado?
```

Tooling como SecurityHeaders.com, SSL Labs, o Cloudflare Analytics permiten
auto-verificación.

---

## A18 — Async Processing for Heavy Tasks

> **Operaciones >2s o costosas DEBEN ejecutarse asíncronamente vía queue.
> NUNCA bloquear request HTTP con tarea pesada. Job idempotente + retry +
> observable + con DLQ.**

### Definición

**Tarea pesada** (criterios — cumple cualquiera):
- Tiempo de ejecución > 2 segundos
- Involucra llamadas a servicios externos lentos (envío email, generación PDF)
- Procesamiento batch (>100 elementos)
- Operación cara en CPU/memoria/IO
- Operación con tolerancia a latencia (usuario no necesita respuesta inmediata)

Estas tareas se **encolan**, NO se ejecutan síncronas en el handler HTTP.

### Anatomía del sistema

```
Cliente              API (handler)          Queue              Worker
─────                ────────────           ─────              ──────
POST /reporte    →   crear job + persistir
                 ←   202 Accepted + job_id
                                            job en queue
                                                          →   procesa job
                                                              actualiza status
GET /reporte/X   →   lee status
                 ←   200 + status (pending/done/failed)
                                                          →   notifica si done
```

**Componentes obligatorios**:

1. **API endpoint** que enqueue el job y retorna `202 + job_id` inmediatamente
2. **Tabla de jobs** persistente con status
3. **Queue** (Redis Streams, Postgres LISTEN/NOTIFY, AWS SQS, etc.)
4. **Worker** que consume y procesa
5. **API endpoint** para consultar status del job
6. **Dead Letter Queue (DLQ)** para jobs que fallan persistentemente
7. **Métricas** (jobs encolados, procesados, fallados, tiempo de procesamiento)

### Patrón correcto (Postgres-based queue)

```sql
-- Tabla de jobs (persistente)
CREATE TABLE jobs_sc (
    id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    company_id      UUID NOT NULL,
    created_by      UUID NOT NULL,
    job_type        TEXT NOT NULL,           -- 'generate_pdf', 'send_email_bulk', etc.
    idempotency_key UUID UNIQUE NOT NULL,    -- A8: idempotencia
    payload         JSONB NOT NULL,
    status          TEXT NOT NULL DEFAULT 'pending'
                    CHECK (status IN ('pending','processing','done','failed','dead')),
    retry_count     INTEGER NOT NULL DEFAULT 0,
    max_retries     INTEGER NOT NULL DEFAULT 3,
    result          JSONB,
    error_message   TEXT,
    enqueued_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
    started_at      TIMESTAMPTZ,
    completed_at    TIMESTAMPTZ,
    next_retry_at   TIMESTAMPTZ
);

CREATE INDEX idx_jobs_pending ON jobs_sc(next_retry_at)
    WHERE status IN ('pending');
CREATE INDEX idx_jobs_company ON jobs_sc(company_id, created_by);

-- API: enqueue job
CREATE OR REPLACE FUNCTION enqueue_job(
    p_job_type TEXT,
    p_payload JSONB,
    p_idempotency_key UUID
) RETURNS UUID
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_company_id UUID := get_my_sc_company_id();
    v_user_id UUID := auth.uid();
    v_job_id UUID;
BEGIN
    -- A8: idempotencia (mismo idempotency_key → mismo job)
    SELECT id INTO v_job_id
    FROM jobs_sc
    WHERE idempotency_key = p_idempotency_key
      AND company_id = v_company_id;

    IF FOUND THEN
        RETURN v_job_id;  -- ya existe, retornar
    END IF;

    -- A16: rate limit por tenant antes de encolar
    IF NOT check_rate_limit('tenant:' || v_company_id || ':enqueue', 100) THEN
        RAISE EXCEPTION 'rate limit exceeded';
    END IF;

    -- Crear job
    INSERT INTO jobs_sc (
        company_id, created_by, job_type,
        idempotency_key, payload
    ) VALUES (
        v_company_id, v_user_id, p_job_type,
        p_idempotency_key, p_payload
    ) RETURNING id INTO v_job_id;

    -- Notificar workers vía LISTEN/NOTIFY (o usar SKIP LOCKED en el worker)
    PERFORM pg_notify('jobs_channel', v_job_id::text);

    RETURN v_job_id;
END;
$BODY$;

-- Worker: claim job (atomic con FOR UPDATE SKIP LOCKED)
CREATE OR REPLACE FUNCTION claim_next_job()
RETURNS TABLE (
    id UUID,
    company_id UUID,
    job_type TEXT,
    payload JSONB,
    retry_count INTEGER
)
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
BEGIN
    RETURN QUERY
    UPDATE jobs_sc
    SET status = 'processing',
        started_at = now()
    WHERE id = (
        SELECT j.id
        FROM jobs_sc j
        WHERE j.status = 'pending'
          AND (j.next_retry_at IS NULL OR j.next_retry_at <= now())
        ORDER BY j.enqueued_at
        LIMIT 1
        FOR UPDATE SKIP LOCKED  -- A13: concurrency-safe
    )
    RETURNING jobs_sc.id, jobs_sc.company_id, jobs_sc.job_type,
              jobs_sc.payload, jobs_sc.retry_count;
END;
$BODY$;

-- Worker: completar job
CREATE OR REPLACE FUNCTION complete_job(
    p_job_id UUID,
    p_result JSONB
) RETURNS VOID
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
BEGIN
    UPDATE jobs_sc
    SET status = 'done',
        result = p_result,
        completed_at = now()
    WHERE id = p_job_id;
END;
$BODY$;

-- Worker: marcar fallo con retry o DLQ
CREATE OR REPLACE FUNCTION fail_job(
    p_job_id UUID,
    p_error_message TEXT
) RETURNS VOID
LANGUAGE plpgsql SECURITY DEFINER
SET search_path = public
AS $BODY$
DECLARE
    v_retry_count INTEGER;
    v_max_retries INTEGER;
BEGIN
    SELECT retry_count, max_retries INTO v_retry_count, v_max_retries
    FROM jobs_sc WHERE id = p_job_id;

    IF v_retry_count + 1 >= v_max_retries THEN
        -- DLQ: máximo de retries alcanzado
        UPDATE jobs_sc
        SET status = 'dead',
            error_message = p_error_message,
            completed_at = now()
        WHERE id = p_job_id;
    ELSE
        -- Retry con backoff exponencial
        UPDATE jobs_sc
        SET status = 'pending',
            retry_count = retry_count + 1,
            error_message = p_error_message,
            next_retry_at = now() + (interval '1 minute' * power(2, retry_count))
        WHERE id = p_job_id;
    END IF;
END;
$BODY$;
```

### Implementaciones válidas

| Queue | Notas |
|---|---|
| **PostgreSQL + LISTEN/NOTIFY + SKIP LOCKED** | Si ya tenés Postgres. Simple, transaccional. Stallen-friendly. |
| **Redis Streams / BullMQ** | Más performante. Requiere Redis adicional. |
| **AWS SQS + Lambda** | Serverless. Buena para spikes. |
| **Supabase Edge Functions + pg_cron** | Para Supabase stack. Limitado pero suficiente para arrancar. |
| **Inngest / Trigger.dev** | Managed. Buena DX. Costo recurrente. |

### Anti-pattern conocido

Ver **AP-3.9 Sync Heavy Operation** en `ANTI-PATRONES.md`.

### Cómo verificar

Validaciones automáticas:
```
- Detectar: HTTP handler con duración media > 2s en métricas → review
- Detectar: handler con bucle for > 100 iteraciones síncrono → review
- Detectar: handler con llamada a SendGrid/Stripe/etc síncrona → review
- Detectar: handler que toca > 5 tablas en una transacción → review
```

---

## A19 — External Service Resilience

> **Toda llamada a servicio externo (API, BD remota, email, payment, etc.)
> DEBE tener: timeout explícito + retry con backoff + circuit breaker +
> Result type. Una falla externa NUNCA cascadea a falla total del sistema.**

### Definición

Servicios externos típicos:
- APIs HTTP (Stripe, Twilio, SendGrid, OpenAI, etc.)
- Servicios de email (SMTP, SES, SendGrid)
- DBs remotas (réplicas, sharding)
- Servicios internos en otra zona/región
- Webhooks salientes

**Todos pueden fallar**: timeout, 5xx, 4xx, DNS error, connection refused,
rate-limited, slow response, partial response.

### Patrón obligatorio

```
TODA LLAMADA EXTERNA TIENE LAS 4 DEFENSAS:

1. TIMEOUT EXPLÍCITO
   - NO usar timeout default del cliente HTTP (suele ser muy alto)
   - Timeout específico por servicio (Stripe: 10s, email: 30s, etc.)
   - Connection timeout + read timeout separados

2. RETRY CON BACKOFF EXPONENCIAL
   - Max 3-5 retries
   - Backoff: 1s, 2s, 4s, 8s, 16s (con jitter)
   - SOLO retriar errores transitorios (5xx, timeout, conexión)
   - NUNCA retriar errores 4xx (validation, auth) — son del cliente
   - Idempotency key para POST/PUT (A8)

3. CIRCUIT BREAKER
   - Tracking de fallos consecutivos por servicio
   - Si > N fallos en M segundos → circuit OPEN (no llamar por X tiempo)
   - Después de X tiempo → circuit HALF-OPEN (probar con 1 request)
   - Si OK → CLOSED. Si falla → OPEN otra vez.

4. RESULT TYPE (no propagar excepción cruda)
   - Retornar Ok(value) | Err(code, details)
   - El caller decide si retry, fallback, degradación
   - NO lanzar excepción que rompe handler
```

### Patrón correcto (Python)

```python
import httpx
from typing import Generic, TypeVar, Union
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging
import random

logger = logging.getLogger(__name__)
T = TypeVar('T')

@dataclass
class Ok(Generic[T]):
    value: T

@dataclass
class Err:
    code: str
    message: str
    retryable: bool
    details: dict = None

# Circuit Breaker (simplified)
class CircuitBreaker:
    def __init__(self, name: str, threshold=5, timeout_seconds=60):
        self.name = name
        self.threshold = threshold
        self.timeout = timeout_seconds
        self.failures = 0
        self.last_failure = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN

    def can_attempt(self) -> bool:
        if self.state == "CLOSED":
            return True
        if self.state == "OPEN":
            if datetime.now() - self.last_failure > timedelta(seconds=self.timeout):
                self.state = "HALF_OPEN"
                return True
            return False
        # HALF_OPEN: permite 1 intento
        return True

    def record_success(self):
        self.failures = 0
        self.state = "CLOSED"

    def record_failure(self):
        self.failures += 1
        self.last_failure = datetime.now()
        if self.failures >= self.threshold:
            self.state = "OPEN"
            logger.warning(
                f"Circuit breaker OPEN for {self.name}",
                extra={"failures": self.failures}
            )

# Cliente externo con las 4 defensas
class StripeClient:
    def __init__(self):
        self.timeout = httpx.Timeout(connect=5.0, read=10.0, write=5.0, pool=5.0)
        self.breaker = CircuitBreaker("stripe", threshold=5, timeout_seconds=60)

    def charge(self, amount: int, idempotency_key: str) -> Union[Ok[dict], Err]:
        # Circuit breaker check
        if not self.breaker.can_attempt():
            return Err(
                code="CIRCUIT_OPEN",
                message="Stripe circuit breaker is open",
                retryable=True  # eventualmente vuelve a estar disponible
            )

        # Retry con backoff exponencial
        for attempt in range(5):
            try:
                with httpx.Client(timeout=self.timeout) as client:
                    response = client.post(
                        "https://api.stripe.com/v1/charges",
                        headers={"Idempotency-Key": idempotency_key},
                        data={"amount": amount}
                    )

                # 2xx = éxito
                if 200 <= response.status_code < 300:
                    self.breaker.record_success()
                    return Ok(value=response.json())

                # 4xx = error del cliente, NO retriar
                if 400 <= response.status_code < 500:
                    return Err(
                        code=f"CLIENT_ERROR_{response.status_code}",
                        message=response.json().get("error", {}).get("message"),
                        retryable=False
                    )

                # 5xx = error servidor, retriar
                if response.status_code >= 500:
                    if attempt < 4:
                        wait = (2 ** attempt) + random.uniform(0, 1)  # jitter
                        time.sleep(wait)
                        continue
                    self.breaker.record_failure()
                    return Err(
                        code="SERVER_ERROR",
                        message=f"Stripe returned {response.status_code}",
                        retryable=True
                    )

            except httpx.TimeoutException:
                if attempt < 4:
                    wait = (2 ** attempt) + random.uniform(0, 1)
                    time.sleep(wait)
                    continue
                self.breaker.record_failure()
                return Err(
                    code="TIMEOUT",
                    message="Stripe API timeout",
                    retryable=True
                )

            except httpx.RequestError as e:
                self.breaker.record_failure()
                return Err(
                    code="CONNECTION_ERROR",
                    message=str(e),
                    retryable=True
                )

# CONSUMER:
result = stripe.charge(amount=1000, idempotency_key=str(uuid4()))
match result:
    case Ok(value=charge):
        # Procesar charge exitoso
        save_charge_to_db(charge)
    case Err(code="CLIENT_ERROR_400"):
        # Error del usuario, mostrar al UI
        return http_400("Invalid card")
    case Err(code="CIRCUIT_OPEN" | "TIMEOUT" | "SERVER_ERROR", retryable=True):
        # Encolar para retry (A18) o degradar
        enqueue_retry_charge(amount, idempotency_key)
        return http_202("Charge queued for retry")
    case Err():
        # Fallback genérico
        return http_503("Payment service unavailable")
```

### Bibliotecas recomendadas

| Lenguaje | Retry+Backoff | Circuit Breaker | HTTP con timeouts |
|---|---|---|---|
| Python | `tenacity` | `pybreaker` o custom | `httpx` |
| TypeScript/Node | `p-retry` | `opossum` | `axios` con timeout |
| Go | `cenkalti/backoff` | `sony/gobreaker` | std `net/http` |

### Observabilidad obligatoria

```
Métricas por servicio externo:
- external.requests_total (counter)
- external.requests_failed (counter, por error code)
- external.latency_seconds (histogram)
- external.circuit_state (gauge: 0=closed, 1=half_open, 2=open)
- external.retry_count (histogram)

Alertas:
- latency p99 > 5s sostenido → degradación
- error rate > 5% sostenido → circuit cerca de abrirse
- circuit OPEN > 5 min → escalation
```

### Anti-pattern conocido

Ver **AP-3.10 External Call Without Timeout** en `ANTI-PATRONES.md`.

### Cómo verificar

Validaciones automáticas:
```
- Detectar: requests.get(url) sin timeout= → alert
- Detectar: httpx.get(url) sin timeout= → alert
- Detectar: llamada externa sin try/except → alert
- Detectar: handler con > 3 llamadas externas síncronas → review (mover a job)
- Métricas: alert si servicio externo tiene > 10% error rate
```

---

## Mapping a Harness Engineering Subsystems

Estas reglas materializan las 5 subsystems del harness según la disciplina formal:

| Regla A* | Subsystem Harness |
|---|---|
| A1, A2, A3 | **Instructions** (cómo organizar interfaces) |
| A4 | **Instructions** + **Verification** (acíclicidad verificable) |
| A5, A6 | **Scope** (límites de qué un módulo puede tocar) |
| A7 | **Scope** (captura previa define scope) |
| A8 | **Session Lifecycle** (rollback = recuperación) |
| A9 | **Scope** (stop conditions = límites de scope) |
| A10 | **Verification** (qué cuenta como código real) |
| A11 | **Instructions** (DAO/DTO = interfaces formales) |
| A12 | **Scope** + **Verification** (zero trust = límite + check) |
| A13 | **Verification** (concurrency checks) |
| A14 | **Verification** (explicit failure = check de retorno) |
| A15 | **Verification** (adversarial testing) |
| A16 | **Scope** (rate limiting = límite de uso) |
| A17 | **Scope** (edge protection = perímetro defensivo) |
| A18 | **Session Lifecycle** (jobs asíncronos = lifecycle separado) |
| A19 | **Verification** + **Session Lifecycle** (external = lifecycle independiente) |

---

## Mapping a SOLID

| Regla A* | Principio SOLID dominante |
|---|---|
| A1 Module Ownership | **SRP** (cada módulo = una responsabilidad) |
| A2 Encapsulación | **OCP** (interfaces estables, implementación libre de cambiar) |
| A3 Contratos | **LSP** (interface formal permite sustituir implementación) |
| A4 Acíclicidad | **DIP** (módulos dependen de abstracciones, no se entrelazan) |
| A5 Multi-tenant | **SRP** + **ISP** (cada tenant aislado, interfaces específicas) |
| A6 Inmutabilidad | **OCP** (extender via eventos nuevos, no modificar historial) |
| A7 Domain First | **DIP** (implementación depende del dominio, no al revés) |
| A8 Idempotency | **OCP** (cambiar implementación sin romper estado) |
| A9 Stop Conditions | **ISP** (cada operación tiene scope claro) |
| A10 No Test Code | **SRP** (artefactos de producción != artefactos de testing) |
| A11 DAO + DTO | **SRP** + **DIP** (separación capas, abstracción de almacenamiento) |
| A12 Zero Trust | (transversal: aplica a SRP, OCP, ISP simultáneamente) |
| A13 Concurrency Safety | **SRP** (cada txn = una unidad atómica de responsabilidad) |
| A14 Explicit Failure | **LSP** (contratos de error claros, substituibles) |
| A15 Unhappy Path First | **OCP** (sistema preparado para casos futuros sin modificar) |
| A16 Rate Limiting | **SRP** (defensa = responsabilidad separada del negocio) |
| A17 Edge Protection | **SRP** + **DIP** (defensa perimetral abstrae infra específica) |
| A18 Async Processing | **SRP** (handler ≠ worker, separación de responsabilidad) |
| A19 External Resilience | **DIP** + **LSP** (abstracción de servicio, contrato sustituible) |

---

## Cómo se evalúa una propuesta de cambio arquitectónico

Antes de agregar/modificar una regla en este documento:

```
□ ¿La regla aplica a CUALQUIER proyecto SaaS multi-tenant?
□ ¿Es agnóstica del stack tecnológico específico?
□ ¿Tiene 2+ manifestaciones empíricas en proyectos distintos?
□ ¿Está alineada con SOLID y/o Harness Engineering?
□ ¿Es verificable automáticamente (al menos en parte)?
□ ¿Tiene ejemplo de anti-pattern conocido que evita?
```

Si todas son SÍ → vale agregar/modificar.
Si alguna es NO → re-evaluar si pertenece a otro nivel.

---

## Cambios a este documento

**Cambios válidos**:
- Aparece patrón nuevo con evidencia empírica de 2+ proyectos
- Se formaliza una regla existente con vocabulario industrial
- Se identifica un anti-pattern nuevo con evidencia

**Cambios INVÁLIDOS**:
- "Stallen necesita esto" → Nivel 4 (`domain-captures/`)
- "Mi proyecto actual decidió X" → Nivel 5 (`decisions/`)
- "Cambio de stack" → Nivel 3 (`.claude/skills/`)

---

## Histórico de versiones

- **1.0** (2026-05-15): Versión inicial con reglas A1-A10
- **1.1** (2026-05-15): Audit empírico de Julián detectó 5 GAPS (DAO/DTO, Zero Trust,
  Concurrency, Explicit Failure, Unhappy Path First). Agregadas reglas A11-A15
  + mapping actualizado a Harness Engineering y SOLID.
- **1.2** (2026-05-15): 2do audit empírico de Julián detectó 4 GAPS adicionales
  (Rate Limiting, Edge Protection, Async Processing, External Service Resilience).
  Cubre **dimensión de infraestructura resiliente** que faltaba en A1-A15.
  Agregadas reglas A16-A19 + mapping actualizado.

---

Versión: 1.2 | Creado: 2026-05-15 | Última edición: 2026-05-15 (post audit empírico 2)
Origen: destilado de legacy SigmaControl (`core/contratos.py`, `skill-contratos-modulos.md`, 170+ reglas SQL)
Manifestaciones empíricas: 1 (Stallen via SigmaControl legacy)
