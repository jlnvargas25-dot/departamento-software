# Proposal: Personal Todo Management with User Authentication

**Change name**: todo-management
**Phase**: sdd-propose
**Date**: 2026-05-21
**Artifact store**: openspec
**Run purpose**: T1.9 — empirical comparison `sdd-*` vs `speckit-*` on identical input
**Upstream**: `openspec/changes/todo-management/exploration.md`

---

## Why

A signed-in user needs a private place to capture and complete personal tasks. The smallest correct version of this is also the **canonical Tier-1 SaaS multi-tenant pattern at scale = 1**: one user = one tenant, no sharing, no workspaces. The same A5 (Multi-tenant Isolation) and A12 (Zero Trust) constraints that apply to a 10k-user product apply here — so this is the cheapest realistic case to validate the whole sandbox stack (Next.js + Supabase + Vercel + RLS) end-to-end.

**Problem**: greenfield. No code exists. No prior contract on auth, ownership, observability or rollback strategy. Without a proposal artifact, the spec phase has no anchor to enumerate invariants against.

**Value**:
1. Produces a working canonical reference for "Tier-1 multi-tenant @ scale 1" inside the Framework Departamento.
2. Generates empirical evidence for ADR-009 R1 (`sdd-*` vs `speckit-*` friction comparison).
3. Locks design tradeoffs as **explicit assumptions**, not implicit defaults, so the spec phase can audit them.

---

## What Changes

### In Scope (v1)

- Email/password + magic link auth via Supabase Auth (US2).
- Todo CRUD: create, list, update title, toggle complete, soft-delete (US1).
- Strict ownership: a user sees and mutates only `todos WHERE user_id = auth.uid() AND deleted_at IS NULL`.
- Anonymous access fully blocked at both server-action layer and DB (RLS).
- Server Actions as the only data-access surface (no `/api/*` routes).
- Hexagonal layout: `domain/` -> `ports/` -> `adapters/{supabase,next}/`.
- `Result<T, E>` tagged union on every server action.
- Structured logs via `pino` with PII redaction (`email` masked).
- Soft-delete with 30-day cron purge job.
- Adversarial test matrix (A15) covering cross-tenant access, anon access, expired session, RLS bypass attempts.

### Out of Scope (deferred, NOT v1)

- Shared workspaces / multi-user collaboration.
- Optimistic UI (`useOptimistic`) — server round-trip in v1.
- Pagination — load-all capped at 200 items in v1.
- OpenTelemetry traces — `pino` + Vercel Analytics only.
- External API / mobile clients — Server Actions are sufficient.
- `SECURITY DEFINER` RPCs — direct RLS-aware queries suffice.
- GDPR Right-to-Erasure flow — see Assumption #4.
- Audit event tables (`todo_events`, `auth_events`) — see Assumption #5.
- Circuit breaker for Supabase outages (A19 deferred to v1.1).

---

## Capabilities

> Contract between this proposal and `sdd-spec`. The spec phase will create one
> `openspec/specs/<capability>/spec.md` per "New Capability" below.

### New Capabilities

- `auth-session`: Email/password and magic-link sign-in/sign-out, session cookie handling, server-side session extraction, anonymous redirect.
- `todo-management`: User-owned todo lifecycle — create, list (active), update title, toggle complete, soft-delete; ownership invariant enforced at server action + RLS.
- `data-lifecycle`: Soft-delete semantics, 30-day purge cron, `deleted_at` filtering everywhere, hard-delete on account erasure path (stub for v2).
- `observability`: Structured `pino` logs, PII redaction policy, server-action timing metrics, error categorization (auth / authz / domain / infra).

### Modified Capabilities

None. This is greenfield — no existing specs in `openspec/specs/`.

---

## Approach

Spine pulled from `exploration.md` recommendation:

| Dimension | Decision |
|-----------|----------|
| Data access | Server Actions (no `/api/*`) |
| Security | RLS (DB) + server-side ownership check (app) — defense in depth |
| Auth | Both email/password + magic link (Supabase native) |
| Architecture | Hexagonal: `domain/` -> `ports/` -> `adapters/{supabase,next}/` |
| Delete | Soft delete + 30-day cron purge |
| Errors | `Result<T, E>` tagged union end-to-end |
| State | Server round-trip v1; optimistic UI deferred v2 |
| Observability | `pino` + Vercel Analytics; PII redaction; traces deferred v2 |
| Testing | Adversarial-first (A15) — cross-tenant + bypass cases gate the merge |

---

## 3 Capas Afectadas (Principio II)

