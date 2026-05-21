# Todo Management Specification

## Purpose

Defines the full lifecycle of a user-owned todo item: creation, listing (active only), title update, completion toggle, and soft-delete. Every operation MUST enforce strict ownership: a user SHALL only read or mutate todos where `user_id = auth.uid()` AND `deleted_at IS NULL`. This invariant is enforced independently at the server-action layer (app) and at the database layer (RLS). (A5, A12 ZT-3, A25)

---

## Requirements

### Requirement: Create Todo

An authenticated user MUST be able to create a new todo item with a non-empty title. (A12, A25)

| Field | Rule |
|-------|------|
| title | MUST be a non-empty string; MUST be <= 500 characters; leading/trailing whitespace trimmed |
| user_id | MUST be set server-side from `getServerSession().userId`; MUST NOT be accepted from client payload |
| completed | MUST default to `false`; `completed_at` MUST default to `NULL` |
| deleted_at | MUST default to `NULL` |

#### Scenario: Successful creation

- GIVEN an authenticated user submits a title of 1–500 non-whitespace characters
- WHEN the `createTodo` server action is invoked
- THEN a new row is inserted with `user_id = auth.uid()`, `completed = false`, `deleted_at = NULL`
- AND the action returns `Result<{ todo: Todo }, never>`
- AND the new item appears at the top of the active list

#### Scenario: Empty title

- GIVEN a user submits an empty string or whitespace-only title
- WHEN the zod schema validates
- THEN validation fails before any DB call
- AND the action returns `Result<never, { code: "VALIDATION_ERROR", field: "title" }>`

#### Scenario: Title exceeds 500 characters

- GIVEN a user submits a title longer than 500 characters
- WHEN the zod schema validates
- THEN validation fails before any DB call
- AND the action returns `Result<never, { code: "VALIDATION_ERROR", field: "title", reason: "TOO_LONG" }>`

#### Scenario: Unauthenticated create attempt

- GIVEN no valid session exists
- WHEN `createTodo` is invoked (e.g. via direct HTTP call)
- THEN `getServerSession()` returns null
- AND the action returns `Result<never, { code: "UNAUTHENTICATED" }>`
- AND NO row is inserted

---

### Requirement: List Active Todos

An authenticated user MUST be able to retrieve all their active (non-deleted) todos. The list MUST be scoped strictly to the authenticated user. (A5, A12 ZT-3)

