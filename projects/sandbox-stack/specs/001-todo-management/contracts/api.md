# Contracts: Server Actions

**Phase 1 output**. Next.js Server Action signatures + zod schemas + return shapes.

All actions live under `src/app/actions/`. All accept and return plain values (no `Response` objects). Errors are returned as tagged discriminated unions, not thrown (A14 explicit failure).

## Common shape

```ts
type Ok<T> = { ok: true; value: T };
type Err = { ok: false; error: { code: ErrorCode; message: string } };
type Result<T> = Ok<T> | Err;

type ErrorCode =
  | 'UNAUTHENTICATED'    // A12: session absent or expired
  | 'FORBIDDEN'          // A5: tried to touch another user's todo
  | 'NOT_FOUND'          // todo doesn't exist (or already hard-deleted)
  | 'STALE_VERSION'      // A13: optimistic concurrency conflict
  | 'INVALID_INPUT'      // zod validation failed
  | 'RATE_LIMITED'       // A16: too many auth attempts
  | 'INTERNAL';          // Supabase/Vercel transient; A14 explicit
```

## Auth actions

### `signUp(input)`
```ts
input: { email: string; password: string }   // both 1..256; email valid; password >=8 + (number|symbol)
output: Result<{ requiresEmailConfirmation: boolean }>
```
Errors: `INVALID_INPUT`, `RATE_LIMITED`, `INTERNAL`. Never `UNAUTHENTICATED`. Anti-enumeration: on duplicate email, returns `ok: true` with generic message-side hint (A5 confidentiality).

### `signInWithPassword(input)`
```ts
input: { email: string; password: string }
output: Result<{ userId: string }>
```
Errors: `INVALID_INPUT`, `UNAUTHENTICATED` (single code for both wrong-email and wrong-password — anti-enumeration FR-005), `RATE_LIMITED`, `INTERNAL`.

### `requestMagicLink(input)`
```ts
input: { email: string }
output: Result<{ sent: boolean }>   // returns sent:true regardless to avoid enumeration
```
Errors: `INVALID_INPUT`, `RATE_LIMITED`, `INTERNAL`.

### `signOut()`
```ts
input: void
output: Result<null>
```
Errors: `INTERNAL` only. Always best-effort; clears session cookies.

### `deleteAccount()`
```ts
input: void
output: Result<{ deletedTodos: number }>   // count for confirmation
```
Errors: `UNAUTHENTICATED`, `INTERNAL`. Cascades delete on user and todos (FK ON DELETE CASCADE). Writes `auth_events` kind='signout' before destruction.

## Todo actions

### `createTodo(input)`
```ts
input: { text: string }   // 1..1000 chars, trimmed
output: Result<Todo>      // Todo = { id, text, createdAt, updatedAt, completedAt: null }
```
Errors: `UNAUTHENTICATED`, `INVALID_INPUT`, `INTERNAL`.

### `listActiveTodos(input)`
```ts
input: { pageCursor?: string; limit?: number }   // limit default 50, max 100
output: Result<{ items: Todo[]; nextCursor: string | null }>
```
Errors: `UNAUTHENTICATED`, `INVALID_INPUT`, `INTERNAL`.

### `updateTodo(input)`
```ts
input: { id: string; text: string; expectedUpdatedAt: string }   // ISO-8601
output: Result<Todo>
```
Errors: `UNAUTHENTICATED`, `FORBIDDEN` (cross-tenant attempt → RLS denies), `NOT_FOUND` (already hard-deleted), `STALE_VERSION` (concurrent edit), `INVALID_INPUT`, `INTERNAL`.

### `completeTodo(input)` / `uncompleteTodo(input)`
```ts
input: { id: string; expectedUpdatedAt: string }
output: Result<Todo>
```
Errors: same as `updateTodo`. Idempotent: repeat completes return success without changing `completed_at`.

### `deleteTodo(input)` (soft)
```ts
input: { id: string }
output: Result<{ deletedAt: string }>
```
Errors: `UNAUTHENTICATED`, `FORBIDDEN`, `NOT_FOUND`, `INTERNAL`. Idempotent: re-delete returns the existing `deleted_at` without modification.

## Cross-cutting concerns

- **Every action** calls `getServerSession()` first; absent session → return `UNAUTHENTICATED` immediately (A12).
- **Every action** validates input with the corresponding zod schema before any DB call.
- **Every successful write** appends a row to `todo_events` (or `auth_events` for auth actions) via the same transaction where possible.
- **Every action** logs structured success / failure to `pino` with `user_id`, `action`, `outcome`, `duration_ms`. No PII in logs (email redacted).

## Adversarial test contract

The Playwright suite under `tests/e2e/adversarial.spec.ts` must verify, for each todo action:

1. Anonymous session → `UNAUTHENTICATED`, no rows touched, no data leaked in body or headers.
2. Authenticated user A invoking with a todo `id` owned by user B → `FORBIDDEN` or `NOT_FOUND` (both acceptable; never silent success).
3. Expired session → `UNAUTHENTICATED` and redirect to sign-in.

These three scenarios MUST pass on every CI run; failure blocks merge (A5, A12 CRITICA).
