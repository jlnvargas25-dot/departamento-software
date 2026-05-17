# NORTE — Stallen

> **Propósito**: visión del proyecto Stallen. Se lee ~1 vez al mes o al
> arrancar un hito grande. NO se lee en cada sesión.

**Versión**: 0.1 (placeholder inicial)
**Última actualización**: 2026-05-15
**Estado**: ⚠️ PENDIENTE — vale completar con Julián como stakeholder

---

## Qué es Stallen

⚠️ **PLACEHOLDER — Julián vale completar**

Stallen es:
- (Describir el negocio: qué tipo de empresa, qué hace, para quién)
- (Módulos principales: Caja, Inventario, CRM, Agenda, Procesos, etc.)
- (Cuántos usuarios reales lo usan hoy)
- (Cuántos años en producción)

## Por qué existe Stallen

⚠️ **PLACEHOLDER**

- (Problema que resuelve)
- (Por qué se construyó en lugar de comprar)
- (Diferenciador vs alternativas comerciales)

## Stack tecnológico actual

- **Backend**: Supabase (PostgreSQL + Auth + Storage + RPCs)
- **Frontend**: Vercel + Next.js
- **Multi-tenant**: RLS con `get_my_sc_company_id()` helper
- **Otros**: (completar — ej. Stripe para pagos, qué más)

## Stakeholders

- **Owner**: Julián Vargas
- **Usuarios**: (cuántos hay, qué tipo)
- **Otros stakeholders**: (si hay socios, partners, etc.)

## Criterios de éxito

⚠️ **PLACEHOLDER**

Stallen es exitoso si:
- (Métrica 1: usuarios activos / mes)
- (Métrica 2: revenue / mes)
- (Métrica 3: uptime / disponibilidad)
- (Métrica 4: tiempo medio de respuesta UX)
- (Métrica cualitativa: satisfacción de los usuarios)

## Decisiones fundamentales (no negociables)

1. **Multi-tenant strict isolation** (A5): jamás cross-tenant data leak
2. **Tier 1 commercial robust** (ADR-004): defensas arquitectónicas estrictas
3. **Supabase + Vercel stack** (decisión técnica explícita): NO cambiar sin ADR
4. **(Agregar otras decisiones fundacionales)**

## Restricciones

⚠️ **PLACEHOLDER**

- **Presupuesto**: ¿Hay budget mensual? ¿Cuál?
- **Equipo**: 1 persona (Julián) usando IA del ecosistema
- **Compliance**: (¿hay requisitos legales? PCI? GDPR? LATAM-específicos?)
- **Stack lock-in aceptable**: Supabase + Vercel está OK

## Driver del proyecto

⚠️ **PLACEHOLDER**

¿Qué motiva este proyecto?
- (Razón económica)
- (Razón personal)
- (Razón estratégica)

## Criterio de stop / pivot

¿Cuándo Stallen dejaría de tener sentido?
- (Métrica 1 cae bajo X)
- (Aparece alternativa Y mejor)
- (Otro)

---

## Acciones pendientes para completar este NORTE

- [ ] Llenar todos los placeholders ⚠️
- [ ] Validar con vos mismo como stakeholder (entrevista interna)
- [ ] Versionar a 1.0 cuando completo
- [ ] Archivar versiones anteriores en `auditoria/historia-estrategica/` cuando haya pivots

---

## Versionado

- v0.1 (2026-05-15) — INICIAL placeholder. Pendiente completar con Julián.
- v1.0 (futuro) — Versión completa tras entrevista de captura.
