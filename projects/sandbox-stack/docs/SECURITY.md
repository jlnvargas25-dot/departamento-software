# Security Reference — sandbox-stack Todo App

**A22 + A12 + A5**: This document covers all security-sensitive configuration,
rotation schedules, and threat model notes.

---

## Environment Variables

| Variable | Classification | Notes |
|---|---|---|
| `NEXT_PUBLIC_SUPABASE_URL` | Public | Safe in browser bundle |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | Public (restricted) | RLS enforces access — anon key alone cannot read other users' data |
| `SUPABASE_SERVICE_ROLE_KEY` | SECRET — server only | Bypasses RLS; never in `NEXT_PUBLIC_` prefix |
| `UPSTASH_REDIS_REST_URL` | Server only | Rate limiter endpoint |
| `UPSTASH_REDIS_REST_TOKEN` | SECRET — server only | Rate limiter auth |

### Verification (post-deploy)

1. Open browser DevTools on the production URL.
2. Go to Network → search JS bundle responses for the strings `service_role` and `UPSTASH_REDIS_REST_TOKEN`.
3. If either string appears → CRITICAL: revoke the exposed key immediately and investigate the build.

---

## Rotation Schedule (A22)

| Secret | Rotation Method | Frequency | Owner |
|---|---|---|---|
| Supabase Anon Key | Dashboard → Settings → API → Regenerate | Quarterly | DevOps |
| Supabase Service Role Key | Dashboard → Settings → API → Regenerate | Quarterly | DevOps |
| Upstash Redis Token | Upstash Console → Database → Reset Token | Quarterly | DevOps |

After any rotation:
1. Update Vercel env vars immediately.
2. Trigger a new deploy.
3. Run full smoke checklist (see `docs/DEPLOYMENT.md` section 5).

---

## RLS Threat Model (A5)

The database enforces `auth.uid() = user_id` on every DML operation via Postgres Row-Level Security. This is the **primary** enforcement layer — not the application layer.

Attack vectors tested (see `tests/e2e/adversarial-*.spec.ts` and `tests/integration/rls-isolation.spec.ts`):

| Vector | Defense | Test |
|---|---|---|
| Anonymous direct Supabase client SELECT | RLS: auth.uid()=null → 0 rows | RLS-01 |
| Anonymous INSERT with forged user_id | RLS: WITH CHECK fails → 42501 | RLS-02 |
| User B SELECT user A's todos | RLS: auth.uid() ≠ user_id → 0 rows | RLS-03, RLS-04 |
| User B UPDATE user A's todo | RLS: 0 rows matched | RLS-05 |
| User B DELETE user A's todo | RLS: 0 rows matched | RLS-06 |
| User B INSERT with A's user_id | RLS: WITH CHECK fails | RLS-08 |

---

## Zero-Trust Middleware (A12)

Every request to protected routes passes through:

1. **Middleware** (`src/middleware.ts`): calls `supabase.auth.getUser()` to validate JWT signature server-side. Cookie existence alone is NOT trusted.
2. **Server actions** (`src/app/actions/*.ts`): independently call `getUser()` at the top of every action. Middleware is defense-in-depth, not the gate.
3. **RLS** (`supabase/migrations/202605211900_initial.sql`): enforces at the DB layer regardless of application code path.

This is a 3-layer defense: middleware → server action → RLS.

---

## PII Handling (A21, A22)

- Email addresses are classified as PII.
- The pino logger is configured with `redact: { paths: ["email", "*.email", "password", "*.password", "*.token"] }`.
- IP addresses are FNV-1a hashed before storage in `auth_events.ip_hash` — raw IPs are never persisted.
- Deleted accounts cascade to destroy all todos within 30 days (A24 purge cron + FK ON DELETE CASCADE).

---

## Rate Limiting (A16)

| Endpoint | Limit | Window |
|---|---|---|
| Sign-up | 10 attempts | Per IP per hour |
| Magic link request | 5 attempts | Per IP per hour |

Implemented via Upstash Redis sliding window. Falls back to in-memory counter if Redis is unavailable (local dev only — not suitable for production multi-instance).

---

## Audit Trail (A6, A21)

- `public.todo_events`: append-only audit log for all todo mutations. No UPDATE/DELETE RLS policy defined → DB rejects any modification attempt.
- `public.auth_events`: auth lifecycle log inserted via service-role only (bypasses RLS). No INSERT policy for anon/authenticated keys.

Both tables are immutable by design at the DB level.

---

## Pre-production Risks

Items documented here are KNOWN, non-blocking risks accepted for v1 with an explicit follow-up commitment.

### CSP `style-src 'unsafe-inline'` (MEDIUM)

**Status**: Accepted for v1 — ADR-FOLLOWUP required before public launch.

**Detail**: The current `Content-Security-Policy` allows `'unsafe-inline'` in `style-src`. This is required by Tailwind CSS v3 `@apply` rules and Next.js inline critical styles. Without it, styles break entirely.

**Remediation path** (either option):
- Option A: Add nonce-based CSP via Next.js middleware — inject a per-request nonce, pass it to `<style>` tags and the CSP header simultaneously.
- Option B: Hash-based allowlisting — enumerate all inline style hashes at build time (complex with Tailwind).

**Owner**: DevOps + Frontend lead.
**File**: `next.config.ts` → `buildCsp()` → `style-src` directive.