| Capa | Mecanismo en este change |
|------|--------------------------|
| **Preventiva** (compile / load) | TypeScript strict mode; `zod` schemas for input DTOs; hexagonal layout structurally prevents `domain/` from importing `@supabase/*` (A4 + A20); env-var schema validation at boot rejects missing `SUPABASE_*`. |
| **Verificable** (runtime / test) | `getServerSession()` at top of every server action (A12 ZT-3); Postgres RLS policies on `todos`; `pino` structured logs with redaction; adversarial test matrix (A15) covering anon access, cross-tenant access, RLS bypass via `service_role` leak. |
| **Correctiva** (auto-fix) | Soft-delete is itself a corrective layer: accidental deletes recoverable within 30 days. Auth middleware **auto-redirects** unauthenticated requests to `/login` (deterministic — not LLM-mediated). Idempotent `complete`/`delete` (A8) auto-collapses double-clicks instead of erroring. |

---

## Python vs LLM (Principio I)

This sandbox does not have the Python orchestration layer yet (pre-Sprint 2 — see `../../CLAUDE.md` state section). For this change, the mapping is:

| Layer | Generated/orchestrated by | Verified by |
|-------|---------------------------|-------------|
| SQL migration files (`supabase/migrations/*.sql`) | LLM authors content; SDD spec phase locks invariants | Deterministic check: `supabase db diff --linked` MUST be empty before merge (planned for `sdd-verify`); RLS test matrix MUST pass |
| RLS policies | LLM drafts; reviewer reads against A5 checklist | Adversarial cross-tenant test MUST fail-closed (deterministic boolean gate) |
| Server actions (`Result<T,E>` shape) | LLM implements | `tsc --noEmit` (planned, currently absent — see `config.yaml` `testing`) + eslint rule for unhandled `Result` |
| `pino` log redaction config | LLM authors | Deterministic grep: log fixture MUST NOT contain raw `email` substring after redaction layer (CI gate) |
| Soft-delete purge cron | LLM authors handler | Deterministic: dry-run on staging DB MUST report exact row count before scheduled run |

**Anti-pattern explicitly avoided**: do **not** ask the LLM to "decide" whether a request is authenticated. The `getServerSession()` call is deterministic Python-equivalent code (TypeScript here, but same role) — the LLM only wires it in. (4th principio: auto-fix > finding; 1st principio: code traces, LLM walks.)

---

## Meta-Pattern Reference (Principio V — cross-pollination)

A-rules in scope (from `exploration.md` table; criticality preserved):

**CRITICAL** — A5 (Multi-tenant Isolation), A12 (Zero Trust), A20 (Hexagonal), A21 (Observability), A22 (Secrets), A24 (Data Lifecycle).

**Important** — A4 (Aciclicidad), A8 (Idempotency), A11 (DAO+DTO), A13 (Concurrency Safety), A14 (Explicit Failure), A15 (Unhappy Path First), A16 (Rate Limiting), A19 (External Resilience), A25 (Authorization).

**Polinización candidates** (patterns this change formalizes for reuse elsewhere):

1. **"RLS + server-side ownership check"** pair — reusable for every future Tier-1 multi-tenant table. Candidate to extract as Framework rule (`A5.1`) or as a reusable skill (`skill: tier1-tenant-table`).
2. **`Result<T, E>` + `pino`-redaction pair** at every server-action boundary — candidate cross-cutting pattern for all Server-Action features.
3. **Adversarial-test-matrix-before-happy-path** workflow (A15 made concrete) — candidate to formalize as a `sdd-tasks` lint that fails if no adversarial pair exists per feature task.

These will be flagged again at `sdd-archive` (paso 12 — radar de polinización).

---

## Affected Areas

| Area | Impact | Description |
|------|--------|-------------|
| `src/domain/todo.ts` | New | `Todo` entity, invariants, `TodoId`, validation rules. No infra imports. |
| `src/domain/auth.ts` | New | `AuthIdentity`, `UserId` brand types. |
| `src/ports/todo-repository.ts` | New | Repository interface — port for adapters. |
| `src/ports/auth-port.ts` | New | Session/auth port. |
| `src/adapters/supabase/todo-repository.ts` | New | Supabase implementation of `TodoRepository`. |
| `src/adapters/supabase/auth-adapter.ts` | New | Supabase Auth wrapper. |
| `src/adapters/supabase/client.ts` | New | `createServerClient()` / `createBrowserClient()` factories. |
| `src/adapters/next/actions/*.ts` | New | Server actions returning `Result<T,E>`. |
| `app/(auth)/login/page.tsx` | New | Email/password + magic link UI. |
| `app/(app)/todos/page.tsx` | New | Authenticated todos page. |
| `app/layout.tsx` + `middleware.ts` | New | Root layout + auth redirect middleware. |
| `supabase/migrations/0001_init.sql` | New | `todos` table, indexes, `deleted_at`. |
| `supabase/migrations/0002_rls.sql` | New | RLS policies — owner-only, deleted-filter. |
| `supabase/functions/purge-deleted/index.ts` | New | 30-day soft-delete purge cron. |
| `src/lib/result.ts` | New | `Result<T, E>` tagged union (A14). |
| `src/lib/logger.ts` | New | `pino` instance + PII redaction config (A21). |
| `src/lib/env.ts` | New | Env-var schema validation at boot (A22). |
| `.env.example` | New | Documents required env keys; secrets never committed. |
| Vercel project env | Modified | `SUPABASE_URL`, `SUPABASE_ANON_KEY` (public), `SUPABASE_SERVICE_ROLE_KEY` (secret, server-only). |
| `package.json` | New | Next 15, `@supabase/ssr`, `zod`, `pino`, Vitest, Playwright. |
| `vitest.config.ts` + `playwright.config.ts` | New | Test runners (currently absent per `openspec/config.yaml`). |
| `eslint.config.mjs` + `tsconfig.json` | New | Strict TS, hexagonal import-boundary rule. |

