# ANTI-PATRONES

> **Nivel 2: arquitectura universal** | Lo que NO hacer (con evidencia empírica)
> Versión: 1.3 | Creado: 2026-05-15 | Última edición: 2026-05-20 (post audit 3 / Opción D)

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

**Total actual: 36 anti-patterns** (versión 1.3).

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

### AP-2.10 — Unbounded API Surface

**Síntoma**: endpoint público o función costosa sin rate limiting. Cualquier
usuario puede invocarlo arbitrariamente.

**Ejemplos**:
```
INCORRECTO: endpoint público sin defensa

  POST /api/enviar-email-masivo
  → cuerpo: { destinatarios: [...] }
  → NO valida frecuencia: usuario puede llamar 1000x/segundo

INCORRECTO: función costosa sin rate limit

  CREATE FUNCTION generar_reporte_anual(p_year INT) RETURNS BYTEA
  AS ...
      -- Procesa millones de filas, ~30s de cómputo
      -- Sin rate limit: 10 usuarios = 300s de DB CPU bloqueado
  ...
```

**Causa raíz**: enfoque solo en happy path. "Si funciona, listo".

**Violaciones**:
- **A16 Rate Limiting & Throttling** (Nivel 2 universal)
- Indirecta: A12 Zero Trust (no confiar en que el cliente se autorregule)

**Por qué importa**:
- **Noisy neighbor**: un tenant en loop infinito → DoS para los demás
- **Runaway costs**: API key leaked en GitHub → bill de servicio externo explota
- **Resource exhaustion**: 1 atacante con $5 = DB CPU 100% por horas
- **Bots scrapean APIs** → costos cloud + degradación
- **Sin observabilidad** → imposible detectar abuse hasta que duele

Manifestaciones típicas en producción:
- Cliente en producción reporta "lentitud aleatoria" → era otro tenant abusivo
- Bill de Stripe inesperadamente triplicado → API key leaked, atacante creando charges
- DB caída a las 3am → bot scraper en bucle infinito

**Corrección**: aplicar A16 en TODAS las dimensiones relevantes (ver A16 para
patrón completo con `check_rate_limit()` por tenant + usuario + endpoint).

**Prevención**:
- Validator detecta endpoints públicos sin `check_rate_limit()` → alert
- Validator detecta funciones costosas (bucle, JOIN N tablas, llamada externa) sin rate limit → review
- Documentación OpenAPI debe declarar rate limits por endpoint
- Code review obligatorio sobre cualquier nuevo endpoint público

---

### AP-2.11 — Exposed Origin

**Síntoma**: el origin server (donde corre tu app) es directamente accesible
desde internet. El DNS público resuelve a la IP del origin, no a un CDN/edge.

**Ejemplos**:
```
INCORRECTO:
  app.stallen.com → A record → 198.51.100.42 (Vercel/AWS directo)

  Resultado:
  - Atacante hace dig app.stallen.com, obtiene IP, ataca directamente
  - DDoS volumétrico → origin sobrecargado
  - WAF (si existe) no intercepta porque tráfico no pasa por él
  - SQL injection en endpoint no documentado → BD comprometida
  - Latencia alta para usuarios geográficamente distantes
```

```
CORRECTO:
  app.stallen.com → A/CNAME → cdn.cloudflare.com → (proxy) → origin

  Resultado:
  - Atacante obtiene IP del CDN, no del origin
  - DDoS volumétrico absorbido por CDN edge
  - WAF intercepta requests maliciosos antes del origin
  - TLS termination en edge (más rápido)
  - Assets estáticos servidos desde edge cerca del usuario
```

**Causa raíz**: "no hay tiempo para configurar Cloudflare" o "es solo MVP".
Las defensas perimetrales se posponen hasta que pasa algo grave.

**Violaciones**:
- **A17 Edge Protection (CDN + WAF + DDoS Mitigation)** (Nivel 2 universal)

**Por qué importa**:
- **DDoS de $5**: cualquier script kiddie con un booter puede tirar tu app
- **SQL injection en input no esperado**: aunque tengas A12 Zero Trust, una
  capa más de defensa ayuda
- **Sin caching edge**: cada request va al origin, costos cloud altos
- **Sin geographic restrictions**: si solo operás en LATAM, no tiene sentido
  aceptar tráfico de Rusia/China
- **Latencia alta global**: pierdes usuarios distantes

Manifestaciones típicas en producción:
- App caída por DDoS de $20 contratado por competencia
- BD comprometida por SQL injection que el WAF habría bloqueado
- Bill de AWS multiplicado x10 en un día por scraper bot
- Usuarios en Asia se quejan de "muy lento"

**Corrección**: configurar edge protection con cualquier proveedor válido
(Cloudflare es el más popular y tiene free tier). Ver A17 para configuración
mínima por proveedor.

**Prevención**:
- Pre-deploy check: `dig +short app.dominio.com` debe NO retornar IP del origin
- CI/CD validation: verificar que origin no es directamente accesible
- Monitoring: alert si tráfico inusual llega directo al origin (bypassing edge)

---

### AP-2.12 — Missing Pagination

**Síntoma**: endpoint o RPC público que retorna una lista sin LIMIT explícito.
A medida que crecen los datos, la query devuelve miles/millones de filas y
revienta el servidor, el cliente, o ambos.

**Ejemplos**:
```sql
-- INCORRECTO: sin LIMIT
CREATE FUNCTION get_all_orders()
RETURNS SETOF orders_sc AS ...
    RETURN QUERY SELECT * FROM orders_sc
    WHERE company_id = get_my_sc_company_id()
    ORDER BY created_at DESC;
    -- 1 año después: 250k filas, 30s de query, OOM en frontend
...
```

