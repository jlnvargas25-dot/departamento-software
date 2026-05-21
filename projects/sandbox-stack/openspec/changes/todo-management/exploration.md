# Exploration: Personal Todo Management with User Authentication

**Change name**: todo-management
**Phase**: sdd-explore
**Date**: 2026-05-21
**Artifact store**: openspec
**Run purpose**: T1.9 — empirical comparison sdd-* vs speckit-* on identical input
**Input (verbatim)**: "Build a simple todo CRUD with user authentication using Supabase + Vercel. The app lets a signed-in user create, read, update, delete and complete their own todos. Anonymous users cannot access todos. Multi-tenant by user_id (no shared workspaces). Stack: Next.js on Vercel, Supabase Auth (email/password + magic link), Supabase Postgres with RLS, Tailwind UI minimal."

---

## Idea

A personal todo CRUD where each authenticated user owns exactly their own todos. The isolation model is user_id-based (no workspaces, no sharing). Anonymous access is fully blocked. The stack is prescribed: Next.js 15 App Router on Vercel, Supabase for auth + database + RLS enforcement, Tailwind for UI.

This is a canonical "Tier 1 SaaS multi-tenant" pattern at its simplest form — one tenant = one user. All A5 (Multi-tenant Isolation) principles apply identically even at this small scale.

---

## Context

**Architecture constraints (from constitution + openspec/config.yaml)**:
- A20 Hexagonal Architecture (CRITICAL): domain has zero infrastructure imports; Supabase is an adapter, not the domain
- A5 Multi-tenant Strict Isolation (CRITICAL): user_id = tenant; one RLS misconfiguration = full exposure
- A12 Zero Trust (CRITICAL): verify identity at every boundary — server action level AND DB level
- A22 Secrets Management (CRITICAL): SUPABASE_SERVICE_ROLE_KEY stays server-side; anon key only for client
- A24 Data Lifecycle (CRITICAL): retention policies, soft delete, purge strategy
- A21 Structured Observability (CRITICAL): structured logs, PII redaction, metrics

**Current state**: Greenfield. No application code. The speckit-* planning run in `specs/001-todo-management/` was NOT consulted (T1.9 isolation rule).

**Framework context**: ADR-009 v0.5 PROPOSED — this run is evidence for open risk R1 (sdd-* vs speckit-* comparison).

---

## Current State

No code exists. Affected modules will be created from scratch.

**Modules to create**:
- `src/domain/` — Todo entity, AuthIdentity, domain validation rules (A20 core)
- `src/ports/` — TodoRepository interface, AuthPort interface (A20 ports)
- `src/adapters/supabase/` — SupabaseTodoRepository, SupabaseAuthAdapter (A20 adapters)
- `src/adapters/next/` — Server actions as Next.js adapters (A20)
- `app/` — Next.js App Router pages, layouts, route handlers if any
- `supabase/migrations/` — SQL schema, RLS policies, indexes
- `src/lib/result.ts` — Result<T, E> tagged union (A14)
- `src/lib/auth.ts` — Session extraction utility (A12)
- `.env.local` / Vercel environment — secrets (A22)

---

## Approaches Considered

### 1. Data Access: Server Actions vs API Routes

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Server Actions** | Co-located with UI, no extra roundtrip, automatic CSRF, type-safe end-to-end with zod, native App Router | Cannot be called from mobile/external clients without wrapping | Low |
| **API Routes (`/api/`)** | Explicit REST contract, consumable externally, OpenAPI-documentable | Extra roundtrip, manual CSRF, more boilerplate | Medium |
| **Hybrid** | Best of both | Two mental models, complexity split | Medium |

**Recommendation**: Server Actions only. Requirement is web UI for signed-in users — no external clients. Server Actions keep secrets server-side (A22), enforce session check naturally (A12), and return Result<T,E> for A14.

---

### 2. Security Model: RLS-only vs RLS + Server-Side Check

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **RLS-only** | Postgres enforces at DB, app bugs don't cause leaks | service_role leak bypasses RLS; no defense in depth | Low |
| **RLS + server-side check** | Defense in depth (A12 ZT-3), two independent barriers | Slightly more code, two places to update | Low-Medium |
| **SECURITY DEFINER RPCs only** | Controlled surface, explicit | PL/pgSQL for every operation, hard to maintain | High |