---

## Open Assumptions (converted from exploration §Open Questions)

These are **decisions**, not questions. Spec phase may challenge any of them with a structural reason.

| # | Assumption | Source question | Reversal cost |
|---|-----------|-----------------|---------------|
| 1 | **Custom SMTP** (Resend or SES) is configured in the Supabase project before production. Default Supabase SMTP (4 magic links/hr) is acceptable for staging only. | SMTP | Low — config change, no schema impact. |
| 2 | **Rate limiting backend = Upstash Redis** (free tier sufficient v1). Auth endpoints rate-limited; CRUD endpoints not (single-user scope). | Rate-limit backend | Medium — adds one secret (A22) and one dependency. |
| 3 | **Session duration = Supabase defaults** (1h access, 7d refresh). Sliding refresh on activity. | Session duration | Low — configuration. |
| 4 | **GDPR scope = NOT in v1**. App targets EN/ES users without EU residency claim. Right-to-erasure stub in `data-lifecycle` spec but not wired. Soft-delete window applies uniformly. | GDPR | High if reversed late — affects `data-lifecycle` retention semantics; spec phase must flag it as "REVIEW IF EU LAUNCH". |
| 5 | **Audit event tables = deferred to v1.1**. `todo_events` / `auth_events` not in v1; A6 (Append-Only) satisfied for v1 by `pino` log retention. | Audit tables | Medium — 2 migrations + RLS policy; design phase MAY override if A6 deemed critical. |
| 6 | **Pagination = load-all with hard cap of 200 todos** per user. Above 200, oldest active items hidden with banner; deleted items never loaded. | Pagination | Low — UI + server-action change, no schema. |
| 7 | **`completed` semantics = boolean + `completed_at TIMESTAMPTZ`**. Timestamp enables A6/A24 trail without separate event table. | `completed` shape | Low — additive column. |
| 8 | **Region alignment = both `us-east-1`** (Vercel + Supabase). Documented as a deployment invariant; mismatch is a CI warning. | Region | Low — Vercel/Supabase project setting. |

---

## Success Criteria (empirical, NOT aspirational — Principio I/II)

- [ ] **Anonymous access blocked end-to-end**: automated test asserts `GET /todos` and every server-action call without session returns HTTP 401/redirect, AND direct DB query via `anon` key returns `0 rows` for any user's todos. (Two independent gates — A5 + A12.)
- [ ] **Cross-tenant access impossible**: adversarial test creates user A and user B; user B's session **cannot** read, update, or soft-delete any of user A's todos via server action OR direct DB call. Test MUST be red before RLS+ownership-check is wired, green after. (A5 + A15.)
- [ ] **`Result<T, E>` coverage = 100%**: every exported server action's return type is `Result<T, E>`. Verified by an `eslint` rule (planned) OR `tsc --noEmit` + grep over `app/actions` (deterministic).
- [ ] **PII redaction verified**: log fixture run through `pino` MUST NOT contain raw `email` substring. CI grep gate, deterministic boolean.
- [ ] **Hexagonal boundary holds**: `rg "supabase" src/domain/` returns zero matches. Deterministic.
- [ ] **Soft-delete purge dry-run accurate**: cron handler dry-run on seeded staging DB MUST report the exact row count that a non-dry run would delete (off-by-one is a fail).
- [ ] **Adversarial test matrix exists and is red-first**: at least one test per A-rule in CRITICAL scope (A5, A12, A20, A21, A22, A24) — six tests minimum, each written **before** the feature it protects.
- [ ] **Empirical artifact for ADR-009 R1 produced**: `EVALUATION.md` captures `sdd-*` chain timing, A-rule coverage observed, and operator friction signals — comparable side-by-side with `specs/001-todo-management/`. (T1.9 closure condition.)

---

## Rollback Plan

This is greenfield; rollback is **scope-removal**, not state-restoration. Order matters:

1. **Pre-merge**: abandon = delete `openspec/changes/todo-management/` and any feature branch. No production impact.
2. **Post-deploy, pre-traffic**: revert the deployment in Vercel (one-click previous deployment). Revoke `SUPABASE_SERVICE_ROLE_KEY` rotation if it was issued for this deploy.
3. **Post-traffic, data already written**:
   1. Disable user-facing routes in Vercel (deploy a "maintenance" build that returns 503 on `/todos` and `/login`).
   2. Run `supabase db dump --data-only --table=todos` to a versioned S3 bucket (A24 audit).
   3. Drop `todos` table via reverse migration `supabase/migrations/0001_init.down.sql`.
   4. Revoke RLS policies via `0002_rls.down.sql`.
   5. Remove Supabase Auth users via Admin API (only if change is fully abandoned; otherwise keep).
   6. Cancel the `purge-deleted` cron in Supabase Functions.
4. **Secrets rotation**: `SUPABASE_SERVICE_ROLE_KEY` rotated (A22) regardless of cause if rollback was triggered by a security incident.
5. **Decision artifact**: write rollback rationale into `decisions/ADR-XXX-rollback-todo-management.md`. The rollback itself is a meta-pattern candidate (5th principio) — capture it.

**Reversibility note (per `design` rule R-5)**: every operation listed above is **reversible** within 24h of deploy. After 24h, soft-deleted rows older than 24h that the purge cron has already hard-deleted are NOT recoverable — this is the rollback's hard floor.

---

## Risks

| Risk | Likelihood | Impact | Mitigation |
|------|------------|--------|------------|
| RLS policy misconfiguration leaks cross-tenant data | Medium | CRITICAL (A5) | Adversarial test gate before merge; server-side check is independent second barrier; `service_role` key never reaches client (A22). |
| `service_role` key leak via env misuse | Low | CRITICAL (A22) | `env.ts` schema validation refuses to expose `SUPABASE_SERVICE_ROLE_KEY` to client bundle; eslint rule bans `process.env.SUPABASE_SERVICE_ROLE_KEY` in `app/` client components; Vercel marks it server-only. |
| Magic-link SMTP rate-limit in production | Medium (if Assumption #1 violated) | High UX | Block production launch until custom SMTP verified; staging uses default SMTP. |
| Soft-delete `WHERE deleted_at IS NULL` forgotten in a query path | Medium | High (tombstone leak) | RLS policy itself filters `deleted_at IS NULL`; lint rule for `from('todos')` requires explicit filter or `.is('deleted_at', null)`. |
| Adversarial tests written AFTER happy path (A15 violated) | High (process risk) | Medium | `sdd-tasks` will be required to pair every feature task with adversarial test task; `sdd-verify` rejects if pair missing. |
| Vercel <-> Supabase region mismatch (Assumption #8 violated) | Low | Medium (cold start) | Document as deployment invariant; CI warning, not blocker. |
| `Result<T, E>` adopted partially, mixing thrown exceptions in some actions | Medium (process risk) | Medium (API inconsistency) | `eslint` rule (planned) flagging server actions whose return type is not `Result<_, _>`; spec phase enumerates it as MUST. |
| Sandbox lacks test runner today (per `openspec/config.yaml`) | High (known) | Blocks Success Criteria verification | Tasks phase MUST schedule Vitest + Playwright install as foundational task **before** any feature task. Per `config.yaml`, this is expected. |
| Comparison contamination: reader of this proposal also reads `specs/001-todo-management/` | Medium (process risk) | High (T1.9 invalidated) | Each phase explicitly forbids cross-reading; `EVALUATION.md` documents isolation discipline. |

---

## Dependencies

- **External services**: Supabase project (URL + anon key + service-role key) provisioned; Vercel project linked.
- **Pre-flight (must precede task execution)**: Vitest + Playwright + eslint + prettier installed as the **first foundational task** in `sdd-tasks` (currently absent per `openspec/config.yaml` `testing` block).
- **Upstream artifact**: `exploration.md` (✓ present).
- **Constitutional anchors**: `../../CLAUDE.md` (7 principios), `architecture/PRINCIPIOS-ARQUITECTURA.md` (A1–A25), `PROTOCOLO-CONSTRUCCION-CODIGO.md` (R-0 a R-6).
- **Strategic anchor**: ADR-009 v0.5 — this change is evidence for R1 (sdd-* vs speckit-* comparison).

---

## Next Phase

Ready for **`sdd-spec`** (define MUST/SHOULD requirements per capability, RFC-2119 keywords, Given/When/Then) and **`sdd-design`** (sequence diagrams, port/adapter contracts, RLS policy SQL, trace boundaries). These two MAY run in parallel — they read this proposal and produce independent artifacts.