```python
# INCORRECTO: sin pagination en API
@app.get("/api/orders")
def list_orders():
    orders = db.query("SELECT * FROM orders WHERE company_id = $1", tenant_id)
    return {"orders": orders}  # puede ser 50,000 filas
```

**Causa raíz**: "en MVP solo hay 50 órdenes, no importa". El problema se
amplifica con el crecimiento natural del producto.

**Violaciones**:
- **A11 DAO + DTO** (parcial: el contrato no declara paginación)
- Performance universal: query lenta + ancho de banda + memoria cliente

**Por qué importa**:
- Producción degrada **silenciosamente** a medida que crece la data
- Cliente enterprise con 1M de órdenes → tu app se vuelve inutilizable para él
- Costo cloud explota (queries lentas, transferencia de bytes)
- UX rota (loader infinito, scroll que no termina)
- Vulnerabilidad: atacante puede pedir "todo" repetidamente → DoS por exhaustion

Manifestaciones típicas:
- "La app está lenta" después de 6 meses en producción → era falta de pagination
- Frontend crash en clientes "grandes" → cargaba 50k filas en memoria
- AWS bill 5x más alto que esperado → outbound bandwidth de queries gigantes

**Corrección**: usar **cursor-based pagination** (mejor) o offset-based
(aceptable para datasets pequeños):

```sql
-- CORRECTO: cursor-based pagination con LIMIT obligatorio + cap máximo
CREATE FUNCTION list_orders(
    p_cursor TIMESTAMPTZ DEFAULT NULL,  -- created_at del último item de la página anterior
    p_limit INT DEFAULT 50
) RETURNS TABLE (
    id UUID,
    customer_id UUID,
    total_cents BIGINT,
    status TEXT,
    created_at TIMESTAMPTZ
)
LANGUAGE plpgsql STABLE SECURITY DEFINER
SET search_path = public
AS ...
DECLARE
    v_company_id UUID := get_my_sc_company_id();
    v_safe_limit INT := LEAST(GREATEST(p_limit, 1), 100);  -- cap máximo
BEGIN
    RETURN QUERY
    SELECT o.id, o.customer_id, o.total_cents, o.status, o.created_at
    FROM orders_sc o
    WHERE o.company_id = v_company_id
      AND (p_cursor IS NULL OR o.created_at < p_cursor)
    ORDER BY o.created_at DESC
    LIMIT v_safe_limit;
END;
...
```

**Prevención**:
- Linter detecta RPCs públicas con `RETURN QUERY SELECT` sin LIMIT → alert
- Linter detecta API endpoints que retornan listas sin parámetro de paginación → review
- Validator: cada endpoint paginado documenta su `default_limit` y `max_limit`
- Tests: assertion de que `LIMIT 100` máximo es enforced incluso si client pide 10000

---

### AP-2.13 — Domain Polluted by Infrastructure

**Síntoma**: código del dominio (lógica de negocio) importa o depende
directamente de infraestructura específica (Supabase client, httpx, framework
HTTP, ORM, etc.). El dominio "sabe" de cómo se persiste o comunica, en lugar
de solo definir QUÉ hace.

**Ejemplos**:
```python
# INCORRECTO: domain/order.py importa supabase
from supabase import create_client  # ← importación de infra
from app.config import SUPABASE_URL, SUPABASE_KEY

class Order:
    def save(self):
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        client.rpc('upsert_order', self.__dict__).execute()
        # El "dominio" ahora depende de Supabase específicamente

    @classmethod
    def get(cls, id):
        client = create_client(SUPABASE_URL, SUPABASE_KEY)
        response = client.rpc('get_order', {'p_id': id}).execute()
        return cls(**response.data[0])

# INCORRECTO en use case
def cancel_order_use_case(order_id):
    client = create_client(SUPABASE_URL, SUPABASE_KEY)  # ← infra leak
    order = Order.get(order_id)
    # ...
```

**Causa raíz**: empezar sin Hexagonal Architecture y "evolucionar" sin
estructura. Es más rápido en el MVP escribir `client.rpc(...)` directamente
en la función de negocio. La deuda se acumula silenciosamente.

**Violaciones**:
- **A20 Hexagonal Architecture (Ports & Adapters)** (Nivel 2 universal)
- **DIP** (Dependency Inversion Principle): el dominio depende de infra
  concreta en lugar de una abstracción

**Por qué importa**:
- **Acoplamiento a Supabase total**: cambiar de proveedor = rewrite
- **Tests requieren BD real**: lentos, frágiles, requieren fixtures
- **Lógica de negocio mezclada con SQL/HTTP**: imposible razonar aisladamente
- **Imposible testear edge cases**: no podés simular "BD caída" o "API
  externa lenta"
- **Cambios de infra cascadean**: nuevo proveedor de email → tocar 30 archivos
- **Negocio atrapado**: tu app no puede migrar de stack sin reescribir

Manifestaciones típicas:
- Test del use case "cancel order" tarda 8s porque levanta DB real
- Quisieron probar Neon en lugar de Supabase → semanas de rewrite
- 50% del código del dominio es manejo de errores de la BD específica

**Corrección**: extraer ports, mover lógica de infra a adapters:

