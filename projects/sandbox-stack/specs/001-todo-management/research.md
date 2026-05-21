# Research: Personal Todo Management

**Phase 0 output**. Resolves the few decisions not pinned by spec assumptions or constitution.

## Decision 1 — Auth provider: Supabase Auth (vs Auth0, Clerk, NextAuth)

- **Decision**: Supabase Auth.
- **Rationale**: pinned by spec input. Plus: same vendor as data → single key surface; RLS uses `auth.uid()` natively (A5); built-in email + magic link; free tier ample for MVP.
- **Alternatives considered**:
  - **Clerk** — better DX but separate identity surface; would require sync to user_id in DB. Rejected.
  - **NextAuth** — flexibility but every adapter is custom code; reintroduces ownership question on session storage. Rejected.
  - **Auth0** — enterprise-grade but cost and complexity dwarf MVP scope. Rejected.

## Decision 2 — Multi-tenant isolation: RLS-first (vs app-layer filter)

- **Decision**: enforce `user_id = auth.uid()` via PostgreSQL Row-Level Security on `todos`. No service-role queries reach the client; all reads/writes use the user's JWT.
- **Rationale**: A5 is CRITICA. App-layer filters are bypassable on every regression. RLS makes A5 violation impossible without a database superuser. Adversarial Playwright test confirms denial on cross-tenant attempt.
- **Alternatives considered**:
  - **App-layer filter only** — fast to ship, leaky by design. Rejected as primary control; kept as defense-in-depth via zod schema validating user_id matches session.
  - **Schema-per-tenant** — operationally heavy for 1k users. Rejected.

## Decision 3 — Soft delete via `deleted_at` (vs hard delete + audit log)

- **Decision**: `todos.deleted_at TIMESTAMPTZ NULL`. Active rows have `deleted_at IS NULL`. Cron job after 30 days hard-deletes rows where `deleted_at < now() - interval '30 days'`.
- **Rationale**: A6 immutability for audit (logical), A8 idempotent delete (re-deleting just sets the same timestamp), A24 retention window explicit. User-recoverable in v1.1 if needed.
- **Alternatives considered**:
  - **Hard delete + `todo_events` audit** — cleaner table, but recovery is reconstruction. Audit-only is still required (kept as parallel decision below).
  - **Status enum (active/deleted)** — same semantics with worse query patterns (forces partial index). Rejected.

## Decision 4 — Audit log: `todo_events` append-only

- **Decision**: separate `public.todo_events` table with insert-only RLS, recording every create/update/complete/delete with actor and timestamp. Read access only to owner via RLS on `actor_user_id`.
- **Rationale**: A6 immutability, A21 structured observability at data-layer level. Pairs with structured app logs (`pino`) for cross-correlation.
- **Alternative**: log only to app (pino) — no DB audit. Rejected because logs are not user-recoverable and Vercel log retention is platform-bound.

## Decision 5 — Concurrency: optimistic via `updated_at` token (vs row lock)

- **Decision**: each `todos` row has `updated_at TIMESTAMPTZ`. Update RPC accepts `expected_updated_at` and rejects if mismatched.
- **Rationale**: A13 concurrency safety. Last-write-wins is acceptable for single-user todo app, but optimistic token gives clean error UX when the same user edits from two devices.
- **Alternative**: row-level pessimistic lock. Rejected (overkill for low-conflict workload).

## Decision 6 — Server I/O via Next.js Server Actions (vs REST API routes)

- **Decision**: Server actions in `src/app/actions/`. No `/api/*` routes in v1.
- **Rationale**: same trust boundary as the page render; no JSON contract to maintain client-side; zod validation co-located with action. Simpler MVP surface.
- **Alternative**: REST routes. Rejected for v1 (defer to v2 if mobile app or third-party API needs).

## Decision 7 — Testing strategy: adversarial-first

- **Decision**: e2e suite leads with `adversarial.spec.ts` (cross-tenant + anonymous deny). Unit + integration tests built around it.
- **Rationale**: A15 unhappy path first. A5 + A12 are CRITICA; their tests gate release.
- **Alternative**: happy-path first. Rejected explicitly per constitution.

## Decision 8 — Rate limiting: Upstash + Vercel Edge Config

- **Decision**: `@upstash/ratelimit` on `POST /sign-up` and magic-link request actions. Default: 10 requests / hour / IP for sign-up; 5 / hour / IP for magic-link.
- **Rationale**: A16. Auth endpoints are abuse vectors. Todo CRUD limited indirectly by Vercel platform.
- **Alternative**: only platform rate limit. Rejected (insufficient granularity for auth abuse).

## Decision 9 — Logging: pino with redaction

- **Decision**: `pino` with `redact: ['email', 'password', '*.token']` patterns. Logs include `user_id` (UUID), action, outcome, timestamp.
- **Rationale**: A21 + A22 (don't log secrets).
- **Alternative**: console.log. Rejected (no structure, no redaction).

## Decision 10 — Schema migrations: Supabase CLI

- **Decision**: `supabase/migrations/*.sql` versioned in repo, applied via `supabase db push` per deploy.
- **Rationale**: A23 deployment safety (versioned, reviewable, reversible via new migration). Migration in PR is reviewable.
- **Alternative**: console-applied schema. Rejected (not reproducible).

## Outstanding / deferred to v2

- **Distributed traces** (A21 third pillar): Vercel + Supabase don't share trace context natively. Deferred.
- **Circuit breaker for Supabase outage** (A19): MVP shows user-visible error; v1.1 introduces retry-with-backoff per call site. Deferred.
- **Real-time todo updates** (Supabase Realtime): out of scope for v1; would change concurrency model.
