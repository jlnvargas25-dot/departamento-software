# Tasks: Personal Todo Management with User Authentication

**Change name**: todo-management
**Phase**: sdd-tasks
**Date**: 2026-05-21
**Artifact store**: openspec
**Run purpose**: T1.9 — empirical comparison `sdd-*` vs `speckit-*`
**Strict TDD**: DISABLED (no test runner installed — Vitest + Playwright scheduled in Phase 0)
**Delivery strategy**: single-pr (sandbox comparison run)

---

## Review Workload Forecast

| Field | Value |
|-------|-------|
| Estimated changed lines | 1 800 – 2 400 (greenfield: 30+ new files, migrations, tests, CI) |
| 400-line budget risk | High |
| Chained PRs recommended | No (delivery strategy override: single-pr) |
| Suggested split | Single PR — sandbox comparison run; `size:exception` accepted |
| Delivery strategy | single-pr |
| Chain strategy | size-exception |

Decision needed before apply: No
Chained PRs recommended: No
Chain strategy: size-exception
400-line budget risk: High

### Suggested Work Units

| Unit | Goal | Likely PR | Notes |
|------|------|-----------|-------|
| 1 | All 7 phases | PR 1 (size:exception) | Sandbox comparison — single diff for fair evaluation against speckit-* |

---

## Phase 0 — Foundational Infrastructure

- [ ] **T-00** Init repo scaffold
  - **What**: Run `npx create-next-app@15` with TypeScript, App Router, Tailwind; commit baseline.
  - **Done when**: `npx tsc --noEmit` exits 0 on the empty scaffold.
  - **A-rule(s)**: A20, A22
  - **Depends on**: —
  - **Parallel-OK with**: —

- [ ] **T-01** Install and configure toolchain
  - **What**: Add Vitest, `@vitest/ui`, Playwright, eslint (flat config), prettier, `eslint-plugin-import`; write `vitest.config.ts` and `playwright.config.ts`.
  - **Done when**: `npx vitest run` exits 0 (no tests yet = pass); `npx playwright install` completes without error.
  - **A-rule(s)**: A15
  - **Depends on**: T-00
  - **Parallel-OK with**: —

- [ ] **T-02** TypeScript strict mode + hexagonal import-boundary lint rule
  - **What**: Set `"strict": true` in `tsconfig.json`; configure `eslint-plugin-import` rule that forbids `src/domain/` from importing `src/adapters/`, `src/lib/`, or any `node_modules` infra package.
  - **Done when**: `rg "supabase|pino|@upstash|next/" src/domain/` returns 0 matches; `npx tsc --noEmit` exits 0.
  - **A-rule(s)**: A4, A20
  - **Depends on**: T-01
  - **Parallel-OK with**: T-03

- [ ] **T-03** Environment variable schema (`src/lib/env.ts`)
  - **What**: Write zod schema validating `NEXT_PUBLIC_SUPABASE_URL`, `NEXT_PUBLIC_SUPABASE_ANON_KEY`, `SUPABASE_SERVICE_ROLE_KEY` (server-only), `UPSTASH_REDIS_REST_URL`, `UPSTASH_REDIS_REST_TOKEN`; throws at boot if any is missing. Add `.env.example` with placeholder values; `.gitignore` covers `.env*` excluding `.example`.
  - **Done when**: `node -e "require('./src/lib/env')"` with a missing var exits non-zero with an explicit error message; `.env.example` committed; `git status` shows no `.env.local` tracked.
  - **A-rule(s)**: A22
  - **Depends on**: T-01
  - **Parallel-OK with**: T-02

- [ ] **T-04** Pino logger singleton (`src/lib/logger.ts`)
  - **What**: Create pino instance with `base: { service: "todo-app" }`, `redact.paths: ["context.email", "context.user.email", "*.email", "context.userId", "*.password"]`, `censor: "<REDACTED>"`. Add eslint rule forbidding `console.*` outside `src/lib/logger.ts`.
  - **Done when**: Unit test `tests/unit/logger.test.ts` — logs `{ context: { email: "x@example.com" } }` and asserts output JSON contains `"<REDACTED>"`, NOT the raw email. `npx vitest run tests/unit/logger.test.ts` exits 0.
  - **A-rule(s)**: A21, A24
  - **Depends on**: T-01, T-03
  - **Parallel-OK with**: T-05