```python
# domain/order.py — limpio, sin imports de infra
from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

class OrderRepository(Protocol):
    def get(self, id: UUID) -> 'Order | None': ...
    def save(self, order: 'Order') -> None: ...

@dataclass
class Order:
    id: UUID
    status: str
    # lógica de negocio pura

# infrastructure/supabase/order_repository.py — adapter
from supabase import Client
from domain.order import Order, OrderRepository

class SupabaseOrderRepository(OrderRepository):
    def __init__(self, client: Client):
        self.client = client

    def get(self, id):
        response = self.client.rpc('get_order', {'p_id': str(id)}).execute()
        return Order(**response.data[0]) if response.data else None

    def save(self, order):
        self.client.rpc('upsert_order', order.__dict__).execute()
```

**Prevención**:
- `import-linter` contracts (Python) que prohiben `domain/*` importar de
  `infrastructure/*` o de librerías de infra
- Detectar: archivo en `domain/` con `from supabase import`, `import httpx`,
  `import boto3`, etc. → alert
- Detectar: archivo en `domain/` con string literal SQL → alert
- Detectar: use case que recibe Client de Supabase como parámetro → alert
- Tests del dominio: requirement de que NO toquen BD real (medir tiempo)

---

### AP-2.14 — Hardcoded Secrets

**Síntoma**: credenciales (API keys, DB passwords, tokens, JWT secrets)
escritos como strings literales en el código fuente. O committeados en
archivos `.env` versionados.

**Ejemplos**:
```python
# INCORRECTO: API key hardcoded
STRIPE_KEY = "sk_live_51HxRkLDjsKjShrV..."

# INCORRECTO: comment con secret
# TODO: rotar este token: ghp_abc123def456...

# INCORRECTO: connection string con password
DATABASE_URL = "postgresql://admin:SuperSecret123@db.host:5432/prod"
```

```
# INCORRECTO: .env committeado al repo
# .env (NO debe estar en git)
STRIPE_SECRET_KEY=sk_live_51HxRkLDjsKjShrV...
DATABASE_URL=postgresql://admin:SuperSecret123@...
JWT_SIGNING_KEY=mySigningKey123
```

```sql
-- INCORRECTO: secret en migración
INSERT INTO config (key, value)
VALUES ('stripe_secret', 'sk_live_51HxRkLDjsKjShrV...');
```

**Causa raíz**: "lo pongo acá, después lo muevo a env vars". Casi siempre,
"después" nunca llega. O el secret se descubre cuando ya hubo abuse.

**Violaciones**:
- **A22 Secrets Management** (Nivel 2 universal)
- **A12 Zero Trust** (ZT-6: logs no contienen secrets) — caso específico

**Por qué importa**:
- **Bots de scraping** de GitHub encuentran API keys en minutos
- Casos reales documentados: $50,000 USD de cargos fraudulentos en Stripe
  en 1 día por API key filtrada en repo público
- Bills de OpenAI/Anthropic explotando por API key en GitHub commit historic
- AWS keys filtradas → mining crypto en tu cuenta → bills de $10k+
- Aunque el repo sea privado, el riesgo de leak vía PR/fork/dev personal
  laptop comprometida es real
- Imposible rotar individual: si está hardcoded, requiere deploy

Manifestaciones típicas:
- "Recibí alerta de Stripe que mi API key fue usada desde IP rara" → leak
- "Bill de OpenAI me llegó $5000, no uso tanto" → key en GitHub público
- "Cliente vio un secret en el commit message" → reputación dañada

**Corrección**:
```python
# CORRECTO: env vars con validación al startup
import os

def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value

STRIPE_KEY = get_required_env("STRIPE_SECRET_KEY")
DATABASE_URL = get_required_env("DATABASE_URL")
JWT_KEY = get_required_env("JWT_SIGNING_KEY")
```

```
# CORRECTO: .gitignore
.env
.env.local
.env.production
*.pem
*.key

# .env.example (committeable, sin valores reales)
STRIPE_SECRET_KEY=sk_test_REPLACE_WITH_REAL_KEY
DATABASE_URL=postgresql://user:password@host:5432/db
JWT_SIGNING_KEY=<256-bit-random>
```

Y si ya hubo leak: **ROTACIÓN INMEDIATA en el proveedor + verificar uso
malicioso + post-mortem**. Eliminar de git history NO es suficiente.

**Prevención**:
- **gitleaks** pre-commit hook (obligatorio)
- **gitleaks** o **truffleHog** en CI/CD para cada PR
- GitHub secret scanning habilitado (gratis para repos públicos)
- Validator estático: archivo `.env` en root → alert si no está en `.gitignore`
- Validator: string literal matcheando patrones `sk_live_*`, `AKIA*`,
  `ghp_*`, `sk-ant-*`, `xoxb-*` → alert
- Validator: `logger.info(...secret_var...)` en código → alert
- Audit periódico: rotation status de todos los secrets

---

### AP-2.15 — PII Without Classification

**Síntoma**: tablas con campos de información personal identificable (PII)
sin marca explícita de clasificación, sin retention policy declarada, sin
implementación de derecho a borrado. Compliance breach esperando suceder.

**Ejemplos**:
```sql
-- INCORRECTO: tabla con PII sin clasificación ni retention
CREATE TABLE customers_sc (
    id UUID PRIMARY KEY,
    email TEXT,           -- PII pero sin marca
    phone TEXT,           -- PII pero sin marca
    full_name TEXT,       -- PII pero sin marca
    ssn TEXT,             -- PII SENSITIVE pero sin encryption
    created_at TIMESTAMPTZ
);
-- Sin COMMENT classification
-- Sin retention policy declarada
-- Sin endpoint /api/users/me/delete
-- Sin cascading de erasure a tablas relacionadas
```

```python
# INCORRECTO: log con PII
logger.info(f"User logged in: {user.email}, phone: {user.phone}")
# PII en logs sin sanitization → leak silencioso
```

