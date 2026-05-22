# Deployment Runbook — sandbox-stack Todo App

**A22**: This document lists all secrets by name. No real values are stored here.
Rotate secrets quarterly (see schedule below).

---

## Prerequisites

- Vercel account with the project linked (`vercel link`)
- Supabase cloud project provisioned
- Node.js 20.x, Supabase CLI, Vercel CLI installed locally

---

## 1. Environment Variables Checklist

Configure these in **Vercel Project Settings → Environment Variables**.

| Variable | Required | Scope | Description |
|---|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Yes | All | Supabase project API URL (public) |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Yes | All | Supabase anon key (public, safe for browser) |
| `SUPABASE_SERVICE_ROLE_KEY` | Yes | Server only | Service role key — NEVER prefix with `NEXT_PUBLIC_` |
| `UPSTASH_REDIS_REST_URL` | Yes (prod) | Server only | Upstash Redis endpoint for rate limiting |
| `UPSTASH_REDIS_REST_TOKEN` | Yes (prod) | Server only | Upstash Redis auth token |

**Critical (A22)**:
- `SUPABASE_SERVICE_ROLE_KEY` must NEVER appear in client bundles.
- Verify after deploy: open browser DevTools → Network → check JS bundles for the string `service_role`. If found, STOP — the key is exposed.
- `UPSTASH_REDIS_REST_TOKEN` is server-only. Same check applies.

### Rotation Schedule (quarterly — A22)

| Secret | Rotation Command | Who | Frequency |
|---|---|---|---|
| `SUPABASE_ANON_KEY` | Supabase Dashboard → Settings → API → Regenerate | DevOps | Quarterly |
| `SUPABASE_SERVICE_ROLE_KEY` | Supabase Dashboard → Settings → API → Regenerate | DevOps | Quarterly |
| `UPSTASH_REDIS_REST_TOKEN` | Upstash Console → Database → Reset Token | DevOps | Quarterly |

After rotation: update Vercel env vars → trigger a new deployment → run smoke checklist (section 5).

---

## 2. Schema Migration

### First deployment (new Supabase project)

```bash
supabase link --project-ref <your-project-ref>
supabase db push
```

Verify migration applied:

```bash
supabase db diff   # must output: No schema changes found
```

### Subsequent migrations

```bash
supabase migration new <description>
# Edit supabase/migrations/<timestamp>_<description>.sql
supabase db push
```

**Never** edit `202605211900_initial.sql` directly — create a new migration file.

---

## 3. Vercel Deployment Steps

### Preview deploy

```bash
vercel env pull .env.local   # sync cloud env to local
vercel                        # deploys to preview URL
```

### Production promote

```bash
vercel --prod
```

Or via GitHub integration: merge to `main` → Vercel auto-deploys.

**Gate**: the `adversarial-gate` and `integration-rls` CI checks must be green
before merging (A5 + A12 CRITICA — see `.github/workflows/test.yml`).

---

## 4. Supabase Edge Function: purge-expired-todos

Deploy the 30-day purge cron (A24):

```bash
supabase functions deploy purge-expired-todos
```

Configure the schedule in `supabase/config.toml`:

```toml
[functions.purge-expired-todos]
schedule = "0 3 * * *"   # daily at 03:00 UTC
```

Manual trigger for verification:

```bash
supabase functions invoke purge-expired-todos --local
```

Expected response: `{ "purged": <n>, "cutoff": "<ISO date>", "timestamp": "<ISO date>" }`

---

## 5. Smoke Test Checklist (post-deploy)

Run after every production promote. Record results in `docs/SMOKE-LOG.md`.

### Authentication

- [ ] Sign up with a fresh email → lands in empty todo list (SC-001: < 90 seconds)
- [ ] Sign out → redirected to `/sign-in`
- [ ] Sign in with same email + password → same (empty) list visible
- [ ] Request magic link → check inbox → click link → lands in app (SC-002: < 30 seconds)
- [ ] Submit wrong credentials → generic error message, no email enumeration (FR-005)

### Todo CRUD

- [ ] Create 3 todos → all visible, most-recent first
- [ ] Mark one complete → completion timestamp visible, visually distinct
- [ ] Edit one → text updated; `updated_at` advanced on reload
- [ ] Soft delete one → disappears from active list immediately

### Multi-tenant isolation (SC-003)

- [ ] Open two browsers as users A and B → A's todos are invisible to B

### Adversarial (SC-004)

- [ ] Anonymous GET `/todos` → redirected to `/sign-in`, no todo data in body
- [ ] Anonymous fetch to any `/api/todos/*` endpoint → `UNAUTHENTICATED` response
- [ ] Check browser bundle for `service_role` string → must NOT be found

### Observability

- [ ] Vercel Analytics dashboard shows page-view events after navigation
- [ ] Vercel Logs show structured JSON lines for auth + todo events
- [ ] No email addresses visible in log output (A22 redaction)

---

## 6. Rollback

If a production deploy fails smoke check:

```bash
vercel rollback   # reverts to previous production deployment
```

If a migration causes issues: create a new migration to revert the change —
**never** `supabase db reset` in production.

---

## 7. Useful Operations

| Task | Command |
|---|---|
| View Vercel logs | `vercel logs --follow` |
| Inspect auth events | `select * from auth_events order by occurred_at desc limit 50;` |
| Inspect todo events | `select * from todo_events order by occurred_at desc limit 50;` |
| Manual purge trigger | `supabase functions invoke purge-expired-todos` |
| Reset local DB | `supabase db reset` (local only) |