- [ ] **T-05** `Result<T, E>` library (`src/domain/result.ts` + `src/lib/result-helpers.ts`)
  - **What**: Implement `Result<T,E>` tagged union with `Ok<T>` / `Err<E>` variants; export `Ok()` and `Err()` constructors; export `isOk()` / `isErr()` type guards.
  - **Done when**: `npx tsc --noEmit` exits 0; unit test `tests/unit/result.test.ts` asserts round-trip Ok/Err construction and type narrowing.
  - **A-rule(s)**: A14
  - **Depends on**: T-02
  - **Parallel-OK with**: T-04

- [ ] **T-06** Supabase client factories (`src/adapters/supabase/client.ts`)
  - **What**: Implement `createServerClient()` (cookie-based, `@supabase/ssr`) and `createBrowserClient()` factories; import `env.ts` for credentials; add eslint rule banning `process.env.SUPABASE_SERVICE_ROLE_KEY` outside `src/adapters/supabase/` and `supabase/functions/`.
  - **Done when**: `npx tsc --noEmit` exits 0; eslint reports 0 errors on `src/adapters/supabase/client.ts`.
  - **A-rule(s)**: A22
  - **Depends on**: T-03
  - **Parallel-OK with**: T-05

- [ ] **T-07** Database migration — schema (`supabase/migrations/0001_init.sql`)
  - **What**: Write migration creating `public.todos` table per design §3.3 (columns, constraints, CHECK, two partial indexes, `moddatetime` trigger for `updated_at`).
  - **Done when**: `supabase db diff --linked` returns empty diff after applying the migration to a local Supabase instance.
  - **A-rule(s)**: A24
  - **Depends on**: T-00
  - **Parallel-OK with**: T-02, T-03, T-04, T-05

- [ ] **T-08** Database migration — RLS (`supabase/migrations/0002_rls.sql`)
  - **What**: Write RLS migration per design §9.1: enable RLS, four policies (SELECT/INSERT/UPDATE/anon REVOKE), no authenticated DELETE policy.
  - **Done when**: `supabase db diff --linked` returns empty diff; psql direct query with `anon` role against `todos` returns 0 rows.
  - **A-rule(s)**: A5, A25
  - **Depends on**: T-07
  - **Parallel-OK with**: T-05, T-06

- [ ] **T-09** CI workflow (`.github/workflows/ci.yml`)
  - **What**: Add GitHub Actions workflow: `tsc --noEmit`, eslint, `vitest run`, `playwright test`, deterministic CI gates (`rg "supabase|pino" src/domain/` → 0 matches; `rg "email" tests/fixtures/log-output.log` → 0 raw emails).
  - **Done when**: Workflow file lints without syntax errors (`actionlint`); at least the tsc and eslint steps run locally via `act` or pass in CI on push.
  - **A-rule(s)**: A15, A21
  - **Depends on**: T-01, T-02, T-04
  - **Parallel-OK with**: T-07, T-08

---

## Phase 1 — Domain + Ports (A20 Hexagonal)

- [ ] **T-10** Domain types — Auth (`src/domain/auth.ts`)
  - **What**: Define `UserId` brand type, `AuthIdentity` value object; zero infrastructure imports.
  - **Done when**: `rg "supabase|pino|@upstash|next/" src/domain/auth.ts` returns 0; `npx tsc --noEmit` exits 0.
  - **A-rule(s)**: A20
  - **Depends on**: T-05
  - **Parallel-OK with**: T-11

- [ ] **T-11** Domain types — Todo (`src/domain/todo.ts`)
  - **What**: Define `TodoId` brand type, `Todo` entity (all fields per design §3.3), `createTodo()` factory enforcing title invariants (1–500 chars, trim); zero infra imports.
  - **Done when**: Unit test `tests/unit/domain/todo.test.ts` covers empty title, 501-char title, and valid creation. `npx vitest run tests/unit/domain/todo.test.ts` exits 0.
  - **A-rule(s)**: A20, A14
  - **Depends on**: T-05
  - **Parallel-OK with**: T-10

- [ ] **T-12** Port — `TodoRepository` (`src/ports/todo-repository.ts`)
  - **What**: Define interface with five methods per design §5.3: `insert`, `listActiveByUser`, `updateTitle`, `toggle`, `softDelete`; all return `Promise<Result<_, _>>`.
  - **Done when**: `npx tsc --noEmit` exits 0; interface imports only from `src/domain/`.
  - **A-rule(s)**: A20, A11
  - **Depends on**: T-10, T-11
  - **Parallel-OK with**: T-13