```
# INCORRECTO: BI dashboard usa data real con PII
SELECT email, full_name, total_orders FROM customers
-- Analista puede identificar individuos en analytics
```

**Causa raíz**: foco en building features, compliance pospuesta hasta que un
cliente enterprise lo exige (o hasta la primera multa). "Después lo arreglamos"
aplicado a compliance regulatoria.

**Violaciones**:
- **A24 Data Lifecycle & Privacy** (Nivel 2 universal)
- Indirecta: A21 Observability (PII en logs sin sanitization)

**Por qué importa**:
- **GDPR multas**: 4% revenue global anual o €20M (lo que sea mayor)
- **CCPA multas**: $7,500 por violación intencional
- **Enterprise B2B SaaS**: requieren DPA (Data Processing Agreement) firmado
  antes de comprar. Sin compliance básica = no venta
- **Right-to-erasure**: si un usuario pide ser borrado y no podés cumplir,
  GDPR multa garantizada
- **Reputación**: data breach = pérdida de clientes existentes y futuros

Manifestaciones típicas:
- Cliente enterprise quiere comprar → pregunta por DPA → no tenés → no venta
- Usuario pide ser borrado → tu sistema no lo soporta → reportás incidente → multa
- Analista junior accede a BI con PII real → identifica gente → leak interno
- Backup viejo restored → restaurás PII que ya debió borrarse → multa

**Corrección**:

```sql
-- 1. Clasificar cada columna con COMMENT
COMMENT ON COLUMN customers_sc.email IS 'PII_BASIC: email, sujeto a erasure tras request';
COMMENT ON COLUMN customers_sc.phone IS 'PII_BASIC: phone opcional';
COMMENT ON COLUMN customers_sc.full_name IS 'PII_BASIC: nombre completo';
COMMENT ON COLUMN customers_sc.ssn IS 'PII_SENSITIVE: encrypted at rest, audit on access';
COMMENT ON COLUMN customers_sc.created_at IS 'INTERNAL: timestamp, no PII';

-- 2. Retention policy declarada (en docs/compliance/data-retention.yaml)
-- 3. Implementar endpoint de erasure (ver A24 para patrón completo)
-- 4. Trigger de erasure cascading a tablas FK
-- 5. Anonymization en BI/analytics
```

**Prevención**:
- Linter: detectar tabla nueva sin COMMENT por columna → review
- Linter: detectar `logger.info(...email...)` o `logger.info(...phone...)`
  sin masking → alert
- Validator: para cada tabla con campos PII, debe existir estrategia de
  erasure documentada
- CI check: endpoint `/api/users/me/delete` (o equivalente) existe y tiene
  tests
- Audit periódico: cada nueva columna pasa por review de clasificación PII

---

### AP-2.16 — Authorization Only in UI

**Síntoma**: el frontend oculta botones / opciones / rutas para usuarios sin
permisos, pero el backend NO valida el permiso en el endpoint correspondiente.
Cualquier usuario autenticado que llame al endpoint vía curl/Postman bypassa
toda la "seguridad".

**Ejemplos**:
```typescript
// INCORRECTO: solo UI authorization
function OrderActions({ order, currentUser }) {
  return (
    <div>
      <button>View</button>
      {currentUser.role === 'admin' && (
        <button onClick={() => deleteOrder(order.id)}>Delete</button>
      )}
      {currentUser.role === 'admin' && (
        <button onClick={() => refundOrder(order.id)}>Refund</button>
      )}
    </div>
  );
}
```

```python
# INCORRECTO: endpoint backend sin authz check
@app.delete("/api/orders/{order_id}")
def delete_order(order_id, current_user):
    # Si está autenticado, lo borra. NO chequea rol.
    db.execute("DELETE FROM orders WHERE id = $1", order_id)
    return {"ok": True}
```

Atacante:
```bash
# Empleado normal (sin rol admin) puede:
curl -X DELETE \
  -H "Authorization: Bearer $MY_TOKEN" \
  https://api.tuapp.com/api/orders/abc-123
# → 200 OK, orden eliminada
# Vertical privilege escalation: empleado → admin
```

**Causa raíz**: "el UI ya valida". Falsa premisa. El UI es código que el
cliente controla; siempre puede ser bypasseado.

**Violaciones**:
- **A25 Authorization Model** (Nivel 2 universal)
- **A12 Zero Trust** (ZT-4: authorization explícita por operación)
- **A15 Unhappy Path First** (no test de privilege escalation)

**Por qué importa**:
- **Privilege escalation vertical**: empleado normal hace operaciones de admin
- **Privilege escalation horizontal**: usuario A accede a recursos de usuario B
- **Vulnerabilidad masiva**: una sola línea faltante = pérdida total de control
- **Sin audit**: la operación no se loggea como "rol incorrecto"
- **Compliance breach**: muchas regulaciones requieren authz granular auditado

Manifestaciones típicas:
- Pen-tester encuentra que `DELETE /api/users` no chequea rol → reporta
  como Critical
- Usuario reporta que "puede ver órdenes de otra empresa" → horizontal
  escalation por falta de chequeo de tenant + rol
- Empleado curioso descubre endpoint admin por curiosidad y lo usa
- Cliente enterprise rechaza el producto en security review

**Corrección**: authz check en backend, en cada operación sensible:

```python
# CORRECTO: authz en backend
@app.delete("/api/orders/{order_id}")
def delete_order(order_id, current_user):
    require_permission(current_user, "orders.delete")  # ← check explícito
    # Si no tiene permiso, levanta 403

    # A12: además verifica que la orden es del tenant correcto
    order = order_repo.get(order_id)
    if order.company_id != current_user.company_id:
        raise NotFoundError()  # 404 prefiere no revelar existencia

    db.execute("DELETE FROM orders WHERE id = $1", order_id)
    # AUTHZ-5: audit log
    audit_log("order_deleted", current_user.id, target_id=order_id)
    return {"ok": True}
```

```sql
-- CORRECTO: authz check en función SQL (ver A25 para patrón completo)
CREATE FUNCTION delete_order(p_order_id UUID)
RETURNS JSONB AS ...
BEGIN
    -- AUTHZ-2: check granular
    PERFORM require_permission('orders.delete');

    -- ... operación
END;
...
```

Y en UI: mantener la ocultación de botones (UX correcta), pero NUNCA
dependiendo de eso para seguridad.

**Prevención**:
- Linter: detectar endpoint en `/admin/*` o `delete_*` / `refund_*` sin
  llamada a `require_permission()` → alert
- Linter: detectar función SQL con nombres sensibles
  (`eliminar_*`, `refund_*`, `cambiar_rol_*`) sin `require_permission()` → alert
- Tests adversariales obligatorios:
  - Empleado intenta endpoint admin → 403
  - Usuario A intenta acceder a recurso de usuario B → 403/404
  - Token expirado → 401
- Penetration test suite con casos de privilege escalation
- Code review obligatorio sobre cualquier nuevo endpoint sensible

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
- **A19 External Service Resilience** (subset: este pattern es solo retry, A19 es completo)

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
Code review enforced. Ver AP-3.10 para versión completa con timeout + circuit
breaker + Result type.

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

### AP-3.9 — Sync Heavy Operation

**Síntoma**: endpoint HTTP que ejecuta operación pesada (>2s, batch grande,
llamada externa lenta) de forma síncrona. El cliente espera la respuesta
durante todo el procesamiento.

**Ejemplos**:
```python
# INCORRECTO: endpoint síncrono con operación pesada
@app.post("/api/enviar-newsletter")
def enviar_newsletter(body):
    destinatarios = obtener_destinatarios()  # 10,000 emails

    for email in destinatarios:
        sendgrid.send(email)  # 0.5s cada uno = 5,000s total

    return {"ok": True}
    # Cliente espera ~83 minutos (HTTP timeout fallará primero)
```

```sql
-- INCORRECTO en SQL: función pesada llamada síncrona desde frontend
CREATE FUNCTION generar_reporte_anual_pdf(p_year INT)
RETURNS BYTEA AS ...
    -- Procesa 1 millón de filas, genera PDF de 50MB
    -- Tarda 45 segundos
    -- Cliente HTTP: timeout en 30s
    -- Worker DB: bloqueado 45s atendiendo solo esta request
...
```

**Resultado en producción**:
- HTTP timeout (cliente recibe error después de esperar)
- Pero la operación a veces SÍ completa (silenciosa)
- Worker pool del servidor bloqueado durante la operación
- Otros usuarios ven el sistema "lento" o caído
- Sin retry: si falla a la mitad, no se reanuda
- Sin observabilidad: imposible saber cuántos emails se enviaron
- Sin idempotencia: cliente retry duplica trabajo

**Causa raíz**: simplicidad aparente en MVP. "Lo arreglamos después con queue".

**Violaciones**:
- **A18 Async Processing for Heavy Tasks** (Nivel 2 universal)
- **A19 External Service Resilience** (parcial: sin timeout/retry de los servicios externos)

**Por qué importa**:
- **UX rota**: usuarios ven errores aleatorios o timeouts
- **Worker exhaustion**: pool de workers bloqueados → caída del sistema
- **Sin retry**: fallas parciales son catastróficas (50% de emails enviados)
- **Sin idempotencia**: cliente reintenta → trabajo duplicado
- **Sin observabilidad**: imposible diagnosticar lo que pasó
- **Sin priorización**: tarea pesada bloquea tareas rápidas

Manifestaciones típicas:
- Cliente reporta "el botón no hace nada" (en realidad timeout pero éxito parcial)
- Sistema "se cae" durante envío masivo de emails → todo bloqueado
- Reporte falla a la mitad → 50% de datos procesados, 50% perdidos

**Corrección**: encolar el trabajo y retornar `202 Accepted` con job_id
(ver A18 para patrón completo con tabla de jobs + worker + DLQ).

**Prevención**:
- Validator detecta endpoints con duración media > 2s → review
- Validator detecta handlers con bucles for > 100 iteraciones → review
- Validator detecta handlers con llamadas a servicios externos lentos → alert
- Métricas: alert si p99 latencia de endpoint > 5s

---

### AP-3.10 — External Call Without Timeout

**Síntoma**: llamada a servicio externo (HTTP, BD remota, RPC) sin las 4
defensas obligatorias: timeout, retry con backoff, circuit breaker, Result
type. Un servicio externo lento o caído cascadea a falla total del sistema.

**Ejemplos**:
```python
# INCORRECTO: sin timeout, sin retry, sin circuit breaker
import requests

@app.post("/api/procesar-pago")
def procesar_pago(body):
    # requests.post sin timeout = wait forever
    response = requests.post(
        "https://api.stripe.com/v1/charges",
        data={"amount": body["amount"]}
    )

    if response.status_code == 200:  # asume que llegó
        return {"ok": True}
    return {"ok": False}, 500
    # Si Stripe está caído: el handler queda esperando hasta que
    # el cliente HTTP timeout (puede ser 60s+)
    # Mientras tanto, este worker está bloqueado
    # 100 requests simultáneos = todo el pool bloqueado
```

