# Implementation Plan: Personal Todo Management with User Authentication

**Branch**: `001-todo-management` | **Date**: 2026-05-21 | **Spec**: [spec.md](./spec.md)

**Input**: Feature specification from `specs/001-todo-management/spec.md`

## Summary

Build a multi-tenant SaaS-style web app where every signed-in user manages a private list of todos (create, read, update, complete, soft-delete). Anonymous access is denied at the data layer. Identity is provided by Supabase Auth (email + password + magic link). Persistence is Postgres on Supabase with Row-Level Security enforcing strict per-user isolation. The web tier is Next.js (App Router) deployed on Vercel. UI is minimal Tailwind, no design system.

The technical approach prioritizes A* compliance for a Tier-1 SaaS: A5 multi-tenant isolation enforced **at the data layer via RLS** (not only at app layer), A12 zero-trust on every request, A20 hexagonal boundaries between Next.js server actions and Postgres, A21 structured logs for all auth + write events, A22 secrets only via Vercel env vars, A25 RBAC inferred from `auth.uid()` (no admin roles in v1).

## Technical Context

**Language/Version**: TypeScript 5.5 on Node.js 20 (Vercel runtime)

**Primary Dependencies**: Next.js 15 (App Router) · @supabase/ssr · @supabase/supabase-js · zod (input validation) · Tailwind CSS 4

**Storage**: PostgreSQL 15 (Supabase) with Row-Level Security; `auth.users` (managed by Supabase) + `public.todos`

**Testing**: Vitest (unit, domain rules) · Playwright (e2e adversarial, multi-tenant isolation tests, anonymous-deny tests) · supabase-cli local Postgres for integration tests

**Target Platform**: Vercel (web app) · Supabase (managed DB + Auth) · Modern evergreen browsers

**Project Type**: Web application (single Next.js full-stack project; no separate frontend/backend split)

**Performance Goals**: P95 page load < 2s on residential connection; P95 server action latency < 400ms for todo CRUD; cold-start < 1s on Vercel Functions

**Constraints**: All todo data access MUST traverse RLS — no service-role keys leaving server boundary; only `anon` and authenticated user keys reach the client; secrets only via Vercel env vars rotated quarterly

**Scale/Scope**: v1 designed for ~1,000 users, ~500 active todos per user; pagination at 50/page; no realtime subscriptions in v1

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

Mapping plan-level decisions against constitution `.specify/memory/constitution.md` and A1-A25:

| Rule | Criticidad | Plan compliance approach | Status |
|---|---|---|---|
| A1 Module Ownership | Importante | `todos` table owned by todo module; auth owned by Supabase; no cross-module table writes | OK |
| A2 Encapsulacion tablas | Importante | Public interface = server actions; tables not exposed to client | OK |
| A3 Inter-Module Contracts | Importante | Typed zod schemas at every server action boundary | OK |
| A4 Acyclic deps | Importante | Hexagonal split: domain -> ports -> adapters (Supabase). No cycles | OK |
| A5 Multi-tenant isolation | CRITICA | RLS `auth.uid() = user_id` on todos table; verified by adversarial Playwright test | OK |
| A6 Immutability for audit | Importante | `todo_events` append-only log (insert-only RLS) | OK |
| A7 Domain validation before impl | Importante | This plan + research.md cover dominio antes de implementation | OK |
| A8 Idempotency or rollback | Importante | Soft delete + completion are idempotent; updates use optimistic concurrency via `updated_at` | OK |
| A9 Stop conditions explicit | Importante | No loops/retries in MVP scope beyond Supabase SDK defaults | OK |
| A10 No test code in prod | Importante | `tests/` isolated from `src/`; tree-shaking removes test imports | OK |
| A11 DAO + DTO | Importante | Supabase client = DAO; zod schemas = DTOs; domain types separate | OK |
| A12 Zero Trust | CRITICA | Every server action verifies session via `createServerClient`; RLS denies otherwise | OK |
| A13 Concurrency Safety | Importante | Optimistic concurrency token on update; last-write-wins documented for MVP | OK |
| A14 Explicit Failure | Importante | All server actions return tagged `{ ok, error }` discriminated unions; errors logged structurally | OK |
| A15 Unhappy Path First | Importante | Playwright suite covers anonymous-deny + cross-tenant attempts before happy CRUD | OK |
| A16 Rate Limiting | Importante | Vercel Edge Config + `upstash/ratelimit` on auth endpoints (sign-up, magic-link request) | OK |
| A17 Edge Protection | Importante | Vercel WAF default + DDoS mitigation; no custom rules required for MVP | OK |
| A18 Async for heavy | Importante | N/A for MVP (no heavy operations); flagged as deferred | DEFERRED |
| A19 External Resilience | Importante | Supabase down -> degrade to user-visible error; no circuit breaker in v1 (deuda) | DEFERRED |
| A20 Hexagonal | CRITICA | `domain/` (entities, ports) + `adapters/` (supabase impl, ui) + `app/` (Next routes) - strict imports | OK |
| A21 Observability | CRITICA | Structured logs via `pino` to Vercel; metrics via Vercel Analytics; traces deferred to v2 | PARTIAL |
| A22 Secrets | CRITICA | Vercel env vars + Supabase service role NEVER on client; rotation quarterly documented | OK |
| A23 Deployment Safety | Importante | Vercel preview deployments per PR; production promotion via manual approval; rollback via Vercel UI | OK |
| A24 Data Lifecycle | CRITICA | Soft-delete 30d window + hard-delete on account closure; PII classification on email | OK |
| A25 Authorization | Importante | RBAC implicit: every user is owner of their todos only; no admin role in v1 | OK |