- [ ] **T-13** Port — `AuthPort` + `LoggerPort` + `RateLimiterPort` (`src/ports/*.ts`)
  - **What**: Define three port interfaces per design §5.3 and §6; all return `Promise<Result<_,_>>` or `Promise<void>`; zero infra imports.
  - **Done when**: `npx tsc --noEmit` exits 0; all three files pass `rg "supabase|pino|@upstash" src/ports/` → 0 matches.
  - **A-rule(s)**: A20, A16
  - **Depends on**: T-10
  - **Parallel-OK with**: T-12

---

## Phase 2 — Supabase Adapters + Upstash Rate Limiter

- [ ] **T-14** `SupabaseTodoRepository` (`src/adapters/supabase/todo-repository.ts`)
  - **What**: Implement `TodoRepository` port; each method uses `createServerClient()`, scopes query with `userId`, applies `deleted_at IS NULL` where required; `softDelete` idempotent; `listActiveByUser` uses `LIMIT 201` and returns `{ todos, capped }`.
  - **Done when**: `npx tsc --noEmit` exits 0; integration test against local Supabase: `insert` then `listActiveByUser` returns 1 item.
  - **A-rule(s)**: A5, A11, A24
  - **Depends on**: T-08, T-12, T-06
  - **Parallel-OK with**: T-15

- [ ] **T-15** `SupabaseAuthAdapter` (`src/adapters/supabase/auth-adapter.ts`)
  - **What**: Implement `AuthPort`; `getServerSession()` uses `@supabase/ssr` cookie read; `signUp`, `signInPassword`, `signInMagicLink`, `signOut` wrap Supabase Auth calls; all return `Result<_,_>`.
  - **Done when**: `npx tsc --noEmit` exits 0; `getServerSession()` returns `null` when no cookie is present (unit test with mocked Supabase client).
  - **A-rule(s)**: A12, A22
  - **Depends on**: T-06, T-13
  - **Parallel-OK with**: T-14

- [ ] **T-16** `UpstashRateLimiter` (`src/adapters/upstash/rate-limiter.ts`)
  - **What**: Implement `RateLimiterPort` using `@upstash/ratelimit`; sliding-window algorithm; `check(ipHash, "auth")` returns `Result<{ allowed: true }, { code: "RATE_LIMITED", retryAfter: number }>`.
  - **Done when**: `npx tsc --noEmit` exits 0; unit test with mocked Upstash client asserts blocked result after threshold exceeded.
  - **A-rule(s)**: A16
  - **Depends on**: T-03, T-13
  - **Parallel-OK with**: T-14, T-15

- [ ] **T-17** Ownership check helper (`src/adapters/supabase/ownership-check.ts`)
  - **What**: Export `assertOwnership(rowCount: number): Result<void, { code: "NOT_FOUND" }>` — returns `Err` when 0 rows affected; used by all mutating repository methods.
  - **Done when**: Unit test covers 0-row and 1-row cases. `npx vitest run` exits 0.
  - **A-rule(s)**: A5, A25
  - **Depends on**: T-05
  - **Parallel-OK with**: T-14, T-15, T-16

---

## Phase 3 — Auth Server Actions + Middleware (US2)

- [ ] **T-18** Sign-up server action (`src/adapters/next/actions/auth/sign-up.ts`)
  - **What**: Implement `signUp(input)` — zod validate, rate-limit check, delegate to `AuthPort.signUp`, return `Result<{userId}, AuthError>`; log `action.success` / `action.validation_failed` / `action.signup_duplicate` per observability spec; non-enumerating error message.
  - **Done when**: Unit test covers spec scenarios: valid input → Ok, duplicate email → Err EMAIL_TAKEN (non-enumerating message), invalid email → Err VALIDATION_ERROR, rate-limited → Err RATE_LIMITED. `npx vitest run` exits 0.
  - **A-rule(s)**: A12, A16, A21
  - **Depends on**: T-13, T-15, T-16, T-04, T-05
  - **Parallel-OK with**: T-19, T-20

- [ ] **T-19** Sign-in server action (`src/adapters/next/actions/auth/sign-in.ts`)
  - **What**: Implement `signIn(input)` — zod validate, rate-limit check, `AuthPort.signInPassword`, persist httpOnly cookie via `@supabase/ssr`; timing-equal error for wrong password vs unknown email; log per observability spec.
  - **Done when**: Unit test covers: valid credentials → Ok + cookie set, wrong password → Err INVALID_CREDENTIALS (non-enumerating, timing-safe), empty fields → Err VALIDATION_ERROR, rate-limited → Err RATE_LIMITED + 429. `npx vitest run` exits 0.
  - **A-rule(s)**: A12, A16, A21
  - **Depends on**: T-13, T-15, T-16, T-04, T-05
  - **Parallel-OK with**: T-18, T-20