```typescript
// INCORRECTO en frontend: fetch sin timeout
const response = await fetch('/api/heavy');  // espera indefinida
// Si el backend está lento, el usuario ve loader eterno
```

```sql
-- INCORRECTO en SQL: dblink/foreign data wrapper sin timeout
SELECT * FROM dblink('conn_string', 'SELECT ...') AS t(...);
-- Si la BD remota está caída, la sesión local se cuelga
```

**Causa raíz**: usar API default del cliente HTTP (que NO tiene timeout
explícito o tiene uno muy alto). Asumir que "el servicio externo siempre
responde rápido". Optimismo no fundado.

**Violaciones**:
- **A19 External Service Resilience** (Nivel 2 universal)

**Por qué importa**:
- **Cascade failure**: un servicio externo caído → tu app entera cae
- **Worker pool exhaustion**: requests acumulándose esperando externos
- **No retry**: errores transitorios (5xx, network blip) son catastróficos
- **No circuit breaker**: si Stripe está caído, seguís haciendo requests
  que sabés que van a fallar (latency + costos)
- **Excepciones crudas**: rompen el handler en vez de degradar elegantemente
- **No observabilidad**: imposible saber qué servicios fallaron, cuándo, cuánto

Manifestaciones típicas:
- Stripe tiene incidente de 10 minutos → tu app cae por 10 minutos
- API de email tarda 30s → todo el sistema "se siente lento"
- Webhook saliente a cliente caído → workers bloqueados horas
- Bill de Stripe inesperado: bug hizo retry sin idempotency_key

**Corrección**: aplicar las 4 defensas de A19 (timeout explícito + retry con
backoff exponencial + circuit breaker + Result type). Ver A19 para patrón
completo en Python con `httpx` + circuit breaker custom.

**Prevención**:
- Linter detecta `requests.get/post(...)` sin `timeout=` → alert
- Linter detecta `httpx.get/post(...)` sin `timeout=` → alert
- Linter detecta `fetch(url)` sin AbortSignal en JS/TS → alert
- Validator detecta handler con > 3 llamadas externas síncronas → review (mover a job)
- Métricas: alert si servicio externo tiene latency p99 > 5s sostenido
- Métricas: alert si error rate de servicio externo > 10% sostenido

---

### AP-3.11 — N+1 Query Pattern

**Síntoma**: una query inicial trae N resultados, y por cada resultado se
ejecuta una query adicional. Total: 1 + N queries para algo que debería
ser 1 query con JOIN, o 2 queries con batch.

**Ejemplos**:
```python
# INCORRECTO: N+1 clásico con ORM lazy loading
orders = db.query("SELECT * FROM orders WHERE company_id = $1", tenant_id)
# → 1 query: trae 100 órdenes

for order in orders:
    customer = db.query("SELECT * FROM customers WHERE id = $1", order.customer_id)
    # → 1 query por orden = 100 queries adicionales
    print(f"{order.id}: {customer.name}")
# Total: 1 + 100 = 101 queries

# El usuario ve "list of orders" tardar 5 segundos
# El profiler muestra 101 queries
```

```typescript
// INCORRECTO: N+1 en frontend con multiple .rpc()
const orders = await supabase.rpc('list_orders');
for (const order of orders.data) {
  const customer = await supabase.rpc('get_customer', { id: order.customer_id });
  // 1 round-trip al servidor por orden
}
```

**Causa raíz**:
- ORM con lazy loading sin tener cuidado (Django, Rails ActiveRecord)
- No detectar el patrón en code review
- "Funciona en dev con 5 órdenes, deployamos" → producción tiene 5000

**Violaciones**:
- Performance universal (no regla A* específica, pero crítico)
- Indirecta: A16 (operación costosa sin rate limit amplifica el problema)

**Por qué importa**:
- Producción tarda 10x más de lo necesario
- DB CPU explota innecesariamente
- Costos cloud altos por queries que se podían combinar
- Latencia percibida del usuario alta
- Bug invisible en dev (con poca data), catastrófico en prod

Manifestaciones típicas:
- Dashboard tarda 30s en cargar → era N+1 con N=500
- DB hits 100% CPU sin spike de tráfico → era N+1 que escaló con data
- Bill de Supabase 5x mayor de lo esperado → queries excesivas

**Corrección**: **JOIN** o **batch query** según contexto.

```sql
-- CORRECTO en SQL: JOIN
CREATE FUNCTION list_orders_with_customers()
RETURNS TABLE (
    order_id UUID,
    order_total NUMERIC,
    customer_name TEXT,
    customer_email TEXT
) AS ...
    RETURN QUERY
    SELECT o.id, o.total, c.name, c.email
    FROM orders_sc o
    LEFT JOIN customers_sc c ON c.id = o.customer_id
    WHERE o.company_id = get_my_sc_company_id()
    LIMIT 100;
    -- 1 sola query, todos los datos juntos
...
```

```python
# CORRECTO en Python: batch query
orders = db.query("SELECT * FROM orders WHERE company_id = $1", tenant_id)
customer_ids = [o.customer_id for o in orders]
customers = db.query(
    "SELECT * FROM customers WHERE id = ANY($1)",
    customer_ids
)
# Total: 2 queries en vez de 101
customers_by_id = {c.id: c for c in customers}
for order in orders:
    print(f"{order.id}: {customers_by_id[order.customer_id].name}")
```

**Prevención**:
- Query profiler en tests/CI: alert si test ejecuta > N queries
- Code review obligatorio para queries en loops
- ORM: configurar eager loading explícito donde aplique
  (`select_related`, `prefetch_related`, `joinedload`)
