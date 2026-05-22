# sandbox-stack — Personal Todo Management

Sandbox empírico del **Framework Departamento de Software** (SigmaControl).
Feature: `001-todo-management` — multi-tenant todo CRUD with Supabase Auth + RLS.

**Stack**: Next.js 15 (App Router) · Supabase Auth + Postgres RLS · Tailwind 4 · Vercel · TypeScript strict

---

## Architecture

```
Browser
  └── Next.js App Router (Vercel Edge)
        ├── Middleware (session refresh + protected route guard — A12)
        ├── Server Components (SSR — initial data fetch)
        ├── Server Actions (auth.ts + todos.ts — zero-trust, A12 + A5)
        └── Client Components (optimistic UI — todo-list.tsx, todo-row.tsx)
              └── Supabase Postgres (RLS — primary security boundary — A5)
                    ├── todos (RLS: auth.uid() = user_id)
                    ├── todo_events (append-only audit — A6)
                    └── auth_events (service-role inserts only — A22)
```

**Security layers** (defense-in-depth):
1. Middleware: validates JWT signature on every request
2. Server actions: independent `getUser()` call at each action boundary
3. RLS: DB enforces ownership regardless of application code path

---

## Quick Start (local development)

### Prerequisites

- Node.js 20.x · npm 10+
- Docker (for `supabase start`)
- Supabase CLI: `npm i -g supabase`
- Vercel CLI (optional): `npm i -g vercel`

### 1. Clone & install

```bash
git clone <repo>
cd <repo>
npm ci
```

### 2. Start local Supabase

```bash
supabase start          # boots Postgres + Auth + Studio
supabase db push        # applies supabase/migrations/202605211900_initial.sql
```

Note the `anon key`, `service role key`, and `API URL` printed by `supabase start`.

### 3. Configure environment

Create `.env.local`:

```env
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key from supabase start>
SUPABASE_SERVICE_ROLE_KEY=<service role key — server only, NEVER NEXT_PUBLIC_>
UPSTASH_REDIS_REST_URL=<optional — rate limiter falls back to in-memory locally>
UPSTASH_REDIS_REST_TOKEN=<optional>
```

**A22 critical**: `SUPABASE_SERVICE_ROLE_KEY` bypasses RLS. Keep it server-only.

### 4. Run dev server

```bash
npm run dev
```

Open http://localhost:3000. Sign up with any email.
Magic links are visible in Supabase Studio: http://127.0.0.1:54323 → Auth → Inbox.

---

## Tests

```bash
npm run test:unit          # Vitest — domain entities (no infra)
npm run test:integration   # Vitest + local Supabase (requires supabase start)
npm run test:e2e           # Playwright — full browser suite
npm run test:all           # all of the above
```

### Adversarial suite (A5 + A12 CRITICA)

```bash
npx playwright test tests/e2e/adversarial-*.spec.ts
```

These tests **must be green before any merge**. The CI gate (`.github/workflows/test.yml`)
blocks PRs if adversarial tests fail. No `[skip-ci]` override is permitted on PRs
that touch `auth.ts`, `todos.ts`, or `202605211900_initial.sql`.

Key adversarial tests:
- `adversarial-anonymous.spec.ts` — anonymous denial (SC-004)
- `adversarial-cross-tenant.spec.ts` — cross-tenant denial (SC-003)
- `adversarial-rls-bypass.spec.ts` — direct Supabase client bypass attempts
- `adversarial-log-redaction.spec.ts` — pino email redaction verification

---

## Deployment

See [`docs/DEPLOYMENT.md`](docs/DEPLOYMENT.md) for the full runbook including:
- Environment variables checklist (A22)
- Migration apply steps
- Vercel preview + production promote
- Smoke test checklist (post-deploy)
- Key rotation schedule (quarterly)

Quick deploy to preview:

```bash
vercel env pull .env.local
vercel
```

---

## Security

See [`docs/SECURITY.md`](docs/SECURITY.md) for:
- RLS threat model (A5)
- Zero-trust middleware architecture (A12)
- PII handling and log redaction (A21, A22)
- Rate limiting configuration (A16)
- Audit trail immutability (A6)

---

## Cron: 30-day purge of soft-deleted todos

The Supabase Edge Function `supabase/functions/purge-expired-todos/index.ts`
runs daily at 03:00 UTC and hard-deletes todos with `deleted_at < now() - 30 days`.

```bash
supabase functions deploy purge-expired-todos
supabase functions invoke purge-expired-todos --local   # manual trigger
```

---

## Project structure

```
src/
  app/
    (auth)/          sign-in, sign-up, magic-link pages
    todos/           todos list page + _components/
    actions/         auth.ts, todos.ts (server actions)
  adapters/
    supabase/        auth-provider.ts, todo-repository.ts, client.ts
    logging/         pino.ts (redacted structured logger)
  domain/
    todo.ts, user.ts  pure domain entities
    errors.ts         tagged DomainError discriminated union
    ports/            TodoRepository, AuthProvider interfaces
  lib/
    schemas.ts        zod input schemas
    rate-limit.ts     Upstash sliding window
    result.ts         Result<T, E> monad
supabase/
  migrations/        202605211900_initial.sql (todos + RLS + audit tables)
  functions/         purge-expired-todos/ (Deno Edge Function)
tests/
  unit/              domain invariants (Vitest)
  integration/       RLS isolation, auth provider (Vitest + Supabase)
  e2e/               Playwright: auth, todo CRUD, adversarial suite
  smoke/             Post-deploy smoke checklist (Playwright)
docs/
  DEPLOYMENT.md      Runbook + secrets table + smoke checklist
  SECURITY.md        Threat model + rotation schedule
  SMOKE-LOG.md       Deploy smoke test results log
.github/
  workflows/
    test.yml         CI: adversarial gate blocks merge (A5+A12 CRITICA)
```

---

## Constitution A-rules exercised

| Rule | Description | Evidence |
|---|---|---|
| A5 | Multi-tenant RLS isolation | RLS policies + adversarial tests CT-01–CT-06 |
| A6 | Append-only audit trail | todo_events + auth_events; no UPDATE/DELETE RLS |
| A8 | Idempotent operations | complete/uncomplete/delete in repository |
| A12 | Zero-trust session validation | getUser() in every server action + middleware |
| A13 | Optimistic concurrency | expectedUpdatedAt in update/complete/uncomplete |
| A14 | No thrown exceptions | Result<T> monad throughout |
| A15 | Unhappy path first | adversarial tests written before happy-path polish |
| A16 | Rate limiting | Upstash sliding window on sign-up + magic-link |
| A21 | Structured observability | pino + Vercel Analytics + todo/auth event tables |
| A22 | Secrets isolation | Service role key server-only; pino redact; ip_hash |
| A24 | Soft-delete + purge cron | deleted_at + 30-day Edge Function cron |
| A25 | Owner-only authorization | userId from getUser(), never from client input |