- [ ] **T-20** Magic-link server action (`src/adapters/next/actions/auth/magic-link.ts`)
  - **What**: Implement `sendMagicLink(input)` — zod validate email, rate-limit check, `AuthPort.signInMagicLink`; always returns `Result<{sent:true}, never>` for valid emails (no enumeration); log per spec.
  - **Done when**: Unit test: valid email → Ok regardless of whether email exists in Supabase; invalid format → Err VALIDATION_ERROR; rate-limited → Err RATE_LIMITED. `npx vitest run` exits 0.
  - **A-rule(s)**: A12, A16
  - **Depends on**: T-13, T-15, T-16, T-04, T-05
  - **Parallel-OK with**: T-18, T-19

- [ ] **T-21** Sign-out server action (`src/adapters/next/actions/auth/sign-out.ts`)
  - **What**: Implement `signOut()` — call `AuthPort.signOut()`, clear cookie (Max-Age=0), redirect to `/login`; idempotent (already-invalid session does not error — A8).
  - **Done when**: Unit test: authenticated call → cookie cleared, redirect; already-signed-out call → same redirect, no error. `npx vitest run` exits 0.
  - **A-rule(s)**: A8, A12
  - **Depends on**: T-15, T-04, T-05
  - **Parallel-OK with**: T-22

- [ ] **T-22** Auth redirect middleware (`app/middleware.ts`)
  - **What**: Implement Next.js edge middleware — check session cookie on every `/(app)/*` route; redirect to `/login` if absent; use `@supabase/ssr` cookie utilities to refresh session on valid request.
  - **Done when**: Playwright test: unauthenticated GET `/todos` → 302 to `/login`; authenticated GET `/todos` → 200. `npx playwright test tests/e2e/middleware.spec.ts` exits 0.
  - **A-rule(s)**: A12
  - **Depends on**: T-15
  - **Parallel-OK with**: T-21

- [ ] **T-23** Login page UI (`app/(auth)/login/page.tsx`)
  - **What**: Build RSC login page with email/password form + magic-link form; wires `signIn`, `signUp`, `sendMagicLink` server actions; displays non-enumerating error messages from `Result.Err`.
  - **Done when**: Playwright test: submit valid credentials → redirect to `/todos`; submit invalid email format → inline error visible. `npx playwright test tests/e2e/auth.spec.ts` exits 0.
  - **A-rule(s)**: A12
  - **Depends on**: T-18, T-19, T-20, T-22
  - **Parallel-OK with**: —

---

## Phase 4 — Todo Server Actions + UI (US1)

- [ ] **T-24** `createTodo` server action (`src/adapters/next/actions/todos/create.ts`)
  - **What**: Implement per design §2.3 skeleton — `getServerSession()` gate, zod validate title (1–500, trim), `TodoRepository.insert`, return `Result<{todo}, ActionError>`; log per observability spec.
  - **Done when**: Unit test covers: valid title → Ok with new todo, empty title → Err VALIDATION_ERROR, unauthenticated → Err UNAUTHENTICATED, 501-char title → Err VALIDATION_ERROR (TOO_LONG). `npx vitest run` exits 0.
  - **A-rule(s)**: A5, A12, A14, A21, A25
  - **Depends on**: T-14, T-17, T-04, T-05, T-13
  - **Parallel-OK with**: T-25, T-26, T-27, T-28

- [ ] **T-25** `listTodos` server action (`src/adapters/next/actions/todos/list.ts`)
  - **What**: Implement — `getServerSession()` gate, call `TodoRepository.listActiveByUser(userId, 200)` with `LIMIT 201` logic, return `Result<{todos, capped, total?}, ActionError>`.
  - **Done when**: Unit test: authenticated user with 0 todos → Ok empty array; authenticated with 250 → Ok 200 items + `capped: true`; unauthenticated → Err UNAUTHENTICATED. `npx vitest run` exits 0.
  - **A-rule(s)**: A5, A12
  - **Depends on**: T-14, T-04, T-05, T-13
  - **Parallel-OK with**: T-24, T-26, T-27, T-28

- [ ] **T-26** `updateTodoTitle` server action (`src/adapters/next/actions/todos/update-title.ts`)
  - **What**: Implement — session gate, zod validate title (1–500, trim), `TodoRepository.updateTitle(id, userId, title)`, ownership check (0 rows → NOT_FOUND), return `Result<{todo}, ActionError>`.
  - **Done when**: Unit test: valid update → Ok; wrong owner id → Err NOT_FOUND; deleted todo → Err NOT_FOUND; empty title → Err VALIDATION_ERROR. `npx vitest run` exits 0.
  - **A-rule(s)**: A5, A12, A25
  - **Depends on**: T-14, T-17, T-04, T-05
  - **Parallel-OK with**: T-24, T-25, T-27, T-28