- Métricas: medir queries por endpoint, alert si > 10
- Linter: detectar `for ... in` con call a DB adentro → review

---

### AP-3.12 — Unstructured Logging

**Síntoma**: logs son `print()` statements, strings interpolados,
o `logger.info("user X did Y")` en formato libre. No JSON, sin campos
estructurados, sin trace_id, sin contexto correlacionable. En producción
multi-servidor es imposible debuggear.

**Ejemplos**:
```python
# INCORRECTO: print en producción
print(f"User {user_id} placed order {order_id}")

# INCORRECTO: logger con string interpolado (no estructurado)
logger.info(f"Order created: id={order_id}, total={total}")
# Al parsear logs, hay que regex parsear el string

# INCORRECTO: sin trace_id ni context
logger.error(f"Failed to charge: {error}")
# ¿Qué request era? ¿Qué usuario? ¿Qué tenant? Imposible saber

# INCORRECTO: nivel mal usado
logger.warn("DB connection failed")  # esto debería ser ERROR

# INCORRECTO: silent (sin log)
try:
    pay()
except Exception:
    return None  # falla sin trace
```

**Causa raíz**:
- "Rápido de escribir" en desarrollo
- No pensar en observability desde el inicio
- Falta de structlog/logger config con JSON output

**Violaciones**:
- **A21 Structured Observability** (Nivel 2 universal) — viola OBS-1
- Parcial: **A14 Explicit Failure** (errores sin contexto)

**Por qué importa**:
- En producción con >1 servidor, logs llegan a un agregador (Loki, Datadog)
- Buscar por `trace_id="abc-123"` requiere campos estructurados
- Sin context (user_id, tenant_id), imposible "ver qué pasó con el cliente X"
- Bug en producción a las 3am → tu único debugging tool son los logs.
  Si son string mush, perdés horas
- Sin nivel correcto → alerting impossible (no podés distinguir error real
  de "info ruidoso")
- Sin trace_id → no podés correlacionar entre servicios

Manifestaciones típicas:
- "Tengo un error en prod" → 4 horas buscando en logs sin trace_id
- Datadog cuesta $5000/mes porque ingiere strings sin parsear
- Cliente reporta bug → "no encuentro nada en los logs"
- Alert no dispara porque level era WARN cuando debió ser ERROR

**Corrección**: structured logging con context binding (ver A21 para
implementación completa con `structlog` + trace_id propagation).

```python
# CORRECTO: estructurado con context
log = logger.bind(
    operation="place_order",
    user_id=user_id,
    tenant_id=tenant_id,
    trace_id=trace_id_var.get(),
)
log.info("order_placement_started", order_total=total)
# ... operación ...
log.info("order_placed", order_id=order_id, duration_ms=elapsed_ms())
```

```json
// Output JSON:
{"timestamp": "2026-05-20T15:23:01Z", "level": "info",
 "operation": "place_order", "user_id": "u-456",
 "tenant_id": "t-123", "trace_id": "abc-789",
 "order_total": 5000, "event": "order_placement_started"}
```

**Prevención**:
- Linter detecta `print()` en código que no es script one-shot → alert
- Linter detecta `logger.info(f"...")` sin structured fields → review
- Linter detecta `logger.warn(...)` para excepciones (debería ser error) → review
- Code review obligatorio: cada operación crítica tiene log de inicio + fin
- CI check: cada servicio tiene log config que outputs JSON
- Pre-deploy: verificar que `/health/liveness` y `/health/readiness` existen

---

### AP-3.13 — Breaking API Change Without Versioning

**Síntoma**: se modifica el contrato (shape de response, parámetros, comportamiento)
de un endpoint o RPC existente sin crear una versión nueva. Los clientes que
ya consumen el endpoint se rompen en producción al deployar.

**Ejemplos**:
```python
# INCORRECTO: cambiar shape de /v1/orders sin versionar

# Antes (v1):
@app.get("/api/v1/orders/{id}")
def get_order(id):
    return {
        "id": id,
        "total": 5000,  # cents como int
        "status": "paid"
    }

# Después (mismo endpoint, breaking change):
@app.get("/api/v1/orders/{id}")
def get_order(id):
    return {
        "id": id,
        "total": {"amount": 5000, "currency": "USD"},  # objeto en lugar de int
        "status": "paid",
        "created_at": "2026-05-20"  # campo nuevo, OK
    }
# Frontend que esperaba total como número crashea
# Mobile app vieja (deployada hace semanas) deja de funcionar
# Integraciones de partners se rompen sin warning
```

```sql
-- INCORRECTO: cambiar RETURNS TABLE de RPC pública
CREATE OR REPLACE FUNCTION get_products()
RETURNS TABLE (
    id UUID,
    nombre TEXT,
    -- ANTES: precio NUMERIC
    -- AHORA: precio_cents BIGINT  ← rename + cambio de tipo
    precio_cents BIGINT,
    stock INT
) AS ...
-- Cualquier consumer que llamaba get_products() y leía .precio se rompe
```

**Causa raíz**: "es solo un cambio chiquito", subestimar impacto de
cambios de contrato. No tener disciplina de versionado explícito.

**Violaciones**:
- **A23 Deployment Safety** (Nivel 2 universal) — viola DEP-2 API versioning

**Por qué importa**:
- Clientes en producción se rompen sin warning
- Mobile apps deployadas hace tiempo → imposible "redeployar al cliente"
- Integraciones de partners pierden confianza
- Sin rollback fácil (deploy fue de schema/lógica, no de flag)
- Compliance: contratos B2B requieren API versioning explícito
- Tu propio frontend se rompe si el deploy de backend va antes