**Recommendation**: RLS + server-side check. A12 Zero Trust mandates verification at every boundary. Pattern: `getServerSession()` -> verify `session.user.id === todo.user_id` -> then DB call which also enforces RLS. Principio II (3 capas) applied to auth: preventiva (server action check) + verificable (RLS) + correctiva (adversarial test suite that catches bypasses).

---

### 3. Auth Strategy: Email/Password only vs Magic Link vs Both

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Email + password only** | Simple, well-understood UX | Password management burden, credential stuffing risk (A12), needs rate limiting (A16) | Low |
| **Magic Link only** | No passwords, phishing-resistant | Requires reliable email delivery, UX friction | Low |
| **Both** | Broader UX coverage, Supabase native support at zero marginal cost | Two flows to test | Low |

**Recommendation**: Both. Supabase Auth handles both natively. Marginal implementation cost is near-zero. Rate limiting is required regardless (A16). Custom SMTP required for production (Supabase free tier: 4 magic links/hour).

---

### 4. Concurrency: Optimistic UI vs Server Round-Trip

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Server round-trip only** | Simplest, no stale state, server is source of truth | ~100-300ms perceived latency per action | Low |
| **Optimistic UI** (`useOptimistic`) | Snappy UX | Rollback logic on failure, state divergence risk | Medium |
| **SWR / React Query** | Background revalidation, caching | Extra dependency, complex with SSR + App Router | Medium-High |

**Recommendation**: Server round-trip for v1. "Simple todo CRUD" — Vercel + Supabase latency is acceptable. A8 (Idempotency) is trivial with server-round-trip (no client-side retry state). Optimistic UI is a v2 enhancement.

---

### 5. Multi-Tenancy: RLS filter vs Application filter vs Both

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Application filter only** (`WHERE user_id = $1`) | Simple | One missing WHERE = full tenant exposure. No defense in depth. | Low (dangerous) |
| **RLS as primary** | Postgres-enforced, impossible to bypass via app bugs | Requires correct client setup (anon vs service_role) | Low |
| **RLS + application filter** | Defense in depth (A5 CRITICAL) | Slightly more code | Low-Medium |

**Recommendation**: RLS as primary + application-layer ownership check in server actions. The `createServerClient()` (cookie-based session) inherits RLS context for the authenticated user automatically. Server actions re-verify ownership as second barrier. Adversarial test matrix MUST include cross-tenant access attempts (A15 + A5).

---

### 6. Delete Strategy: Soft vs Hard Delete

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **Hard delete** | Simpler queries | Irreversible, no GDPR purge window, no audit trail (A24) | Low |
| **Soft delete** (`deleted_at`) | Recoverable, audit trail (A24), supports cron purge policy | Filter `deleted_at IS NULL` everywhere, tombstone handling | Low-Medium |

**Recommendation**: Soft delete + 30-day hard purge via cron. A24 (Data Lifecycle & Privacy) is CRITICAL. The 30-day window satisfies a recovery UX if needed. RLS must filter `deleted_at IS NULL` to prevent tombstone leaks. Note: if GDPR applies, user account deletion triggers immediate hard delete (not 30-day window).

---

### 7. Observability Stack

| Approach | Pros | Cons | Effort |
|----------|------|------|--------|
| **console.log only** | Zero setup | Unstructured, not A21-compliant | Low |
| **pino + Vercel Analytics** | A21 OBS-1 (structured logs) + OBS-2 (metrics), PII-redactable, searchable | pino setup, log schema discipline | Low-Medium |
| **pino + Sentry + OpenTelemetry traces** | A21 complete (logs + metrics + traces) | High setup cost for MVP | High |

**Recommendation**: pino + Vercel Analytics for v1. Traces deferred to v2 (A21 partial acceptable). A21 OBS-6: `email` fields must be masked in all log outputs.

---

## A-Rules In Scope