- [ ] **T-27** `toggleTodo` server action (`src/adapters/next/actions/todos/toggle.ts`)
  - **What**: Implement per design §2.4 — session gate, `TodoRepository.toggle(id, userId)` which runs the idempotent UPDATE (NOT completed + completed_at); 0 rows → NOT_FOUND; return `Result<{todo}, ActionError>`.
  - **Done when**: Unit test: toggle false→true → Ok completed=true + completed_at set; toggle true→false → Ok completed=false + completed_at null; double-toggle → Ok (no error); wrong owner → Err NOT_FOUND. `npx vitest run` exits 0.
  - **A-rule(s)**: A5, A8, A12
  - **Depends on**: T-14, T-17, T-04, T-05
  - **Parallel-OK with**: T-24, T-25, T-26, T-28

- [ ] **T-28** `deleteTodo` server action (`src/adapters/next/actions/todos/delete.ts`)
  - **What**: Implement per design §2.5 — session gate, `TodoRepository.softDelete(id, userId)` idempotent (already-deleted → Ok, first timestamp preserved); return `Result<{id}, ActionError>`.
  - **Done when**: Unit test: active todo → Ok deleted; already-deleted → Ok (idempotent, no error); wrong owner → Err NOT_FOUND; unauthenticated → Err UNAUTHENTICATED. `npx vitest run` exits 0.
  - **A-rule(s)**: A5, A8, A12, A24
  - **Depends on**: T-14, T-17, T-04, T-05
  - **Parallel-OK with**: T-24, T-25, T-26, T-27

- [ ] **T-29** Todos page UI (`app/(app)/todos/page.tsx` + `app/layout.tsx`)
  - **What**: Build RSC todos page — calls `listTodos` server action, renders todo list, create form, toggle/delete buttons, overflow banner when `capped: true`; root `layout.tsx` with Vercel Analytics.
  - **Done when**: Playwright test: authenticated user sees own todos; create form submits and list updates (full page reload); overflow banner visible when mock returns `capped: true`. `npx playwright test tests/e2e/todos.spec.ts` exits 0.
  - **A-rule(s)**: A5, A21
  - **Depends on**: T-22, T-23, T-24, T-25, T-26, T-27, T-28
  - **Parallel-OK with**: T-30

- [ ] **T-30** Purge cron function (`supabase/functions/purge-deleted/index.ts`)
  - **What**: Implement Supabase Edge Function — receives `{ dry_run: boolean }`; SELECT count of rows where `deleted_at < NOW() - INTERVAL '30 days'`; on `dry_run=false` DELETE RETURNING id; log `{ purged_count, run_at, dry_run }` via pino-compatible structured output.
  - **Done when**: Invoke with `dry_run=true` on seeded local DB → count equals what `dry_run=false` would delete (off-by-one = FAIL). Unit test asserts log output structure. `npx vitest run tests/unit/purge-cron.test.ts` exits 0.
  - **A-rule(s)**: A8, A13, A24
  - **Depends on**: T-08, T-04
  - **Parallel-OK with**: T-29

---

## Phase 5 — Adversarial Tests (A15 — must be written before or alongside feature code)

- [ ] **T-31** ADV-A1: Rate-limit brute-force test
  - **What**: Write `tests/adversarial/auth/rate-limit.test.ts` — simulate 100 sign-in attempts in 60s window against mocked Upstash; assert 429 returned after threshold; Supabase Auth mock receives at most `threshold` calls.
  - **Done when**: `npx vitest run tests/adversarial/auth/rate-limit.test.ts` exits 0 and test is RED before T-16 is wired.
  - **A-rule(s)**: A15, A16
  - **Depends on**: T-01
  - **Parallel-OK with**: T-32, T-33, T-34, T-35, T-36, T-37, T-38, T-39

- [ ] **T-32** ADV-A2 + ADV-A3: Forged/expired JWT session test
  - **What**: Write `tests/adversarial/auth/session-forgery.test.ts` — pass forged JWT to `getServerSession()` mock; assert null returned and action returns Err UNAUTHENTICATED; replay expired token → same result.
  - **Done when**: `npx vitest run tests/adversarial/auth/session-forgery.test.ts` exits 0.
  - **A-rule(s)**: A12, A15
  - **Depends on**: T-01
  - **Parallel-OK with**: T-31, T-33, T-34, T-35, T-36, T-37, T-38, T-39