Manifestaciones típicas:
- "El cambio rompió el mobile" → mobile no se puede redeployar inmediatamente
- "El cliente enterprise se quejó porque su integración rompió" → pérdida
  de cliente
- "Tuvimos que rollback el deploy" → schema ya cambió, rollback complejo
- Partners cancelando contratos por falta de stability

**Corrección**: crear versión nueva, mantener vieja con deprecation:

```python
# CORRECTO: v1 sigue funcionando, v2 es el nuevo shape
@app.get("/api/v1/orders/{id}")
def get_order_v1(id):
    order = order_service.get(id)
    return {
        "id": str(order.id),
        "total": order.total.amount,  # solo amount, no currency (shape vieja)
        "status": order.status
    }
    # NOTE: Deprecated 2026-06-01, removal 2026-12-01

@app.get("/api/v2/orders/{id}")
def get_order_v2(id):
    order = order_service.get(id)
    return {
        "id": str(order.id),
        "total": {
            "amount": order.total.amount,
            "currency": order.total.currency  # NUEVO en v2
        },
        "status": order.status,
        "created_at": order.created_at.isoformat()  # NUEVO en v2
    }
```

Para RPCs SQL: crear `get_products_v2()` o usar parámetro `p_version`.

**Prevención**:
- Linter detecta cambios en `RETURNS TABLE` de RPCs públicas → alert
- Linter detecta cambios en shape de response de endpoint existente → alert
- Code review obligatorio: cada cambio de API se evalúa "¿es breaking?"
- OpenAPI/Swagger spec versionada en repo: diff automático muestra breaking
  changes
- Deprecation policy declarada: v1 mantenido N meses tras lanzar v2
- Pre-deploy CI: smoke tests usan clientes de v1 antiguos para verificar
  compat

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
  AP-2.8 Raw Table Response                  ← v1.1 (A11)
  AP-2.9 Trust Boundary Violation            ← v1.1 (A12)
  AP-2.10 Unbounded API Surface              ← v1.2 (A16)
  AP-2.11 Exposed Origin                     ← v1.2 (A17)
  AP-2.12 Missing Pagination                 ← nuevo v1.3 (universal)
  AP-2.13 Domain Polluted by Infrastructure  ← nuevo v1.3 (A20)
  AP-2.14 Hardcoded Secrets                  ← nuevo v1.3 (A22)
  AP-2.15 PII Without Classification         ← nuevo v1.3 (A24)
  AP-2.16 Authorization Only in UI           ← nuevo v1.3 (A25)

PROCESO:
  AP-3.1 Mixing Cleanup with Execution
  AP-3.2 Test Code in Production
  AP-3.3 Infinite Retry without Stop Conditions
  AP-3.4 Aprendizajes Duplicados Acumulados
  AP-3.5 API Call Without Retry
  AP-3.6 Silent Exception Swallow            ← v1.1 (A14)
  AP-3.7 Happy Path Only Testing             ← v1.1 (A15)
  AP-3.8 Inconsistent FOR UPDATE Order       ← v1.1 (A13)
  AP-3.9 Sync Heavy Operation                ← v1.2 (A18)
  AP-3.10 External Call Without Timeout      ← v1.2 (A19)
  AP-3.11 N+1 Query Pattern                  ← nuevo v1.3 (universal)
  AP-3.12 Unstructured Logging               ← nuevo v1.3 (A21)
  AP-3.13 Breaking API Change Without Versioning ← nuevo v1.3 (A23)

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

- **1.2** (2026-05-15): 2do audit empírico de Julián detectó 4 GAPS adicionales
  (rate limiting, edge protection, async processing, external resilience).
  Cubre **dimensión de infraestructura resiliente**. Agregados:
  - AP-2.10 Unbounded API Surface (vinculado a A16 Rate Limiting)
  - AP-2.11 Exposed Origin (vinculado a A17 Edge Protection)
  - AP-3.9 Sync Heavy Operation (vinculado a A18 Async Processing)
  - AP-3.10 External Call Without Timeout (vinculado a A19 External Resilience)

  Total: 28 anti-patterns.

- **1.3** (2026-05-20): 3er audit empírico de Julián (Opción D — catálogo
  completo Nivel 2 contra 13 dimensiones arquitectónicas) detectó 6 GAPS
  adicionales en reglas A20-A25 + 2 anti-patterns universales sin regla A*
  directa. Cubre **dimensiones de paradigma, observabilidad, secrets,
  deployment, data lifecycle, authorization** + **performance básico**.
  Agregados:
  - AP-2.12 Missing Pagination (sin regla A* directa, performance universal)
  - AP-2.13 Domain Polluted by Infrastructure (vinculado a A20 Hexagonal)
  - AP-2.14 Hardcoded Secrets (vinculado a A22 Secrets Management)
  - AP-2.15 PII Without Classification (vinculado a A24 Data Lifecycle)
  - AP-2.16 Authorization Only in UI (vinculado a A25 Authorization)
  - AP-3.11 N+1 Query Pattern (sin regla A* directa, performance universal)
  - AP-3.12 Unstructured Logging (vinculado a A21 Observability)
  - AP-3.13 Breaking API Change Without Versioning (vinculado a A23 Deployment Safety)

  Total: 36 anti-patterns.

---

Versión: 1.3 | Creado: 2026-05-15 | Última edición: 2026-05-20 (post audit 3 / Opción D)
Origen: análisis legacy SigmaControl + síntesis de patrones SOLID/Harness Engineering
