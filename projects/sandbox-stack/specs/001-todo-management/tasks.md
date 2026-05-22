---

description: "Task list for 001-todo-management (Spec Kit + ECC + claude-mem stack)"
---

# Tasks: Personal Todo Management with User Authentication

**Input**: Design documents from `specs/001-todo-management/`

**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api.md, quickstart.md

**Tests**: INCLUDED — adversarial tests are mandatory per Principle II (3 capas VERIFICABLE) and A15 Unhappy Path First. Constitution gates A5 and A12 cannot ship without the adversarial Playwright suite green.

**Organization**: Tasks grouped by user story for independent implementation. Note: US2 (auth) precedes US1 (todos) because todos depend on identity. US3 (anonymous-denied) is verification phase covering both.

## Format

`- [ ] [TaskID] [P?] [Story?] Description with file path`

- **[P]**: parallelizable (different files, no incomplete dependencies)
- **[Story]**: maps to user stories US1 (todo CRUD), US2 (sign-up/sign-in), US3 (anonymous denial)

## Path Conventions

- Single Next.js full-stack project, no frontend/backend split
- Source: `src/`, tests: `tests/`, migrations: `supabase/migrations/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: project skeleton, deps, tool config.

- [x] T001 Initialize Next.js 15 App Router project at repo root with TypeScript and Tailwind 4 via `npx create-next-app@latest . --typescript --tailwind --app --no-src-dir false`
- [x] T002 [P] Add Supabase deps: `npm install @supabase/ssr @supabase/supabase-js zod pino` and dev deps `npm install -D vitest @playwright/test @upstash/ratelimit @upstash/redis supabase`
- [x] T003 [P] Configure ESLint + Prettier + tsconfig strict mode in `tsconfig.json`, `.eslintrc.cjs`, `.prettierrc`
- [x] T004 [P] Create `.env.example` listing required env vars (NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY, UPSTASH_REDIS_REST_URL, UPSTASH_REDIS_REST_TOKEN) per quickstart.md section 3
- [x] T005 Initialize Supabase local dev: `supabase init` in repo root; verify `supabase/config.toml` created
- [x] T006 [P] Configure Playwright: `npx playwright install --with-deps chromium` and create `playwright.config.ts` with baseURL http://localhost:3000

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: hexagonal skeleton, schema, RLS, logging, zod, rate limiter. No user-facing flow yet.

**CRITICAL**: No US1/US2/US3 work can begin until this phase is complete.

- [x] T007 Create hexagonal source layout: `mkdir -p src/domain/ports src/adapters/supabase src/adapters/logging src/app/actions src/app/(auth) src/app/todos src/lib tests/unit tests/integration tests/e2e` per plan.md
- [x] T008 Author migration `supabase/migrations/202605211900_initial.sql` with: `todos` table, `todo_events` table, `auth_events` table, indexes, triggers, RLS policies — exact schema per data-model.md
- [x] T009 Apply migration locally: `supabase start && supabase db push`; verify with `supabase db diff` that no drift remains [MANUAL STEP — SQL written; execution requires Docker + supabase CLI]
- [x] T010 [P] Create domain entities in `src/domain/todo.ts` and `src/domain/user.ts` (pure types + invariants, no IO) per data-model.md
- [x] T011 [P] Create domain ports in `src/domain/ports/todo-repository.ts` and `src/domain/ports/auth-provider.ts` per contracts/api.md
- [x] T012 [P] Create tagged domain errors in `src/domain/errors.ts` (UNAUTHENTICATED, FORBIDDEN, NOT_FOUND, STALE_VERSION, INVALID_INPUT, RATE_LIMITED, INTERNAL) per contracts/api.md
- [x] T013 [P] Create zod schemas in `src/lib/schemas.ts` for all server action inputs per contracts/api.md
- [x] T014 Implement structured logger in `src/adapters/logging/pino.ts` with redact patterns for `email`, `password`, `*.token` per Decision 9 in research.md
- [x] T015 Implement Supabase clients in `src/adapters/supabase/client.ts`: `createServerClient()` (cookie-based, A12) and `createBrowserClient()` (no service role) per @supabase/ssr docs
- [x] T016 [P] Implement Upstash rate limiter wrapper in `src/lib/rate-limit.ts` with 10/h/IP for sign-up and 5/h/IP for magic-link per Decision 8 in research.md

**Checkpoint**: foundation ready — US1/US2/US3 implementation can begin.

---

## Phase 3: User Story 2 — Sign-up and sign-in (Priority: P1)

**Goal**: New visitor can sign up, returning visitor can sign in with email+password or magic link; sign-out works; anti-enumeration on errors.

**Independent Test**: Clean session → sign up new email → verify landed in app. Sign out → sign in again → verify same state. Submit wrong credentials → verify generic error.

### Tests for User Story 2

- [x] T017 [P] [US2] Playwright e2e `tests/e2e/auth.spec.ts`: scenarios for sign-up happy path, sign-in success, magic-link request and redemption, sign-out, anti-enumeration on bad creds, deleteAccount cascade
- [x] T018 [P] [US2] Vitest integration `tests/integration/auth-provider.spec.ts`: against local Supabase verifying signUp / signIn / requestMagicLink return shapes match contracts/api.md
- [x] T019 [P] [US2] Vitest unit `tests/unit/schemas-auth.spec.ts`: zod schemas reject empty, oversized, malformed email/password

### Implementation for User Story 2

- [x] T020 [P] [US2] Implement `src/adapters/supabase/auth-provider.ts` implementing `AuthProvider` port using `@supabase/ssr` — signUp, signIn, requestMagicLink, signOut, deleteAccount per contracts/api.md
- [x] T021 [US2] Implement server action `src/app/actions/auth.ts` exporting `signUp`, `signInWithPassword`, `requestMagicLink`, `signOut`, `deleteAccount` — each validates input with zod, calls auth-provider, wraps rate limiter, writes `auth_events`, returns `Result<T>` per contracts/api.md (depends on T020)
- [x] T022 [P] [US2] Build sign-in page at `src/app/(auth)/sign-in/page.tsx` with form posting to `signInWithPassword` action + link to magic-link request
- [x] T023 [P] [US2] Build sign-up page at `src/app/(auth)/sign-up/page.tsx` with form posting to `signUp` action
- [x] T024 [P] [US2] Build magic-link request page at `src/app/(auth)/magic-link/page.tsx` and confirmation route at `src/app/(auth)/callback/route.ts` for Supabase OAuth/magic-link callback
- [x] T025 [US2] Add session-aware middleware at `src/middleware.ts` that refreshes Supabase cookies on every request (required by @supabase/ssr) per Vercel docs
- [x] T026 [US2] Add structured logging hooks in `src/app/actions/auth.ts` for every outcome (success, RATE_LIMITED, UNAUTHENTICATED, INTERNAL) — redacted email per T014

**Checkpoint**: US2 fully functional — sign-up, sign-in, magic-link, sign-out all work. Adversarial deferred to US3.

---

## Phase 4: User Story 1 — Authenticated user manages their own todos (Priority: P1)

**Goal**: signed-in user can CRUD their own todos with strict isolation, soft delete, completion toggle, optimistic concurrency.

**Independent Test**: Sign in as user A (via US2), create 3 todos, sign out, sign in as user B, verify zero todos visible; sign in as A again, verify 3 todos still there with identical state.

### Tests for User Story 1

- [x] T027 [P] [US1] Playwright e2e `tests/e2e/todo-crud.spec.ts`: create / list / update / complete / uncomplete / soft-delete happy paths; pagination at 50; edge cases (empty text, oversize text, stale version)
- [x] T028 [P] [US1] Vitest integration `tests/integration/todo-repository.spec.ts`: against local Supabase verifying RLS-scoped queries return only own rows; cross-tenant insert fails
- [x] T029 [P] [US1] Vitest unit `tests/unit/todo.spec.ts`: domain Todo entity invariants (text length, transitions completed↔not-completed, deleted_at semantics)

### Implementation for User Story 1

- [x] T030 [P] [US1] Implement `src/adapters/supabase/todo-repository.ts` implementing `TodoRepository` port — listActive, create, update with `expected_updated_at` check, complete, uncomplete, softDelete; all queries use server client (A12) per contracts/api.md
- [x] T031 [US1] Implement server actions `src/app/actions/todos.ts`: `createTodo`, `listActiveTodos`, `updateTodo`, `completeTodo`, `uncompleteTodo`, `deleteTodo` — each validates with zod, asserts session, delegates to repository, writes `todo_events`, returns `Result<T>` per contracts/api.md (depends on T030)
- [x] T032 [P] [US1] Build todos list page `src/app/todos/page.tsx` (Server Component) calling `listActiveTodos` for initial render; passes data to client component
- [x] T033 [P] [US1] Build todo list client component `src/app/todos/_components/todo-list.tsx` rendering active todos with optimistic UI updates and pagination cursor
- [x] T034 [P] [US1] Build todo create form component `src/app/todos/_components/todo-create-form.tsx` with client-side zod mirror for length
- [x] T035 [P] [US1] Build todo row component `src/app/todos/_components/todo-row.tsx` supporting edit-in-place, completion toggle, delete with confirmation
- [x] T036 [US1] Wire optimistic concurrency surfaces: when STALE_VERSION returns, show "this todo was updated elsewhere — refresh" UX without silent loss
- [x] T037 [US1] Add structured logging in `src/app/actions/todos.ts` for every outcome with user_id, action, todo_id, outcome, duration_ms

**Checkpoint**: US1 fully functional — owner can do everything on their own todos. Cross-tenant + anonymous validated in US3.

---

## Phase 5: User Story 3 — Anonymous and cross-tenant denial (Priority: P1)

**Goal**: prove A5 (multi-tenant isolation) and A12 (zero-trust) hold under adversarial conditions. This is the CRITICA gate per constitution.

**Independent Test**: Replay any authenticated request as anonymous → denied with no data. User A's token attempting user B's todo → denied with no data. Expired session → denied.

### Tests for User Story 3 (adversarial — mandatory)

- [x] T038 [US3] Playwright e2e `tests/e2e/adversarial-anonymous.spec.ts` + `tests/e2e/adversarial-log-redaction.spec.ts` — anonymous denial (AN-01–AN-08) + pino redaction (LR-01–LR-04, LR-E2E-01–02); anonymous GET /todos → redirect; anonymous server actions → UNAUTHENTICATED; email never in logs
- [x] T039 [US3] Playwright e2e `tests/e2e/adversarial-cross-tenant.spec.ts` — cross-tenant denial (CT-01–CT-05): user B cannot read/update/complete/delete user A's todos; A's todo verified unchanged after all attacks
- [x] T040 [US3] Vitest integration `tests/integration/rls-isolation.spec.ts` — 10 RLS bypass scenarios: anon SELECT→0 rows, anon INSERT→42501, user B SELECT/UPDATE/DELETE A's rows→0 rows, ownership forgery→rejected
- [x] T041 [US3] CI gate: `.github/workflows/test.yml` — jobs `adversarial-gate` + `integration-rls` are required status checks; failure blocks merge to main (A5 + A12 CRITICA); no [skip-ci] override

**Checkpoint**: US3 green → A5 and A12 verifiably hold → product is shippable.

---

## Phase 6: Polish & Cross-Cutting Concerns

- [x] T042 [P] Lint gate wired in CI (`npm run lint` with `--max-warnings 0` in package.json scripts); A14 enforced — no silent quality failures
- [x] T043 [P] `docs/SECURITY.md` created: env vars table, rotation schedule (quarterly), RLS threat model, PII handling, rate limit config, audit trail immutability
- [x] T044 [P] Vercel Analytics wired in `src/app/layout.tsx`: `<Analytics />` + `<SpeedInsights />`; packages added to package.json; covers A21 metrics pillar
- [x] T045 Supabase Edge Function `supabase/functions/purge-expired-todos/index.ts` (Deno): daily 03:00 UTC via config.toml schedule; hard-deletes todos where deleted_at < now()-30d; A24 enforced
- [x] T046 [P] Smoke test suite written at `tests/smoke/smoke.spec.ts` (SMOKE-01–07); `docs/SMOKE-LOG.md` created with 2026-05-21 entry; execution deferred to first live deploy
- [x] T047 Final constitution re-check: A-rule matrix documented in `T1.10-EVIDENCE.md`; drift noted (A1/A2/A3/A4/A7/A9/A10/A11/A17/A18/A19/A20/A23 — sandbox scope, not violations)

---

## Dependencies & Execution Order

### Phase dependencies

- **Setup (Phase 1)**: no deps; can start immediately.
- **Foundational (Phase 2)**: depends on Setup; BLOCKS all user stories.
- **US2 (Phase 3)**: depends on Foundational; precedes US1 because todos require identity.
- **US1 (Phase 4)**: depends on Foundational + US2 (needs working session).
- **US3 (Phase 5)**: depends on US1 and US2 being implementable (otherwise nothing to attack). Tests run in CI after both.
- **Polish (Phase 6)**: depends on US1 + US2 + US3 complete.

### Within each user story

- Tests written FIRST and confirmed FAIL → implementation → tests PASS → checkpoint.
- Models/ports (`domain/`) before adapters (`adapters/`).
- Adapters before server actions (`app/actions/`).
- Server actions before UI pages.
- Anti-enumeration and RLS asserted explicitly in code reviews (paired-eyes on PRs touching `auth.ts` or RLS policies).

### Parallel opportunities

- T002, T003, T004, T006 — parallel within Setup.
- T010, T011, T012, T013, T016 — parallel within Foundational (different files).
- T017, T018, T019 — parallel within US2 tests.
- T022, T023, T024 — parallel within US2 UI (separate route files).
- T027, T028, T029 — parallel within US1 tests.
- T032, T033, T034, T035 — parallel within US1 UI (different component files).
- T042, T043, T044, T046 — parallel within Polish.

---

## Parallel Example: Phase 2 Foundational

```bash
# After T007–T009 (skeleton + schema), launch in parallel:
Task: "Create domain entities in src/domain/todo.ts and src/domain/user.ts"
Task: "Create domain ports in src/domain/ports/todo-repository.ts and src/domain/ports/auth-provider.ts"
Task: "Create tagged domain errors in src/domain/errors.ts"
Task: "Create zod schemas in src/lib/schemas.ts"
Task: "Implement Upstash rate limiter wrapper in src/lib/rate-limit.ts"
```

---

## Implementation Strategy

### MVP First (US2 + US1, then ship behind feature flag)

1. Phase 1 Setup.
2. Phase 2 Foundational (DB + skeleton + zod + logger).
3. Phase 3 US2 (auth) — checkpoint: sign-up/sign-in/sign-out work.
4. Phase 4 US1 (todos) — checkpoint: full CRUD for owner.
5. Phase 5 US3 (adversarial) — checkpoint: A5 + A12 green, CI gate active.
6. Soft launch behind Vercel preview link.
7. Phase 6 Polish, then production promote.

### Incremental Delivery

- After US2: identity works but no app surface yet — internal-only deploy.
- After US1: usable app for invited testers (no public sign-up open).
- After US3: open public sign-up.

### Parallel Team Strategy

With 2 developers:

- Dev A: T020-T021, T025-T026 (auth backend + middleware).
- Dev B: T022-T024 (auth UI) in parallel.
- Then Dev A: T030-T031 (todo backend), Dev B: T032-T035 (todo UI) in parallel.
- Both: T038-T041 (adversarial) jointly — security work pairs naturally.

---

## Notes

- Every PR touching `auth.ts`, `todo-repository.ts`, or `202605211900_initial.sql` requires a security review (constitution governance).
- Commit at every checkpoint at minimum; prefer per-task commits when atomic.
- Adversarial CI gate (T041) is non-overridable: no `[skip-ci]` allowed on PRs that change auth or todos.
- After T047 (final constitution re-check), capture any drift in the next ADR before shipping.