- [ ] **T-33** ADV-A4: Client-supplied `user_id` injection test
  - **What**: Write `tests/adversarial/auth/user-id-injection.test.ts` — call `createTodo` with `user_id: victimId` in payload; assert server action uses session userId, NOT payload; victim's todos untouched.
  - **Done when**: `npx vitest run tests/adversarial/auth/user-id-injection.test.ts` exits 0.
  - **A-rule(s)**: A5, A12, A15
  - **Depends on**: T-01
  - **Parallel-OK with**: T-31, T-32, T-34, T-35, T-36, T-37, T-38, T-39

- [ ] **T-34** ADV-A5: `service_role` key exposure test
  - **What**: Write `tests/adversarial/secrets/service-role-leak.test.ts` — run eslint on `app/**/*.tsx` and `app/**/*.ts`; assert zero matches for `SUPABASE_SERVICE_ROLE_KEY`; confirm `env.ts` boot throws on missing key.
  - **Done when**: `npx vitest run tests/adversarial/secrets/service-role-leak.test.ts` exits 0 (eslint run as child process in test).
  - **A-rule(s)**: A15, A22
  - **Depends on**: T-02, T-03
  - **Parallel-OK with**: T-31, T-32, T-33, T-35, T-36, T-37, T-38, T-39

- [ ] **T-35** ADV-T1 + ADV-T2 + ADV-T3: Cross-tenant access tests
  - **What**: Write `tests/adversarial/todos/cross-tenant.test.ts` — create user A + user B with separate mocked sessions; user B calls `updateTodoTitle`, `deleteTodo`, `toggleTodo` with user A's todo ID; assert Err NOT_FOUND for all three; no data leaked.
  - **Done when**: `npx vitest run tests/adversarial/todos/cross-tenant.test.ts` exits 0. Tests MUST be RED before T-14 RLS is wired.
  - **A-rule(s)**: A5, A15, A25
  - **Depends on**: T-01
  - **Parallel-OK with**: T-31, T-32, T-33, T-34, T-36, T-37, T-38, T-39

- [ ] **T-36** ADV-T4 + ADV-T5: Anon role + deleted-row RLS bypass tests
  - **What**: Write `tests/adversarial/todos/rls-bypass.test.ts` — query `todos` via Supabase `anon` key (no JWT); assert 0 rows returned; query with `deleted_at IS NOT NULL` filter on behalf of anon role; assert still 0 rows (RLS SELECT policy includes deleted_at IS NULL).
  - **Done when**: `npx vitest run tests/adversarial/todos/rls-bypass.test.ts` exits 0 against local Supabase instance.
  - **A-rule(s)**: A5, A12, A15
  - **Depends on**: T-08
  - **Parallel-OK with**: T-31, T-32, T-33, T-34, T-35, T-37, T-38, T-39

- [ ] **T-37** ADV-T6: Concurrent purge cron race test
  - **What**: Write `tests/adversarial/purge/concurrent-purge.test.ts` — run purge function twice concurrently against seeded DB with 5 eligible rows; assert total purged_count across both runs equals 5 (no double-delete, no under-delete).
  - **Done when**: `npx vitest run tests/adversarial/purge/concurrent-purge.test.ts` exits 0.
  - **A-rule(s)**: A8, A13, A15
  - **Depends on**: T-08
  - **Parallel-OK with**: T-31, T-32, T-33, T-34, T-35, T-36, T-38, T-39

- [ ] **T-38** ADV-T7: Client-supplied list limit bypass test
  - **What**: Write `tests/adversarial/todos/limit-bypass.test.ts` — call `listTodos` with any client-supplied limit param; assert response always caps at 200 items; mock repo with 300 rows and confirm returned array length ≤ 200.
  - **Done when**: `npx vitest run tests/adversarial/todos/limit-bypass.test.ts` exits 0.
  - **A-rule(s)**: A5, A15
  - **Depends on**: T-01
  - **Parallel-OK with**: T-31, T-32, T-33, T-34, T-35, T-36, T-37, T-39

- [ ] **T-39** ADV-O1 + ADV-O4: PII redaction CI gate test
  - **What**: Write `tests/adversarial/observability/pii-redaction.test.ts` — run pino logger with `{ context: { email: "x@example.com", user: { email: "y@test.org" }, password: "secret" } }`; capture serialized output; assert `rg "x@example.com|y@test.org|secret"` returns 0 matches. Write fixture file to `tests/fixtures/log-output.log` for CI grep gate.
  - **Done when**: `npx vitest run tests/adversarial/observability/pii-redaction.test.ts` exits 0. `rg -i "@" tests/fixtures/log-output.log` returns 0 matches.
  - **A-rule(s)**: A15, A21, A24
  - **Depends on**: T-04
  - **Parallel-OK with**: T-31, T-32, T-33, T-34, T-35, T-36, T-37, T-38