| Constraint | Rule |
|------------|------|
| Filter | `user_id = auth.uid() AND deleted_at IS NULL` — enforced at BOTH app and RLS layers |
| Ordering | SHOULD be `created_at DESC` (newest first) |
| Cap | MUST be capped at 200 items (Assumption #6); if user has > 200 active todos, oldest are hidden with a banner |
| Completed items | MUST be included in the list (visible but visually distinguished) |

#### Scenario: User has active todos

- GIVEN an authenticated user has N active todos (N <= 200)
- WHEN `listTodos` server action is invoked
- THEN the action returns `Result<{ todos: Todo[] }, never>` with exactly N items
- AND every item satisfies `user_id = auth.uid() AND deleted_at IS NULL`

#### Scenario: User has no todos

- GIVEN an authenticated user has zero active todos
- WHEN `listTodos` is invoked
- THEN the action returns `Result<{ todos: [] }, never>`
- AND the UI renders an empty state (not an error)

#### Scenario: User exceeds 200-item cap

- GIVEN a user has 250 active todos
- WHEN `listTodos` is invoked
- THEN the action returns the 200 most-recently-created items
- AND the response includes `{ capped: true, total: 250 }` so the UI can render the overflow banner

#### Scenario: Cross-tenant isolation — user sees only own todos (A5)

- GIVEN user A has todos and user B is authenticated
- WHEN user B calls `listTodos`
- THEN the response contains ONLY user B's todos
- AND user A's todos are absent from the result at both app and RLS layers

#### Scenario: Unauthenticated list attempt

- GIVEN no valid session exists
- WHEN `listTodos` is invoked
- THEN the action returns `Result<never, { code: "UNAUTHENTICATED" }>`
- AND NO data is returned

---

### Requirement: Update Todo Title

An authenticated user MUST be able to update the title of one of their own active todos. The user MUST NOT be able to update another user's todo. (A5, A25)

#### Scenario: Successful title update

- GIVEN an authenticated user owns todo `T` and `T.deleted_at IS NULL`
- WHEN `updateTodoTitle(id: T.id, title: "new title")` is invoked
- THEN the todo row is updated with the new title
- AND the action returns `Result<{ todo: Todo }, never>`

#### Scenario: Todo not found or not owned

- GIVEN a user supplies a `todoId` that either does not exist or belongs to another user
- WHEN `updateTodoTitle` is invoked
- THEN the DB UPDATE touches 0 rows (RLS silently filters)
- AND the action returns `Result<never, { code: "NOT_FOUND" }>`
- AND no error leaks the existence of the other user's todo (A5)

#### Scenario: Update on soft-deleted todo

- GIVEN a todo has `deleted_at IS NOT NULL`
- WHEN `updateTodoTitle` is invoked with its `id`
- THEN the DB UPDATE touches 0 rows (RLS filters deleted items)
- AND the action returns `Result<never, { code: "NOT_FOUND" }>`

#### Scenario: Empty or invalid title on update

- GIVEN a user submits an empty or > 500-char title
- WHEN the zod schema validates
- THEN validation fails before the DB call
- AND the action returns `Result<never, { code: "VALIDATION_ERROR", field: "title" }>`

---

### Requirement: Toggle Completion

An authenticated user MUST be able to toggle the `completed` state of their own active todos. The operation MUST be idempotent. (A8, A5, A25)

| Field | Rule |
|-------|------|
| completed | Toggled boolean; `completed_at` set to `NOW()` on true, `NULL` on false (Assumption #7) |

#### Scenario: Mark as complete

- GIVEN an active todo with `completed = false`
- WHEN `toggleTodo(id)` is invoked
- THEN `completed = true` and `completed_at = NOW()` are set
- AND the action returns `Result<{ todo: Todo }, never>`

#### Scenario: Mark as incomplete (undo)

- GIVEN an active todo with `completed = true`
- WHEN `toggleTodo(id)` is invoked
- THEN `completed = false` and `completed_at = NULL` are set
- AND the action returns `Result<{ todo: Todo }, never>`

#### Scenario: Double-toggle (idempotency — A8)

- GIVEN a user triggers toggle twice in rapid succession (e.g. double-click)
- WHEN both `toggleTodo` calls execute
- THEN the second call results in the same final state as one call (no error, no corrupted state)
- AND the server MUST NOT return an error for the second call

#### Scenario: Toggle on another user's todo

- GIVEN a user supplies a `todoId` owned by another user
- WHEN `toggleTodo` is invoked
- THEN 0 rows are updated (RLS)
- AND the action returns `Result<never, { code: "NOT_FOUND" }>`

---

### Requirement: Soft-Delete Todo

An authenticated user MUST be able to soft-delete one of their own todos. Soft-deleted todos MUST be invisible in all normal list queries. Hard-delete is performed by the purge cron after 30 days. (A24, A5)

#### Scenario: Successful soft-delete

- GIVEN an authenticated user owns active todo `T`
- WHEN `deleteTodo(id: T.id)` is invoked
- THEN `T.deleted_at` is set to `NOW()`
- AND the action returns `Result<{ id: T.id }, never>`
- AND `T` no longer appears in `listTodos` results
- AND `T` is recoverable within 30 days (A24 — data lifecycle window)

#### Scenario: Soft-delete already-deleted todo (idempotency — A8)

- GIVEN a todo already has `deleted_at IS NOT NULL`
- WHEN `deleteTodo(id)` is invoked
- THEN the action returns `Result<{ id }, never>` (idempotent success — no error)
- AND `deleted_at` is NOT overwritten (first deletion timestamp is preserved)

#### Scenario: Soft-delete another user's todo

- GIVEN a user supplies a `todoId` owned by another user
- WHEN `deleteTodo` is invoked
- THEN 0 rows are updated (RLS)
- AND the action returns `Result<never, { code: "NOT_FOUND" }>`

#### Scenario: Unauthenticated delete attempt

- GIVEN no valid session exists
- WHEN `deleteTodo` is invoked
- THEN the action returns `Result<never, { code: "UNAUTHENTICATED" }>`
- AND NO row is mutated

---

### Requirement: Data Lifecycle — 30-Day Purge (A24)

Soft-deleted todos MUST be hard-deleted by an automated cron job 30 days after `deleted_at`. The cron MUST support a dry-run mode for staging verification. (A24, Principio I)

#### Scenario: Cron purges eligible rows

- GIVEN rows exist where `deleted_at < NOW() - INTERVAL '30 days'`
- WHEN the `purge-deleted` Supabase Function runs (scheduled)
- THEN those rows are permanently deleted from the `todos` table
- AND a structured log entry records `{ purged_count, run_at, dry_run: false }`

#### Scenario: Dry-run reports exact count without deleting

- GIVEN the cron is invoked with `{ dry_run: true }` on a seeded staging DB
- WHEN the handler executes
- THEN it returns the count of rows that WOULD be deleted
- AND NO rows are deleted
- AND the reported count MUST equal the count a live run would delete (off-by-one is a FAIL — Principio I)

#### Scenario: No eligible rows

- GIVEN no rows satisfy the 30-day predicate
- WHEN the cron runs
- THEN `purged_count = 0` is logged
- AND the cron exits without error

---

## Invariants

1. **Ownership**: Every server action that reads or mutates a todo MUST scope its query with `user_id = auth.uid()`. Server actions MUST NOT accept `user_id` from client input. (A5, A25)
2. **Deleted-at filter**: Every query against `todos` MUST include `deleted_at IS NULL` unless it is the purge cron itself. (A24)
3. **Result<T,E> coverage**: Every exported server action MUST return `Result<T, E>`. No thrown exceptions escape the action boundary. (A14)
4. **Session-first**: `getServerSession()` MUST be called before any data operation in every server action. (A12 ZT-3)
5. **200-item cap**: The list query MUST apply `LIMIT 200` at the DB level, not in application code after fetching all rows. (Assumption #6)
6. **Idempotent mutations**: `toggleTodo` and `deleteTodo` MUST be idempotent — repeated calls with the same input MUST NOT produce errors or corrupted state. (A8)

---

## Multi-Tenant Isolation Block (A5)

RLS policies on `todos` MUST enforce the following:

```sql
-- SELECT policy
CREATE POLICY "owner_select" ON todos
  FOR SELECT USING (user_id = auth.uid() AND deleted_at IS NULL);

-- INSERT policy
CREATE POLICY "owner_insert" ON todos
  FOR INSERT WITH CHECK (user_id = auth.uid());

-- UPDATE policy
CREATE POLICY "owner_update" ON todos
  FOR UPDATE USING (user_id = auth.uid() AND deleted_at IS NULL);

-- DELETE (hard) policy — purge cron only, uses service_role, RLS bypassed via policy exception
-- No user-facing DELETE policy; soft-delete uses UPDATE
```

Server-action layer MUST additionally:
- Extract `userId` from `getServerSession()` — NEVER from the request body or query params.
- Pass `userId` as an explicit parameter to the repository, not via ambient context.
- Verify the returned row count > 0 after UPDATE/soft-delete; treat 0 rows as `NOT_FOUND`.

---

## Adversarial Scenarios (A15)

| # | Attack | Expected System Behavior |
|---|--------|--------------------------|
| ADV-T1 | User B crafts a `createTodo` call with `user_id` set to User A's ID in the request body | Server action ignores payload `user_id`; uses `getServerSession().userId` — User A's todos unaffected |
| ADV-T2 | User B calls `updateTodoTitle` with User A's `todoId` | RLS predicate `user_id = auth.uid()` returns 0 rows; action returns `NOT_FOUND` — no data leaked |
| ADV-T3 | User B calls `deleteTodo` with User A's `todoId` | Same as ADV-T2 — 0 rows updated, `NOT_FOUND` returned |
| ADV-T4 | Attacker queries Supabase REST API directly with `anon` key (no JWT) | RLS returns 0 rows on SELECT; INSERT rejected by owner check; no user data disclosed |
| ADV-T5 | Attacker bypasses `deleted_at IS NULL` filter by crafting a direct DB query | RLS SELECT policy includes `deleted_at IS NULL` — deleted rows invisible even via direct query |
| ADV-T6 | Purge cron runs twice concurrently (race condition — A13) | Both runs compute the same predicate; second run finds 0 eligible rows — idempotent, no double-delete corruption |
| ADV-T7 | Client sends `limit=9999` to list endpoint trying to fetch beyond 200 cap | Server action applies `LIMIT 200` unconditionally; client-supplied limit is ignored |

These scenarios MUST be written as automated tests BEFORE the feature code they protect. (A15)