**Gate result**: PASS with 3 items not fully covered (A18, A19, A21 traces). All 3 are documented as deuda or partial coverage via stack defaults. Re-check after Phase 1 design confirmed unchanged.

## Project Structure

### Documentation (this feature)

```text
specs/001-todo-management/
├── plan.md              # This file
├── research.md          # Phase 0 output
├── data-model.md        # Phase 1 output
├── quickstart.md        # Phase 1 output
├── contracts/
│   └── api.md           # Server action signatures + zod schemas
└── tasks.md             # Phase 2 output (/speckit-tasks)
```

### Source Code (repository root)

```text
src/
├── domain/                    # A20: pure domain, no IO
│   ├── todo.ts                # Todo entity + invariants
│   ├── user.ts                # User entity
│   ├── ports/                 # interfaces only
│   │   ├── todo-repository.ts
│   │   └── auth-provider.ts
│   └── errors.ts              # tagged domain errors
├── adapters/                  # A20: IO implementations
│   ├── supabase/
│   │   ├── client.ts          # server + browser clients
│   │   ├── todo-repository.ts # implements port
│   │   └── auth-provider.ts   # implements port
│   └── logging/
│       └── pino.ts            # structured logger
├── app/                       # Next.js App Router
│   ├── (auth)/                # sign-in/sign-up/magic-link
│   ├── todos/                 # main app screens
│   └── actions/               # server actions (todos, auth)
└── lib/
    └── schemas.ts             # zod schemas (DTOs)

tests/
├── unit/                      # Vitest, domain only
│   └── todo.spec.ts
├── integration/               # Vitest + supabase-cli local
│   └── todo-repository.spec.ts
└── e2e/                       # Playwright
    ├── auth.spec.ts
    ├── todo-crud.spec.ts
    └── adversarial.spec.ts    # cross-tenant + anonymous deny (A5, A12, A15)

supabase/
└── migrations/
    └── 0001_initial.sql       # todos table + RLS + indexes
```

**Structure Decision**: Single Next.js full-stack project under repo root. Hexagonal split inside `src/` (domain → ports → adapters) enforces A20. Tests organized by scope (unit / integration / e2e). Supabase migrations versioned alongside code.

## Complexity Tracking

No constitution violations require justification. The 3 items not fully covered (A18, A19, A21 traces) are documented as **stack-default partial coverage**, not violations:

- **A18 Async**: MVP has no heavy operations to async. Flagged for v2 if/when reminders or notifications land.
- **A19 External Resilience**: no circuit breaker for Supabase in v1. Mitigation: user-visible error + retry-after backoff. Deuda formal flagged for v1.1.
- **A21 Observability traces**: logs + metrics present; distributed traces deferred to v2 (Vercel + Supabase don't share trace context in v1 architecture).