---

## Phase 6 — Observability, Cron Schedule, Polish

- [ ] **T-40** Hexagonal boundary CI gate
  - **What**: Add explicit CI step in `.github/workflows/ci.yml`: `rg "supabase|pino|@upstash|next/" src/domain/ src/ports/` → MUST return 0 matches; fail the build otherwise.
  - **Done when**: CI run on a branch that intentionally imports `pino` in `src/domain/` → CI step fails with non-zero exit. Remove the bad import → CI passes.
  - **A-rule(s)**: A4, A20
  - **Depends on**: T-09
  - **Parallel-OK with**: T-41, T-42

- [ ] **T-41** Error categorization enforcement — eslint rule
  - **What**: Add eslint rule (or `no-restricted-syntax` pattern) that flags any `return Err(...)` in a server action file where the object does NOT include `errorCategory`. Wire into CI.
  - **Done when**: Intentionally remove `errorCategory` from one action → eslint fails. Restore → eslint passes. `npx eslint src/adapters/next/actions/` exits 0.
  - **A-rule(s)**: A14, A21
  - **Depends on**: T-02
  - **Parallel-OK with**: T-40, T-42

- [ ] **T-42** Vercel Analytics integration
  - **What**: Add `@vercel/analytics` package; import `<Analytics />` component in `app/layout.tsx`; confirm component renders without runtime error.
  - **Done when**: `npx tsc --noEmit` exits 0; Playwright test: page load does not emit any console errors related to Analytics.
  - **A-rule(s)**: A21
  - **Depends on**: T-29
  - **Parallel-OK with**: T-40, T-41

- [ ] **T-43** Supabase cron schedule registration
  - **What**: Configure `purge-deleted` function schedule in `supabase/config.toml` (or via Supabase dashboard) for daily 03:00 UTC. Write deployment runbook section in `README.md` documenting the schedule and the dry-run verification procedure.
  - **Done when**: `supabase functions list` shows `purge-deleted` with schedule; README section exists and includes dry-run command.
  - **A-rule(s)**: A24
  - **Depends on**: T-30
  - **Parallel-OK with**: T-44, T-45

- [ ] **T-44** ADV-O3 + ADV-O5: Unhandled exception + console.log lint gates
  - **What**: Write `tests/adversarial/observability/unhandled-exception.test.ts` — mock a server action that throws unexpectedly; assert Next.js global error boundary logs `{ level: "fatal", msg: "action.unhandled_exception" }` and HTTP response does NOT expose stack trace. Separately: run eslint rule asserting 0 `console.*` calls outside `src/lib/logger.ts`.
  - **Done when**: `npx vitest run tests/adversarial/observability/unhandled-exception.test.ts` exits 0; `npx eslint src/` (excluding logger.ts) finds 0 `console.*` violations.
  - **A-rule(s)**: A15, A21
  - **Depends on**: T-04, T-09
  - **Parallel-OK with**: T-43, T-45

