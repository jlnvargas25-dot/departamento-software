# Quickstart: Personal Todo Management

**Phase 1 output**. Steps to bring a developer machine to a running app + passing tests.

## Prerequisites

- Node.js 20.x and npm 10+
- Docker (for `supabase start` local Postgres)
- Supabase CLI (`npm i -g supabase` or `brew install supabase/tap/supabase`)
- Vercel CLI (optional, only for `vercel dev` and env pulls)

## 1. Clone & install

```bash
git clone <repo>
cd <repo>
npm ci
```

## 2. Local Supabase

```bash
supabase start             # boots local Postgres + Auth + Studio at default ports
supabase db push           # applies supabase/migrations/202605211900_initial.sql
```

Take note of the `anon key`, `service role key`, and `API URL` printed by `supabase start`.

## 3. Environment

Create `.env.local`:

```
NEXT_PUBLIC_SUPABASE_URL=http://127.0.0.1:54321
NEXT_PUBLIC_SUPABASE_ANON_KEY=<anon key from supabase start>
SUPABASE_SERVICE_ROLE_KEY=<service role key — server only, never NEXT_PUBLIC_>
UPSTASH_REDIS_REST_URL=<optional for local; rate limiter falls back to in-memory>
UPSTASH_REDIS_REST_TOKEN=<optional for local>
```

**Critical (A22)**: `SUPABASE_SERVICE_ROLE_KEY` is server-only. It MUST NOT be prefixed with `NEXT_PUBLIC_`. Never reference it in `app/*` page or client component code.

## 4. Run dev server

```bash
npm run dev
```

Open http://localhost:3000. Sign up with any email; magic links are visible in Supabase Studio (http://127.0.0.1:54323 → Auth → Inbox).

## 5. Tests

```bash
npm run test:unit          # Vitest, domain only (fast)
npm run test:integration   # Vitest + local Supabase (requires `supabase start`)
npm run test:e2e           # Playwright; spins up dev server + runs adversarial suite
npm run test:all           # all of the above
```

**Adversarial suite must be green** before any merge (A5, A12 CRITICA gating). Failure → CI blocks the PR.

## 6. Deploy preview

```bash
vercel link                  # one-time
vercel env pull .env.local   # pull cloud env into local
vercel                       # deploy preview
```

Supabase cloud project is provisioned separately; `supabase link --project-ref <ref>` then `supabase db push` to migrate cloud schema.

## 7. Smoke checklist after deploy

- [ ] Sign up with a fresh email → land in empty todo list
- [ ] Create 3 todos → all visible, most-recent first
- [ ] Mark one complete → visible distinction + completion timestamp
- [ ] Edit one → text updated; updated_at advanced
- [ ] Soft delete one → disappears from active list
- [ ] Sign out, attempt to GET / → redirected to sign-in
- [ ] Open two browsers as users A and B → A's todos invisible to B
- [ ] Adversarial: hit a server action from anonymous fetch → returns `UNAUTHENTICATED`

If any of step 7 fails, do not promote to production.

## 8. Useful operations

| Task | Command |
|---|---|
| Reset local DB | `supabase db reset` |
| Tail Vercel logs | `vercel logs --follow` |
| Rotate Supabase keys | Supabase Dashboard → Settings → API → Regenerate; update Vercel env |
| Purge soft-deleted todos | scheduled via `supabase db cron`, manual: `select cron.invoke('purge_soft_deleted_todos');` |
| Inspect auth events | `select * from auth_events where actor_user_id = '<uuid>' order by occurred_at desc limit 50;` |
