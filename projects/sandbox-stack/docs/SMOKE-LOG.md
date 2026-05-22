# Smoke Test Log

Record results here after every production promote and every preview deploy
that touches auth, todos, or RLS (per quickstart.md section 7).

---

## Format

```
## [YYYY-MM-DD] Deploy: <vercel-preview-url or "production">

| Check | Result | Notes |
|---|---|---|
| SMOKE-01 Sign up → todos | PASS / FAIL / SKIP | ... |
...
```

---

## [2026-05-21] Sandbox — Initial implementation (Iteración 3)

**Environment**: Local (`http://localhost:3000`)
**Status**: Sandbox — tests written; execution requires `supabase start` + `npm run dev`.
**Executed by**: Iteración 3 Phase 5+6 sub-agent (file-only mode)

| Check | Result | Notes |
|---|---|---|
| SMOKE-01 Sign up → land in todos | NOT RUN | Requires running dev server + Supabase |
| SMOKE-02 Create 3 todos → visible | NOT RUN | Same |
| SMOKE-03 Mark complete → visual distinction | NOT RUN | Same |
| SMOKE-04 Sign out → /sign-in redirect | NOT RUN | Same |
| SMOKE-05 Anonymous GET /todos → /sign-in | NOT RUN | Same |
| SMOKE-06 Anonymous server action → UNAUTHENTICATED | NOT RUN | Same |
| SMOKE-07 Multi-tenant isolation (A vs B) | NOT RUN | Same |
| Bundle check: no service_role string | NOT RUN | Requires `npm run build` |
| Vercel Analytics events visible | NOT RUN | Requires Vercel deploy |
| Purge cron function deployed | NOT RUN | Requires `supabase functions deploy` |

**Next action**: Run `npm run test:all` after `supabase start` to get first green baseline.

---

_Add new entries above this line, newest first._