| Rule | Criticality | Design Decision |
|------|-------------|-----------------|
| **A5** Multi-tenant Isolation | CRITICAL | RLS + server-side ownership check; adversarial tests gate |
| **A12** Zero Trust | CRITICAL | `getServerSession()` at top of every server action; ZT-3 at every boundary |
| **A20** Hexagonal Architecture | CRITICAL | domain -> ports -> adapters; Supabase never imported in domain |
| **A22** Secrets Management | CRITICAL | SERVICE_ROLE_KEY server-only; anon key via env; never client-side |
| **A24** Data Lifecycle | CRITICAL | Soft delete + 30d purge; audit event table insert-only (A6) |
| **A21** Structured Observability | CRITICAL | pino + Vercel Analytics v1; PII redaction; traces v2 |
| **A14** Explicit Failure | Important | Result<T, E> tagged union on all server actions |
| **A15** Unhappy Path First | Important | Adversarial test matrix designed before happy path |
| **A25** Authorization | Important | Owner-only: `user_id = auth.uid()` in RLS + app layer |
| **A16** Rate Limiting | Important | Auth endpoints rate-limited (Upstash or Vercel Edge) |
| **A13** Concurrency Safety | Important | `updated_at` token for optimistic concurrency on update/complete |
| **A11** DAO + DTO | Important | Supabase = DAO; zod schemas = DTO; domain types != DB types |
| **A8** Idempotency | Important | `complete` and `delete` are idempotent (already done = 200) |
| **A4** Aciclicidad | Important | Hexagonal enforces structurally — domain imports nothing from adapters |
| **A19** External Resilience | Important | Supabase = external; timeouts + error handling required; circuit breaker deferred v1.1 |

**Not in scope for v1**: A9 (no loops), A10 (test isolation — standard practice), A17 (Vercel WAF default), A18 (no heavy async tasks), A23 (Vercel preview deployments).

---

## Open Questions

1. **SMTP for magic links**: Is custom SMTP configured in the Supabase project? Default is rate-limited (4/hour free tier) — unusable in production.
2. **Rate limiting backend**: Upstash Redis vs Vercel Edge Config vs in-memory? Upstash is standard for serverless but requires an additional account + secret (A22).
3. **Session duration**: Default Supabase (1h access + 7d refresh)? Affects UX and security posture.
4. **GDPR scope**: EU users? If yes, "right to erasure" changes soft-delete behavior on account deletion (immediate hard delete, not 30d window) — meaningful scope addition for A24.
5. **Audit event table scope**: `todo_events` + `auth_events` insert-only tables (A6) — v1 or deferred? Adds ~2 migration files and RLS policy complexity.
6. **Pagination**: Load-all todos (with cap) vs paginated? For a personal list, load-all <=200 items is reasonable for v1.
7. **`completed` field semantics**: Boolean only vs boolean + `completed_at TIMESTAMP`? Timestamp enables analytics + audit trail (A6, A24).
8. **Vercel + Supabase region alignment**: Same region (e.g. both `us-east-1`) to minimize cold-start + DB connection latency? Measurable UX impact.

---

## Recommendation

**Recommended architecture for proposal**:

| Dimension | Decision |
|-----------|----------|
| Data access | Server Actions (not API routes) |
| Security model | RLS + server-side ownership check (defense in depth) |
| Auth methods | Both: email/password + magic link |
| Architecture | Hexagonal: `domain/` -> `ports/` -> `adapters/supabase/` + `adapters/next/` |
| Delete strategy | Soft delete + 30d cron purge (A24) |
| Error handling | Result<T, E> tagged union on all server actions (A14) |
| State | Server round-trip v1; optimistic UI deferred v2 |
| Observability | pino + Vercel Analytics v1; traces deferred v2 (A21 partial) |
| Testing gate | Adversarial test suite (A5 cross-tenant + A12 bypass) before merge |

**Ready for Proposal**: Yes. Open questions 1-8 should be resolved as explicit assumptions in the proposal — none are blockers that prevent design. Question #4 (GDPR) is the highest-impact unknown.

---

## ADR-009 R1 Cross-Reference (T1.9 Comparison Signal)

This exploration, compared to the speckit-* run, provides evidence for ADR-009 risk R1:

- **sdd-explore structure**: 7 approach dimensions analyzed with pros/cons/effort tables + A-rule mapping per dimension. A-rule coverage emerged naturally from the skill structure — no manual injection required by the operator.
- **Comparison hypothesis**: speckit-clarify surfaced ~10/25 A-rules via its 10-category taxonomy; sdd-explore surfaces A-rules through approach-level tradeoff analysis. The two methods produce different friction profiles — the orchestrator should measure: how many A-rule decisions require manual operator injection in each chain.
- **Key difference to evaluate**: sdd-* separates exploration from proposal (explicit artifact boundary); speckit-* folds clarification into the plan template (Constitution Check as manual injection point).