- [ ] **T-45** Smoke test + deployment runbook
  - **What**: Write `tests/e2e/smoke.spec.ts` — Playwright test sequence: sign-up new user → create todo → list → toggle → soft-delete → sign-out → confirm redirect to `/login`. Write `DEPLOYMENT.md` covering Supabase project setup, env var checklist (A22), region alignment check (Assumption #8), custom SMTP verification (Assumption #1), and rollback steps.
  - **Done when**: `npx playwright test tests/e2e/smoke.spec.ts` exits 0 against staging. `DEPLOYMENT.md` committed.
  - **A-rule(s)**: A21, A22
  - **Depends on**: T-29, T-30, T-43
  - **Parallel-OK with**: T-44

- [ ] **T-46** `EVALUATION.md` — T1.9 comparison artifact
  - **What**: Write `EVALUATION.md` documenting: sdd-* chain artifact counts, timing per phase, A-rule coverage observed, operator friction signals; comparable table for side-by-side with `speckit-*` results.
  - **Done when**: File committed; table includes both sdd-* and speckit-* columns (speckit-* cells may be TBD if run not yet complete).
  - **A-rule(s)**: —
  - **Depends on**: T-45
  - **Parallel-OK with**: —

---

## Dependency Graph

```
T-00 (scaffold)
 ├── T-01 (toolchain)
 │    ├── T-02 (tsc strict + lint)
 │    │    └── T-05 (Result<T,E>)
 │    │         ├── T-10 (domain/auth)
 │    │         ├── T-11 (domain/todo)
 │    │         │    └── T-12 (port/todo-repo)
 │    │         │         └── T-14 (SupabaseTodoRepository)
 │    │         └── T-13 (ports/auth+logger+rl)
 │    │              ├── T-15 (SupabaseAuthAdapter)
 │    │              └── T-16 (UpstashRateLimiter)
 │    ├── T-03 (env.ts)
 │    │    └── T-06 (supabase/client.ts)
 │    │         ├── T-14
 │    │         └── T-15
 │    └── T-04 (pino logger)
 │         ├── T-18..T-21 (auth actions)
 │         ├── T-24..T-28 (todo actions)
 │         └── T-39 (ADV-O1/O4)
 ├── T-07 (migration 0001_init)
 │    └── T-08 (migration 0002_rls)
 │         ├── T-14
 │         ├── T-36 (ADV-T4/T5)
 │         └── T-37 (ADV-T6)
 └── T-09 (CI workflow)
      ├── T-40 (boundary CI gate)
      └── T-44 (ADV-O3/O5)

T-17 (ownership check) ─→ T-14..T-16, T-24..T-28

Auth actions (T-18..T-22) ─→ T-23 (login UI)
Todo actions (T-24..T-28) ─→ T-29 (todos UI)
T-29 ─→ T-42 (Vercel Analytics)
T-30 (purge cron) ─→ T-43 (cron schedule) ─→ T-45 (smoke) ─→ T-46 (EVALUATION)

Adversarial tests T-31..T-39: depend only on T-01 or T-08 (written early, run red-first)
```

---

## Parallel Opportunities

| Group | Tasks | Condition |
|-------|-------|-----------|
| Foundation | T-02, T-03, T-07 | All depend only on T-00/T-01 — run simultaneously |
| Domain types | T-10, T-11 | Both depend on T-05 only |
| Port interfaces | T-12, T-13 | T-12 depends on T-10+T-11; T-13 on T-10 — near-simultaneous |
| Adapters | T-14, T-15, T-16, T-17 | All can be authored in parallel once T-06+T-08+T-12+T-13 are done |
| Auth actions | T-18, T-19, T-20, T-21 | Fully parallel once T-13+T-15+T-16+T-04+T-05 are done |
| Todo actions | T-24, T-25, T-26, T-27, T-28 | Fully parallel once T-14+T-17+T-04+T-05 are done |
| Adversarial tests | T-31..T-39 | Fully parallel with each other (only need T-01/T-08) |
| Phase 6 | T-40, T-41, T-42 | Parallel after their direct parents |

**Critical path**: T-00 → T-01 → T-02 → T-05 → T-11 → T-12 → T-14 → T-24..T-28 → T-29 → T-45 → T-46

---

## Task Summary

| Phase | Tasks | Count |
|-------|-------|-------|
| 0 — Foundational Infrastructure | T-00 – T-09 | 10 |
| 1 — Domain + Ports | T-10 – T-13 | 4 |
| 2 — Supabase Adapters + Rate Limiter | T-14 – T-17 | 4 |
| 3 — Auth Actions + Middleware (US2) | T-18 – T-23 | 6 |
| 4 — Todo Actions + UI (US1) | T-24 – T-30 | 7 |
| 5 — Adversarial Tests (A15) | T-31 – T-39 | 9 |
| 6 — Observability, Cron, Polish | T-40 – T-46 | 7 |
| **Total** | | **47** |

**A15 adversarial pairing map** (every US feature has an adversarial sibling):

| Feature task | Adversarial sibling |
|---|---|
| T-18 signUp | T-31 (rate-limit), T-34 (service_role leak) |
| T-19 signIn | T-31 (rate-limit), T-32 (forged JWT) |
| T-20 magicLink | T-31 (rate-limit), T-32 (expired token) |
| T-22 middleware | T-32 (session forgery) |
| T-24 createTodo | T-33 (user_id injection), T-35 (cross-tenant) |
| T-25 listTodos | T-36 (anon/RLS), T-38 (limit bypass) |
| T-26 updateTitle | T-35 (cross-tenant), T-36 (anon) |
| T-27 toggleTodo | T-35 (cross-tenant) |
| T-28 deleteTodo | T-35 (cross-tenant), T-36 (anon/deleted-row) |
| T-30 purge cron | T-37 (concurrent race) |
| T-04 pino logger | T-39 (PII redaction), T-44 (console.log lint) |
